import asyncio
import os
import sys
from dataclasses import dataclass

import asyncpg
from dotenv import load_dotenv
from embeddings import Embedder, build_embedder, vector_json
from pydantic_ai import Agent, RunContext

load_dotenv()


@dataclass
class Deps:
    embedder: Embedder
    pool: asyncpg.Pool


model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")

agent = Agent(
    model,
    deps_type=Deps,
    instructions=(
        "You answer questions about this Pydantic AI course. "
        "Always call retrieve before answering. "
        "Answer in Korean. Use only retrieved context. "
        "If the context is insufficient, say that the course documents "
        "do not contain enough information. "
        "End with a short 'Sources:' list."
    ),
)


@agent.tool
async def retrieve(ctx: RunContext[Deps], query: str) -> str:
    """Retrieve relevant course document chunks for a learner question."""
    vector = vector_json(await ctx.deps.embedder.embed(query))
    rows = await ctx.deps.pool.fetch(
        """
        SELECT source, title, content
        FROM doc_chunks
        ORDER BY embedding <=> $1::vector
        LIMIT 5
        """,
        vector,
    )
    if not rows:
        return "No matching course documents found."
    return "\n\n".join(
        f"Source: {row['source']}\nTitle: {row['title']}\nContent:\n{row['content']}"
        for row in rows
    )


async def main() -> None:
    question = " ".join(sys.argv[1:]) or "Pydantic AI에서 tool은 언제 쓰나요?"
    dsn = os.getenv(
        "POSTGRES_DSN",
        "postgresql://postgres:postgres@localhost:54320/pydantic_ai_course",
    )
    pool = await asyncpg.create_pool(dsn)
    try:
        deps = Deps(embedder=build_embedder(), pool=pool)
        result = await agent.run(question, deps=deps)
        print(result.output)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
