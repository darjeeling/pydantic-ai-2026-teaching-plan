# 4회차: Evals, Graph, Multi-agent Workflow

## 2시간 목표

이 회차의 목표는 수강생이 agent 기능을 만든 뒤 반드시 "품질을 어떻게 확인할 것인가"를 묻게 만드는 것이다. 또한 Pydantic Evals, Pydantic Graph, multi-agent workflow가 각각 다른 문제를 해결한다는 점을 구분하게 한다.

완성 결과물은 세 가지다.

- `examples/04_evals/evaluate_contract.py`: deterministic eval dataset과 custom evaluator
- `examples/04_evals/rag_tool_use_eval.py`: RAG source hit와 tool-use policy를 검증하는 deterministic eval
- `examples/04_evals/compare_models.py`: 모델 후보 전환 전 pass rate와 usage를 비교하는 eval
- `examples/04_evals/graph_workflow.py`: retrieve -> draft -> review typed graph
- `examples/04_evals/multi_agent_workflow.py`: parent agent가 researcher agent를 tool처럼 호출하는 workflow
- `examples/04_evals/human_approval_gate.py`: 사람이 승인해야 하는 deferred tool call

## 사례로 시작하기: "데모는 됐는데 모델을 바꾸니 망가졌습니다"

수업은 다음 상황에서 시작한다.

1회차 course assistant는 데모에서 자연스럽게 답했다. 2회차 RAG도 몇 가지 질문에는 잘 답했다. 3회차 CodeMode도 표를 만들었다. 그래서 팀은 비용을 줄이려고 모델을 바꾼다. 그런데 배포 뒤 문제가 생긴다.

- 새 모델은 tool을 덜 호출하고 기억으로 답한다.
- RAG 질문에서 source가 없는 답변이 늘어난다.
- JSON schema는 맞지만 `lesson_ids`가 비어 있다.
- reviewer agent는 "좋음"이라고 하지만 실제로는 금지된 action을 제안한다.
- workflow가 길어지면서 어디서 실패했는지 trace만으로는 의사결정 흐름이 잘 보이지 않는다.

이 사례에서 필요한 도구는 하나가 아니다.

| 문제 | 필요한 장치 | 이유 |
| --- | --- | --- |
| 모델 변경 후 품질 회귀 | eval | 같은 질문 세트로 이전/이후를 비교한다 |
| RAG source 누락 | RAG/tool-use eval | 답변 내용뿐 아니라 tool 선택과 source hit를 본다 |
| 단계가 고정된 workflow | graph | retrieve -> draft -> review 같은 상태 전이를 명시한다 |
| 역할 분리 | multi-agent | researcher, writer, reviewer의 책임을 분리한다 |
| 실제 권한이 필요한 행동 | human approval | 모델 판단이 아니라 사람의 책임 있는 승인이 필요하다 |

강사가 강조할 문장:

"eval, graph, multi-agent는 모두 agent를 더 복잡하게 만드는 도구입니다. 복잡하게 만들 이유가 없으면 쓰지 않습니다. 하지만 실패를 재현해야 하거나, 상태 전이가 운영 규칙이 되거나, 책임 경계가 갈라지는 순간에는 코드로 드러내야 합니다."

## 수업 전 준비

API key 없이 실행 가능한 예제:

```bash
uv run python examples/04_evals/evaluate_contract.py
uv run python examples/04_evals/rag_tool_use_eval.py
uv run python examples/04_evals/graph_workflow.py
uv run python examples/04_evals/human_approval_gate.py
```

API key가 필요한 예제:

```bash
uv run python examples/04_evals/compare_models.py
uv run python examples/04_evals/multi_agent_workflow.py
```

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-10분 | 3회차 복습 | 기능이 늘면 검증이 필요함을 연결 | 실패 가능성 말하기 |
| 10-35분 | Evals 기본 | Dataset, Case, Evaluator 이해 | eval 예제 실행 |
| 35-52분 | Custom evaluator | source marker 검증과 회귀 테스트 이해 | evaluator 수정 |
| 52-68분 | RAG/tool-use eval | retrieval, answer, tool call 정책을 나눠 평가 | `rag_tool_use_eval.py` 실행 |
| 68-78분 | 모델 전환 eval과 CI | 모델 변경을 dependency upgrade로 검증하는 방법 이해 | compare 모델 예제 읽기 |
| 78-83분 | 휴식/질문 | eval과 unit test 차이 정리 | 질문 |
| 83-96분 | Graph 기본 | 상태 전이가 복잡할 때 graph를 쓰는 이유 이해 | graph 예제 실행 |
| 96-108분 | Multi-agent | delegation, handoff, graph orchestration 구분 | parent/child 흐름 읽기 |
| 108-116분 | Human-in-the-loop gate | 사람이 승인해야 하는 tool call과 reviewer agent의 차이 이해 | approval 예제 실행 |
| 116-118분 | 통합 리뷰 | 어떤 상황에 무엇을 쓸지 판단 | 시나리오 분류 |
| 118-120분 | 다음 회차 연결 | durable execution 필요성 연결 | 회고 |

## 도입 이야기

수업을 이렇게 시작한다.

"지금까지 우리는 agent를 만들었습니다. RAG도 붙였고, CodeMode로 여러 tool 호출도 할 수 있습니다. 이제 진짜 질문은 이것입니다. 고쳤더니 좋아졌나요? 아니면 그럴듯해 보이지만 중요한 행동이 깨졌나요? AI 기능은 테스트 없이 운영하면 매번 감으로 배포하게 됩니다."

칠판에 다음을 쓴다.

```text
Prompt change = code change
Model change = dependency upgrade
RAG corpus change = data migration
Tool schema change = API contract change
```

핵심 메시지:

- eval은 "AI 답변을 완벽히 증명"하는 도구가 아니다.
- eval은 반복 가능한 품질 신호를 만드는 도구다.
- graph와 multi-agent는 기능 확장 도구지만, eval 없이는 복잡도만 늘 수 있다.

## Evals 개념 설명

### Dataset

`Dataset`은 평가할 case 모음이다. 각 case는 입력, 기대 출력, metadata, evaluator를 가질 수 있다.

초보자 설명:

"unit test에서 test case를 여러 개 두듯이, eval에서도 질문과 기대 행동을 여러 개 둡니다. 차이는 출력이 항상 exact match로만 평가되지 않는다는 점입니다."

### Case

case는 하나의 시나리오다.

예:

```python
Case(
    name="tool_definition",
    inputs="tool은 무엇인가요?",
    expected_output="Tool은 모델이 앱 코드에 요청하는 함수입니다. [source:lesson-01]",
)
```

수업에서는 문자열 함수로 시작한다. agent를 바로 평가하지 않는 이유는 초보자가 eval framework와 LLM 변동성을 동시에 배우면 혼란스럽기 때문이다.

### Evaluator

evaluator는 실제 output이 기대 조건을 만족하는지 판단한다.

종류:

- `EqualsExpected`: 정확히 같은지 확인
- `Contains`: 특정 문자열 포함 여부
- custom evaluator: domain-specific rule
- LLM-as-a-judge: 주관적 품질 평가
- span-based evaluator: tool 호출 여부 같은 behavior 평가

강사가 강조할 tradeoff:

- deterministic evaluator는 싸고 안정적이지만 유연하지 않다.
- LLM judge는 유연하지만 비용과 변동성이 있다.
- span/tool-call evaluator는 agent 행동 검증에 좋다.

## 라이브코딩 1: Deterministic Eval

파일: `examples/04_evals/evaluate_contract.py`

진행:

1. `deterministic_course_answer`가 agent 대신 쓰인 fake task임을 설명한다.
2. `Dataset`과 `Case`를 읽는다.
3. `EqualsExpected()`가 exact match를 확인하는 것을 설명한다.
4. `HasSourceMarker` custom evaluator를 읽는다.
5. 실행한다.

```bash
uv run python examples/04_evals/evaluate_contract.py
```

출력에서 볼 것:

- case별 assertions
- averages
- pass rate

말할 내용:

"이 예제는 LLM이 아닙니다. 그래서 너무 단순해 보입니다. 하지만 eval framework를 배울 때는 이 단순함이 좋습니다. 먼저 평가 구조를 이해하고, 나중에 task 함수를 agent 호출로 바꾸면 됩니다."

## 실습 1: Eval Case 추가

수강생 작업:

1. "DBOS는 무엇인가요?" case를 추가한다.
2. `deterministic_course_answer`에 DBOS 답변을 추가한다.
3. 일부러 source marker를 빼고 실패를 본다.
4. 다시 source marker를 넣고 통과시킨다.

강사 순회 체크:

- case 이름이 의미 있는가?
- expected output이 너무 장황하지 않은가?
- evaluator 실패 메시지가 읽을 만한가?

리뷰 포인트:

"eval은 실패해야 가치가 있습니다. 실패 메시지가 명확해야 다음 사람이 고칠 수 있습니다."

## RAG Eval과 Tool-use Eval

2회차에서는 RAG 실패를 눈으로 분류했다. 4회차에서는 그 분류를 평가 case로 만든다. RAG 품질은 하나의 점수로 보지 않고 최소한 retrieval, answer, source, hallucination을 나눠 본다.

| 평가 대상 | 질문 | deterministic 신호 예 |
| --- | --- | --- |
| Retrieval eval | 기대 source가 top-k 안에 들어왔는가? | `lesson-02`가 `retrieved_sources`에 있음 |
| Answer eval | 답변이 검색된 근거와 일치하는가? | source 밖 내용을 금지 |
| Source eval | 답변에 근거 source를 표시했는가? | `[source:lesson-02]` 포함 |
| Hallucination eval | 검색 결과에 없는 내용을 만들지 않았는가? | "모른다" policy 준수 |

Function calling과 tool use도 별도 평가 대상이다. 모델이 답변을 잘 써도 tool 선택이 틀리면 서비스는 깨진다.

| 평가 대상 | 질문 |
| --- | --- |
| Tool selection | 호출해야 하는 질문에서 올바른 tool을 호출했는가? |
| No-tool behavior | 일반 질문에서 불필요한 tool을 호출하지 않았는가? |
| Argument quality | tool arguments가 schema와 의도에 맞는가? |
| Safety policy | 위험한 write tool을 승인 없이 호출하지 않았는가? |
| Idempotency | retry가 같은 외부 write를 중복 실행하지 않게 설계됐는가? |

`examples/04_evals/rag_tool_use_eval.py`는 실제 LLM 없이 이 구조를 보여준다. task output은 답변 문자열 하나가 아니라 trace 형태다.

```python
TraceOutput(
    answer="...",
    retrieved_sources=("lesson-02",),
    tool_calls=("retrieve_course_docs",),
    refused=False,
)
```

Custom evaluator는 세 가지를 본다.

- `ExpectedSourcesHit`: 기대 source가 검색 결과에 있는가
- `ToolCallPolicy`: 필요한 tool은 호출했고 금지 tool은 호출하지 않았는가
- `RefusalPolicy`: 위험 요청을 거절하거나 승인 gate로 보냈는가

강사가 강조할 문장:

"RAG eval은 답변 문장만 평가하면 늦습니다. 먼저 검색이 맞았는지, 그 다음 답변이 근거를 따랐는지 봐야 합니다. Tool-use eval도 마찬가지입니다. 최종 답변이 그럴듯해도 잘못된 tool을 호출했다면 실패입니다."

## 라이브코딩 1-1: RAG와 Tool-use Eval

파일: `examples/04_evals/rag_tool_use_eval.py`

진행:

1. `TraceOutput`이 answer, retrieved sources, tool calls를 함께 담는 것을 설명한다.
2. `rag_question_retrieves_lesson_02` case를 읽는다.
3. `dangerous_write_requires_approval` case를 읽는다.
4. `ToolCallPolicy`의 forbidden tools를 읽는다.
5. 실행한다.

```bash
uv run python examples/04_evals/rag_tool_use_eval.py
```

수강생에게 물어볼 질문:

- "답변 문자열만 있으면 expected source hit를 평가할 수 있을까요?"
- "운영 DB 삭제 요청에서 기대 tool은 `delete_database`인가요, `request_human_approval`인가요?"
- "tool arguments까지 평가하려면 output trace에 무엇을 더 저장해야 할까요?"

## 실습 1-1: Tool-use Policy Case 추가

수강생 작업:

1. "그냥 RAG 개념을 설명해줘" case를 추가한다.
2. 기대 output에는 `tool_calls=()`를 둔다.
3. 일부러 task에서 `retrieve_course_docs`를 호출하게 바꾸고 실패를 확인한다.
4. 다시 tool 없이 답하게 고친다.

