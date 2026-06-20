# Pydantic AI 기본

Pydantic AI의 Agent는 모델, instructions, tools, dependencies, output validation을 한 실행 단위로 묶는다.

Tool은 모델이 애플리케이션 코드에 요청할 수 있는 함수다. Tool 함수의 이름, 타입 힌트, docstring은 모델에게 전달되는 schema의 기반이 된다.

RunContext는 tool이 실행될 때 dependencies, usage, retry 정보 같은 실행 문맥에 접근하게 해준다.

Structured output은 모델 답변을 Pydantic 타입으로 검증해서 API 응답 계약처럼 사용할 수 있게 한다.

