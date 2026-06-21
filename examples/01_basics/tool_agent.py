import asyncio
import os
from dataclasses import dataclass
from typing import cast

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

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


@dataclass
class CourseDeps:
    lessons: dict[str, str]


class LessonAnswer(BaseModel):
    answer: str = Field(description="Short answer for the learner")
    lesson_ids: list[str] = Field(description="Relevant lesson ids")
    confidence: float = Field(ge=0, le=1)


model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")

agent = Agent(
    model,
    deps_type=CourseDeps,
    output_type=LessonAnswer,
    instructions=(
        "You are a course assistant. Use tools before answering questions about the course. "
        "If the catalog does not contain enough information, say so."
    ),
)


@agent.tool
async def read_lesson(ctx: RunContext[CourseDeps], lesson_id: str) -> str:
    """Read a lesson summary by id, for example '01' or '02'."""
    return ctx.deps.lessons.get(lesson_id, f"Unknown lesson id: {lesson_id}")


@agent.tool_plain
def list_lesson_ids() -> list[str]:
    """List available lesson ids."""
    return ["01", "02", "03", "04", "05"]


async def main() -> None:
    prompt = "RAG를 배우려면 어떤 회차를 보면 되나요?"
    deps = CourseDeps(
        lessons={
            "01": "Pydantic AI basics: Agent, instructions, tools, deps, structured output.",
            "02": "RAG: chunk Markdown docs, embed text, store in pgvector, retrieve with a tool.",
            "03": "Monty and CodeMode: run model-written Python inside a constrained sandbox.",
            "04": "Evals, Graph, and multi-agent workflow.",
            "05": "DBOS durable execution and a FastAPI chatbot.",
        }
    )
    api_logger().info(
        "agent.run start example=tool_agent model=%s prompt_chars=%s",
        model,
        len(prompt),
    )
    result = await agent.run(prompt, deps=deps)
    api_logger().info(
        "agent.run done example=tool_agent model=%s usage=%s",
        model,
        result.usage,
    )
    answer = cast(LessonAnswer, result.output)
    print(answer.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