확장:

- `send_email` 같은 forbidden tool을 output에 넣고 실패를 확인한다.
- `tool_args`에 기대 query가 들어 있는지 검사하는 evaluator를 추가한다.

## 모델 전환을 Eval로 판단하기

모델 변경은 단순 설정 변경이 아니라 dependency upgrade다. `openai:gpt-5.1`에서 `openai:gpt-5.2`로 바꾸거나, 비싼 모델에서 저렴한 모델로 낮추거나, provider를 바꿀 때 "응답이 대충 괜찮아 보인다"로 결정하면 안 된다. 최소한 기존 eval dataset에서 pass rate, latency, token usage, 실패 유형을 비교해야 한다.

강사가 말할 핵심:

- 모델 전환은 기능 변경과 비용 변경을 동시에 만든다.
- 새 모델이 평균적으로 좋아도 특정 case가 깨질 수 있다.
- 평가 dataset은 "대표 질문"만이 아니라 "깨지면 안 되는 계약"을 포함해야 한다.
- 비용 절감을 위해 모델을 낮출 때는 pass rate 하락을 어느 정도까지 허용할지 미리 정해야 한다.

비교할 지표:

| 지표 | 왜 보는가 | 예 |
| --- | --- | --- |
| assertion pass rate | 필수 계약을 지키는지 확인 | source marker, required term |
| output quality score | 주관적 품질 비교 | LLM judge 또는 human review |
| requests/tool calls | agent loop가 길어졌는지 확인 | tool call 폭증 |
| input/output tokens | 비용과 latency 추정 | total_tokens |
| latency | 사용자 경험 확인 | p95 duration |
| failure cases | 어떤 질문이 깨졌는지 확인 | RAG 질문만 실패 |

`examples/04_evals/compare_models.py`는 이 흐름을 보여주는 작은 예제다. `EVAL_MODELS`에 후보 모델을 comma-separated로 넣고, 같은 dataset을 각 모델에 대해 실행한다.

```bash
EVAL_MODELS=openai:gpt-5.1,openai:gpt-5.2 \
EVAL_REPEAT=2 \
EVAL_MAX_CONCURRENCY=2 \
EVAL_MIN_ASSERTION_RATE=0.8 \
uv run python examples/04_evals/compare_models.py
```

이 예제는 `agent.override(model=model_name)`으로 같은 agent를 다른 모델에 대해 실행한다. task 함수 안에서는 `set_eval_attribute("model", model_name)`으로 어떤 모델이 사용됐는지 report에 남기고, `increment_eval_metric(...)`으로 token usage를 기록한다.

수업에서 보여줄 코드 포인트:

```python
with agent.override(model=model_name):
    report = dataset.evaluate_sync(
        make_task(model_name),
        name=model_name,
        repeat=repeat,
        max_concurrency=max_concurrency,
    )
```

`repeat`는 같은 case를 여러 번 실행해 stochastic variation을 보는 데 사용한다. `max_concurrency`는 provider rate limit과 비용 폭주를 막기 위해 둔다. 모델 비교를 CI나 release gate에 넣을 때는 무제한 동시 실행을 피한다.

모델 전환 승인 기준 예:

```text
새 모델로 전환하려면:
- assertion pass rate >= 95%
- critical case 실패 0개
- 평균 total_tokens가 기존 대비 120% 이하
- 사람이 검토한 샘플 10개 중 blocker 없음
```

이 기준은 기술적으로 정해지는 것이 아니라 제품과 비용 요구사항으로 정한다. 중요한 것은 모델 변경 PR 전에 기준을 먼저 합의하는 것이다.

## CI에서 Eval 운영하기

모든 eval을 모든 PR에서 돌리면 비용과 시간이 커진다. 따라서 eval을 계층화한다.

### PR마다 돌릴 cheap gate

API key 없이 빠르게 도는 deterministic eval, 문법 검증, lint를 실행한다.

```bash
uv run python examples/04_evals/evaluate_contract.py
uv run python -m compileall examples
uv run ruff check examples
```

이 저장소에는 예시 workflow가 있다.

```text
.github/workflows/evals.yml
```

