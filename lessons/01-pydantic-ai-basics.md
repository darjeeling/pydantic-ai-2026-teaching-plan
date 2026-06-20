# 1회차: Pydantic AI 기본, Logfire, Tool 사용

## 2시간 목표

이 회차의 목표는 수강생이 "Pydantic AI agent는 LLM 호출 함수가 아니라, 타입이 있는 애플리케이션 경계"라는 감각을 갖게 하는 것이다. 동시에 agent 실행은 print 결과만 보지 말고 trace로 관찰해야 한다는 습관을 첫 시간부터 만든다. 수업이 끝나면 수강생은 `Agent`, Logfire trace, `instructions`, `tool`, `RunContext`, `deps_type`, `output_type`을 한 문장씩 설명하고, 작은 교육 상담 agent를 직접 고칠 수 있어야 한다.

완성 결과물은 `examples/01_basics/tool_agent.py`를 기반으로 한 course assistant다. 이 assistant는 Logfire instrumentation이 켜진 상태로 수업 catalog를 tool로 조회하고, Pydantic 모델로 검증된 JSON 형식 답변을 반환한다.

## 사례로 시작하기: "그냥 LLM API 호출하면 왜 부족한가"

강의 첫 예시는 일부러 단순한 FastAPI endpoint에서 시작한다고 가정한다.

```python
@app.post("/ask")
async def ask(question: str) -> str:
    return await call_llm(question)
```

데모에서는 잘 된다. 사용자가 "2회차에서는 무엇을 배우나요?"라고 물으면 자연스러운 답이 나온다. 하지만 서비스를 붙이는 순간 질문이 바뀐다.

- 프론트엔드는 응답이 항상 문자열이라고 믿어도 되는가?
- 답변이 실제 수업 catalog에서 온 것인지, 모델이 그럴듯하게 만든 것인지 어떻게 구분하는가?
- 모델이 DB를 읽어야 할 때 어떤 함수가 호출됐는지 어디서 확인하는가?
- 응답에 `lesson_ids`, `confidence`, `next_action` 같은 필드가 필요하면 누가 보장하는가?
- user A가 볼 수 있는 자료와 user B가 볼 수 있는 자료가 다르면 tool은 어떤 권한으로 실행되는가?

Pydantic AI의 `Agent`는 이 문제를 "LLM을 더 똑똑하게 만들기"보다 "LLM 호출을 애플리케이션 경계 안에 넣기"로 다룬다. `instructions`는 정책, `tools`는 외부 세계와의 접점, `deps`는 요청 단위 의존성, `output_type`은 API 응답 계약, Logfire trace는 실행 증거다.

이 사례에서 강조할 문장:

"최종 답변이 자연스러운지는 첫 번째 검증일 뿐입니다. 백엔드 서비스에서는 어떤 tool을 어떤 인자로 호출했고, 어떤 타입으로 반환됐고, 실패했을 때 어디서 고칠 수 있는지가 더 중요합니다."

## 프레임워크 위치: 왜 Pydantic AI로 시작하는가

수강생 중에는 이미 LangChain, LangGraph, Spring AI를 들어본 사람이 있을 수 있다. 여기서 중요한 것은 "무엇이 더 좋은가"가 아니라 "어떤 문제를 먼저 설명할 것인가"다. agent framework 선택은 기능 목록만으로 정하지 않는다. 주력 언어, 기존 서비스 프레임워크, 팀이 디버깅할 수 있는 타입 시스템, 운영 스택에 따라 달라진다.

공식 문서 기준으로 LangChain은 `create_agent`를 중심으로 모델, tool, system prompt, middleware를 빠르게 조립하는 범용 agent framework다. 표준 모델 인터페이스, integration, middleware, LangSmith 관측/평가와 잘 연결된다. 이미 LangChain ecosystem의 retriever, middleware, LangSmith 운영 흐름을 쓰는 팀이라면 LangChain으로 시작하는 선택이 자연스럽다.

