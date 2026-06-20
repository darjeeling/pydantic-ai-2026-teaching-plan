from dataclasses import dataclass

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import EqualsExpected, EvaluationReason, Evaluator, EvaluatorContext


def deterministic_course_answer(question: str) -> str:
    if "tool" in question.lower() or "도구" in question:
        return "Tool은 모델이 앱 코드에 요청하는 함수입니다. [source:lesson-01]"
    if "rag" in question.lower():
        return "RAG는 검색된 문맥을 바탕으로 답하게 하는 패턴입니다. [source:lesson-02]"
    return "교안에 충분한 정보가 없습니다. [source:none]"


@dataclass
class HasSourceMarker(Evaluator[str, str, None]):
    """Every answer must expose whether it used a source."""

    def evaluate(self, ctx: EvaluatorContext[str, str, None]) -> EvaluationReason:
        ok = "[source:" in ctx.output
        reason = "answer includes source marker" if ok else "missing source marker"
        return EvaluationReason(value=ok, reason=reason)


dataset = Dataset[str, str, None](
    name="course_contracts",
    cases=[
        Case(
            name="tool_definition",
            inputs="tool은 무엇인가요?",
            expected_output="Tool은 모델이 앱 코드에 요청하는 함수입니다. [source:lesson-01]",
        ),
        Case(
            name="rag_definition",
            inputs="RAG가 뭐예요?",
            expected_output=(
                "RAG는 검색된 문맥을 바탕으로 답하게 하는 패턴입니다. "
                "[source:lesson-02]"
            ),
        ),
    ],
    evaluators=[EqualsExpected(), HasSourceMarker()],
)


def main() -> None:
    report = dataset.evaluate_sync(deterministic_course_answer)
    report.print()
    averages = report.averages()
    assert averages is not None
    assert averages.assertions == 1.0


if __name__ == "__main__":
    main()
