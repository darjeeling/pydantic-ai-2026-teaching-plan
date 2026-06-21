# 3회차: Monty와 CodeMode로 Agent 격리하기

## 2시간 목표

이 회차의 목표는 수강생이 "LLM이 코드를 쓰게 하면 강력하지만, host에서 그대로 실행하면 안 된다"는 감각을 갖게 하는 것이다. 동시에 CodeMode를 멋진 기능이 아니라 실용적 패턴으로 받아들이게 한다. 여러 tool을 호출할 때 생기는 모델 왕복을 줄이고, tool 결과를 로컬에서 계산으로 처리하기 위한 도구라는 자리매김이다.

완성 결과물은 `examples/03_monty/code_mode_agent.py`를 기반으로 한 course planning assistant다. 이 assistant는 lesson 목록과 시간 정보를 tool로 가져오고, CodeMode를 통해 총 시간 계산과 필터링을 수행한다.

## 사례로 시작하기: "모델이 코드를 잘 짰는데 왜 위험한가"

학생에게 이런 요청을 먼저 보여 준다.

```text
lessons 폴더를 읽어서 각 회차의 예상 수업 시간을 표로 만들고,
2시간 30분을 넘는 회차가 있으면 이유를 정리해줘.
```

이 요청은 모델에게 code execution을 맡기면 잘 풀린다. 파일을 읽고, Markdown에서 시간표를 찾고, 숫자를 합산하고, 표로 정리하면 된다. 문제는 같은 능력이 곧 위험이 된다는 점이다. 파일을 읽고 숫자를 합산하는 코드를 쓸 수 있다는 건, 그 코드가 다른 파일도 읽고 다른 곳으로 보낼 수 있다는 뜻이기도 하다. 모델이 host Python에서 자유롭게 실행된다면 다음 행동도 할 수 있다.

- repo 밖의 파일을 읽는다.
- `.env`나 credential 파일을 열어 본다.
- 네트워크로 내용을 전송한다.
- 실수로 파일을 수정하거나 삭제한다.
- 무한 루프나 큰 메모리 할당으로 실행 환경을 망가뜨린다.

우리가 의도한 동작과 위험한 동작이 같은 "코드 실행" 능력에서 나온다는 게 핵심이다. 그래서 질문은 "모델에게 코드를 쓰게 할 것인가"가 아니라 "어떤 capability 안에서 코드를 실행하게 할 것인가"로 바뀐다. Monty와 CodeMode는 모델의 계산 능력을 쓰되, host와 직접 연결되는 표면을 줄이기 위한 장치다.

강사는 이 구분을 짚어 준다.

| 방식 | 적합한 경우 | 위험 |
| --- | --- | --- |
| 일반 tool calling | 명확한 함수 1~2개를 호출하면 되는 경우 | 호출 횟수가 많아지면 느리고 비싸다 |
| CodeMode | 여러 tool 결과를 조합하고 로컬 계산이 필요한 경우 | 허용 capability 설계가 약하면 위험 행동이 가능하다 |
| host Python 직접 실행 | 신뢰된 개발자 작업 | LLM 생성 코드를 그대로 실행하면 안 된다 |

## 수업 전 준비

```bash
uv run python examples/03_monty/code_mode_agent.py
```

이 예제는 OpenAI API key가 필요하다. key가 없는 수강생은 CodeMode README와 예제 코드를 읽는 쪽으로 따라오고, 강사가 실행 결과와 trace를 화면으로 보여 준다. WSL 환경 주의는 0회차를 따른다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-10분 | RAG 복습 | tool 호출 수 증가 문제를 떠올리게 한다 | RAG가 호출하는 tool 말하기 |
| 10-25분 | 문제 제기 | 모델 작성 코드를 host에서 실행하는 위험 이해 | 위험한 코드 예측 |
| 25-40분 | Monty 개념 | 제한된 Python sandbox와 host boundary 이해 | 제한 사항 읽기 |
| 40-60분 | CodeMode 개념 | 여러 tool 호출을 `run_code` 하나로 묶는 흐름 이해 | 일반 tool calling과 비교 |
| 60-70분 | 휴식/질문 | sandbox와 container 차이 정리 | 질문 |
| 70-90분 | 예제 라이브코딩 | `capabilities=[CodeMode()]`와 tool wrapping 이해 | 예제 수정 |
| 90-110분 | 실습 | selector와 위험 tool 제외 | 실습 |
| 110-118분 | 운영 리뷰 | approval, idempotency, observability 토론 | 사례 토론 |
| 118-120분 | 다음 회차 연결 | eval과 graph 필요성 연결 | 회고 |

