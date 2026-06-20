# Pydantic AI 키워드 누적 목록

챕터별로 등장하는 핵심 키워드를 누적 관리한다. 참조 사이트처럼 새로 등장한 개념과 다시 연결되는 개념을 구분해서, 수강생이 "지금 배우는 기능이 앞 회차의 어떤 문제를 이어받는지" 확인할 수 있게 한다.

- 새 키워드: 해당 챕터에서 처음 본격적으로 다루는 개념
- 재등장 키워드: 이전 챕터에서 배운 개념이 다른 문제 안에서 다시 쓰이는 경우
- 심화 키워드: 본편에서는 판단 기준만 다루고 별도 심화반으로 넘기는 개념

---

## Ch.0 - 모델 공급자와 개발 환경

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| `uv` | 새 키워드 | Python 버전, dependency, 실행 명령을 재현 가능하게 고정하는 프로젝트 도구 |
| `.venv` | 새 키워드 | 수업 repo 안에서 격리된 Python 실행 환경 |
| `uv.lock` | 새 키워드 | 실제 설치할 dependency 버전을 잠그는 파일 |
| VS Code Remote WSL | 새 키워드 | Windows에서도 Linux 기준 경로와 도구 체인을 쓰게 하는 개발 방식 |
| `ty` | 새 키워드 | AI assistant 없이 타입 기반 자동완성, hover, diagnostics를 제공하는 language server |
| `COURSE_MODEL` | 새 키워드 | 수업 예제에서 provider/model을 바꿔 끼우는 공통 환경 변수 |
| provider capability | 새 키워드 | structured output, tool calling, streaming, multimodal input 지원 여부 |
| credential / region / project | 새 키워드 | AI 앱 실행 실패가 코드 문제가 아니라 계정/권한 문제일 수 있음을 보여주는 운영 경계 |

### 키워드 연관 관계

```{mermaid}
graph LR
    UV["uv"] --> VENV[".venv"]
    UV --> LOCK["uv.lock"]
    VSC["VS Code"] --> TY["ty language server"]
    WSL["Remote WSL"] --> VSC
    CM["COURSE_MODEL"] --> Provider["provider:model-id"]
    Provider --> Cred["credential"]
    Provider --> Region["region/project"]
    Provider --> Cap["model capability"]
    Cap --> Tool["tool calling"]
    Cap --> Output["structured output"]
```

---

## Ch.1 - Pydantic AI 기본

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| `Agent` | 새 키워드 | model, instructions, tools, deps, output validation을 묶는 LLM 앱 경계 |
| instructions | 새 키워드 | 매 요청마다 반복되는 agent 행동 규칙 |
| tool calling | 새 키워드 | 모델이 애플리케이션 함수를 호출하겠다고 요청하고 framework가 실행하는 흐름 |
| `RunContext` | 새 키워드 | tool이 현재 실행의 deps, usage 같은 문맥에 접근하는 통로 |
| `deps_type` | 새 키워드 | 요청 단위 의존성과 권한/상태를 타입으로 고정하는 장치 |
| `output_type` | 새 키워드 | LLM 응답을 API response schema처럼 검증하는 Pydantic 모델 |
| Logfire trace | 새 키워드 | agent run, model request, tool call, usage를 관찰하는 실행 증거 |
| provider capability | 재등장 (Ch.0) | 모든 모델이 tool calling과 structured output을 같은 방식으로 지원하지는 않는다 |

### 키워드 연관 관계

```{mermaid}
graph LR
    Agent["Agent"] --> Model["model"]
    Agent --> Inst["instructions"]
    Agent --> Tools["tools"]
    Agent --> Deps["deps_type"]
    Agent --> Output["output_type"]
    Tools --> Ctx["RunContext"]
    Ctx --> Deps
    Agent --> Trace["Logfire trace"]
    Model -.-> Cap["provider capability<br/>(Ch.0)"]
```

---

