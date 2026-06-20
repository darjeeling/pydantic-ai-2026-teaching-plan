# Python AI Topic Map

이 문서는 `python-ai-teaching-topics-2026-06-12.md` 분석을 현재 Pydantic AI 교안에 어떻게 반영할지 정리한 대응표다.

## Scope

이 교안의 중심은 Python 문법이나 전통 ML 모델 학습이 아니라 **Python으로 LLM/RAG/Agent 서비스를 만드는 앱 엔지니어링**이다.

따라서 pandas/EDA/scikit-learn, Vision model training, MLflow/Airflow/vLLM/Kubernetes는 본편에서 깊게 다루지 않는다. 대신 본편의 각 회차에서 운영 관점과 연결하고, 별도 심화반 후보로 남긴다.

## Topic Mapping

| 보고서 토픽 | 현재 교안 반영 | 보강 내용 |
| --- | --- | --- |
| Python 데이터 실습 기초 | 0회차 `uv`, VS Code, `ty`; 2회차 ingestion | pandas/EDA는 본편 제외, JSON/Markdown/API/DB 중심 |
| Data-Centric AI | 2회차 RAG | Data-Centric RAG, 최신성, 중복, metadata, prompt injection |
| 모델 학습과 평가 | 4회차 eval | 모델 학습 대신 LLM/RAG/tool-use eval과 model-switch gate |
| NLP/Vision/멀티모달 | 0회차 provider capability | Vision/VLM 구현 대신 image/document input capability 확인 |
| LLM/RAG/GraphRAG | 1~2회차, 4회차 graph | Vector RAG 구현, GraphRAG는 관계 기반 검색 심화로 소개 |
| Function Calling/Tool Use/Agent | 1회차 tools, 4회차 tool-use eval | tool selection, arguments, forbidden tool policy 평가 |
| Agent framework 비교 | 1회차 Pydantic AI 위치, 4회차 graph 비교 | LangChain은 범용 agent framework, LangGraph는 orchestration runtime, Spring AI는 Spring/JVM 통합, Pydantic AI는 type-safe Python agent framework로 구분 |
| AI 코딩 도구와 에이전트 개발 | 3회차 CodeMode/Monty, 부록 | AI assistant 사용법이 아니라 생성 코드 검증 습관으로 다룸 |
| 서비스화/MLOps/인프라 | 5회차 FastAPI/DBOS/Logfire/eval | MLflow/Airflow/vLLM/Kubernetes는 심화로 분리 |

## Suggested Advanced Classes

현재 본편 뒤에 별도 심화반을 만든다면 아래 순서가 자연스럽다.

1. **Python Data & Baseline ML**
   - pandas EDA
   - train/test split
   - scikit-learn baseline
   - metric 해석

2. **Advanced RAG / GraphRAG**
   - reranking
   - query rewriting
   - metadata filtering
   - entity/relation extraction
   - Neo4j 또는 graph DB 기반 retrieval

3. **LLM Tool Evaluation**
   - BFCL-style function calling benchmark 개념
   - tool schema mutation test
   - unsafe tool blocking
   - tool argument quality evaluator

4. **AI Service Operations**
   - Docker image
   - CI/CD
   - DB migration
   - background ingestion
   - rate limiting
   - cost dashboard

5. **Self-hosted LLM Serving**
   - vLLM
   - Qwen/Llama 계열 모델
   - OpenWebUI
   - GPU serving and batching

## AI Coding Tool Appendix

본편 실습에서는 AI assistant를 사용하지 않는다. 대신 자동완성은 `ty` language server로 확인한다. 이유는 수강생이 Pydantic AI, RAG, eval, durable execution의 경계를 직접 읽고 이해해야 하기 때문이다.

AI coding tool은 별도 부록에서 "코드를 대신 짜게 하는 방법"이 아니라 "AI가 만든 코드를 검증하는 개발자 습관"으로 다룬다.

검증 체크리스트:

- `uv run ty check`
- `uv run ruff check examples`
- `python3 -m compileall examples`
- unit test 또는 deterministic eval
- RAG/tool-use eval
- Logfire trace 확인
- dangerous tool은 approval gate 필요 여부 확인
- sandbox나 CodeMode가 필요한 코드 실행인지 확인

강사가 강조할 문장:

"AI coding tool을 쓰더라도 책임은 개발자에게 남습니다. 그래서 자동 생성보다 중요한 것은 타입 체크, lint, test, eval, trace로 검증 가능한 경계를 만드는 것입니다."
