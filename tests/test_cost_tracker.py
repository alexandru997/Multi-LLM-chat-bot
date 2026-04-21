from chat.cost_tracker import CostTracker
from providers.base import Usage


class TestCostTracker:
    def test_initial_state_is_zero(self) -> None:
        tracker = CostTracker(provider_name="groq")
        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.message_count == 0
        assert tracker.cost() == 0.0

    def test_unknown_provider_defaults_to_zero_pricing(self) -> None:
        tracker = CostTracker(provider_name="unknown-provider")
        tracker.add(Usage(input_tokens=1000, output_tokens=1000))
        assert tracker.cost() == 0.0

    def test_add_accumulates_tokens_and_messages(self, usage_small: Usage) -> None:
        tracker = CostTracker(provider_name="groq")
        tracker.add(usage_small)
        tracker.add(usage_small)
        assert tracker.total_input_tokens == 200
        assert tracker.total_output_tokens == 100
        assert tracker.message_count == 2

    def test_cost_uses_configured_pricing(self) -> None:
        tracker = CostTracker(provider_name="groq")
        tracker.add(Usage(input_tokens=1_000_000, output_tokens=1_000_000))
        assert tracker.cost() == 0.59 + 0.79

    def test_ollama_cost_is_free(self) -> None:
        tracker = CostTracker(provider_name="ollama")
        tracker.add(Usage(input_tokens=10_000, output_tokens=10_000))
        assert tracker.cost() == 0.0

    def test_summary_contains_expected_lines(self, usage_small: Usage) -> None:
        tracker = CostTracker(provider_name="gemini")
        tracker.add(usage_small)
        summary = tracker.summary()
        assert "gemini" in summary
        assert "Messages:" in summary
        assert "Input tokens:" in summary
        assert "Output tokens:" in summary
        assert "Estimated cost:" in summary
        assert "100" in summary
        assert "50" in summary
