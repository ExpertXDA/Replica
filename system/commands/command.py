from dataclasses import dataclass
from typing import Callable


@dataclass
class Command:
    name: str
    description: str
    action: Callable[[str], str]