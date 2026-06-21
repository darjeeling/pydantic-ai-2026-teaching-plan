# 1회차 실습 TODO

## 시작 파일

- `examples/01_basics/httpx_raw_api_log.py`
- `examples/01_basics/logfire_agent.py`
- `examples/01_basics/tool_agent.py`

## 과제

1. `httpx_raw_api_log.py`를 실행해서 raw HTTP request/response가 파일에 남는 것을 확인한다.
2. raw 로그에 prompt와 response body가 그대로 남는다는 점을 확인하고, 왜 이 파일을 공유하면 안 되는지 메모한다.
3. `tool_agent.py`에서 `list_lesson_ids`를 대신할, lesson id와 title을 함께 반환하는 `list_lessons` tool을 만든다.
4. 존재하지 않는 lesson id를 물어보면 agent가 지어내지 않고 "교안에 없음"이라고 답하게 한다.
5. `LessonAnswer`에 `next_action: str` 필드를 추가한다.
6. 안전한 로컬 API 호출 로그에서 실제 provider 호출이 남았는지 확인한다.
7. Logfire trace에서 tool call이 실제로 일어났는지 확인한다.
8. VS Code Debugger나 `breakpoint()`로 `read_lesson` 안에서 `lesson_id`와 `ctx.deps.lessons` 값을 들여다본다.
9. 질문을 다음처럼 바꿔서 실행한다.

```text
Monty를 배우려면 어떤 회차를 보면 되고, 다음에는 무엇을 해야 하나요?
```

로그 확인:

```bash
tail -n 20 logs/httpx-raw-api.log
tail -n 30 logs/api-calls.log
```

## 통과 기준

- 출력 JSON에 관련 lesson id가 들어 있다.
- `confidence`가 0과 1 사이 값이다.
- `next_action`이 수강생이 바로 할 수 있는 행동으로 읽힌다.
- `logs/httpx-raw-api.log`에서 raw request/response body를 확인했다.
- `logs/api-calls.log`에서 `tool_agent`의 `agent.run start/done` 로그를 확인했다.
- Logfire를 쓸 수 있는 환경이면 agent run과 tool call trace를 확인했다.
- debugger나 `pdb`로 tool 인자와 deps 값을 직접 확인했다.