## Ch.2 - RAG 만들기

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| ingestion | 새 키워드 | 원본 문서를 검색 가능한 단위로 수집하고 정리하는 과정 |
| chunking | 새 키워드 | 문서를 모델이 검색/사용하기 좋은 작은 단위로 나누는 작업 |
| embedding | 새 키워드 | 텍스트 의미를 vector로 바꾸어 유사도 검색에 쓰는 표현 |
| pgvector | 새 키워드 | Postgres 안에서 vector 저장과 검색을 가능하게 하는 확장 |
| metadata | 새 키워드 | source, title, timestamp, 권한 같은 검색/감사 보조 정보 |
| answer policy | 새 키워드 | 검색 근거만 사용할지, 모르면 어떻게 말할지 정하는 답변 규칙 |
| Data-Centric RAG | 새 키워드 | 모델보다 문서 품질, 최신성, 중복, metadata 관리에 초점을 둔 RAG 관점 |
| GraphRAG | 심화 키워드 | 문서 간 entity/relation을 저장해야 할 때 검토하는 관계 기반 검색 패턴 |
| tool calling | 재등장 (Ch.1) | retrieval을 agent tool로 감싸서 모델이 필요할 때 검색하게 만든다 |
| Logfire trace | 재등장 (Ch.1) | 검색된 chunk와 tool 인자를 확인해 RAG 실패 위치를 좁힌다 |

### 키워드 연관 관계

```{mermaid}
graph LR
    Docs["Markdown docs"] --> Ingest["ingestion"]
    Ingest --> Chunk["chunking"]
    Chunk --> Embed["embedding"]
    Embed --> PG["pgvector"]
    PG --> Retrieve["retrieve tool"]
    Retrieve --> Agent["Agent<br/>(Ch.1)"]
    Retrieve --> Meta["metadata"]
    Agent --> Policy["answer policy"]
    Policy --> Source["source audit"]
    Meta --> DCRAG["Data-Centric RAG"]
    DCRAG -.-> GraphRAG["GraphRAG<br/>(심화)"]
```

---

## Ch.3 - Monty와 CodeMode

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| sandbox | 새 키워드 | 모델 작성 코드가 host 권한을 그대로 갖지 않게 제한하는 실행 경계 |
| Monty | 새 키워드 | LLM tool orchestration을 위한 제한된 Python subset/runtime |
| CodeMode | 새 키워드 | 여러 tool 호출과 로컬 계산을 sandboxed code execution으로 묶는 Pydantic AI Harness 기능 |
| capability | 새 키워드 | sandbox 안에서 허용되는 행동의 목록 |
| host boundary | 새 키워드 | repo, 파일 시스템, network, credential 같은 실제 실행 환경과의 경계 |
| approval | 재등장/예고 | 위험 tool이나 side effect에는 별도 승인 경계가 필요하다 |
| tool calling | 재등장 (Ch.1) | CodeMode는 일반 tool calling이 많아질 때의 비용과 복잡도를 줄이는 대안이다 |
| Logfire trace | 재등장 (Ch.1) | CodeMode가 어떤 code와 tool 호출로 실행됐는지 관찰한다 |

### 키워드 연관 관계

```{mermaid}
graph LR
    Agent["Agent"] --> CodeMode["CodeMode"]
    CodeMode --> Monty["Monty sandbox"]
    Monty --> Cap["capabilities"]
    Cap --> SafeTools["allowed tools"]
    Host["host boundary"] -.-> Monty
    CodeMode --> LocalCalc["local calculation"]
    CodeMode --> ToolBatch["tool call batching"]
    Risk["dangerous side effect"] --> Approval["approval gate<br/>(Ch.4)"]
```

---