Spring AI는 Python framework가 아니다. Spring Boot/JVM 애플리케이션에 AI model, RAG, tool calling, structured output을 붙이기 위한 Spring-native abstraction이다. `ChatClient`, Advisor API, `ToolCallback`, `VectorStore`, Java class/record 기반 structured output이 기존 Spring service, repository, configuration, observability 흐름과 잘 맞는다. 팀의 주력 서비스가 Spring Boot라면 Pydantic AI보다 Spring AI가 더 자연스러운 출발점일 수 있다.

Pydantic AI는 Python type hint와 Pydantic validation을 agent의 중심 개념으로 둔다. `Agent[Deps, Output]`, `RunContext`, `deps_type`, `output_type`을 통해 tool과 응답을 타입 있는 애플리케이션 경계로 다룬다. 이 교안의 대상은 Python 백엔드 개발자이고, FastAPI/Pydantic식 schema 감각을 LLM 앱으로 확장하는 것이 목표다. 그래서 첫 agent framework는 Pydantic AI로 잡는다.

비교 설명은 다음 정도로 제한한다.

| 질문 | LangChain | Spring AI | Pydantic AI |
| --- | --- | --- | --- |
| 첫 인상 | 넓은 integration과 middleware를 갖춘 agent framework | Spring Boot 앱에 AI 기능을 붙이는 JVM/Spring abstraction | Python 타입과 Pydantic validation을 중심에 둔 agent framework |
| 기본 진입점 | `create_agent(model=..., tools=..., system_prompt=...)` | `ChatClient`, Advisors, ToolCallback, VectorStore | `Agent(model, instructions=..., deps_type=..., output_type=...)` |
| 강점 | provider/integration ecosystem, middleware, LangSmith 연결 | Spring DI/configuration/service 계층과의 자연스러운 통합 | type-safe deps/output, Pydantic schema, FastAPI 백엔드 감각과의 연결 |
| 선택 기준 | Python에서 다양한 agent integration을 빠르게 조립할 때 | 기존 제품과 팀이 Java/Spring 중심일 때 | Python 백엔드에서 타입 있는 agent 경계를 먼저 가르칠 때 |
| 수업에서의 역할 | 비교 대상으로 소개 | Python 밖의 목적별 선택지로 소개 | 본편 실습의 기준 |

강사가 강조할 문장:

"LangChain이나 Spring AI를 몰라서 Pydantic AI를 쓰는 것이 아닙니다. 목적이 다릅니다. Spring Boot 제품에 AI를 붙이는 수업이면 Spring AI가 더 맞을 수 있고, LangChain 생태계 integration을 빠르게 쓰는 수업이면 LangChain이 맞을 수 있습니다. 이 수업은 LLM 호출을 타입 있는 Python 애플리케이션 경계로 만드는 법을 먼저 가르치기 때문에 Pydantic AI가 출발점입니다."

## 수업 전 준비

- 0회차 provider smoke test가 끝났고 `.env`에 `COURSE_MODEL`이 들어 있어야 한다.
- OpenAI만 쓰는 환경이면 `COURSE_MODEL=openai:gpt-5.2`와 `OPENAI_API_KEY`를 설정한다. 경고를 피하고 싶으면 `openai-chat:gpt-5.2` 또는 `openai-responses:gpt-5.2`로 바꾼다.
- Logfire hosted UI에서 trace를 보려면 `uv run logfire auth` 후 `uv run logfire projects use <project>`를 실행해 `.logfire` 설정을 만든다. 설정이 없어도 예제는 `send_to_logfire="if-token-present"` 때문에 실행 가능하다.
- 첫 API 호출은 raw HTTPX 예제로 `logs/httpx-raw-api.log`에 request/response body를 남겨 API 모양을 확인한다.
- 이후 Pydantic AI 예제는 안전한 breadcrumb만 `logs/api-calls.log`에 남긴다. Logfire UI를 못 쓰는 교육장에서도 이 파일로 "실제 provider 호출이 나갔는가"를 확인한다.
- 실행 확인:

```bash
uv run python examples/01_basics/httpx_raw_api_log.py
tail -n 20 logs/httpx-raw-api.log
uv run python examples/01_basics/hello_agent.py
uv run python examples/01_basics/logfire_agent.py
uv run python examples/01_basics/tool_agent.py
tail -n 30 logs/api-calls.log
```

