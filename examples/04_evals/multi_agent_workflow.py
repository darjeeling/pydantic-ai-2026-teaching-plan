import asyncio
import os
from typing import cast

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits

load_dotenv()

model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.2")

researcher = Agent(
    model,
    output_type=list[str],
    instructions=(
        "You are a researcher. Return 3 concise bullet facts as a Python list of strings. "
        "Focus on Pydantic AI course design."
    ),
)

writer = Agent(
    model,
    instructions=(
        "You are the orchestrator. Use gather_course_facts before writing. "
        "Write the final answer in Korean."
    ),
)


@writer.tool
async def gather_course_facts(ctx: RunContext[None], topic: str) -> list[str]:
    """Ask the researcher agent for concise facts about a course topic."""
    result = await researcher.run(
        f"Research this topic for a beginner workshop: {topic}",
        usage=ctx.usage,
    )
    return cast(list[str], result.output)


async def main() -> None:
    result = await writer.run(
        "RAG 회차를 왜 두 번째에 배치했는지 설명해줘.",
        usage_limits=UsageLimits(request_limit=6, total_tokens_limit=2000),
    )
    print(result.output)
    print(result.usage)


if __name__ == "__main__":
    asyncio.run(main())
