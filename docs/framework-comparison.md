# LangChain, LangGraph, Spring AI, Pydantic AI 비교

이 문서는 2026-06-20 기준 공식 문서 리서치를 바탕으로 수업에서 어떻게 설명할지 정리한다. 목적은 "어느 프레임워크가 더 좋다"가 아니라, 각 도구가 해결하는 문제, 팀의 언어/운영 스택, 그리고 이 교안에서 Pydantic AI를 중심으로 잡는 이유를 명확히 하는 것이다.

## 한 줄 요약

| 도구 | 한 줄 포지션 | 수업에서의 위치 |
| --- | --- | --- |
| LangChain | 모델, tool, middleware, agent loop를 빠르게 조립하는 범용 agent framework | 1회차에서 비교 대상으로 소개 |
| LangGraph | 오래 실행되는 stateful agent/workflow를 제어하는 low-level orchestration runtime | 4회차 graph 설명에서 비교 |
| Spring AI | Spring Boot/JVM 애플리케이션에 AI model, RAG, tool calling, structured output을 붙이는 Spring-native AI abstraction | Python 밖의 비교 대상으로 소개 |
| Pydantic AI | Python type hint와 Pydantic validation을 중심에 둔 type-safe agent framework | 본편 실습의 기준 프레임워크 |

## 공식 문서 기준 핵심 차이

LangChain 공식 문서는 `create_agent`를 모델, prompt, tools, middleware를 감싸는 configurable harness로 설명한다. 표준 모델 인터페이스, middleware, LangSmith 관측/평가, 그리고 LangGraph 기반 durable execution을 강점으로 둔다. 따라서 이미 LangChain 생태계의 integration과 middleware를 적극 활용해야 하는 프로젝트라면 LangChain으로 시작하는 것이 자연스럽다.

LangGraph 공식 문서는 LangGraph를 long-running, stateful agent를 만들고 운영하기 위한 low-level orchestration framework/runtime으로 설명한다. durable execution, persistence, streaming, human-in-the-loop, memory, LangSmith 기반 디버깅이 중심이다. LangChain component를 자주 쓰지만 LangChain 없이도 사용할 수 있다. 따라서 agent loop보다 workflow runtime과 상태 관리가 핵심이면 LangGraph가 비교 대상이다.

Spring AI 공식 문서는 Spring AI의 목적을 AI 기능을 Spring 애플리케이션에 불필요한 복잡성 없이 통합하는 것으로 설명한다. LangChain/LlamaIndex 같은 Python 프로젝트에서 영감을 받았지만 직접 port는 아니며, AI 애플리케이션이 Python 개발자만의 영역이 아니라 여러 언어로 확산된다는 전제에서 출발한다. 핵심은 enterprise data/API와 AI model을 연결하는 것이고, `ChatClient`, Advisor API, tool calling, structured output, vector store/RAG abstraction을 Spring Boot 방식으로 제공한다. 따라서 조직의 주력 서비스가 Java/Spring이고 기존 DI, configuration, observability, deployment 흐름을 유지해야 한다면 Spring AI가 자연스러운 선택지다.

Pydantic AI 공식 문서는 `Agent[Deps, Output]`, dependency injection, `RunContext`, tool schema, Pydantic output validation, Logfire/Evals, Pydantic Graph를 강조한다. Python backend 개발자가 타입, validation, 테스트, 관측을 같은 언어로 다루게 하는 데 초점이 있다. 따라서 이 교안처럼 "LLM/RAG/Agent 서비스를 백엔드 앱 경계로 설계한다"는 목표에는 Pydantic AI가 설명 기준으로 적합하다.

## 언제 무엇을 선택하나

| 목적/상황 | 더 자연스러운 선택 | 이유 |
| --- | --- | --- |
| Python 타입, Pydantic 모델, FastAPI 응답 schema와 agent output을 같은 방식으로 다루고 싶다 | Pydantic AI | `deps_type`, `output_type`, Pydantic validation, static type checking 흐름이 수업 목표와 맞다 |
| 다양한 provider, retriever, middleware, integration을 빠르게 조립하고 싶다 | LangChain | 범용 agent framework와 integration ecosystem이 강하다 |
| workflow가 오래 실행되고, 중단/재개, persistence, human-in-the-loop, streaming runtime이 핵심이다 | LangGraph | orchestration runtime 자체가 주제다 |
| 기존 서비스가 Spring Boot이고 Java/Kotlin 코드, Bean, properties, actuator/observability, JVM 배포 흐름을 유지해야 한다 | Spring AI | `ChatClient`, Advisor, ToolCallback, VectorStore가 Spring 방식으로 통합된다 |
| Java/Spring 팀이 내부 업무 시스템에 RAG 또는 tool calling을 붙이고 싶다 | Spring AI | 기존 service/repository/security 계층을 AI tool과 RAG context로 연결하기 쉽다 |
| typed state machine을 Python 타입으로 작게 설명하고 싶다 | Pydantic Graph | Pydantic AI 교안 안에서 graph 개념을 과하지 않게 연결할 수 있다 |
| LangChain 기반 agent를 production runtime으로 확장하고 싶다 | LangChain + LangGraph + LangSmith | 공식 stack이 build/test/deploy/monitor 흐름으로 통합돼 있다 |
| FastAPI 백엔드 수업에서 "LLM 호출을 타입 있는 API 경계로 만드는 법"을 먼저 가르치고 싶다 | Pydantic AI | 학생이 이미 배운 Python type hint와 Pydantic/FastAPI 감각을 재사용할 수 있다 |