API 키가 없는 수강생이 있으면 강사는 실행 결과를 화면에서 보여주고, 수강생은 코드 읽기와 TODO 수정 중심으로 따라오게 한다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-10분 | 문제 제기 | LLM 호출과 앱 개발의 차이를 만든다 | "그냥 API 호출하면 왜 부족한가" 답하기 |
| 10-22분 | Raw HTTPX 호출 | HTTP request/response가 실제 파일에 남는 것 확인 | `httpx_raw_api_log.py` 실행 |
| 22-32분 | 최소 Agent | raw HTTP 호출을 Pydantic AI `Agent.run_sync`로 감싸는 의미 이해 | `hello_agent.py` 실행 |
| 32-40분 | 안전한 로컬 API 로그 | payload 없는 breadcrumb로 줄이는 이유 이해 | `logs/api-calls.log` 확인 |
| 40-50분 | Logfire 관측 | agent run, model request, usage, trace 개념 이해 | `logfire_agent.py` 읽기 |
| 50-58분 | Instructions | 고정 prompt와 런타임 prompt 구분 | instructions 수정 후 결과 비교 |
| 58-65분 | Tool calling | tool schema, docstring, 타입 힌트 이해 | `read_lesson` tool 읽기 |
| 65-70분 | 짧은 휴식/질문 | 모호한 개념 정리 | 질문 |
| 70-90분 | Deps와 RunContext | 전역 상태 대신 요청 단위 의존성 주입 이해 | lesson catalog를 deps로 바꿔보기 |
| 90-105분 | Structured output | Pydantic 모델이 응답 계약이 되는 방식 이해 | `LessonAnswer` 필드 추가 |
| 105-118분 | 실습 리뷰 | 흔한 실패를 디버깅한다 | 결과 공유 |
| 118-120분 | 다음 회차 연결 | tool에서 RAG로 넘어갈 이유 만들기 | 한 줄 회고 |

## 도입 이야기

수업을 이렇게 시작한다.

"LLM API를 호출하는 코드는 누구나 10분 안에 만들 수 있습니다. 하지만 회사 서비스에 넣으려면 질문이 바뀝니다. 이 답변은 어떤 타입인가요? 모델이 우리 DB를 언제 읽나요? tool이 실패하면 누가 재시도하나요? 프론트엔드는 어떤 schema를 믿고 렌더링하나요? Pydantic AI는 이 질문에 답하기 위해 LLM 호출 주변에 Python 타입과 Pydantic validation을 붙이는 framework입니다."

그 다음 칠판에 다음 그림을 그린다.

```text
user prompt
   |
   v
Agent = model + instructions + tools + deps + output validation
   |
   v
typed application result
```

중요한 메시지는 두 가지다. 첫째, "agent가 똑똑해서 좋은 것이 아니라, agent 경계가 명확해서 유지보수 가능하다." 둘째, "agent 경계가 실제로 어떻게 실행됐는지는 trace로 확인해야 한다."

## 개념 설명 스크립트

### Agent

`Agent`는 모델 이름과 실행 정책을 가진 객체다. 함수 하나로 보이지만 내부적으로는 모델 요청, tool 정의, tool 실행, output 검증, usage 수집을 관리한다.

강사가 말할 포인트:

- `Agent("openai:gpt-5.2")` 또는 `Agent("openrouter:anthropic/claude-sonnet-4.6")`처럼 어떤 provider/model을 사용할지 정한다.
- agent는 보통 전역 객체로 만들어 재사용한다.
- 요청마다 달라지는 값은 agent 생성자에 넣기보다 `run(..., deps=...)`로 넘긴다.
- agent가 stateless에 가깝게 설계되어야 테스트와 운영이 쉽다.

수강생에게 물어볼 질문:

- "사용자 id는 agent 생성자에 넣어야 할까요, deps에 넣어야 할까요?"
- "DB connection pool은 전역 agent 안에 넣는 것이 좋을까요?"

정답 방향은 "요청마다 달라지는 것은 deps, 앱 lifetime 동안 공유되는 것은 외부에서 관리"다.

