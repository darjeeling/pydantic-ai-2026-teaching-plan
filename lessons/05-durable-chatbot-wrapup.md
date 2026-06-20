# 5회차: Durable Execution과 기본 챗봇

## 2시간 목표

이 회차의 목표는 수강생이 agent를 실제 백엔드 앱으로 연결할 때 필요한 운영 관점을 갖게 하는 것이다. 특히 retry와 durable execution의 차이, graph 상태 저장/복구, human-in-the-loop 승인 대기/재개, DBOS workflow/step, FastAPI 챗봇의 message history 저장, 그리고 전체 과정의 기술들이 어떻게 연결되는지 정리한다.

완성 결과물은 다음과 같다.

- `examples/05_chatbot/dbos_agent.py`: `DBOSAgent`로 감싼 durable agent
- `examples/05_chatbot/dbos_graph_resume.py`: graph state와 다음 node를 저장하고 재개하는 DBOS 예제
- `examples/05_chatbot/app.py`: FastAPI 웹챗과 SQLite message history
- `examples/05_chatbot/retrying_openai_model.py`: HTTP timeout과 provider retry policy 예시
- 4회차의 `human_approval_gate.py`를 운영 시스템으로 옮기기 위한 approval ticket 설계

## 사례로 시작하기: "승인 버튼을 누르기 전에 서버가 재시작됐습니다"

마지막 회차는 챗봇 UI가 아니라 운영 사고에서 시작한다.

운영자가 agent에게 "수강생에게 일정 변경 공지를 작성하고 발송 준비해줘"라고 요청한다. agent는 RAG로 최신 일정을 찾고, 초안을 만들고, reviewer agent를 거친 뒤 "발송 승인 필요" 상태가 된다. 운영자는 회의에 들어가고 1시간 뒤 승인 버튼을 누른다. 그 사이 서버가 재시작됐다.

durable execution이 없으면 질문은 곧바로 어려워진다.

- 승인 대기 전까지 어떤 step이 완료됐는가?
- 다시 시작하면 RAG 검색부터 반복할 것인가, review 이후부터 이어갈 것인가?
- 이미 생성한 초안과 approval request id는 어디에 저장됐는가?
- 승인 버튼을 두 번 누르면 이메일이 두 번 나가는가?
- provider timeout으로 재시도된 요청과 사용자의 중복 클릭을 어떻게 구분하는가?

이 사례에서 retry만으로는 부족하다. retry는 실패한 호출을 다시 시도하지만, 긴 workflow에서 이미 완료된 step과 아직 실행하지 않은 side effect를 구분하지 못한다. durable execution은 "어디까지 완료됐는지"를 저장하고, 재개 시 같은 side effect가 중복되지 않게 설계하는 문제다.

수강생에게 보여줄 판단표:

| 상황 | 단순 retry | durable execution |
| --- | --- | --- |
| 일시적 HTTP timeout | 적합 | 필요할 수도 있지만 과할 수 있음 |
| 5단계 workflow 중 3단계 완료 후 재시작 | 부족 | 적합 |
| 사람 승인 대기 | 부족 | 적합 |
| 이메일/결제/공지 발행 같은 side effect | 위험 | idempotency와 함께 필요 |
| 단순 질의응답 챗봇 | 대체로 충분 | 보통 과함 |

이 장의 핵심은 "DBOS를 붙이면 안전하다"가 아니다. 안전성은 workflow step 경계, request idempotency, approval state, message history, side effect 설계가 함께 맞을 때 생긴다.

## 수업 전 준비

DBOS agent:

```bash
uv run python examples/05_chatbot/dbos_agent.py
```

Durable graph checkpoint/resume:

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --render
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --reset --stop-after draft
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --resume
```

FastAPI 챗봇:

```bash
uv run uvicorn app:app --app-dir examples/05_chatbot --reload
```

브라우저에서 `http://127.0.0.1:8000`을 연다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-8분 | 4회차 복습 | 긴 workflow 실패 문제 연결 | 실패 시나리오 말하기 |
| 8-24분 | Durable execution | retry와 durable의 차이 이해 | workflow/step 그림 읽기 |
| 24-40분 | DBOSAgent | Pydantic AI agent를 DBOS workflow로 감싸기 | `dbos_agent.py` 실행 |
| 40-58분 | Graph checkpoint/resume | graph state와 다음 node를 저장하고 복구하는 패턴 이해 | `dbos_graph_resume.py` 실행 |
| 58-70분 | Timeout과 retry policy | provider retry, tool retry, DBOS retry 차이 이해 | retry 예제 읽기 |
| 70-80분 | Human-in-the-loop durable 설계 | 승인 대기/재개가 durable boundary를 요구하는 이유 이해 | approval ticket 설계 |
| 80-85분 | 휴식 | 정리 | 질문 |
| 85-103분 | FastAPI 챗봇 | message history, request idempotency, agent run 연결 | 웹챗 실행 |
| 103-112분 | 서비스화/MLOps 경계 | 데모 앱을 운영 앱으로 바꿀 때 필요한 항목 이해 | 운영 체크리스트 작성 |
| 112-118분 | 통합 설계와 전체 리뷰 | RAG/HITL/DBOS/chatbot 연결 및 기술 선택 기준 정리 | 설계 토론 |
| 118-120분 | 마무리 | 다음 학습 방향 제시 | 회고 |

