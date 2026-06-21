# 2회차: RAG 만들기

## 2시간 목표

이 회차의 목표는 수강생이 RAG를 "검색을 붙인 챗봇" 정도로 끝내지 않는 것이다. 문서 ingestion, chunking, embedding model 선택, vector search, answer policy, 데이터 품질이 모두 답변 품질에 맞물려 있다는 감각을 갖게 한다.

완성 결과물은 `examples/02_rag`의 pgvector 기반 RAG agent다. 수강생은 샘플 Markdown 문서를 추가하고, embedding을 재생성하고, agent가 검색된 근거만 사용해 답하게 만든다. 마지막에는 같은 RAG라도 문서 품질, metadata, 최신성, 중복 문서가 어떻게 실패를 만드는지 분류한다.

## 도입 이야기

수업을 이렇게 연다.

"1회차에서 agent는 작은 lesson catalog를 tool로 읽었죠. catalog가 5개면 괜찮아요. 그런데 회사 기술 문서가 5천 개라면 어떻게 할까요? 전부 prompt에 넣을 수도 없고, 전부 tool 결과로 돌려줄 수도 없어요. RAG는 이 문제를 '먼저 검색하고, 필요한 문맥만 넣자'로 푸는 패턴입니다."

칠판에 다음 두 방식을 비교한다.

```text
Bad:
all docs -> prompt -> model

Better:
question -> embedding -> vector search -> top chunks -> model
```

전하고 싶은 메시지는 세 가지다.

- RAG는 모델을 학습시키는 게 아니다.
- RAG는 답변 직전에 외부 지식을 검색해서 context로 넣는 것이다.
- 검색 품질이 나쁘면 모델이 아무리 좋아도 답변 품질이 나쁘다.

## 사례로 시작하기: "문서를 넣었는데 왜 답이 틀리나요?"

도입 다음에는 다음 장애 사례로 들어간다.

운영팀이 새 교육 공지를 Markdown으로 추가했다. 그런데 챗봇은 "최신 수업 일정"을 묻는 질문에 여전히 예전 일정을 답한다. 개발자는 "RAG를 붙였으니 문서를 보고 답했겠지"라고 생각하지만, trace를 열어 보면 검색된 chunk는 예전 공지이고 새 문서는 색인조차 되지 않았다. 다른 질문에서는 새 문서가 검색되지만, chunk가 너무 길어서 모델이 핵심 날짜를 놓친다. 또 다른 질문에서는 검색 결과는 맞는데 답변 정책이 약해서 모델이 출처 없는 추론을 섞는다.

이 사례에서 RAG 실패는 하나가 아니다.

| 실패 위치 | 증상 | 확인할 것 |
| --- | --- | --- |
| ingestion | 문서가 아예 검색되지 않는다 | 파일 수집, 중복 제거, 최신성, 삭제 정책 |
| chunking | 검색은 되지만 핵심 문장이 빠진다 | chunk 크기, overlap, 제목/metadata 포함 여부 |
| embedding | 비슷한 질문인데 엉뚱한 문서가 뜬다 | embedding model, dimension, 재색인 여부 |
| retrieval | 맞는 문서가 6등이라 context에 못 들어간다 | top-k, score, metadata filter |
| generation | context는 맞는데 답이 과장된다 | answer policy, source citation, 모르면 모른다고 하기 |

그래서 이 회차의 핵심 질문은 "vector search 코드를 어떻게 짜는가"가 아니다. "답이 틀렸을 때 어느 단계가 틀렸는지 어떻게 좁히는가"다. 수강생은 RAG를 모델 기능이 아니라 데이터 파이프라인과 답변 정책의 결합으로 보게 된다.

강사가 던질 질문:

- "검색 결과 1등이 틀렸나요, 아니면 검색은 맞는데 모델이 잘못 썼나요?"
- "embedding model을 바꾼 뒤 기존 vector를 그대로 쓰면 어떤 일이 생기나요?"
- "문서에 없는 답을 해야 하는 상황에서 좋은 챗봇은 무엇을 말해야 하나요?"

## 수업 전 준비

기본 RAG 실습은 OpenAI API key와 Docker가 필요하다.

