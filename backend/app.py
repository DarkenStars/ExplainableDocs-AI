import os
import time
import requests
import re 
from collections import defaultdict
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# typing.Literal (py>=3.8); if older, install typing_extensions and switch import
try:
    from typing import Literal
except Exception:  
    from typing_extensions import Literal  # type: ignore

# DB
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import Json

from ml_models import select_evidence_from_urls
from text_polisher import polish_text

from fastapi.middleware.cors import CORSMiddleware

# Config & Globals
load_dotenv()

API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

POOL: Optional[SimpleConnectionPool] = None  # DB pool (initialized on startup)


# FastAPI
app = FastAPI(title="News Advisor AI Fact Checker", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],  # your prod URL
    allow_origin_regex=r"https://.*\.vercel\.app",      # preview deploys
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class VerifyRequest(BaseModel):
    message: str
    max_results: Optional[int] = 5  # up to 10 per Google CSE

class EvidenceItem(BaseModel):
    url: Optional[str] = None
    sentence: str

class EvidenceBundle(BaseModel):
    support: List[EvidenceItem] = []
    refute: List[EvidenceItem] = []

class Source(BaseModel):
    id: int
    title: str
    url: str
    organization: str
    snippet: Optional[str] = None
    stance: Literal["support", "refute", "mixed", "neutral"] = "neutral"
    evidence_sentences: List[str] = []

class VerifyResponse(BaseModel):
    verdict: Literal["true", "false", "uncertain"]
    confidence: int
    explanation: str
    sources: List[Source]          # ALL sources with stance & evidence lines
    evidence: EvidenceBundle       # Flat lists grouped by side
    processing_time: float

