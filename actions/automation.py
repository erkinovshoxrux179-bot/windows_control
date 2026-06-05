"""Klaviatura, sichqoncha, ekran rasmi (screenshot) va matn yozish."""

import os
import time
from datetime import datetime

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None


# Foydalanuvchi aytadigan tugma nomlari -> pyautogui nomlari
_KEY_ALIASES = {
    "enter": "enter", "kirish": "enter",
    "esc": "esc", "escape": "esc",
    "tab": "tab", "space": "space", "probel": "space", "bo'shliq": "space",
    "win": "win", "windows": "win",
    "del": "delete", "delete": "delete", "o'chir": "delete",
    "backspace": "backspace",
    "up": "up", "down": "down", "left": "left", "right": "right",
}


def _normalize_keys(keys: str) -> list:
    """'ctrl+c' -> ['ctrl', 'c']"""
    parts = [p.strip().lower() for p in keys.replace(" ", "+").split("+") if p.strip()]
    return [_KEY_ALIASES.get(p, p) for p in parts]


def press_key(keys: str) -> str:
    if pyautogui is None:
        return "Tugma bosish uchun pyautogui kerak."
    combo = _normalize_keys(keys)
    if not combo:
        return "Qaysi tugmani bosishni tushunmadim."
    try:
        if len(combo) == 1:
            pyautogui.press(combo[0])
        else:
            pyautogui.hotkey(*combo)
        return f"'{keys}' bosildi."
    except Exception as e:
        return f"Tugmani bosolmadim: {e}"


def type_text(text: str) -> str:
    """Matnni yozadi. O'zbekcha harflar (o', g', ...) uchun clipboard orqali."""
    if pyautogui is None:
        return "Matn yozish uchun pyautogui kerak."
    if not text:
        return "Nima yozishni aytmadingiz."
    try:
        # Unicode (o'zbekcha) belgilar uchun clipboard + Ctrl+V eng ishonchli usul
        try:
            import pyperclip
            pyperclip.copy(text)
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "v")
        except Exception:
            # pyperclip bo'lmasa, oddiy yozuv (faqat ASCII uchun ishonchli)
            pyautogui.write(text, interval=0.02)
        return f"Yozildi: {text[:40]}"
    except Exception as e:
        return f"Yozolmadim: {e}"


def screenshot() -> str:
    if pyautogui is None:
        return "Ekran rasmini olish uchun pyautogui kerak."
    try:
        folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(folder, exist_ok=True)
        fname = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        path = os.path.join(folder, fname)
        img = pyautogui.screenshot()
        img.save(path)
        return f"Ekran rasmi saqlandi: {path}"
    except Exception as e:
        return f"Rasm olishda xato: {e}"


def mouse(operation: str, x: int = None, y: int = None) -> str:
    if pyautogui is None:
        return "Sichqoncha boshqaruvi uchun pyautogui kerak."
    operation = (operation or "").lower()
    try:
        if x is not None and y is not None:
            pyautogui.moveTo(int(x), int(y), duration=0.2)
        if operation == "click":
            pyautogui.click()
            return "Bosildi."
        elif operation == "right_click":
            pyautogui.click(button="right")
            return "O'ng tugma bosildi."
        elif operation == "double_click":
            pyautogui.doubleClick()
            return "Ikki marta bosildi."
        elif operation == "move":
            return "Sichqoncha ko'chirildi."
    except Exception as e:
        return f"Sichqoncha xatosi: {e}"
    return "Sichqoncha buyrug'ini tushunmadim."


def window(operation: str) -> str:
    """Faol oynani boshqarish."""
    if pyautogui is None:
        return "Oyna boshqaruvi uchun pyautogui kerak."
    operation = (operation or "").lower()
    try:
        if operation == "minimize":
            pyautogui.hotkey("win", "down")
            return "Oyna kichraytirildi."
        elif operation == "maximize":
            pyautogui.hotkey("win", "up")
            return "Oyna kattalashtirildi."
        elif operation == "close":
            pyautogui.hotkey("alt", "f4")
            return "Oyna yopildi."
        elif operation == "minimize_all":
            pyautogui.hotkey("win", "d")
            return "Barcha oynalar kichraytirildi."
        elif operation == "switch":
            pyautogui.hotkey("alt", "tab")
            return "Oyna almashtirildi."
    except Exception as e:
        return f"Oyna xatosi: {e}"
    return "Oyna buyrug'ini tushunmadim."



def media(operation: str) -> str:
    """Media pleer boshqaruvi (media tugmalari orqali)."""
    if pyautogui is None:
        return "Media boshqaruvi uchun pyautogui kerak."
    operation = (operation or "").lower()
    key_map = {
        "play_pause": "playpause",
        "play": "playpause",
        "pause": "playpause",
        "next": "nexttrack",
        "prev": "prevtrack",
        "previous": "prevtrack",
        "stop": "stop",
        "mute": "volumemute",
    }
    key = key_map.get(operation)
    if not key:
        return "Media buyrug'ini tushunmadim."
    try:
        pyautogui.press(key)
        return "Bajarildi."
    except Exception as e:
        return f"Media xatosi: {e}"
