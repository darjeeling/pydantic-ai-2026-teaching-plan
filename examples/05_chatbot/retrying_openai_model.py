from __future__ import annotations

import httpx
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential


def create_retrying_http_client() -> httpx.AsyncClient:
    def raise_for_retryable_status(response: httpx.Response) -> None:
        if response.status_code in {429, 502, 503, 504}:
            response.raise_for_status()

    transport = AsyncTenacityTransport(
        config=RetryConfig(
            retry=retry_if_exception_type(
                (
                    httpx.HTTPStatusError,
                    httpx.TimeoutException,
                    httpx.ConnectError,
                    httpx.ReadError,
                )
            ),
            wait=wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=1, max=10),
                max_wait=60,
            ),
            stop=stop_after_attempt(3),
            reraise=True,
        ),
        validate_response=raise_for_retryable_status,
    )
    return httpx.AsyncClient(
        transport=transport,
        timeout=httpx.Timeout(30.0),
    )


def build_agent() -> Agent[None, str]:
    client = create_retrying_http_client()
    model = OpenAIChatModel("gpt-5.5", provider=OpenAIProvider(http_client=client))
    return Agent(
        model,
        instructions=(
            "You are a Pydantic AI course assistant. "
            "Answer in Korean and keep the answer under 5 sentences."
        ),
    )


if __name__ == "__main__":
    agent = build_agent()
    result = agent.run_sync("LLM provider retry 정책을 짧게 설명해줘.")
    print(result.output)
