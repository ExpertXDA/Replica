from __future__ import annotations

from dataclasses import dataclass
import subprocess


@dataclass
class LLMReply:
    text: str
    provider: str


class LLMAdapter:
    """Local-first LLM adapter with automatic Ollama bootstrap."""

    def __init__(self, model_name: str = "llama3.1") -> None:
        self.model_name = model_name
        self._serve_process = None

    def ensure_model_ready(self) -> tuple[bool, str]:
        """Ensure local model is reachable; try to start Ollama and pull model automatically."""
        try:
            import requests

            if self._is_ollama_up(requests):
                self._pull_if_missing(requests)
                return True, "ollama"

            self._serve_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            for _ in range(10):
                if self._is_ollama_up(requests):
                    self._pull_if_missing(requests)
                    return True, "ollama"
            return False, "ollama_not_available"
        except Exception:
            return False, "fallback"

    def _is_ollama_up(self, requests_module: object) -> bool:
        try:
            response = requests_module.get("http://127.0.0.1:11434/api/tags", timeout=2)
            return response.ok
        except Exception:
            return False

    def _pull_if_missing(self, requests_module: object) -> None:
        response = requests_module.get("http://127.0.0.1:11434/api/tags", timeout=4)
        response.raise_for_status()
        models = response.json().get("models", [])
        names = {model.get("name", "") for model in models}
        if not any(name.startswith(self.model_name) for name in names):
            requests_module.post(
                "http://127.0.0.1:11434/api/pull",
                json={"name": self.model_name, "stream": False},
                timeout=120,
            ).raise_for_status()

    def generate(self, prompt: str) -> LLMReply:
        try:
            import requests

            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            return LLMReply(text=data.get("response", "").strip(), provider="ollama")
        except Exception:
            return LLMReply(text="Я рядом. Сформулируй задачу, и я помогу по шагам.", provider="fallback")
