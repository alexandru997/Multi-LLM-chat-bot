import logging

from chat.cost_tracker import CostTracker
from providers.base import LLMProvider, ProviderError

logger = logging.getLogger(__name__)

Message = dict[str, str]


class ChatSession:
    def __init__(
        self,
        provider: LLMProvider,
        cost_tracker: CostTracker,
        system_prompt: str = "",
    ) -> None:
        self.provider = provider
        self.cost_tracker = cost_tracker
        self.system_prompt = system_prompt
        self.messages: list[Message] = []

    def chat(self, user_input: str) -> None:
        self.messages.append({"role": "user", "content": user_input})
        try:
            result = self.provider.stream_chat(self.messages, self.system_prompt)
        except ProviderError as e:
            logger.error("Chat turn failed: %s", e)
            self.messages.pop()
            return

        self.messages.append({"role": "assistant", "content": result.text})
        self.cost_tracker.add(result.usage)

    def clear(self) -> None:
        self.messages = []
        print("[Conversation cleared]")

    def run(self) -> None:
        print(f"\nProvider: {self.provider.name} | Model: {self.provider.model}")
        print("Commands: /quit, /clear, /cost")
        print("-" * 40)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue
                if user_input == "/quit":
                    print("\n" + self.cost_tracker.summary())
                    break
                if user_input == "/clear":
                    self.clear()
                elif user_input == "/cost":
                    print("\n" + self.cost_tracker.summary())
                else:
                    print("\nAssistant: ", end="")
                    self.chat(user_input)

            except KeyboardInterrupt:
                print("\n" + self.cost_tracker.summary())
                break
