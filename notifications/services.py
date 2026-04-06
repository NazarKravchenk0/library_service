from django.conf import settings
import requests


TELEGRAM_API_TIMEOUT = 10


def _get_bot_api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"


def get_telegram_updates() -> list[dict]:
    if not settings.TELEGRAM_BOT_TOKEN:
        return []

    response = requests.get(
        _get_bot_api_url("getUpdates"),
        timeout=TELEGRAM_API_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("result", [])


def resolve_chat_id() -> str:
    if settings.TELEGRAM_CHAT_ID:
        return settings.TELEGRAM_CHAT_ID

    updates = get_telegram_updates()
    for update in reversed(updates):
        message = update.get("message") or update.get("channel_post")
        chat = (message or {}).get("chat", {})
        chat_id = chat.get("id")
        if chat_id is not None:
            return str(chat_id)
    return ""


def send_telegram_message(message: str) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN or not message:
        return False

    chat_id = resolve_chat_id()
    if not chat_id:
        return False

    response = requests.post(
        _get_bot_api_url("sendMessage"),
        json={"chat_id": chat_id, "text": message},
        timeout=TELEGRAM_API_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    return bool(payload.get("ok"))
