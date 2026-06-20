# 0회차: uv, VS Code, ty, 모델 공급자 실행 환경 준비

## 2시간 목표

이 회차는 1회차 앞에 두는 사전 준비 수업이다. 1회차에 `Agent`, Logfire, tool, deps, structured output을 모두 다루면 시간이 이미 꽉 찬다. 여기에 VS Code 설정, `uv` 환경, `ty` 자동완성, OpenRouter, AWS Bedrock, Google AI Studio, Google Cloud Vertex까지 한꺼번에 설명하면 수강생은 agent 개념보다 개발 환경과 cloud 권한 문제에 시간을 쓰게 된다. 그래서 실행 환경과 공급자 설정은 0회차로 분리한다.

수업이 끝나면 수강생은 다음을 할 수 있어야 한다.

- Pydantic AI의 모델 문자열이 `provider:model-id` 형태라는 점을 설명한다.
- `uv sync`, `uv run`, `uv lock`, `uv add --dev`가 수업 환경에서 어떤 역할을 하는지 설명한다.
- VS Code workspace 설정으로 `.venv` interpreter, Ruff formatter, `ty` language server를 사용한다.
- AI assistant 없이 `ty`의 자동완성, hover, go-to-definition, diagnostics를 확인한다.
- `COURSE_MODEL` 하나로 OpenAI, OpenRouter, Bedrock, Google AI Studio, Google Cloud Vertex 모델을 바꿔 실행한다.
- 공급자별 필수 인증값, region/project 설정, 계정 권한 오류를 구분한다.
- Logfire trace를 켠 상태에서 provider smoke test를 실행하고, 실패 위치가 설정 문제인지 모델 호출 문제인지 판단한다.

완성 결과물은 VS Code에서 `ty` 자동완성이 켜진 상태로 `examples/00_providers/provider_smoke_test.py`를 읽고 수정할 수 있는 개발 환경과 provider 연결 확인표다. 실제 수업에서는 조별로 서로 다른 provider를 하나씩 맡아 dry-run과 실제 호출 결과를 공유한다.

## 사례로 시작하기: "코드는 같은데 왜 내 컴퓨터에서만 실패하나요?"

수업 첫 질문은 일부러 코드 문제가 아닌 환경 문제로 시작한다.

한 수강생은 `COURSE_MODEL=openai:gpt-5.2`로 예제가 바로 실행된다. 옆자리 수강생은 같은 repo를 clone했는데 `ModuleNotFoundError`가 난다. 또 다른 수강생은 OpenRouter key를 넣었지만 tool calling이 안 되고, Bedrock을 쓰는 수강생은 Python 에러가 아니라 `AccessDeniedException`을 본다. Google Vertex를 쓰는 수강생은 모델 이름은 맞는데 project/location 설정이 없어서 실패한다.

이 상황에서 초보자는 보통 "Pydantic AI 코드가 어렵다"고 느낀다. 하지만 실제 문제는 대부분 아래 네 층 중 하나다.

```text
Python 실행 환경
  -> dependency와 interpreter가 맞는가?
provider 문자열
  -> provider:model-id가 Pydantic AI가 기대하는 형식인가?
credential과 권한
  -> API key, IAM, ADC, project, region이 준비됐는가?
model capability
  -> 이 모델이 structured output, tool calling, streaming을 지원하는가?
```

이 사례에서 학생이 가져가야 할 감각은 "AI 앱 디버깅은 prompt만 보는 일이 아니다"이다. provider가 바뀌면 비용, region, data path, logging retention, quota, tool calling 지원 여부가 함께 바뀐다. 그래서 0회차의 핵심은 멋진 agent를 만드는 것이 아니라, 1회차부터 같은 실패를 같은 이름으로 부를 수 있게 만드는 것이다.

강사가 던질 질문:

- "이 에러는 Python import 문제인가요, provider 인증 문제인가요?"
- "`COURSE_MODEL`만 바꿨는데 실제로 바뀌는 운영 조건은 무엇인가요?"
- "같은 모델 이름이어도 AI Studio와 Vertex에서 의미가 달라지는 이유는 무엇인가요?"

## 수업 전 준비