```bash
docker compose up -d pgvector
uv run python examples/02_rag/load_docs.py
uv run python examples/02_rag/rag_agent.py "RAG는 언제 쓰나요?"
```

Docker가 어려운 환경이면 강사는 `schema.sql`, `load_docs.py`, `rag_agent.py`를 코드 중심으로 설명하고, SQL 결과는 미리 캡처해서 보여 준다.

OpenAI embedding API를 쓰기 어려운 환경이면 Ollama나 SentenceTransformers 기반 로컬 embedding으로 대체할 수 있다. 이때도 답변 생성 agent는 기본적으로 `COURSE_MODEL`을 쓰므로, "embedding만 로컬"인지 "답변 모델까지 로컬"인지 구분해서 설명한다. 이 수업의 예제는 embedding provider만 바꿔 끼우는 구조다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-10분 | 1회차 복습 | tool 개념을 RAG tool로 연결 | tool과 RAG 차이 말하기 |
| 10-25분 | RAG 문제 정의 | 왜 prompt에 문서 전체를 넣을 수 없는지 이해 | 문서 QA 실패 사례 보기 |
| 25-40분 | Chunking | chunk 단위와 metadata 중요성 이해 | sample docs 읽기 |
| 40-60분 | Embedding model과 pgvector | provider, dimension, vector 저장/검색 흐름 이해 | `schema.sql` 읽기 |
| 60-70분 | 휴식/질문 | DB, embedding 질문 정리 | 질문 |
| 70-90분 | Ingestion 라이브코딩 | `load_docs.py` 흐름 이해 | 문서 추가 후 적재 |
| 90-105분 | RAG agent 라이브코딩 | `retrieve` tool과 answer policy 이해 | 질문 실행 |
| 105-116분 | Data-Centric RAG와 GraphRAG 맛보기 | 데이터 품질, metadata, 관계형 검색 필요성 이해 | 실패 유형 분류 |
| 116-118분 | 품질 리뷰 | 좋은 RAG/나쁜 RAG 구분 | 결과 비교 |
| 118-120분 | 다음 회차 연결 | tool 호출 폭증 문제를 CodeMode로 연결 | 회고 |

## 개념 설명 스크립트

### RAG와 Tool의 관계

Pydantic AI 입장에서 RAG 검색은 tool로 구현할 수 있다. `retrieve(query: str) -> str` tool이 vector DB를 검색하고, agent는 반환된 context를 바탕으로 답한다.

다만 목적이 다르다.

- 일반 tool: 외부 행동 또는 특정 정보 조회. 예: `get_weather`, `read_lesson`, `create_ticket`.
- RAG tool: 질문과 관련된 문서 조각 검색. 예: `retrieve_course_docs`.

이렇게 짚어 준다.

- RAG tool은 보통 side effect가 없어야 한다.
- RAG tool은 가능한 한 source를 함께 반환해야 한다.
- RAG tool은 너무 많은 text를 반환하면 오히려 답변 품질이 떨어진다.

### Chunking

chunk는 검색과 답변의 기본 단위다. chunk가 너무 크면 검색은 맞아도 답변에 불필요한 내용이 섞인다. 반대로 너무 작으면 필요한 맥락이 끊긴다.

강의에서 다룰 기준:

- 제목과 본문을 같이 저장한다.
- source path 또는 URL을 저장한다.
- 한 chunk가 하나의 의미 단위를 담게 한다.
- 코드/표/절차 문서는 문단 기준이 항상 최선은 아니다.

수강생 질문:

- "PDF 한 페이지를 chunk로 하면 될까요?"
- "Markdown heading 기준은 항상 좋을까요?"

답변 방향:

- 문서 종류에 따라 다르다.
- FAQ는 질문/답변 쌍, API 문서는 endpoint 단위, 튜토리얼은 heading 단위가 보통 낫다.

### Embedding

embedding은 text를 숫자 vector로 바꾼 것이다. 의미가 비슷한 text가 vector 공간에서 가까워지도록 학습된 모델을 쓴다.

초보자에게는 이렇게 말한다.

