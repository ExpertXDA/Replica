from __future__ import annotations

import threading
import tkinter as tk


class OverlayWindow:
    def __init__(self, initial_text: str = "Replica готова") -> None:
        self.initial_text = initial_text
        self._label: tk.Label | None = None
        self._root: tk.Tk | None = None

    def start(self) -> None:
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        root = tk.Tk()
        root.title("Replica")
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.85)
        root.overrideredirect(True)
        root.geometry("320x90+1550+20")

        frame = tk.Frame(root, bg="#111111")
        frame.pack(fill="both", expand=True)

        label = tk.Label(
            frame,
            text=self.initial_text,
            fg="#e6e6e6",
            bg="#111111",
            font=("Arial", 12),
            anchor="w",
            justify="left",
            padx=10,
            pady=10,
            wraplength=290,
        )
        label.pack(fill="both", expand=True)

        self._root = root
        self._label = label
        root.mainloop()

    def update_text(self, text: str) -> None:
        if self._label is not None:
            self._label.config(text=text)