## Ch.4 - Evals, Graph, Multi-agent

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| Pydantic Evals | 새 키워드 | agent 품질을 case와 evaluator로 반복 확인하는 평가 도구 |
| deterministic eval | 새 키워드 | API key 없이도 항상 같은 판정을 내릴 수 있는 회귀 방지 평가 |
| model-switch eval | 새 키워드 | 모델 후보를 바꾸기 전 pass rate, usage, latency를 비교하는 평가 |
| tool-use eval | 새 키워드 | 답변뿐 아니라 tool 선택, forbidden tool, approval/refusal policy를 검증하는 평가 |
| Pydantic Graph | 새 키워드 | 상태 전이와 분기를 타입이 있는 node/edge로 표현하는 workflow 도구 |
| multi-agent | 새 키워드 | researcher, writer, reviewer처럼 역할이 명확히 나뉠 때 쓰는 설계 패턴 |
| human approval gate | 새 키워드 | 모델 판단이 아니라 사람이 책임지고 승인해야 하는 action 경계 |
| RAG source audit | 재등장 (Ch.2) | RAG 답변이 실제 검색 근거를 사용했는지 평가한다 |
| sandbox/approval | 재등장 (Ch.3) | 코드 실행과 side effect는 권한 경계와 함께 평가해야 한다 |

### 키워드 연관 관계

```{mermaid}
graph LR
    Failure["quality regression"] --> Eval["Pydantic Evals"]
    Eval --> Deterministic["deterministic eval"]
    Eval --> ModelSwitch["model-switch eval"]
    Eval --> ToolUse["tool-use eval"]
    Workflow["fixed workflow"] --> Graph["Pydantic Graph"]
    Graph --> Nodes["retrieve -> draft -> review"]
    Roles["role separation"] --> Multi["multi-agent"]
    Multi --> Researcher["researcher"]
    Multi --> Reviewer["reviewer"]
    SideEffect["publish / delete / email"] --> Human["human approval gate"]
```

---

## Ch.5 - Durable Execution과 기본 챗봇

| 키워드 | 분류 | 한 줄 설명 |
| --- | --- | --- |
| retry | 새 키워드 | 실패한 호출을 다시 시도하는 좁은 복구 전략 |
| durable execution | 새 키워드 | 완료된 step을 보존하고 중단 지점 이후부터 재개하는 실행 모델 |
| DBOS | 새 키워드 | Python workflow/step을 durable하게 실행하기 위한 프레임워크 |
| checkpoint/resume | 새 키워드 | graph 상태와 다음 node를 저장해 중단 뒤 이어서 실행하는 패턴 |
| idempotency | 새 키워드 | 같은 요청이 반복돼도 side effect가 중복되지 않게 만드는 성질 |
| message history | 새 키워드 | 챗봇 대화 맥락을 backend에서 저장하고 재사용하는 기록 |
| FastAPI chatbot | 새 키워드 | agent를 HTTP API와 UI로 연결하는 최소 서비스 골격 |
| human approval gate | 재등장 (Ch.4) | 사람이 늦게 승인해도 workflow 상태를 잃지 않아야 한다 |
| Pydantic Graph | 재등장 (Ch.4) | graph는 상태 전이를 표현하고, durable execution은 저장/재개를 맡는다 |

### 키워드 연관 관계

```{mermaid}
graph LR
    Agent["Agent"] --> Workflow["DBOS workflow"]
    Workflow --> Step["DBOS step"]
    Step --> Checkpoint["checkpoint"]
    Checkpoint --> Resume["resume"]
    Graph["Pydantic Graph<br/>(Ch.4)"] --> State["graph state"]
    State --> Checkpoint
    Human["human approval<br/>(Ch.4)"] --> Pending["pending approval state"]
    Pending --> Resume
    UI["FastAPI chatbot"] --> History["message history"]
    UI --> RequestID["request_id"]
    RequestID --> Idem["idempotency"]
```

---

## 전체 연결

이 과정의 키워드는 기능 목록이 아니라 운영 판단 순서로 이어진다.

```{mermaid}
graph LR
    Env["Ch.0 environment/provider"] --> Agent["Ch.1 typed Agent"]
    Agent --> RAG["Ch.2 RAG"]
    RAG --> Sandbox["Ch.3 CodeMode sandbox"]
    Sandbox --> Eval["Ch.4 eval/graph/multi-agent"]
    Eval --> Durable["Ch.5 durable chatbot"]
```
