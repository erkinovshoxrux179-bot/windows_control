"""Tizim boshqaruvi: ovoz, ekran yorqinligi, quvvat, tizim ma'lumotlari."""

import subprocess

# pyautogui media tugmalari uchun (ovozni ko'tar/tushir/mute)
try:
    import pyautogui
except Exception:
    pyautogui = None

# Aniq foiz qiymatga qo'yish uchun pycaw
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _PYCAW = True
except Exception:
    _PYCAW = False

# Ekran yorqinligi uchun
try:
    import screen_brightness_control as sbc
except Exception:
    sbc = None

try:
    import psutil
except Exception:
    psutil = None


# ---------------------------------------------------------------------
#  OVOZ
# ---------------------------------------------------------------------
def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def volume(operation: str, value: int = None) -> str:
    operation = (operation or "").lower()

    if operation == "set" and value is not None:
        value = max(0, min(100, int(value)))
        if _PYCAW:
            vol = _get_volume_interface()
            # 0.0 - 1.0 oralig'ida o'rnatamiz
            vol.SetMasterVolumeLevelScalar(value / 100.0, None)
            return f"Ovoz {value}% ga qo'yildi."
        return "Ovozni aniq foizga qo'yish uchun pycaw kerak."

    if operation in ("up", "ko'tar", "oshir"):
        if pyautogui:
            for _ in range(5):  # har bosish ~2%, 5 marta ~10%
                pyautogui.press("volumeup")
            return "Ovoz ko'tarildi."
    elif operation in ("down", "tushir", "kamaytir"):
        if pyautogui:
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Ovoz tushirildi."
    elif operation in ("mute", "unmute", "ovozsiz"):
        if _PYCAW:
            vol = _get_volume_interface()
            mute = 0 if operation == "unmute" else 1
            vol.SetMute(mute, None)
            return "Ovoz o'chirildi." if mute else "Ovoz yoqildi."
        if pyautogui:
            pyautogui.press("volumemute")
            return "Ovoz almashtirildi."

    return "Ovoz buyrug'ini tushunmadim."


# ---------------------------------------------------------------------
#  EKRAN YORQINLIGI
# ---------------------------------------------------------------------
def brightness(operation: str, value: int = None) -> str:
    if sbc is None:
        return "Yorqinlikni boshqarish uchun screen-brightness-control kerak."
    operation = (operation or "").lower()
    try:
        current = sbc.get_brightness(display=0)
        current = current[0] if isinstance(current, list) else current
        if operation == "set" and value is not None:
            value = max(0, min(100, int(value)))
            sbc.set_brightness(value)
            return f"Yorqinlik {value}% ga qo'yildi."
        elif operation in ("up", "oshir"):
            sbc.set_brightness(min(100, current + 15))
            return "Yorqinlik oshirildi."
        elif operation in ("down", "kamaytir"):
            sbc.set_brightness(max(0, current - 15))
            return "Yorqinlik kamaytirildi."
    except Exception as e:
        return f"Yorqinlikni o'zgartirolmadim: {e}"
    return "Yorqinlik buyrug'ini tushunmadim."


# ---------------------------------------------------------------------
#  QUVVAT (shutdown / restart / sleep / lock / logoff)
# ---------------------------------------------------------------------
def power(operation: str) -> str:
    operation = (operation or "").lower()
    try:
        if operation == "shutdown":
            subprocess.Popen(["shutdown", "/s", "/t", "5"])
            return "Kompyuter 5 soniyada o'chadi. ('shutdown /a' bilan bekor qilish mumkin)"
        elif operation == "restart":
            subprocess.Popen(["shutdown", "/r", "/t", "5"])
            return "Kompyuter qayta yuklanmoqda."
        elif operation == "logoff":
            subprocess.Popen(["shutdown", "/l"])
            return "Tizimdan chiqilmoqda."
        elif operation == "sleep":
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "Uyqu rejimiga o'tilmoqda."
        elif operation == "lock":
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Ekran qulflandi."
    except Exception as e:
        return f"Buyruqni bajarolmadim: {e}"
    return "Quvvat buyrug'ini tushunmadim."


# ---------------------------------------------------------------------
#  TIZIM MA'LUMOTI
# ---------------------------------------------------------------------
def system_info() -> str:
    if psutil is None:
        return "Tizim ma'lumoti uchun psutil kerak."
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        parts = [f"CPU yuki: {cpu}%", f"Xotira: {mem.percent}% band"]
        if battery is not None:
            parts.append(f"Batareya: {int(battery.percent)}%")
        return ". ".join(parts) + "."
    except Exception as e:
        return f"Ma'lumot olishda xato: {e}"
