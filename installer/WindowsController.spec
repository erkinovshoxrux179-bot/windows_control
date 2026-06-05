# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Windows Controller dasturini yagona papkaga (onedir)
to'playdi. So'ng Inno Setup shu papkani o'rnatgichga aylantiradi.

Ishlatish (loyiha ildizidan):
    pyinstaller installer/WindowsController.spec

Natija:
    dist/WindowsController/WindowsController.exe
"""

import os as _os
from PyInstaller.utils.hooks import collect_all

# Loyiha ildizi — SPECPATH (bu .spec fayl joylashgan papka = installer/) asosida.
# Shunday qilib, pyinstaller qaysi papkadan ishga tushirilsa ham yo'llar to'g'ri bo'ladi.
PROJECT_ROOT = _os.path.abspath(_os.path.join(SPECPATH, ".."))

# customtkinter, edge-tts va boshqa kutubxonalar o'zlari bilan
# data fayllar / yashirin import'lar olib keladi — hammasini yig'amiz.
datas = []
binaries = []
hiddenimports = []

_packages = [
    "customtkinter",
    "edge_tts",
    "pycaw",
    "comtypes",
    "speech_recognition",
    "screen_brightness_control",
    "pygame",
    "pyttsx3",
]

for _pkg in _packages:
    try:
        d, b, h = collect_all(_pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        # Kutubxona o'rnatilmagan bo'lsa, o'tkazib yuboramiz
        pass

# Ba'zi kutubxonalar dinamik import qiladi — qo'lda qo'shamiz
hiddenimports += [
    "win32com",
    "win32com.client",
    "comtypes.client",
    "pyaudio",
    "engineio.async_drivers.threading",
]


block_cipher = None

# Icon ixtiyoriy — installer/app.ico bo'lsa ishlatamiz, bo'lmasa None
_icon_path = _os.path.join(PROJECT_ROOT, "installer", "app.ico")
APP_ICON = _icon_path if _os.path.isfile(_icon_path) else None


a = Analysis(
    [_os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WindowsController",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # GUI dastur — konsol oynasi chiqmaydi
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=APP_ICON,            # ixtiyoriy: installer/app.ico bo'lsa ishlatiladi
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WindowsController",
)
