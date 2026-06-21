# 3회차 슬라이드: Monty와 CodeMode

## 오늘의 결과물

- `CodeMode`를 붙인 agent
- 여러 tool 호출을 `run_code` 하나로 묶는 흐름
- sandbox에 넣을 tool과 제외할 tool 구분

## 문제

tool을 여러 번 호출하면 느리고 비싸다.

LLM이 생성한 코드를 host Python에서 그대로 실행하는 건 위험하다.

## CodeMode

- tool들을 `run_code` tool 안에 노출
- 모델이 Python 코드로 반복, 조건, 집계, 병렬 호출을 표현
- Monty sandbox에서 실행

## Monty Sandbox

- host filesystem 기본 차단
- env variable 기본 차단
- network 기본 차단
- 제한된 Python subset
- resource limit 지원

## 좋은 사용처

- 여러 검색 결과를 가져와 정렬/필터링
- 다수 API 호출을 병렬화
- tool 결과를 로컬 계산으로 요약

## 조심할 사용처

- 결제, 삭제, 메일 발송
- 권한이 필요한 관리자 작업
- 외부 side effect가 있는 tool

## 실무 질문

- sandbox 안의 tool도 idempotent한가?
- approval이 필요한 tool은 어떻게 분리할 것인가?
- 실패한 `run_code`를 어떻게 디버깅할 것인가?

