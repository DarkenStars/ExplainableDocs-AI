"""Utility functions and helpers."""

from typing import Dict, Any, List


def normalize_claim(text: str) -> str:
    """Normalize claim text for processing and comparison."""
    return " ".join((text or "").split()).lower()


def get_evidence_url(evidence: Dict[str, Any]) -> str:
    """Extract URL from evidence item, checking multiple possible keys."""
    return evidence.get("url") or evidence.get("source") or evidence.get("link") or ""


def calculate_confidence(final_verdict: str, entailing: List[Dict], contradicting: List[Dict]) -> int:
    """Calculate confidence score based on verdict and evidence strength."""
    confidence = 75
    
    if final_verdict in ["true", "false"]:
        confidence = 90
    
    if len(entailing) >= 2 or len(contradicting) >= 2:
        confidence = min(95, confidence + 10)
    
    return confidence


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to maximum length."""
    if not text:
        return ""
    return text[:max_length] if len(text) > max_length else text