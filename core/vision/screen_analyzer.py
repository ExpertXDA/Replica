from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@dataclass
class ScreenAnalysis:
    changed: bool
    summary: str
    diff_score: float


class ScreenAnalyzer:

    def __init__(self, llm=None, change_threshold: float = 20.0) -> None:
        self.change_threshold = change_threshold
        self._last_frame = None
        self.llm = llm

    # ------------------------------------------------
    # SCREENSHOT
    # ------------------------------------------------

    def capture_screen(self):

        try:
            import mss
            import numpy as np
            from PIL import Image

            with mss.mss() as sct:

                monitor = sct.monitors[1]
                raw = sct.grab(monitor)

                image = Image.frombytes("RGB", raw.size, raw.rgb)

                # уменьшение без убийства качества
                image.thumbnail((1280, 720))

                buffer = BytesIO()
                image.save(buffer, format="PNG")

                frame = np.array(image)

                img_b64 = base64.b64encode(buffer.getvalue()).decode()

                return img_b64, frame

        except Exception:
            return None, None

    # ------------------------------------------------
    # CHANGE DETECTION
    # ------------------------------------------------

    def analyze_change(self, frame):

        try:
            import numpy as np

            if frame is None:
                return ScreenAnalysis(False, "Экран недоступен.", 0)

            if self._last_frame is None:
                self._last_frame = frame
                return ScreenAnalysis(True, "Первичное наблюдение.", 0)

            diff = float(np.mean(np.abs(frame - self._last_frame)))

            changed = diff >= self.change_threshold

            self._last_frame = frame

            return ScreenAnalysis(
                changed=changed,
                summary="Экран изменился." if changed else "Экран стабилен.",
                diff_score=diff
            )

        except Exception:
            return ScreenAnalysis(False, "Ошибка анализа.", 0)

    # ------------------------------------------------
    # OCR
    # ------------------------------------------------

    def read_text(self, frame):

        try:
            import cv2
            from PIL import Image

            if frame is None:
                return ""

            img = frame

            # upscale для лучшего OCR
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            thresh = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                2
            )

            pil = Image.fromarray(thresh)

            text = pytesseract.image_to_string(
                pil,
                lang="rus+eng",
                config="--psm 3"
            )

            return text[:500]

        except Exception:
            return ""

    # ------------------------------------------------
    # VISION LLM
    # ------------------------------------------------

    def vision_llm_analysis(self, img_b64, text):

        if not self.llm:

            if text:
                return f"На экране текст: {text[:200]}"

            return "Графический интерфейс без читаемого текста."

        prompt = f"""
Ты анализируешь скриншот компьютера пользователя.

Текст распознанный OCR:
{text}

Определи:

1. какое приложение открыто
2. что происходит на экране
3. какие элементы интерфейса видны
4. что пользователь может сделать дальше

Ответ кратко (2-3 предложения).
"""

        try:

            result = self.llm.generate(
                prompt=prompt,
                image=img_b64
            )

            return result.text.strip()

        except Exception:
            return "Vision анализ не удался."

    # ------------------------------------------------
    # AUTO MODE (если нужен мониторинг)
    # ------------------------------------------------

    def analyze(self):

        img_b64, frame = self.capture_screen()

        change = self.analyze_change(frame)

        if frame is None:
            return change

        text = self.read_text(frame)

        if not change.changed:

            if text:
                return ScreenAnalysis(
                    False,
                    f"Экран стабилен. Найден текст: {text[:120]}",
                    change.diff_score
                )

            return change

        summary = self.vision_llm_analysis(img_b64, text)

        return ScreenAnalysis(True, summary, change.diff_score)

    # ------------------------------------------------
    # ON DEMAND ANALYSIS (правильный режим)
    # ------------------------------------------------

    def analyze_on_demand(self):

        img_b64, frame = self.capture_screen()

        if frame is None:
            return ScreenAnalysis(False, "Экран недоступен.", 0)

        text = self.read_text(frame)

        summary = self.vision_llm_analysis(img_b64, text)

        return ScreenAnalysis(True, summary, 0)

