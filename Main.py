import time
import base64
import threading
from io import BytesIO
import os

import mss
import numpy as np
from PIL import Image

import speech_recognition as sr
import pyttsx3

from openai import OpenAI

# =========================
# API
# =========================

API_KEY = "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"
client = OpenAI(api_key=API_KEY)

# =========================
# Голос
# =========================

engine = pyttsx3.init()
engine.setProperty("rate", 180)

def speak(text):
    print("AI:", text)
    engine.say(text)
    engine.runAndWait()

# =========================
# PROMPT
# =========================

SYSTEM_PROMPT = """
Ты голосовой ассистент пользователя за компьютером.

Стиль:
- русский
- неформально
- кратко
- допускается лёгкий сарказм
- иногда можешь слегка подколоть пользователя

Поведение:
1. Отвечай на вопросы пользователя.
2. Не болтай без причины.
3. Иногда комментируй экран если:
   - появилась ошибка
   - пользователь застрял
   - что-то необычное

Комментарии:
- максимум 1–2 предложения
- не повторяй очевидное
"""

history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# =========================
# AI
# =========================

def ask_ai(text=None, image=None):

    content = []

    if text:
        content.append({
            "type": "input_text",
            "text": text
        })

    if image:
        content.append({
            "type": "input_image",
            "image_base64": image
        })

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": content
        }]
    )

    try:
        return response.output[0].content[0].text
    except:
        return "Не смог разобрать ответ модели."

# =========================
# SCREEN
# =========================

def capture_screen():

    with mss.mss() as sct:

        monitor = sct.monitors[1]

        img = sct.grab(monitor)

        image = Image.frombytes("RGB", img.size, img.rgb)

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        return img_b64, np.array(image)

# =========================
# SCREEN LOOP
# =========================

last_frame = None
last_comment_time = 0

def screen_loop():

    global last_frame, last_comment_time

    while True:

        try:

            img_b64, frame = capture_screen()

            if last_frame is None:
                last_frame = frame
                time.sleep(10)
                continue

            diff = np.mean(np.abs(frame - last_frame))

            last_frame = frame

            # экран сильно изменился
            if diff > 20 and time.time() - last_comment_time > 30:

                comment = ask_ai(
                    text="Коротко прокомментируй происходящее на экране",
                    image=img_b64
                )

                speak(comment)

                last_comment_time = time.time()

            time.sleep(8)

        except Exception as e:
            print("Ошибка screen_loop:", e)
            time.sleep(5)

# =========================
# VOICE LOOP
# =========================

recognizer = sr.Recognizer()
mic = sr.Microphone()

def voice_loop():

    while True:

        try:

            with mic as source:

                print("Слушаю...")

                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                audio = recognizer.listen(source, phrase_time_limit=6)

            text = recognizer.recognize_google(audio, language="ru-RU")

            print("Ты:", text)

            answer = ask_ai(text=text)

            speak(answer)

        except sr.UnknownValueError:
            pass

        except Exception as e:
            print("Ошибка voice_loop:", e)

# =========================
# START
# =========================

print("Ассистент запущен")

threading.Thread(target=screen_loop, daemon=True).start()

voice_loop()