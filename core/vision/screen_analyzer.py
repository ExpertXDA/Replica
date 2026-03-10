from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO


@dataclass
class ScreenAnalysis:
    changed: bool
    summary: str
    diff_score: float


class ScreenAnalyzer:
    def __init__(self, change_threshold: float = 20.0) -> None:
        self.change_threshold = change_threshold
        self._last_frame = None

    def capture_screen(self) -> tuple[str | None, object | None]:
        try:
            import mss  # type: ignore
            import numpy as np
            from PIL import Image  # type: ignore

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                raw = sct.grab(monitor)
                image = Image.frombytes("RGB", raw.size, raw.rgb)
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                frame = np.array(image)
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                return img_b64, frame
        except Exception:
            return None, None

    def analyze_change(self, frame: object | None) -> ScreenAnalysis:
        try:
            import numpy as np

            if frame is None:
                return ScreenAnalysis(changed=False, summary="Экран недоступен.", diff_score=0.0)
            if self._last_frame is None:
                self._last_frame = frame
                return ScreenAnalysis(changed=False, summary="Стартовое наблюдение экрана.", diff_score=0.0)

            diff = float(np.mean(np.abs(frame - self._last_frame)))
            self._last_frame = frame
            changed = diff >= self.change_threshold

            if changed:
                return ScreenAnalysis(changed=True, summary="На экране заметные изменения.", diff_score=diff)
            return ScreenAnalysis(changed=False, summary="Сцена стабильна.", diff_score=diff)
        except Exception:
            return ScreenAnalysis(changed=False, summary="Не удалось проанализировать экран.", diff_score=0.0)
