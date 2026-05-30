from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderRequest:
    prompt: str
    model_name: str
    model_version: str
    metadata: dict


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    latency_ms: int
    raw: dict


class LLMProvider(Protocol):
    name: str

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        ...

