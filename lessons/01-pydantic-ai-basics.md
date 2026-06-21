# 1회차: Pydantic AI 기본, Logfire, Tool 사용

## 2시간 목표

이 회차의 목표는 수강생이 "Pydantic AI agent는 LLM 호출 함수가 아니라 타입이 있는 애플리케이션 경계"라는 감각을 갖는 것이다. 동시에, agent 실행을 print 결과로만 보지 말고 trace로 관찰하는 습관을 첫 시간부터 들인다. 수업이 끝나면 수강생은 `Agent`, Logfire trace, `instructions`, `tool`, `RunContext`, `deps_type`, `output_type`을 각각 한 문장으로 설명하고, 작은 교육 상담 agent를 직접 고칠 수 있어야 한다.

완성 결과물은 `examples/01_basics/tool_agent.py`를 바탕으로 한 course assistant다. 이 assistant는 Logfire instrumentation을 켠 채로 수업 catalog를 tool로 조회하고, Pydantic 모델로 검증한 JSON 답변을 돌려준다.

## 사례로 시작하기: "그냥 LLM API 호출하면 왜 부족한가"

첫 예시는 일부러 단순한 FastAPI endpoint에서 시작한다.

```python
@app.post("/ask")
async def ask(question: str) -> str:
    return await call_llm(question)
```

데모에서는 잘 돈다. "2회차에서는 무엇을 배우나요?"라고 물으면 자연스러운 답이 나온다. 그런데 여기에 실제 서비스를 붙이는 순간 질문이 달라진다.

- 프론트엔드는 응답이 항상 문자열이라고 믿어도 되는가?
- 답변이 실제 수업 catalog에서 온 것인지, 모델이 그럴듯하게 지어낸 것인지 어떻게 구분하는가?
- 모델이 DB를 읽어야 할 때, 어떤 함수가 호출됐는지 어디서 확인하는가?
- 응답에 `lesson_ids`, `confidence`, `next_action` 같은 필드가 필요하면 누가 그 형식을 보장하는가?
- user A가 볼 수 있는 자료와 user B가 볼 수 있는 자료가 다르면, tool은 누구의 권한으로 실행되는가?

Pydantic AI의 `Agent`는 이 문제를 "LLM을 더 똑똑하게 만들기"가 아니라 "LLM 호출을 애플리케이션 경계 안에 넣기"로 푼다. `instructions`는 정책, `tools`는 외부 세계와의 접점, `deps`는 요청 단위 의존성, `output_type`은 API 응답 계약, Logfire trace는 실행 증거다.

이 사례에서는 이렇게 말한다.

"최종 답변이 자연스러운지는 첫 번째 검증일 뿐이에요. 백엔드 서비스에서는 어떤 tool을 어떤 인자로 불렀고, 어떤 타입으로 돌아왔고, 실패하면 어디서 고치는지가 훨씬 중요합니다."

## 프레임워크 위치: 왜 Pydantic AI로 시작하는가

수강생 중에는 LangChain, LangGraph, Spring AI를 이미 들어본 사람도 있다. 여기서 중요한 건 "무엇이 더 좋은가"가 아니라 "어떤 문제를 먼저 설명할 것인가"다. agent framework는 기능 목록만 보고 고르지 않는다. 주력 언어, 기존 서비스 프레임워크, 팀이 디버깅할 수 있는 타입 시스템, 운영 스택에 따라 답이 달라진다.

공식 문서 기준으로 LangChain은 `create_agent`를 중심으로 모델, tool, system prompt, middleware를 빠르게 조립하는 범용 agent framework다. 표준 모델 인터페이스, integration, middleware, LangSmith 관측/평가와 잘 엮인다. 이미 LangChain 생태계의 retriever, middleware, LangSmith 운영 흐름을 쓰는 팀이라면 LangChain으로 시작하는 게 자연스럽다.

Spring AI는 Python framework가 아니다. Spring Boot/JVM 애플리케이션에 AI model, RAG, tool calling, structured output을 붙이는 Spring-native abstraction이다. `ChatClient`, Advisor API, `ToolCallback`, `VectorStore`, Java class/record 기반 structured output이 기존 Spring service, repository, configuration, observability 흐름과 잘 맞는다. 팀의 주력 서비스가 Spring Boot라면 Pydantic AI보다 Spring AI가 더 자연스러운 출발점일 수 있다.

