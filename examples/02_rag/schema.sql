-- Default schema for OpenAI text-embedding-3-small.
-- `load_docs.py` now generates the same schema dynamically from EMBEDDING_DIMENSIONS
-- or by probing the selected embedding provider. Keep this file as a readable SQL
-- reference for class discussion.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS doc_chunks (
    id text PRIMARY KEY,
    source text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    embedding vector(1536) NOT NULL
);

CREATE INDEX IF NOT EXISTS doc_chunks_embedding_idx
ON doc_chunks
USING hnsw (embedding vector_cosine_ops);
