# fact_checker_plus_fusion.py
# Retrieval-first fact checker:
# - Google CSE retrieval (your links)
# - Heuristic verdict from titles/snippets (fast)
# - Slim NLI evidence (MiniLM rank + BART-MNLI)
# - SIMPLE FUSION: NLI rules win only when clearly strong; else fall back to heuristic
# - PostgreSQL cache with UPSERT (stores final verdict, top link, explanation, evidence)

import os
import re
import json
import requests
import psycopg2
from dotenv import load_dotenv

# --- ML & extraction ---
import trafilatura
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# =========================
# Config & Globals
# =========================
load_dotenv()

API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

# Tunables for the slim NLI explainer
MAX_URLS = 3               # fetch at most N pages from your search results
PER_URL_CANDIDATES = 8     # run NLI on at most N top-similarity sentences per page
ENTAIL_THRESHOLD = 0.72
CONTRA_THRESHOLD = 0.72
MAX_ENTAILING = 6
MAX_CONTRA = 2

# HTTP UA for fetching pages
_UA = {"User-Agent": "Mozilla/5.0 (FactCheckerFusion)"}

# =========================
# DB helpers (cache)
# =========================
def setup_database():
    """Connect to PostgreSQL and ensure cache table exists."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT
        )
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
        print("✅ Database ready.")
        return conn
    except Exception as e:
        print(f"❌ DB error: {e}")
        return None

def normalize_claim(text: str) -> str:
    return " ".join((text or "").split()).lower()

def check_cache(conn, claim_norm):
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT verdict, source_link, explanation, evidence_json
                FROM search_log
                WHERE lower(btrim(user_input)) = lower(btrim(%s));
            """, (claim_norm,))
            row = cur.fetchone()
            if row:
                return {"verdict": row[0], "link": row[1], "explanation": row[2], "evidence": row[3]}
    except Exception as e:
        print(f"Cache check error: {e}")
    return None