- `uv sync`
- `cp .env.example .env`
- VS Code 설치
- VS Code 권장 확장: `astral-sh.ty`, `charliermarsh.ruff`, `ms-python.python`
- Windows 수강생은 WSL 2와 VS Code WSL extension 준비
- 최소 하나의 LLM provider credential
- Logfire hosted UI를 보려면 `uv run logfire auth` 후 `uv run logfire projects use <project>`
- 로컬 API 호출 로그는 기본적으로 `logs/api-calls.log`에 남긴다. 로그 파일은 수업 중 확인용이며 git에는 포함하지 않는다.

이 수업에서는 AI assistant를 쓰지 않는다. GitHub Copilot, Copilot Chat, Cursor/Cline류 코드 생성 기능은 꺼 두거나 사용하지 않는다. 자동완성은 `ty` language server가 제공하는 completion, hover, signature help, go-to-definition만 사용한다. 실습의 목적은 "모델이 코드를 대신 쓰는 경험"이 아니라 "타입이 있는 Python 코드가 편집기에서 어떻게 보조되는지 확인하는 경험"이다.

기본 실행 확인:

```bash
uv sync
uv run ty check
uv run ruff check examples
uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

OpenRouter 예:

```bash
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6 \
  uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

실제 호출은 API key와 계정 권한이 준비된 뒤에 실행한다.

```bash
COURSE_MODEL=google:gemini-3-pro-preview \
  uv run python examples/00_providers/provider_smoke_test.py
```

실제 호출 후에는 로컬 로그 파일에서 provider 요청이 나갔는지 확인한다.

```bash
tail -n 20 logs/api-calls.log
```

이 로그는 prompt나 response payload를 기본으로 남기지 않는다. `agent.run_sync start/done`, model string, usage, `httpx` request line/status처럼 "호출이 발생했는가"를 확인하는 breadcrumb만 남긴다. 더 깊게 봐야 할 때만 `LOGFIRE_CAPTURE_HTTPX=1`을 사용한다.

### Windows / WSL 사전 준비

Windows 수강생은 Windows native Python, PowerShell의 `uv`, WSL의 `uv`를 섞지 않는다. 이 수업에서는 WSL 2 안의 Ubuntu를 기준 환경으로 삼는다. 이유는 세 가지다.

- `.vscode/settings.json`이 `${workspaceFolder}/.venv/bin/python`을 가리킨다.
- 수업 명령과 Docker/Postgres/pgvector 흐름을 Linux 경로 기준으로 통일할 수 있다.
- `ty`, Ruff, Python import resolution이 수강생마다 다르게 보이는 일을 줄인다.

PowerShell에서 WSL을 설치한다.

```powershell
wsl --install
```

재부팅이 필요할 수 있다. Ubuntu가 처음 열리면 Linux 사용자명과 비밀번호를 만든다. 이후 모든 수업 명령은 Ubuntu/WSL 터미널에서 실행한다.

```bash
sudo apt update
sudo apt install -y git curl
curl -LsSf https://astral.sh/uv/install.sh | sh
exec $SHELL -l
```

repo는 Windows 파일 시스템이 아니라 WSL 파일 시스템에 둔다.

```bash
mkdir -p ~/src
cd ~/src
git clone <repo-url>
cd pydantic-ai-2026-teaching-plan
code .
```

강사가 강조할 점:

- `code .`는 PowerShell이 아니라 WSL 터미널에서 실행한다.
- VS Code 왼쪽 아래가 `WSL: Ubuntu`처럼 표시되어야 한다.
- `/mnt/c/Users/...` 아래에 clone하지 않는다. Linux 도구로 작업할 때는 `~/src/...` 아래가 더 빠르고 경로 문제가 적다.
- VS Code Windows 창 안에서 열려 있어도 터미널, extension host, Python interpreter는 WSL 쪽이어야 한다.
- WSL 안에서 `uv --version`, `uv run python --version`, `uv run ty check`가 통과해야 1회차로 넘어간다.

## 120분 진행안

