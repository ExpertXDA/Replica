from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO

import mss
import numpy as np
import pytesseract
from PIL import Image

# Путь к Tesseract (проверь, что он актуален для твоей системы)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@dataclass
class ScreenAnalysis:
    summary: str  # Ответ от ИИ
    ocr_text: str  # Распознанный текст


class ScreenAnalyzer:

    def __init__(self, llm):
        self.llm = llm

    # ------------------------------------------------
    # ЗАХВАТ ЭКРАНА (Оптимизировано для слабой нагрузки)
    # ------------------------------------------------
    def capture_screen(self):
        try:
            with mss.mss() as sct:
                # Индекс монитора может быть 1 (первый/основной) или 0 (все мониторы)
                monitor = sct.monitors[1]
                raw = sct.grab(monitor)

                image = Image.frombytes("RGB", raw.size, raw.rgb)

                # ЖЕСТКАЯ ОПТИМИЗАЦИЯ РАЗМЕРА:
                # Снижаем до 800x450. Этого за глаза хватит ИИ, чтобы понять,
                # что открыто (браузер, игра, рабочий стол).
                image.thumbnail((800, 450))

                buffer = BytesIO()
                # Сохраняем в JPEG с качеством 70% для ускорения кодирования и передачи
                image.save(buffer, format="JPEG", quality=70)

                frame = np.array(image)
                img_b64 = base64.b64encode(buffer.getvalue()).decode()

                return img_b64, frame

        except Exception as e:
            print(f"Ошибка захвата экрана: {e}")
            return None, None

    # ------------------------------------------------
    # OCR (Чтение текста чисто через PIL, без тяжелого cv2)
    # ------------------------------------------------
    def read_text(self, frame):
        try:
            if frame is None:
                return ""

            # Превращаем numpy-массив обратно в картинку PIL
            img = Image.fromarray(frame)

            # Upscale (увеличение в 2 раза для лучшего распознавания мелкого шрифта)
            new_width = img.width * 2
            new_height = img.height * 2
            img = img.resize((new_width, new_height), Image.Resampling.BICUBIC)

            # Делаем черно-белой (Grayscale)
            img = img.convert("L")

            text = pytesseract.image_to_string(
                img,
                lang="rus+eng",
                config="--psm 3"
            )

            # Ограничиваем текст до 250 символов, чтобы не грузить контекст ИИ
            return text[:250]
        except Exception as e:
            print(f"Ошибка OCR: {e}")
            return ""

    # ------------------------------------------------
    # АНАЛИЗ ПО КОМАНДЕ (ВСЕГДА ЧЕРЕЗ ИИ)
    # ------------------------------------------------
    def analyze_now(self) -> ScreenAnalysis:
        """
        Вызывай этот метод, когда нужно проанализировать экран.
        """
        img_b64, frame = self.capture_screen()

        if frame is None:
            return ScreenAnalysis(summary="Ошибка: Экран недоступен.", ocr_text="")

        if not self.llm:
            return ScreenAnalysis(summary="Ошибка: LLM не передана в ScreenAnalyzer!", ocr_text="")

        # Читаем текст с экрана
        text = self.read_text(frame)

        # ОПТИМИЗИРОВАННЫЙ ПРОМПТ
        # Заставляем ИИ отвечать очень коротко. Меньше слов = меньше нагрузка на GPU.
        prompt = f"""Опиши скриншот ОДНИМ коротким предложением (максимум 10-15 слов). 
Какое приложение открыто и что происходит?
Текст на экране для подсказки: {text}"""

        try:
            result = self.llm.generate(
                prompt=prompt,
                image=img_b64
            )
            summary = result.text.strip()
        except Exception as e:
            summary = f"Ошибка Vision анализа: {e}"

        return ScreenAnalysis(summary=summary, ocr_text=text)