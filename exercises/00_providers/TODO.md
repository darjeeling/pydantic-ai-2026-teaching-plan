# 0회차 실습 TODO

## 시작 파일

- `examples/00_providers/provider_smoke_test.py`
- `.env.example`
- `.vscode/settings.json`
- `.vscode/tasks.json`

## 과제

1. Windows 수강생은 WSL 2 안에서 repo를 연다.

PowerShell:

```powershell
wsl --install
```

Ubuntu/WSL:

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

확인할 점:

- repo 경로가 `/mnt/c/...`가 아니라 `~/src/...` 아래에 있다.
- VS Code 왼쪽 아래에 `WSL: Ubuntu`처럼 표시된다.
- 이후 명령은 PowerShell이 아니라 VS Code의 WSL 터미널에서 실행한다.

2. VS Code에서 workspace 권장 확장을 설치한다.
   - `astral-sh.ty`
   - `charliermarsh.ruff`
   - `ms-python.python`
   - Windows host에는 `ms-vscode-remote.remote-wsl`
3. 이번 실습에서는 AI assistant를 쓰지 않는다.
   - GitHub Copilot/Copilot Chat을 끈다.
   - Cursor/Cline류 코드 생성 기능도 끈다.
   - 자동완성은 ty language server만 쓴다.
4. `uv sync`를 실행한다.

```bash
uv sync
```

5. VS Code에서 `examples/00_providers/provider_smoke_test.py`를 열고, `print_hint()` 안에서 `hint.`을 입력했을 때 자동완성이 뜨는지 확인한다.
6. `ProviderHint(...)` 위에 마우스를 올려(hover) field와 signature help가 보이는지 확인한다.
7. Command Palette에서 `Tasks: Run Task`를 열어 `ty: check`를 실행한다.
8. 터미널에서도 같은 검사를 돌려본다.

```bash
uv run ty check
uv run ruff check examples
```

9. `.env.example`을 `.env`로 복사한다.
10. 조별로 provider를 하나 고른다.
   - OpenRouter
   - AWS Bedrock
   - Google AI Studio
   - Google Cloud Vertex
11. 고른 provider의 credential과 `COURSE_MODEL` 예시를 `.env`에 적는다.
12. dry-run을 실행한다.

```bash
uv run python examples/00_providers/provider_smoke_test.py --dry-run
```

13. 가능하면 실제 호출을 실행한다.

```bash
uv run python examples/00_providers/provider_smoke_test.py
```

14. 로컬 API 호출 로그를 확인한다.

```bash
tail -n 20 logs/api-calls.log
```

15. Logfire를 쓸 수 있는 환경이면 agent run trace까지 확인한다.

## Provider별 예시

```bash
COURSE_MODEL=openrouter:anthropic/claude-sonnet-4.6
COURSE_MODEL=bedrock:anthropic.claude-sonnet-4-5-20250929-v1:0
COURSE_MODEL=google:gemini-3.1-pro-preview
COURSE_MODEL=google-cloud:gemini-3.1-pro-preview
```

## 제출할 메모

- 선택한 provider
- 사용한 model string
- 필요한 환경 변수
- 필요한 capability: structured output, tool calling, image/document input, streaming 중 무엇이 필요한지
- 데이터 경로/region/logging retention에서 확인한 점
- `uv run ty check` 결과
- VS Code ty 자동완성 확인 여부
- Windows라면 WSL remote 사용 여부와 repo 경로
- dry-run 결과
- 실제 호출 성공/실패 여부
- `logs/api-calls.log`에서 확인한 model string과 호출 완료 여부
- 실패했다면 가장 먼저 어디부터 확인할지

## 통과 기준

- `uv sync`, `uv run ty check`, `uv run ruff check examples`를 모두 실행했다.
- Windows 수강생은 WSL remote에서 `~/src/...` 아래 repo를 열었다.
- VS Code에서 ty 자동완성, hover, diagnostics를 확인했다.
- AI assistant 없이 실습했다.
- `COURSE_MODEL`의 provider prefix를 설명할 수 있다.
- provider 이름과 model capability가 다를 수 있다는 점을 설명할 수 있다.
- `google:`과 `google-cloud:`를 구분할 수 있다.
- Bedrock은 region과 model access가 필요하다는 점을 설명할 수 있다.
- OpenRouter는 downstream provider를 거친다는 점을 설명할 수 있다.
- 실제 호출 뒤 `logs/api-calls.log`에서 호출 breadcrumb를 확인했다.
- 1회차에서 쓸 모델 설정을 정했다.
