# 3회차 실습 TODO

## 시작 파일

- `examples/03_monty/code_mode_agent.py`

## 과제

1. `get_lesson_minutes`와 `get_lesson_title`만 써서 총 시간을 계산하도록 prompt를 바꾼다.
2. `CodeMode(tools=["list_lessons", "get_lesson_minutes", "get_lesson_title"])`로 selector를 명시한다.
3. 다음 위험한 tool을 추가하되, sandbox selector에는 넣지 않는다.

```python
@agent.tool_plain
def delete_lesson(lesson_id: str) -> str:
    """Dangerous example: delete a lesson."""
    return f"deleted {lesson_id}"
```

## 토론 질문

- 이 tool은 실제 운영에서 어떤 approval을 거쳐야 하는가?
- sandbox에 넣지 않더라도 이 tool이 위험한 이유는 무엇인가?
- 모델이 작성한 코드가 실패했을 때, 그 로그는 어디에 남겨야 하는가?

## 통과 기준

- agent가 총 750분을 계산한다.
- 삭제 tool은 `run_code` 안에서 호출되지 않는다.
- 위험한 side effect tool은 따로 관리해야 한다는 점을 설명할 수 있다.

