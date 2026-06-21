# 4회차 슬라이드: Evals, Graph, Multi-agent

## 오늘의 결과물

- Pydantic Evals dataset
- custom evaluator
- RAG/tool-use policy eval
- typed graph workflow
- agent delegation 예제
- human approval gate

## 왜 Eval인가

- prompt 변경은 코드 변경이다.
- model 변경은 dependency upgrade다.
- RAG 데이터 변경은 search behavior 변경이다.

## Dataset

```python
Dataset(
    cases=[Case(inputs="...", expected_output="...")],
    evaluators=[...],
)
```

## Evaluator 종류

- deterministic check
- expected output comparison
- LLM-as-a-judge
- span/tool-call based check

## RAG Eval

답변만 보고 판단하면 이미 늦다.

- Retrieval: 기대 source가 top-k에 있는가?
- Answer: 근거와 일치하는가?
- Source: source marker가 있는가?
- Hallucination: 근거 밖 내용을 만들지 않는가?

## Tool-use Eval

- 필요한 tool을 호출했는가?
- 불필요한 tool을 호출하지 않았는가?
- arguments가 schema와 의도에 맞는가?
- 위험한 write tool을 approval 없이 호출하지 않는가?

## Graph는 언제 쓰나

- 상태 전이가 명확하다.
- 분기와 재시도가 많다.
- 시각화와 replay가 필요하다.

Graph는 처음부터 꺼낼 선택지가 아니다.

## Multi-agent 패턴

- agent delegation
- programmatic handoff
- graph-based orchestration
- deep agent

## Human-in-the-loop

- reviewer agent는 품질 신호를 준다.
- human approval은 책임 있는 actor의 승인이다.
- 위험한 tool call은 `requires_approval=True`로 멈춘다.
- 승인/거절 후 `DeferredToolResults`로 이어간다.

4회차: 어디에 사람을 넣을지 설계

5회차: 승인 대기와 재개를 durable하게 구현

## 실무 질문

- token budget은 parent와 child가 공유하는가?
- 실패한 sub-agent 결과를 parent가 어떻게 처리하는가?
- eval은 어느 단계의 품질을 측정하는가?
- 이 결정은 reviewer agent로 충분한가, 사람이 승인해야 하는가?
- retrieval 실패와 generation 실패를 어떻게 구분할 것인가?
- forbidden tool 호출을 어떤 eval로 막을 것인가?
