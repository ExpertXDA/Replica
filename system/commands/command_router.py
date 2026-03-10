from __future__ import annotations

import platform
import subprocess


class CommandRouter:
    def __init__(self) -> None:
        self.system = platform.system().lower()

    def execute(self, command_text: str) -> str:
        text = command_text.lower().strip()

        if "открой браузер" in text:
            return self._open_url("https://www.google.com")
        if "запусти discord" in text:
            return self._open_app("discord")
        if "сделай скрин" in text or "скриншот" in text:
            return "Скриншот захватывается модулем анализа экрана автоматически."
        if "громкость" in text:
            return "Громкость меняется в настройках. Нативный системный контроллер можно добавить плагином."
        if "выключи компьютер" in text:
            return "Для выключения нужна отдельная кнопка подтверждения в интерфейсе (безопасность)."

        return "Команда не распознана."

    def _open_url(self, url: str) -> str:
        return self._spawn([url], kind="url")

    def _open_app(self, app_name: str) -> str:
        return self._spawn([app_name], kind="app")

    def _spawn(self, arg: list[str], kind: str) -> str:
        try:
            if self.system == "linux":
                if kind == "url":
                    subprocess.Popen(["xdg-open", arg[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([arg[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.system == "windows":
                if kind == "url":
                    subprocess.Popen(["start", arg[0]], shell=True)
                else:
                    subprocess.Popen(["start", arg[0]], shell=True)
            elif self.system == "darwin":
                if kind == "url":
                    subprocess.Popen(["open", arg[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(["open", "-a", arg[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                return "Неизвестная ОС: команда не выполнена."
            return "Выполняю команду."
        except Exception:
            return "Не удалось выполнить команду."
