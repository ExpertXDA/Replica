from __future__ import annotations

from dataclasses import dataclass
import subprocess
import time


@dataclass
class LLMReply:
    text: str
    provider: str


class LLMAdapter:
    def __init__(self, model_name: str = "llama3.2") -> None:
        self.model_name = model_name
        self._serve_process = None

    # ------------------------------------------------
    # MODEL START
    # ------------------------------------------------

    def ensure_model_ready(self) -> tuple[bool, str]:
        try:
            import requests

            if self._is_ollama_up(requests):
                print("✅ Ollama уже работает")
                self._pull_if_missing(requests)
                return True, "ollama"

            print("⚠ Ollama API не найден. Пытаюсь запустить сервер...")

            try:
                self._serve_process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                print("❌ ollama.exe не найден.")

            for _ in range(30):
                if self._is_ollama_up(requests):
                    print("✅ Ollama сервер доступен")
                    self._pull_if_missing(requests)
                    return True, "ollama"

                time.sleep(1)

            print("❌ Не удалось подключиться к Ollama")
            return False, "ollama_not_available"

        except Exception as e:
            print("Ошибка запуска:", e)
            return False, "fallback"

    def _is_ollama_up(self, requests_module):
        try:
            r = requests_module.get(
                "http://127.0.0.1:11434/api/tags",
                timeout=3
            )
            return r.ok
        except:
            return False

    def _pull_if_missing(self, requests_module):

        r = requests_module.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=10
        )

        r.raise_for_status()

        models = r.json().get("models", [])
        names = {m.get("name", "") for m in models}

        if not any(name.startswith(self.model_name) for name in names):

            print(f"⬇ Скачиваю модель {self.model_name}")

            requests_module.post(
                "http://127.0.0.1:11434/api/pull",
                json={
                    "name": self.model_name,
                    "stream": False
                },
                timeout=600
            ).raise_for_status()

            print("✅ Модель скачана")

        else:
            print("✅ Модель уже есть")

    # ------------------------------------------------
    # TEXT GENERATION
    # ------------------------------------------------

    def generate(self, prompt: str, image: str | None = None) -> LLMReply:

        try:
            import requests

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }

            # если есть изображение — добавляем vision
            if image is not None:
                payload["images"] = [image]

            r = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json=payload,
                timeout=180
            )

            r.raise_for_status()
            data = r.json()

            return LLMReply(
                text=data.get("response", "").strip(),
                provider="ollama"
            )

        except Exception as e:

            print("Ошибка генерации:", e)

            return LLMReply(
                text="Я рядом. Опиши задачу.",
                provider="fallback"
            )

