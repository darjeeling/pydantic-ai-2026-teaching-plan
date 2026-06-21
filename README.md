# Pydantic AI 2026 Teaching Plan

Pydantic AI를 처음 배우는 개발자를 위한 교안입니다. 2일 워크숍 분량을 2~3시간짜리 사전 준비 1회와 본 수업 5회 실습으로 나눴습니다. 수강생이 AI 앱을 처음 다룬다고 가정하되, 백엔드 실무자가 운영 환경에서 마주치는 타입, 도구, DB, 평가, 격리, 내구 실행, 웹 API 관점을 함께 다룹니다.

이 과정은 Python 문법이나 전통 ML 모델 학습이 아니라, Python으로 LLM/RAG/Agent 서비스를 만드는 앱 엔지니어링에 초점을 둡니다. pandas/EDA/scikit-learn, MLflow/Airflow, vLLM/Kubernetes는 본편에서 운영 경계로만 짚고 심화반 후보로 분리합니다.

## Course Goals

- Pydantic AI의 `Agent`, instructions, tools, dependencies, structured output을 사용한다.
- `uv`, VS Code, `ty` language server로 AI assistant 없는 재현 가능한 실습 환경을 만든다.
- OpenAI, OpenRouter, AWS Bedrock, Google AI Studio, Google Cloud Vertex 모델 공급자를 구분하고 `COURSE_MODEL`로 바꿔 실행한다.
- 1회차부터 Logfire를 붙여 agent run, model request, tool call trace를 관찰한다.
- pgvector 기반 RAG를 직접 만들고 agent tool로 연결한다.
- RAG를 데이터 품질, metadata, source audit, GraphRAG 심화 가능성 관점에서 설명한다.
- Pydantic AI Harness의 `CodeMode`와 Monty sandbox가 왜 필요한지 이해한다.
- Pydantic Evals, RAG/tool-use eval, Pydantic Graph, multi-agent workflow를 구분해서 쓴다.
- DBOS로 agent 실행과 graph checkpoint/resume을 durable workflow 관점에서 설명한다.
- FastAPI 기반 기본 챗봇을 만들고 message history, 운영 체크리스트, 서비스화 경계를 설명한다.

## Schedule

| 회차 | 시간 | 주제 | 결과물 |
| --- | ---: | --- | --- |
| 0 | 2h | uv, VS Code, ty, 모델 공급자 실행 환경 | AI assistant 없는 자동완성 환경, provider smoke test, `COURSE_MODEL` 설정 |
| 1 | 2~3h | Pydantic AI 기본, Logfire, tools, deps, structured output | trace가 보이는 교육 상담 agent |
| 2 | 2~3h | RAG with Postgres pgvector | 문서 검색 tool, Data-Centric RAG, GraphRAG 맛보기 |
| 3 | 2~3h | Monty sandbox, CodeMode | 여러 tool 호출을 sandboxed code execution으로 묶는 agent |
| 4 | 2~3h | Evals, Graph, multi-agent workflow | 품질 eval, RAG/tool-use eval, typed graph, agent delegation 예제 |
| 5 | 2~3h | DBOS durable execution, graph resume, FastAPI chatbot | durable agent, graph checkpoint/resume, 웹 챗봇, 서비스화 체크리스트 |

각 회차의 실제 진행 기준은 `lessons/` 문서입니다. 모든 레슨은 120분 운영안, 강사용 설명 스크립트, 라이브코딩 흐름, 실습, 리뷰 질문을 담고 있습니다. `slides/`는 발표 보조 자료라 짧게 유지했습니다. 0회차는 credential과 cloud 권한 문제를 1회차에서 떼어내기 위한 사전 준비 수업입니다.

## Repository Layout

- `lessons/`: 회차별 Markdown 교안
- `slides/`: 회차별 슬라이드 초안
- `examples/`: 강사용 완성 예제
- `exercises/`: 수강생 실습 지시서
- `references/`: 최신 Pydantic 관련 레포 clone 및 조사 기준
- `docs/lesson-review-2026-06-11.md`: 2시간 수업 가능성 기준의 교안 리뷰
- `docs/python-ai-topic-map.md`: Python AI 교육 토픽 분석과 현재 교안의 대응표
- `.github/workflows/evals.yml`: deterministic eval과 수동 model-switch eval을 분리한 CI 예시

## Setup

