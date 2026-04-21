import logging

from chat.cost_tracker import CostTracker
from chat.session import ChatSession
from providers import ProviderError, get_provider
from utils import parse_args, setup_logging

logger = logging.getLogger(__name__)


def main() -> int:
    setup_logging()
    args = parse_args()

    try:
        provider = get_provider(args.provider)
    except ProviderError as e:
        logger.error("Provider initialization failed: %s", e)
        return 1

    cost_tracker = CostTracker(provider_name=provider.name)
    session = ChatSession(
        provider=provider,
        cost_tracker=cost_tracker,
        system_prompt=args.system_prompt,
    )
    session.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
