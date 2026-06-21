import os
from typing import TypedDict

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

load_dotenv()


class Lesson(TypedDict):
    title: str
    minutes: int


LESSONS: dict[str, Lesson] = {
    "01": {"title": "Pydantic AI basics", "minutes": 150},
    "02": {"title": "RAG with pgvector", "minutes": 150},
    "03": {"title": "Monty and CodeMode", "minutes": 150},
    "04": {"title": "Evals, Graph, Multi-agent", "minutes": 150},
    "05": {"title": "DBOS and FastAPI chatbot", "minutes": 150},
}

model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")

agent = Agent(
    model,
    capabilities=[CodeMode()],
    instructions=(
        "You are a course planning assistant. "
        "When arithmetic, filtering, or combining many tool results is needed, use run_code. "
        "Answer in Korean."
    ),
)


@agent.tool_plain
def list_lessons() -> list[dict[str, str]]:
    """List lesson ids and titles."""
    return [{"id": lesson_id, "title": lesson["title"]} for lesson_id, lesson in LESSONS.items()]


@agent.tool_plain
def get_lesson_minutes(lesson_id: str) -> int:
    """Return planned minutes for a lesson id."""
    return int(LESSONS[lesson_id]["minutes"])


@agent.tool_plain
def get_lesson_title(lesson_id: str) -> str:
    """Return the title for a lesson id."""
    return str(LESSONS[lesson_id]["title"])


def main() -> None:
    result = agent.run_sync(
        "전체 과정 시간을 계산하고, 3시간을 넘는 회차가 있는지 확인해줘. "
        "계산 과정은 간단히 설명해줘."
    )
    print(result.output)


if __name__ == "__main__":
    main()