```bash
uv sync
cp .env.example .env
```

`.env`에 사용할 provider credential을 설정합니다. 기본값이 OpenAI라서 `OPENAI_API_KEY`와 `COURSE_MODEL=openai:gpt-5.5`만 넣으면 바로 시작할 수 있습니다. 기존 예제와의 호환을 위해 `OPENAI_MODEL`도 fallback으로 남겨 두었습니다. Pydantic AI가 `openai:` prefix에 대해 v2 동작 변경 경고를 띄우면, 현재 Chat Completions 동작을 고정하려면 `COURSE_MODEL=openai-chat:gpt-5.5`를, Responses API를 명시하려면 `COURSE_MODEL=openai-responses:gpt-5.5`를 씁니다.

VS Code 실습은 `.vscode/`의 workspace 설정을 따릅니다. 공통으로 권장하는 확장은 `astral-sh.ty`, `charliermarsh.ruff`, `ms-python.python`이고, Windows host에서는 WSL 연결용 `ms-vscode-remote.remote-wsl`도 필요합니다. AI assistant는 실습 도구로 쓰지 않습니다. 자동완성, hover, go-to-definition은 `ty` language server로 확인합니다.

```bash
uv run ty check
uv run ruff check examples
```

## Documentation Site

이 repo는 GitHub Pages 배포를 염두에 둔 Sphinx 문서 사이트를 `docs/` 아래에 둡니다. 홈에는 커리큘럼을 두고, 왼쪽 내비게이션에서 강사용 교안, 실습, 슬라이드, 분석 문서로 이동할 수 있게 구성했습니다.

로컬 빌드:

```bash
uv sync --group docs
uv run --group docs sphinx-build -b html docs docs/_build/html
```

빌드 결과는 `docs/_build/html/index.html`에서 확인합니다. GitHub Pages 배포는 `.github/workflows/docs.yml`이 맡습니다. 저장소 URL 아이콘을 Sphinx 테마에 표시하려면 workflow나 Pages 환경에서 `DOCS_SOURCE_REPOSITORY`를 `https://github.com/<owner>/<repo>/` 형식으로 설정합니다.

## Maintenance CI

`.github/workflows/maintenance.yml`은 매주 dependency와 Python compatibility를 확인합니다.

- `uv lock --upgrade` 후 API-free 예제와 Sphinx 빌드가 통과하면 dependency refresh PR을 만든다.
- Python `3.11`, `3.12`, `3.13`, `3.14` matrix로 compile, lint, `ty check`, deterministic eval, graph/HITL 예제를 실행한다.
- Sphinx는 nitpicky HTML build, doctest builder, scheduled linkcheck로 확인한다.
- 실제 provider 호출 예제는 API key가 필요하므로 public scheduled CI에서는 실행하지 않는다.

### Windows / WSL

Windows 수강생은 Windows native Python 환경이 아니라 WSL 2에서 실습합니다. 이 repo의 VS Code 설정이 `.venv/bin/python`을 기준으로 하기 때문에, Windows에서도 WSL 안에서 `code .`로 열어야 Linux/macOS와 같은 경로로 동작합니다.

먼저 PowerShell에서 WSL을 설치합니다.

```powershell
wsl --install
```

재부팅과 Ubuntu 초기 계정 설정을 마쳤으면, Ubuntu/WSL 터미널에서 이어 진행합니다.

```bash
sudo apt update
sudo apt install -y git curl
curl -LsSf https://astral.sh/uv/install.sh | sh
exec $SHELL -l
mkdir -p ~/src
cd ~/src
git clone <repo-url>
cd pydantic-ai-2026-teaching-plan
code .
```

주의할 점:

- repo는 `C:\Users\...`나 `/mnt/c/...`가 아니라 WSL 파일 시스템의 `~/src/...` 아래에 둔다.
- VS Code는 Windows에 설치하고, WSL extension으로 이 폴더를 연다.
- VS Code 왼쪽 아래가 `WSL: Ubuntu`처럼 표시되는지 확인한다.
- `uv`, `.venv`, `ty`, provider 실행은 모두 WSL 터미널에서 실행한다.

다른 모델 공급자를 쓰려면 0회차 교안을 먼저 진행합니다.

