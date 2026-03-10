from __future__ import annotations

import subprocess
import threading
import queue
import numpy as np
import sounddevice as sd


class TTSAdapter:

    def __init__(self, rate: float = 1.0) -> None:
        self.rate = rate
        self._queue: queue.Queue[str] = queue.Queue()

        self.piper_path = "piper/piper.exe"
        self.model_path = "piper/models/ru_RU-dmitri-medium.onnx"

        # иногда Windows выбирает не то устройство
        sd.default.samplerate = 22050
        sd.default.channels = 1

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def speak(self, text: str) -> None:
        if text.strip():
            self._queue.put(text)

    def _loop(self) -> None:
        while True:
            text = self._queue.get()

            try:
                process = subprocess.Popen(
                    [
                        self.piper_path,
                        "-m",
                        self.model_path,
                        "--length_scale",
                        str(1 / self.rate),
                        "--output_raw",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                )

                audio_bytes, _ = process.communicate(input=text.encode("utf-8"))

                if not audio_bytes:
                    print("TTS: пустой аудио буфер")
                    continue

                # Piper -> int16
                audio = np.frombuffer(audio_bytes, dtype=np.int16)

                # int16 -> float32
                audio = audio.astype(np.float32) / 32768.0

                sd.play(audio)
                sd.wait()

            except Exception as e:
                print("TTS error:", e)