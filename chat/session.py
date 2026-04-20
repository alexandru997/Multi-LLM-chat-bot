from providers.base import LLMProvider
from chat.cost_tracker import CostTracker

class ChatSession:

    def __init__(self, provider: LLMProvider, cost_tracker: CostTracker, system_prompt: str = ""):
        self.provider = provider
        self.cost_tracker = cost_tracker
        self.system_prompt = system_prompt
        self.messages = []

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

        response = self.provider.stream_chat(self.messages, self.system_prompt)

        self.messages.append({"role": "assistant", "content": response})

        input_tokens = self._estimate_tokens(user_input)
        output_tokens = self._estimate_tokens(response)
        self.cost_tracker.add(input_tokens, output_tokens)

    def clear(self):
        self.messages = []
        print("[Conversation cleared]")

    def run(self):
        print(f"\nProvider: {self.provider.name} | Model: {self.provider.model}")
        print("Commands: /quit, /clear, /cost")
        print("-" * 40)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue
                elif user_input == "/quit":
                    print(self.cost_tracker.summary())
                    break
                elif user_input == "/clear":
                    self.clear()
                elif user_input == "/cost":
                    print(self.cost_tracker.summary())
                else:
                    print("\nAssistant: ", end="")
                    self.chat(user_input)

            except KeyboardInterrupt:
                print(self.cost_tracker.summary())
                break