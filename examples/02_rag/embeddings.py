import os
from dataclasses import dataclass
from typing import Protocol

import httpx
from openai import AsyncOpenAI
from pydantic_core import to_json


class Embedder(Protocol):
    async def embed(self, text: str) -> list[float]: ...


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str
    model: str
    dimensions: int | None
    ollama_base_url: str
    sentence_transformers_device: str | None

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        provider = os.getenv("EMBEDDING_PROVIDER", "openai").strip().lower()
        model = os.getenv("EMBEDDING_MODEL")
        dimensions = os.getenv("EMBEDDING_DIMENSIONS")

        if model is None:
            if provider == "openai":
                model = "text-embedding-3-small"
            elif provider == "ollama":
                model = "embeddinggemma"
            else:
                model = "sentence-transformers/all-MiniLM-L6-v2"

        return cls(
            provider=provider,
            model=model,
            dimensions=int(dimensions) if dimensions else None,
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            sentence_transformers_device=os.getenv("SENTENCE_TRANSFORMERS_DEVICE") or None,
        )


@dataclass
class OpenAIEmbedder:
    model: str
    client: AsyncOpenAI

    async def embed(self, text: str) -> list[float]:
        result = await self.client.embeddings.create(input=text, model=self.model)
        return result.data[0].embedding


@dataclass
class OllamaEmbedder:
    model: str
    base_url: str

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.post("/api/embed", json={"model": self.model, "input": text})
            response.raise_for_status()
            data = response.json()
        return data["embeddings"][0]


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str, device: str | None = None):
        try:
            from sentence_transformers import SentenceTransformer  # ty: ignore[unresolved-import]
        except ImportError as exc:
            raise RuntimeError(
                "Install sentence-transformers to use EMBEDDING_PROVIDER=sentence-transformers: "
                "uv add sentence-transformers"
            ) from exc

        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)

    async def embed(self, text: str) -> list[float]:
        import asyncio

        vector = await asyncio.to_thread(
            self.model.encode,
            [text],
            normalize_embeddings=True,
        )
        return vector[0].tolist()


def build_embedder(config: EmbeddingConfig | None = None) -> Embedder:
    config = config or EmbeddingConfig.from_env()

    if config.provider == "openai":
        return OpenAIEmbedder(model=config.model, client=AsyncOpenAI())
    if config.provider == "ollama":
        return OllamaEmbedder(model=config.model, base_url=config.ollama_base_url)
    if config.provider in {"sentence-transformers", "sentence_transformers", "local"}:
        return SentenceTransformersEmbedder(
            model_name=config.model,
            device=config.sentence_transformers_device,
        )

    raise ValueError(
        "Unknown EMBEDDING_PROVIDER. Use one of: openai, ollama, sentence-transformers."
    )


async def resolve_dimensions(embedder: Embedder, config: EmbeddingConfig) -> int:
    if config.dimensions is not None:
        return config.dimensions
    if config.provider == "openai" and config.model == "text-embedding-3-small":
        return 1536

    probe = await embedder.embed("dimension probe")
    return len(probe)


def vector_json(vector: list[float]) -> str:
    return to_json(vector).decode()
