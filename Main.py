from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.brain.assistant_brain import AssistantBrain
from core.brain.llm_adapter import LLMAdapter
from core.memory.memory_store import MemoryStore
from core.speech.stt_adapter import STTAdapter
from core.speech.tts_adapter import TTSAdapter
from system.commands.command_router import CommandRouter
from system.config.loader import load_settings
from ui.avatar.avatar_provider import AvatarProvider
from ui.emotions.state import Emotion
from ui.window.overlay import OverlayWindow
from ui.window.settings_panel import SettingsPanel


class ReplicaApp:
    def __init__(self) -> None:
        self.settings = load_settings()

        # Инициализация интерфейса
        self.root = tk.Tk()
        self.root.title("Replica")
        self.root.geometry("520x600")
        self.root.configure(bg="#121212")

        # --- СТИЛИЗАЦИЯ (ТЕМНЫЙ СТИЛЬ) ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background="#2d2d2d", foreground="#ffffff", borderwidth=0, padding=8)
        style.map("TButton", background=[('active', '#3d3d3d')])
        style.configure("Accent.TButton", background="#0078D7", foreground="white", borderwidth=0, padding=8)
        style.map("Accent.TButton", background=[('active', '#005a9e')])

        # Логика системы
        self.memory = MemoryStore(
            short_term_limit=self.settings.performance.max_memory_items // 4,
            long_term_limit=self.settings.performance.max_memory_items,
        )

        self.llm = LLMAdapter(self.settings.ai.llm_model)
        self.brain = AssistantBrain(self.memory, self.llm)
        self.tts = TTSAdapter()
        self.stt = STTAdapter(language="ru-RU", wake_word="реплика")
        self.commands = CommandRouter(llm=self.llm)
        self.avatar_provider = AvatarProvider("assets/avatars")

        self.status_var = tk.StringVar(value="Инициализация системы...")
        self.input_var = tk.StringVar()

        self._build_main_ui()

        self.overlay = OverlayWindow(
            self.root,
            avatar_provider=self.avatar_provider,
            initial_text="Replica: активна",
            topmost=self.settings.interface.always_on_top,
            transparency=self.settings.interface.transparency,
            avatar_size=self.settings.interface.avatar_size,
            auto_hide=self.settings.interface.auto_hide
        )
        self.overlay.set_visible(self.settings.interface.display_enabled)

    def _build_main_ui(self) -> None:
        tk.Label(self.root, text="REPLICA", bg="#121212", fg="#0078D7",
                 font=("Segoe UI", 20, "bold")).pack(pady=(15, 0))
        tk.Label(self.root, textvariable=self.status_var, bg="#121212", fg="#888",
                 font=("Segoe UI", 9)).pack(pady=(0, 10))

        # История диалога
        self.history = tk.Text(self.root, height=14, bg="#181818", fg="#ccc",
                               relief="flat", font=("Segoe UI", 10), padx=10, pady=10)
        self.history.pack(fill="both", expand=True, padx=20)
        self.history.configure(state="disabled")

        # Поле ввода
        input_frame = tk.Frame(self.root, bg="#121212")
        input_frame.pack(fill="x", padx=20, pady=15)

        entry = tk.Entry(input_frame, textvariable=self.input_var, bg="#252525",
                         fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=8)
        entry.bind("<Return>", lambda _e: self._send_text())

        ttk.Button(input_frame, text="Отправить", command=self._send_text, style="Accent.TButton").pack(side="left",
                                                                                                        padx=10)

        # Контролы
        ctrl_frame = tk.Frame(self.root, bg="#121212")
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 15))
        ttk.Button(ctrl_frame, text="Настройки", command=self._open_settings).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Выход", command=self.shutdown).pack(side="right", padx=5)

    def start(self) -> None:
        ready, provider = self.llm.ensure_model_ready()
        self.status_var.set(f"AI готова ({provider}:{self.settings.ai.llm_model})" if ready else "Ошибка AI")

        if self.settings.voice.continuous_listening:
            self.stt.start_continuous_listening(
                on_text=lambda text: self.root.after(0, lambda: self._handle_user_text(text)),
                sensitivity=self.settings.voice.sensitivity,
                wake_word_enabled=self.settings.voice.wake_word_enabled,
            )

        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.root.mainloop()

    def _open_settings(self) -> None:
        SettingsPanel(self.root, self.settings, on_saved=lambda: self.status_var.set("Настройки сохранены")).open()

    def _send_text(self) -> None:
        text = self.input_var.get().strip()
        self.input_var.set("")
        self._handle_user_text(text)

    def _handle_user_text(self, user_text: str) -> None:
        if not user_text: return
        self._append_history(f"Ты: {user_text}")
        self.status_var.set("Replica анализирует...")
        self.root.update_idletasks()

        reply = self.brain.generate_reply(user_text=user_text, screen_summary="")

        if reply.intent:
            result = self.commands.execute(reply.intent, reply.argument)
            self._say(result, reply.emotion)
        else:
            self._say(reply.text, reply.emotion)
        self.status_var.set("Replica готова")

    def _say(self, text: str, emotion: Emotion) -> None:
        self._append_history(f"Replica: {text}")
        self.overlay.update_avatar(emotion)
        self.overlay.update_text(f"Replica: {text}")
        self.tts.speak(text)

    def _append_history(self, text: str) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", text + "\n")
        self.history.see("end")
        self.history.configure(state="disabled")

    def shutdown(self) -> None:
        if self.stt: self.stt.stop()
        self.root.destroy()


if __name__ == "__main__":
    ReplicaApp().start()