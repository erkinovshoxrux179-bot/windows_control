"""Dasturlarni ochish va yopish."""

import os
import subprocess

try:
    import psutil
except ImportError:  # sandbox/Windows bo'lmagan muhitda import xatosini yutamiz
    psutil = None


# Tanish nomlar (o'zbekcha/inglizcha) -> ishga tushirish buyrug'i.
# os.startfile yoki subprocess orqali ishlatiladi.
APP_ALIASES = {
    # Brauzerlar
    "chrome": "chrome", "google": "chrome", "brauzer": "chrome", "internet": "chrome",
    "edge": "msedge", "microsoft edge": "msedge",
    "firefox": "firefox", "opera": "opera",
    # Tizim dasturlari
    "notepad": "notepad", "bloknot": "notepad", "daftar": "notepad",
    "calc": "calc", "kalkulyator": "calc", "hisoblagich": "calc",
    "explorer": "explorer", "fayl": "explorer", "papka": "explorer", "kompyuter": "explorer",
    "paint": "mspaint", "rasm": "mspaint",
    "cmd": "cmd", "terminal": "cmd", "buyruq qatori": "cmd",
    "powershell": "powershell",
    "task manager": "taskmgr", "dispetcher": "taskmgr", "vazifa dispetcheri": "taskmgr",
    "sozlamalar": "ms-settings:", "settings": "ms-settings:",
    "control panel": "control", "boshqaruv paneli": "control",
    # Office
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt", "outlook": "outlook",
    # Boshqalar
    "telegram": "telegram", "spotify": "spotify", "vscode": "code", "code": "code",
}


def _resolve(name: str) -> str:
    name = (name or "").strip().lower()
    return APP_ALIASES.get(name, name)


def open_app(name: str) -> str:
    """Dasturni ochadi. name — tanish nom yoki to'g'ridan-to'g'ri buyruq."""
    target = _resolve(name)
    if not target:
        return "Qaysi dasturni ochishni aytmadingiz."

    # ms-settings: kabi protokol manzillari
    if target.endswith(":") or "://" in target:
        os.startfile(target)
        return f"{name} ochildi."

    try:
        # explorer/calc/notepad kabi tizim dasturlari uchun shell orqali
        subprocess.Popen(target, shell=True)
        return f"{name} ochildi."
    except Exception as e:
        return f"{name} ni ocholmadim: {e}"


def close_app(name: str) -> str:
    """Dastur jarayonini yopadi."""
    target = _resolve(name)
    # .exe qo'shamiz (taskkill uchun)
    exe = target if target.endswith(".exe") else f"{target}.exe"

    if psutil is not None:
        killed = 0
        for proc in psutil.process_iter(["name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if pname == exe.lower() or pname == f"{target}.exe".lower():
                    proc.terminate()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed:
            return f"{name} yopildi."
        return f"{name} ochiq emas ekan."

    # psutil bo'lmasa taskkill
    try:
        subprocess.run(["taskkill", "/IM", exe, "/F"], check=True,
                       capture_output=True)
        return f"{name} yopildi."
    except Exception:
        return f"{name} ni yopolmadim."
