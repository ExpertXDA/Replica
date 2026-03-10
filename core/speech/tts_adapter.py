from __future__ import annotations


class TTSAdapter:
    """Text-to-speech adapter with local pyttsx3 fallback."""

    def __init__(self, voice_name: str = "default", rate: int = 180) -> None:
        self.voice_name = voice_name
        self.rate = rate
        self._engine = None
        self._setup_engine()

    def _setup_engine(self) -> None:
        try:
            import pyttsx3  # type: ignore

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            if self.voice_name != "default":
                for voice in self._engine.getProperty("voices"):
                    if self.voice_name.lower() in voice.name.lower():
                        self._engine.setProperty("voice", voice.id)
                        break
        except Exception:
            self._engine = None

    def speak(self, text: str) -> None:
        if not self._engine:
            return
        self._engine.say(text)
        self._engine.runAndWait()