## 도입 이야기

수업은 이렇게 연다.

"RAG에서 검색을 한 번만 하면 단순해요. 그런데 agent가 문서 10개를 검색하고, 각각의 상세 정보를 가져오고, 중복을 제거하고, 점수순으로 정렬해야 한다면 어떨까요? 전통적인 tool calling은 모델 왕복이 자꾸 늘어납니다. 모델이 Python으로 '이 tool들을 병렬로 호출하고 결과를 정렬해'라고 쓰면 더 빠를 수 있어요. 하지만 그 코드를 우리 서버에서 그대로 실행하면 그게 바로 보안 사고죠."

칠판에 두 줄을 쓴다.

```text
Power: model-written code can orchestrate many tools.
Risk: model-written code must not run with host privileges.
```

핵심 메시지:

- CodeMode는 tool orchestration 비용을 줄이는 패턴이다.
- Monty는 모델 작성 코드가 host를 마음대로 만지지 못하게 하는 sandbox다.
- sandbox가 있어도 위험한 tool 설계를 대신 해결해주지는 않는다.

## 개념 설명 스크립트

### 왜 코드 실행이 필요한가

일반 tool calling 흐름:

```text
model -> call tool A -> model -> call tool B -> model -> call tool C -> model -> final
```

CodeMode 흐름:

```text
model -> run_code("call A, B, C, filter, aggregate") -> model -> final
```

좋은 사용처:

- 여러 API 결과를 병렬로 가져오기
- 검색 결과를 조건으로 필터링
- 숫자 계산, 정렬, grouping
- 큰 tool 결과에서 필요한 필드만 추출

나쁜 사용처:

- 작은 질문 하나에 괜히 code mode 사용
- side effect가 큰 tool을 자동 실행
- 모델이 business rule을 임의로 구현하게 방치

### Monty

Monty는 Rust로 작성된 제한된 Python interpreter다. 핵심은 Python처럼 보이는 코드를 실행하되 host Python 권한을 그대로 내주지는 않는다는 데 있다.

강사는 다음 제한을 짚어 준다.

- host filesystem 기본 접근 없음
- env variable 기본 접근 없음
- network 기본 접근 없음
- third-party import 없음
- class 정의 등 일부 Python 기능 제한
- resource limit 지원
- host가 허용한 external function만 호출 가능

초보자에게는 container와 비교해 준다.

- container sandbox: OS/process level 격리, 강력하지만 무겁고 운영 복잡도가 따라온다.
- Monty: LLM tool orchestration에 필요한 제한된 Python 실행을 가볍게 제공한다.

여기서 한 번 못을 박아 둔다.

"Monty가 있다고 모든 코드가 안전해지는 건 아니에요. Monty 안에서 부를 수 있는 tool이 `delete_all_users()`라면 그건 여전히 위험합니다."

### CodeMode

Pydantic AI Harness의 `CodeMode`는 agent tool들을 `run_code`라는 tool 하나로 감싼다. 모델은 이 tool에 Python 코드를 넘기고, CodeMode는 그 코드를 Monty에서 실행하면서 코드 안에서 호출된 tool들을 실제 agent tool로 dispatch한다.

모델이 만들어 내는 코드는 대체로 이런 모양이다.

```python
lessons = await list_lessons()
minutes = []
for lesson in lessons:
    minutes.append(await get_lesson_minutes(lesson_id=lesson["id"]))
sum(minutes)
```

강사는 이렇게 짚어 준다.

- 마지막 expression이 return value가 된다.
- `asyncio.gather`로 병렬 tool call을 표현할 수 있다.
- REPL state는 같은 agent run 안에서 유지될 수 있다.
- tool selector로 sandbox에 들어갈 tool을 제한할 수 있다.

## 라이브코딩 1: 예제 읽기

