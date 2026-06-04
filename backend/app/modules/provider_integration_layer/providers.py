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
    max_rate_limit_retries = 4

    def _rate_limit_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), 30)
            except ValueError:
                pass
        return min(2**attempt, 30)

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        settings = get_settings()
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for Groq provider")
        started = time.perf_counter()
        response: httpx.Response | None = None
        for attempt in range(self.max_rate_limit_retries + 1):
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
            if response.status_code != 429 or attempt == self.max_rate_limit_retries:
                break
            time.sleep(self._rate_limit_delay(response, attempt))
        if response is None:
            raise RuntimeError("Groq provider did not return a response")
        response.raise_for_status()
        payload = response.json()
        text = payload["choices"][0]["message"]["content"]
        return ProviderResponse(text=text, latency_ms=int((time.perf_counter() - started) * 1000), raw=payload)


class HuggingFaceProvider:
    name = "huggingface"
    router_base_url = "https://router.huggingface.co/v1"

    def _response_error_detail(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text[:300]
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                return str(error.get("message") or error)
            if error:
                return str(error)
            return str(payload.get("message") or payload)
        return str(payload)

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
            return False, "HUGGINGFACE_API_KEY is missing from .env or backend/.env"
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
            detail = self._response_error_detail(response)
            if response.status_code == 401:
                return False, f"HuggingFace token is unauthorized for chat completions. Create a token with Inference Providers permission. Router detail: {detail}"
            if response.status_code == 403:
                return False, f"HuggingFace token is forbidden for chat completions. Check token permissions, provider access, or billing access. Router detail: {detail}"
            if response.status_code == 404:
                return False, f"HuggingFace model is unavailable for chat completions: {model_name}. Router detail: {detail}"
            if response.status_code == 400:
                return False, f"HuggingFace rejected the chat-completions request for model {model_name}. Router detail: {detail}"
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
