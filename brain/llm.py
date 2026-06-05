"""
LLM klienti — provayderga bog'liq emas (Gemini va OpenAI ikkalasini ham qo'llaydi).

Maqsad: matnli so'rovni (system + user) yuborib, javob matnini qaytarish.
NLU moduli bu javobdan JSON buyruqni ajratib oladi.
"""

import requests

import config


class LLMError(Exception):
    """LLM bilan bog'liq xatoliklar."""


def ask(system_prompt: str, user_text: str, temperature: float = 0.2) -> str:
    """System + user matnini LLM'ga yuboradi va matn javobini qaytaradi."""
    provider = (config.LLM_PROVIDER or "gemini").lower()

    if not config.API_KEY:
        raise LLMError(
            "API kaliti topilmadi. config.py dagi API_KEY ni to'ldiring "
            "yoki WC_API_KEY muhit o'zgaruvchisini o'rnating."
        )

    if provider == "gemini":
        return _ask_gemini(system_prompt, user_text, temperature)
    elif provider == "openai":
        return _ask_openai(system_prompt, user_text, temperature)
    else:
        raise LLMError(f"Noma'lum provayder: {provider} (gemini yoki openai bo'lishi kerak)")


# ---------------------------------------------------------------------
#  Gemini (Google Generative Language API, REST)
# ---------------------------------------------------------------------
def _ask_gemini(system_prompt: str, user_text: str, temperature: float) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=20)
    except requests.RequestException as e:
        raise LLMError(f"Gemini'ga ulanib bo'lmadi: {e}") from e

    if resp.status_code != 200:
        raise LLMError(f"Gemini xatosi {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"Gemini javobini o'qib bo'lmadi: {data}") from e


# ---------------------------------------------------------------------
#  OpenAI (yoki mos keluvchi chat/completions endpoint)
# ---------------------------------------------------------------------
def _ask_openai(system_prompt: str, user_text: str, temperature: float) -> str:
    url = f"{config.OPENAI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
    except requests.RequestException as e:
        raise LLMError(f"OpenAI'ga ulanib bo'lmadi: {e}") from e

    if resp.status_code != 200:
        raise LLMError(f"OpenAI xatosi {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise LLMError(f"OpenAI javobini o'qib bo'lmadi: {data}") from e