## 도입 이야기

수업을 이렇게 시작한다.

"4회차에서 workflow가 길어졌습니다. researcher agent가 호출되고, reviewer agent가 검토하고, graph가 여러 단계를 지나갑니다. 그리고 공지 발행처럼 사람이 승인해야 하는 tool call도 생겼습니다. 이 실행 중 서버가 죽으면 어떻게 될까요? 승인자가 3시간 뒤에 버튼을 누르면 어떤 message history로 이어가야 할까요? 그냥 처음부터 다시 하면 비용이 두 배가 될 수 있습니다. 더 위험한 것은 이메일 발송이나 결제 같은 side effect가 중복되는 것입니다."

칠판에 비교한다.

```text
Retry:
  failed operation -> try again

Durable execution:
  completed steps are checkpointed
  restart resumes from last completed step
  long-running approval waits keep their state
```

핵심 메시지:

- retry는 실패한 일을 다시 시도한다.
- durable execution은 진행 상태를 저장하고 이어간다.
- agent workflow는 model call, tool call, external API call이 섞여 있어 durable boundary가 중요하다.
- human approval은 HTTP request 하나보다 오래 걸릴 수 있으므로 approval state와 message history를 저장해야 한다.

## Durable Execution 개념 설명

### Workflow

workflow는 전체 업무 흐름이다. DBOS에서는 workflow input과 step output이 DB에 저장되어 재시작 시 복구에 사용된다.

초보자 설명:

"택배 배송 상태를 생각하면 됩니다. 접수, 집화, 간선 이동, 배송 출발이 기록되어 있으면 중간에 시스템이 꺼져도 처음 접수부터 다시 하지 않습니다."

### Step

step은 I/O나 외부 호출을 수행하는 단위다. model request, MCP communication, 일부 tool call이 step이 될 수 있다.

주의:

- workflow는 deterministic해야 한다.
- I/O는 step에 있어야 한다.
- custom tool이 DB, 네트워크, 파일 I/O를 한다면 `@DBOS.step`을 고려해야 한다.

### DBOS와 Pydantic AI

Pydantic AI의 `DBOSAgent`는 agent run을 DBOS workflow로 감싸고, model request와 MCP communication을 DBOS step으로 감싼다.

중요한 제약:

- agent에는 unique `name`이 필요하다.
- `DBOSAgent`는 `DBOS.launch()` 전에 정의되어야 한다.
- deps와 step output은 직렬화 가능해야 한다.
- streaming은 durable workflow와 직접 맞물리기 어렵다. event stream handler 같은 별도 패턴을 검토한다.

## 라이브코딩 1: DBOSAgent

파일: `examples/05_chatbot/dbos_agent.py`

진행:

1. `DBOSConfig`를 읽는다.
2. `system_database_url`이 SQLite를 가리키는 것을 설명한다.
3. `Agent(... name="course_qa_durable" ...)`에서 `name`을 강조한다.
4. `DBOSAgent(agent)`를 설명한다.
5. `DBOS.launch()` 이후 `dbos_agent.run(...)`을 실행한다.

수강생에게 물어볼 질문:

- "agent name이 왜 필요할까요?"
- "SQLite는 운영에서도 충분할까요?"
- "custom tool이 외부 API를 호출하면 자동으로 durable step인가요?"

답변 방향:

- name은 workflow/step 식별에 쓰인다.
- SQLite는 로컬 실습용이고 운영은 Postgres를 권장한다.
- custom tool은 자동으로 모두 step이 되지 않으므로 I/O tool은 명시적 step 설계를 고려한다.

## 실습 1: DBOS 실패 관찰

수강생 작업:

1. 정상 실행한다.
2. agent `name`을 제거한다.
3. 에러를 읽는다.
4. 다시 name을 복구한다.
5. 생성된 `examples/05_chatbot/dbos.sqlite` 파일을 확인한다.

강사 정리:

"durable system은 실행을 나중에 다시 찾아야 합니다. 이름이 없는 workflow는 운영에서 추적하기 어렵습니다. 그래서 Pydantic AI의 DBOS wrapper는 agent name을 요구합니다."

## 라이브코딩 2: Graph Checkpoint와 Resume

파일: `examples/05_chatbot/dbos_graph_resume.py`

