"""
Windows Controller — markaziy sozlamalar.

Sozlamalar quyidagi tartibda (yuqori ustun) o'qiladi:
  1. Muhit o'zgaruvchilari (environment variables) — eng yuqori ustunlik
  2. settings.env fayli — o'rnatgich (Inno Setup) shu faylga API kalitni yozadi
  3. Quyidagi standart qiymatlar

settings.env qaysi joylardan qidiriladi:
  - %APPDATA%\\WindowsController\\settings.env   (o'rnatgich yozadigan joy)
  - dastur (exe yoki main.py) yonidagi settings.env
"""

import os
import sys


def _candidate_setting_paths():
    """settings.env qidiriladigan joylar ro'yxati."""
    paths = []
    # 1) %APPDATA%\WindowsController\settings.env
    appdata = os.getenv("APPDATA")
    if appdata:
        paths.append(os.path.join(appdata, "WindowsController", "settings.env"))
    # 2) Dastur yonidagi (frozen exe yoki skript) settings.env
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    paths.append(os.path.join(base, "settings.env"))
    return paths


def _load_settings_file():
    """settings.env dagi KEY=VALUE qatorlarini o'qib, muhitga qo'shadi.

    os.environ.setdefault ishlatamiz — ya'ni allaqachon o'rnatilgan
    muhit o'zgaruvchisi ustun turadi, aks holda fayldagi qiymat ishlatiladi.
    """
    for path in _candidate_setting_paths():
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key:
                        os.environ.setdefault(key, value)
        except OSError:
            continue


# Sozlamalarni o'qishdan OLDIN settings.env ni yuklaymiz
_load_settings_file()


# =====================================================================
#  LLM (sun'iy intellekt "miya") sozlamalari
# =====================================================================
# Qaysi provayderdan foydalanasiz: "gemini" yoki "openai"
LLM_PROVIDER = os.getenv("WC_LLM_PROVIDER", "gemini")

# API kalitingiz. Eng yaxshisi: terminalda muhit o'zgaruvchisini o'rnating.
#   Windows (PowerShell):  $env:WC_API_KEY="sizning_kalitingiz"
# Yoki shu yerga to'g'ridan-to'g'ri yozing (tavsiya etilmaydi):
API_KEY = os.getenv("WC_API_KEY", "")

# Model nomi
GEMINI_MODEL = os.getenv("WC_GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = os.getenv("WC_OPENAI_MODEL", "gpt-4o-mini")

# OpenAI-mos endpoint (OpenAI yoki mos keluvchi xizmatlar uchun)
OPENAI_BASE_URL = os.getenv("WC_OPENAI_BASE_URL", "https://api.openai.com/v1")

# =====================================================================
#  Ovoz (voice) sozlamalari
# =====================================================================
# STT (ovozni matnga) tili
STT_LANGUAGE = "uz-UZ"

# Ovozli boshqaruv har doim yoniqmi (fonda doimiy tinglaydi)
ALWAYS_LISTENING = True

# "Uyg'otuvchi so'z" (wake word). Bo'sh bo'lsa — har bir gapni qabul qiladi.
# Masalan: "kompyuter" yoki "asistent". Bo'sh string = wake word o'chirilgan.
WAKE_WORD = os.getenv("WC_WAKE_WORD", "")

# TTS (matnni ovozga) — Uzbek ovozlar: "uz-UZ-MadinaNeural" yoki "uz-UZ-SardorNeural"
TTS_VOICE = os.getenv("WC_TTS_VOICE", "uz-UZ-SardorNeural")
TTS_ENABLED = True

# Mikrofon sezgirligi (energiya chegarasi). None = avtomatik sozlash.
MIC_ENERGY_THRESHOLD = None
# Gap tugaganini aniqlash uchun jimlik (sekund)
MIC_PAUSE_THRESHOLD = 0.8

# =====================================================================
#  Xavfsizlik
# =====================================================================
# Xavfli buyruqlar (o'chirish, qayta yuklash) bajarilishidan oldin tasdiq so'ralsinmi
CONFIRM_DANGEROUS_ACTIONS = True

# =====================================================================
#  UI sozlamalari
# =====================================================================
APP_TITLE = "Windows controller"
UI_WIDTH = 760
UI_HEIGHT = 64
UI_ALWAYS_ON_TOP = True