| 시간 | 내용 | 강사 목표 | 수강생 활동 |
| --- | --- | --- | --- |
| 0-8분 | 왜 0회차인가 | agent 개념과 환경/provider 문제를 분리한다 | 자신이 쓸 OS/editor/provider 말하기 |
| 8-20분 | Windows/WSL 분기 | Windows native와 WSL을 섞지 않게 한다 | Windows 수강생은 WSL remote인지 확인 |
| 20-35분 | uv 프로젝트 환경 | `pyproject.toml`, `uv.lock`, `.venv`, `.python-version` 역할 설명 | `uv sync`, `uv run ty check` 실행 |
| 35-50분 | VS Code와 ty | AI assistant 없이 ty 자동완성/진단만 사용하게 한다 | 권장 확장 설치, `hint.` 자동완성 확인 |
| 50-60분 | 공통 환경 변수와 smoke test | `COURSE_MODEL`, `.env`, Logfire 흐름 설명 | provider dry-run 실행 |
| 60-70분 | Pydantic AI 모델 문자열 | `provider:model-id` mental model 정리 | 모델 문자열을 표에 적기 |
| 70-75분 | 휴식 | 질문 정리 | 질문 |
| 75-88분 | OpenAI와 OpenRouter | 기본 provider와 router provider 차이 설명 | OpenRouter 모델 문자열 만들기 |
| 88-100분 | Google AI Studio와 Vertex | `google:`, `google-cloud:`, ADC, project/location 설명 | Google 설정 체크리스트 작성 |
| 100-112분 | AWS Bedrock | IAM, region, model access, boto3 오류 설명 | Bedrock 설정 체크리스트 작성 |
| 112-118분 | 조별 smoke test 리뷰 | 실패 유형을 분류한다 | 결과 공유 |
| 118-120분 | 1회차 연결 | 준비된 모델로 agent 수업에 들어간다 | 사용할 `COURSE_MODEL` 확정 |

## 도입 이야기

수업을 이렇게 시작한다.

"Pydantic AI 코드는 provider가 바뀌어도 대부분 그대로 유지됩니다. 하지만 수업이 제대로 진행되려면 두 가지가 먼저 맞아야 합니다. 첫째, 모두가 같은 Python 환경에서 같은 명령을 실행해야 합니다. 둘째, 모델 공급자 설정 실패와 코드 실패를 구분할 수 있어야 합니다. OpenRouter는 하나의 key로 여러 모델을 라우팅하고, Bedrock은 IAM과 region과 모델 접근 권한이 필요하고, Google은 AI Studio와 Vertex가 서로 다른 인증/운영 모델을 가집니다. 이 차이를 모른 채 1회차 agent 실습을 시작하면 코드가 틀린 것인지 계정 설정이 틀린 것인지 구분하지 못합니다."

칠판에는 다음처럼 쓴다.

```text
Agent code
  |
  v
model string: provider:model-id
  |
  v
provider credentials + region/project + account permissions
```

핵심 메시지는 세 가지다. 첫째, `uv`는 수업의 실행 재현성을 만든다. 둘째, `ty`는 AI assistant 없이도 타입 기반 자동완성과 진단을 제공한다. 셋째, Pydantic AI의 코드 경계는 단순하지만 provider 경계는 운영 경계다. 수강생은 1회차부터 `Agent(model, ...)`을 볼 것이므로, 이 `model` 값이 단순 문자열이 아니라 배포/비용/데이터 경로를 결정한다는 감각을 먼저 가져야 한다.

## 개념 설명 스크립트

### uv 프로젝트 환경

`uv`는 이 수업의 Python package/project manager다. 수강생에게는 "pip, venv, pip-tools, 일부 poetry 역할을 한 명령 체계로 묶은 도구"라고 설명한다. 중요한 것은 속도가 아니라 재현성이다.

이 repo에서 `uv`가 관리하는 파일:

- `pyproject.toml`: 프로젝트 dependency와 tool 설정
- `uv.lock`: 실제로 설치할 dependency 버전 잠금
- `.venv/`: `uv sync`가 만드는 격리된 Python 환경
- `.python-version`: 수업 기준 Python minor version

강사가 말할 포인트:

- `uv sync`는 `pyproject.toml`과 `uv.lock`을 기준으로 `.venv`를 맞춘다.
- `uv run ...`은 `.venv`를 직접 activate하지 않아도 프로젝트 환경에서 명령을 실행한다.
- `uv add --dev ty`처럼 dependency를 추가하면 `pyproject.toml`과 `uv.lock`이 함께 바뀐다.
- `uv.lock`은 사람이 손으로 고치는 파일이 아니라 `uv`가 관리하는 파일이다.

