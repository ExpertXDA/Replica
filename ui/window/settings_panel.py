from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from system.config.loader import save_settings
from system.config.settings import ReplicaSettings


class SettingsPanel:

    def __init__(
        self,
        root: tk.Tk,
        settings: ReplicaSettings,
        on_saved: Callable[[], None] | None = None
    ) -> None:

        self.root = root
        self.settings = settings
        self.on_saved = on_saved

    def open(self) -> None:

        window = tk.Toplevel(self.root)
        window.title("Replica Settings")
        window.geometry("500x470")
        window.resizable(False, False)

        container = ttk.Frame(window, padding=16)
        container.pack(fill="both", expand=True)

        # ---------- VARIABLES ----------

        interval_var = tk.IntVar(value=self.settings.screen.interval_seconds)
        mode_var = tk.StringVar(value=self.settings.ai.performance_mode)
        model_var = tk.StringVar(value=self.settings.ai.llm_model)

        tts_voice_var = tk.StringVar(value=self.settings.voice.tts_voice)
        tts_rate_var = tk.IntVar(value=self.settings.voice.tts_rate)
        sensitivity_var = tk.DoubleVar(value=self.settings.voice.sensitivity)

        display_var = tk.BooleanVar(value=self.settings.interface.display_enabled)
        avatar_size_var = tk.IntVar(value=self.settings.interface.avatar_size)
        alpha_var = tk.DoubleVar(value=self.settings.interface.transparency)

        # ---------- SECTIONS ----------

        ai_frame = ttk.LabelFrame(container, text="AI", padding=12)
        ai_frame.pack(fill="x", pady=6)

        voice_frame = ttk.LabelFrame(container, text="Голос", padding=12)
        voice_frame.pack(fill="x", pady=6)

        interface_frame = ttk.LabelFrame(container, text="Интерфейс", padding=12)
        interface_frame.pack(fill="x", pady=6)

        # ---------- AI ----------

        ttk.Label(ai_frame, text="AI модель").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(ai_frame, textvariable=model_var, width=32).grid(row=0, column=1, sticky="ew")

        ttk.Label(ai_frame, text="Режим производительности").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Combobox(
            ai_frame,
            textvariable=mode_var,
            values=["eco", "balanced", "max"],
            state="readonly",
            width=29
        ).grid(row=1, column=1, sticky="ew")

        ttk.Label(ai_frame, text="Интервал анализа экрана (сек)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Spinbox(
            ai_frame,
            from_=5,
            to=120,
            textvariable=interval_var,
            width=10
        ).grid(row=2, column=1, sticky="w")

        # ---------- VOICE ----------

        ttk.Label(voice_frame, text="Голос").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(voice_frame, textvariable=tts_voice_var, width=32).grid(row=0, column=1, sticky="ew")

        ttk.Label(voice_frame, text="Скорость речи").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Scale(
            voice_frame,
            from_=120,
            to=230,
            variable=tts_rate_var,
            orient="horizontal"
        ).grid(row=1, column=1, sticky="ew")

        ttk.Label(voice_frame, text="Чувствительность микрофона").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Scale(
            voice_frame,
            from_=0.1,
            to=1.0,
            variable=sensitivity_var,
            orient="horizontal"
        ).grid(row=2, column=1, sticky="ew")

        # ---------- INTERFACE ----------

        ttk.Label(interface_frame, text="Размер аватара").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Spinbox(
            interface_frame,
            from_=48,
            to=256,
            textvariable=avatar_size_var,
            width=10
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(interface_frame, text="Прозрачность оверлея").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Scale(
            interface_frame,
            from_=0.3,
            to=1.0,
            variable=alpha_var,
            orient="horizontal"
        ).grid(row=1, column=1, sticky="ew")

        ttk.Checkbutton(
            interface_frame,
            text="Показывать ассистента поверх окон",
            variable=display_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=6)

        # ---------- SAVE ----------

        button_frame = ttk.Frame(container)
        button_frame.pack(fill="x", pady=(10, 0))

        def on_save() -> None:

            self.settings.ai.llm_model = model_var.get().strip() or self.settings.ai.llm_model
            self.settings.ai.performance_mode = mode_var.get()

            self.settings.screen.interval_seconds = int(interval_var.get())

            self.settings.voice.tts_voice = tts_voice_var.get().strip() or "male"
            self.settings.voice.tts_rate = int(tts_rate_var.get())
            self.settings.voice.sensitivity = float(sensitivity_var.get())

            self.settings.interface.display_enabled = bool(display_var.get())
            self.settings.interface.avatar_size = int(avatar_size_var.get())
            self.settings.interface.transparency = float(alpha_var.get())

            save_settings(self.settings)

            if self.on_saved:
                self.on_saved()

            window.destroy()

        ttk.Button(
            button_frame,
            text="Сохранить настройки",
            command=on_save
        ).pack(side="right")

