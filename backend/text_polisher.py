# polisher.py
from transformers import pipeline, AutoTokenizer
from transformers.utils import logging as hf_logging

print("Loading text polishing model... (This may take a moment on first run)")
hf_logging.set_verbosity_error()  # hide HF generation-length warnings

MODEL_NAME = "google/pegasus-xsum"

try:
    _POLISHER = pipeline(
        "summarization",
        model=MODEL_NAME,
        # If you have a GPU and torch cuda is available, uncomment:
        device_map="auto"
    )
    _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
    print("Polishing model loaded successfully.")
except Exception as e:
    print(f"ERROR: Could not load polishing model. Details: {e}")
    _POLISHER = None
    _TOKENIZER = None

def _token_len(text: str) -> int:
    if not _TOKENIZER:
        # rough fallback: characters/4 ~ tokens
        return max(1, len(text) // 4)
    ids = _TOKENIZER(text, return_tensors="pt", truncation=True).input_ids
    return ids.shape[1]

def polish_text(input_text: str) -> str:
    """
    Rewrites the input to be smoother/clearer while keeping it concise.
    Uses summarization as a controlled paraphrase.
    """
    if not _POLISHER or not input_text or len(input_text.strip()) < 15:
        return input_text

    in_tok = _token_len(input_text)

    # Very short inputs: don't touch
    if in_tok < 30:
        return input_text

    # Keep output clearly shorter than input, suitable for "polishing"
    # Clamp to safe, model-friendly bounds.
    max_new = max(24, min(160, int(in_tok * 0.5)))   # ~50% of input tokens
    min_new = max(12, min(max_new - 6, int(in_tok * 0.25)))  # ~25% of input tokens

    try:
        out = _POLISHER(
            input_text,
            max_new_tokens=max_new,
            min_new_tokens=min_new,
            do_sample=False,
            num_beams=4,
            no_repeat_ngram_size=3,
            early_stopping=True,
            clean_up_tokenization_spaces=True,
        )
        return out[0]["summary_text"]
    except Exception as e:
        print(f"Error during text polishing: {e}")
        return input_text