### API 호출 관측과 Logfire

LLM 애플리케이션은 느리고, 비싸고, 비결정적이다. print로 최종 답변만 보면 다음 질문에 답하기 어렵다.

- 모델 요청이 몇 번 발생했는가?
- tool은 호출됐는가, 호출되지 않았는가?
- 어떤 tool 인자가 들어갔는가?
- output validation 전후에 어떤 일이 있었는가?
- token usage는 얼마인가?
- 실패가 모델 문제인가, tool 문제인가, instructions 문제인가?

수업에서는 API 호출 확인을 두 단계로 나눈다. 첫 번째는 raw HTTPX 호출이다. request와 response를 파일에 거의 그대로 남겨 "LLM 호출도 결국 HTTP API 호출"이라는 사실을 확인한다. 두 번째는 안전한 breadcrumb 로그다. raw log는 설명에는 좋지만 공유/운영에는 위험하므로, 이후 예제는 payload 없이 호출 시작/종료, model string, usage 정도만 남긴다.

Logfire trace는 그 다음 단계다. 파일 로그는 "호출이 나갔는가"를 확인하고, Logfire는 agent run, model request, tool call, validation을 span으로 보여 준다.

### 1단계: raw HTTPX 전체 로그

파일: `examples/01_basics/httpx_raw_api_log.py`

이 예제는 Pydantic AI를 쓰지 않고 `httpx`로 OpenAI Responses API를 직접 호출한다. 목적은 abstraction 없이 API 호출 모양을 보는 것이다.

```bash
uv run python examples/01_basics/httpx_raw_api_log.py
tail -n 20 logs/httpx-raw-api.log
```

로그에는 다음이 남는다.

- HTTP method와 URL
- Authorization을 제외한 request headers
- request body
- response status
- response headers
- response body

이 파일은 일부러 "너무 많이" 남긴다. 그래서 수업에서는 좋지만, 공유하거나 운영 기본값으로 쓰면 안 된다. prompt, 사용자 입력, 모델 응답이 그대로 남기 때문이다. 이 단계의 목표는 안전한 설계가 아니라 API 호출의 실체를 보는 것이다.

강사가 강조할 문장:

"처음에는 다 봅니다. 그래야 모델 호출이 어떤 HTTP 요청인지 감이 생깁니다. 그 다음에는 안전하게 줄입니다. 운영에서 필요한 것은 모든 payload가 아니라, 어떤 호출이 언제 어떤 모델로 나갔고 성공했는지 확인할 수 있는 증거입니다."

### 2단계: 안전한 API 호출 breadcrumb

예제는 공통 헬퍼인 `examples/course_logging.py`를 사용해 API 호출 breadcrumb를 파일로 남긴다.

```python
from examples.course_logging import api_logger, configure_api_call_logging

configure_api_call_logging()
api_logger().info("agent.run_sync start model=%s", model)
result = agent.run_sync(prompt)
api_logger().info("agent.run_sync done model=%s usage=%s", model, result.usage)
```

기본 로그 파일:

```bash
logs/api-calls.log
```

수업 중 확인:

```bash
tail -n 30 logs/api-calls.log
```

로그 파일에 남기는 것은 다음 수준으로 제한한다.

- `agent.run_sync start/done`
- model string
- prompt 길이
- usage
- HTTPX request line/status

기본값은 payload를 남기지 않는다. prompt, 개인정보, API response body를 파일에 남기면 교육장 공유 화면이나 과제 제출에서 문제가 생길 수 있다. 그래서 상세 payload는 로컬 로그의 기본 목표가 아니다.

환경변수:

```bash
COURSE_API_LOG_FILE=logs/api-calls.log
COURSE_API_LOG_LEVEL=INFO
COURSE_API_LOG_DISABLED=1
```

`COURSE_API_LOG_LEVEL=DEBUG`는 throwaway prompt에서만 사용한다. provider SDK가 내부 debug log에 request option을 더 많이 남길 수 있기 때문이다.

### Logfire trace

