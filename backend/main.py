import os
import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv() 

API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

def setup_database():
    """Connects to PostgreSQL and creates the search_log table if it doesn't exist."""
    # (This function remains the same)
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        print("Database connection established.")
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS search_log (
                    id SERIAL PRIMARY KEY,
                    user_input TEXT NOT NULL UNIQUE,
                    verdict TEXT,
                    source_link TEXT,
                    searched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Table 'search_log' is ready.")
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to the database: {e}")
        return None


def check_database_for_claim(conn, user_input):
    """Checks the database for a previously searched claim."""
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT verdict, source_link FROM search_log WHERE user_input = %s", (user_input,))
            result = cur.fetchone()
            if result:
                return {"verdict": result[0], "link": result[1]}
    except Exception as e:
        print(f"Error checking database cache: {e}")
    return None


def search_claim(query):
    """Searches for a claim using the Google Custom Search API, fetching up to 5 results."""
    if not SEARCH_ENGINE_ID or "YOUR_SEARCH_ENGINE_ID" in SEARCH_ENGINE_ID:
        return {"error": "Configuration Error: Please set your SEARCH_ENGINE_ID."}
    
    url = "https://www.googleapis.com/customsearch/v1"
    # Request 5 results instead of the default
    params = {"key": API_KEY, "cx": SEARCH_ENGINE_ID, "q": query, "num": 5}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()

        if "items" in results and len(results["items"]) > 0:
            return {"results": results["items"]}
        else:
            return {"results": []}
            
    except requests.exceptions.HTTPError as e:
        error_message = e.response.json().get("error", {}).get("message", "An unknown HTTP error occurred.")
        return {"error": f"API Error: {error_message}"}
    except Exception as e:
        return {"error": f"A local error occurred during search: {e}"}


def analyze_verdicts(search_results):
    """
    Analyzes snippets from search results to determine a likely verdict using
    expanded and weighted keywords.
    """
    if not search_results:
        return {
            "best_verdict": "Uncertain",
            "percentages": {"Likely True": 0, "Likely False": 0, "Uncertain": 100},
        }

    # Expanded keyword lists with weights
    supporting_keywords = {
        'confirmed': 3, 'true': 3, 'accurate': 3, 'verified': 3, 'fact': 2,
        'correct': 2, 'supported': 1, 'evidence': 1
    }
    refuting_keywords = {
        'hoax': 3, 'false': 3, 'debunked': 3, 'myth': 3, 'conspiracy': 2,
        'incorrect': 2, 'misleading': 2, 'unproven': 1, 'baseless': 1, 'scam': 2
    }

    support_score = 0
    refute_score = 0

    for item in search_results:
        snippet = item.get('snippet', '').lower()
        title = item.get('title', '').lower()
        text_to_analyze = f"{title} {snippet}" # Analyze both title and snippet

        for keyword, weight in supporting_keywords.items():
            if keyword in text_to_analyze:
                support_score += weight
        for keyword, weight in refuting_keywords.items():
            if keyword in text_to_analyze:
                refute_score += weight

    total_score = support_score + refute_score
    if total_score == 0:
        # Fallback: Check for softer indicators if no strong keywords are found
        if any("fact-check" in item.get('title','').lower() for item in search_results):
             best_verdict = "Fact-Check Found / Uncertain"
        else:
             best_verdict = "Uncertain"
        
        return {
            "best_verdict": best_verdict,
            "percentages": {"Likely True": 0, "Likely False": 0, "Uncertain": 100},
        }

    # Calculate percentages
    support_percent = round((support_score / total_score) * 100)
    refute_percent = round((refute_score / total_score) * 100)

    # Determine best verdict based on scores
    if refute_score > support_score * 1.5: # Require a stronger signal for a "False" verdict
        best_verdict = "Likely False"
    elif support_score > refute_score * 1.5:
        best_verdict = "Likely True"
    else:
        best_verdict = "Mixed / Uncertain"

    return {
        "best_verdict": best_verdict,
        "percentages": {
            "Likely True": support_percent,
            "Likely False": refute_percent,
        },
    }

def store_result(conn, user_input, verdict, source_link):
    """Stores the user input and the search result in the PostgreSQL database."""
    # (This function remains the same)
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO search_log (user_input, verdict, source_link) VALUES (%s, %s, %s)",
                (user_input, verdict, source_link),
            )
            conn.commit()
            print("\nResult stored in the database for future reference.")
    except Exception as e:
        print(f"Failed to store result in the database: {e}")
        conn.rollback()


def main():
    """Main function to run the fact-checker loop."""
    print("--- Local Fact Checker ---")
    db_connection = setup_database()
    if not db_connection:
        print("\nExiting due to database connection failure.")
        return

    try:
        while True:
            user_input = input("\nEnter a claim to verify (or type 'exit' to quit): ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue
            
            # 1. CHECK CACHE FIRST
            cached_result = check_database_for_claim(db_connection, user_input)
            if cached_result:
                print("\n--- Result Found in Database Cache ---")
                print(f"Verdict: {cached_result['verdict']}")
                print(f"Source: {cached_result['link']}")
                print("------------------------------------")
                continue

            # 2. IF NOT IN CACHE, SEARCH ONLINE
            print(f"\nSearching for: '{user_input}'...")
            search_data = search_claim(user_input)
            
            if "error" in search_data:
                print(f"Error: {search_data['error']}")
                continue

            search_results = search_data.get("results", [])

            # 3. ANALYZE AND DISPLAY RESULTS
            analysis = analyze_verdicts(search_results)

            print("\n--- Analysis ---")
            print(f"Best Possible Verdict: {analysis['best_verdict']}")
            print(f"Confidence: {analysis['percentages']}")
            print("----------------")
            
            print("\n--- Top Sources Found ---")
            if not search_results:
                print("No sources were found.")
            else:
                for i, item in enumerate(search_results):
                    print(f"{i+1}. {item.get('title')}")
                    print(f"   Link: {item.get('link')}")
            print("-------------------------")
            
            # 4. STORE THE NEW RESULT IN THE DATABASE
            if search_results:
                # We now store the ANALYZED verdict, not the raw snippet.
                analyzed_verdict_to_store = analysis['best_verdict']
                top_link = search_results[0].get('link', 'No link found.')
                store_result(db_connection, user_input, analyzed_verdict_to_store, top_link)

    finally:
        if db_connection:
            db_connection.close()
            print("\nDatabase connection closed. Program finished.")


if __name__ == "__main__":
    main()