"embedding은 텍스트의 의미 좌표예요. 'tool 사용법'과 'function calling'은 단어가 달라도 의미가 가까울 수 있죠. vector search는 이런 의미적 가까움을 이용합니다."

운영 관점:

- embedding model을 바꾸면 기존 vector와 dimension이 달라질 수 있다.
- 같은 model이라도 chunking이 바뀌면 재색인이 필요하다.
- embedding 비용은 문서 수와 재색인 빈도에 비례한다.

### Data-Centric RAG

RAG 품질은 모델 이름보다 데이터 상태에 더 크게 흔들릴 때가 많다. 좋은 모델을 써도 검색되는 문서가 오래됐거나, 중복됐거나, source가 없거나, chunk가 애매하면 답변은 나빠진다.

강사는 이렇게 말한다.

"RAG는 prompt engineering 문제이기도 하지만 data engineering 문제이기도 해요. 좋은 답변을 만들려면 좋은 검색 대상이 있어야 하고, 좋은 검색 대상은 문서 구조와 metadata에서 시작합니다."

Data-Centric 관점에서 확인할 항목:

| 항목 | 질문 | 실패 예 |
| --- | --- | --- |
| 최신성 | 이 chunk는 최신 문서인가? | 예전 API 사용법을 답함 |
| 중복 | 같은 내용이 여러 버전으로 들어갔는가? | 서로 다른 답변 근거가 동시에 검색됨 |
| 출처 | source/title/version을 추적할 수 있는가? | 답변 근거를 UI나 로그에서 설명할 수 없음 |
| 의미 단위 | chunk 하나가 하나의 의미를 담는가? | 검색은 됐지만 답변에 필요한 문장이 빠짐 |
| 권한 | 사용자가 이 문서를 볼 수 있는가? | 다른 tenant의 문서가 검색됨 |
| 오염 | 문서 안에 prompt injection이 있는가? | "이전 지시를 무시하라" 같은 문장을 모델이 따름 |

RAG 실패는 세 단계로 나눠 본다.

| 실패 위치 | 증상 | 먼저 볼 것 |
| --- | --- | --- |
| Retrieval 실패 | 관련 source가 top-k에 없다 | chunking, embedding model, query rewrite, metadata filter |
| Context 실패 | source는 맞지만 답변에 필요한 문장이 없다 | chunk 크기, overlap, heading 포함 여부 |
| Generation 실패 | context는 있는데 모델이 무시하거나 환각한다 | instructions, answer policy, source citation, eval |

이 분류는 4회차의 RAG eval로 이어진다. 2회차에서는 실패를 눈으로 분류하고, 4회차에서는 그 분류를 dataset과 evaluator로 만든다.

### Embedding model 선택

Embedding model은 답변 생성 모델과 별개다. `gpt-5.2` 같은 chat model이 답변을 만들더라도, 문서와 질문을 vector로 바꾸는 embedding model은 OpenAI API일 수도 있고 로컬 모델일 수도 있다.

수업에서는 세 가지 선택지를 보여 준다.

| 선택지 | 예 | 장점 | 주의 |
| --- | --- | --- | --- |
| OpenAI API | `text-embedding-3-small` | 설정이 단순하고 품질이 안정적 | API key, 비용, 외부 전송 |
| Ollama 로컬 | `embeddinggemma`, `qwen3-embedding`, `all-minilm` | 로컬 실행, 네트워크 의존 낮음 | 모델 pull, 로컬 리소스, dimension 확인 |
| SentenceTransformers 로컬 | `sentence-transformers/all-MiniLM-L6-v2` | Python 안에서 직접 실행, 실험 쉬움 | 패키지/모델 다운로드, CPU/GPU 성능 |

여기서 꼭 짚을 점:

- embedding model을 바꾸면 기존 vector와 query vector가 같은 공간에 있지 않다.
- 같은 테이블에 서로 다른 dimension/model의 vector를 섞으면 안 된다.
- model을 바꾸면 보통 `RESET_RAG_TABLE=1`로 테이블을 지우고 다시 적재한다.
- vector dimension은 pgvector schema와 맞아야 한다.

