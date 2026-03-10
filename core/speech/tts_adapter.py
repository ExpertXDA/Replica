from __future__ import annotations


class TTSAdapter:
    """Text-to-speech adapter with preferred male voice selection."""

    def __init__(self, voice_name: str = "male", rate: int = 175) -> None:
        self.voice_name = voice_name
        self.rate = rate
        self._engine = None
        self._setup_engine()

    def _setup_engine(self) -> None:
        try:
            import pyttsx3  # type: ignore

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            voices = self._engine.getProperty("voices")

            preferred = [self.voice_name.lower(), "male", "dmitry", "alex", "pavel"]
            for token in preferred:
                for voice in voices:
                    name = getattr(voice, "name", "").lower()
                    if token in name:
                        self._engine.setProperty("voice", voice.id)
                        return
        except Exception:
            self._engine = None

    def set_rate(self, rate: int) -> None:
        self.rate = rate
        if self._engine:
            self._engine.setProperty("rate", rate)

    def speak(self, text: str) -> None:
        if not self._engine:
            return
        self._engine.say(text)
        self._engine.runAndWait()