수업에서 쓸 명령:

```bash
uv sync
uv run python --version
uv run ty check
uv run ruff check examples
uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

실패 시 대응:

- `uv: command not found`: uv 설치부터 확인한다.
- Windows에서 `uv`가 PowerShell에서는 되는데 VS Code task에서 안 되면, VS Code가 WSL remote가 아니라 Windows local로 열렸는지 확인한다.
- `.venv`가 꼬였다고 바로 삭제하지 않는다. 먼저 `uv sync`를 다시 실행한다.
- dependency를 추가해야 하면 `pip install` 대신 `uv add` 또는 `uv add --dev`를 쓴다.
- `uv.lock` 충돌이 나면 dependency 변경자가 누구인지 확인하고, 임의로 손편집하지 않는다.

### VS Code와 ty

이 수업의 VS Code 구성은 `.vscode/`에 들어 있다.

- `.vscode/extensions.json`: 추천 확장 목록
- `.vscode/settings.json`: interpreter, ty, Ruff, AI assistant 비활성화 설정
- `.vscode/tasks.json`: `uv sync`, `ty check`, `ruff check`, provider dry-run task

권장 확장:

- `astral-sh.ty`: type checker와 language server
- `charliermarsh.ruff`: lint/format/import 정리
- `ms-python.python`: Python 기본 실행/테스트 integration

명시적으로 쓰지 않는 것:

- GitHub Copilot
- Copilot Chat
- Cursor/Cline류 코드 생성 기능
- 기타 AI assistant의 코드 작성/수정 제안

강사가 이렇게 말한다.

"오늘 자동완성은 LLM이 코드를 추측해서 써 주는 기능이 아닙니다. ty가 현재 파일의 타입, dataclass field, 함수 signature, import 가능한 symbol을 보고 제공하는 language server 기능입니다. 이 차이를 분명히 해야 1회차부터 agent 코드의 타입 경계를 직접 읽고 고칠 수 있습니다."

실습:

1. VS Code에서 이 폴더를 연다.
2. 권장 확장을 설치한다.
3. `examples/00_providers/provider_smoke_test.py`를 연다.
4. `print_hint()` 안에서 `hint.`를 입력해 `name`, `prefixes`, `env_vars`, `example_model`, `note` completion이 뜨는지 확인한다.
5. `ProviderHint(...)` 생성자에 마우스를 올려 signature help와 dataclass field 정보를 본다.
6. `Course_MODEL`처럼 일부러 틀린 이름을 적어 ty diagnostic이 표시되는지 확인한 뒤 되돌린다.
7. Command Palette에서 `Tasks: Run Task`를 열고 `ty: check`를 실행한다.

체크 포인트:

- VS Code 오른쪽 아래 Python interpreter가 `.venv`를 가리키는가?
- Windows 수강생은 VS Code 왼쪽 아래가 `WSL: Ubuntu`처럼 보이는가?
- Python language server가 Pylance가 아니라 ty로 동작하는가?
- 자동완성이 뜨는가?
- `uv run ty check`와 VS Code diagnostics가 같은 문제를 보고하는가?
- AI assistant가 만든 코드가 아니라 수강생이 직접 타입을 읽고 수정했는가?

### 모델 문자열

Pydantic AI에서 가장 단순한 모델 선택은 문자열이다.

```python
from pydantic_ai import Agent

