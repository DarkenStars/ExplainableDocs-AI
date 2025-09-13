import os
from typing import List, Dict, Any

from dotenv import load_dotenv, find_dotenv
import httpx

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv(find_dotenv())

def resolve_verify_url() -> str:
    api = os.getenv("API_URL", "http://127.0.0.1:5000").strip()
    explicit = os.getenv("INTERNAL_VERIFY_URL", "").strip()
    base = (explicit or api).rstrip("/")
    if not base.endswith("/verify"):
        base = base + "/verify"
    print(f"[bot] Using verify endpoint: {base}")  
    return base

# ---- Config ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  
INTERNAL_VERIFY_URL = resolve_verify_url()    
TG_MAX_SOURCES = int(os.getenv("TG_MAX_SOURCES", "5"))
TG_TEXT_LIMIT = int(os.getenv("TG_TEXT_LIMIT", "4000"))  

# ----------------- Utilities -----------------
def _chunk(text: str, limit: int = TG_TEXT_LIMIT) -> List[str]:
    """Split long text into message-sized chunks, preferably at newlines."""
    text = text or ""
    parts: List[str] = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:]
    if text:
        parts.append(text)
    return parts

def _format_reply(data: Dict[str, Any]) -> str:
    """Build a friendly reply from /verify response JSON."""
    verdict_map = {"true": "✅ TRUE", "false": "❌ FALSE", "uncertain": "⚠️ UNCERTAIN"}
    verdict = str(data.get("verdict", "uncertain")).lower()
    confidence = int(data.get("confidence", 0))
    explanation = data.get("explanation", "No explanation available.") or "No explanation available."
    sources = data.get("sources", []) or []

    lines = [
        f"Verdict: {verdict_map.get(verdict, verdict.upper())}",
        f"Confidence: {confidence}%",
        "",
        f"Why: {explanation}",
        "",
        "Sources:",
    ]
    for i, s in enumerate(sources[:TG_MAX_SOURCES], 1):
        title = (s.get("title") or "Source").strip()
        url = s.get("url") or s.get("link") or "#"
        lines.append(f"{i}. {title}\n{url}")

    lines.append("\nSend another claim to check.")
    return "\n".join(lines)

# Handlers 
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Send me any claim and I’ll fact-check it for you.\n\n"
        'Example: "The Great Wall of China is visible from space."'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Please send a text claim.")
        return

    client: httpx.AsyncClient = context.application.bot_data["http_client"]

    try:
        # Call FastAPI backend /verify
        resp = await client.post(
            INTERNAL_VERIFY_URL,
            json={"message": text, "max_results": 10},
            timeout=40.0,
        )
        if resp.status_code >= 400:
            # helpful debug
            body = await resp.aread()
            await update.message.reply_text(
                f"Error reaching fact-checker service (HTTP {resp.status_code}) at {INTERNAL_VERIFY_URL}\n"
                f"{body[:500]!r}"
            )
            return

        data = resp.json()
        reply = _format_reply(data)

    except Exception as e:
        reply = f"Error reaching fact-checker service: {e}"

    for part in _chunk(reply):
        await update.message.reply_text(part)

# App lifecycle 
async def _post_init(app: Application) -> None:
    # Create one shared AsyncClient for all requests
    app.bot_data["http_client"] = httpx.AsyncClient(follow_redirects=True)

async def _post_shutdown(app: Application) -> None:
    client: httpx.AsyncClient = app.bot_data.get("http_client")
    if client:
        await client.aclose()

def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is not set in the environment.")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.post_init = _post_init
    application.post_shutdown = _post_shutdown

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running (polling). Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()