Pydantic AI는 Python type hint와 Pydantic validation을 agent의 중심에 둔다. `Agent[Deps, Output]`, `RunContext`, `deps_type`, `output_type`으로 tool과 응답을 타입 있는 애플리케이션 경계로 다룬다. 이 교안의 대상은 Python 백엔드 개발자이고, FastAPI/Pydantic식 schema 감각을 LLM 앱으로 넓히는 게 목표다. 그래서 첫 agent framework는 Pydantic AI로 잡는다.

비교는 이 정도로만 한다. (LangGraph 같은 graph 기반 비교는 4회차에서 Pydantic Graph를 다룰 때 다시 짧게 언급한다.)

| 질문 | LangChain | Spring AI | Pydantic AI |
| --- | --- | --- | --- |
| 첫 인상 | 넓은 integration과 middleware를 갖춘 agent framework | Spring Boot 앱에 AI 기능을 붙이는 JVM/Spring abstraction | Python 타입과 Pydantic validation을 중심에 둔 agent framework |
| 기본 진입점 | `create_agent(model=..., tools=..., system_prompt=...)` | `ChatClient`, Advisors, ToolCallback, VectorStore | `Agent(model, instructions=..., deps_type=..., output_type=...)` |
| 강점 | provider/integration ecosystem, middleware, LangSmith 연결 | Spring DI/configuration/service 계층과의 자연스러운 통합 | type-safe deps/output, Pydantic schema, FastAPI 백엔드 감각과의 연결 |
| 선택 기준 | Python에서 다양한 agent integration을 빠르게 조립할 때 | 기존 제품과 팀이 Java/Spring 중심일 때 | Python 백엔드에서 타입 있는 agent 경계를 먼저 가르칠 때 |
| 수업에서의 역할 | 비교 대상으로 소개 | Python 밖의 목적별 선택지로 소개 | 본편 실습의 기준 |

이렇게 말한다.

"LangChain이나 Spring AI를 몰라서 Pydantic AI를 쓰는 게 아니에요. 목적이 다른 거예요. Spring Boot 제품에 AI를 붙이는 수업이면 Spring AI가 더 맞고, LangChain 생태계 integration을 빠르게 쓰고 싶으면 LangChain이 맞아요. 이 수업은 LLM 호출을 타입 있는 Python 애플리케이션 경계로 만드는 법을 먼저 가르치기 때문에 Pydantic AI에서 출발합니다."

## 수업 전 준비

- 0회차 provider smoke test가 끝났고 `.env`에 `COURSE_MODEL`이 들어 있어야 한다.
- OpenAI만 쓰는 환경이면 `COURSE_MODEL=openai:gpt-5.5`와 `OPENAI_API_KEY`를 설정한다. 경고를 피하고 싶으면 `openai-chat:gpt-5.5` 또는 `openai-responses:gpt-5.5`로 바꾼다.
- Logfire hosted UI에서 trace를 보려면 `uv run logfire auth` 후 `uv run logfire projects use <project>`로 `.logfire` 설정을 만든다. 설정이 없어도 예제는 `send_to_logfire="if-token-present"` 덕분에 그냥 돈다.
- 첫 API 호출은 raw HTTPX 예제로 돌려서, request/response body가 실제 파일에 어떻게 남는지 본다.
- 그 다음부터 Pydantic AI 예제는 안전한 breadcrumb만 `logs/api-calls.log`에 남긴다. Logfire UI를 못 쓰는 교육장에서도 이 파일로 "실제 provider 호출이 나갔는가"를 확인할 수 있다.
- VS Code Debugger나 `breakpoint()`/`pdb`로 `agent.run_sync`, tool 함수, structured output 직전의 변수를 들여다볼 수 있어야 한다.
- 실행 확인:

```bash
uv run python examples/01_basics/httpx_raw_api_log.py
tail -n 20 logs/httpx-raw-api.log
uv run python examples/01_basics/hello_agent.py
uv run python examples/01_basics/logfire_agent.py
uv run python examples/01_basics/tool_agent.py
tail -n 30 logs/api-calls.log
```

