# 1회차 슬라이드: Pydantic AI 기본

## 오늘의 결과물

- 가장 작은 Pydantic AI agent
- Logfire로 관측되는 agent run
- tool을 호출하는 agent
- deps와 structured output을 가진 agent

## 왜 Pydantic AI인가

- Python type hint와 Pydantic validation을 agent 경계에 사용
- FastAPI와 비슷한 개발자 경험
- tools, output, deps, evals, graph, durable execution을 한 stack에서 연결

## Mental Model

LLM은 답변을 생성한다.

Agent는 그 생성 앞뒤에 애플리케이션 계약을 씌운다.

Tool은 LLM이 애플리케이션에 요청할 수 있는 함수다.

## Logfire

```python
import logfire

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()
```

- agent run trace
- model request span
- tool call span
- token usage
- 실패 지점 확인

## 최소 Agent

```python
from pydantic_ai import Agent

agent = Agent("openai:gpt-5.2", instructions="간결하게 답하세요.")
result = agent.run_sync("Pydantic AI를 한 문장으로 설명해줘.")
print(result.output)
```

실습에서는 0회차에서 정한 `COURSE_MODEL`을 사용한다.

## Tool

- 함수 이름, 타입 힌트, docstring이 tool schema가 된다.
- 모델은 tool을 직접 실행하지 않는다.
- 애플리케이션 코드가 tool call을 받아 실행한다.

## RunContext와 Deps

- 요청 단위 자원을 안전하게 넘긴다.
- DB connection, API client, user id, tenant id를 전역으로 두지 않는다.
- 테스트에서 fake deps로 바꾸기 쉽다.

## Structured Output

- 답변을 Pydantic 모델로 검증한다.
- UI/API 계약으로 바로 쓸 수 있다.
- 실패 시 retry와 validation feedback의 기반이 된다.

## 실무 질문

- 이 실행을 trace로 설명할 수 있는가?
- 이 tool은 누구 권한으로 실행되는가?
- timeout과 retry는 어디에 있는가?
- tool 결과가 너무 크면 어떻게 줄일 것인가?
- output schema가 바뀌면 클라이언트 영향은 무엇인가?
