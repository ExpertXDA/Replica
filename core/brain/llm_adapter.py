from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMReply:
    text: str
    provider: str


class LLMAdapter:
    """Local-first LLM adapter.

    - Preferred: Ollama local server
    - Fallback: rule-based response
    """

    def __init__(self, model_name: str = "llama3.1") -> None:
        self.model_name = model_name

    def generate(self, prompt: str) -> LLMReply:
        try:
            import requests

            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False},
                timeout=12,
            )
            response.raise_for_status()
            data = response.json()
            return LLMReply(text=data.get("response", ""), provider="ollama")
        except Exception:
            return LLMReply(text="Сейчас отвечу кратко и по делу.", provider="fallback")
