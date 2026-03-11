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

            # --- НАСТРОЙКИ ДЛЯ ДЛИННЫХ ФРАЗ ---
            recognizer.energy_threshold = max(100, int(1000 * sensitivity))
            recognizer.pause_threshold = 3.0  # Ждет 3 секунды тишины перед завершением фразы
            recognizer.dynamic_energy_threshold = True

            try:
                mic = sr.Microphone()
            except Exception:
                self._running = False
                return

            while self._running:
                try:
                    with mic as source:
                        # Адаптация к шуму только в начале или изредка, чтобы не ломать поток
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)

                        # phrase_time_limit=15 позволяет говорить долго
                        audio = recognizer.listen(source, phrase_time_limit=15)

                    text = recognizer.recognize_google(audio, language=self.language).strip()

                    if not text:
                        continue

                    normalized = text.lower()

                    # Проверка wake_word
                    if wake_word_enabled and self.wake_word not in normalized:
                        continue

                    cleaned = normalized.replace(self.wake_word, "").strip() if wake_word_enabled else text

                    if cleaned:
                        on_text(cleaned)

                except sr.WaitTimeoutError:
                    continue
                except Exception:
                    # Игнорируем ошибки распознавания (например, когда фоновый шум приняли за речь)
                    continue

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._running = False
