# 5회차 슬라이드: DBOS와 FastAPI 챗봇

## 오늘의 결과물

- `DBOSAgent`
- graph checkpoint/resume
- human approval 대기/재개 설계
- FastAPI 웹챗
- SQLite message history
- request idempotency
- timeout/retry policy
- service/MLOps boundary
- 운영 관점 체크리스트

## Durable Execution

retry는 처음부터 다시 시도한다.

durable execution은 진행 상태를 저장해 두고 멈춘 지점부터 이어서 실행한다.

Human approval은 HTTP request 하나보다 오래 걸릴 수 있다.

Retry는 비용과 side effect를 키울 수 있다.

## DBOS

- workflow 상태를 DB에 checkpoint
- step은 I/O를 수행하고 재시도 가능
- SQLite로 로컬 실습, Postgres로 운영 권장

## Graph Resume

GraphBuilder는 흐름을 표현한다.

영구 저장과 복구는 durable execution과 앱 checkpoint로 설계한다.

최소한 저장할 값:

- `run_id`
- `state_json`
- `next_node`
- `status`

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --reset --stop-after draft
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --resume
```

## Timeout / Retry

- Provider HTTP retry: 429, 5xx, timeout
- Tool retry: model에게 tool call 재시도 요청
- DBOS step retry: durable step 재실행
- UI retry: 사용자의 재클릭/재전송

retry는 누가 책임질지 owner를 정한다.

provider 3회 * DBOS 3회 = 최대 9회

## Pydantic AI 통합

```python
agent = Agent("gpt-5.5", name="course_qa")
dbos_agent = DBOSAgent(agent)
```

## Human-in-the-loop

4회차:

- `requires_approval=True`
- `DeferredToolRequests`
- `DeferredToolResults`

5회차:

- approval ticket 저장
- message history 보존
- 승인/거절 후 workflow 재개
- side effect idempotency

## 챗봇 Backend

- `POST /chat`
- `request_id` idempotency key
- message history load
- agent run
- new messages persist
- transcript 반환

## 중복 클릭 방지

Frontend:

- pending 중 button/input disabled
- `crypto.randomUUID()`로 `request_id`

Backend:

- `chat_requests.request_id` unique
- completed request는 cached response 반환
- running request는 409

## 운영 체크리스트

- session id
- auth
- rate limit
- secret/env 관리
- DB migration
- message retention
- RAG source logging
- eval regression
- graph checkpoint policy
- durable background work
- approval audit log
- idempotency key
- timeout budget
- retry/backoff policy
- token/cost tracking
- provider fallback policy

## MLOps 경계

본편:

- FastAPI
- DB history/source audit
- Logfire
- eval regression
- DBOS durable workflow

심화:

- MLflow
- Airflow
- vLLM/OpenWebUI
- Kubernetes

## 마무리

Agent -> RAG -> sandbox -> eval/graph -> multi-agent -> HITL -> durable execution -> chatbot

어느 기능도 멋있어서 넣은 게 아니라, 저마다 특정 운영 문제를 풀려고 가져온 것이다.