agent = Agent("openrouter:anthropic/claude-sonnet-4.6")
```

앞의 `openrouter`는 provider prefix이고, 뒤의 `anthropic/claude-sonnet-4.6`은 provider가 이해하는 model id다. 같은 agent 코드라도 모델 문자열을 바꾸면 다른 계정, 다른 billing, 다른 데이터 처리 경로, 다른 tool/structured output 지원 상태를 사용하게 된다.

수업에서는 provider 중립 환경 변수로 `COURSE_MODEL`을 쓴다.

```bash
COURSE_MODEL=openai:gpt-5.2
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6
COURSE_MODEL=bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0
COURSE_MODEL=google:gemini-3-pro-preview
COURSE_MODEL=google-cloud:gemini-3-pro-preview
```

기존 `OPENAI_MODEL`은 fallback으로 남겨 둔다. 초보자 수업에서는 이름이 다소 어색해도 `OPENAI_MODEL`만 쓰면 provider 전환을 떠올리기 어렵다. 그래서 새 교안에서는 `COURSE_MODEL`을 우선 쓰고, OpenAI만 사용하는 환경도 깨지지 않게 `OPENAI_MODEL` fallback을 둔다.

### 공급자 선택 기준

| 공급자 | Pydantic AI prefix | 인증 | 장점 | 주의 |
| --- | --- | --- | --- | --- |
| OpenAI | `openai:`, `openai-chat:`, `openai-responses:` | `OPENAI_API_KEY` | 수업 기본값, 예제가 단순함 | v2 prefix 정책과 API 종류를 명시해야 할 수 있음 |
| OpenRouter | `openrouter:` | `OPENROUTER_API_KEY` | 여러 모델을 한 계정으로 비교하기 쉬움 | downstream provider와 OpenRouter를 모두 데이터 경로로 봐야 함 |
| AWS Bedrock | `bedrock:` | bearer token 또는 AWS credential | 기업 AWS 계정/IAM과 잘 맞음 | region, model access, IAM 권한 오류가 많음 |
| Google AI Studio | `google:` | `GOOGLE_API_KEY` | Gemini API를 빠르게 실습하기 좋음 | 운영 통제는 Vertex보다 약함 |
| Google Cloud Vertex | `google-cloud:` | ADC, service account, 또는 API key | project/location, enterprise control, quota 관리 | Cloud project, API enablement, region 설정 필요 |

강사가 강조할 점:

- provider 전환은 단순 성능 비교가 아니라 dependency 교체다.
- 모델마다 tool calling, structured output, streaming, thinking, caching 지원이 다르다.
- 계정 설정 실패와 Pydantic AI 코드 실패를 구분하려면 최소 smoke test가 필요하다.
- 비용/데이터 처리 위치/로그 보존 정책은 코드 밖의 운영 의사결정이다.

### Provider Capability 확인

같은 provider 안에서도 model마다 지원 기능이 다를 수 있다. "OpenAI를 쓴다", "Gemini를 쓴다"가 충분한 정보가 아니다. 실제 앱에서 필요한 기능을 먼저 정하고, 그 기능을 model/provider가 지원하는지 확인해야 한다.

수업에서 확인할 capability checklist:

| Capability | 왜 확인하나 | 깨지는 예 |
| --- | --- | --- |
| Text input/output | 기본 agent 실행 가능 여부 | completion API와 chat/messages API 혼동 |
| Structured output | Pydantic output type을 안정적으로 받을 수 있는가 | JSON mode 미지원 또는 schema 준수 약함 |
| Tool calling | function tool을 모델이 선택하고 인자를 만들 수 있는가 | tool schema를 무시하고 일반 텍스트로 답함 |
| Image/document input | Vision/VLM, PDF, 이미지 실습 가능 여부 | 같은 provider라도 모델별 multimodal 지원 차이 |
| Streaming | UI에서 부분 응답을 보여줄 수 있는가 | durable workflow와 직접 streaming이 충돌 |
| Safety/approval controls | 위험 tool을 멈추고 사람이 승인할 수 있는가 | provider 기능이 아니라 앱 레벨 설계가 필요 |
| Region/data path | 사용자 데이터가 어디로 가는가 | OpenRouter downstream provider, Bedrock/Vertex region 혼동 |
| Logging/retention | prompt와 response가 어디에 저장되는가 | 민감 데이터가 provider 로그에 남음 |

강사가 강조할 문장:

"모델 선택은 leaderboard에서 1등을 고르는 일이 아닙니다. 내 앱이 필요한 capability, 데이터 경로, 비용, 실패 모드를 만족하는 dependency를 고르는 일입니다."

Vision/NLP/멀티모달 수요는 여기서 짧게 언급한다. 이 과정은 별도 Vision 모델 학습 수업이 아니라 Pydantic AI 기반 LLM app engineering 수업이므로, 멀티모달은 provider capability와 입력 타입 확인 문제로 다룬다.

## 공통 실습: provider smoke test

파일: `examples/00_providers/provider_smoke_test.py`

dry-run은 네트워크 호출을 하지 않고 모델 prefix와 필요한 환경 변수만 보여준다.

```bash
uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

