from __future__ import annotations

import tkinter as tk

from system.config.loader import save_settings
from system.config.settings import ReplicaSettings


class SettingsPanel:
    def __init__(self, settings: ReplicaSettings) -> None:
        self.settings = settings

    def open(self) -> None:
        root = tk.Tk()
        root.title("Replica Settings")
        root.geometry("380x280")

        volume_var = tk.DoubleVar(value=self.settings.volume)
        interval_var = tk.IntVar(value=self.settings.screen.interval_seconds)
        mode_var = tk.StringVar(value=self.settings.ai.performance_mode)

        tk.Label(root, text="Громкость").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Scale(root, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", variable=volume_var).pack(fill="x", padx=10)

        tk.Label(root, text="Интервал анализа экрана (сек)").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Spinbox(root, from_=5, to=120, textvariable=interval_var).pack(fill="x", padx=10)

        tk.Label(root, text="Режим производительности").pack(anchor="w", padx=10, pady=(10, 0))
        tk.OptionMenu(root, mode_var, "eco", "balanced", "max").pack(fill="x", padx=10)

        def on_save() -> None:
            self.settings.volume = float(volume_var.get())
            self.settings.screen.interval_seconds = int(interval_var.get())
            self.settings.ai.performance_mode = mode_var.get()
            save_settings(self.settings)
            root.destroy()

        tk.Button(root, text="Сохранить", command=on_save).pack(pady=16)
        root.mainloop()