```bash
uv run python examples/00_providers/provider_smoke_test.py --dry-run

COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6 \
  uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

1회차에서는 먼저 raw HTTPX 호출을 실행해 request/response가 실제 파일에 어떻게 남는지 봅니다. 이 로그에는 prompt와 response body가 그대로 담기므로 수업용으로만 씁니다.

```bash
uv run python examples/01_basics/httpx_raw_api_log.py
tail -n 20 logs/httpx-raw-api.log
```

그다음 Pydantic AI 예제부터는 안전한 breadcrumb 로그만 남깁니다. 기본 로그는 payload를 빼고 model string, request 시작/종료, usage, HTTPX request line/status 정도만 기록합니다.

```bash
uv run python examples/01_basics/hello_agent.py
tail -n 30 logs/api-calls.log
```

로그 위치는 `COURSE_API_LOG_FILE=logs/api-calls.log`로 바꿀 수 있고, 로그가 필요 없으면 `COURSE_API_LOG_DISABLED=1`을 설정합니다.

RAG 실습은 pgvector가 필요합니다.

```bash
docker compose up -d pgvector
uv run python examples/02_rag/load_docs.py
uv run python examples/02_rag/rag_agent.py "Pydantic AI에서 tool은 언제 쓰나요?"
```

OpenAI embedding 대신 로컬 embedding을 쓰려면 2회차 교안의 "Embedding model 선택"을 참고합니다. 예를 들어 Ollama를 쓸 수 있습니다.

```bash
ollama pull embeddinggemma
EMBEDDING_PROVIDER=ollama EMBEDDING_MODEL=embeddinggemma EMBEDDING_DIMENSIONS= RESET_RAG_TABLE=1 \
  uv run python examples/02_rag/load_docs.py
```

## Instructor Notes

- 초보자에게는 "LLM이 답하는 코드"보다 "LLM이 호출할 수 있는 경계를 타입으로 설계하는 코드"라는 관점을 반복한다.
- provider 설정은 0회차에서 끝내고, 1회차부터는 `COURSE_MODEL`이 이미 smoke test를 통과했다고 가정한다.
- 백엔드 관점에서는 API key 관리, DB connection lifecycle, retries, idempotency, eval regression, observability, durable execution을 각 회차마다 짧게 연결한다.
- RAG, sandbox, multi-agent, durable execution은 모두 agent를 똑똑하게 만드는 기능이지만 해결하는 문제가 다르다. 각 기능을 도입하기 전에 "이 기능이 없으면 어떤 장애/비용/위험이 생기는가"를 먼저 묻는다.
- AI coding tool은 본편 실습 도구로 쓰지 않는다. 대신 AI가 만든 코드도 `ty`, `ruff`, test, eval, trace로 검증해야 한다는 습관을 부록에서 다룬다.

## Reference Sources

이 교안은 2026-06-11 기준 최신 자료를 확인하며 작성했습니다.

- Pydantic AI: https://github.com/pydantic/pydantic-ai
- Pydantic AI docs: https://pydantic.dev/docs/ai/overview/
- uv docs: https://docs.astral.sh/uv/
- ty docs: https://docs.astral.sh/ty/
- ty VS Code integration: https://docs.astral.sh/ty/editors/
- Microsoft WSL setup: https://learn.microsoft.com/en-us/windows/wsl/setup/environment
- VS Code WSL development: https://code.visualstudio.com/docs/remote/wsl
- Model providers overview: https://pydantic.dev/docs/ai/models/
- OpenRouter provider: https://pydantic.dev/docs/ai/models/openrouter/
- AWS Bedrock provider: https://pydantic.dev/docs/ai/models/bedrock/
- Google providers: https://pydantic.dev/docs/ai/models/google/
- Function tools: https://pydantic.dev/docs/ai/tools-toolsets/tools/
- RAG example: https://pydantic.dev/docs/ai/examples/data-analytics/rag/
- Pydantic Evals: https://pydantic.dev/docs/ai/evals/evals/
- Pydantic Graph: https://pydantic.dev/docs/ai/graph/graph/
- Multi-agent applications: https://pydantic.dev/docs/ai/multi-agent-applications/
- Durable execution with DBOS: https://pydantic.dev/docs/ai/integrations/durable_execution/dbos/
- HTTP request retries: https://pydantic.dev/docs/ai/retries/
- Monty: https://github.com/pydantic/monty
- Pydantic AI Harness: https://github.com/pydantic/pydantic-ai-harness
