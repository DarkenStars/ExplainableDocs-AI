# main.py
import os
import re
import json
import requests
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

# Import the ML logic from our new file
from ml_models import select_evidence_from_urls

# =========================
# Config
# =========================
load_dotenv()

API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

# =========================
# DB helpers, Retrieval, Heuristic Analysis
# (These functions remain here as they are part of the core app logic)
# =========================

def setup_database():
    # (code is unchanged)
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT
        )
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_log (
                    id SERIAL PRIMARY KEY, user_input TEXT NOT NULL UNIQUE,
                    verdict TEXT, source_link TEXT, explanation TEXT,
                    evidence_json JSONB, searched_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS search_log_user_input_norm_idx
                ON search_log ((lower(btrim(user_input))));
            """)
            conn.commit()
        print("Database ready.")
        return conn
    except Exception as e:
        print(f"DB error: {e}")
        return None

def normalize_claim(text: str) -> str:
    # (code is unchanged)
    return " ".join((text or "").split()).lower()

def check_cache(conn, claim_norm):
    # (code is unchanged)
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT verdict, source_link, explanation, evidence_json
                FROM search_log WHERE lower(btrim(user_input)) = lower(btrim(%s));
            """, (claim_norm,))
            row = cur.fetchone()
            if row:
                return {"verdict": row[0], "link": row[1], "explanation": row[2], "evidence": row[3]}
    except Exception as e:
        print(f"Cache check error: {e}")
    return None

