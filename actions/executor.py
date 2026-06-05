"""
Executor — NLU dan kelgan tuzilgan buyruqni olib, mos amalni bajaradi.

Kirish: {"action": ..., "params": {...}, "reply": "..."}
Chiqish: foydalanuvchiga ko'rsatiladigan/aytiladigan natija matni (str).
"""

import config
from actions import apps, system, automation, web


# Tasdiq talab qiladigan xavfli amallar
_DANGEROUS = {
    ("power", "shutdown"),
    ("power", "restart"),
    ("power", "logoff"),
}


def is_dangerous(action: str, params: dict) -> bool:
    return (action, (params or {}).get("operation")) in _DANGEROUS


def execute(command: dict) -> str:
    """Buyruqni bajaradi va natija matnini qaytaradi."""
    action = command.get("action", "unknown")
    params = command.get("params", {}) or {}
    reply = command.get("reply", "") or ""

    try:
        result = _dispatch(action, params)
    except Exception as e:
        return f"Amalni bajarishda xato: {e}"

    # LLM bergan "reply" bo'lsa, uni asosiy javob qilamiz; amal natijasini qo'shamiz.
    if action in ("chat", "unknown"):
        return reply or result
    if reply and result and reply != result:
        return reply
    return result or reply


def _dispatch(action: str, params: dict) -> str:
    if action == "open_app":
        return apps.open_app(params.get("name", ""))
    if action == "close_app":
        return apps.close_app(params.get("name", ""))
    if action == "volume":
        return system.volume(params.get("operation", ""), params.get("value"))
    if action == "brightness":
        return system.brightness(params.get("operation", ""), params.get("value"))
    if action == "power":
        return system.power(params.get("operation", ""))
    if action == "system_info":
        return system.system_info()
    if action == "screenshot":
        return automation.screenshot()
    if action == "type_text":
        return automation.type_text(params.get("text", ""))
    if action == "press_key":
        return automation.press_key(params.get("keys", ""))
    if action == "media":
        return automation.media(params.get("operation", ""))
    if action == "window":
        return automation.window(params.get("operation", ""))
    if action == "mouse":
        return automation.mouse(
            params.get("operation", ""), params.get("x"), params.get("y")
        )
    if action == "web_search":
        return web.web_search(params.get("query", ""))
    if action == "open_url":
        return web.open_url(params.get("url", ""))
    if action == "chat":
        return ""  # javob "reply" da
    return ""  # unknown