4회차에서는 Pydantic Graph로 `retrieve -> draft -> review` 같은 상태 전이를 만들었다. 여기서 중요한 운영 질문은 이것이다.

"`draft`까지 끝난 뒤 서버가 내려가면, 다시 시작할 때 `retrieve`부터 할 것인가, `review`부터 할 것인가?"

Pydantic Graph의 builder API는 graph 구조와 step-by-step 실행 제어를 제공하지만, builder 자체가 모든 실행 상태를 자동으로 영구 저장해 주지는 않는다. 공식 문서도 builder API persistence는 durable execution 계층과 함께 설계하라고 안내한다. 따라서 운영 설계에서는 graph state와 다음에 실행할 node를 앱 DB나 durable workflow state에 명시적으로 저장한다.

이 예제의 핵심 구조:

```text
graph shape:
  retrieve -> draft -> review -> done

checkpoint row:
  run_id
  state_json
  next_node
  status
  updated_at
```

강사가 보여줄 실행:

```bash
uv run python examples/05_chatbot/dbos_graph_resume.py --render
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --reset --stop-after draft
uv run python examples/05_chatbot/dbos_graph_resume.py --run-id demo-graph --resume
```

첫 번째 명령은 Mermaid graph를 출력한다. 두 번째 명령은 `retrieve`, `draft`를 실행하고 `review` 직전에 멈춘다. 세 번째 명령은 같은 `run_id`의 checkpoint를 읽고 `review`만 실행해서 완료한다.

수강생이 관찰할 출력:

```text
status: paused
next_node: review
visited: retrieve, draft
```

재개 후:

```text
status: completed
next_node: done
visited: retrieve, draft, review
```

코드에서 볼 지점:

- `CourseGraphState`: graph가 들고 다니는 serializable state
- `GraphCheckpoint`: `state_json`, `next_node`, `status`로 재개 위치 표현
- `@DBOS.step()`이 붙은 `run_retrieve_node`, `run_draft_node`, `run_review_node`
- `@DBOS.workflow(name="course_graph.run_or_resume")`: checkpoint를 읽고 다음 node부터 실행
- `save_checkpoint`: replay나 재시도에도 같은 `run_id` row를 upsert하는 idempotent write

강사가 강조할 문장:

"Graph는 흐름을 표현하고, durable execution은 흐름의 진행 상태를 잃지 않게 합니다. 두 개를 섞을 때 핵심은 `다음에 실행할 node가 무엇인가`를 데이터로 저장하는 것입니다."

주의할 점:

| 파일 | 역할 |
| --- | --- |
| `dbos_graph.sqlite` | DBOS가 workflow/step 실행 기록을 저장하는 system DB |
| `dbos_graph_state.sqlite` | 예제 앱이 graph `state_json`과 `next_node`를 저장하는 checkpoint DB |

- DBOS system database와 앱 checkpoint table은 목적이 다르다.
- DBOS는 workflow/step의 실행과 재시도를 durable하게 만든다.
- graph를 HTTP 요청 여러 번에 걸쳐 pause/resume하려면 앱 레벨의 `run_id`, `next_node`, `state_json`이 필요하다.
- state는 작고 직렬화 가능해야 한다. DB connection, file handle, live client 객체를 state에 넣지 않는다.
- side effect가 있는 node는 idempotency key를 받아야 한다.
- parallel graph는 snapshot 기준이 더 복잡하다. 처음에는 순차 node 경계에서 checkpoint한다.

## 실습 2: Graph 저장과 복구

수강생 작업:

1. `--render`로 graph 구조를 확인한다.
2. `--run-id my-graph --reset --stop-after draft`로 `review` 직전에 멈춘다.
3. 출력에서 `status`, `next_node`, `visited`를 기록한다.
4. `--run-id my-graph --resume`으로 이어 실행한다.
5. `examples/05_chatbot/dbos_graph_state.sqlite`가 생성됐는지 확인한다.
6. `--stop-after retrieve`로 멈춘 뒤 재개하면 어떤 node부터 실행되는지 확인한다.

토론 질문:

- "`state_json`에 LLM 응답 전문을 모두 넣어도 될까요?"
- "`retrieve`가 외부 검색 API를 호출한다면 retry와 idempotency는 어디에 있어야 할까요?"
- "parallel branch가 있는 graph에서는 어느 시점에 checkpoint해야 할까요?"

답변 방향:

- 큰 데이터는 object storage나 별도 table에 두고 checkpoint에는 reference를 둔다.
- 외부 I/O는 DBOS step이나 provider retry policy를 명확히 정한다.
- parallel graph는 branch별 완료 상태와 join 상태까지 저장해야 하므로 처음에는 순차 graph로 시작한다.

## Timeout과 Retry Policy