API 키가 없는 수강생이 있으면, 강사가 실행 결과를 화면으로 보여 주고 수강생은 코드 읽기와 TODO 수정 위주로 따라온다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-10분 | 문제 제기 | LLM 호출과 앱 개발의 차이를 만든다 | "그냥 API 호출하면 왜 부족한가" 답하기 |
| 10-22분 | Raw HTTPX 호출 | HTTP request/response가 실제 파일에 남는 것 확인 | `httpx_raw_api_log.py` 실행 |
| 22-32분 | 최소 Agent | raw HTTP 호출을 Pydantic AI `Agent.run_sync`로 감싸는 의미 이해 | `hello_agent.py` 실행 |
| 32-40분 | 안전한 로컬 API 로그 | payload 없는 breadcrumb로 줄이는 이유 이해 | `logs/api-calls.log` 확인 |
| 40-50분 | Logfire 관측 | agent run, model request, usage, trace 개념 이해 | `logfire_agent.py` 읽기 |
| 50-62분 | 로컬 디버깅 | VS Code Debugger와 `breakpoint()`로 변수와 tool 인자 확인 | breakpoint 걸고 실행 |
| 62-68분 | Instructions | 고정 prompt와 런타임 prompt 구분 | instructions 수정 후 결과 비교 |
| 68-75분 | Tool calling | tool schema, docstring, 타입 힌트 이해 | `read_lesson` tool 읽기 |
| 75-80분 | 짧은 휴식/질문 | 모호한 개념 정리 | 질문 |
| 80-95분 | Deps와 RunContext | 전역 상태 대신 요청 단위 의존성 주입 이해 | lesson catalog를 deps로 바꿔보기 |
| 95-108분 | Structured output | Pydantic 모델이 응답 계약이 되는 방식 이해 | `LessonAnswer` 필드 추가 |
| 108-118분 | 디버깅 실습 리뷰 | 흔한 실패를 로그, trace, debugger로 분리한다 | 결과 공유 |
| 118-120분 | 다음 회차 연결 | tool에서 RAG로 넘어갈 이유 만들기 | 한 줄 회고 |

## 도입 이야기

수업은 이렇게 연다.

"LLM API를 호출하는 코드야 누구나 10분이면 만들어요. 그런데 회사 서비스에 넣으려고 하면 질문이 달라집니다. 이 답변은 타입이 뭐죠? 모델이 우리 DB를 언제 읽나요? tool이 실패하면 누가 재시도하나요? 프론트엔드는 어떤 schema를 믿고 화면을 그리나요? Pydantic AI는 바로 이 질문들에 답하려고, LLM 호출 주변에 Python 타입과 Pydantic validation을 둘러주는 framework예요."

그러고 나서 칠판에 이 그림을 그린다.

```text
user prompt
   |
   v
Agent = model + instructions + tools + deps + output validation
   |
   v
typed application result
```

전하고 싶은 메시지는 두 가지다. 첫째, agent가 똑똑해서 좋은 게 아니라 경계가 명확해서 유지보수가 된다. 둘째, 그 경계가 실제로 어떻게 실행됐는지는 trace로 확인해야 한다.

## 개념 설명 스크립트

### Agent

`Agent`는 모델 이름과 실행 정책을 들고 있는 객체다. 겉보기엔 함수 하나 같지만, 안에서는 모델 요청부터 tool 정의와 실행, output 검증, usage 집계까지 다 챙긴다.

수업에서는 이렇게 짚어 준다.

- `Agent("openai:gpt-5.5")`나 `Agent("openrouter:anthropic/claude-sonnet-4.6")`처럼 어떤 provider/model을 쓸지 정한다.
- agent는 보통 전역 객체로 한 번 만들어 두고 재사용한다.
- 요청마다 달라지는 값은 생성자에 넣지 말고 `run(..., deps=...)`로 넘긴다.
- agent를 stateless에 가깝게 설계해야 테스트와 운영이 쉬워진다.
- 실행은 `agent.run_sync(...)`(동기)와 `await agent.run(...)`(비동기) 두 가지다. 간단한 스크립트나 디버깅에는 `run_sync`, FastAPI 같은 async 서버에서는 `run`을 쓴다. 그래서 예제도 단독 실행 스크립트(`hello_agent.py`)는 `run_sync`, deps를 받아 돌리는 `tool_agent.py`는 `await agent.run(...)`을 쓴다.