Logfire는 Pydantic 팀이 만든 OpenTelemetry 기반 observability 도구다. Pydantic AI는 Logfire instrumentation을 지원하므로 다음 두 줄로 agent run trace를 만들 수 있다.

```python
import logfire

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()
```

강사가 강조할 점:

- Logfire는 hosted product지만, OpenTelemetry 기반이라 관측 개념 자체는 vendor-neutral하게 이해할 수 있다.
- `send_to_logfire="if-token-present"`를 쓰면 Logfire token이 있을 때만 전송한다. 수업 예제는 token이 없어도 실행된다.
- trace에는 agent run, model request, tool call, usage 같은 디버깅 단서가 들어간다.
- `logfire.instrument_httpx(capture_all=True)`는 provider HTTP request/response까지 볼 수 있지만, prompt, user data, API payload가 노출될 수 있으므로 수업에서는 주의 옵션으로 다룬다.

초반에 Logfire를 넣는 이유:

"agent를 먼저 만들고 나중에 관측을 붙이면, 수강생은 최종 답변만 보는 습관이 생깁니다. 첫 시간부터 trace를 보면 tool call과 model call을 실행 흐름으로 이해하게 됩니다. 이후 RAG, CodeMode, multi-agent, DBOS를 배울 때도 trace를 기준으로 디버깅할 수 있습니다."

### Instructions

instructions는 agent의 기본 행동 규칙이다. 사용자 질문과 다르게 매 요청마다 반복되는 policy를 담는다.

좋은 instructions 예:

```text
Answer in Korean.
Use tools before answering questions about the course.
If the tool result is insufficient, say that the course catalog does not contain enough information.
```

나쁜 instructions 예:

```text
Be smart and helpful.
```

나쁜 이유는 평가하기 어렵고, 실패했을 때 고칠 수 있는 기준이 없기 때문이다.

### Tools

tool은 모델이 호출할 수 있는 애플리케이션 함수다. Pydantic AI는 함수 이름, 인자 타입, 반환 타입, docstring을 바탕으로 모델에게 줄 tool schema를 만든다.

강사가 강조할 점:

- 모델은 Python 함수를 직접 실행하지 않는다. 모델은 "이 tool을 이런 인자로 호출하고 싶다"고 요청한다.
- framework가 그 요청을 받아 실제 Python 함수를 실행한다.
- docstring은 사람만 읽는 주석이 아니라 모델이 읽는 tool 설명이다.
- tool 이름은 API endpoint 이름처럼 안정적이어야 한다.

`@agent.tool`과 `@agent.tool_plain` 차이:

- `@agent.tool`: 첫 인자로 `RunContext`를 받아 deps, usage 등 실행 문맥을 읽는다.
- `@agent.tool_plain`: context가 필요 없는 순수 함수에 쓴다.

### Deps와 RunContext

`RunContext[CourseDeps]`는 tool이 현재 실행의 dependency에 접근하는 통로다.

전역 dict를 직접 읽는 코드:

```python
LESSONS = {...}

@agent.tool_plain
def read_lesson(lesson_id: str) -> str:
    return LESSONS[lesson_id]
```

교육용으로는 가능하지만 운영에서는 테스트와 요청 분리가 어렵다. deps를 쓰면 요청마다 catalog, 사용자, 권한, DB 세션을 바꿀 수 있다.

```python
@dataclass
class CourseDeps:
    lessons: dict[str, str]

@agent.tool
async def read_lesson(ctx: RunContext[CourseDeps], lesson_id: str) -> str:
    return ctx.deps.lessons.get(lesson_id, "Unknown lesson id")
```

### Structured Output

`output_type=LessonAnswer`는 모델이 반환해야 하는 최종 결과를 Pydantic 모델로 제한한다. 초보자에게는 "LLM 답변을 API response schema로 바꾸는 단계"라고 설명한다.

장점:

- UI가 `answer`, `lesson_ids`, `confidence` 필드를 믿고 사용할 수 있다.
- validation 실패가 보이면 prompt나 schema를 고칠 수 있다.
- eval에서 field 단위로 품질을 측정할 수 있다.

주의:

- schema가 너무 복잡하면 모델이 자주 실패한다.
- `confidence` 같은 숫자는 모델의 주관적 추정이므로 실제 확률처럼 쓰면 안 된다.
- 사용자에게 보여줄 텍스트와 내부 control field를 구분해야 한다.

## 라이브코딩 1: 최소 Agent

파일: `examples/01_basics/hello_agent.py`

진행:

1. import를 읽는다.
2. `load_dotenv()`가 왜 있는지 설명한다.
3. `COURSE_MODEL` 환경변수를 바꿀 수 있음을 설명한다.
4. instructions를 제거하고 실행한다.
5. instructions를 "한 문장으로 답해"로 바꾸고 결과를 비교한다.

말할 내용:

"처음에는 이것이 그냥 API wrapper처럼 보입니다. 하지만 곧 tool과 output type을 붙이면 agent는 작은 backend service처럼 행동하게 됩니다."

실패 시 대응:

- `OPENAI_API_KEY` 없음: 환경변수 확인.
- model prefix 경고: README에 있는 `openai-chat:` 선택지를 설명.
- 네트워크 실패: 수업 흐름상 코드를 읽고 강사 실행 결과로 대체.

## 라이브코딩 2: Logfire 붙이기

파일: `examples/01_basics/logfire_agent.py`

진행:

1. `configure_observability()`를 읽는다.
2. `logfire.configure(send_to_logfire="if-token-present")`가 token이 있을 때만 전송한다는 점을 설명한다.
3. `logfire.instrument_pydantic_ai()`가 agent run/model request/tool call span을 만든다는 점을 설명한다.
4. `LOGFIRE_CAPTURE_HTTPX=1` 옵션은 HTTP payload까지 캡처할 수 있으므로 운영에서는 조심해야 한다고 설명한다.
5. `result.usage`를 출력해서 trace와 local usage 값이 연결되는 것을 보여준다.

말할 내용:

"이 코드는 기능을 바꾸지 않습니다. 하지만 운영 가능성을 바꿉니다. 답변이 이상할 때 prompt를 감으로 고치는 대신, trace에서 모델 요청과 tool 호출을 먼저 봅니다."

실패 시 대응:

- Logfire login이 안 되어 있음: 예제는 그대로 실행된다. hosted UI만 비어 있을 수 있다.
- `.logfire` 설정이 없음: `uv run logfire auth`, `uv run logfire projects use <project>`를 수업 자료로 안내한다.
- 민감한 payload 우려: `LOGFIRE_CAPTURE_HTTPX`를 켜지 않는다.

## 라이브코딩 3: Tool이 있는 Agent

파일: `examples/01_basics/tool_agent.py`

진행:

1. `CourseDeps`를 읽는다.
2. `LessonAnswer`를 읽고 각 필드가 UI/API에 어떤 의미인지 묻는다.
3. `Agent(... deps_type=CourseDeps, output_type=LessonAnswer ...)` 줄을 설명한다.
4. `read_lesson` tool의 docstring을 더 나쁘게 바꿔본다.
5. `list_lesson_ids`가 context 없는 tool이므로 `tool_plain`인 이유를 설명한다.
6. prompt를 바꿔 tool 호출이 필요한 질문과 필요 없는 질문을 비교한다.

수강생에게 보여줄 관찰 포인트:

- 모델이 tool을 호출해도 최종 출력은 `LessonAnswer`다.
- tool 반환값이 문자열이면 모델이 다시 해석한다.
- tool 결과가 모호하면 모델 답변도 흔들린다.
- Logfire trace를 보면 tool이 실제로 호출됐는지 확인할 수 있다.

## 실습 1: Lesson Catalog 개선

목표: 수강생이 tool schema와 반환값 설계를 직접 만져보게 한다.

지시:

1. `list_lesson_ids`를 `list_lessons`로 바꾼다.
2. 반환값을 `list[dict[str, str]]` 형태로 바꾼다.
3. 각 dict는 `id`, `title`을 가진다.
4. prompt를 "Monty를 배우려면 어떤 회차를 보면 되나요?"로 바꾼다.

강사 순회 체크:

- tool 이름이 너무 추상적이지 않은가?
- docstring이 모델에게 충분한가?
- 반환값이 너무 큰가?
- tool이 없는 lesson id에서 예외를 던지지 않는가?
- Logfire trace에서 수정한 tool 이름이 보이는가?

리뷰 때 비교할 두 설계:

```python
def list_lessons() -> list[str]:
    return ["01", "02", "03"]
```

```python
def list_lessons() -> list[dict[str, str]]:
    return [{"id": "01", "title": "Pydantic AI basics"}]
```

두 번째가 모델에게 더 친절하지만, 데이터가 커질수록 context 비용이 늘어난다. 이 tradeoff를 설명한다.

## 실습 2: Structured Output 확장

목표: schema를 바꾸면 application contract가 바뀐다는 점을 경험하게 한다.

지시:

1. `LessonAnswer`에 `next_action: str`을 추가한다.
2. Field description을 붙인다.
3. instructions에 "next_action은 수강생이 바로 할 수 있는 행동이어야 한다"를 추가한다.
4. 출력 JSON을 확인한다.

예상 질문:

- "Field description은 꼭 필요한가요?"
- "한국어 description을 써도 되나요?"
- "list가 비어도 되나요?"

답변 방향:

- description은 모델에게 schema 의도를 알려준다. 복잡한 field일수록 필요하다.
- 한국어 서비스라면 한국어 description도 가능하지만, provider/model에 따라 영어가 더 안정적인 경우가 있다.
- 비어도 되는 field라면 타입과 instructions에서 명확히 한다.

## 흔한 오해와 정리

오해 1: "tool을 만들면 모델이 항상 tool을 호출한다."

정리: 아니다. instructions, prompt, 모델 판단에 따라 호출 여부가 달라진다. 반드시 호출해야 한다면 instructions와 eval로 강제/검증해야 한다.

오해 2: "structured output이면 답변 내용이 참이다."

정리: 아니다. structured output은 형식을 검증한다. 사실성은 tool, RAG, eval, human review로 관리한다.

오해 3: "deps는 그냥 전역 변수를 감싼 것뿐이다."

정리: deps는 요청 단위 상태를 분리하는 장치다. 테스트, multi-tenant, 권한 확인에서 차이가 커진다.

오해 4: "Logfire는 배포 후 모니터링할 때만 붙이면 된다."

정리: 아니다. 개발 중에도 trace를 보면 tool call, model request, usage, validation 실패를 빠르게 확인할 수 있다. 특히 RAG와 multi-agent처럼 실행 경로가 길어질수록 초반부터 관측 습관을 갖는 것이 중요하다.

## 미니 리뷰 질문

수업 마지막 10분에 수강생이 짝과 답하게 한다.

1. `RunContext`가 필요한 tool과 필요 없는 tool의 예를 하나씩 들어보세요.
2. tool docstring이 나쁘면 어떤 문제가 생기나요?
3. `output_type`은 hallucination을 막나요, 아니면 형식을 막나요?
4. 다음 회차 RAG에서 `retrieve`는 tool일까요, 별도 기능일까요?
5. Logfire trace에서 agent 디버깅에 도움이 되는 정보는 무엇인가요?

## 다음 회차 연결

"오늘 tool은 작은 catalog를 읽었습니다. 하지만 회사 문서는 수천 페이지일 수 있습니다. 모든 문서를 tool 결과로 반환하면 context가 터집니다. 그래서 2회차에서는 문서를 잘게 나누고 embedding으로 검색해서, 필요한 조각만 agent에게 주는 RAG를 만듭니다."

## 강사용 완료 기준

- 수강생이 최소 agent와 tool agent를 모두 실행하거나 코드 흐름을 설명했다.
- `@agent.tool`과 `@agent.tool_plain` 차이를 최소 1명이 말로 설명했다.
- Logfire instrumentation 두 줄과 trace에서 볼 수 있는 정보를 설명했다.
- output schema 변경 실습에서 validation된 JSON을 확인했다.
- 다음 회차 RAG가 "큰 지식 소스를 tool로 다루기 위한 확장"이라는 연결이 만들어졌다.