VS Code에서는 `Tasks: Run Task`에서 `provider: dry-run`을 선택해 같은 명령을 실행할 수 있다.

실제 호출은 다음 흐름으로 진행한다.

1. `.env`에 provider별 key를 넣는다.
2. `COURSE_MODEL`을 설정한다.
3. dry-run으로 missing env를 확인한다.
4. 실제 호출을 실행한다.
5. Logfire UI가 준비되어 있으면 agent run trace를 확인한다.

```bash
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6 \
  uv run python examples/00_providers/provider_smoke_test.py
```

수강생에게 묻는다.

- 에러가 난다면 provider prefix, credential, account permission 중 어디가 의심되는가?
- Logfire trace에서 모델 요청까지 도달했는가?
- 같은 prompt를 다른 provider로 바꾸면 token usage와 latency가 어떻게 달라지는가?

## OpenRouter

OpenRouter는 여러 모델 provider를 하나의 API key와 model namespace로 사용할 수 있게 해 준다. 수업에서 모델 전환을 빠르게 보여주기 좋다.

환경 변수:

```bash
OPENROUTER_API_KEY=...
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6
```

문자열 방식:

```python
from pydantic_ai import Agent

agent = Agent("openrouter:anthropic/claude-sonnet-4.6")
```

provider를 직접 만들면 app attribution이나 API key 주입을 코드로 제어할 수 있다.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

model = OpenRouterModel(
    "anthropic/claude-sonnet-4.6",
    provider=OpenRouterProvider(
        api_key="your-openrouter-api-key",
        app_title="Pydantic AI Course",
        app_url="https://example.com",
    ),
)
agent = Agent(model)
```

강사가 말할 운영 포인트:

- OpenRouter key 하나만 보이지만 실제 추론은 downstream provider가 수행한다.
- 모델 id는 OpenRouter catalog 기준이다. provider 공식 model id와 완전히 같다고 가정하지 않는다.
- tool calling, structured output, prompt caching 지원은 downstream 모델과 OpenRouter 지원 범위의 교집합이다.
- 수업 중 모델 비교에는 편하지만, 운영 도입 전에는 데이터 처리 경로와 장애 책임 범위를 확인해야 한다.

## Google AI Studio / Gemini API

Google AI Studio는 Gemini API key를 빠르게 만들 수 있어 개인 실습에 적합하다. Pydantic AI에서는 `GoogleProvider`가 이 경로를 담당하고, prefix는 `google:`이다. 예전 자료의 `google-gla:` prefix는 더 이상 새 교안에서 쓰지 않는다.

환경 변수:

```bash
GOOGLE_API_KEY=...
COURSE_MODEL=google:gemini-3-pro-preview
```

문자열 방식:

```python
from pydantic_ai import Agent

agent = Agent("google:gemini-3-pro-preview")
```

직접 provider를 만들 수도 있다.

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

provider = GoogleProvider(api_key="your-google-api-key")
model = GoogleModel("gemini-3-pro-preview", provider=provider)
agent = Agent(model)
```

강사가 말할 운영 포인트:

- AI Studio는 수업과 프로토타입에 좋다.
- 기업 운영, project별 quota, region 통제, provisioned throughput이 필요하면 Vertex 쪽을 검토한다.
- `GOOGLE_API_KEY`는 Google AI Studio와 Vertex Express Mode에서 모두 보일 수 있으므로, 현재 prefix가 `google:`인지 `google-cloud:`인지 함께 확인한다.

## Google Cloud Vertex

Google Cloud Vertex는 Pydantic AI에서 `GoogleCloudProvider`가 담당하고, prefix는 `google-cloud:`이다. 예전 자료의 `google-vertex:` prefix는 새 코드에서 쓰지 않는다.

가장 흔한 개발자 로컬 흐름:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export COURSE_MODEL=google-cloud:gemini-3-pro-preview
```

문자열 방식:

```python
from pydantic_ai import Agent

agent = Agent("google-cloud:gemini-3-pro-preview")
```

project/location을 코드에서 명시할 수도 있다.

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(
    project="your-google-cloud-project-id",
    location="asia-northeast3",
)
model = GoogleModel("gemini-3-pro-preview", provider=provider)
agent = Agent(model)
```