예제 코드는 `.env`의 `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`를 읽는다. `load_docs.py`는 dimension을 명시하지 않으면 provider에 probe embedding을 요청해 길이를 추론한다. 운영에서는 probe에 의존하기보다 model과 dimension을 설정으로 고정하는 편이 낫다.

OpenAI 기본값:

```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
uv run python examples/02_rag/load_docs.py
```

Ollama 로컬 embedding:

```bash
ollama pull embeddinggemma
curl http://127.0.0.1:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "dimension test"
}' | jq '.embeddings[0] | length'

EMBEDDING_PROVIDER=ollama \
EMBEDDING_MODEL=embeddinggemma \
EMBEDDING_DIMENSIONS= \
OLLAMA_BASE_URL=http://127.0.0.1:11434 \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

`EMBEDDING_DIMENSIONS`를 직접 넣고 싶다면 위 `jq` 결과를 사용한다.

```bash
EMBEDDING_PROVIDER=ollama \
EMBEDDING_MODEL=embeddinggemma \
EMBEDDING_DIMENSIONS=768 \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

위의 `768`은 예시다. 실제 값은 사용하는 Ollama embedding model의 응답으로 확인해야 한다. Ollama 공식 API는 `/api/embed`에 `model`과 `input`을 보내고, 응답의 `embeddings` 배열을 반환한다.

SentenceTransformers 로컬 embedding:

```bash
uv add sentence-transformers

EMBEDDING_PROVIDER=sentence-transformers \
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
EMBEDDING_DIMENSIONS= \
SENTENCE_TRANSFORMERS_DEVICE=mps \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

Apple Silicon이 아니면 `SENTENCE_TRANSFORMERS_DEVICE`를 비우거나 `cpu`, `cuda` 등 로컬 환경에 맞게 쓴다. SentenceTransformers는 모델 이름 대신 로컬 디렉터리 경로도 받을 수 있으므로, 사내망에서 미리 내려받은 모델을 쓰는 방식도 가능하다.

### pgvector

`examples/02_rag/schema.sql`의 핵심은 이 한 줄이다.

```sql
embedding vector(1536) NOT NULL
```

기본 예제의 `text-embedding-3-small`은 1536 dimension vector를 반환한다. 다른 embedding model을 쓰면 `vector(1536)` 부분이 달라져야 한다. 현재 `load_docs.py`는 선택한 provider의 dimension에 맞춰 schema를 동적으로 만든다. `schema.sql`은 기본 OpenAI 설정을 설명하기 위한 읽기 자료로 남겨 둔다.

SQL 검색은 다음처럼 동작한다.

```sql
ORDER BY embedding <-> $1::vector
LIMIT 5
```

이 쿼리는 질문 embedding과 가까운 chunk를 찾는다.

강사가 설명할 tradeoff:

- `LIMIT`이 너무 작으면 근거가 부족하다.
- `LIMIT`이 너무 크면 context가 길어지고 noise가 늘어난다.
- 운영에서는 score threshold, metadata filter, reranking을 추가할 수 있다.

### GraphRAG와 Knowledge Graph 맛보기

Vector RAG는 의미적으로 가까운 chunk를 찾는 데 강하다. 하지만 질문이 entity와 relation을 따라가야 하는 경우라면 vector search만으로 부족할 수 있다.

예:

```text
"A 프로젝트의 장애 원인과 관련된 배포, 담당자, 후속 조치를 모두 알려줘."
```

이 질문은 "장애 원인"과 가까운 문서 하나만 찾는 문제가 아니다. 프로젝트, 배포, 담당자, 장애, 조치의 관계를 따라가야 한다. 이럴 때 GraphRAG나 Knowledge Graph가 도움이 될 수 있다.

수업에서는 구현하지 않고 구분만 한다.

| 방식 | 잘하는 일 | 먼저 배울 것 |
| --- | --- | --- |
| Vector RAG | 의미적으로 가까운 chunk 찾기 | chunking, embedding, pgvector |
| GraphRAG/KG | entity와 relation을 따라 근거 확장 | entity extraction, relation schema, graph query |

여기서 강사는 이렇게 말한다.

"처음부터 GraphRAG로 시작하지 않아요. 기본 Vector RAG가 어떤 질문에서 실패하는지 먼저 보고, 관계를 저장해야 할 이유가 생겼을 때 GraphRAG를 검토합니다."

## 라이브코딩 1: Schema 읽기

파일: `examples/02_rag/schema.sql`

진행:

1. `CREATE EXTENSION IF NOT EXISTS vector;`
2. `doc_chunks` 컬럼을 하나씩 설명한다.
3. `id text PRIMARY KEY`가 재적재할 때 중복을 막아 주는 이유를 짚는다.
4. HNSW index는 검색 성능을 위한 것이라고만 설명하고, 수식 설명에 오래 머물지 않는다.
5. embedding provider를 바꾸면 `vector(1536)`도 바뀌어야 한다는 점을 강조한다.

이렇게 말한다.

"RAG는 LLM 기능처럼 보이지만 실제로는 데이터 모델링 문제이기도 해요. source와 title을 저장하지 않으면 답변에 근거를 붙일 수 없고요. id가 안정적이지 않으면 같은 문서를 계속 중복으로 쌓게 됩니다."

## 라이브코딩 2: Ingestion

파일: `examples/02_rag/load_docs.py`

진행:

1. `DOCS_DIR`와 `SCHEMA_PATH`를 확인한다.
2. `split_markdown`이 heading 기준으로 문서를 나누는 것을 읽는다.
3. `stable_id`가 source와 content로 hash를 만드는 것을 설명한다.
4. `EmbeddingConfig.from_env()`가 provider/model/dimension 설정을 읽는 흐름을 설명한다.
5. `build_embedder()`가 OpenAI, Ollama, SentenceTransformers 중 하나를 골라 만든다는 걸 보여 준다.
6. `ON CONFLICT DO UPDATE`가 재실행 가능한 ingestion을 만든다는 점을 강조한다.

수강생에게 물어볼 질문:

- "문서를 수정하면 id가 바뀔까요?"
- "source path만 id로 쓰면 어떤 문제가 생길까요?"
- "title만 embedding하면 왜 부족할까요?"
- "embedding model을 바꾸면 기존 테이블을 그대로 써도 될까요?"

답변 방향:

- content가 바뀌면 현재 구현에서는 id가 바뀐다. 운영에서는 source와 chunk position, content hash를 별도로 둘 수 있다.
- source path만 쓰면 한 파일의 여러 chunk를 구분하기 어렵다.
- title만 embedding하면 본문 의미 검색이 약하다.
- embedding model이 바뀌면 같은 vector 공간이 아니므로 재색인해야 한다.

## 라이브코딩 3: RAG Agent

파일: `examples/02_rag/rag_agent.py`

진행:

1. `Deps`가 OpenAI client와 asyncpg pool을 들고 있다는 걸 설명한다.
2. agent instructions에서 "Always call retrieve"와 "Use only retrieved context"를 읽는다.
3. `retrieve` tool이 질문 embedding을 만들고 DB 검색을 수행하는 흐름을 따라간다.
4. 반환 문자열에 `Source`, `Title`, `Content`가 포함되는 이유를 설명한다.
5. `Deps`가 OpenAI client 대신 provider-agnostic `embedder`를 들고 있다는 점을 짚는다.
6. 질문을 2개 실행한다.

질문 예:

```bash
uv run python examples/02_rag/rag_agent.py "Pydantic AI에서 tool은 언제 쓰나요?"
uv run python examples/02_rag/rag_agent.py "DBOS는 무엇인가요?"
```

두 번째 질문은 현재 sample docs에 DBOS가 없으면 부족하다고 답해야 한다. 이 결과가 중요하다. RAG의 좋은 행동은 모르는 것을 모른다고 하는 것이다.

## 실습 1: 문서 추가와 재색인

수강생 작업:

1. `examples/02_rag/sample_docs/dbos.md`를 만든다.
2. DBOS durable execution의 핵심을 3~5문단으로 적는다.
3. `load_docs.py`를 다시 실행한다.
4. DBOS 관련 질문을 한다.

강사 순회 체크:

- Markdown heading이 있는가?
- 문서가 너무 짧거나 너무 긴가?
- 적재 로그에 새 chunk가 보이는가?
- 답변에 source가 붙는가?

리뷰 때는 이렇게 정리한다.

"문서를 추가했더니 답변이 나아졌죠. 모델을 fine-tune한 게 아니에요. 검색 가능한 지식 저장소를 갱신했을 뿐입니다. 이게 RAG의 운영상 장점이에요."

## 실습 2: Retrieval 품질 조정

선택 과제:

1. `LIMIT 5`를 `LIMIT 2`로 줄이고 답변을 비교한다.
2. `LIMIT 8`로 늘리고 답변을 비교한다.
3. `retrieve` 반환에 `Rank: 1`, `Rank: 2`를 붙인다.
4. source list가 더 읽기 좋게 나오도록 instructions를 수정한다.

이렇게 짚어 준다.

- retrieval parameter는 prompt만큼 중요하다.
- 답변이 길어진다고 항상 좋아지는 것은 아니다.
- source가 UI에 어떻게 표시될지까지 생각해야 한다.

## 실습 2-1: Data-Centric RAG 실패 분류

수강생 작업:

1. `sample_docs`에 비슷한 제목의 문서를 하나 더 추가한다.
2. 일부러 오래된 내용이라는 문장을 넣는다. 예: "이 문서는 2025년 기준이다."
3. 문서를 다시 적재하고 같은 질문을 실행한다.
4. 검색 결과에 새 문서가 섞이는지 확인한다.
5. 실패를 아래 중 하나로 분류한다.

```text
retrieval failure
context failure
generation failure
metadata/versioning failure
```

토론:

- source에 `updated_at`이 있으면 agent나 UI가 무엇을 다르게 할 수 있을까?
- 같은 문서의 여러 버전이 있을 때 최신 버전만 검색하려면 schema에 무엇이 필요할까?
- prompt injection 문장이 문서에 들어 있으면 retrieve tool에서 막을 것인가, generation policy에서 막을 것인가?

이렇게 정리한다.

"RAG 운영에서 문서 품질 관리는 부가 작업이 아니에요. 잘못된 데이터는 잘못된 답변으로 바로 이어집니다."

## 실습 3: 로컬 Embedding으로 전환

목표: 답변 생성 모델과 embedding 모델이 독립적으로 교체 가능하다는 점을 직접 경험한다.

수강생 작업 A: Ollama

1. Ollama가 설치되어 있으면 embedding model을 하나 받는다.

```bash
ollama pull embeddinggemma
```

2. dimension을 확인한다.

```bash
curl http://127.0.0.1:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "dimension test"
}' | jq '.embeddings[0] | length'
```

3. 테이블을 재생성하며 문서를 다시 적재한다.

```bash
EMBEDDING_PROVIDER=ollama \
EMBEDDING_MODEL=embeddinggemma \
EMBEDDING_DIMENSIONS= \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

