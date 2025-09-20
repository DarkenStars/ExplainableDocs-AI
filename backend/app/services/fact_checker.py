"""Fact-checking service with search and analysis functionality."""

import os
import re
import requests
from typing import Dict, List, Any
from collections import defaultdict


def search_claim(query: str, num: int = 10, api_key: str = None, search_engine_id: str = None) -> Dict[str, Any]:
    """Search for information about a claim using Google Custom Search."""
    if not api_key:
        return {"error": "Configuration Error: Please set API_KEY."}
    if not search_engine_id:
        return {"error": "Configuration Error: Please set SEARCH_ENGINE_ID."}
    
    num = max(1, min(int(num or 10), 10))  # Google CSE max per call = 10

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query, "num": num}
    
    try:
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        return {"results": resp.json().get("items", [])}
    except Exception as e:
        return {"error": f"Search API error: {e}"}


def analyze_verdicts_improved(search_results: List[Dict]) -> Dict[str, Any]:
    """
    Analyzes search results with improved accuracy by using whole word matching,
    counting keyword frequency, handling basic negation, and weighting sources.
    """
    if not search_results:
        return {"best_verdict": "uncertain", "percentages": {"true": 0, "false": 0, "uncertain": 100}}

    # Keywords with weights. Using more specific, powerful words is key.
    supporting_keywords = {
        'confirmed': 3, 'verified': 3, 'accurate': 3, 'fact-check: true': 4, 
        'correct': 2, 'evidence': 1
    }
    refuting_keywords = {
        'hoax': 3, 'false': 3, 'debunked': 3, 'myth': 3, 'fact-check: false': 4, 
        'incorrect': 2, 'misleading': 2, 'baseless': 1
    }
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
        text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
        source_url = item.get('source', '')
        
        # Determine the weight for the current source
        item_weight = default_weight
        for domain, weight in source_weights.items():
            if domain in source_url:
                item_weight = weight
                break  # Stop after finding the first match

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


def build_explanation(claim: str, entailing: List[Dict], contradicting: List[Dict]) -> str:
    """Build an explanation based on evidence found."""
    if not entailing and not contradicting:
        return f"After reviewing top sources, no strong evidence was found to either support or refute the claim about '{claim}'."
    
    if len(contradicting) >= 2 and len(contradicting) >= len(entailing) + 1:
        evidence_snippets = [f'"{ev.get("sentence", "")}"' for ev in contradicting[:2]]
        return f"Evidence strongly suggests the claim about '{claim}' is false. Key sources state: {' '.join(evidence_snippets)}"
    elif len(entailing) >= 2 and len(entailing) >= len(contradicting) + 1:
        evidence_snippets = [f'"{ev.get("sentence", "")}"' for ev in entailing[:2]]
        return f"Evidence tends to support the claim about '{claim}'. Relevant sources mention: {' '.join(evidence_snippets)}"
    else:
        return f"The evidence regarding '{claim}' is mixed and inconclusive based on available sources."


def simple_fuse_verdict(heuristic_best_verdict: str, entailing: List[Dict], contradicting: List[Dict]) -> str:
    """Fuse heuristic verdict with ML evidence to get final verdict."""
    e, c = len(entailing), len(contradicting)
    
    if e >= 2 and e >= c + 1:
        return "true"
    if c >= 2 and c >= e + 1:
        return "false"
    
    return heuristic_best_verdict


# Legacy function name mapping for backward compatibility
def analyze_verdicts(search_results: List[Dict]) -> Dict[str, Any]:
    """Legacy function name - calls analyze_verdicts_improved."""
    return analyze_verdicts_improved(search_results)