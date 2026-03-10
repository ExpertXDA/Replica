from __future__ import annotations

import platform
import subprocess


class CommandRouter:
    def __init__(self) -> None:
        self.system = platform.system().lower()

    def execute(self, command_text: str) -> str:
        text = command_text.lower().strip()

        if "открой браузер" in text:
            return self._open_browser()
        if "сделай скрин" in text:
            return "Скриншот можно сделать через модуль vision (capture_screen)."
        if "громкость" in text:
            return "Управление громкостью подключается через OS-адаптер (следующий шаг)."
        if "выключи компьютер" in text:
            return "Команда выключения требует явного подтверждения в UI."

        return "Команда не распознана."

    def _open_browser(self) -> str:
        try:
            if self.system == "linux":
                subprocess.Popen(["xdg-open", "https://www.google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.system == "windows":
                subprocess.Popen(["start", "https://www.google.com"], shell=True)
            elif self.system == "darwin":
                subprocess.Popen(["open", "https://www.google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                return "Неизвестная ОС: браузер не открыт."
            return "Открываю браузер."
        except Exception:
            return "Не удалось открыть браузер."