수강생에게 던질 질문:

- "사용자 id는 agent 생성자에 넣을까요, deps에 넣을까요?"
- "DB connection pool은 전역 agent 안에 두는 게 좋을까요?"

정답 방향은 "요청마다 달라지는 건 deps로, 앱 lifetime 동안 공유되는 건 agent 밖에서 관리"다.

### API 호출 관측과 Logfire

LLM 애플리케이션은 느리고, 비싸고, 비결정적이다. print로 최종 답변만 보면 다음 질문에 답하기 어렵다.

- 모델 요청이 몇 번 나갔는가?
- tool은 호출됐는가, 안 됐는가?
- 어떤 tool 인자가 들어갔는가?
- output validation 전후로 무슨 일이 있었는가?
- token usage는 얼마인가?
- 실패가 모델 탓인가, tool 탓인가, instructions 탓인가?

수업에서는 API 호출 확인을 두 단계로 나눈다. 첫 단계는 raw HTTPX 호출이다. request와 response를 거의 그대로 파일에 남겨서 "LLM 호출도 결국 HTTP API 호출"이라는 사실을 눈으로 확인한다. 둘째 단계는 안전한 breadcrumb 로그다. raw log는 설명용으로는 좋지만 공유나 운영에는 위험하니, 이후 예제는 payload 없이 호출 시작/종료, model string, usage 정도만 남긴다.

Logfire trace는 그다음이다. 파일 로그가 "호출이 나갔는가"를 본다면, Logfire는 agent run, model request, tool call, validation을 span으로 보여 준다.

### 디버깅 도구의 역할 구분

1회차에서 디버깅 도구를 한꺼번에 쏟아내면 수강생이 헷갈린다. 그래서 도구마다 역할을 갈라서 설명한다.

| 도구 | 확인하는 것 | 언제 쓰는가 |
| --- | --- | --- |
| Raw HTTPX 로그 | 실제 HTTP request/response body | "LLM 호출도 HTTP API 호출"이라는 감각을 만들 때 |
| `logs/api-calls.log` | 호출 시작/종료, model string, usage, HTTP status | Logfire 없이 provider 호출 여부를 확인할 때 |
| Logfire trace | agent run, model request, tool call, validation 흐름 | 실행 경로와 tool 호출 여부를 확인할 때 |
| VS Code Debugger | Python 변수, 분기, call stack | 코드를 한 줄씩 따라가며 원인을 찾을 때 |
| `breakpoint()`/`pdb` | 터미널에서 변수와 stack 확인 | VS Code를 못 쓰거나 빠르게 한 지점만 멈출 때 |
| traceback | 예외가 발생한 파일, 줄, 원인 | validation error, env var 누락, auth error를 읽을 때 |

이렇게 말한다.

"로그와 trace는 실행이 지나간 증거를 봅니다. debugger랑 `pdb`는 지금 돌고 있는 Python 상태를 멈춰서 보는 거고요. 답변이 이상하면 먼저 trace에서 tool이 불렸는지 보고, tool 안의 값이 이상하면 debugger로 `ctx.deps`와 인자를 봅니다."

### 1단계: raw HTTPX 전체 로그

파일: `examples/01_basics/httpx_raw_api_log.py`

이 예제는 Pydantic AI를 안 쓰고 `httpx`로 OpenAI Responses API를 직접 호출한다. abstraction 없이 API 호출의 맨얼굴을 보자는 게 목적이다.

```bash
uv run python examples/01_basics/httpx_raw_api_log.py
tail -n 20 logs/httpx-raw-api.log
```

로그에는 이런 게 남는다.

- HTTP method와 URL
- Authorization을 뺀 request headers
- request body
- response status
- response headers
- response body

