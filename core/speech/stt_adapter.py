from __future__ import annotations

from dataclasses import dataclass


@dataclass
class STTResult:
    text: str
    provider: str


class STTAdapter:
    """Speech-to-text adapter with a local-first strategy.

    1) Try Vosk if available.
    2) Fall back to speech_recognition (Google backend) if installed.
    3) Return an empty result when not available.
    """

    def __init__(self, language: str = "ru-RU") -> None:
        self.language = language

    def transcribe(self, audio_bytes: bytes) -> STTResult:
        if not audio_bytes:
            return STTResult(text="", provider="none")

        try:
            import vosk  # type: ignore
            import json
            import wave
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp.flush()
                with wave.open(tmp.name, "rb") as wf:
                    model = vosk.Model(lang="ru")
                    rec = vosk.KaldiRecognizer(model, wf.getframerate())
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        rec.AcceptWaveform(data)
                    payload = json.loads(rec.FinalResult())
                    return STTResult(text=payload.get("text", ""), provider="vosk")
        except Exception:
            pass

        try:
            import speech_recognition as sr  # type: ignore
            import io

            recognizer = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=self.language)
            return STTResult(text=text, provider="speech_recognition")
        except Exception:
            return STTResult(text="", provider="none")
