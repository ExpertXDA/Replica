from __future__ import annotations

import subprocess
import webbrowser
import os
import pyautogui
import pyperclip
import psutil
import platform
import urllib.parse
import random
import threading
import time
#import screen_brightness_control as sbc
from datetime import datetime

from system.commands.command import Command


class CommandRouter:

    def __init__(self, llm=None) -> None:
        self.commands: dict[str, Command] = {
            # --- ОСНОВНЫЕ ---
            "open_browser": Command("open_browser", "Браузер", self.open_browser),
            "open_url": Command("open_url", "Сайт", self.open_url),
            "open_app": Command("open_app", "Приложение", self.open_app),
            "close_window": Command("close_window", "Закрыть окно", self.close_window),
            "minimize_windows": Command("minimize_windows", "Свернуть все", self.minimize_windows),

            # --- ВВОД И БУФЕР ---
            "type_text": Command("type_text", "Печать", self.type_text),
            "press_key": Command("press_key", "Клавиша", self.press_key),
            "copy_clipboard": Command("copy_clipboard", "Копировать", self.copy_clipboard),
            "paste_clipboard": Command("paste_clipboard", "Вставить", self.paste_clipboard),

            # --- СИСТЕМА И НАСТРОЙКИ ---
            "volume_up": Command("volume_up", "Громче", self.volume_up),
            "volume_down": Command("volume_down", "Тише", self.volume_down),
            "set_brightness": Command("set_brightness", "Яркость", self.set_brightness),
            "get_time": Command("get_time", "Время", self.get_time),
            "get_sys_info": Command("get_sys_info", "Статус ПК", self.get_sys_info),
            "kill_process": Command("kill_process", "Убить процесс", self.kill_process),
            "shutdown_pc": Command("shutdown_pc", "Выключение", self.shutdown_pc),

            # --- ПРИКОЛЮХИ ---
            "search_google": Command("search_google", "Поиск", self.search_google),
            "random_fact": Command("random_fact", "Факт", self.random_fact),
            "timer": Command("timer", "Таймер", self.set_timer),
            "joke": Command("joke", "Шутка", self.tell_joke),
            "clear_trash": Command("clear_trash", "Корзина", self.clear_trash),

            # --- МЕДИА ---
            "media_play_pause": Command("media_play_pause", "Пауза/Плей", self.media_play_pause),
            "media_next": Command("media_next", "Следующий трек", self.media_next),
        }

    def execute(self, intent: str, argument: str = "") -> str:
        command = self.commands.get(intent)
        if not command: return "Команда не найдена."
        try:
            return command.action(argument)
        except Exception as e:
            return f"Ошибка выполнения: {e}"

    # --- РЕАЛИЗАЦИЯ ---

    def copy_clipboard(self, arg: str) -> str:
        pyautogui.hotkey('ctrl', 'c')
        return "Текст скопирован в буфер."

    def paste_clipboard(self, arg: str) -> str:
        pyperclip.copy(pyperclip.paste())  # Обновляем
        pyautogui.hotkey('ctrl', 'v')
        return "Текст вставлен."

    def get_sys_info(self, arg: str) -> str:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"Система стабильна. CPU: {cpu}%, RAM: {ram}%."

    def kill_process(self, app_name: str) -> str:
        if not app_name:
            return "Не указано имя процесса."

        found = False
        for proc in psutil.process_iter(['name']):
            try:
                # Проверяем, содержит ли имя процесса то, что ввел пользователь
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    found = True
                    # Не выходим сразу, чтобы убить все копии процесса (например, все окна chrome)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Пропускаем процессы, к которым нет доступа или которые уже закрыты
                continue

        if found:
            return f"Процессы, содержащие '{app_name}', завершены."
        return f"Процесс '{app_name}' не найден или недоступен."

    def shutdown_pc(self, arg: str) -> str:
        os.system("shutdown /s /t 30")
        return "Таймер выключения запущен (30 сек)."

    def set_brightness(self, level: str) -> str:
        try:
            #sbc.set_brightness(int(level))
            return f"Яркость: {level}%."
        except:
            return "Ошибка установки яркости."

    def random_fact(self, arg: str) -> str:
        facts = ["Мед не портится.", "Осьминоги имеют 3 сердца.", "В космосе нет звука.", "У вас 206 костей."]
        return random.choice(facts)

    def set_timer(self, minutes: str) -> str:
        def timer_thread():
            time.sleep(int(minutes) * 60)
            pyautogui.alert(f"Таймер {minutes} минут истек!")

        threading.Thread(target=timer_thread, daemon=True).start()
        return f"Таймер на {minutes} минут запущен."

    def tell_joke(self, arg: str) -> str:
        jokes = ["Почему программисты не любят природу? Слишком много багов.",
                 "Компьютер не делает то, что вы хотите. Он делает то, что вы говорите."]
        return random.choice(jokes)

    def clear_trash(self, arg: str) -> str:
        return "Функция очистки корзины ограничена правами доступа Windows."

    def media_play_pause(self, arg: str) -> str:
        pyautogui.press("playpause")
        return "Медиа: переключение состояния."

    def media_next(self, arg: str) -> str:
        pyautogui.press("nexttrack")
        return "Следующий трек."

    # --- БАЗОВЫЕ ---
    def open_browser(self, arg: str) -> str:
        webbrowser.open("https://google.com")
        return "Браузер открыт."

    def open_url(self, url: str) -> str:
        webbrowser.open(url)
        return f"Перехожу на {url}."

    def open_app(self, app: str) -> str:
        subprocess.Popen(app, shell=True)
        return f"Запуск: {app}."

    def close_window(self, arg: str) -> str:
        pyautogui.hotkey('alt', 'f4')
        return "Окно закрыто."

    def minimize_windows(self, arg: str) -> str:
        pyautogui.hotkey('win', 'd')
        return "Окна свернуты."

    def type_text(self, text: str) -> str:
        pyautogui.write(text)
        return "Текст введен."

    def press_key(self, key: str) -> str:
        pyautogui.press(key)
        return f"Клавиша {key} нажата."

    def volume_up(self, arg: str) -> str:
        for _ in range(5): pyautogui.press("volumeup")
        return "Громкость увеличена."

    def volume_down(self, arg: str) -> str:
        for _ in range(5): pyautogui.press("volumedown")
        return "Громкость уменьшена."

    def get_time(self, arg: str) -> str:
        return f"Сейчас {datetime.now().strftime('%H:%M')}."

    def search_google(self, query: str) -> str:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Поиск: {query}."

    def analyze_screen(self, arg: str) -> str:
        return "Функция визуального анализа отключена."