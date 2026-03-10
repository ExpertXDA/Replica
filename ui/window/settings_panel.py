from __future__ import annotations

import tkinter as tk
from typing import Callable

from system.config.loader import save_settings
from system.config.settings import ReplicaSettings


class SettingsPanel:
    def __init__(self, root: tk.Tk, settings: ReplicaSettings, on_saved: Callable[[], None] | None = None) -> None:
        self.root = root
        self.settings = settings
        self.on_saved = on_saved

    def open(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Replica Settings")
        window.geometry("460x420")

        interval_var = tk.IntVar(value=self.settings.screen.interval_seconds)
        mode_var = tk.StringVar(value=self.settings.ai.performance_mode)
        model_var = tk.StringVar(value=self.settings.ai.llm_model)
        tts_voice_var = tk.StringVar(value=self.settings.voice.tts_voice)
        tts_rate_var = tk.IntVar(value=self.settings.voice.tts_rate)
        sensitivity_var = tk.DoubleVar(value=self.settings.voice.sensitivity)
        display_var = tk.BooleanVar(value=self.settings.interface.display_enabled)
        avatar_size_var = tk.IntVar(value=self.settings.interface.avatar_size)
        alpha_var = tk.DoubleVar(value=self.settings.interface.transparency)

        def row_label(text: str) -> None:
            tk.Label(window, text=text, anchor="w").pack(fill="x", padx=12, pady=(8, 0))

        row_label("AI модель")
        tk.Entry(window, textvariable=model_var).pack(fill="x", padx=12)

        row_label("Режим производительности")
        tk.OptionMenu(window, mode_var, "eco", "balanced", "max").pack(fill="x", padx=12)

        row_label("Интервал анализа экрана (сек)")
        tk.Spinbox(window, from_=5, to=120, textvariable=interval_var).pack(fill="x", padx=12)

        row_label("Голос (предпочтительно мужской)")
        tk.Entry(window, textvariable=tts_voice_var).pack(fill="x", padx=12)

        row_label("Скорость речи")
        tk.Scale(window, from_=120, to=230, orient="horizontal", variable=tts_rate_var).pack(fill="x", padx=12)

        row_label("Чувствительность микрофона")
        tk.Scale(window, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", variable=sensitivity_var).pack(fill="x", padx=12)

        row_label("Размер аватара")
        tk.Spinbox(window, from_=48, to=256, textvariable=avatar_size_var).pack(fill="x", padx=12)

        row_label("Прозрачность оверлея")
        tk.Scale(window, from_=0.3, to=1.0, resolution=0.05, orient="horizontal", variable=alpha_var).pack(fill="x", padx=12)

        tk.Checkbutton(window, text="Показывать ассистента поверх окон", variable=display_var).pack(anchor="w", padx=12, pady=10)

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

        tk.Button(window, text="Сохранить", command=on_save).pack(pady=12)
