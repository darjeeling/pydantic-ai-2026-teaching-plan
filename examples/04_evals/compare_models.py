import os
from dataclasses import dataclass
from typing import Any

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

load_dotenv()

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()


@dataclass
class CourseAnswerContract(Evaluator[str, str, dict[str, Any]]):
    """Check model answers against minimal course-answer contracts."""

    def evaluate(self, ctx: EvaluatorContext[str, str, dict[str, Any]]) -> dict[str, bool | str]:
        metadata = ctx.metadata or {}
        output = ctx.output.lower()
        source_marker = str(metadata["source_marker"]).lower()
        any_terms = [str(term).lower() for term in metadata.get("any_terms", [])]

        has_source = source_marker in output
        has_required_term = any(term in output for term in any_terms) if any_terms else True

        return {
            "has_source": has_source,
            "has_required_term": has_required_term,
            "reason": (
                "contract passed"
                if has_source and has_required_term
                else f"missing source={not has_source}, missing term={not has_required_term}"
            ),
        }


dataset = Dataset[str, str, dict[str, Any]](
    name="course_model_switch",
    cases=[
        Case(
            name="tool_definition",
            inputs="Pydantic AI에서 tool은 무엇이고 언제 쓰나요?",
            metadata={
                "source_marker": "[source:lesson-01]",
                "any_terms": ["tool", "도구", "함수"],
            },
        ),
        Case(
            name="rag_definition",
            inputs="RAG를 만들 때 embedding과 vector DB는 어떤 역할인가요?",
            metadata={
                "source_marker": "[source:lesson-02]",
                "any_terms": ["embedding", "vector", "검색"],
            },
        ),
        Case(
            name="durable_execution",
            inputs="DBOS durable execution은 retry와 무엇이 다른가요?",
            metadata={
                "source_marker": "[source:lesson-05]",
                "any_terms": ["checkpoint", "재시작", "workflow"],
            },
        ),
    ],
    evaluators=[CourseAnswerContract()],
)

agent = Agent(
    os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5"),
    instructions=(
        "You are a Pydantic AI course assistant. Answer in Korean. "
        "Use the course lesson markers exactly as requested by the question category: "
        "tool basics must cite [source:lesson-01], RAG must cite [source:lesson-02], "
        "and DBOS durable execution must cite [source:lesson-05]. "
        "Keep answers under 6 sentences."
    ),
)


def make_task(model_name: str):
    async def answer_question(question: str) -> str:
        set_eval_attribute("model", model_name)
        result = await agent.run(question)
        increment_eval_metric("requests", result.usage.requests)
        increment_eval_metric("input_tokens", result.usage.input_tokens)
        increment_eval_metric("output_tokens", result.usage.output_tokens)
        increment_eval_metric("total_tokens", result.usage.total_tokens)
        return result.output

    return answer_question


def assert_report_threshold(model_name: str, report, threshold: float) -> None:
    averages = report.averages()
    if averages is None or averages.assertions is None:
        raise SystemExit(f"{model_name}: evaluation produced no assertion average")
    if averages.assertions < threshold:
        raise SystemExit(
            f"{model_name}: assertion pass rate {averages.assertions:.1%} "
            f"is below threshold {threshold:.1%}"
        )


def compare_models() -> None:
    models = [
        model.strip()
        for model in os.getenv("EVAL_MODELS", "openai:gpt-5.4,openai:gpt-5.5").split(",")
        if model.strip()
    ]
    repeat = int(os.getenv("EVAL_REPEAT", "1"))
    max_concurrency = int(os.getenv("EVAL_MAX_CONCURRENCY", "2"))
    threshold = float(os.getenv("EVAL_MIN_ASSERTION_RATE", "0.8"))

    for model_name in models:
        print(f"\n=== Evaluating {model_name} ===")
        with agent.override(model=model_name):
            report = dataset.evaluate_sync(
                make_task(model_name),
                name=model_name,
                repeat=repeat,
                max_concurrency=max_concurrency,
            )
        report.print()
        assert_report_threshold(model_name, report, threshold)


if __name__ == "__main__":
    compare_models()
