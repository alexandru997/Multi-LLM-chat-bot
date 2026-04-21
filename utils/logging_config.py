import logging
import os


def setup_logging(level: int | None = None) -> None:
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "WARNING").upper()
        level = getattr(logging, env_level, logging.WARNING)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
