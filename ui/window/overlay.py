from __future__ import annotations

import tkinter as tk
from tkinter import PhotoImage

from ui.avatar.avatar_provider import AvatarProvider
from ui.emotions.state import Emotion


class OverlayWindow:
    def __init__(
        self,
        root: tk.Tk,
        avatar_provider: AvatarProvider,
        initial_text: str = "Replica готова",
        topmost: bool = True,
        transparency: float = 0.85,
        avatar_size: int = 96,
    ) -> None:
        self.avatar_provider = avatar_provider
        self.avatar_size = avatar_size
        self._photo: PhotoImage | None = None

        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", topmost)
        self.window.attributes("-alpha", transparency)
        self.window.geometry("360x120+1520+20")

        self.frame = tk.Frame(self.window, bg="#121212")
        self.frame.pack(fill="both", expand=True)

        self.avatar_label = tk.Label(self.frame, text="😐", bg="#121212", fg="#f0f0f0", font=("Arial", 28))
        self.avatar_label.pack(side="left", padx=12, pady=10)

        self.text_label = tk.Label(
            self.frame,
            text=initial_text,
            fg="#f0f0f0",
            bg="#121212",
            font=("Arial", 11),
            justify="left",
            anchor="w",
            wraplength=230,
        )
        self.text_label.pack(side="left", fill="both", expand=True, padx=8, pady=10)

        self._drag_start_x = 0
        self._drag_start_y = 0
        for widget in (self.frame, self.avatar_label, self.text_label):
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_start_x = event.x_root - self.window.winfo_x()
        self._drag_start_y = event.y_root - self.window.winfo_y()

    def _drag(self, event: tk.Event) -> None:
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.window.geometry(f"+{x}+{y}")

    def set_visible(self, visible: bool) -> None:
        if visible:
            self.window.deiconify()
        else:
            self.window.withdraw()

    def update_avatar(self, emotion: Emotion) -> None:
        path = self.avatar_provider.get_avatar_image_path(emotion)
        if path:
            try:
                image = PhotoImage(file=path)
                factor = max(1, int(image.width() / self.avatar_size))
                image = image.subsample(factor, factor)
                self._photo = image
                self.avatar_label.config(image=self._photo, text="")
                return
            except Exception:
                pass
        self.avatar_label.config(image="", text=self.avatar_provider.get_fallback_emoji(emotion), font=("Arial", 28))

    def update_text(self, text: str) -> None:
        self.text_label.config(text=text)