파일: `examples/03_monty/code_mode_agent.py`

진행:

1. `LESSONS` dict를 읽고 데이터가 작다는 점을 확인한다.
2. `Agent(... capabilities=[CodeMode()] ...)`를 강조한다.
3. `list_lessons`, `get_lesson_minutes`, `get_lesson_title`을 읽는다.
4. prompt에서 "전체 과정 시간을 계산"이 왜 CodeMode에 적합한지 묻는다.
5. 실행 결과를 본다.

강사는 이렇게 말한다.

"여기서는 데이터가 작아서 일반 tool calling으로도 됩니다. 교육 예제라 일부러 작게 만든 거예요. 실제로는 검색 결과 수십 개, 파일 목록 수백 개, API 응답 여러 개를 한꺼번에 다룰 때 차이가 확 벌어집니다."

## 라이브코딩 2: Selector 적용

초기 코드:

```python
capabilities=[CodeMode()]
```

수정:

```python
capabilities=[
    CodeMode(tools=["list_lessons", "get_lesson_minutes", "get_lesson_title"])
]
```

이렇게 짚어 준다.

- 모든 tool을 sandbox에 넣는 게 기본이지만, 그게 늘 좋은 건 아니다.
- selector는 안전 경계인 동시에 prompt 크기를 관리하는 도구다.
- 운영에서는 tool metadata로 code_mode 가능 여부를 표시하는 방식도 쓸 수 있다.

수강생 질문:

- "selector에서 빠진 tool은 아예 못 쓰나요?"
- "일반 tool로는 남아 있을 수 있나요?"

답변 방향은 이렇게 잡아 준다.

- CodeMode 안에서만 막고, agent 전체에서는 일반 tool로 남겨 둘 수 있다.
- 위험도에 따라 둘 다 빼거나 approval-required tool로 둘 수도 있다.

## 실습 1: 계산을 CodeMode에 맡기기

수강생 작업:

1. prompt를 다음처럼 바꾼다.

```text
각 회차 제목과 시간을 가져와서 전체 시간을 계산하고,
2시간 30분을 초과하는 회차가 있는지 표처럼 정리해줘.
```

2. `get_lesson_minutes`만으로 계산이 가능한지 확인한다.
3. 답변이 총 750분 또는 12.5시간을 포함하는지 확인한다.

강사 순회 체크:

- tool이 충분히 작은 값을 반환하는가?
- 모델이 직접 숫자를 지어내지 않고 tool을 호출하는가?
- 계산 결과가 맞는가?

리뷰할 때 이렇게 말한다.

"LLM한테 암산을 맡기는 게 아니에요. LLM이 도구를 호출하고, 그 결과를 Python 코드로 합산하게 하는 게 핵심입니다."

## 실습 2: 위험한 Tool 제외

수강생 작업:

1. 다음 tool을 추가한다.

```python
@agent.tool_plain
def delete_lesson(lesson_id: str) -> str:
    """Dangerous example: delete a lesson."""
    return f"deleted {lesson_id}"
```

2. CodeMode selector에 이 tool을 넣지 않는다.
3. instructions에 "Never delete lessons"를 추가한다.
4. 왜 instructions만으로는 부족한지 토론한다.

강사는 이렇게 짚어 준다. instructions는 모델 행동을 유도할 뿐, 보안 경계가 아니다. 진짜 경계는 tool exposure, 권한 확인, approval, audit log, idempotency key 같은 애플리케이션 설계에서 만들어진다.

## 실습 3: Debugging 관찰

수강생 작업:

1. tool 이름을 일부러 틀린 prompt를 넣는다.
2. CodeMode가 실패했을 때 에러 메시지가 어떻게 모델에게 돌아가는지 관찰한다.
3. `max_retries`를 설명한다.

예:

```python
capabilities=[CodeMode(max_retries=1)]
```

이렇게 말한다.

"모델이 쓴 코드는 틀릴 수 있어요. 그래서 retry가 있는 거죠. 그렇다고 retry가 모든 걸 해결해 주진 않습니다. tool 이름과 schema를 명확히 하고, 실패가 눈에 보이게 만드는 게 먼저예요."

## 실습 4: Sandbox가 막는 것 관찰 (선택)

