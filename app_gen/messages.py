
from dataclasses import dataclass

@dataclass(frozen=True)
class GenMessages:
    FAILED_DEPENDENCY: str = "Failed to communicate with the OpenAI service." 