def upsert_result(conn, claim_norm, verdict, source_link, explanation=None, evidence_json=None):
    # (code is unchanged)
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_log (user_input, verdict, source_link, explanation, evidence_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_input) DO UPDATE SET
                    verdict = EXCLUDED.verdict, source_link = EXCLUDED.source_link,
                    explanation = EXCLUDED.explanation, evidence_json = EXCLUDED.evidence_json,
                    searched_at = CURRENT_TIMESTAMP;
            """, (
                claim_norm, verdict, source_link, explanation,
                json.dumps(evidence_json) if evidence_json is not None else None
            ))
            conn.commit()
            print("💾 Cached (UPSERT).")
    except Exception as e:
        print(f"Store error: {e}")
        conn.rollback()

def search_claim(query):
    # (code is unchanged)
    if not API_KEY: return {"error": "Configuration Error: Please set API_KEY."}
    if not SEARCH_ENGINE_ID: return {"error": "Configuration Error: Please set SEARCH_ENGINE_ID."}
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": SEARCH_ENGINE_ID, "q": query, "num": 10}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return {"results": resp.json().get("items", [])}
    except Exception as e:
        return {"error": f"Search API error: {e}"}

def analyze_verdicts(search_results):
    # (code is unchanged)
    # This heuristic analysis is fast and part of the main logic flow
    if not search_results:
        return {"best_verdict": "Uncertain", "percentages": {"Likely True": 0, "Likely False": 0, "Uncertain": 100}}
    supporting_keywords = {'confirmed': 3, 'true': 3, 'accurate': 3, 'verified': 3, 'fact': 2, 'correct': 2, 'supported': 1, 'evidence': 1}
    refuting_keywords = {'hoax': 3, 'false': 3, 'debunked': 3, 'myth': 3, 'conspiracy': 2, 'incorrect': 2, 'misleading': 2, 'unproven': 1, 'baseless': 1, 'scam': 2}
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
    if refute_score > support_score * 1.5: best = "Likely False"
    elif support_score > refute_score * 1.5: best = "Likely True"
    else: best = "Mixed / Uncertain"
    return {"best_verdict": best, "percentages": {"Likely True": s_pct, "Likely False": f_pct}}


# =========================
# Explanation, Fusion, and Main CLI
# =========================

def build_explanation(claim: str, entailing, contradicting):
    # (code is unchanged)
    if not entailing and not contradicting:
        return (f"**Claim:** {claim}\n\nI checked the retrieved sources but didn’t find strong sentence-level support or refutation.")
    if len(entailing) >= 2 and len(entailing) >= (len(contradicting) + 1): trend = "Overall, the strongest snippets **support** the claim."
    elif len(contradicting) >= 2 and len(contradicting) >= (len(entailing) + 1): trend = "Overall, the strongest snippets **refute** the claim."
    else: trend = "Overall, the evidence is **mixed/uncertain**."
    lines = [f"**Claim:** {claim}", "", "**Evidence (top snippets):**"]
    for i, rec in enumerate(entailing[:3], 1):
        host = urlparse(rec["url"]).netloc
        snip = rec["sentence"].strip()[:257] + "..." if len(rec["sentence"].strip()) > 260 else rec["sentence"].strip()
        lines.append(f"- [E{i}] {snip}\n  ↪ Source: {host} — {rec['url']}")
    for i, rec in enumerate(contradicting[:2], 1):
        host = urlparse(rec["url"]).netloc
        snip = rec["sentence"].strip()[:257] + "..." if len(rec["sentence"].strip()) > 260 else rec["sentence"].strip()
        lines.append(f"- [C{i}] {snip}\n  ↪ Source: {host} — {rec['url']}")
    lines += ["", trend]
    return "\n".join(lines)


def simple_fuse_verdict(heuristic_best_verdict: str, entailing, contradicting) -> str:
    # (code is unchanged)
    e, c = len(entailing), len(contradicting)
    if e >= 2 and e >= c + 1: return "Likely True"
    if c >= 2 and c >= e + 1: return "Likely False"
    return heuristic_best_verdict


def main():
    print("--- Fact Checker (Retrieval + Heuristic + Slim NLI + Fusion) ---")
    db = setup_database()
    if not db:
        print("Exiting due to DB failure.")
        return

    try:
        while True:
            raw = input("\nEnter a claim to verify (or 'exit'): ").strip()
            if raw.lower() == "exit": break
            if not raw: continue
            
            claim_norm = normalize_claim(raw)

            cached = check_cache(db, claim_norm)
            if cached:
                print("\n--- Result (Cache) ---")
                print(f"Final Verdict: {cached['verdict']}\nSource: {cached['link']}")
                if cached.get("explanation"):
                    print("\n--- Explanation ---\n" + cached["explanation"])
                print("---------------------")
                continue

            print(f"\nSearching for: '{raw}' ...")
            search_data = search_claim(raw)
            if "error" in search_data:
                print(f"Error: {search_data['error']}")
                continue
            
            results = search_data.get("results", [])
            print("\n--- Top Sources Found ---")
            if not results: print("No sources found.")
            else:
                for i, item in enumerate(results, 1):
                    print(f"{i}. {item.get('title')}\n   {item.get('link')}")
            print("-------------------------")

            heuristic = analyze_verdicts(results)
            print("\n--- Heuristic Verdict ---")
            print(f"{heuristic['best_verdict']}  |  Confidence: {heuristic['percentages']}")
            print("-------------------------")

            print("\n🔬 Performing deep analysis on sources...")
            links = [it.get("link") for it in results[:5] if it.get("link")]
            entailing, contradicting = select_evidence_from_urls(raw, links)

            final_verdict = simple_fuse_verdict(heuristic["best_verdict"], entailing, contradicting)
            print("\n=== FINAL VERDICT ===")
            print(final_verdict)
            print("=====================")

            explanation = build_explanation(raw, entailing, contradicting)
            print("\n--- Explanation ---\n" + explanation)
            print("-------------------")
            
            top_link = results[0].get("link") if results else "No link found."
            evidence_payload = {"entailing": entailing, "contradicting": contradicting, "heuristic": heuristic}
            upsert_result(db, claim_norm, final_verdict, top_link, explanation=explanation, evidence_json=evidence_payload)

    finally:
        if db:
            db.close()
            print("\nDB connection closed. Bye!")

if __name__ == "__main__":
    main()