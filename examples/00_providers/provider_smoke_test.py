from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

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

DEFAULT_MODEL = "openai:gpt-5.2"


@dataclass(frozen=True)
class ProviderHint:
    name: str
    prefixes: tuple[str, ...]
    env_vars: tuple[str, ...]
    example_model: str
    note: str


PROVIDER_HINTS = (
    ProviderHint(
        name="OpenAI",
        prefixes=("openai", "openai-chat", "openai-responses"),
        env_vars=("OPENAI_API_KEY",),
        example_model="openai:gpt-5.2",
        note="수업 기본값. v2 prefix 경고가 있으면 openai-chat 또는 openai-responses를 명시합니다.",
    ),
    ProviderHint(
        name="OpenRouter",
        prefixes=("openrouter",),
        env_vars=("OPENROUTER_API_KEY",),
        example_model="openrouter:anthropic/claude-sonnet-4.6",
        note="하나의 OpenRouter 키로 여러 downstream provider를 라우팅합니다.",
    ),
    ProviderHint(
        name="AWS Bedrock",
        prefixes=("bedrock",),
        env_vars=("AWS_BEARER_TOKEN_BEDROCK", "AWS_DEFAULT_REGION"),
        example_model="bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0",
        note="Bedrock 콘솔에서 모델 접근 권한과 region을 먼저 확인해야 합니다.",
    ),
    ProviderHint(
        name="Google AI Studio / Gemini API",
        prefixes=("google",),
        env_vars=("GOOGLE_API_KEY",),
        example_model="google:gemini-3-pro-preview",
        note="AI Studio에서 만든 Gemini API key를 사용합니다.",
    ),
    ProviderHint(
        name="Google Cloud / Vertex AI",
        prefixes=("google-cloud",),
        env_vars=("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "GOOGLE_API_KEY"),
        example_model="google-cloud:gemini-3-pro-preview",
        note="ADC, service account, 또는 Vertex AI Express Mode API key를 사용할 수 있습니다.",
    ),
)


def model_from_env() -> str:
    return os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL


def provider_prefix(model: str) -> str:
    return model.split(":", maxsplit=1)[0].strip().lower()


def hint_for_model(model: str) -> ProviderHint | None:
    prefix = provider_prefix(model)
    return next((hint for hint in PROVIDER_HINTS if prefix in hint.prefixes), None)


def print_hint(model: str) -> None:
    hint = hint_for_model(model)
    print(f"model: {model}")

    if hint is None:
        print("provider: unknown")
        print(
            "hint: Pydantic AI docs에서 provider prefix와 "
            "필요한 optional dependency를 확인하세요."
        )
        return

    print(f"provider: {hint.name}")
    print(f"example: {hint.example_model}")
    print(f"note: {hint.note}")
    for env_var in hint.env_vars:
        value = os.getenv(env_var)
        print(f"{env_var}: {'set' if value else 'missing'}")

    if hint.name == "AWS Bedrock" and not (
        os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        or (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
    ):
        print("AWS credentials: missing bearer token or access-key pair")

    if hint.name == "Google Cloud / Vertex AI" and not os.getenv("GOOGLE_API_KEY"):
        print(
            "Google Cloud auth: GOOGLE_API_KEY is optional when "
            "ADC or service account is configured"
        )


def configure_logfire(capture_httpx: bool) -> None:
    api_log_file = configure_api_call_logging()
    if api_log_file:
        print(f"api log file: {api_log_file}")

    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()

    if capture_httpx or os.getenv("LOGFIRE_CAPTURE_HTTPX") == "1":
        logfire.instrument_httpx(capture_all=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal Pydantic AI provider smoke test.")
    parser.add_argument(
        "--model",
        default=model_from_env(),
        help=(
            "Pydantic AI model string. Defaults to COURSE_MODEL, "
            "OPENAI_MODEL, then openai:gpt-5.2."
        ),
    )
    parser.add_argument(
        "--prompt",
        default="Pydantic AI에서 model provider를 바꿀 때 확인할 것을 세 가지로 답하세요.",
        help="Prompt used for the real provider call.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print provider hints without sending a model request.",
    )
    parser.add_argument(
        "--capture-httpx",
        action="store_true",
        help="Capture HTTPX payloads in Logfire. Do not use with sensitive prompts.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    print_hint(args.model)
    if args.dry_run:
        return

    configure_logfire(args.capture_httpx)
    agent = Agent(
        args.model,
        instructions=(
            "You are a concise backend engineering instructor. "
            "Answer in Korean and mention provider-specific setup risks."
        ),
    )
    api_logger().info(
        "agent.run_sync start example=provider_smoke_test model=%s prompt_chars=%s",
        args.model,
        len(args.prompt),
    )
    result = agent.run_sync(args.prompt)
    api_logger().info(
        "agent.run_sync done example=provider_smoke_test model=%s usage=%s",
        args.model,
        result.usage,
    )
    print("\nresponse:")
    print(result.output)
    print("\nusage:")
    print(result.usage)


if __name__ == "__main__":
    main()
