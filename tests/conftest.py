import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from providers.base import ChatResult, Usage  # noqa: E402


@pytest.fixture
def usage_small() -> Usage:
    return Usage(input_tokens=100, output_tokens=50)


@pytest.fixture
def usage_zero() -> Usage:
    return Usage(input_tokens=0, output_tokens=0)


@pytest.fixture
def chat_result(usage_small: Usage) -> ChatResult:
    return ChatResult(text="hello", usage=usage_small)
