import tkinter as tk
from ui.avatar.avatar_provider import AvatarProvider
from ui.emotions.state import Emotion
from PIL import Image, ImageTk


class OverlayWindow:
    def __init__(
            self,
            root: tk.Tk,
            avatar_provider: AvatarProvider,
            initial_text: str = "Replica готова",
            topmost: bool = True,
            transparency: float = 0.95,
            avatar_size: int = 128,
            auto_hide: bool = True,
    ) -> None:

        self.avatar_provider = avatar_provider
        self.avatar_size = avatar_size
        self.auto_hide = auto_hide
        self.padding_x = 20
        self._photo = None
        self._hide_timer = None

        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", topmost)
        self.window.attributes("-alpha", transparency)
        self.window.attributes("-transparentcolor", "#000001")

        self.canvas = tk.Canvas(self.window, bg="#000001", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Пузырь речи (облако)
        self.bubble = self.canvas.create_polygon(0, 0, 0, 0, fill="#202020", outline="#404040", width=2)

        # Текст (wraplength ограничивает ширину, чтобы не вылезал)
        self.text_id = self.canvas.create_text(
            self.avatar_size + self.padding_x + 30, 30, text=initial_text, fill="white",
            font=("Segoe UI", 12), width=300, anchor="nw"
        )

        # Аватар
        self.avatar_label = tk.Label(self.window, bg="#000001", fg="#f0f0f0", font=("Segoe UI Emoji", 40))
        self.avatar_label.place(x=10, y=10)

        # Драг
        for target in (self.canvas, self.avatar_label):
            target.bind("<Button-1>", self._start_drag)
            target.bind("<B1-Motion>", self._drag)

        self._update_geometry(initial_text)

    def _update_geometry(self, text):
        # Рассчитываем размер текста
        bbox = self.canvas.bbox(self.text_id)
        if not bbox: return

        text_h = (bbox[3] - bbox[1]) + 40
        window_h = max(self.avatar_size + 40, text_h + 40)
        window_w = self.avatar_size + 400

        self.window.geometry(f"{window_w}x{window_h}")
        self._draw_bubble(text_h)

    def _draw_bubble(self, text_h):
        x, y, w, h = self.avatar_size + self.padding_x, 10, 360, max(80, text_h)
        r = 15
        points = [
            x + r, y, x + w - r, y, x + w, y + r, x + w, y + h - r, x + w - r, y + h,
            x + r, y + h, x, y + h - r, x, y + r, x - 15, y + 40, x, y + 30
        ]
        self.canvas.coords(self.bubble, *points)

    def _start_drag(self, event):
        self._drag_start_x = event.x_root - self.window.winfo_x()
        self._drag_start_y = event.y_root - self.window.winfo_y()

    def _drag(self, event):
        x = event.x_root - self._drag_start_x
        y = event.y_root - self._drag_start_y
        self.window.geometry(f"+{x}+{y}")

    def update_avatar(self, emotion: Emotion) -> None:
        path = self.avatar_provider.get_avatar_image_path(emotion)
        if path:
            try:
                img = Image.open(path).resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)
                self._photo = ImageTk.PhotoImage(img)
                self.avatar_label.config(image=self._photo, text="")
            except Exception:
                self._show_fallback(emotion)
        else:
            self._show_fallback(emotion)
        self.window.deiconify()

    def _show_fallback(self, emotion: Emotion) -> None:
        emoji = self.avatar_provider.get_fallback_emoji(emotion)
        self.avatar_label.config(image="", text=emoji, font=("Segoe UI Emoji", 60))

    def update_text(self, text: str) -> None:
        self.window.deiconify()
        self.canvas.itemconfig(self.text_id, state="normal", text=text)
        self.canvas.itemconfig(self.bubble, state="normal")
        self._update_geometry(text)

        if self._hide_timer: self.window.after_cancel(self._hide_timer)
        self._hide_timer = self.window.after(5000, self._hide_elements)

    def _hide_elements(self):
        if self.auto_hide:
            self.window.withdraw()
        else:
            self.canvas.itemconfig(self.text_id, state="hidden")
            self.canvas.itemconfig(self.bubble, state="hidden")

    def set_visible(self, visible: bool) -> None:
        self.window.deiconify() if visible else self.window.withdraw()