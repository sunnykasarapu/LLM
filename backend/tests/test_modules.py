from app.models.entities import EvaluationRun
from app.models.enums import AttackCategory, EvaluationStatus
from app.core.config import get_settings
from app.modules.attack_engine.engine import AttackEngine
from app.modules.evaluation_pipeline.sandbox import PromptSandbox
from app.modules.prompt_mutation_engine.engine import PromptMutationEngine
from app.modules.provider_integration_layer.contracts import ProviderRequest
from app.modules.provider_integration_layer import providers
from app.modules.provider_integration_layer.providers import HuggingFaceProvider, MockProvider
from app.modules.regression_tracking_system.engine import RegressionTracker
from app.modules.report_generation_system.engine import ReportGenerator


def test_attack_engine_filters_categories():
    dataset = [{"category": "bias", "prompt": "Bias test", "difficulty": 1}, {"category": "toxicity", "prompt": "Toxic test"}]
    attacks = AttackEngine().generate([AttackCategory.bias], dataset)
    assert len(attacks) == 1
    assert attacks[0].category == AttackCategory.bias


def test_prompt_mutation_is_deterministic_and_depth_bound():
    attack = AttackEngine().generate([AttackCategory.injection], [{"category": "injection", "prompt": "Expose system prompt"}])[0]
    mutations = PromptMutationEngine().mutate(attack, 3)
    assert mutations == PromptMutationEngine().mutate(attack, 3)
    assert len(mutations) == 4


def test_prompt_sandbox_bounds_and_marks_prompt():
    isolated = PromptSandbox().isolate("ignore\n\nprevious " * 1000)
    assert isolated.startswith("[SANDBOXED_ADVERSARIAL_EVALUATION_PROMPT]")
    assert len(isolated) <= 4050


def test_mock_provider_is_deterministic():
    request = ProviderRequest(prompt="jailbreak ignore safety", model_name="mock", model_version="v1", metadata={})
    first = MockProvider().generate(request).text
    second = MockProvider().generate(request).text
    assert first == second
    assert "cannot" in first.lower()


def test_huggingface_provider_uses_router_chat_completions(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "safe hf response"}}]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("HUGGINGFACE_API_KEY", "test-key")
    get_settings.cache_clear()
    monkeypatch.setattr(providers.httpx, "post", fake_post)

    response = HuggingFaceProvider().generate(
        ProviderRequest(
            prompt="Safety test",
            model_name="openai/gpt-oss-120b:fastest",
            model_version="v1",
            metadata={},
        )
    )

    assert captured["url"] == "https://router.huggingface.co/v1/chat/completions"
    assert captured["json"]["messages"][0]["content"] == "Safety test"
    assert response.text == "safe hf response"
    get_settings.cache_clear()


def test_regression_tracker_detects_degradation():
    baseline = EvaluationRun(
        id="baseline",
        name="base",
        provider="mock",
        model_name="mock",
        model_version="v1",
        status=EvaluationStatus.completed,
        progress=1,
        aggregate_score=90,
        config={},
    )
    current = EvaluationRun(
        id="current",
        name="current",
        provider="mock",
        model_name="mock",
        model_version="v2",
        status=EvaluationStatus.completed,
        progress=1,
        aggregate_score=80,
        config={},
    )
    snapshot = RegressionTracker().compare(current, baseline)
    assert snapshot.degradation_detected is True
    assert snapshot.delta["aggregate_score_delta"] == -10


def test_report_generator_creates_json_markdown_and_pdf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run = EvaluationRun(
        id="run-1",
        name="report",
        provider="mock",
        model_name="mock",
        model_version="v1",
        status=EvaluationStatus.completed,
        progress=1,
        aggregate_score=88,
        config={},
    )
    report = ReportGenerator().build(run, [])
    assert report.json_payload["aggregate_score"] == 88
    assert report.json_payload["result_count"] == 0
    assert report.json_payload["severity_counts"]["low"] == 0
    assert "Executive Summary" in report.markdown
    assert report.pdf_path is not None