## 목적별 판단 축

프레임워크 선택은 agent 기능 목록만 보고 결정하지 않는다. 적어도 아래 네 가지를 함께 본다.

| 판단 축 | 질문 | 선택에 미치는 영향 |
| --- | --- | --- |
| 주력 언어와 팀 역량 | 팀이 Python backend에 익숙한가, Spring/JVM에 익숙한가? | Python/FastAPI/Pydantic 팀이면 Pydantic AI, Spring Boot 팀이면 Spring AI가 운영 비용이 낮다 |
| 필요한 추상화 수준 | agent loop를 빠르게 조립할 것인가, workflow runtime을 직접 제어할 것인가? | agent harness는 LangChain/Pydantic AI/Spring AI, long-running orchestration은 LangGraph나 durable execution 계층을 본다 |
| 타입/스키마 경계 | 응답 schema와 tool 인자를 어떤 타입 시스템으로 관리할 것인가? | Python type hint/Pydantic이면 Pydantic AI, Java class/record/Bean 기반이면 Spring AI가 자연스럽다 |
| 운영 생태계 | 관측, 설정, 배포, 보안, DI를 어떤 stack에 맞출 것인가? | LangSmith 중심이면 LangChain/LangGraph, Logfire/Pydantic stack이면 Pydantic AI, Spring Boot 운영 체계면 Spring AI |

강의에서는 이 판단 축을 학생에게 먼저 보여준다. "AI agent framework"라는 이름이 같아도 실제 선택은 언어, 기존 서비스, 운영 체계, 팀이 디버깅할 수 있는 타입 시스템에 의해 달라진다.

## 수업에 넣는 위치

1회차 Pydantic AI 기본에는 "왜 Pydantic AI로 시작하는가"를 넣는다. 학생이 LangChain이나 Spring AI를 이미 들어봤을 가능성이 있으므로, 경쟁 구도가 아니라 목적 구도로 설명한다. "LangChain은 넓은 integration과 middleware 중심, Spring AI는 Spring/JVM 앱 통합 중심, Pydantic AI는 Python 타입과 validation 중심"이라고 구분한다.

4회차 Evals/Graph/Multi-agent에는 "LangGraph와 Pydantic Graph는 같은 graph라는 단어를 쓰지만 같은 층위가 아니다"를 넣는다. LangGraph는 long-running stateful workflow runtime이고, Pydantic Graph는 typed Python graph/state machine이다. 이 교안은 4회차에서 graph 개념을 익히고, 5회차에서 DBOS로 durable execution을 별도 주제로 다룬다.

분석 문서에는 이 페이지를 두어 수업 범위 결정을 설명한다. 본편은 Pydantic AI 중심으로 진행하지만, 수강생이 LangChain/LangGraph/Spring AI와 비교해 위치를 잡을 수 있게 한다.

## 강사가 강조할 문장

"LangChain, LangGraph, Spring AI, Pydantic AI는 모두 AI 애플리케이션을 만든다는 큰 범주에 있지만 같은 층위와 같은 생태계의 도구가 아닙니다. LangChain은 넓은 agent framework, LangGraph는 orchestration runtime, Spring AI는 Spring/JVM 앱에 AI 기능을 통합하는 abstraction, Pydantic AI는 Python 타입과 validation을 중심에 둔 agent framework입니다. 목적과 팀 스택에 따라 선택은 달라집니다. 이 수업은 Python 백엔드 개발자가 타입 있는 앱 경계를 만드는 것이 목표라서 Pydantic AI를 기준으로 설명합니다."

## 참고한 공식 문서

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Spring AI introduction](https://docs.spring.io/spring-ai/reference/index.html)
- [Spring AI ChatClient](https://docs.spring.io/spring-ai/reference/api/chatclient.html)
- [Spring AI Tool Calling](https://docs.spring.io/spring-ai/reference/api/tools.html)
- [Spring AI RAG](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)
- [Spring AI Structured Output](https://docs.spring.io/spring-ai/reference/api/structured-output-converter.html)
- [Spring AI Vector Databases](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)
- [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/)
- [Pydantic AI agents](https://pydantic.dev/docs/ai/core-concepts/agent/)
- [Pydantic Graph overview](https://pydantic.dev/docs/ai/graph/graph/)
