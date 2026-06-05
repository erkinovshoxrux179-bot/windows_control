"""
Windows Controller — bosh dastur.

UI <-> Ovoz (STT/TTS) <-> Miya (NLU/LLM) <-> Amallar (executor) ni bog'laydi.

Ishga tushirish:  python main.py
Chiqish:          Ctrl+Q  (yoki avatarga o'ng tugma bilan bosing)
"""

import threading

import config
from ui.overlay import ControllerUI
from brain import nlu
from actions import executor
from voice import tts

try:
    from voice.stt import VoiceListener
except Exception:
    VoiceListener = None


class App:
    def __init__(self):
        self.ui = ControllerUI(
            on_submit=self.handle_command,
            on_mic_toggle=self.toggle_mic,
        )
        self._busy = threading.Lock()
        self.listener = None

        # Mikrofonni tayyorlash
        if VoiceListener is not None:
            try:
                self.listener = VoiceListener(
                    on_text=self.on_voice,
                    on_status=self.ui.set_status,
                )
            except Exception as e:
                self.ui.show_response(f"Mikrofon ishga tushmadi: {e}")
        else:
            self.ui.show_response(
                "Ovoz moduli yo'q. 'pip install SpeechRecognition PyAudio' ni bajaring."
            )

        # Chiqish tugmalari
        self.ui.bind("<Control-q>", lambda e: self.quit())
        self.ui.avatar.bind("<Button-3>", lambda e: self.quit())

    # -----------------------------------------------------------------
    def run(self):
        if config.ALWAYS_LISTENING and self.listener:
            self.listener.start()
            self.ui.show_response("Tinglayapman... 🎤")
        self.ui.mainloop()

    def quit(self):
        if self.listener:
            self.listener.stop()
        self.ui.destroy()

    # -----------------------------------------------------------------
    #  Ovozdan kelgan matn
    # -----------------------------------------------------------------
    def on_voice(self, text: str):
        if text.startswith("[xato]"):
            self.ui.show_response(text)
            return
        self.ui.set_recognized_text(text)
        self.handle_command(text)

    # -----------------------------------------------------------------
    #  Buyruqni qayta ishlash (matn yoki ovoz)
    # -----------------------------------------------------------------
    def handle_command(self, text: str):
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text: str):
        # Bir vaqtda faqat bitta buyruq bajarilsin
        if not self._busy.acquire(blocking=False):
            return
        try:
            if self.listener:
                self.listener.pause()  # TTS ovozini eshitmasligi uchun

            command = nlu.parse(text)

            # Xavfli amal bo'lsa — tasdiq so'raymiz
            if config.CONFIRM_DANGEROUS_ACTIONS and executor.is_dangerous(
                command["action"], command["params"]
            ):
                question = command.get("reply") or "Ushbu amalni bajaraymi?"
                if not self._confirm(question):
                    self._respond("Bekor qilindi.")
                    return

            result = executor.execute(command)
            self._respond(result)
        finally:
            self._busy.release()

    def _respond(self, text: str):
        if not text:
            self._resume_listening()
            return
        self.ui.show_response(text)
        tts.speak(text, on_done=self._resume_listening)

    def _resume_listening(self):
        if self.listener:
            self.listener.resume()

    # -----------------------------------------------------------------
    #  Xavfli amal uchun tasdiq (asosiy oqimda dialog)
    # -----------------------------------------------------------------
    def _confirm(self, message: str) -> bool:
        import tkinter.messagebox as mb

        result = {}
        done = threading.Event()

        def ask():
            try:
                result["ok"] = mb.askyesno("Tasdiqlang", message + "\n\nBajarilsinmi?")
            except Exception:
                result["ok"] = False
            done.set()

        self.ui.after(0, ask)
        done.wait()
        return result.get("ok", False)

    # -----------------------------------------------------------------
    def toggle_mic(self, enabled: bool):
        if not self.listener:
            return
        if enabled:
            self.listener.start()
            self.ui.show_response("Mikrofon yoqildi. 🎤")
        else:
            self.listener.stop()
            self.ui.show_response("Mikrofon o'chirildi. 🔇")


if __name__ == "__main__":
    App().run()
