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
configure_api_call_logging()
logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()


def main() -> None:
    model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")
    prompt = "Pydantic AI를 처음 배우는 사람에게 한 문단으로 설명해줘."
    agent = Agent(
        model,
        instructions=(
            "You are a teaching assistant for a beginner Pydantic AI workshop. "
            "Answer in Korean, briefly, and include one concrete example."
        ),
    )

    api_logger().info(
        "agent.run_sync start example=hello_agent model=%s prompt_chars=%s",
        model,
        len(prompt),
    )
    result = agent.run_sync(prompt)
    api_logger().info(
        "agent.run_sync done example=hello_agent model=%s usage=%s",
        model,
        result.usage,
    )
    print(result.output)


if __name__ == "__main__":
    main()
