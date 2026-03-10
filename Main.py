from __future__ import annotations

import threading
import time

from core.brain.assistant_brain import AssistantBrain
from core.brain.llm_adapter import LLMAdapter
from core.memory.memory_store import MemoryStore
from core.speech.tts_adapter import TTSAdapter
from core.vision.screen_analyzer import ScreenAnalyzer
from system.commands.command_router import CommandRouter
from system.config.loader import load_settings
from ui.avatar.emoji_avatar import pick_emoji
from ui.window.overlay import OverlayWindow
from ui.window.settings_panel import SettingsPanel


class ReplicaApp:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.memory = MemoryStore(
            short_term_limit=self.settings.performance.max_memory_items // 4,
            long_term_limit=self.settings.performance.max_memory_items,
        )
        self.brain = AssistantBrain(self.memory, LLMAdapter(self.settings.ai.llm_model))
        self.tts = TTSAdapter(voice_name=self.settings.voice.tts_voice)
        self.vision = ScreenAnalyzer()
        self.commands = CommandRouter()
        self.overlay = OverlayWindow("Replica: готова к диалогу")
        self._last_screen_summary = ""
        self._running = True

    def start(self) -> None:
        self.overlay.start()
        if self.settings.screen.enabled:
            threading.Thread(target=self._screen_loop, daemon=True).start()

        print("Replica запущена.")
        print("Команды: /settings, /exit")

        while self._running:
            user_text = input("Ты: ").strip()
            if not user_text:
                continue

            if user_text in {"/exit", "exit", "quit", "выход"}:
                self._running = False
                print("Replica: До связи.")
                break

            if user_text == "/settings":
                SettingsPanel(self.settings).open()
                print("Настройки обновлены.")
                continue

            if self._looks_like_system_command(user_text):
                result = self.commands.execute(user_text)
                self._say(result)
                continue

            reply = self.brain.generate_reply(user_text=user_text, screen_summary=self._last_screen_summary)
            avatar = pick_emoji(reply.emotion)
            self._say(f"{avatar} {reply.text}")

    def _screen_loop(self) -> None:
        while self._running:
            _, frame = self.vision.capture_screen()
            analysis = self.vision.analyze_change(frame)
            self._last_screen_summary = f"{analysis.summary} (diff={analysis.diff_score:.2f})"
            if analysis.changed:
                self.overlay.update_text(f"Replica: {analysis.summary}")
            time.sleep(max(5, self.settings.screen.interval_seconds))

    def _looks_like_system_command(self, text: str) -> bool:
        samples = ["открой", "запусти", "сделай скрин", "выключи", "громкость"]
        lower = text.lower()
        return any(sample in lower for sample in samples)

    def _say(self, text: str) -> None:
        print(f"Replica: {text}")
        self.overlay.update_text(f"Replica: {text}")
        self.tts.speak(text)


if __name__ == "__main__":
    ReplicaApp().start()