운영에서 LLM provider 호출은 끊길 수 있다. DNS, TLS, provider 장애, rate limit, 긴 추론, client timeout, worker restart가 모두 가능하다. 이때 무조건 retry를 많이 넣으면 해결되는 것이 아니라 비용과 중복 side effect가 늘어난다.

구분해야 할 retry:

| 계층 | 무엇을 다시 시도하나 | 예 | 주의 |
| --- | --- | --- | --- |
| Provider HTTP retry | provider HTTP request | 429, 502, 503, timeout | `Retry-After` 존중, 비용 증가 |
| Pydantic AI tool retry | 모델에게 tool call을 다시 시도하게 함 | `ModelRetry`, tool timeout | 같은 외부 write가 중복되지 않게 설계 |
| Durable step retry | workflow step을 재실행 | DBOS model step, custom `@DBOS.step` | provider SDK retry와 겹치면 시도 횟수 폭증 |
| UI retry | 사용자가 다시 누름/브라우저 재전송 | fetch 재시도, 새로고침 | idempotency key 없으면 agent run 중복 |

강사가 강조할 문장:

"retry는 공짜가 아닙니다. LLM 호출은 비용이 들고, tool은 side effect를 만들 수 있습니다. retry를 켜기 전에 어떤 계층에서, 어떤 오류에 대해, 몇 번까지 다시 시도할지 정해야 합니다."

Pydantic AI의 HTTP retry transport는 HTTPX client에 붙인다. 예제 파일은 `examples/05_chatbot/retrying_openai_model.py`다.

```python
transport = AsyncTenacityTransport(
    config=RetryConfig(
        retry=retry_if_exception_type(
            (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError)
        ),
        wait=wait_retry_after(
            fallback_strategy=wait_exponential(multiplier=1, max=10),
            max_wait=60,
        ),
        stop=stop_after_attempt(3),
        reraise=True,
    ),
    validate_response=raise_for_retryable_status,
)
client = httpx.AsyncClient(transport=transport, timeout=httpx.Timeout(30.0))
```

이 예제의 포인트:

- 429, 502, 503, 504처럼 일시적일 수 있는 상태만 retry한다.
- `Retry-After`가 있으면 우선 존중하고, 없으면 exponential backoff를 쓴다.
- 전체 timeout을 둔다. retry가 늘어나면 사용자가 기다리는 시간도 늘어난다.
- Bedrock은 HTTPX가 아니라 boto3 retry 설정을 사용한다.

DBOS와 함께 쓸 때:

- DBOS model step retry를 켤지, provider HTTP retry를 켤지 한 계층을 주 retry owner로 정한다.
- 둘 다 켜야 한다면 총 시도 횟수를 계산한다. 예: provider 3회 * DBOS step 3회 = 최대 9회.
- 외부 write tool은 idempotency key를 받게 만든다.
- timeout은 provider client, agent request, web request, workflow step 각각에서 일관되게 잡는다.

교육용 권장:

- 5회차 기본 챗봇은 app-level `AGENT_TIMEOUT_SECONDS`로 사용자가 무한 대기하지 않게 한다.
- provider retry 예제는 읽고 토론한다.
- DBOS retry는 개념으로 설명하고, 실제 운영에서는 계층별 retry owner를 먼저 정하게 한다.

## DBOS 운영 주의사항

강사가 설명할 항목:

- **직렬화 가능성**: deps에 live socket, DB connection, thread lock 같은 것을 넣으면 durable boundary에서 문제가 될 수 있다.
- **step 크기**: 큰 output을 DB에 계속 저장하면 성능과 비용 문제가 생긴다.
- **side effect**: 이메일 발송, 결제, 외부 write는 idempotency key를 둔다.
- **retry 중복**: provider SDK retry와 DBOS retry가 겹치면 예상보다 많이 재시도할 수 있다.
- **streaming**: 사용자의 실시간 UI와 durable workflow는 별도 설계가 필요할 수 있다.

이 부분은 구현보다 사고방식을 전달한다. 수강생이 "그냥 DBOSAgent로 감싸면 모든 운영 문제가 해결된다"고 오해하지 않게 한다.

## Human-in-the-loop Durable 설계

4회차에서는 `requires_approval=True` tool과 `DeferredToolRequests`를 봤다. 그 예제는 한 Python 프로세스 안에서 바로 승인 결과를 만들었다. 운영에서는 보통 그렇지 않다.

실제 흐름:

```text
agent run
  -> model requests risky tool call
  -> DeferredToolRequests output
  -> create approval ticket
  -> return "pending approval" to UI
  -> human approves/denies minutes or days later
  -> resume agent with message_history + DeferredToolResults
```

여기서 durable execution이 필요한 이유:

- 승인자가 바로 응답하지 않을 수 있다.
- web worker가 재시작될 수 있다.
- 승인 요청을 중복 생성하면 안 된다.
- 승인 이후 같은 tool call이 두 번 실행되면 안 된다.
- 승인/거절 사유는 감사 로그로 남아야 한다.
- 재개할 때 원래 `message_history`와 tool call id가 필요하다.

Approval ticket에 저장할 최소 필드:

| 필드 | 이유 |
| --- | --- |
| `ticket_id` | UI와 workflow가 참조하는 id |
| `workflow_id` | durable workflow 재개 대상 |
| `session_id` / `user_id` | 누가 요청했는지 |
| `tool_call_id` | `DeferredToolResults.approvals` key |
| `tool_name` | 어떤 행동인지 |
| `tool_args_json` | 승인자가 볼 인자 |
| `message_history_json` | agent run 재개에 필요 |
| `status` | `pending`, `approved`, `denied`, `expired` |
| `approver_id` | 누가 승인했는지 |
| `decision_reason` | 승인/거절 이유 |
| `created_at`, `decided_at` | 감사와 timeout |

강사가 강조할 문장:

"Human-in-the-loop에서 어려운 부분은 버튼을 만드는 것이 아닙니다. 어떤 tool call을 어떤 message history와 함께 멈췄는지 잃지 않고, 승인 후 정확히 그 자리에서 이어가는 것입니다."

DBOS로 설계할 때의 경계:

- agent를 실행하는 workflow가 `DeferredToolRequests`를 받으면 approval ticket을 만든다.
- ticket 생성은 idempotent해야 한다. 같은 workflow replay에서 중복 ticket이 생기면 안 된다.
- 사람이 승인하면 별도 endpoint가 ticket 상태를 바꾸고 workflow 재개 신호를 보낸다.
- 실제 외부 write tool은 승인 후에도 idempotency key를 사용한다.

교육용 pseudocode:

```python
@DBOS.workflow()
async def run_agent_until_approval(session_id: str, prompt: str) -> str:
    result = await dbos_agent.run(prompt)
    if isinstance(result.output, DeferredToolRequests):
        await create_approval_ticket(
            session_id=session_id,
            requests=result.output,
            message_history=result.all_messages_json(),
        )
        return "pending_approval"
    return str(result.output)


@DBOS.workflow()
async def resume_after_approval(ticket_id: str) -> str:
    ticket = await load_approval_ticket(ticket_id)
    deferred_results = build_deferred_results(ticket)
    result = await dbos_agent.run(
        "승인 결과를 반영해서 계속 진행하세요.",
        message_history=ticket.message_history,
        deferred_tool_results=deferred_results,
    )
    return str(result.output)
```

이 코드는 수업용 구조 설명이다. 실제 DBOS API와 이벤트/queue 설계는 프로젝트 환경에 맞춰 잡아야 한다.

## FastAPI 챗봇 개념 설명

챗봇 backend에서 필요한 최소 요소:

- HTTP endpoint
- user message input
- request idempotency key
- message history load
- agent run
- new messages persist
- transcript response

`examples/05_chatbot/app.py`는 SQLite에 Pydantic AI message history를 저장한다. 핵심은 `ModelMessagesTypeAdapter.validate_json(...)`와 `result.new_messages_json()`이다.

설명:

- Pydantic AI message는 provider별 raw message가 아니라 normalized message다.
- 저장된 history를 다음 `agent.run(..., message_history=history)`에 넘긴다.
- 단일 SQLite 파일은 교육용이다. 운영에서는 session id, user id, retention policy가 필요하다.

### 중복 클릭과 Idempotency

웹 UI에서 사용자가 버튼을 여러 번 클릭하거나, 브라우저/네트워크가 같은 요청을 다시 보낼 수 있다. backend가 아무 방어도 하지 않으면 같은 user prompt가 여러 번 agent에게 전달되고, 비용이 여러 번 발생하며, message history도 중복된다.

이 예제는 두 겹으로 막는다.

1. Frontend guard
   - submit 후 input과 button을 disabled로 바꾼다.
   - 진행 중인 `pendingRequestId`가 있으면 submit을 무시한다.
   - `crypto.randomUUID()`로 `request_id`를 만든다.
2. Backend idempotency
   - `/chat` 요청은 `request_id`를 받는다.
   - `chat_requests.request_id`에 unique constraint를 둔다.
   - 같은 `request_id`가 이미 완료됐으면 저장된 response를 반환한다.
   - 같은 `request_id`가 아직 running이면 409를 반환한다.

핵심은 frontend만 믿지 않는 것이다. 실제 운영에서는 브라우저 탭 여러 개, 모바일 네트워크 재전송, proxy retry, 사용자 새로고침이 모두 가능하므로 backend idempotency가 필요하다.

예제에서 볼 코드:

```python
class ChatRequest(BaseModel):
    request_id: str
    message: str


cached_response = store.begin_request(request.request_id)
if cached_response is not None:
    return cached_response
```

운영에서 추가할 것:

- `request_id`를 session/user와 묶는다. 다른 사용자가 같은 id를 보내면 안 된다.
- running 상태가 너무 오래 지속되면 timeout/expired 처리를 한다.
- response JSON뿐 아니라 error와 retry 가능 여부를 저장한다.
- agent run이 외부 write를 한다면 tool에도 같은 idempotency key를 전달한다.

## 라이브코딩 3: FastAPI 앱

파일: `examples/05_chatbot/app.py`

진행:

1. `agent = Agent(...)` instructions를 읽는다.
2. `ChatRequest`, `ChatMessage` 모델을 읽는다.
3. `ChatStore.connect`가 messages table을 만드는 것을 설명한다.
4. `get_model_messages`가 저장된 JSON을 Pydantic AI message로 복원하는 것을 설명한다.
5. `/chat` endpoint에서 history를 읽고 agent를 실행하고 new messages를 저장하는 흐름을 따라간다.
6. 브라우저에서 질문하고 `/messages`를 확인한다.
7. 버튼을 빠르게 여러 번 눌러도 중복 메시지가 생기지 않는지 확인한다.

질문 예:

```text
Pydantic AI에서 tool과 RAG는 어떻게 다른가요?
```

수강생 관찰 포인트:

- 두 번째 질문에서 이전 대화가 반영되는지 확인한다.
- `/messages`에 user/model message가 쌓이는지 확인한다.
- API 키가 없으면 UI는 열리지만 `/chat` 호출은 실패할 수 있다.

## 실습 3: Persona와 History 확인

수강생 작업:

1. instructions를 "백엔드 실무자 관점으로 답하라"로 바꾼다.
2. 서버를 재시작한다.
3. 같은 질문을 다시 던져 답변 스타일 변화를 본다.
4. `/messages` endpoint를 열어 history가 저장되어 있는지 확인한다.
5. 같은 질문을 입력하고 Send 버튼을 빠르게 여러 번 눌러 중복 요청 방지를 확인한다.

강사 질문:

- "instructions를 바꿨는데 기존 history는 그대로 둬도 될까요?"
- "운영에서 prompt version이 바뀌면 과거 대화와 호환성 문제가 생길까요?"

답변 방향:

- prompt/instructions version을 저장하는 것이 좋다.
- 큰 변경이 있으면 새 session으로 분리하거나 migration 정책이 필요하다.

## 실습 4: Timeout과 Retry 설계

수강생 작업:

1. `examples/05_chatbot/retrying_openai_model.py`를 읽는다.
2. retry 대상 HTTP status와 exception을 확인한다.
3. `AGENT_TIMEOUT_SECONDS=1`로 챗봇을 실행하면 어떤 사용자 경험이 되는지 토론한다.
4. provider retry 3회와 DBOS step retry 3회를 동시에 켰을 때 최대 몇 번 호출될지 계산한다.
5. 외부 write tool이라면 어떤 idempotency key를 넘길지 적는다.

강사 정리:

"timeout은 UX 정책이고, retry는 장애 대응 정책이고, durable execution은 진행 상태 보존 정책입니다. 세 가지를 한 단어로 뭉개면 운영에서 비용과 중복 실행을 제어할 수 없습니다."

## 서비스화와 MLOps 경계

이 과정의 마지막 앱은 FastAPI 챗봇이지만, 수업의 목표는 "브라우저에서 한 번 답하게 만들기"가 아니다. Python AI 앱이 서비스가 되려면 모델 호출, RAG 데이터, workflow 상태, 비용, 배포, 관측 가능성이 함께 관리되어야 한다.

강사가 먼저 선을 긋는다.

"이 수업은 MLflow, Airflow, Kubernetes, vLLM을 깊게 배우는 수업이 아닙니다. 대신 Pydantic AI 앱을 운영으로 보내기 전에 어떤 질문을 해야 하는지 익힙니다. 지금 범위에서는 FastAPI, DB, eval, Logfire, DBOS가 운영 입문선입니다."

운영 체크리스트:

| 영역 | 질문 | 현재 교안의 연결 |
| --- | --- | --- |
| 환경/secret | API key와 provider credential은 어디서 주입하는가? | 0회차 `.env`, provider smoke test |
| 배포 | 같은 명령이 서버에서도 재현되는가? | `uv`, Docker 후보, `.python-version` |
| DB migration | SQLite table을 언제/어떻게 바꾸는가? | RAG schema, chat history schema |
| RAG ingestion | 문서 변경, 삭제, 중복, version을 어떻게 처리하는가? | 2회차 Data-Centric RAG |
| Eval gate | prompt/model/RAG 변경이 회귀를 만들었는가? | 4회차 deterministic/model-switch eval |
| Observability | 어떤 run이 어떤 tool/model/source를 썼는가? | 1회차 Logfire, 5회차 request id |
| Cost/usage | token usage와 provider 비용을 추적하는가? | 4회차 usage metric, Logfire trace |
| Rate limit | 사용자/tenant/provider별 제한이 있는가? | FastAPI middleware 또는 gateway |
| Background work | 긴 ingestion/eval/workflow를 HTTP 요청 안에서 처리하는가? | DBOS workflow/queue 후보 |
| Retention | message history와 approval audit을 얼마나 보관하는가? | chat store, approval ticket |
| Fallback | provider 장애 때 fail closed인가, 다른 모델로 전환인가? | 0회차 provider matrix, 4회차 model eval |

MLOps 도구를 어디에 둘지:

| 도구/영역 | 이 과정에서의 위치 |
| --- | --- |
| MLflow | 전통 ML experiment tracking 또는 self-host model 평가 심화 |
| Airflow | 문서 ingestion, batch eval, scheduled refresh 심화 |
| vLLM/OpenWebUI | self-hosted LLM serving 심화 |
| Kubernetes | 운영 배포/스케일링 심화 |
| DBOS | agent workflow와 long-running approval의 durable execution |
| Logfire | Pydantic AI run/model/tool 관측 |

수강생에게 물어볼 질문:

- "이 챗봇을 사내 서비스로 배포하려면 가장 먼저 빠진 것은 무엇인가요?"
- "RAG 문서가 매일 바뀐다면 ingestion은 HTTP request 안에서 할까요?"
- "모델 비용이 갑자기 두 배가 되면 어떤 로그나 metric으로 원인을 찾을까요?"
- "provider 장애 시 사용자에게 실패를 보여줄지, 더 싼/느린 fallback 모델로 보낼지 누가 결정해야 할까요?"

## 실습 5: 운영 체크리스트 작성

수강생 작업:

1. 현재 FastAPI 챗봇을 운영 배포한다고 가정한다.
2. 위 체크리스트에서 "이미 있다", "수업 예제에는 없다", "우리 서비스에는 필요 없다"로 표시한다.
3. `eval`, `observability`, `rate limit`, `retention`, `fallback` 중 가장 먼저 추가할 2개를 고른다.
4. 선택 이유를 장애/비용/보안 관점으로 설명한다.

## 통합 설계: RAG 챗봇으로 확장

수업 후반은 구현보다 설계 토론으로 둔다.

질문:

"2회차 RAG agent와 4회차 human approval gate를 이 FastAPI 챗봇에 붙이려면 무엇을 바꿔야 할까요?"

기대 답:

- `Deps`에 OpenAI client와 asyncpg pool이 필요하다.
- FastAPI lifespan에서 pool을 생성하고 종료한다.
- `/chat`에서 `agent.run(..., deps=deps, message_history=history)`를 호출한다.
- source를 UI response에 별도로 담고 싶으면 output schema를 바꾼다.
- session별 history와 RAG source audit을 함께 저장한다.
- 위험 tool call은 즉시 실행하지 않고 approval ticket으로 반환한다.
- 사용자 요청은 `request_id`로 idempotent하게 처리한다.
- approval UI는 ticket의 tool name, args, reason, requester를 보여준다.
- 승인 endpoint는 `DeferredToolResults`를 만들 수 있을 만큼 tool call id와 message history를 보존해야 한다.

칠판 설계:

```text
FastAPI request
  -> load session history
  -> begin idempotent request(request_id)
  -> build deps(openai, pg pool, user/session)
  -> agent with retrieve tool
  -> if DeferredToolRequests: create approval ticket
  -> save new messages
  -> return reply + sources
```

## 전체 과정 리뷰

마지막에는 5회차 전체를 하나의 선택 기준으로 정리한다.

| 문제 | 사용할 도구 |
| --- | --- |
| LLM 호출을 타입 있는 앱 경계로 만들고 싶다 | Pydantic AI Agent |
| 모델이 앱 코드 기능을 쓰게 하고 싶다 | Function tools |
| 사내 문서 기반 답변이 필요하다 | RAG |
| 여러 tool 호출과 로컬 계산이 많다 | CodeMode |
| 모델 작성 코드를 제한하고 싶다 | Monty |
| 품질 회귀를 잡고 싶다 | Pydantic Evals |
| 상태 전이가 복잡하고 시각화가 필요하다 | Pydantic Graph |
| 역할별 agent를 나누고 싶다 | Multi-agent workflow |
| 위험한 tool call에 사람 승인이 필요하다 | Human-in-the-loop deferred tool |
| 긴 실행을 실패 후 이어가고 싶다 | DBOS durable execution |
| graph를 중간에 멈추고 다음 node부터 재개하고 싶다 | graph state checkpoint + durable workflow |
| 사용자가 버튼을 여러 번 눌러도 한 번만 실행하고 싶다 | request idempotency key |
| provider timeout/rate limit을 다루고 싶다 | HTTP retry/backoff policy |
| 사용자에게 웹으로 제공하고 싶다 | FastAPI chatbot |
| 운영에서 비용/품질/장애를 추적하고 싶다 | Logfire + eval report + usage metric |
| 노트북 AI 실습을 서비스 운영으로 확장하고 싶다 | FastAPI, DB migration, background workflow, deployment checklist |