`deterministic-evals` job은 pull request와 main push에서 실행된다. 이 job은 외부 LLM API를 호출하지 않으므로 빠르고 안정적이다.

### 수동/예약으로 돌릴 model-switch gate

실제 LLM API를 호출하는 모델 비교 eval은 비용이 있으므로 `workflow_dispatch`로 분리한다.

```yaml
model-switch-evals:
  if: github.event_name == 'workflow_dispatch'
```

운영에서는 다음 시점에 실행한다.

- 모델 버전 변경 PR
- provider 변경 PR
- 중요한 prompt/instructions 변경
- RAG chunking/embedding model 변경
- tool schema 또는 approval policy 변경
- release 전 nightly 또는 weekly regression

CI에서 model eval을 돌릴 때 주의할 점:

- API key는 GitHub Actions secret에 둔다.
- `max_concurrency`를 낮춰 rate limit을 피한다.
- pass rate threshold를 환경변수로 둔다.
- 실패 case 이름과 출력 일부를 artifact로 남긴다.
- flaky case는 삭제하지 말고 원인을 분류한다. dataset이 나쁜지, evaluator가 불안정한지, 모델이 불안정한지 구분한다.

### Dataset 관리

Pydantic Evals는 dataset을 YAML/JSON으로 저장할 수 있다. 운영 repo에서는 eval case를 코드 안에만 두기보다 `evals/*.yaml` 같은 파일로 version control하는 편이 좋다.

장점:

- PM/기획자도 case를 읽고 리뷰하기 쉽다.
- PR diff에서 어떤 품질 기준이 바뀌었는지 보인다.
- schema file을 같이 두면 IDE validation을 받을 수 있다.

교육 예제는 단순화를 위해 dataset을 Python 코드에 직접 둔다. 하지만 실무 프로젝트에서는 다음 형태를 권장한다.

```text
evals/
  course_qa.yaml
  course_qa_schema.json
examples/04_evals/
  run_course_eval.py
```

### CI에서 실패를 해석하는 법

Eval 실패는 바로 "모델이 나쁘다"는 뜻이 아니다. 다음 순서로 본다.

1. case가 현재 제품 요구사항을 잘 표현하는가?
2. evaluator가 너무 엄격하거나 너무 느슨하지 않은가?
3. model output이 실제로 나쁜가, 표현만 다른가?
4. prompt/tool/RAG data 변경 중 무엇이 원인인가?
5. threshold를 바꿔야 하는가, 코드를 고쳐야 하는가?

강사가 강조할 문장:

"CI eval은 사람의 판단을 없애는 것이 아니라, 사람이 봐야 할 실패를 빨리 찾아주는 장치입니다."

## Graph 개념 설명

Pydantic Graph는 typed async graph/state machine library다. Pydantic AI의 기본 agent보다 어렵고, 모든 workflow에 필요한 도구가 아니다.

수업에서 분명히 말할 문장:

"Graph는 기본 선택지가 아닙니다. 단순히 agent가 tool 두 개 호출하는 정도라면 graph가 과합니다. 하지만 상태 전이, 분기, review, retry, persistence가 명확해야 하면 graph가 도움이 됩니다."

Graph가 필요한 신호:

- 단계가 명확하고 순서가 중요하다.
- 중간 state를 저장하거나 시각화해야 한다.
- 분기와 join이 많다.
- agent 여러 개를 deterministic control flow로 묶어야 한다.

Graph가 과한 신호:

- prompt 하나와 tool 한두 개면 충분하다.
- 단계가 자주 바뀌고 아직 탐색 중이다.
- 팀이 Python generics와 async에 익숙하지 않다.

### LangGraph와 Pydantic Graph 구분

LangGraph와 Pydantic Graph는 둘 다 "graph"라는 단어를 쓰지만 같은 층위의 도구가 아니다.

LangGraph 공식 문서는 LangGraph를 long-running, stateful agent를 만들고 운영하기 위한 low-level orchestration framework/runtime으로 설명한다. 핵심은 durable execution, persistence, streaming, human-in-the-loop, memory, LangSmith 기반 디버깅이다. LangChain agent도 LangGraph 위에 구축되어 durable execution과 human-in-the-loop 같은 runtime 기능을 활용한다.

