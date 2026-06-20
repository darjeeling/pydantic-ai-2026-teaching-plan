# 3회차 실습 TODO

## 시작 파일

- `examples/03_monty/code_mode_agent.py`

## 과제

1. `get_lesson_minutes`와 `get_lesson_title`만 사용해 총 시간을 계산하게 prompt를 바꾼다.
2. `CodeMode(tools=["list_lessons", "get_lesson_minutes", "get_lesson_title"])`로 명시적 selector를 사용한다.
3. 다음 위험한 tool을 추가하되, sandbox selector에서는 제외한다.

```python
@agent.tool_plain
def delete_lesson(lesson_id: str) -> str:
    """Dangerous example: delete a lesson."""
    return f"deleted {lesson_id}"
```

## 토론 질문

- 이 tool은 실제 운영에서 어떤 approval이 필요한가?
- sandbox 안에 들어가지 않아도 위험한 이유는 무엇인가?
- 모델이 작성한 코드의 실패 로그는 어디에 남겨야 하는가?

## 통과 기준

- agent가 총 750분을 계산한다.
- 삭제 tool은 `run_code` 안에서 호출할 수 없다.
- 위험한 side effect tool을 별도 관리해야 한다는 설명을 할 수 있다.

