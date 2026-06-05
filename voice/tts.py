"""
TTS — Text To Speech (matnni ovozga), o'zbek tilida.

edge-tts orqali Microsoft'ning o'zbekcha neyron ovozlaridan foydalanadi:
  - uz-UZ-SardorNeural  (erkak)
  - uz-UZ-MadinaNeural  (ayol)
Ovoz fayli vaqtincha yaratilib, pygame orqali ijro etiladi.
"""

import asyncio
import os
import tempfile
import threading

try:
    import edge_tts
except Exception:
    edge_tts = None

try:
    import pygame
    pygame.mixer.init()
    _MIXER = True
except Exception:
    _MIXER = False

import config


_lock = threading.Lock()


async def _synthesize(text: str, path: str):
    communicate = edge_tts.Communicate(text, config.TTS_VOICE)
    await communicate.save(path)


def speak(text: str, on_done=None):
    """Matnni ovozli aytadi (alohida oqimda, bloklamasdan)."""
    if not config.TTS_ENABLED or not text:
        if on_done:
            on_done()
        return
    if edge_tts is None or not _MIXER:
        # TTS imkoni bo'lmasa, jim o'tib ketamiz
        if on_done:
            on_done()
        return

    threading.Thread(target=_speak_blocking, args=(text, on_done), daemon=True).start()


def _speak_blocking(text: str, on_done=None):
    with _lock:
        path = None
        try:
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            asyncio.run(_synthesize(text, path))

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        except Exception:
            pass
        finally:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            if on_done:
                on_done()
