class CostTracker:

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.message_count = 0

    def add(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.message_count += 1

    def summary(self) -> str:
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return (
            f"\n--- Session Summary ---"
            f"\n Messages:        {self.message_count}"
            f"\n Input tokens:    {self.total_input_tokens}"
            f"\n Output tokens:   {self.total_output_tokens}"
            f"\n Total tokens:    {total_tokens}"
            f"\n(Free providers have no $ cost)"
        )