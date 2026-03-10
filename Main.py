from __future__ import annotations

import threading
import time
import tkinter as tk

from core.brain.assistant_brain import AssistantBrain
from core.brain.llm_adapter import LLMAdapter
from core.memory.memory_store import MemoryStore
from core.speech.stt_adapter import STTAdapter
from core.speech.tts_adapter import TTSAdapter
from core.vision.screen_analyzer import ScreenAnalyzer
from system.commands.command_router import CommandRouter
from system.config.loader import load_settings
from ui.avatar.avatar_provider import AvatarProvider
from ui.emotions.state import Emotion
from ui.window.overlay import OverlayWindow
from ui.window.settings_panel import SettingsPanel


class ReplicaApp:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.memory = MemoryStore(
            short_term_limit=self.settings.performance.max_memory_items // 4,
            long_term_limit=self.settings.performance.max_memory_items,
        )

        self.llm = LLMAdapter(self.settings.ai.llm_model)
        self.brain = AssistantBrain(self.memory, self.llm)
        self.tts = TTSAdapter(voice_name=self.settings.voice.tts_voice, rate=self.settings.voice.tts_rate)
        self.stt = STTAdapter(language="ru-RU", wake_word="replica")
        self.vision = ScreenAnalyzer()
        self.commands = CommandRouter()
        self.avatar_provider = AvatarProvider("assets/avatars")

        self.root = tk.Tk()
        self.root.title("Replica")
        self.root.geometry("520x340")
        self.root.configure(bg="#101010")

        self.status_var = tk.StringVar(value="Инициализация...")
        self.input_var = tk.StringVar()
        self.history = tk.Text(self.root, height=11, bg="#1b1b1b", fg="#e8e8e8", relief="flat")
        self.history.configure(state="disabled")

        self.overlay = OverlayWindow(
            self.root,
            avatar_provider=self.avatar_provider,
            initial_text="Replica: готова к запуску",
            topmost=self.settings.interface.always_on_top,
            transparency=self.settings.interface.transparency,
            avatar_size=self.settings.interface.avatar_size,
        )
        self.overlay.set_visible(self.settings.interface.display_enabled)

        self._last_screen_summary = ""
        self._running = True
        self._build_main_ui()

    def _build_main_ui(self) -> None:
        tk.Label(self.root, text="Replica", bg="#101010", fg="#f0f0f0", font=("Arial", 18, "bold")).pack(pady=(12, 6))
        tk.Label(self.root, textvariable=self.status_var, bg="#101010", fg="#9ac7ff").pack(pady=(0, 8))

        self.history.pack(fill="both", expand=True, padx=14)

        input_frame = tk.Frame(self.root, bg="#101010")
        input_frame.pack(fill="x", padx=14, pady=8)

        entry = tk.Entry(input_frame, textvariable=self.input_var, bg="#202020", fg="#f1f1f1", insertbackground="#f1f1f1")
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda _event: self._send_text())

        tk.Button(input_frame, text="Отправить", command=self._send_text).pack(side="left", padx=6)
        tk.Button(input_frame, text="Настройки", command=self._open_settings).pack(side="left")

        controls = tk.Frame(self.root, bg="#101010")
        controls.pack(fill="x", padx=14, pady=(0, 10))
        tk.Button(controls, text="Свернуть в фон", command=self.root.iconify).pack(side="left")
        tk.Button(controls, text="Выход", command=self.shutdown).pack(side="right")

    def start(self) -> None:
        ready, provider = self.llm.ensure_model_ready()
        if ready:
            self.status_var.set(f"AI готова ({provider}:{self.settings.ai.llm_model})")
        else:
            self.status_var.set("AI fallback: локальная модель недоступна")

        if self.settings.screen.enabled:
            threading.Thread(target=self._screen_loop, daemon=True).start()

        if self.settings.voice.continuous_listening:
            self.stt.start_continuous_listening(
                on_text=lambda text: self.root.after(0, lambda: self._handle_user_text(text)),
                sensitivity=self.settings.voice.sensitivity,
                wake_word_enabled=self.settings.voice.wake_word_enabled,
            )

        self.overlay.update_avatar(Emotion.NEUTRAL)
        self.overlay.update_text("Replica: активна")
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.root.mainloop()

    def _open_settings(self) -> None:
        SettingsPanel(self.root, self.settings, on_saved=self._apply_settings).open()

    def _apply_settings(self) -> None:
        self.tts.set_rate(self.settings.voice.tts_rate)
        self.overlay.set_visible(self.settings.interface.display_enabled)
        self.status_var.set("Настройки сохранены")

    def _send_text(self) -> None:
        text = self.input_var.get().strip()
        self.input_var.set("")
        self._handle_user_text(text)

    def _handle_user_text(self, user_text: str) -> None:
        if not user_text:
            return

        self._append_history(f"Ты: {user_text}")

        if self._looks_like_system_command(user_text):
            response = self.commands.execute(user_text)
            self._say(response, Emotion.CURIOUS)
            return

        reply = self.brain.generate_reply(user_text=user_text, screen_summary=self._last_screen_summary)
        self._say(reply.text, reply.emotion)

    def _say(self, text: str, emotion: Emotion) -> None:
        self._append_history(f"Replica: {text}")
        self.overlay.update_avatar(emotion)
        self.overlay.update_text(f"Replica: {text}")
        threading.Thread(target=self.tts.speak, args=(text,), daemon=True).start()

    def _append_history(self, text: str) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", text + "\n")
        self.history.see("end")
        self.history.configure(state="disabled")

    def _screen_loop(self) -> None:
        while self._running:
            _, frame = self.vision.capture_screen()
            analysis = self.vision.analyze_change(frame)
            self._last_screen_summary = f"{analysis.summary} (diff={analysis.diff_score:.2f})"
            if analysis.changed:
                self.root.after(0, lambda: self.overlay.update_text(f"Replica: {analysis.summary}"))
            time.sleep(max(5, self.settings.screen.interval_seconds))

    def _looks_like_system_command(self, text: str) -> bool:
        samples = ["открой", "запусти", "сделай скрин", "скриншот", "выключи", "громкость"]
        lower = text.lower()
        return any(sample in lower for sample in samples)

    def shutdown(self) -> None:
        self._running = False
        self.stt.stop()
        self.root.destroy()


if __name__ == "__main__":
    ReplicaApp().start()