이 파일은 일부러 "너무 많이" 남긴다. 그래서 수업용으로는 좋지만, 그대로 공유하거나 운영 기본값으로 쓰면 안 된다. prompt, 사용자 입력, 모델 응답이 고스란히 남기 때문이다. 이 단계의 목표는 안전한 설계가 아니라 API 호출의 실체를 보는 것이다.

이렇게 말한다.

"처음엔 다 봅니다. 그래야 모델 호출이 어떤 HTTP 요청인지 감이 잡혀요. 그다음엔 안전하게 줄입니다. 운영에서 필요한 건 모든 payload가 아니라, 어떤 호출이 언제 어떤 모델로 나갔고 성공했는지 확인할 증거니까요."

### 2단계: 안전한 API 호출 breadcrumb

예제는 공통 헬퍼 `examples/course_logging.py`로 API 호출 breadcrumb를 파일에 남긴다.

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

여기 남기는 건 다음 수준까지만이다.

- `agent.run_sync start/done`
- model string
- prompt 길이
- usage
- HTTPX request line/status

기본값은 payload를 안 남긴다. prompt, 개인정보, API response body가 파일에 남으면 교육장 화면 공유나 과제 제출에서 사고가 난다. 그래서 상세 payload는 로컬 로그의 기본 목표가 아니다.

환경변수:

```bash
COURSE_API_LOG_FILE=logs/api-calls.log
COURSE_API_LOG_LEVEL=INFO
COURSE_API_LOG_DISABLED=1
```

`COURSE_API_LOG_LEVEL=DEBUG`는 버려도 되는 prompt에서만 쓴다. provider SDK가 내부 debug log에 request option을 더 많이 남길 수 있기 때문이다.

### Logfire trace

Logfire는 Pydantic 팀이 만든 OpenTelemetry 기반 observability 도구다. Pydantic AI가 Logfire instrumentation을 지원하니, 다음 두 줄이면 agent run trace를 만들 수 있다.

```python
import logfire

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()
```

이렇게 짚어 준다.

- Logfire는 hosted product지만 바탕이 OpenTelemetry라, 관측 개념 자체는 vendor에 묶이지 않고 이해할 수 있다.
- `send_to_logfire="if-token-present"`는 Logfire token이 있을 때만 전송한다. 그래서 수업 예제는 token이 없어도 돈다.
- trace에는 agent run, model request, tool call, usage 같은 디버깅 단서가 담긴다.
- `logfire.instrument_httpx(capture_all=True)`는 provider HTTP request/response까지 볼 수 있지만, prompt와 user data, API payload가 노출될 수 있으니 수업에서는 주의 옵션으로만 다룬다.

초반에 Logfire를 넣는 이유는 이렇게 말한다.

"agent부터 만들고 관측을 나중에 붙이면, 결국 최종 답변만 보는 습관이 들어요. 첫 시간부터 trace를 같이 보면 tool call과 model call을 실행 흐름으로 이해하게 됩니다. 나중에 RAG, CodeMode, multi-agent, DBOS를 배울 때도 똑같이 trace를 기준으로 디버깅할 수 있고요."

### 로컬 디버깅: VS Code Debugger, breakpoint, pdb

Logfire와 파일 로그가 "agent가 무엇을 했는가"를 보여 준다면, 로컬 debugger는 "지금 Python 코드 안에 어떤 값이 들어 있는가"를 보여 준다. 1회차에서는 복잡한 기법까지 갈 것 없이, 다음 세 지점만 멈춰 보면 충분하다.

추천 breakpoint:

- `examples/01_basics/hello_agent.py`: `agent.run_sync(prompt)` 직전과 직후
- `examples/01_basics/tool_agent.py`: `read_lesson(ctx, lesson_id)` 첫 줄
- `examples/01_basics/tool_agent.py`: `answer = cast(LessonAnswer, result.output)` 직후

VS Code에서는 `.vscode/launch.json`의 `01 hello_agent`, `01 tool_agent`, `01 raw HTTPX log` 구성을 골라 실행한다. 수강생에게는 이 순서로 보여 준다.

