# Lesson Coverage Review - 2026-06-11

## Review 기준

요청 기준은 "각 레슨이 2시간 동안 이야기와 실습이 가능할 만큼 충분한 내용"이다. 슬라이드는 간결해도 되지만, 강사용 교안에는 말할 거리, 실습 흐름, 리뷰 질문, 운영 관점이 충분해야 한다.

## 회차별 리뷰

| 회차 | 2시간 운영안 | 강사용 이야기 | 실습 | 리뷰/질문 | 판정 |
| --- | --- | --- | --- | --- | --- |
| 0. uv/VS Code/ty/모델 공급자 | 0-120분 minute block 포함 | uv 재현성, Windows/WSL 분기, AI assistant 없는 ty 자동완성, OpenAI/OpenRouter/Bedrock/Google 차이와 capability 확인 설명 | VS Code ty completion, `uv run ty check`, provider smoke test, credential/capability checklist | 개발 환경과 provider별 실패 유형 리뷰 포함 | 충분 |
| 1. Pydantic AI 기본 | 0-120분 minute block 포함 | Agent, Logfire, instructions, tools, deps, output type 설명 확장 | Logfire trace 확인, catalog tool 개선, output schema 확장 | 오해 정리와 미니 리뷰 포함 | 충분 |
| 2. RAG | 0-120분 minute block 포함 | chunking, OpenAI/로컬 embedding, pgvector, answer policy, Data-Centric RAG, GraphRAG 맛보기 설명 확장 | 문서 추가, 재색인, retrieval 조정, Data-Centric 실패 분류, Ollama/SentenceTransformers 전환 | 운영 디버깅과 리뷰 질문 포함 | 충분 |
| 3. Monty/CodeMode | 0-120분 minute block 포함 | 모델 작성 코드의 힘과 위험, sandbox boundary 설명 확장 | selector 적용, 위험 tool 제외, debugging 관찰 | 운영 토론 포함 | 충분 |
| 4. Evals/Graph/Multi-agent | 0-120분 minute block 포함 | eval의 필요성, RAG/tool-use eval, 모델 전환 평가, CI gate, graph 사용 기준, delegation tradeoff, human approval gate 확장 | eval case 추가, RAG/tool-use policy eval, model compare, CI gate 분리, review node 수정, reviewer agent 설계, approval gate 실행 | 시나리오 분류 활동 포함 | 충분 |
| 5. DBOS/Chatbot | 0-120분 minute block 포함 | retry vs durable, graph checkpoint/resume, timeout/retry policy, request idempotency, DBOSAgent, human approval 대기/재개, message history, 서비스화/MLOps 경계, 운영 주의 확장 | DBOS name failure, graph `stop-after`/`resume`, FastAPI history/중복 클릭 확인, retry 예제 읽기, 서비스화 체크리스트, HITL durable 설계, RAG chatbot 설계 | 전체 과정 선택 기준 포함 | 충분 |

## 보완된 부분

- 각 레슨에 120분 진행안을 추가했다.
- 강사가 그대로 말할 수 있는 도입 이야기와 핵심 설명 스크립트를 추가했다.
- 라이브코딩 순서와 실패 시 대응을 추가했다.
- 실습별 강사 순회 체크와 리뷰 포인트를 추가했다.
- 초보자 오해를 정리해 수업 중 질문 대응이 가능하게 했다.
- 백엔드 실무 관점의 운영 이슈를 각 회차에 연결했다.
- 2회차에 OpenAI 외 Ollama/SentenceTransformers 로컬 embedding 선택지, dimension 확인, provider 변경 시 재색인 절차를 추가했다.
- 2회차에 Data-Centric RAG, retrieval/context/generation/metadata 실패 분류, GraphRAG/Knowledge Graph 맛보기를 추가했다.
- 4회차에 `rag_tool_use_eval.py`를 추가해 RAG source hit, tool selection, forbidden tool, approval/refusal policy를 deterministic eval로 확인하게 했다.
- 4회차에 모델 전환 eval, `agent.override(model=...)`, repeat/max_concurrency, token usage metric, PR용 deterministic CI와 수동 model-switch CI 분리 전략을 추가했다.
- 4회차에 Human-in-the-loop approval gate를 추가해 reviewer agent와 실제 사람 승인 경계를 구분하게 했다.
- 5회차에 approval 요청 저장, 승인 대기, 승인 결과로 workflow를 재개하는 durable execution 관점을 추가했다.
- 5회차에 Pydantic Graph state와 `next_node`를 저장했다가 DBOS workflow에서 재개하는 예제와 실습을 추가했다.
- 5회차에 웹 UI 중복 클릭 방지, backend `request_id` idempotency, provider timeout/retry와 DBOS retry의 계층 구분을 추가했다.
- 5회차에 FastAPI 데모를 운영 서비스로 확장할 때 필요한 secret, DB migration, rate limit, cost tracking, fallback, background workflow 체크리스트를 추가했다.
- 1회차 앞부분에 Logfire instrumentation을 추가해 agent run/model request/tool call trace를 먼저 보고 이후 RAG, CodeMode, multi-agent, DBOS 디버깅의 기준으로 삼게 했다.
- 0회차를 추가해 OpenRouter, AWS Bedrock, Google AI Studio, Google Cloud Vertex 설정을 1회차에서 분리하고 `COURSE_MODEL` 기반 smoke test를 넣었다.
- 0회차에 provider별 capability 확인 항목(structured output, tool calling, multimodal input, streaming, region/data path, logging retention)을 추가했다.
- 0회차에 VS Code workspace 설정, `uv` 프로젝트 명령, `ty` type checker/language server 실습을 추가하고 AI assistant 없이 자동완성만 쓰는 운영 규칙을 넣었다.
- Windows 수강생은 WSL 2 + VS Code WSL extension으로 열고, repo를 `/mnt/c`가 아니라 WSL 파일 시스템의 `~/src` 아래에 두도록 안내했다.
- `docs/python-ai-topic-map.md`를 추가해 Python AI 교육 토픽 분석과 현재 Pydantic AI 교안의 scope/대응 관계를 명시했다.

## 남은 리스크

- API key, Docker, pgvector가 없는 수강생은 일부 실습을 직접 실행하지 못한다. 이 경우 강사 실행 화면과 코드 리뷰 중심으로 대체해야 한다.
- Bedrock/Vertex는 계정 권한, region, project 설정이 수업 시간에 해결되지 않을 수 있다. 0회차에서는 dry-run과 강사 demo로 대체할 수 있게 운영한다.
- VS Code extension 설치 권한이 제한된 교육장에서는 강사 화면으로 ty completion을 시연하고, 수강생은 `uv run ty check` CLI로 대체해야 한다.
- Windows 교육장에서는 WSL 설치/재부팅/가상화 설정 문제가 0회차 전에 해결되어야 한다. 현장에서는 강사 예비 장비 또는 cloud devbox 대안을 준비하는 것이 좋다.
- Pydantic AI의 model prefix 정책은 v2에서 바뀔 수 있으므로 수업 직전 `COURSE_MODEL` 기본값을 다시 확인해야 한다.
- 슬라이드는 의도적으로 짧다. 실제 강의의 상세 설명은 `lessons/` 문서를 기준으로 진행해야 한다.

## 최종 판정

현재 `lessons/` 문서는 각 회차마다 2시간 강의에 필요한 이야기, 개념 설명, 라이브코딩, 실습, 리뷰 질문을 포함한다. 슬라이드는 보조 자료로 충분하며, 강의 본문은 `lessons/` 기준으로 진행 가능하다.
