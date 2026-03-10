from __future__ import annotations

import subprocess
import webbrowser
import os
import pyautogui


from system.commands.command import Command
from core.vision.screen_analyzer import ScreenAnalyzer


class CommandRouter:

    def __init__(self, llm) -> None:

        self.screen = ScreenAnalyzer()

        self.commands: dict[str, Command] = {

            "open_browser": Command(
                "open_browser",
                "Открыть браузер",
                self.open_browser
            ),

            "open_url": Command(
                "open_url",
                "Открыть сайт",
                self.open_url
            ),

            "open_app": Command(
                "open_app",
                "Запустить приложение",
                self.open_app
            ),

            "screenshot": Command(
                "screenshot",
                "Сделать скриншот",
                self.screenshot
            ),

            "type_text": Command(
                "type_text",
                "Напечатать текст",
                self.type_text
            ),

            "press_key": Command(
                "press_key",
                "Нажать клавишу",
                self.press_key
            ),

            "volume_up": Command(
                "volume_up",
                "Увеличить громкость",
                self.volume_up
            ),

            "volume_down": Command(
                "volume_down",
                "Уменьшить громкость",
                self.volume_down
            ),

            "analyze_screen": Command(
                "analyze_screen",
                "Проанализировать экран",
                self.analyze_screen
            ),
        }

    def execute(self, intent: str, argument: str = "") -> str:

        command = self.commands.get(intent)

        if not command:
            return "Не знаю такой команды."

        try:
            return command.action(argument)
        except Exception as e:
            return f"Ошибка выполнения: {e}"

    # -----------------------------
    # Команды
    # -----------------------------

    def open_browser(self, arg: str) -> str:
        webbrowser.open("https://google.com")
        return "Открываю браузер."

    def open_url(self, url: str) -> str:

        if not url:
            return "Не указан сайт."

        webbrowser.open(url)
        return f"Открываю {url}"

    def open_app(self, app: str) -> str:

        if not app:
            return "Не указано приложение."

        subprocess.Popen(app, shell=True)
        return f"Запускаю {app}"

    def screenshot(self, arg: str) -> str:

        image = pyautogui.screenshot()

        path = os.path.join(os.getcwd(), "screenshot.png")

        image.save(path)

        return f"Скриншот сохранён: {path}"

    def type_text(self, text: str) -> str:

        if not text:
            return "Нет текста для ввода."

        pyautogui.write(text, interval=0.03)

        return "Текст введён."

    def press_key(self, key: str) -> str:

        if not key:
            return "Не указана клавиша."

        pyautogui.press(key)

        return f"Нажимаю {key}"

    def volume_up(self, arg: str) -> str:

        for _ in range(5):
            pyautogui.press("volumeup")

        return "Громкость увеличена."

    def volume_down(self, arg: str) -> str:

        for _ in range(5):
            pyautogui.press("volumedown")

        return "Громкость уменьшена."

    def analyze_screen(self, arg: str) -> str:

        result = self.screen.analyze()

        return f"Анализ экрана: {result.summary}"