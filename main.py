from utils.cli import parse_args
from providers import get_provider
from chat.session import ChatSession
from chat.cost_tracker import CostTracker

def main():
    args = parse_args()

    provider = get_provider(args.provider)
    cost_tracker = CostTracker()
    session = ChatSession(
        provider=provider,
        cost_tracker=cost_tracker,
        system_prompt=args.system_prompt,
    )

    session.run()

if __name__ == "__main__":
    main()