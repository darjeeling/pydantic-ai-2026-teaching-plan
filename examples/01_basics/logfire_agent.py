import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

try:
    from examples.course_logging import api_logger, configure_api_call_logging
except ModuleNotFoundError as exc:
    if exc.name != "examples":
        raise
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from examples.course_logging import api_logger, configure_api_call_logging

load_dotenv()


def configure_observability() -> None:
    api_log_file = configure_api_call_logging()
    if api_log_file:
        print(f"api log file: {api_log_file}")

    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()

    if os.getenv("LOGFIRE_CAPTURE_HTTPX") == "1":
        # This captures provider HTTP request/response details. Use carefully.
        logfire.instrument_httpx(capture_all=True)


def main() -> None:
    configure_observability()

    model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")
    prompt = "Logfire를 왜 agent 수업 초반에 붙이나요?"
    agent = Agent(
        model,
        instructions=(
            "You are a Pydantic AI course assistant. "
            "Answer in Korean and mention what a trace can reveal."
        ),
    )

    api_logger().info(
        "agent.run_sync start example=logfire_agent model=%s prompt_chars=%s",
        model,
        len(prompt),
    )
    result = agent.run_sync(prompt)
    api_logger().info(
        "agent.run_sync done example=logfire_agent model=%s usage=%s",
        model,
        result.usage,
    )
    print(result.output)
    print(result.usage)


if __name__ == "__main__":
    main()
