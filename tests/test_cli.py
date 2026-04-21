from pytest_mock import MockerFixture

from utils.cli import parse_args


class TestParseArgs:
    def test_defaults_to_groq_no_system_prompt(self, mocker: MockerFixture) -> None:
        mocker.patch("sys.argv", ["main.py"])
        args = parse_args()
        assert args.provider == "groq"
        assert args.system_prompt == ""

    def test_provider_flag_accepted(self, mocker: MockerFixture) -> None:
        mocker.patch("sys.argv", ["main.py", "--provider", "ollama"])
        args = parse_args()
        assert args.provider == "ollama"

    def test_system_prompt_is_captured(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "sys.argv",
            ["main.py", "--provider", "gemini", "--system-prompt", "be concise"],
        )
        args = parse_args()
        assert args.provider == "gemini"
        assert args.system_prompt == "be concise"
