# 2회차 실습 TODO

## 시작 파일

- `examples/02_rag/load_docs.py`
- `examples/02_rag/rag_agent.py`

## 과제

1. `examples/02_rag/sample_docs`에 `dbos.md`를 새로 만든다.
2. DBOS durable execution의 핵심을 담은 문장을 3~5개 적는다.
3. `uv run python examples/02_rag/load_docs.py`로 다시 적재한다.
4. `rag_agent.py`에 질문을 던져본다.

```bash
uv run python examples/02_rag/rag_agent.py "DBOS는 retry와 무엇이 다른가요?"
```

## 확장 과제

- `retrieve` tool의 반환값에 `rank`를 포함한다.
- 검색 결과가 없을 때 agent가 추측하지 않도록 instructions를 더 강하게 다듬는다.
- `LIMIT 5`를 환경변수로 바꿀 수 있게 한다.

## Data-Centric RAG 과제

1. `sample_docs`에 기존 문서와 주제가 비슷하면서 오래된 문서를 하나 추가한다.
2. 그 문서에 "이 문서는 2025년 기준이다"처럼 오래된 버전임을 알리는 신호를 넣는다.
3. 다시 적재하고 같은 질문을 실행한다.
4. 오래된 문서가 검색 결과에 섞여 들어오는지 확인한다.
5. 실패 유형을 하나로 분류한다.

```text
retrieval failure
context failure
generation failure
metadata/versioning failure
```

6. 운영 schema에 추가할 metadata를 3개 적는다. 예: `updated_at`, `version`, `tenant_id`.

## GraphRAG 토론 과제

- Vector RAG보다 GraphRAG가 더 잘 맞을 것 같은 질문을 2개 적는다.
- 그 질문에 필요한 entity와 relation을 적는다.
- 이번 수업에서 GraphRAG를 구현하지 않고 개념만 다루는 이유를 설명한다.

## 로컬 Embedding 과제

OpenAI embedding 대신 로컬 embedding provider를 하나 골라 써본다.

### Ollama 선택지

```bash
ollama pull embeddinggemma
curl http://127.0.0.1:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "dimension test"
}' | jq '.embeddings[0] | length'

EMBEDDING_PROVIDER=ollama \
EMBEDDING_MODEL=embeddinggemma \
EMBEDDING_DIMENSIONS= \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

### SentenceTransformers 선택지

```bash
uv add sentence-transformers

EMBEDDING_PROVIDER=sentence-transformers \
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
EMBEDDING_DIMENSIONS= \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

로컬 embedding으로 다시 적재한 뒤 같은 질문을 실행하고, OpenAI embedding 결과와 retrieval 품질을 비교한다.

## 통과 기준

- 새로 추가한 문서 내용이 답변에 반영된다.
- 답변 끝에 source가 붙는다.
- 문서에 없는 질문에는 모른다고 답한다.
- embedding provider를 바꿀 때 dimension 확인과 재색인이 필요한 이유를 설명할 수 있다.
- RAG 실패를 retrieval/context/generation/metadata 문제로 분류할 수 있다.
- GraphRAG가 필요한 상황과, 그래도 기본 Vector RAG를 먼저 쓰는 이유를 설명할 수 있다.