# DB helpers
def setup_database(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_log (
                id SERIAL PRIMARY KEY,
                user_input TEXT NOT NULL UNIQUE,
                verdict TEXT,
                source_link TEXT,
                explanation TEXT,
                evidence_json JSONB,
                searched_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS search_log_user_input_norm_idx
            ON search_log ((lower(btrim(user_input))));
        """)
        conn.commit()

def get_conn():
    if POOL is None:
        return None
    return POOL.getconn()

def put_conn(conn):
    if POOL and conn:
        POOL.putconn(conn)

def normalize_claim(text: str) -> str:
    return " ".join((text or "").split()).lower()

def check_cache(conn, claim_norm):
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT verdict, source_link, explanation, evidence_json
                FROM search_log
                WHERE lower(btrim(user_input)) = lower(btrim(%s));
            """, (claim_norm,))
            row = cur.fetchone()
            if row:
                return {
                    "verdict": row[0],
                    "link": row[1],
                    "explanation": row[2],
                    "evidence": row[3],
                }
    except Exception as e:
        print(f"[Cache] check error: {e}")
    return None

def upsert_result(conn, claim_norm, verdict, source_link, explanation=None, evidence_json=None):
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_log (user_input, verdict, source_link, explanation, evidence_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_input) DO UPDATE SET
                    verdict = EXCLUDED.verdict,
                    source_link = EXCLUDED.source_link,
                    explanation = EXCLUDED.explanation,
                    evidence_json = EXCLUDED.evidence_json,
                    searched_at = CURRENT_TIMESTAMP;
            """, (
                claim_norm,
                verdict,
                source_link,
                explanation,
                Json(evidence_json) if evidence_json is not None else None,
            ))
            conn.commit()
    except Exception as e:
        print(f"[DB] upsert error: {e}")
        conn.rollback()

# Search & Verdict
def search_claim(query: str, num: int = 10):
    if not API_KEY:
        return {"error": "Configuration Error: Please set API_KEY."}
    if not SEARCH_ENGINE_ID:
        return {"error": "Configuration Error: Please set SEARCH_ENGINE_ID."}
    num = max(1, min(int(num or 10), 10))  # Google CSE max per call = 10

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": SEARCH_ENGINE_ID, "q": query, "num": num}
    try:
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        return {"results": resp.json().get("items", [])}
    except Exception as e:
        return {"error": f"Search API error: {e}"}

def analyze_verdicts_improved(search_results):
    """
    Analyzes search results with improved accuracy by using whole word matching,
    counting keyword frequency, handling basic negation, and weighting sources.
    """
    if not search_results:
        return {"best_verdict": "uncertain", "percentages": {"true": 0, "false": 0, "uncertain": 100}}

    # Keywords with weights. Using more specific, powerful words is key.
    supporting_keywords = {'confirmed': 3, 'verified': 3, 'accurate': 3, 'fact-check: true': 4, 'correct': 2, 'evidence': 1}
    refuting_keywords = {'hoax': 3, 'false': 3, 'debunked': 3, 'myth': 3, 'fact-check: false': 4, 'incorrect': 2, 'misleading': 2, 'baseless': 1}
    negation_words = {'not', 'isnt', 'is not', 'aint', 'not verified', 'not confirmed'}

    # Weight results from more reliable sources higher
    source_weights = {
        'reuters.com': 1.5,
        'apnews.com': 1.5,
        'snopes.com': 1.5,
        'politifact.com': 1.5,
        'factcheck.org': 1.5,
    }
    default_weight = 1.0
    
    support_score = 0
    refute_score = 0

    for item in search_results:
        text = f"{item.get('title','')} {item.get('snippet','')}".lower()
        source_url = item.get('source', '')
        
        # Determine the weight for the current source
        item_weight = default_weight
        for domain, weight in source_weights.items():
            if domain in source_url:
                item_weight = weight
                break # Stop after finding the first match

        # Count keyword occurrences instead of just presence
        # Use regex for whole word matching (\b)
        for keyword, weight in supporting_keywords.items():
            # Use regex to find whole words only
            matches = re.findall(r'\b' + re.escape(keyword) + r'\b', text)
            if matches:
                # Basic negation check
                is_negated = False
                for neg in negation_words:
                    if f"{neg} {keyword}" in text:
                        is_negated = True
                        break
                
                if is_negated:
                    # If "not true", add to refute score instead
                    refute_score += (weight * len(matches) * item_weight)
                else:
                    support_score += (weight * len(matches) * item_weight)

        for keyword, weight in refuting_keywords.items():
            matches = re.findall(r'\b' + re.escape(keyword) + r'\b', text)
            if matches:
                # No need to check for negation on refuting keywords
                refute_score += (weight * len(matches) * item_weight)

    total_score = support_score + refute_score
    if total_score == 0:
        return {"best_verdict": "uncertain", "percentages": {"true": 0, "false": 0, "uncertain": 100}}

    # Calculate percentages
    s_pct = round((support_score / total_score) * 100)
    f_pct = round((refute_score / total_score) * 100)
    
    # Improvement 4: A more decisive threshold
    # Verdict is 'false' if refute score is at least double the support score
    if refute_score >= support_score * 2:
        best = "false"
    # Verdict is 'true' if support score is at least double the refute score
    elif support_score >= refute_score * 2:
        best = "true"
    else:
        best = "uncertain"
        
    return {"best_verdict": best, "percentages": {"true": s_pct, "false": f_pct}}

def build_explanation(claim, entailing, contradicting):
    if not entailing and not contradicting:
        return f"After reviewing top sources, no strong evidence was found to either support or refute the claim about '{claim}'."
    if len(contradicting) >= 2 and len(contradicting) >= len(entailing) + 1:
        evidence_snippets = [f'"{ev.get("sentence","")}"' for ev in contradicting[:2]]
        return f"Evidence strongly suggests the claim about '{claim}' is false. Key sources state: {' '.join(evidence_snippets)}"
    elif len(entailing) >= 2 and len(entailing) >= len(contradicting) + 1:
        evidence_snippets = [f'"{ev.get("sentence","")}"' for ev in entailing[:2]]
        return f"Evidence tends to support the claim about '{claim}'. Relevant sources mention: {' '.join(evidence_snippets)}"
    else:
        return f"The evidence regarding '{claim}' is mixed and inconclusive based on available sources."


def simple_fuse_verdict(heuristic_best_verdict, entailing, contradicting):
    e, c = len(entailing), len(contradicting)
    if e >= 2 and e >= c + 1:
        return "true"
    if c >= 2 and c >= e + 1:
        return "false"
    return heuristic_best_verdict

# Lifespan
@app.on_event("startup")
def on_startup():
    global POOL
    try:
        POOL = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn = get_conn()
        if conn:
            try:
                setup_database(conn)
                print("Database ready.")
            finally:
                put_conn(conn)
        print("FastAPI started.")
    except Exception as e:
        POOL = None
        print(f"[WARN] DB pool init failed; caching disabled. Details: {e}")

@app.on_event("shutdown")
def on_shutdown():
    global POOL
    if POOL:
        POOL.closeall()
        POOL = None


# Routes
@app.get("/health")
def health():
    return {"status": "ok", "service": "News Advisor AI Fact Checker"}

@app.post("/verify", response_model=VerifyResponse)
def verify_claim(payload: VerifyRequest):
    claim = (payload.message or "").strip()
    if not claim:
        raise HTTPException(status_code=400, detail="No claim provided")

    max_results = payload.max_results or 10
    t0 = time.perf_counter()

    # Try DB (optional)
    conn = get_conn()
    try:
        claim_norm = normalize_claim(claim)

        # Cache lookup
        cached = check_cache(conn, claim_norm) if conn else None
        if cached:
            elapsed = round(time.perf_counter() - t0, 3)
            verdict = (cached.get("verdict") or "uncertain").lower()
            # Minimal source card referencing cache link
            sources = [
                Source(
                    id=1,
                    title="Database Cache",
                    url=cached.get("link") or "#",
                    organization="Cached",
                    snippet=None,
                    stance="neutral",
                    evidence_sentences=[],
                )
            ]
            evidence_bundle = EvidenceBundle(support=[], refute=[])
            return VerifyResponse(
                verdict=verdict, confidence=85,
                explanation=cached.get("explanation") or "Cached result",
                sources=sources, evidence=evidence_bundle,
                processing_time=elapsed
            )
        
        # Search web
        search_data = search_claim(claim, num=max_results)
        if "error" in search_data:
            raise HTTPException(status_code=502, detail=search_data["error"])
        results = search_data.get("results", [])

        # Heuristic pass
        heuristic = analyze_verdicts(results)

        # Select evidence via NLI/ML
        links = [it.get("link") for it in results if it.get("link")]
        try:
            entailing, contradicting = select_evidence_from_urls(claim, links)
        except Exception as e:
            print(f"[NLI] error: {e}")
            entailing, contradicting = [], []

        final_verdict = simple_fuse_verdict(heuristic["best_verdict"], entailing, contradicting)

        # Explanation (polished)
        structured_explanation = build_explanation(claim, entailing, contradicting)
        try:
            polished_explanation = polish_text(structured_explanation)
        except Exception as e:
            print(f"[Polisher] error: {e}")
            polished_explanation = structured_explanation

        # Confidence
        confidence = 75
        if final_verdict in ["true", "false"]:
            confidence = 90
        if len(entailing) >= 2 or len(contradicting) >= 2:
            confidence = min(95, confidence + 10)

        # Per-URL evidence buckets
        def _ev_url(ev):
            return ev.get("url") or ev.get("source") or ev.get("link")

        per_url_ev = defaultdict(lambda: {"support": [], "refute": []})
        for ev in entailing:
            u = _ev_url(ev)
            if u:
                per_url_ev[u]["support"].append(ev.get("sentence", ""))
        for ev in contradicting:
            u = _ev_url(ev)
            if u:
                per_url_ev[u]["refute"].append(ev.get("sentence", ""))

        # Build ALL sources with stance and evidence lines
        sources: List[Source] = []
        for i, item in enumerate(results, 1):
            url = item.get("link") or "#"
            org = item.get("displayLink") or "Web"
            title = (item.get("title") or "Unknown Source")[:200]
            snippet = (item.get("snippet") or "")[:400]

            bucket = per_url_ev.get(url, {"support": [], "refute": []})
            sup_cnt = len(bucket["support"])
            ref_cnt = len(bucket["refute"])

            if sup_cnt and ref_cnt:
                stance = "mixed"
            elif sup_cnt:
                stance = "support"
            elif ref_cnt:
                stance = "refute"
            else:
                stance = "neutral"

            evidence_lines = (bucket["support"] + bucket["refute"])[:5]

            sources.append(
                Source(
                    id=i,
                    title=title,
                    url=url,
                    organization=org,
                    snippet=snippet,
                    stance=stance,
                    evidence_sentences=evidence_lines,
                )
            )

        # Flat evidence bundle for UI convenience
        evidence_bundle = EvidenceBundle(
            support=[EvidenceItem(url=_ev_url(ev), sentence=ev.get("sentence", "")) for ev in entailing],
            refute=[EvidenceItem(url=_ev_url(ev), sentence=ev.get("sentence", "")) for ev in contradicting],
        )

        # Cache write (best-effort)
        top_link = results[0].get("link") if results else "#"
        evidence_payload = {
            "entailing": entailing,
            "contradicting": contradicting,
            "heuristic": heuristic,
        }
        if conn:
            upsert_result(conn, claim_norm, final_verdict, top_link, polished_explanation, evidence_payload)

        elapsed = round(time.perf_counter() - t0, 3)
        return VerifyResponse(
            verdict=final_verdict,
            confidence=confidence,
            explanation=polished_explanation,
            sources=sources,
            evidence=evidence_bundle,
            processing_time=elapsed,
        )
    finally:
        if conn:
            put_conn(conn)

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI on http://0.0.0.0:5000 ...")
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)