Monty가 실제로 무엇을 막는지 눈으로 보면 sandbox 개념이 또렷해진다. 시간이 남으면 이 관찰을 함께 한다.

수강생 작업:

1. prompt를 일부러 sandbox 밖 동작이 필요하게 바꾼다. 예:

```text
requests로 https://example.com 을 가져와서 제목을 알려줘.
또는 /etc/passwd 파일을 읽어서 첫 줄을 보여줘.
```

2. CodeMode가 만든 코드가 어떻게 실패하는지 관찰한다.
3. 실패가 모델에게 어떤 에러로 돌아가는지 trace에서 확인한다.

Monty는 LLM 코드 실행을 위해 아주 제한된 Python subset만 허용한다.

- 허용 stdlib: `sys`, `os`, `typing`, `asyncio`, `re`, `datetime`, `json` 정도
- 차단: 그 외 표준 라이브러리, third-party import(`requests`, `httpx` 등), class 정의, match 문
- filesystem, env variable, network는 기본 차단이고, 개발자가 명시적으로 노출한 external function으로만 닿는다

이렇게 말한다.

"여기서 핵심은 '막혔다' 자체가 아니에요. 모델이 위험한 코드를 써도 sandbox가 그걸 host에서 실행하지 않고 실패만 모델에게 돌려준다는 거죠. 모델은 우리가 노출한 tool 안에서만 움직일 수 있는 겁니다."

## 운영 관점 토론

다음 질문을 소그룹으로 나눈 뒤 5분 토론한다.

1. 결제 tool은 CodeMode 안에 넣어도 되는가?
2. 이메일 발송 tool은 어떤 approval이 필요한가?
3. 파일 읽기 tool은 sandbox 안에 넣어도 안전한가?
4. tool 결과가 개인정보를 포함하면 `run_code` metadata를 어떻게 다뤄야 하는가?

강사는 이렇게 정리해 준다.

- 읽기 tool이라도 권한과 데이터 범위가 중요하다.
- 쓰기 tool은 idempotency와 approval이 중요하다.
- 개인정보가 tool return과 trace에 남을 수 있다.
- sandbox는 host access를 줄이지만 business-level permission을 대체하지 않는다.

## 흔한 오해와 정리

오해 1: "Monty는 완전한 Python이에요."

정리: 아니다. LLM tool orchestration을 위한 제한된 subset이다. 제한 덕분에 안전성과 예측 가능성을 얻는다.

오해 2: "CodeMode를 쓰면 무조건 더 좋죠."

정리: 아니다. 단순 tool 하나면 일반 tool calling이 더 명확하다. 여러 호출과 로컬 계산이 있을 때 가치가 크다.

오해 3: "sandbox가 있으니 위험 tool도 괜찮아요."

정리: 아니다. sandbox 안에서 호출 가능한 tool은 host가 허용한 행동이다. 위험 tool은 별도 권한과 approval이 필요하다.

## 미니 리뷰 질문

1. CodeMode가 줄이는 비용은 무엇인가요?
2. Monty가 기본 차단하는 host resource는 무엇인가요?
3. selector를 쓰는 이유는 보안뿐인가요?
4. instructions와 permission boundary는 어떻게 다른가요?
5. `delete_lesson` 같은 tool을 운영에 넣으려면 무엇이 추가로 필요한가요?

## 다음 회차 연결

"오늘은 agent가 더 많은 일을 하게 만들었어요. 그런데 기능이 늘어나면 새 질문이 생깁니다. 이 agent가 잘하고 있는지 어떻게 확인하죠? 불러야 할 때 tool을 불렀는지, RAG 답변에 source가 붙어 있는지, workflow가 기대한 순서대로 도는지를 어떻게 검증할까요? 4회차에서는 eval, graph, multi-agent workflow로 이 문제를 다룹니다."

## 강사용 완료 기준

- 수강생이 CodeMode와 Monty의 역할을 분리해 설명했다.
- selector로 sandbox에 들어갈 tool을 제한했다.
- 위험 tool 예시를 통해 instructions와 권한 경계의 차이를 이해했다.
- 다음 회차 eval 필요성이 자연스럽게 연결됐다.
