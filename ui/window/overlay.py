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
        transparency: float = 0.9,
        avatar_size: int = 96,
    ) -> None:

        self.avatar_provider = avatar_provider
        self.avatar_size = avatar_size
        self._photo: PhotoImage | None = None

        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", topmost)
        self.window.attributes("-alpha", transparency)

        # стартовая позиция
        screen_w = self.window.winfo_screenwidth()
        self.window.geometry(f"380x120+{screen_w-420}+30")

        # основной контейнер
        self.frame = tk.Frame(self.window, bg="#121212")
        self.frame.pack(fill="both", expand=True)

        # аватар
        self.avatar_label = tk.Label(
            self.frame,
            text="😐",
            bg="#121212",
            fg="#f0f0f0",
            font=("Segoe UI Emoji", 28)
        )

        self.avatar_label.pack(
            side="left",
            padx=12,
            pady=10
        )

        # текст
        self.text_label = tk.Label(
            self.frame,
            text=initial_text,
            fg="#f0f0f0",
            bg="#121212",
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
            wraplength=250
        )

        self.text_label.pack(
            side="left",
            fill="both",
            expand=True,
            padx=8,
            pady=10
        )

        # drag support
        self._drag_start_x = 0
        self._drag_start_y = 0

        for widget in (self.frame, self.avatar_label, self.text_label):
            widget.bind("<Button-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)

    # ------------------------------------------------
    # DRAG WINDOW
    # ------------------------------------------------

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_start_x = event.x_root - self.window.winfo_x()
        self._drag_start_y = event.y_root - self.window.winfo_y()

    def _drag(self, event: tk.Event) -> None:

        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y

        self.window.geometry(f"+{x}+{y}")

    # ------------------------------------------------
    # VISIBILITY
    # ------------------------------------------------

    def set_visible(self, visible: bool) -> None:

        if visible:
            self.window.deiconify()
        else:
            self.window.withdraw()

    # ------------------------------------------------
    # AVATAR
    # ------------------------------------------------

    def update_avatar(self, emotion: Emotion) -> None:

        path = self.avatar_provider.get_avatar_image_path(emotion)

        if path:

            try:

                image = PhotoImage(file=path)

                w = image.width()
                h = image.height()

                scale = max(1, int(max(w, h) / self.avatar_size))

                image = image.subsample(scale, scale)

                self._photo = image

                self.avatar_label.config(
                    image=self._photo,
                    text=""
                )

                return

            except Exception:
                pass

        # fallback emoji
        self.avatar_label.config(
            image="",
            text=self.avatar_provider.get_fallback_emoji(emotion),
            font=("Segoe UI Emoji", 28)
        )

    # ------------------------------------------------
    # TEXT
    # ------------------------------------------------

    def update_text(self, text: str) -> None:

        # ограничиваем длину
        if len(text) > 220:
            text = text[:220] + "..."

        # обновляем через idle чтобы не лагал tk
        self.window.after_idle(
            lambda: self.text_label.config(text=text)
        )

