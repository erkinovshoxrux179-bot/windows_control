"""
UI — suzib yuruvchi (floating), har doim ustda turuvchi boshqaruv paneli.

Rasmga mos ko'rinish:
  [ Windows controller ]  [ Buyruq yuboring... ]  [ mic ]  [ to'lqin ]  [ avatar ]
"""

import customtkinter as ctk

import config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Ranglar
BG       = "#1e2530"
ACCENT   = "#4a90e2"
INPUT_BG = "#2a323f"
TEXT     = "#e6edf3"
MUTED    = "#8b97a7"


class ControllerUI(ctk.CTk):
    def __init__(self, on_submit, on_mic_toggle=None):
        super().__init__()
        self.on_submit = on_submit
        self.on_mic_toggle = on_mic_toggle or (lambda enabled: None)
        self._mic_on = config.ALWAYS_LISTENING
        self._wave_running = False
        self._wave_phase = 0

        # --- Oyna sozlamalari (frameless, ustda) ---
        self.overrideredirect(True)            # ramkasiz
        self.attributes("-topmost", config.UI_ALWAYS_ON_TOP)
        try:
            self.attributes("-alpha", 0.97)
        except Exception:
            pass
        w, h = config.UI_WIDTH, config.UI_HEIGHT
        sw = self.winfo_screenwidth()
        x = (sw - w) // 2
        y = 40
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(fg_color=BG)

        self._build()
        self._enable_drag()

    # -----------------------------------------------------------------
    def _build(self):
        container = ctk.CTkFrame(self, fg_color=BG, corner_radius=18)
        container.pack(fill="both", expand=True, padx=4, pady=4)
        container.grid_columnconfigure(1, weight=1)

        # Sarlavha
        self.title_lbl = ctk.CTkLabel(
            container, text=config.APP_TITLE,
            font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT,
        )
        self.title_lbl.grid(row=0, column=0, padx=(18, 12), pady=10)

        # Matn kiritish maydoni
        self.entry = ctk.CTkEntry(
            container, placeholder_text="Buyruq yuboring...",
            height=38, corner_radius=12, border_width=0,
            fg_color=INPUT_BG, text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=14),
        )
        self.entry.grid(row=0, column=1, sticky="ew", pady=12)
        self.entry.bind("<Return>", self._submit)

        # Mikrofon tugmasi
        self.mic_btn = ctk.CTkButton(
            container, text="🎤", width=40, height=38, corner_radius=12,
            fg_color=INPUT_BG, hover_color="#39424f",
            font=ctk.CTkFont(size=16), command=self._toggle_mic,
        )
        self.mic_btn.grid(row=0, column=2, padx=(10, 6))

        # To'lqin (waveform) indikatori — kichik kanvas
        self.wave = ctk.CTkCanvas(
            container, width=46, height=30, bg=BG, highlightthickness=0
        )
        self.wave.grid(row=0, column=3, padx=6)
        self._bars = []
        for i in range(5):
            bar = self.wave.create_rectangle(
                i * 9 + 2, 12, i * 9 + 7, 18, fill=ACCENT, width=0
            )
            self._bars.append(bar)

        # Avatar (yumaloq tugma)
        self.avatar = ctk.CTkButton(
            container, text="✦", width=40, height=40, corner_radius=20,
            fg_color="#0f1620", hover_color="#16202c", text_color=ACCENT,
            font=ctk.CTkFont(size=18),
        )
        self.avatar.grid(row=0, column=4, padx=(6, 14))

        # Javob/holat satri (panel ostida ko'rinadi)
        self.status_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12),
            text_color=MUTED, fg_color=BG, corner_radius=10, wraplength=config.UI_WIDTH - 40,
        )
        # Boshlanishda yashirin; javob kelganda ko'rsatamiz

        self._update_mic_visual()

    # -----------------------------------------------------------------
    #  Sudrash (drag) — ramkasiz oynani ko'chirish
    # -----------------------------------------------------------------
    def _enable_drag(self):
        def start(e):
            self._dx, self._dy = e.x, e.y
        def move(e):
            x = self.winfo_x() + e.x - self._dx
            y = self.winfo_y() + e.y - self._dy
            self.geometry(f"+{x}+{y}")
        for widget in (self, self.title_lbl):
            widget.bind("<Button-1>", start)
            widget.bind("<B1-Motion>", move)

    # -----------------------------------------------------------------
    #  Hodisalar
    # -----------------------------------------------------------------
    def _submit(self, event=None):
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, "end")
            self.on_submit(text)

    def _toggle_mic(self):
        self._mic_on = not self._mic_on
        self._update_mic_visual()
        self.on_mic_toggle(self._mic_on)

    def _update_mic_visual(self):
        if self._mic_on:
            self.mic_btn.configure(fg_color=ACCENT, text="🎤")
        else:
            self.mic_btn.configure(fg_color=INPUT_BG, text="🔇")

    # -----------------------------------------------------------------
    #  Tashqi API (boshqa modullar chaqiradi) — thread-safe
    # -----------------------------------------------------------------
    def set_status(self, state: str):
        """Ovoz holatiga qarab to'lqinni boshqaradi."""
        self.after(0, self._apply_status, state)

    def _apply_status(self, state: str):
        if state in ("listening", "recognizing"):
            if not self._wave_running:
                self._wave_running = True
                self._animate_wave()
        else:
            self._wave_running = False

    def _animate_wave(self):
        import math
        if not self._wave_running:
            # tinch holat — pastga tushir
            for i, bar in enumerate(self._bars):
                self.wave.coords(bar, i * 9 + 2, 13, i * 9 + 7, 17)
            return
        self._wave_phase += 1
        for i, bar in enumerate(self._bars):
            amp = (math.sin(self._wave_phase * 0.4 + i) + 1) / 2  # 0..1
            half = 3 + amp * 11
            self.wave.coords(bar, i * 9 + 2, 15 - half, i * 9 + 7, 15 + half)
        self.after(90, self._animate_wave)

    def show_response(self, text: str):
        """Javobni panel ostida ko'rsatadi."""
        self.after(0, self._show_response, text)

    def _show_response(self, text: str):
        if not text:
            return
        self.status_lbl.configure(text=text)
        self.status_lbl.place(x=20, y=config.UI_HEIGHT + 2)
        # 6 soniyadan keyin yashiramiz
        self.after(6000, self.status_lbl.place_forget)

    def set_recognized_text(self, text: str):
        """Tushunilgan ovozli matnni inputga qisqa ko'rsatish."""
        self.after(0, lambda: (self.entry.delete(0, "end"),
                               self.entry.insert(0, text)))