Pydantic Graph는 Pydantic AI와 함께 제공되는 typed async graph/state machine library다. Python type hint로 node, edge, state, dependency를 표현하고, 복잡한 control flow를 명시하는 데 초점이 있다. Pydantic 공식 문서도 graph를 기본 선택지로 두지 않고, 일반 agent나 multi-agent 패턴으로 충분한지 먼저 보라고 설명한다.

수업에서는 이렇게 구분한다.

| 질문 | LangGraph | Pydantic Graph |
| --- | --- | --- |
| 주된 층위 | orchestration runtime | typed graph/state machine library |
| 강한 문제 | 오래 실행되는 stateful agent, persistence, HITL, streaming, deployment/observability stack | Python 타입으로 workflow 상태 전이와 분기 명시 |
| 생태계 연결 | LangChain, LangSmith, LangGraph Platform | Pydantic AI, Pydantic Evals, Logfire, DBOS/Temporal 등 durable integration |
| 이 교안에서의 위치 | 비교 대상으로 설명 | 4회차 live coding 대상 |

강사가 강조할 문장:

"LangGraph는 production orchestration runtime에 가깝고, Pydantic Graph는 typed Python graph를 통해 control flow를 설명하기 좋은 도구입니다. 이 수업은 4회차에서 graph 개념을 작게 익히고, 5회차에서 DBOS로 durable execution을 별도 주제로 다룹니다."

## 라이브코딩 2: Typed Graph

파일: `examples/04_evals/graph_workflow.py`

진행:

1. `Retrieve`, `Draft`, `Review` node를 읽는다.
2. 각 node의 `run` return type이 다음 node를 나타낸다는 점을 설명한다.
3. `End[str]`가 graph 종료를 의미한다고 설명한다.
4. `GraphBuilder(input_type=str, output_type=str)`를 설명한다.
5. `render()`로 Mermaid diagram을 출력한다.

수강생에게 물어볼 질문:

- "이 예제에서 RAG 검색은 어느 node에 들어갈까요?"
- "review가 실패하면 어디로 되돌릴 수 있을까요?"
- "이 workflow를 그냥 함수 3개로 만들면 안 될까요?"

답변 방향:

- 단순하면 함수 3개도 좋다.
- graph는 workflow가 커지고 시각화/분기/상태 관리가 필요해질 때 쓴다.

## 실습 2: Review 조건 추가

수강생 작업:

1. `Review` node에서 답변 길이가 30자보다 짧으면 reject한다.
2. reject message를 명확하게 만든다.
3. `course_graph.render()` 결과를 확인한다.

확장:

- `Review`가 실패하면 `Draft`로 되돌아가게 return type을 바꿔본다.
- 이때 무한 루프 위험을 어떻게 막을지 토론한다.

강사 정리:

"Graph를 쓰기 시작하면 retry count, state mutation, persistence 같은 운영 문제가 바로 생깁니다. 그래서 graph는 필요한 경우에만 사용해야 합니다."

## Multi-agent 개념 설명

Pydantic AI 문서의 multi-agent 복잡도는 대략 다음 단계로 볼 수 있다.

1. single agent workflow
2. agent delegation
3. programmatic handoff
4. graph-based control flow
5. deep agent

이번 수업에서는 agent delegation을 다룬다.

Agent delegation:

- parent agent가 tool 안에서 child agent를 호출한다.
- child agent는 별도 message history를 가진다.
- parent의 `ctx.usage`를 넘겨 usage limit을 공유할 수 있다.

좋은 사용처:

- 역할이 명확히 나뉜다. 예: researcher, writer, reviewer.
- child agent가 다른 instructions/output schema를 가진다.
- parent context를 줄이고 싶다.

주의:

- agent가 많아지면 tracing과 eval이 어려워진다.
- 실패를 parent가 어떻게 처리할지 정해야 한다.
- token budget이 빠르게 늘 수 있다.

## Human-in-the-loop는 어디에 넣는가

Human-in-the-loop는 두 회차에 걸쳐 다룬다.

4회차에서는 설계 패턴으로 다룬다. "이 결정을 모델이나 reviewer agent에게 맡겨도 되는가, 아니면 실제 사람이 승인해야 하는가"를 구분하게 한다. 예를 들어 문장 품질 검토는 reviewer agent가 할 수 있지만, 공지 발행, 이메일 발송, 계정 삭제, 결제, 개인정보 열람 같은 행동은 사람이 승인해야 한다.

