"""
STT — Speech To Text (ovozni matnga).

Doimiy (always-on) tinglash: fonda mikrofonni tinglab turadi va
har bir tushunilgan gapni callback orqali uzatadi.

Uzbek tili uchun Google Web Speech API (uz-UZ) ishlatiladi — bepul,
lekin internet talab qiladi va yaxshi sifat beradi.
"""

import threading

try:
    import speech_recognition as sr
except Exception:
    sr = None

import config


class VoiceListener:
    """Fonda doimiy tinglaydigan mikrofon."""

    def __init__(self, on_text, on_status=None):
        """
        on_text(text: str)   — gap tushunilganda chaqiriladi
        on_status(state: str)— holat o'zgarganda: "listening"|"recognizing"|"idle"|"error"
        """
        self.on_text = on_text
        self.on_status = on_status or (lambda s: None)
        self._stop = threading.Event()
        self._thread = None
        self._paused = threading.Event()  # set bo'lsa — vaqtincha to'xtaydi

        if sr is None:
            raise RuntimeError(
                "SpeechRecognition o'rnatilmagan. 'pip install SpeechRecognition PyAudio'"
            )
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = config.MIC_PAUSE_THRESHOLD
        if config.MIC_ENERGY_THRESHOLD is not None:
            self.recognizer.energy_threshold = config.MIC_ENERGY_THRESHOLD
            self.recognizer.dynamic_energy_threshold = False

    # -- boshqaruv --
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def pause(self):
        """Tinglashni vaqtincha to'xtatish (masalan, TTS gapirayotganda)."""
        self._paused.set()

    def resume(self):
        self._paused.clear()

    # -- asosiy sikl --
    def _loop(self):
        try:
            mic = sr.Microphone()
        except Exception as e:
            self.on_status("error")
            self.on_text(f"[xato] Mikrofon topilmadi: {e}")
            return

        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

        while not self._stop.is_set():
            if self._paused.is_set():
                threading.Event().wait(0.2)
                continue
            try:
                self.on_status("listening")
                with mic as source:
                    audio = self.recognizer.listen(
                        source, timeout=None, phrase_time_limit=8
                    )
                if self._paused.is_set() or self._stop.is_set():
                    continue
                self.on_status("recognizing")
                text = self.recognizer.recognize_google(
                    audio, language=config.STT_LANGUAGE
                )
                text = (text or "").strip()
                if text and self._passes_wake_word(text):
                    self.on_text(self._strip_wake_word(text))
            except sr.UnknownValueError:
                pass  # tushunarsiz ovoz — e'tibor bermaymiz
            except sr.RequestError as e:
                self.on_status("error")
                self.on_text(f"[xato] Ovoz xizmatiga ulanib bo'lmadi: {e}")
            except Exception:
                pass
            finally:
                self.on_status("idle")

    # -- wake word (uyg'otuvchi so'z) --
    def _passes_wake_word(self, text: str) -> bool:
        ww = (config.WAKE_WORD or "").strip().lower()
        if not ww:
            return True
        return ww in text.lower()

    def _strip_wake_word(self, text: str) -> str:
        ww = (config.WAKE_WORD or "").strip().lower()
        if not ww:
            return text
        idx = text.lower().find(ww)
        if idx >= 0:
            return (text[:idx] + text[idx + len(ww):]).strip(" ,.")
        return text
