import time

import httpx

from app.core.config import get_settings
from app.modules.provider_integration_layer.contracts import LLMProvider, ProviderRequest, ProviderResponse


class MockProvider:
    name = "mock"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        started = time.perf_counter()
        lower = request.prompt.lower()
        if "ignore" in lower or "jailbreak" in lower:
            text = "I cannot bypass safety rules, but I can help evaluate the request safely."
        elif "false" in lower or "hallucination" in lower:
            text = "I do not have enough evidence to assert that claim. Verification is required."
        elif "toxic" in lower or "insult" in lower:
            text = "I will not generate abusive content. I can provide a neutral rewrite."
        elif "bias" in lower:
            text = "I cannot make a demographic generalization. Use evidence-based evaluation criteria."
        else:
            text = "Safe mock response for deterministic evaluation."
        return ProviderResponse(text=text, latency_ms=int((time.perf_counter() - started) * 1000) + 5, raw={"provider": self.name})


class GroqProvider:
    name = "groq"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        settings = get_settings()
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for Groq provider")
        started = time.perf_counter()
        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={
                "model": request.model_name,
                "messages": [{"role": "user", "content": request.prompt}],
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        return ProviderResponse(text=text, latency_ms=int((time.perf_counter() - started) * 1000), raw=payload)


class HuggingFaceProvider:
    name = "huggingface"
    router_base_url = "https://router.huggingface.co/v1"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        settings = get_settings()
        if not settings.huggingface_api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY is required for HuggingFace provider")
        started = time.perf_counter()
        response = httpx.post(
            f"{self.router_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
            json={
                "model": request.model_name,
                "messages": [{"role": "user", "content": request.prompt}],
                "temperature": 0,
                "stream": False,
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        return ProviderResponse(text=text, latency_ms=int((time.perf_counter() - started) * 1000), raw={"payload": payload})

    def validate(self, model_name: str = "openai/gpt-oss-120b:fastest") -> tuple[bool, str]:
        settings = get_settings()
        if not settings.huggingface_api_key:
            return False, "HUGGINGFACE_API_KEY is missing from backend .env"
        if not settings.huggingface_api_key.startswith("hf_"):
            return False, "HuggingFace token should start with hf_"
        try:
            response = httpx.post(
                f"{self.router_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.huggingface_api_key}"},
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "preflight"}],
                    "max_tokens": 1,
                    "stream": False,
                },
                timeout=10,
            )
            if response.status_code == 401:
                return False, "HuggingFace token is unauthorized for chat completions. Create a token with Inference Providers permission."
            if response.status_code == 403:
                return False, "HuggingFace token is forbidden for chat completions. Check token permissions, provider access, or billing access."
            if response.status_code == 404:
                return False, f"HuggingFace model is unavailable for chat completions: {model_name}"
            response.raise_for_status()
        except httpx.ConnectError:
            return False, "HuggingFace router is not reachable from the worker/network environment."
        except httpx.HTTPError as exc:
            return False, f"HuggingFace provider validation failed: {exc}"
        return True, "HuggingFace Inference Providers access verified"


class ProviderFactory:
    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {
            "mock": MockProvider(),
            "groq": GroqProvider(),
            "huggingface": HuggingFaceProvider(),
        }

    def get(self, provider_name: str) -> LLMProvider:
        try:
            return self._providers[provider_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported provider: {provider_name}") from exc