service account를 쓰는 서버 환경에서는 credential 객체를 직접 넘긴다.

```python
from google.oauth2 import service_account
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
provider = GoogleCloudProvider(credentials=credentials, project="your-project-id")
model = GoogleModel("gemini-3-flash-preview", provider=provider)
agent = Agent(model)
```

강사가 말할 운영 포인트:

- Vertex AI API가 project에서 enabled 상태여야 한다.
- ADC가 있다고 해서 모든 모델에 접근 가능한 것은 아니다. quota와 region별 모델 지원을 확인해야 한다.
- `GOOGLE_CLOUD_LOCATION` 기본 후보로 `us-central1`을 많이 쓰지만, 한국 서비스에서는 latency, 규제, 모델 지원 범위를 따져 region을 정한다.
- API key를 쓰는 Express Mode와 ADC/service account 방식은 운영 권한 모델이 다르다.

## AWS Bedrock

Bedrock은 기업 AWS 계정, IAM, region, 모델 접근 권한과 연결된다. Pydantic AI에서는 `BedrockConverseModel`을 쓰며 prefix는 `bedrock:`이다.

환경 변수 예:

```bash
AWS_BEARER_TOKEN_BEDROCK=...
# 또는:
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
COURSE_MODEL=bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0
```

문자열 방식:

```python
from pydantic_ai import Agent

agent = Agent("bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0")
```

직접 모델을 만들 수도 있다.

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel

model = BedrockConverseModel("anthropic.claude-sonnet-4-5-20250929-v1:0")
agent = Agent(model)
```

강사가 말할 운영 포인트:

- `NoRegionError`는 코드 문제가 아니라 region 설정 문제다.
- `AccessDenied`나 model access 오류는 IAM 또는 Bedrock console의 model access 설정 문제일 가능성이 높다.
- Bedrock은 boto3를 사용하므로 `LOGFIRE_CAPTURE_HTTPX=1`이 provider HTTP payload까지 모두 보여준다고 기대하면 안 된다. Pydantic AI agent/model/tool span은 관측하되, AWS SDK 레벨 진단은 CloudTrail, Bedrock 로그, boto3 설정과 함께 봐야 한다.
- 모델 id는 region과 계정 설정에 따라 달라질 수 있다. 수업 직전 Bedrock 콘솔에서 실제 사용 가능한 model id를 확인한다.

## Logfire와 provider 전환

0회차에서 Logfire를 같이 켜는 이유는 provider 전환을 감으로 하지 않기 위해서다.

```python
import logfire

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()
```

provider smoke test에서 확인할 것:

- agent run이 시작됐는가?
- model request span이 만들어졌는가?
- 요청이 credential 단계에서 실패했는가, provider 응답 후 실패했는가?
- token usage가 수집되는가?
- 동일 prompt를 provider별로 실행했을 때 latency와 usage가 어떻게 다른가?

`LOGFIRE_CAPTURE_HTTPX=1`은 HTTPX 기반 provider의 payload 디버깅에 도움이 될 수 있지만, prompt와 사용자 데이터가 로그에 남을 수 있다. 수업에서는 민감한 데이터가 없는 smoke test에서만 켜고, 운영 기본값으로 쓰지 않는다.

## 흔한 실패와 디버깅

| 증상 | 우선 의심 | 대응 |
| --- | --- | --- |
| `ImportError` | optional dependency 없음 | full `pydantic-ai` 또는 provider optional group 설치 확인 |
| API key missing | `.env` 미로드 또는 변수명 오타 | `provider_smoke_test.py --dry-run`으로 env 확인 |
| OpenRouter 401 | key/credit 문제 | OpenRouter dashboard에서 key와 balance 확인 |
| OpenRouter model not found | catalog model id 불일치 | OpenRouter catalog의 정확한 id 사용 |
| Bedrock `NoRegionError` | region 없음 | `AWS_DEFAULT_REGION` 또는 boto3 session region 설정 |
| Bedrock access denied | IAM/model access | Bedrock console model access와 IAM policy 확인 |
| Google 403 | API 미활성/권한 없음 | AI Studio key, Vertex AI API enablement, project 권한 확인 |
| Google model/region 오류 | location별 모델 지원 차이 | `GOOGLE_CLOUD_LOCATION`과 모델 지원 지역 확인 |
| prefix deprecation warning | 예전 prefix 사용 | `google:` 또는 `google-cloud:`로 변경 |

## 실습 1: provider matrix 작성

목표: 수강생이 provider별 운영 차이를 말로 설명하게 한다.

지시:

1. 조별로 OpenRouter, Bedrock, Google AI Studio, Google Cloud Vertex 중 하나를 맡는다.
2. 필요한 환경 변수와 계정 사전 조건을 적는다.
3. `COURSE_MODEL` 예시를 하나 적는다.
4. 실패했을 때 가장 먼저 볼 곳을 적는다.
5. dry-run 결과를 공유한다.

강사 순회 체크:

- `google:`과 `google-cloud:`를 섞지 않았는가?
- Bedrock에서 region과 model access를 언급했는가?
- OpenRouter에서 downstream provider 데이터 경로를 언급했는가?
- provider 전환을 eval 없이 결정하지 않겠다고 말할 수 있는가?

## 실습 2: 동일 agent를 다른 provider로 실행

목표: agent 코드는 그대로 두고 provider만 바꾸는 흐름을 경험한다.

```bash
COURSE_MODEL=openai:gpt-5.2 \
  uv run python examples/00_providers/provider_smoke_test.py