5회차에서는 운영 구현으로 다룬다. 사람이 승인할 때까지 실행이 멈추면 HTTP request 하나 안에서 기다릴 수 없다. 승인 요청, message history, tool call id, 승인/거절 결과를 저장하고, 나중에 workflow를 이어가야 한다. 이 지점에서 durable execution이 필요하다.

구분:

| 상황 | 4회차 관점 | 5회차 관점 |
| --- | --- | --- |
| 초안 품질 검토 | reviewer agent 또는 graph review node | durable까지는 보통 불필요 |
| 공지 발행 승인 | human approval gate 설계 | 승인 대기/재개 상태 저장 필요 |
| 외부 시스템 write | approval이 필요한 tool로 모델링 | idempotency와 durable step 필요 |
| 며칠 뒤 승인 | graph만으로 부족 | durable workflow가 적합 |

강사가 강조할 문장:

"Human-in-the-loop는 multi-agent의 한 종류가 아닙니다. 사람은 더 똑똑한 reviewer agent가 아니라 책임과 권한을 가진 actor입니다. 4회차에서는 어디에 사람을 넣을지 설계하고, 5회차에서는 사람이 늦게 응답해도 상태를 잃지 않는 방법을 봅니다."

## 라이브코딩 3: Agent Delegation

파일: `examples/04_evals/multi_agent_workflow.py`

진행:

1. `researcher` agent와 `writer` agent instructions를 비교한다.
2. `@writer.tool` 안에서 `researcher.run(...)`을 호출하는 부분을 읽는다.
3. `usage=ctx.usage`가 왜 중요한지 설명한다.
4. `UsageLimits`를 낮춰 실패 가능성을 설명한다.

말할 내용:

"child agent는 함수처럼 호출되지만 내부적으로는 또 다른 model run입니다. 비용, latency, failure mode가 늘어납니다. 그래서 역할 분리가 정말 필요한지 먼저 물어봐야 합니다."

## 실습 3: Reviewer 추가 설계

수강생 작업:

1. `reviewer` agent를 추가한다.
2. writer가 최종 답변을 쓰기 전에 reviewer에게 "근거가 충분한가"를 묻게 설계한다.
3. 구현이 어렵다면 pseudocode로 적는다.

강사가 기대하는 구조:

```text
writer agent
  -> gather_course_facts tool
      -> researcher agent
  -> review_draft tool
      -> reviewer agent
  -> final answer
```

토론:

- reviewer는 parent의 tool이어야 하나, graph node여야 하나?
- reviewer 실패 시 parent가 재작성해야 하나?
- eval은 writer 최종 답변만 볼 것인가, reviewer 판단도 볼 것인가?

## 라이브코딩 4: Human Approval Gate

파일: `examples/04_evals/human_approval_gate.py`

이 예제는 실제 LLM API를 호출하지 않고 `TestModel`을 사용한다. 목적은 모델 품질이 아니라 승인 흐름의 모양을 보는 것이다.

진행:

1. `publish_course_notice`와 `delete_course_notice`에 `requires_approval=True`가 붙은 것을 읽는다.
2. 첫 번째 `agent.run_sync(...)`가 최종 문자열이 아니라 `DeferredToolRequests`를 반환하는 것을 확인한다.
3. `requests.approvals`에 tool name, args, tool call id가 들어 있음을 확인한다.
4. 공지 발행은 승인하고 삭제는 `ToolDenied`로 거절한다.
5. `message_history=messages`와 `deferred_tool_results=approval_results`로 두 번째 run을 이어간다.

핵심 코드:

```python
first_result = agent.run_sync("공지 발행과 삭제를 모두 처리해줘.")
messages = first_result.all_messages()
requests = first_result.output

approval_results = DeferredToolResults()
approval_results.approvals[call.tool_call_id] = True

resumed_result = agent.run_sync(
    "승인 결과를 반영해서 최종 상태를 정리해줘.",
    message_history=messages,
    deferred_tool_results=approval_results,
)
```

수강생에게 물어볼 질문:

- 승인 화면에는 어떤 정보를 보여줘야 하는가?
- 승인자가 tool args를 수정할 수 있게 해야 하는가?
- 거절 메시지는 모델에게 그대로 보여줘도 되는가?
- tool call id와 message history는 어디에 저장해야 하는가?

