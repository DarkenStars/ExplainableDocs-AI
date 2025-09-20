"""Pydantic models and schemas for the application."""

from typing import List, Optional
from pydantic import BaseModel

# Import Literal properly
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore


class VerifyRequest(BaseModel):
    """Request model for fact verification."""
    message: str
    max_results: Optional[int] = 5  # up to 10 per Google CSE


class EvidenceItem(BaseModel):
    """Individual piece of evidence."""
    url: Optional[str] = None
    sentence: str


class EvidenceBundle(BaseModel):
    """Bundle of supporting and refuting evidence."""
    support: List[EvidenceItem] = []
    refute: List[EvidenceItem] = []


class Source(BaseModel):
    """Source information with evidence and stance."""
    id: int
    title: str
    url: str
    organization: str
    snippet: Optional[str] = None
    stance: Literal["support", "refute", "mixed", "neutral"] = "neutral"
    evidence_sentences: List[str] = []


class VerifyResponse(BaseModel):
    """Response model for fact verification."""
    verdict: Literal["true", "false", "uncertain"]
    confidence: int
    explanation: str
    sources: List[Source]          # ALL sources with stance & evidence lines
    evidence: EvidenceBundle       # Flat lists grouped by side
    processing_time: float