4. 같은 질문을 실행하고 OpenAI embedding 결과와 답변 차이를 비교한다.

수강생 작업 B: SentenceTransformers

```bash
uv add sentence-transformers

EMBEDDING_PROVIDER=sentence-transformers \
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
EMBEDDING_DIMENSIONS= \
RESET_RAG_TABLE=1 \
uv run python examples/02_rag/load_docs.py
```

강사 리뷰 포인트:

- provider를 바꿔도 RAG pipeline의 구조는 그대로다.
- embedding model 품질 차이는 retrieval 결과 차이로 나타난다.
- 로컬 모델은 비용과 데이터 외부 전송 측면에서 장점이 있지만, model serving과 성능 관리를 직접 해야 한다.
- 같은 문서라도 embedding model이 바뀌면 기존 vector를 재사용하면 안 된다.

## 흔한 실패와 디버깅

### `relation "doc_chunks" does not exist`

원인: schema 생성 전 검색을 실행했다.

해결:

```bash
uv run python examples/02_rag/load_docs.py
```

### `dimension mismatch`

원인: embedding 모델 dimension과 `vector(1536)`이 다르다.

해결:

- `EMBEDDING_DIMENSIONS`가 실제 모델 dimension과 맞는지 확인한다.
- `RESET_RAG_TABLE=1`로 테이블을 지우고 다시 적재한다.
- OpenAI, Ollama, SentenceTransformers vector를 같은 테이블에 섞지 않는다.

