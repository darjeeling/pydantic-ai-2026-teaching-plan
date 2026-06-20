import asyncio
import hashlib
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv
from embeddings import EmbeddingConfig, build_embedder, resolve_dimensions, vector_json

load_dotenv()

THIS_DIR = Path(__file__).parent
DOCS_DIR = THIS_DIR / "sample_docs"


def schema_sql(dimensions: int) -> str:
    if dimensions <= 0 or dimensions > 20000:
        raise ValueError(f"Unexpected embedding dimension: {dimensions}")
    return f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS doc_chunks (
    id text PRIMARY KEY,
    source text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    embedding vector({dimensions}) NOT NULL
);

CREATE INDEX IF NOT EXISTS doc_chunks_embedding_idx
ON doc_chunks
USING hnsw (embedding vector_cosine_ops);
"""


def split_markdown(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    title = path.stem.replace("-", " ").title()
    chunks: list[tuple[str, str]] = []
    current: list[str] = []
    current_title = title

    for line in text.splitlines():
        if line.startswith("# ") and current:
            chunks.append((current_title, "\n".join(current).strip()))
            current = []
            current_title = line.removeprefix("# ").strip()
        else:
            if line.startswith("# "):
                current_title = line.removeprefix("# ").strip()
            current.append(line)

    if current:
        chunks.append((current_title, "\n".join(current).strip()))
    return [(chunk_title, content) for chunk_title, content in chunks if content]


def stable_id(source: str, content: str) -> str:
    digest = hashlib.sha256(f"{source}\n{content}".encode()).hexdigest()
    return digest[:24]


async def main() -> None:
    dsn = os.getenv(
        "POSTGRES_DSN",
        "postgresql://postgres:postgres@localhost:54320/pydantic_ai_course",
    )
    config = EmbeddingConfig.from_env()
    embedder = build_embedder(config)
    dimensions = await resolve_dimensions(embedder, config)

    print(f"embedding provider={config.provider} model={config.model} dimensions={dimensions}")

    conn = await asyncpg.connect(dsn)
    try:
        if os.getenv("RESET_RAG_TABLE") == "1":
            await conn.execute("DROP TABLE IF EXISTS doc_chunks")

        await conn.execute(schema_sql(dimensions))
        for path in sorted(DOCS_DIR.glob("*.md")):
            for title, content in split_markdown(path):
                chunk_id = stable_id(str(path.relative_to(THIS_DIR)), content)
                vector = vector_json(await embedder.embed(content))
                await conn.execute(
                    """
                    INSERT INTO doc_chunks (id, source, title, content, embedding)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id) DO UPDATE
                    SET source = EXCLUDED.source,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding
                    """,
                    chunk_id,
                    str(path.relative_to(THIS_DIR)),
                    title,
                    content,
                    vector,
                )
                print(f"upserted {chunk_id} {path.name} {title}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
