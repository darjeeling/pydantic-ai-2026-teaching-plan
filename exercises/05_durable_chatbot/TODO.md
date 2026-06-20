# 5회차 실습 TODO

## 시작 파일

- `examples/05_chatbot/dbos_agent.py`
- `examples/05_chatbot/dbos_graph_resume.py`
- `examples/05_chatbot/app.py`
- `examples/05_chatbot/retrying_openai_model.py`

## 과제 A: DBOS

1. `dbos_agent.py`를 실행한다.
2. agent의 `name`을 제거하고 어떤 에러가 나는지 확인한다.
3. `system_database_url`이 생성한 SQLite 파일을 확인한다.

## 과제 B: Graph 저장과 복구

1. graph 구조를 Mermaid로 출력한다.

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --render
```

2. `draft`까지 실행하고 `review` 직전에 멈춘다.

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id my-graph --reset --stop-after draft
```

3. 출력에서 `status: paused`, `next_node: review`, `visited: retrieve, draft`를 확인한다.
4. 같은 `run_id`로 재개한다.

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id my-graph --resume
```

5. 출력에서 `status: completed`, `next_node: done`, `visited: retrieve, draft, review`를 확인한다.
6. `examples/05_chatbot/dbos_graph_state.sqlite`가 어떤 역할인지 설명한다.
7. graph를 재개하려면 최소 `run_id`, `state_json`, `next_node`, `status`가 필요한 이유를 적는다.

## 과제 C: 챗봇

1. 챗봇을 실행한다.

```bash
uv run uvicorn app:app --app-dir examples/05_chatbot --reload
```

2. 브라우저에서 `http://127.0.0.1:8000`을 연다.
3. 두 번 질문하고 `/messages`에서 history가 유지되는지 확인한다.
4. Send 버튼을 빠르게 여러 번 눌러 중복 메시지가 생기지 않는지 확인한다.
5. 브라우저 개발자 도구에서 `/chat` payload에 `request_id`가 들어가는지 확인한다.
6. instructions를 "백엔드 실무 관점"으로 더 강하게 수정한다.

## 과제 D: Timeout과 Retry

1. `examples/05_chatbot/retrying_openai_model.py`를 읽는다.
2. 어떤 HTTP status와 exception이 retry 대상인지 적는다.
3. `AGENT_TIMEOUT_SECONDS`가 너무 짧으면 UI가 어떻게 반응해야 하는지 적는다.
4. provider retry 3회와 DBOS step retry 3회를 동시에 켰을 때 최대 provider 호출 수를 계산한다.
5. 외부 write tool에 넘길 idempotency key 이름을 정한다.

## 과제 E: 서비스화 체크리스트

현재 FastAPI 챗봇을 사내 서비스로 배포한다고 가정한다.

1. 아래 항목을 `있음`, `없음`, `불필요`로 분류한다.

```text
secret/env 관리
DB migration
auth
rate limit
message retention
RAG source audit
eval regression gate
Logfire trace
token/cost tracking
background workflow
approval audit log
provider fallback policy
```

2. 가장 먼저 추가할 항목 2개를 고른다.
3. 각각을 장애/비용/보안 중 어떤 위험을 줄이기 위한 것인지 적는다.
4. MLflow, Airflow, vLLM/OpenWebUI, Kubernetes를 본편이 아니라 심화로 분리한 이유를 적는다.

## 확장 과제

- RAG `retrieve` tool을 챗봇 agent에 붙이는 설계를 작성한다.
- `dbos_graph_resume.py`에 `--stop-after retrieve` 실행 후 재개하는 케이스를 추가로 검증한다.
- graph node가 외부 write를 수행할 때 어떤 idempotency key를 넘길지 작성한다.
- 4회차 `human_approval_gate.py`의 approval request를 FastAPI/DBOS 구조로 옮기는 설계를 작성한다.
- approval ticket table에 필요한 필드를 적는다.
- 승인/거절 endpoint가 `DeferredToolResults`를 만들기 위해 어떤 데이터를 읽어야 하는지 적는다.
- `chat_requests` table의 running request가 오래 남았을 때 expired 처리 정책을 작성한다.
- session id를 query string 또는 cookie로 분리한다.
- message retention 정책을 추가한다.
- token usage와 provider 비용을 기록할 위치를 정한다.
- provider 장애 시 fail closed와 fallback model 중 어느 정책을 쓸지 정한다.

## 통과 기준

- DBOS agent가 답변한다.
- graph를 `draft` 후 멈추고 `review`부터 재개할 수 있다.
- graph checkpoint에 저장해야 하는 최소 필드를 설명할 수 있다.
- FastAPI 챗봇이 대화를 저장한다.
- 새 요청에서 이전 message history가 agent에 전달된다.
- 중복 클릭이 같은 agent run을 여러 번 만들지 않는 이유를 설명할 수 있다.
- provider retry, app timeout, DBOS retry를 구분할 수 있다.
- Human-in-the-loop approval 대기/재개가 왜 durable execution 문제인지 설명할 수 있다.
- FastAPI 데모와 운영 AI 서비스 사이에 필요한 추가 항목을 설명할 수 있다.
