# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Windows Controller dasturini yagona papkaga (onedir)
to'playdi. So'ng Inno Setup shu papkani o'rnatgichga aylantiradi.

Ishlatish (loyiha ildizidan):
    pyinstaller installer/WindowsController.spec

Natija:
    dist/WindowsController/WindowsController.exe
"""

from PyInstaller.utils.hooks import collect_all

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
import os as _os
_icon_path = _os.path.join(_os.path.dirname(SPECPATH), "installer", "app.ico")
if not _os.path.isfile(_icon_path):
    _icon_path = _os.path.join(SPECPATH, "app.ico")
APP_ICON = _icon_path if _os.path.isfile(_icon_path) else None


a = Analysis(
    ["..\\main.py"],
    pathex=[".."],
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