def upsert_result(conn, claim_norm, verdict, source_link, explanation=None, evidence_json=None):
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_log (user_input, verdict, source_link, explanation, evidence_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_input) DO UPDATE
                SET verdict = EXCLUDED.verdict,
                    source_link = EXCLUDED.source_link,
                    explanation = EXCLUDED.explanation,
                    evidence_json = EXCLUDED.evidence_json,
                    searched_at = CURRENT_TIMESTAMP;
            """, (
                claim_norm,
                verdict,
                source_link,
                explanation,
                json.dumps(evidence_json) if evidence_json is not None else None
            ))
            conn.commit()
            print("💾 Cached (UPSERT).")
    except Exception as e:
        print(f"Store error: {e}")
        conn.rollback()

# =========================
# Retrieval: Google CSE
# =========================
def search_claim(query):
    """Return {'results':[...]} or {'error': '...'} using Google Custom Search."""
    if not API_KEY:
        return {"error": "Configuration Error: Please set API_KEY."}
    if not SEARCH_ENGINE_ID or "YOUR_SEARCH_ENGINE_ID" in SEARCH_ENGINE_ID:
        return {"error": "Configuration Error: Please set SEARCH_ENGINE_ID."}

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": SEARCH_ENGINE_ID, "q": query, "num": 5}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"results": data.get("items", [])}
    except requests.exceptions.HTTPError as e:
        try:
            msg = e.response.json().get("error", {}).get("message", "")
        except Exception:
            msg = f"HTTP {getattr(e.response,'status_code','?')}: {getattr(e.response,'text','')[:200]}"
        return {"error": f"API Error: {msg or 'Unknown HTTP error'}"}
    except Exception as e:
        return {"error": f"Local error during search: {e}"}

# =========================
# Heuristic verdict from titles/snippets
# =========================
def analyze_verdicts(search_results):
    """Fast keyword-based read on titles+snippets."""
    if not search_results:
        return {
            "best_verdict": "Uncertain",
            "percentages": {"Likely True": 0, "Likely False": 0, "Uncertain": 100},
        }

    supporting_keywords = {
        'confirmed': 3, 'true': 3, 'accurate': 3, 'verified': 3, 'fact': 2,
        'correct': 2, 'supported': 1, 'evidence': 1
    }
    refuting_keywords = {
        'hoax': 3, 'false': 3, 'debunked': 3, 'myth': 3, 'conspiracy': 2,
        'incorrect': 2, 'misleading': 2, 'unproven': 1, 'baseless': 1, 'scam': 2
    }

    support_score = refute_score = 0
    for item in search_results:
        text = f"{item.get('title','')} {item.get('snippet','')}".lower()
        for k, w in supporting_keywords.items():
            if k in text: support_score += w
        for k, w in refuting_keywords.items():
            if k in text: refute_score += w

    total = support_score + refute_score
    if total == 0:
        best = "Fact-Check Found / Uncertain" if any("fact-check" in (i.get('title','').lower()) for i in search_results) else "Uncertain"
        return {"best_verdict": best, "percentages": {"Likely True": 0, "Likely False": 0, "Uncertain": 100}}

    s_pct = round((support_score / total) * 100)
    f_pct = round((refute_score / total) * 100)
    if refute_score > support_score * 1.5:
        best = "Likely False"
    elif support_score > refute_score * 1.5:
        best = "Likely True"
    else:
        best = "Mixed / Uncertain"
    return {"best_verdict": best, "percentages": {"Likely True": s_pct, "Likely False": f_pct}}

# =========================
# Slim NLI Explainer (MiniLM rank + BART-MNLI)
# =========================
_EMBEDDER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
_NLI = pipeline("text-classification", model="facebook/bart-large-mnli")

def _fetch_clean(url: str, timeout=12) -> str:
    try:
        r = requests.get(url, headers=_UA, timeout=timeout)
        r.raise_for_status()
        txt = trafilatura.extract(r.text, include_comments=False, favor_recall=True)
        return (txt or "").strip()
    except Exception:
        return ""

def _sentences(text: str):
    # Simple sentence split; keep medium-length sentences for NLI
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in raw if 40 <= len(s) <= 300][:800]

def _rank_by_similarity(claim: str, sents, top_k: int):
    if not sents: return []
    c_emb = _EMBEDDER.encode([claim], convert_to_tensor=True, normalize_embeddings=True)
    s_emb = _EMBEDDER.encode(sents, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(c_emb, s_emb).cpu().tolist()[0]
    ranked = sorted(zip(sents, sims), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]

def _batch_nli(claim: str, candidates):
    if not candidates: return []
    payload = [{"text": sent, "text_pair": claim} for sent in candidates]
    out = _NLI(payload, truncation=True)
    res = []
    for sent, pred in zip(candidates, out):
        res.append({"sentence": sent, "label": pred["label"].upper(), "score": float(pred["score"])})
    return res

def select_evidence_from_urls(
    claim: str,
    urls,
    max_urls=MAX_URLS,
    per_url_candidates=PER_URL_CANDIDATES,
    entail_threshold=ENTAIL_THRESHOLD,
    contra_threshold=CONTRA_THRESHOLD,
    max_entailing=MAX_ENTAILING,
    max_contra=MAX_CONTRA,
):
    entailing, contradicting = [], []

    for url in urls[:max_urls]:
        text = _fetch_clean(url)
        if not text or len(text) < 400:
            continue
        sents = _sentences(text)
        ranked = _rank_by_similarity(claim, sents, per_url_candidates)
        cand_sents = [s for s, _ in ranked]
        cand_sim = {s: sim for s, sim in ranked}

        nli_out = _batch_nli(claim, cand_sents)
        for pred in nli_out:
            lbl, score, sent = pred["label"], pred["score"], pred["sentence"]
            sim = float(cand_sim.get(sent, 0.0))
            rec = {"url": url, "sentence": sent, "sim": sim, "nli_score": score}
            if lbl == "ENTAILMENT" and score >= entail_threshold:
                entailing.append(rec)
            elif lbl == "CONTRADICTION" and score >= contra_threshold:
                contradicting.append(rec)

    entailing.sort(key=lambda r: (r["nli_score"], r["sim"]), reverse=True)
    contradicting.sort(key=lambda r: (r["nli_score"], r["sim"]), reverse=True)
    return entailing[:max_entailing], contradicting[:max_contra]

def build_explanation(claim: str, entailing, contradicting):
    """Simple, cited explanation (no generator)."""
    from urllib.parse import urlparse

    if not entailing and not contradicting:
        return (
            f"**Claim:** {claim}\n\n"
            "I checked the retrieved sources but didn’t find strong sentence-level support or refutation. "
            "This looks **uncertain** with the current sources."
        )

    # overall tendency (counts only; keep it simple)
    if len(entailing) >= 2 and len(entailing) >= (len(contradicting) + 1):
        trend = "Overall, the strongest snippets **support** the claim."
    elif len(contradicting) >= 2 and len(contradicting) >= (len(entailing) + 1):
        trend = "Overall, the strongest snippets **refute** the claim."
    else:
        trend = "Overall, the evidence is **mixed/uncertain**."

    lines = [f"**Claim:** {claim}", "", "**Evidence (top snippets):**"]
    for i, rec in enumerate(entailing[:3], 1):
        host = urlparse(rec["url"]).netloc
        snip = rec["sentence"].strip()
        if len(snip) > 260: snip = snip[:257] + "..."
        lines.append(f"- [E{i}] {snip}\n  ↪ Source: {host} — {rec['url']}")
    for i, rec in enumerate(contradicting[:2], 1):
        host = urlparse(rec["url"]).netloc
        snip = rec["sentence"].strip()
        if len(snip) > 260: snip = snip[:257] + "..."
        lines.append(f"- [C{i}] {snip}\n  ↪ Source: {host} — {rec['url']}")
    lines += ["", trend]
    return "\n".join(lines)

# =========================
# FUSION (simple rule)
# =========================
def simple_fuse_verdict(heuristic_best_verdict: str, entailing, contradicting) -> str:
    """
    If NLI is clearly strong, trust it; else fallback to the heuristic verdict.
    Rules:
      - Likely True  if entailing >= 2 and entailing >= contradicting + 1
      - Likely False if contradicting >= 2 and contradicting >= entailing + 1
      - Otherwise: return heuristic_best_verdict
    """
    e = len(entailing)
    c = len(contradicting)
    if e >= 2 and e >= c + 1:
        return "Likely True"
    if c >= 2 and c >= e + 1:
        return "Likely False"
    return heuristic_best_verdict

# =========================
# CLI main
# =========================
def main():
    print("--- Fact Checker (Retrieval + Heuristic + Slim NLI + Fusion) ---")
    db = setup_database()
    if not db:
        print("Exiting due to DB failure.")
        return

    try:
        while True:
            raw = input("\nEnter a claim to verify (or 'exit'): ").strip()
            if raw.lower() == "exit":
                break
            if not raw:
                continue

            claim_norm = normalize_claim(raw)

            # 1) Cache first
            cached = check_cache(db, claim_norm)
            if cached:
                print("\n--- Result (Cache) ---")
                print(f"Final Verdict: {cached['verdict']}")
                print(f"Source:        {cached['link']}")
                if cached.get("explanation"):
                    print("\n--- Explanation ---")
                    print(cached["explanation"])
                print("---------------------")
                continue

            # 2) Retrieve
            print(f"\nSearching for: '{raw}' ...")
            search_data = search_claim(raw)  # use raw for recall
            if "error" in search_data:
                print(f"Error: {search_data['error']}")
                continue
            results = search_data.get("results", [])

            print("\n--- Top Sources Found ---")
            if not results:
                print("No sources found.")
            else:
                for i, item in enumerate(results, 1):
                    print(f"{i}. {item.get('title')}\n   {item.get('link')}")
            print("-------------------------")

            # 3) Heuristic verdict (fast)
            heuristic = analyze_verdicts(results)
            print("\n--- Heuristic Verdict ---")
            print(f"{heuristic['best_verdict']}  |  Confidence: {heuristic['percentages']}")
            print("-------------------------")

            # 4) Slim NLI on YOUR links (only if we have results)
            links = [it.get("link") for it in results[:5] if it.get("link")]
            entailing, contradicting = select_evidence_from_urls(raw, links)

            # 5) Fusion → final verdict
            final_verdict = simple_fuse_verdict(heuristic["best_verdict"], entailing, contradicting)
            print("\n=== FINAL VERDICT ===")
            print(final_verdict)
            print("=====================")

            # 6) Human-friendly explanation (cited)
            explanation = build_explanation(raw, entailing, contradicting)
            print("\n--- Explanation ---")
            print(explanation)
            print("-------------------")

            # 7) Persist (UPSERT)
            top_link = results[0].get("link", "No link found.") if results else "No link found."
            evidence_payload = {"entailing": entailing, "contradicting": contradicting,
                                "heuristic": heuristic}
            upsert_result(
                db, claim_norm, final_verdict, top_link,
                explanation=explanation,
                evidence_json=evidence_payload
            )

    finally:
        if db:
            db.close()
            print("\nDB connection closed. Bye!")

if __name__ == "__main__":
    main()