1. `01 tool_agent`를 선택한다.
2. `read_lesson` 함수 안에 breakpoint를 건다.
3. Debug로 실행한 뒤 Variables 패널에서 `lesson_id`, `ctx.deps.lessons`를 확인한다.
4. Call Stack에서 agent 실행 도중 tool 함수로 들어온 흐름을 본다.
5. Continue로 끝까지 실행하고 `result.output`을 확인한다.

터미널만 쓰는 환경이면 `breakpoint()`를 임시로 넣는다.

```python
@agent.tool
async def read_lesson(ctx: RunContext[CourseDeps], lesson_id: str) -> str:
    breakpoint()
    return ctx.deps.lessons.get(lesson_id, f"Unknown lesson id: {lesson_id}")
```

실행:

```bash
uv run python examples/01_basics/tool_agent.py
```

자주 쓰는 `pdb` 명령은 이 정도면 된다.

| 명령 | 의미 |
| --- | --- |
| `p lesson_id` | 변수 출력 |
| `p ctx.deps.lessons` | deps 안의 catalog 확인 |
| `where` | 현재 call stack 확인 |
| `n` | 다음 줄 실행 |
| `s` | 함수 안으로 들어가기 |
| `c` | 다음 breakpoint까지 계속 실행 |
| `q` | 디버깅 종료 |

주의할 점:

- 수업 자료에 `breakpoint()`를 남긴 채 커밋하지 않는다.
- API key나 prompt가 Variables 패널에 보일 수 있으니, 화면 공유 전에 확인한다.
- provider 호출이 오래 걸릴 수 있으니, breakpoint는 모델 호출 직전/직후나 tool 내부처럼 의미 있는 곳에만 건다.

traceback 읽기도 1회차에서 가볍게 다룬다. 에러가 나면 맨 아래 예외 이름과 메시지를 먼저 보고, 그 위로 올라가며 내 코드 파일 경로를 찾는다. 예를 들어 `ValidationError`면 `LessonAnswer` schema와 모델 출력이 안 맞는 것이고, `RuntimeError: OPENAI_API_KEY is required`면 `.env`와 환경변수부터 본다. 디버깅의 목표는 모든 stack frame을 이해하는 게 아니라 "내가 고칠 파일과 줄"을 찾는 것이다.

### Instructions

instructions는 agent의 기본 행동 규칙이다. 사용자 질문과 달리, 매 요청마다 반복되는 policy를 담는다.

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

나쁜 이유는 평가하기 어렵고, 실패했을 때 고칠 기준이 없기 때문이다.

### Tools

tool은 모델이 부를 수 있는 우리 쪽 애플리케이션 함수다. Pydantic AI는 함수 이름, 인자 타입, 반환 타입, docstring을 모아서 모델에게 넘길 tool schema를 만든다.

이렇게 짚어 준다.

- 모델은 Python 함수를 직접 실행하지 않는다. "이 tool을 이런 인자로 부르고 싶다"고 요청할 뿐이다.
- 그 요청을 받아 실제 Python 함수를 실행하는 건 framework다.
- docstring은 사람만 읽는 주석이 아니라 모델이 읽는 tool 설명이다.
- tool 이름은 API endpoint 이름처럼 안정적이어야 한다.

`@agent.tool`과 `@agent.tool_plain` 차이:

- `@agent.tool`: 첫 인자로 `RunContext`를 받아 deps, usage 같은 실행 문맥을 읽는다.
- `@agent.tool_plain`: context가 필요 없는 순수 함수에 쓴다.

### Deps와 RunContext

`RunContext[CourseDeps]`는 tool이 현재 실행의 dependency에 닿는 통로다.

전역 dict를 직접 읽는 코드:

```python
LESSONS = {...}

@agent.tool_plain
def read_lesson(lesson_id: str) -> str:
    return LESSONS[lesson_id]
```

교육용으로는 되지만, 운영에서는 테스트와 요청 분리가 어렵다. deps를 쓰면 요청마다 catalog, 사용자, 권한, DB 세션을 갈아끼울 수 있다.

```python
@dataclass
class CourseDeps:
    lessons: dict[str, str]

@agent.tool
async def read_lesson(ctx: RunContext[CourseDeps], lesson_id: str) -> str:
    return ctx.deps.lessons.get(lesson_id, "Unknown lesson id")
```

