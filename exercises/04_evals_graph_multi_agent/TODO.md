# 4회차 실습 TODO

## 시작 파일

- `examples/04_evals/evaluate_contract.py`
- `examples/04_evals/rag_tool_use_eval.py`
- `examples/04_evals/compare_models.py`
- `examples/04_evals/graph_workflow.py`
- `examples/04_evals/multi_agent_workflow.py`
- `examples/04_evals/human_approval_gate.py`

## 과제 A: Eval 추가

1. "DBOS는 무엇인가요?" case를 추가한다.
2. `deterministic_course_answer`에 DBOS 답변을 추가한다.
3. source marker가 빠지면 정말 실패하는지 일부러 확인한다.

## 과제 B: RAG / Tool-use Eval

1. `examples/04_evals/rag_tool_use_eval.py`를 실행한다.
2. `rag_question_retrieves_lesson_02` case가 기대하는 source가 무엇인지 확인한다.
3. `dangerous_write_requires_approval` case가 `delete_database`가 아니라 `request_human_approval`을 기대하는 이유를 적는다.
4. 일반 설명 질문 case를 하나 추가하고 기대값으로 `tool_calls=()`를 둔다.
5. 일부러 task가 `retrieve_course_docs`를 호출하게 바꿔서 실패하는지 확인한다.
6. `ToolCallPolicy`의 forbidden tool 목록에 `charge_credit_card`를 추가한다.

## 과제 C: Graph 변경

1. `Review` node에서 답변이 너무 짧으면 reject하게 한다.
2. `course_graph.render()`가 출력한 Mermaid diagram을 슬라이드에 붙인다.

## 과제 D: 모델 전환 Eval 설계

1. `examples/04_evals/compare_models.py`를 읽는다.
2. `EVAL_MODELS`에 비교할 모델 2개를 넣어 실행하는 명령을 작성한다.
3. 모델 전환을 승인할 기준을 3개 적는다.
4. `EVAL_MIN_ASSERTION_RATE`를 0.8에서 0.95로 올리면 어떤 PR이 막힐지 토론한다.

```bash
EVAL_MODELS=openai:gpt-5.4,openai:gpt-5.5 \
EVAL_REPEAT=2 \
EVAL_MIN_ASSERTION_RATE=0.95 \
uv run python examples/04_evals/compare_models.py
```

## 과제 E: CI Gate 분리

1. `.github/workflows/evals.yml`을 읽는다.
2. PR마다 실행되는 job과 수동으로 실행하는 job을 구분한다.
3. 실제 LLM API를 호출하는 eval을 PR마다 돌리지 않는 이유를 적는다.
4. 모델 변경 PR에 반드시 첨부해야 할 eval 결과 항목을 정한다.

## 과제 F: Multi-agent 확장

1. reviewer agent를 추가한다.
2. writer가 researcher 결과를 받은 뒤, reviewer에게 검토를 요청하게 한다.
3. usage limit을 낮춰서 실패 케이스를 관찰한다.

## 과제 G: Human-in-the-loop Gate

1. `examples/04_evals/human_approval_gate.py`를 실행한다.
2. `publish_course_notice`는 승인되고 `delete_course_notice`는 거절되는 흐름을 읽는다.
3. 승인 화면에 보여줘야 할 필드를 적는다.
4. tool call id, 승인자, 승인 시각, 승인/거절 사유를 어디에 저장할지 설계한다.
5. reviewer agent로 대신해도 되는 검토와, 반드시 사람이 승인해야 하는 검토를 구분한다.

## 통과 기준

- eval report의 assertion pass rate가 100%다.
- RAG eval에서 retrieval source hit와 answer quality를 분리해야 하는 이유를 설명할 수 있다.
- Tool-use eval에서 required tool과 forbidden tool을 구분할 수 있다.
- 모델 전환 시 pass rate, token usage, critical case 실패 여부를 함께 비교해야 한다는 점을 설명할 수 있다.
- CI에서 deterministic eval과 model-switch eval을 분리해야 하는 이유를 설명할 수 있다.
- graph가 retrieve -> draft -> review 순서로 실행된다.
- multi-agent 예제에서 parent와 child usage가 함께 집계된다.
- human approval gate와 reviewer agent의 차이를 설명할 수 있다.
