import re
import requests
import trafilatura
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

# --- Configuration ---
MAX_URLS = 10
PER_URL_CANDIDATES = 8
ENTAIL_THRESHOLD = 0.72
CONTRA_THRESHOLD = 0.72
MAX_ENTAILING = 6
MAX_CONTRA = 2

_UA = {"User-Agent": "Mozilla/5.0 (FactCheckerFusion)"}

# --- Model Loading ---
print("Loading ML models... (This may take a moment on first run)")
try:
    _EMBEDDER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    _NLI = pipeline("text-classification", model="facebook/bart-large-mnli")
    print("Models loaded successfully.")
except Exception as e:
    print(f"ERROR: Could not load models. Please check your internet connection and libraries. Details: {e}")
    _EMBEDDER = None
    _NLI = None


# --- Helper Functions ---
def _fetch_clean(url: str, timeout=12) -> str:
    try:
        r = requests.get(url, headers=_UA, timeout=timeout)
        r.raise_for_status()
        txt = trafilatura.extract(r.text, include_comments=False, favor_recall=True)
        return (txt or "").strip()
    except Exception:
        return ""

def _sentences(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in raw if 40 <= len(s) <= 300][:800]

def _rank_by_similarity(claim: str, sents, top_k: int):
    if not sents or not _EMBEDDER: return []
    c_emb = _EMBEDDER.encode([claim], convert_to_tensor=True, normalize_embeddings=True)
    s_emb = _EMBEDDER.encode(sents, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(c_emb, s_emb).cpu().tolist()[0]
    ranked = sorted(zip(sents, sims), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]

def _batch_nli(claim: str, candidates):
    if not candidates or not _NLI: return []
    payload = [{"text": sent, "text_pair": claim} for sent in candidates]
    out = _NLI(payload, truncation=True, max_length=512)
    res = []
    for sent, pred in zip(candidates, out):
        res.append({"sentence": sent, "label": pred["label"].upper(), "score": float(pred["score"])})
    return res


# --- Main NLI Explainer Function ---
def select_evidence_from_urls(claim: str, urls):
    """
    Main function to extract and classify evidence from a list of URLs.
    """
    if not _EMBEDDER or not _NLI:
        print("Cannot select evidence because ML models are not loaded.")
        return [], []

    entailing, contradicting = [], []
    for url in urls[:MAX_URLS]:
        print(f"   ...fetching & analyzing {url}")
        text = _fetch_clean(url)
        if not text or len(text) < 400:
            continue
        
        sents = _sentences(text)
        ranked = _rank_by_similarity(claim, sents, PER_URL_CANDIDATES)
        cand_sents = [s for s, _ in ranked]
        cand_sim = {s: sim for s, sim in ranked}

        nli_out = _batch_nli(claim, cand_sents)
        for pred in nli_out:
            lbl, score, sent = pred["label"], pred["score"], pred["sentence"]
            sim = float(cand_sim.get(sent, 0.0))
            rec = {"url": url, "sentence": sent, "sim": sim, "nli_score": score}
            
            if lbl == "ENTAILMENT" and score >= ENTAIL_THRESHOLD:
                entailing.append(rec)
            elif lbl == "CONTRADICTION" and score >= CONTRA_THRESHOLD:
                contradicting.append(rec)

    entailing.sort(key=lambda r: (r["nli_score"], r["sim"]), reverse=True)
    contradicting.sort(key=lambda r: (r["nli_score"], r["sim"]), reverse=True)
    return entailing[:MAX_ENTAILING], contradicting[:MAX_CONTRA]