### Structured Output

`output_type=LessonAnswer`는 모델이 돌려줘야 하는 최종 결과를 Pydantic 모델로 묶어 둔다. 초보자에게는 "LLM 답변을 API response schema로 바꾸는 단계"라고 설명한다.

장점:

- UI가 `answer`, `lesson_ids`, `confidence` 필드를 믿고 쓸 수 있다.
- validation이 실패하면 그게 보이니 prompt나 schema를 고칠 수 있다.
- eval에서 field 단위로 품질을 잴 수 있다.

주의:

- schema가 너무 복잡하면 모델이 자주 실패한다.
- `confidence` 같은 숫자는 모델의 주관적 추정이라, 실제 확률처럼 쓰면 안 된다.
- 사용자에게 보여줄 텍스트와 내부 control field는 구분해야 한다.

예제에서 `cast(LessonAnswer, result.output)`을 보게 된다. `output_type`을 지정하면 `result.output`은 런타임에 이미 `LessonAnswer` 값이지만, 타입 체커는 종종 이를 `Any`로 본다. `cast`는 런타임에 아무 일도 하지 않고, 타입 체커와 IDE 자동완성에게 "이건 `LessonAnswer`다"라고 알려 주는 표시일 뿐이다.

## 라이브코딩 1: 최소 Agent

파일: `examples/01_basics/hello_agent.py`

진행:

1. import를 읽는다.
2. `load_dotenv()`가 왜 있는지 설명한다.
3. `COURSE_MODEL` 환경변수로 모델을 바꿀 수 있음을 보여 준다.
4. instructions를 빼고 실행한다.
5. instructions를 "한 문장으로 답해"로 바꾸고 결과를 비교한다.

이렇게 말한다.

"처음엔 그냥 API wrapper처럼 보일 거예요. 그런데 여기에 tool과 output type을 붙이는 순간, agent는 작은 backend service처럼 굴기 시작합니다."

실패 시 대응:

- `OPENAI_API_KEY` 없음: 환경변수 확인.
- model prefix 경고: README에 있는 `openai-chat:` 선택지를 설명.
- 네트워크 실패: 흐름상 코드를 읽고 강사 실행 결과로 대체.

## 라이브코딩 2: Logfire 붙이기

파일: `examples/01_basics/logfire_agent.py`

진행:

1. `configure_observability()`를 읽는다.
2. `logfire.configure(send_to_logfire="if-token-present")`가 token이 있을 때만 전송한다는 점을 짚는다.
3. `logfire.instrument_pydantic_ai()`가 agent run/model request/tool call span을 만든다는 점을 보여 준다.
4. `LOGFIRE_CAPTURE_HTTPX=1` 옵션은 HTTP payload까지 캡처할 수 있어 운영에서는 조심해야 한다고 설명한다.
5. `result.usage`를 출력해서 trace와 local usage 값이 이어지는 것을 보여 준다.

이렇게 말한다.

"이 코드는 기능을 바꾸지 않아요. 바꾸는 건 운영 가능성입니다. 답변이 이상할 때 prompt를 감으로 고치는 대신, trace에서 모델 요청과 tool 호출을 먼저 보게 되니까요."

실패 시 대응:

- Logfire login이 안 되어 있음: 예제는 그대로 돈다. hosted UI만 비어 있을 수 있다.
- `.logfire` 설정 없음: `uv run logfire auth`, `uv run logfire projects use <project>`를 안내한다.
- 민감한 payload 우려: `LOGFIRE_CAPTURE_HTTPX`를 켜지 않는다.

## 라이브코딩 3: Tool이 있는 Agent

파일: `examples/01_basics/tool_agent.py`

진행:

1. `CourseDeps`를 읽는다.
2. `LessonAnswer`를 읽고, 각 필드가 UI/API에서 어떤 의미인지 묻는다.
3. `Agent(... deps_type=CourseDeps, output_type=LessonAnswer ...)` 줄을 설명한다.
4. `read_lesson` tool의 docstring을 일부러 더 나쁘게 바꿔 본다.
5. `list_lesson_ids`가 context 없는 tool이라 `tool_plain`인 이유를 설명한다.
6. prompt를 바꿔, tool 호출이 필요한 질문과 필요 없는 질문을 비교한다.

