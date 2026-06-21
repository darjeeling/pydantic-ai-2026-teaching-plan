import asyncio
import os

from dbos import DBOS, DBOSConfig
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.durable_exec.dbos import DBOSAgent

load_dotenv()

dbos_config: DBOSConfig = {
    "name": "pydantic_ai_course",
    "system_database_url": "sqlite:///examples/05_chatbot/dbos.sqlite",
}
DBOS(config=dbos_config)

model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")

agent = Agent(
    model,
    name="course_qa_durable",
    instructions=(
        "You are a Pydantic AI course assistant. "
        "Answer in Korean and keep the answer under 5 sentences."
    ),
)

dbos_agent = DBOSAgent(agent)


async def main() -> None:
    DBOS.launch()
    result = await dbos_agent.run("DBOS durable execution을 초보자에게 설명해줘.")
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
