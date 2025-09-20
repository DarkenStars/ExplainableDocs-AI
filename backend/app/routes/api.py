"""API routes for the fact-checker application."""

import time
from typing import List
from collections import defaultdict
from fastapi import APIRouter, HTTPException

from ..models.schemas import VerifyRequest, VerifyResponse, Source, EvidenceBundle, EvidenceItem
from ..database.db_manager import get_conn, put_conn, check_cache, upsert_result, setup_database
from ..services.fact_checker import search_claim, analyze_verdicts, build_explanation, simple_fuse_verdict
from ..utils.helpers import get_evidence_url, calculate_confidence, truncate_text, normalize_claim
from ..config import config

# Import ML models from parent directory
from ml_models import select_evidence_from_urls
from text_polisher import polish_text

# Create API router
router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": config.APP_TITLE}


@router.post("/verify", response_model=VerifyResponse)
def verify_claim(payload: VerifyRequest):
    """Verify a fact-checking claim."""
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
                verdict=verdict, 
                confidence=85,
                explanation=cached.get("explanation") or "Cached result",
                sources=sources, 
                evidence=evidence_bundle,
                processing_time=elapsed
            )
        
        # Search web
        search_data = search_claim(
            claim, 
            num=max_results, 
            api_key=config.API_KEY, 
            search_engine_id=config.SEARCH_ENGINE_ID
        )
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
        confidence = calculate_confidence(final_verdict, entailing, contradicting)

        # Per-URL evidence buckets
        per_url_ev = defaultdict(lambda: {"support": [], "refute": []})
        
        for ev in entailing:
            u = get_evidence_url(ev)
            if u:
                per_url_ev[u]["support"].append(ev.get("sentence", ""))
        for ev in contradicting:
            u = get_evidence_url(ev)
            if u:
                per_url_ev[u]["refute"].append(ev.get("sentence", ""))

        # Build ALL sources with stance and evidence lines
        sources: List[Source] = []
        for i, item in enumerate(results, 1):
            url = item.get("link") or "#"
            org = item.get("displayLink") or "Web"
            title = truncate_text(item.get("title") or "Unknown Source", 200)
            snippet = truncate_text(item.get("snippet") or "", 400)

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
            support=[EvidenceItem(url=get_evidence_url(ev), sentence=ev.get("sentence", "")) for ev in entailing],
            refute=[EvidenceItem(url=get_evidence_url(ev), sentence=ev.get("sentence", "")) for ev in contradicting],
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