수강생에게 보여줄 관찰 포인트:

- 모델이 tool을 불러도 최종 출력은 `LessonAnswer`다.
- tool 반환값이 문자열이면 모델이 그걸 다시 해석한다.
- tool 결과가 모호하면 모델 답변도 흔들린다.
- Logfire trace를 보면 tool이 실제로 불렸는지 확인된다.

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
- 반환값이 너무 크지 않은가?
- 없는 lesson id에서 예외를 던지지는 않는가?
- Logfire trace에 수정한 tool 이름이 보이는가?

리뷰 때 비교할 두 설계:

```python
def list_lessons() -> list[str]:
    return ["01", "02", "03"]
```

```python
def list_lessons() -> list[dict[str, str]]:
    return [{"id": "01", "title": "Pydantic AI basics"}]
```

두 번째가 모델에게는 더 친절하지만, 데이터가 커질수록 context 비용도 같이 커진다. 이 tradeoff를 설명한다.

## 실습 2: Structured Output 확장

목표: schema를 바꾸면 application contract가 바뀐다는 걸 직접 겪게 한다.

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

- description은 모델에게 schema 의도를 알려준다. field가 복잡할수록 더 필요하다.
- 한국어 서비스라면 한국어 description도 되지만, provider/model에 따라 영어가 더 안정적일 때도 있다.
- 비어도 되는 field라면 타입과 instructions에서 그 점을 분명히 한다.

## 흔한 오해와 정리

오해 1: "tool을 만들면 모델이 항상 tool을 부른다."

정리: 아니다. instructions, prompt, 모델 판단에 따라 호출 여부가 달라진다. 꼭 불러야 한다면 instructions와 eval로 강제하고 검증한다.

오해 2: "structured output이면 답변 내용이 참이다."

정리: 아니다. structured output은 형식을 검증한다. 사실성은 tool, RAG, eval, human review로 관리한다.

오해 3: "deps는 그냥 전역 변수를 감싼 것뿐이다."

정리: deps는 요청 단위 상태를 분리하는 장치다. 테스트, multi-tenant, 권한 확인에서 차이가 크게 벌어진다.

오해 4: "Logfire는 배포 후 모니터링할 때만 붙이면 된다."

정리: 아니다. 개발 중에도 trace를 보면 tool call, model request, usage, validation 실패를 빠르게 잡을 수 있다. 특히 RAG나 multi-agent처럼 실행 경로가 길어질수록 초반부터 관측 습관을 들이는 게 중요하다.

## 미니 리뷰 질문

수업 마지막 10분에 수강생끼리 짝지어 답하게 한다.

1. `RunContext`가 필요한 tool과 필요 없는 tool의 예를 하나씩 들어보세요.
2. tool docstring이 나쁘면 어떤 문제가 생기나요?
3. `output_type`은 hallucination을 막나요, 형식을 막나요?
4. 다음 회차 RAG에서 `retrieve`는 tool일까요, 별도 기능일까요?
5. Logfire trace에서 agent 디버깅에 도움이 되는 정보는 무엇인가요?

## 다음 회차 연결

"오늘 tool은 작은 catalog를 읽었어요. 그런데 회사 문서는 수천 페이지일 수 있죠. 그걸 전부 tool 결과로 돌려주면 context가 터집니다. 그래서 2회차에서는 문서를 잘게 나누고 embedding으로 검색해서, 필요한 조각만 agent에게 넘기는 RAG를 만듭니다."

## 강사용 완료 기준

- 수강생이 최소 agent와 tool agent를 모두 실행했거나, 코드 흐름을 설명했다.
- `@agent.tool`과 `@agent.tool_plain` 차이를 최소 1명이 말로 설명했다.
- Logfire instrumentation 두 줄과 trace에서 볼 수 있는 정보를 설명했다.
- output schema 변경 실습에서 validation된 JSON을 확인했다.
- 다음 회차 RAG가 "큰 지식 소스를 tool로 다루기 위한 확장"이라는 연결이 만들어졌다.
</content>
