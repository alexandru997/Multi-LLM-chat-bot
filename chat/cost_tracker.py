from config import PRICING
from providers.base import Usage


class CostTracker:
    """Accumulates real token counts and computes estimated $ cost per session."""

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name
        self.pricing: dict[str, float] = PRICING.get(
            provider_name, {"input": 0.0, "output": 0.0}
        )
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.message_count = 0

    def add(self, usage: Usage) -> None:
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.message_count += 1

    def cost(self) -> float:
        return (
            self.total_input_tokens * self.pricing["input"]
            + self.total_output_tokens * self.pricing["output"]
        )

    def summary(self) -> str:
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return (
            f"--- Session Summary ({self.provider_name}) ---\n"
            f" Messages:        {self.message_count}\n"
            f" Input tokens:    {self.total_input_tokens}\n"
            f" Output tokens:   {self.total_output_tokens}\n"
            f" Total tokens:    {total_tokens}\n"
            f" Estimated cost:  ${self.cost():.6f}"
        )
