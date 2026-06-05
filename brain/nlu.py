"""
NLU — Natural Language Understanding.

Foydalanuvchining o'zbekcha (yoki aralash) buyrug'ini olib,
LLM yordamida tuzilgan (structured) buyruqqa aylantiradi.

Qaytariladigan format (har doim JSON):
{
  "action": "<amal nomi>",
  "params": { ... },
  "reply": "<o'zbekcha qisqa javob>"
}
"""

import json
import re

from brain import llm


# Qo'llab-quvvatlanadigan amallar ro'yxati (executor shularni biladi):
SUPPORTED_ACTIONS = [
    "open_app",      # dastur ochish        -> params: {"name": "chrome"}
    "close_app",     # dastur yopish        -> params: {"name": "chrome"}
    "volume",        # ovoz balandligi      -> params: {"operation": "set|up|down|mute|unmute", "value": 0-100}
    "brightness",    # ekran yorqinligi     -> params: {"operation": "set|up|down", "value": 0-100}
    "power",         # quvvat               -> params: {"operation": "shutdown|restart|sleep|lock|logoff"}
    "screenshot",    # ekran rasmi          -> params: {}
    "type_text",     # matn yozish          -> params: {"text": "..."}
    "press_key",     # tugma bosish         -> params: {"keys": "ctrl+c"}
    "media",         # media boshqaruvi     -> params: {"operation": "play_pause|next|prev|stop|mute"}
    "web_search",    # internetda qidirish  -> params: {"query": "..."}
    "open_url",      # sayt ochish          -> params: {"url": "https://..."}
    "window",        # oyna boshqaruvi      -> params: {"operation": "minimize|maximize|close|minimize_all|switch"}
    "mouse",         # sichqoncha           -> params: {"operation": "click|right_click|double_click|move", "x": int, "y": int}
    "system_info",   # tizim haqida ma'lumot-> params: {}
    "chat",          # oddiy suhbat/javob   -> params: {}
    "unknown",       # tushunarsiz buyruq   -> params: {}
]


SYSTEM_PROMPT = """Sen "Windows Controller" nomli ovozli yordamchining miyasisan.
Foydalanuvchi O'ZBEK tilida (ba'zan ruscha/inglizcha aralash) gapiradi.
Sening vazifang — uning gapini tushunib, Windows kompyuterda bajariladigan
ANIQ bir buyruqqa aylantirish.

Javobni FAQAT quyidagi JSON ko'rinishida ber (boshqa hech narsa yozma):
{
  "action": "amal_nomi",
  "params": { ... },
  "reply": "foydalanuvchiga o'zbekcha qisqa, samimiy javob"
}

Mavjud amallar (action) va ularning params'lari:
- "open_app"    -> {"name": "<dastur>"}        (chrome, edge, notepad, calc, explorer, word, excel, telegram, ...)
- "close_app"   -> {"name": "<dastur>"}
- "volume"      -> {"operation": "set|up|down|mute|unmute", "value": <0-100, faqat set uchun>}
- "brightness"  -> {"operation": "set|up|down", "value": <0-100, faqat set uchun>}
- "power"       -> {"operation": "shutdown|restart|sleep|lock|logoff"}
- "screenshot"  -> {}
- "type_text"   -> {"text": "<yoziladigan matn>"}
- "press_key"   -> {"keys": "<masalan: ctrl+c, alt+tab, win+d, enter>"}
- "media"       -> {"operation": "play_pause|next|prev|stop|mute"}
- "web_search"  -> {"query": "<qidiruv so'zi>"}
- "open_url"    -> {"url": "https://..."}
- "window"      -> {"operation": "minimize|maximize|close|minimize_all|switch"}
- "mouse"       -> {"operation": "click|right_click|double_click|move", "x": <son>, "y": <son>}
- "system_info" -> {}
- "chat"        -> {}   (agar bu kompyuter buyrug'i bo'lmasa, oddiy savol/suhbat bo'lsa)
- "unknown"     -> {}   (agar umuman tushunmasang)

QOIDALAR:
1. "reply" har doim O'ZBEK tilida, qisqa va tabiiy bo'lsin.
2. Agar foydalanuvchi savol bersa (masalan "soat necha?", "obi-havo qanaqa?"),
   "chat" action ishlat va javobni "reply" ichida ber.
3. Faqat yuqoridagi action nomlaridan foydalan, yangisini o'ylab topma.
4. Aniq son aytilmasa, "value" ni qo'shma.
5. JSON to'g'ri (valid) bo'lishi shart.

MISOLLAR:
Foydalanuvchi: "brauzerni ochib ber"
Javob: {"action": "open_app", "params": {"name": "chrome"}, "reply": "Brauzerni ochyapman."}

Foydalanuvchi: "ovozni ellik foiz qil"
Javob: {"action": "volume", "params": {"operation": "set", "value": 50}, "reply": "Ovozni 50 foizga qo'ydim."}

Foydalanuvchi: "ovozni ko'tar"
Javob: {"action": "volume", "params": {"operation": "up"}, "reply": "Ovozni ko'taryapman."}

Foydalanuvchi: "kompyuterni o'chir"
Javob: {"action": "power", "params": {"operation": "shutdown"}, "reply": "Kompyuter o'chirilmoqda."}

Foydalanuvchi: "ekranni suratga ol"
Javob: {"action": "screenshot", "params": {}, "reply": "Ekran rasmini oldim."}

Foydalanuvchi: "youtubeda mushuklar haqida video qidir"
Javob: {"action": "web_search", "params": {"query": "mushuklar haqida video"}, "reply": "Qidiryapman."}

Foydalanuvchi: "salom, ishlaring qalay?"
Javob: {"action": "chat", "params": {}, "reply": "Salom! Men yaxshi, sizga qanday yordam bera olaman?"}
"""


def _extract_json(text: str) -> dict:
    """LLM javobidan JSON obyektni ajratib oladi (atrofda ortiqcha matn bo'lsa ham)."""
    text = text.strip()
    # To'g'ridan-to'g'ri urinib ko'ramiz
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Matn ichidan birinchi { ... } blokini topamiz
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"JSON ajratib bo'lmadi: {text[:200]}")


def parse(user_text: str) -> dict:
    """Foydalanuvchi matnini tuzilgan buyruqqa aylantiradi."""
    user_text = (user_text or "").strip()
    if not user_text:
        return {"action": "unknown", "params": {}, "reply": "Hech narsa eshitmadim."}

    try:
        raw = llm.ask(SYSTEM_PROMPT, user_text)
        result = _extract_json(raw)
    except (llm.LLMError, ValueError) as e:
        return {
            "action": "unknown",
            "params": {},
            "reply": f"Kechirasiz, tushunolmadim. ({e})",
        }

    # Tekshiruv va standartlash
    action = result.get("action", "unknown")
    if action not in SUPPORTED_ACTIONS:
        action = "unknown"
    return {
        "action": action,
        "params": result.get("params", {}) or {},
        "reply": result.get("reply", "") or "",
    }
