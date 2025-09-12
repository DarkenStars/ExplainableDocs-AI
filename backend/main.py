# main.py
import os
import re
import json
import requests
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse
from ml_models import select_evidence_from_urls
from text_polisher import polish_text 


# Config and other functions...
load_dotenv()
API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

def setup_database():
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
    return " ".join((text or "").split()).lower()

def check_cache(conn, claim_norm):
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
            print("Cached (UPSERT).")
    except Exception as e:
        print(f"Store error: {e}")
        conn.rollback()

def search_claim(query):
    if not API_KEY: return {"error": "Configuration Error: Please set API_KEY."}
    if not SEARCH_ENGINE_ID: return {"error": "Configuration Error: Please set SEARCH_ENGINE_ID."}
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": SEARCH_ENGINE_ID, "q": query, "num": 5}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return {"results": resp.json().get("items", [])}
    except Exception as e:
        return {"error": f"Search API error: {e}"}

def analyze_verdicts(search_results):
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

def build_explanation(claim: str, entailing, contradicting):
    """
    Builds a more detailed, factual explanation from multiple pieces of evidence.
    This provides a rich input for the text polisher.
    """
    # No strong evidence found either way.
    if not entailing and not contradicting:
        return f"After a review of top sources, no strong sentence-level evidence was found to either support or refute the claim that '{claim}'."

    # Evidence is strongly refuting.
    if len(contradicting) >= 2 and len(contradicting) >= len(entailing) + 1:
        trend = f"evidence strongly suggests the claim that '{claim}' is false"
        # Combine the top 2-3 refuting snippets into one string.
        evidence_snippets = [f"\"{ev['sentence']}\"" for ev in contradicting[:3]]
        all_evidence_text = " ".join(evidence_snippets)
        return f"Regarding the claim, the {trend}. For example, key sources state that {all_evidence_text}"
        
    # Evidence is strongly supporting.
    elif len(entailing) >= 2 and len(entailing) >= len(contradicting) + 1:
        trend = f"the evidence tends to support the claim that '{claim}'"
        # Combine the top 2-3 supporting snippets into one string.
        evidence_snippets = [f"\"{ev['sentence']}\"" for ev in entailing[:3]]
        all_evidence_text = " ".join(evidence_snippets)
        return f"In reference to the claim, {trend}. For instance, relevant sources mention that {all_evidence_text}"
    
    # Evidence is mixed or inconclusive. Show both sides.
    else:
        # Get the top supporting and refuting snippets, if they exist.
        top_support = f"\"{entailing[0]['sentence']}\"" if entailing else ""
        top_refute = f"\"{contradicting[0]['sentence']}\"" if contradicting else ""

        if top_support and top_refute:
            return f"The evidence regarding '{claim}' is mixed. For example, one source supports it by stating {top_support}, while another refutes it, mentioning {top_refute}."
        elif top_support: 
             return f"The evidence regarding '{claim}' is inconclusive but leans supportive, with one source stating {top_support}."
        elif top_refute: 
             return f"The evidence regarding '{claim}' is inconclusive but leans negative, with one source mentioning {top_refute}."
        else:
             return f"The evidence regarding the claim '{claim}' is inconclusive based on a review of the top online sources."

def simple_fuse_verdict(heuristic_best_verdict: str, entailing, contradicting) -> str:
    e, c = len(entailing), len(contradicting)
    if e >= 2 and e >= c + 1: return "Likely True"
    if c >= 2 and c >= e + 1: return "Likely False"
    return heuristic_best_verdict

def main():
    print("--- Fact Checker (with Text Polishing) ---")
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

            print("\nPerforming deep analysis on sources...")
            links = [it.get("link") for it in results[:10] if it.get("link")]
            entailing, contradicting = select_evidence_from_urls(raw, links)

            final_verdict = simple_fuse_verdict(heuristic["best_verdict"], entailing, contradicting)
            print("\n=== FINAL VERDICT ===")
            print(final_verdict)
            print("=====================")

            # Build the structured explanation
            structured_explanation = build_explanation(raw, entailing, contradicting)
            
            # Polish the text to make it sound more natural
            print("\nPolishing language...")
            polished_explanation = polish_text(structured_explanation)

            print("\n--- Explanation ---")
            print(polished_explanation)
            print("-------------------")
            
            # Store the single, polished explanation in the database
            top_link = results[0].get("link") if results else "No link found."
            evidence_payload = {"entailing": entailing, "contradicting": contradicting, "heuristic": heuristic}
            upsert_result(db, claim_norm, final_verdict, top_link, explanation=polished_explanation, evidence_json=evidence_payload)

    finally:
        if db:
            db.close()
            print("\nDB connection closed. Bye!")

if __name__ == "__main__":
    main()