마지막 질문이 5회차 durable execution으로 넘어가는 핵심이다.

## 시나리오 분류 활동

마지막 10분에 다음 시나리오를 어떤 도구로 풀지 분류한다.

1. "답변에 source가 반드시 포함되어야 한다."
   - eval
2. "모델을 `gpt-5.1`에서 `gpt-5.2`로 바꾸고 싶다."
   - model-switch eval + CI/manual gate
3. "RAG 답변이 틀렸는데 검색이 틀린 건지 답변 생성이 틀린 건지 모르겠다."
   - RAG retrieval eval + answer eval 분리
4. "위험한 write tool이 승인 없이 호출되지 않는지 확인하고 싶다."
   - tool-use policy eval + human approval gate
5. "검색, 초안, 검토 단계가 고정되어 있고 시각화가 필요하다."
   - graph
6. "법률 검토와 문장 작성 역할을 분리하고 싶다."
   - multi-agent
7. "tool 호출이 20개라 latency가 크다."
   - CodeMode
8. "서버가 죽어도 긴 작업을 이어가야 한다."
   - durable execution
9. "공지 발행은 모델이 제안하되 사람이 승인해야 한다."
   - human-in-the-loop approval gate + durable execution

이 활동은 5회차 DBOS로 넘어가는 다리다.

## 흔한 오해와 정리

오해 1: "eval을 만들면 AI 품질이 보장된다."

정리: 아니다. eval은 선택한 case와 evaluator에 대한 신호를 준다. 중요한 실패를 case로 계속 추가해야 한다.

오해 2: "Graph가 있으면 multi-agent보다 항상 낫다."

정리: 아니다. Graph는 control flow 도구이고, multi-agent는 역할 분리 패턴이다. 함께 쓸 수도 있다.

오해 3: "agent를 많이 나누면 더 똑똑해진다."

정리: 아니다. 더 비싸지고 느려지고 디버깅이 어려워질 수 있다. 역할 경계가 명확할 때만 나눈다.

## 미니 리뷰 질문

1. deterministic evaluator와 LLM judge의 장단점은 무엇인가요?
2. Graph가 과한 경우는 어떤 경우인가요?
3. agent delegation에서 `ctx.usage`를 넘기는 이유는 무엇인가요?
4. reviewer agent를 추가하면 어떤 eval이 더 필요할까요?
5. prompt 변경을 code change로 봐야 하는 이유는 무엇인가요?
6. 모델 변경을 PR에서 바로 merge하지 않고 eval gate로 보는 이유는 무엇인가요?
7. 모든 eval을 PR마다 돌리지 않는 이유는 무엇인가요?
8. reviewer agent와 human approval gate는 무엇이 다른가요?
9. RAG eval에서 retrieval eval과 answer eval을 나누는 이유는 무엇인가요?
10. Tool-use eval에서 forbidden tool을 별도로 검사해야 하는 이유는 무엇인가요?

## 다음 회차 연결

"오늘 우리는 workflow를 복잡하게 만들었습니다. 복잡한 workflow는 시간이 오래 걸리고, 중간에 API 실패나 서버 재시작을 만날 수 있습니다. 그냥 retry하면 처음부터 다시 할 수도 있고, side effect가 중복될 수도 있습니다. 5회차에서는 DBOS로 agent run을 durable workflow로 감싸고, FastAPI 챗봇으로 사용자에게 연결합니다."

## 강사용 완료 기준

- 수강생이 Dataset/Case/Evaluator를 구분했다.
- custom evaluator를 수정하거나 실패 케이스를 확인했다.
- RAG source hit와 tool-use policy를 별도 eval로 설명했다.
- 모델 전환을 eval dataset, pass rate, usage metric으로 판단하는 흐름을 이해했다.
- PR용 cheap eval과 수동/예약 model eval을 분리하는 CI 전략을 설명했다.
- Graph를 기본 선택지가 아니라 고급 control flow 도구로 이해했다.
- multi-agent delegation의 비용과 usage limit 문제를 설명했다.
- human approval이 필요한 tool call을 reviewer agent와 구분했다.
- 5회차 durable execution 필요성이 연결됐다.
