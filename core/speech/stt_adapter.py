from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable


@dataclass
class STTResult:
    text: str
    provider: str


class STTAdapter:
    def __init__(self, language: str = "ru-RU", wake_word: str = "replica") -> None:
        self.language = language
        self.wake_word = wake_word.lower()
        self._running = False
        self._thread: threading.Thread | None = None

    def start_continuous_listening(
        self,
        on_text: Callable[[str], None],
        sensitivity: float = 0.5,
        wake_word_enabled: bool = True,
    ) -> bool:
        if self._running:
            return True

        self._running = True

        def loop() -> None:
            try:
                import speech_recognition as sr  # type: ignore
            except Exception:
                self._running = False
                return

            recognizer = sr.Recognizer()
            recognizer.energy_threshold = max(100, int(1000 * sensitivity))
            try:
                mic = sr.Microphone()
            except Exception:
                self._running = False
                return

            while self._running:
                try:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.2)
                        audio = recognizer.listen(source, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio, language=self.language).strip()
                    if not text:
                        continue
                    normalized = text.lower()
                    if wake_word_enabled and self.wake_word not in normalized:
                        continue
                    cleaned = text
                    if wake_word_enabled:
                        cleaned = normalized.replace(self.wake_word, "").strip() or text
                    on_text(cleaned)
                except Exception:
                    continue

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._running = False