COURSE_MODEL=google:gemini-3-pro-preview \
  uv run python examples/00_providers/provider_smoke_test.py
```

자격 증명이 없는 provider는 dry-run까지만 한다.

비교할 항목:

- 응답 언어와 형식
- latency
- token usage
- 에러 메시지의 위치
- Logfire trace에서 보이는 span 차이

## 1회차와의 연결

0회차가 끝나면 1회차에서는 provider 설정을 다시 길게 설명하지 않는다. 1회차의 목표는 `Agent`, Logfire, tool, deps, structured output이다. 수강생은 이미 자신의 `.env`에 `COURSE_MODEL`을 정해 두고, 다음 파일을 실행할 수 있어야 한다.

```bash
uv run python examples/01_basics/hello_agent.py
uv run python examples/01_basics/logfire_agent.py
uv run python examples/01_basics/tool_agent.py
```

강사는 1회차 초반에 이렇게만 확인한다.

"어제 0회차에서 smoke test가 통과한 모델 문자열을 그대로 씁니다. 오늘부터는 provider가 아니라 agent 경계에 집중합니다."

## 미니 리뷰 질문

1. `uv sync`와 `uv run`은 각각 언제 쓰나요?
2. Windows에서 PowerShell과 WSL의 `uv`를 섞으면 어떤 문제가 생기나요?
3. 이 수업에서 AI assistant를 쓰지 않고 ty 자동완성만 쓰는 이유는 무엇인가요?
4. `google:`과 `google-cloud:`는 무엇이 다른가요?
5. Bedrock에서 같은 코드가 `NoRegionError`를 내면 어디를 봐야 하나요?
6. OpenRouter를 쓰면 실제 추론 provider가 항상 OpenRouter 자체인가요?
7. `COURSE_MODEL`을 바꾸는 것이 왜 dependency 교체인가요?
8. Logfire에서 provider 전환 실험을 볼 때 어떤 지표를 비교해야 하나요?

## 강사용 완료 기준

- 수강생이 최소 하나의 provider model string을 설명했다.
- `uv sync`, `uv run ty check`, `uv run ruff check examples`를 실행했다.
- Windows 수강생은 WSL remote에서 repo를 열고 `~/src/...` 아래에서 실습했다.
- VS Code에서 `.venv` interpreter와 ty completion을 확인했다.
- AI assistant 없이 타입 기반 자동완성과 diagnostics만 사용했다.
- `provider_smoke_test.py --dry-run`을 실행했다.
- OpenRouter, Bedrock, Google AI Studio, Google Cloud Vertex의 인증/운영 차이를 표로 정리했다.
- `COURSE_MODEL`을 정하고 1회차 예제 실행 준비를 마쳤다.
- 실제 provider 호출을 못 한 수강생도 실패 원인과 다음 확인 위치를 설명했다.
