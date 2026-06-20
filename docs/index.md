# Pydantic AI 2026 Teaching Plan

Pydantic AI를 처음 배우는 개발자를 위한 한국어 강의 자료다. Python 문법이나 전통 ML 모델 학습이 아니라, Python으로 LLM, RAG, Agent 서비스를 만드는 앱 엔지니어링 과정을 다룬다.

백엔드 실무자가 운영 환경에서 마주치는 타입 경계, 도구 호출, RAG 데이터 품질, 격리 실행, 평가, durable workflow, 웹 API 연결을 Ch.0 사전 준비와 Ch.1~5 본 수업으로 나누어 학습한다.

---

## 검증 기준

이 문서와 예제는 CI에서 다음 기준으로 검증한다.

| 항목 | 기준 |
| --- | --- |
| 수업 기준 Python | `3.11` (`.python-version`) |
| 주 CI Python | `3.12` |
| 주기 호환성 확인 | `3.11`, `3.12`, `3.13`, `3.14` |
| Dependency 잠금 | `uv.lock` |
| API-free 예제 | compile, lint, type check, deterministic eval, graph/HITL 예제 |
| 문서 품질 | Sphinx nitpicky HTML build, doctest builder, 주기적 linkcheck |
| Provider 호출 예제 | API key가 필요하므로 public scheduled CI에서는 dry-run 또는 로컬 실행 기준 |

Python 3.14는 2026-06 기준 최신 stable Python 라인이다. 주기 maintenance workflow는 잠긴 dependency를 새로 고친 뒤 API-free 예제와 문서 빌드가 통과할 때만 dependency refresh PR을 만든다.

## 커리큘럼

### Part 1. 실행 환경과 Agent 기초 (Ch.0~1)

| 챕터 | 제목 | 핵심 |
| --- | --- | --- |
| Ch.0 | [uv, VS Code, ty, 모델 공급자 실행 환경](lessons/00-model-providers-and-setup.md) | AI assistant 없이 재현 가능한 개발 환경을 만들고 provider별 capability를 확인한다. |
| Ch.1 | [Pydantic AI 기본, Logfire, Tool 사용](lessons/01-pydantic-ai-basics.md) | Agent, instructions, tools, deps, structured output을 타입이 있는 앱 경계로 이해한다. |

### Part 2. 검색과 격리 실행 (Ch.2~3)

| 챕터 | 제목 | 핵심 |
| --- | --- | --- |
| Ch.2 | [RAG 만들기](lessons/02-rag.md) | ingestion, chunking, embedding, pgvector, answer policy, 데이터 품질을 연결한다. |
| Ch.3 | [Monty와 CodeMode로 Agent 격리하기](lessons/03-monty-isolation.md) | 모델이 작성한 코드를 host에서 바로 실행하지 않는 sandbox 경계를 설계한다. |

### Part 3. 품질 관리와 서비스화 (Ch.4~5)

| 챕터 | 제목 | 핵심 |
| --- | --- | --- |
| Ch.4 | [Evals, Graph, Multi-agent Workflow](lessons/04-evals-graph-multi-agent.md) | 품질 평가, RAG/tool-use eval, typed graph, delegation, approval gate를 구분한다. |
| Ch.5 | [Durable Execution과 기본 챗봇](lessons/05-durable-chatbot-wrapup.md) | DBOS, checkpoint/resume, human approval, FastAPI chatbot, 운영 체크리스트로 마무리한다. |

## 대상

- Python으로 LLM/RAG/Agent 애플리케이션을 만들고 싶은 백엔드 개발자
- AI 앱 초보지만 API, 데이터베이스, 운영 환경의 기본 감각이 있는 개발자
- Pydantic AI를 단순 예제가 아니라 서비스 경계와 품질 관리 관점에서 배우고 싶은 수강생
- GitHub 기반 Tutorial 문서로 복습하고, 실습 코드를 직접 실행하며 학습하려는 수강생

## 키워드 추적

챕터별 핵심 키워드는 [키워드 목록](keywords.md)에 누적한다. 수업 중 모르는 개념이 나오면 키워드 목록에서 먼저 위치를 확인하고, 해당 챕터 교안으로 이동한다.

```{toctree}
:hidden:
:caption: 과정 안내

keywords
framework-comparison
analysis
```

```{toctree}
:hidden:
:caption: 강사용 교안

lessons/index
Ch.0 모델 공급자와 개발 환경 <lessons/00-model-providers-and-setup>
Ch.1 Pydantic AI 기본 <lessons/01-pydantic-ai-basics>
Ch.2 RAG 만들기 <lessons/02-rag>
Ch.3 Monty와 CodeMode <lessons/03-monty-isolation>
Ch.4 Evals, Graph, Multi-agent <lessons/04-evals-graph-multi-agent>
Ch.5 Durable Execution과 챗봇 <lessons/05-durable-chatbot-wrapup>
```

```{toctree}
:hidden:
:caption: 실습

exercises/index
exercises/00-providers
exercises/01-basics
exercises/02-rag
exercises/03-monty
exercises/04-evals-graph-multi-agent
exercises/05-durable-chatbot
```

```{toctree}
:hidden:
:caption: 슬라이드

slides/index
slides/00-model-providers-and-setup
slides/01-pydantic-ai-basics
slides/02-rag
slides/03-monty-isolation
slides/04-evals-graph-multi-agent
slides/05-durable-chatbot-wrapup
```
