# 2회차 슬라이드: RAG

## 오늘의 결과물

- Markdown 문서 chunking
- OpenAI embedding 생성
- pgvector 저장과 검색
- RAG search tool을 가진 agent
- Data-Centric RAG 실패 분류

## RAG가 해결하는 문제

- 모델이 모르는 최신/사내 지식
- 출처가 필요한 답변
- 긴 문서를 매번 prompt에 넣을 수 없는 비용 문제

## Pipeline

문서 수집 -> chunking -> embedding -> vector DB -> search -> answer

## Chunk에 넣어야 할 것

- content
- title
- source path 또는 URL
- version 또는 updated_at
- embedding 대상 텍스트

## pgvector 검색

```sql
SELECT source, title, content
FROM doc_chunks
ORDER BY embedding <-> $1::vector
LIMIT 5;
```

## Agent Tool로 연결

```python
@agent.tool
async def retrieve(ctx: RunContext[Deps], query: str) -> str:
    ...
```

## 답변 정책

- 검색 결과 안에서만 답한다.
- 근거가 부족하면 모른다고 한다.
- source를 함께 반환한다.

## Data-Centric RAG

아무리 좋은 모델도 검색된 문서가 나쁘면 나쁜 답을 낸다.

- 최신성
- 중복 문서
- source/version metadata
- tenant 권한
- prompt injection

## 실패 분류

- retrieval failure
- context failure
- generation failure
- metadata/versioning failure

4회차에서는 이 분류를 eval로 만든다.

## GraphRAG 맛보기

Vector RAG는 가까운 chunk를 찾는다.

GraphRAG는 entity와 relation을 따라간다.

처음부터 GraphRAG로 가지는 않는다. 관계를 묻는 질문에서 Vector RAG가 자꾸 실패할 때 검토한다.

## 실무 질문

- embedding 모델이 바뀌면 재색인이 필요한가?
- chunk size와 overlap은 어떻게 정할 것인가?
- 삭제된 문서는 검색에서 어떻게 제거할 것인가?
- prompt injection이 문서에 들어 있으면 어떻게 방어할 것인가?
- source version이 없으면 오래된 문서를 어떻게 걸러낼 것인가?
