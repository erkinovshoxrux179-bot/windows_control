# Windows Controller 🎙️🖥️

Ovozli va matnli buyruqlar bilan Windows'ni boshqaradigan suzib yuruvchi yordamchi.
O'zbek tilini tushunadi (LLM yordamida), har doim tinglab turadi va kompyuterni
maksimal darajada boshqaradi.

![panel](https://via.placeholder.com/760x64/1e2530/4a90e2?text=Windows+controller)

## Imkoniyatlar

- 🗣️ **O'zbekcha ovozli boshqaruv** — har doim yoniq mikrofon (always-on)
- 🧠 **Aqlli tushunish** — tabiiy tilni LLM (Gemini yoki OpenAI) buyruqqa aylantiradi
- 🪟 **Maksimal boshqaruv**:
  - Dastur ochish/yopish (chrome, notepad, kalkulyator, word, ...)
  - Ovoz balandligi (aniq foiz, ko'tarish/tushirish, ovozsiz)
  - Ekran yorqinligi
  - Quvvat (o'chirish, qayta yuklash, uyqu, qulflash)
  - Ekran rasmi (screenshot)
  - Klaviatura va sichqoncha avtomatlashtirish
  - Oyna boshqaruvi (kichraytirish, alt+tab, ...)
  - Internetda qidirish va sayt ochish
  - Tizim ma'lumoti (CPU, xotira, batareya)
- 🔊 **O'zbekcha ovozli javob** (edge-tts)
- 🛡️ **Xavfsizlik** — o'chirish/qayta yuklash kabi amallar oldidan tasdiq so'raydi

## Loyiha tuzilishi

```
windows-controller/
├── main.py            # Bosh dastur (hammasini bog'laydi)
├── cli.py             # UI'siz sinov rejimi (API'ni tekshirish uchun)
├── config.py          # Sozlamalar (API kalit, til, ovoz, ...)
├── requirements.txt
├── brain/             # "Miya"
│   ├── llm.py         #   LLM klienti (Gemini + OpenAI)
│   └── nlu.py         #   Buyruqni tushunish (o'zbekcha system prompt)
├── actions/           # Windows amallari
│   ├── executor.py    #   Buyruqni mos amalga yo'naltiradi
│   ├── apps.py        #   Dastur ochish/yopish
│   ├── system.py      #   Ovoz, yorqinlik, quvvat, tizim ma'lumoti
│   ├── automation.py  #   Klaviatura, sichqoncha, screenshot, oyna, media
│   └── web.py         #   Qidirish, sayt ochish
├── voice/             # Ovoz
│   ├── stt.py         #   Ovozni matnga (uz-UZ, doimiy tinglash)
│   └── tts.py         #   Matnni ovozga (o'zbekcha)
├── ui/
│   └── overlay.py     # Suzib yuruvchi panel
└── installer/         # O'rnatgich (setup.exe) yasash uchun
    ├── WindowsController.spec  #   PyInstaller konfiguratsiyasi
    ├── installer.iss           #   Inno Setup skripti (API so'rovi + autostart)
    └── build.bat               #   Bir buyruqda hammasini yasaydi
```

## O'rnatish

> ⚠️ Bu dastur **Windows** uchun mo'ljallangan (pyautogui, pycaw, pywin32).
> Linux/Mac'da faqat `cli.py` qisman ishlaydi.

1. Python 3.10+ o'rnating.
2. Kutubxonalarni o'rnating:
   ```powershell
   pip install -r requirements.txt
   ```
   PyAudio o'rnatishda muammo bo'lsa:
   ```powershell
   pip install pipwin
   pipwin install pyaudio
   ```

## Sozlash (API kaliti)

Terminalda muhit o'zgaruvchilarini o'rnating (tavsiya etiladi):

```powershell
# Gemini ishlatsangiz:
$env:WC_LLM_PROVIDER="gemini"
$env:WC_API_KEY="sizning_gemini_kalitingiz"

# Yoki OpenAI:
$env:WC_LLM_PROVIDER="openai"
$env:WC_API_KEY="sizning_openai_kalitingiz"
```

Yoki `config.py` faylida `API_KEY` ni to'g'ridan-to'g'ri yozing (kamroq xavfsiz).

## Ishga tushirish

```powershell
# To'liq dastur (UI + ovoz):
python main.py

# Faqat matnli sinov (API'ni tekshirish uchun, mikrofonsiz):
python cli.py
```

**Boshqaruv:**
- Buyruqni yozing va `Enter` bosing, yoki shunchaki gapiring 🎤
- 🎤 tugmasi — mikrofonni yoqish/o'chirish
- Panelni sarlavhadan ushlab ko'chiring
- Chiqish: `Ctrl+Q` yoki avatarga o'ng tugma bilan bosing

## Buyruq misollari

| Aytasiz | Bajariladi |
|---------|------------|
| "brauzerni och" | Chrome ochiladi |
| "ovozni 30 foiz qil" | Ovoz 30% ga qo'yiladi |
| "ovozni ko'tar" | Ovoz balandlashadi |
| "ekranni suratga ol" | Screenshot olinadi |
| "kalkulyatorni och" | Kalkulyator ochiladi |
| "youtube ni och" | YouTube ochiladi |
| "kompyuterni qulfla" | Ekran qulflanadi |
| "tizim haqida ma'lumot ber" | CPU/xotira/batareya |

## Sozlamalarni o'zgartirish (`config.py`)

- `WAKE_WORD` — uyg'otuvchi so'z (masalan "kompyuter"). Bo'sh = har gapni qabul qiladi.
- `TTS_VOICE` — `uz-UZ-SardorNeural` (erkak) yoki `uz-UZ-MadinaNeural` (ayol)
- `ALWAYS_LISTENING` — doimiy tinglashni yoqish/o'chirish
- `CONFIRM_DANGEROUS_ACTIONS` — xavfli amallar uchun tasdiq

## Eslatma

- STT (ovozni tanish) Google'ning bepul xizmatidan foydalanadi — internet kerak.
- Offline STT xohlasangiz, keyinroq Vosk (uz modeli) qo'shsa bo'ladi.

---

## 📦 O'rnatgich (Setup.exe) yasash — Inno Setup

Dasturni boshqa kompyuterlarga oson o'rnatish uchun **`WindowsController-Setup.exe`**
o'rnatgichini yasash mumkin. Bunda Python kerak emas — foydalanuvchi shunchaki
o'rnatadi va ishlatadi.

### Kerakli dasturlar (yasovchi kompyuterda, bir martalik)

1. **Python 3.10+**
2. **Inno Setup 6** — [jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php) dan yuklab o'rnating

### Bir buyruq bilan yasash

Loyiha papkasida quyidagini ishga tushiring:

```powershell
installer\build.bat
```

Bu skript avtomatik ravishda:
1. Kerakli kutubxonalarni o'rnatadi (`requirements.txt` + `requirements-build.txt`)
2. **PyInstaller** bilan dasturni `.exe` ga aylantiradi → `dist\WindowsController\`
3. **Inno Setup** bilan o'rnatgich yasaydi

**Natija:**
```
installer\Output\WindowsController-Setup.exe
```

### Qo'lda yasash (ixtiyoriy)

```powershell
pip install -r requirements.txt -r requirements-build.txt
pyinstaller installer\WindowsController.spec
iscc installer\installer.iss
```

### O'rnatgich nima qiladi?

Foydalanuvchi `WindowsController-Setup.exe` ni ishga tushirganda:

- 🗂️ Dasturni `Program Files\WindowsController` ga o'rnatadi
- 🔑 **API kalit va provayderni (Gemini/OpenAI) so'raydi** va `settings.env` ga yozadi
  — foydalanuvchi config faylini qo'lda tahrirlashi shart emas
- 🖥️ Ish stoli yorlig'ini yaratadi (ixtiyoriy)
- 🚀 **Windows bilan birga avtomatik ishga tushishini** (autostart) yoqadi (ixtiyoriy)
- ▶️ O'rnatish tugagach dasturni ishga tushiradi

> 💡 **Eslatma:** PyInstaller dasturni qaysi OS'da yasasangiz, o'sha OS uchun
> ishlaydi. Windows `.exe` olish uchun build'ni **Windows'da** bajaring.

> 🎨 **Ikonka:** `installer\app.ico` faylini qo'ysangiz, u dastur va o'rnatgich
> ikonkasi sifatida ishlatiladi (ixtiyoriy).
