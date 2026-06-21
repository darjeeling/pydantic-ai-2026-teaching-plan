# 0회차 슬라이드: uv, VS Code, ty, 모델 공급자

## 오늘의 결과물

- provider별 모델 문자열
- uv 기반 `.venv`
- VS Code + ty 자동완성
- `.env` 설정표
- provider smoke test
- 1회차에서 사용할 `COURSE_MODEL`

## 왜 별도 회차인가

1회차는 Agent, Logfire, tools, deps, output type만으로도 이미 빽빽하다.

Provider 설정은 코드 문제라기보다 계정, 권한, region, 비용, 데이터 경로 문제다.

개발 환경 설정도 코드보다 재현성 문제다.

## 실습 도구

- `uv`: dependency, lockfile, `.venv`, command runner
- VS Code: workspace 설정과 tasks
- `ty`: type checker + language server
- Ruff: lint, format, import 정리
- Windows: WSL 2 + VS Code WSL extension

AI assistant는 쓰지 않는다.

## Windows / WSL

PowerShell:

```powershell
wsl --install
```

WSL Ubuntu:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
mkdir -p ~/src
cd ~/src
git clone <repo-url>
cd pydantic-ai-2026-teaching-plan
code .
```

- `/mnt/c/...`에 clone하지 않는다.
- VS Code 왼쪽 아래가 `WSL: Ubuntu`인지 확인한다.

## uv

```bash
uv sync
uv run python --version
uv run ty check
uv run ruff check examples
```

`uv.lock`은 손으로 고치지 않는다.

## VS Code + ty

- 추천 확장: ty, Ruff, Python
- Windows host 확장: WSL
- Python interpreter: `.venv`
- Python language server: `None`
- 자동완성/hover/go-to-definition: ty
- Copilot/Copilot Chat은 workspace에서 비활성

## Mental Model

```text
Agent code
  -> provider:model-id
  -> credentials + account permissions
```

## Provider Prefix

| Provider | Prefix | Credential |
| --- | --- | --- |
| OpenAI | `openai:` | `OPENAI_API_KEY` |
| OpenRouter | `openrouter:` | `OPENROUTER_API_KEY` |
| AWS Bedrock | `bedrock:` | AWS credential + region |
| Google AI Studio | `google:` | `GOOGLE_API_KEY` |
| Google Cloud Vertex | `google-cloud:` | ADC/service account/API key |

## Capability Check

provider 이름만 보고 고르면 안 된다.

- structured output
- tool calling
- image/document input
- streaming
- region/data path
- logging/retention

필요 기능을 먼저 정하고 model을 고른다.

## COURSE_MODEL

```bash
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6
COURSE_MODEL=bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0
COURSE_MODEL=google:gemini-3-pro-preview
COURSE_MODEL=google-cloud:gemini-3-pro-preview
```

## Smoke Test

```bash
uv run python examples/00_providers/provider_smoke_test.py --dry-run

COURSE_MODEL=google:gemini-3-pro-preview \
  uv run python examples/00_providers/provider_smoke_test.py
```

## OpenRouter

- 한 key로 여러 downstream model 사용
- 모델 비교 실습에 편함
- 데이터 경로와 fallback 정책 확인 필요

## Bedrock

- AWS account, IAM, region, model access 필요
- `AWS_DEFAULT_REGION` 누락이 흔한 실수
- Bedrock/boto3 진단은 Logfire와 AWS 로그를 같이 본다.

## Google

- `google:`: AI Studio / Gemini API
- `google-cloud:`: Google Cloud / Vertex AI
- 예전 `google-gla:`, `google-vertex:` prefix는 새 교안에서 쓰지 않는다.

## 1회차로 넘기는 기준

- dry-run에서 provider가 맞게 잡힌다.
- VS Code에서 ty completion이 동작한다.
- 실제 호출 또는 강사 demo를 확인했다.
- `COURSE_MODEL`이 정해졌다.
- credential이 없는 수강생도 실패 원인과 다음에 확인할 곳을 설명할 수 있다.