## 흔한 오해와 정리

오해 1: "DBOS는 retry library다."

정리: retry보다 넓다. checkpoint를 통해 완료된 step을 보존하고 이어서 실행한다.

오해 2: "챗봇은 프론트 UI만 만들면 된다."

정리: message history, session, auth, rate limit, source audit, prompt version, retention이 backend 핵심이다.

오해 3: "DBOSAgent로 감싸면 모든 tool이 안전해진다."

정리: custom tool의 side effect와 idempotency는 여전히 개발자가 설계해야 한다.

오해 4: "Pydantic Graph를 쓰면 실행 상태도 자동으로 영구 저장된다."

정리: graph는 상태 전이와 시각화에 강하다. builder API의 영구 저장/복구는 durable execution이나 앱 checkpoint table과 함께 설계한다.

오해 5: "Human-in-the-loop는 reviewer agent를 하나 더 두면 된다."

정리: 아니다. reviewer agent는 모델 판단이고, human approval은 권한과 책임을 가진 사용자의 결정이다. 승인 대기와 재개 상태를 저장해야 하므로 durable execution과 함께 설계해야 한다.

오해 6: "프론트에서 버튼만 disable하면 중복 실행은 해결된다."

정리: 아니다. frontend guard는 UX 개선이고, backend idempotency가 실제 방어다. 같은 요청이 네트워크/브라우저/proxy에서 다시 들어와도 agent run이 중복되지 않아야 한다.

## 미니 리뷰 질문

1. retry와 durable execution의 차이는 무엇인가요?
2. DBOSAgent에서 agent `name`이 필요한 이유는 무엇인가요?
3. graph를 중간에 멈췄다가 재개하려면 최소 어떤 값을 저장해야 하나요?
4. message history를 provider raw format이 아니라 Pydantic AI message로 저장하는 장점은 무엇인가요?
5. FastAPI 챗봇에 RAG를 붙일 때 deps에는 무엇이 들어가나요?
6. Human-in-the-loop approval ticket에는 어떤 필드가 필요하나요?
7. provider HTTP retry와 DBOS step retry를 동시에 켤 때 어떤 위험이 있나요?
8. 운영 챗봇에서 반드시 필요한 보안/운영 기능 3가지는 무엇인가요?
9. MLflow/Airflow/vLLM 같은 도구를 이 과정 본편이 아니라 심화로 분리한 이유는 무엇인가요?

## 마무리 이야기

"이 과정은 Pydantic AI 문법만 배우는 과정이 아닙니다. agent를 앱으로 만드는 순서를 배웠습니다. 먼저 타입 있는 agent 경계를 만들고, 필요한 지식을 RAG로 붙이고, tool orchestration이 커지면 CodeMode와 Monty를 고려하고, 품질은 eval로 지키고, 복잡한 workflow는 graph나 multi-agent로 구성합니다. 위험한 행동은 human-in-the-loop로 멈추고, 긴 실행과 승인 대기는 DBOS로 durable하게 만들고, 마지막으로 FastAPI로 사용자에게 제공합니다."

수강생에게 마지막 질문을 던진다.

"여러분이 지금 만드는 서비스에서 가장 먼저 필요한 것은 RAG인가요, eval인가요, durable execution인가요? 기술을 많이 쓰는 것이 목표가 아니라, 지금 가장 큰 위험을 줄이는 것이 목표입니다."

## 강사용 완료 기준

- 수강생이 retry와 durable execution을 구분했다.
- `dbos_agent.py`에서 agent name requirement를 확인했다.
- graph state와 `next_node`를 저장하고 재개하는 패턴을 설명했다.
- human approval 대기/재개가 durable execution 문제임을 설명했다.
- FastAPI 챗봇에서 message history 저장 흐름을 설명했다.
- 중복 클릭/재전송을 frontend guard와 backend idempotency로 나눠 설명했다.
- provider timeout/retry와 DBOS retry의 차이를 설명했다.
- RAG/HITL 챗봇 확장 설계를 말로 그릴 수 있다.
- FastAPI 데모와 운영 AI 서비스 사이의 차이를 체크리스트로 설명했다.
- 전체 5회 과정의 기술 선택 기준을 정리했다.