Ollama dimension 확인 예:

```bash
curl http://127.0.0.1:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "dimension test"
}' | jq '.embeddings[0] | length'
```

### Ollama 연결 실패

원인:

- Ollama server가 실행 중이 아니다.
- `OLLAMA_BASE_URL`이 틀렸다.
- embedding model을 pull하지 않았다.

해결:

```bash
ollama serve
ollama pull embeddinggemma
curl http://127.0.0.1:11434/api/embed -d '{"model":"embeddinggemma","input":"test"}'
```

### SentenceTransformers import 실패

원인: 선택 dependency를 설치하지 않았다.

해결:

```bash
uv add sentence-transformers
```

### 답변이 문서 밖 내용을 만들어냄

원인:

- instructions가 약하다.
- retrieve 결과가 너무 적거나 무관하다.
- 질문이 문서 범위를 벗어났다.

해결:

- "Use only retrieved context" 강화.
- source 없는 문장은 금지.
- eval에서 source marker와 refusal behavior를 검증.

## 백엔드 운영 관점

운영형 RAG에서 추가로 필요한 것:

- 문서 ingestion job과 재시도 정책
- document version과 삭제 처리
- tenant별 metadata filter
- 중복 문서와 오래된 문서 정리 정책
- chunk id, content hash, source version 분리
- embedding 비용 모니터링
- embedding provider별 dimension/model version 관리
- 로컬 embedding server의 CPU/GPU 리소스 관리
- prompt injection이 포함된 문서 방어
- 검색 로그와 답변 source audit
- RAG 품질 eval dataset

강사는 여기서 과하게 구현하지 않는다. 대신 "오늘 만든 것은 최소 골격이고, 운영에서는 ingestion pipeline과 품질 평가가 절반 이상"이라고 정리한다.

## 미니 리뷰 질문

1. RAG에서 chunk가 너무 크면 어떤 문제가 생기나요?
2. embedding model을 바꾸면 왜 재색인이 필요할 수 있나요?
3. source를 저장하지 않은 RAG는 어떤 운영 문제가 있나요?
4. RAG tool은 side effect가 있어야 하나요?
5. 검색 결과가 없을 때 좋은 답변은 무엇인가요?
6. OpenAI embedding과 로컬 embedding을 선택할 때 어떤 tradeoff를 봐야 하나요?
7. pgvector dimension mismatch는 왜 발생하나요?
8. RAG 실패를 retrieval/context/generation 실패로 나누는 이유는 무엇인가요?
9. GraphRAG가 필요한 신호는 무엇인가요?

## 다음 회차 연결

"오늘 RAG agent는 검색 tool을 한 번 호출했어요. 그런데 실제 agent는 여러 문서를 검색하고, 여러 API를 호출하고, 결과를 필터링해야 하죠. tool call이 많아질수록 모델 왕복이 늘고 비용도 커집니다. 3회차에서는 모델이 여러 tool 호출을 Python 코드로 묶어 실행하게 하는 CodeMode와, 그 코드를 안전하게 제한하는 Monty를 다룹니다."

## 강사용 완료 기준

- 수강생이 RAG pipeline 7단계를 말할 수 있다.
- 최소 한 명 이상이 `schema.sql`에서 source/title/content/embedding의 역할을 설명했다.
- OpenAI embedding과 로컬 embedding의 tradeoff를 설명했다.
- embedding provider 변경 시 dimension 확인과 재색인이 필요함을 이해했다.
- RAG 품질을 모델 문제가 아니라 데이터 품질 문제로도 설명했다.
- GraphRAG는 기본 선택지가 아니라 관계 기반 검색이 필요할 때 검토하는 심화 패턴임을 이해했다.
- 문서 추가 후 답변 변화가 확인됐다.
- "모르는 질문에 모른다고 답하는 것"이 실패가 아니라 품질 기준임을 공유했다.
