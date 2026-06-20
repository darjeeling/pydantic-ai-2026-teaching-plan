from __future__ import annotations

from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults, ToolDenied
from pydantic_ai.models.test import TestModel

agent = Agent(
    TestModel(call_tools=["publish_course_notice", "delete_course_notice"]),
    output_type=[str, DeferredToolRequests],
    instructions=(
        "You are a course operations assistant. "
        "Publishing or deleting course notices must go through human approval."
    ),
)


@agent.tool_plain(requires_approval=True)
def publish_course_notice(channel: str) -> str:
    """Publish a course notice to the requested channel."""
    return f"Published course notice to {channel}"


@agent.tool_plain(requires_approval=True)
def delete_course_notice(channel: str) -> str:
    """Delete a course notice from the requested channel."""
    return f"Deleted course notice from {channel}"


def main() -> None:
    first_result = agent.run_sync("공지 발행과 삭제를 모두 처리해줘.")
    messages = first_result.all_messages()

    if not isinstance(first_result.output, DeferredToolRequests):
        raise RuntimeError("Expected approval requests from deferred tools")

    requests = first_result.output
    print("approval requests:")
    for call in requests.approvals:
        print(f"- {call.tool_call_id}: {call.tool_name} {call.args}")

    approval_results = DeferredToolResults()
    for call in requests.approvals:
        if call.tool_name == "publish_course_notice":
            approval_results.approvals[call.tool_call_id] = True
        else:
            approval_results.approvals[call.tool_call_id] = ToolDenied(
                "Deleting course notices requires a separate admin review."
            )

    resumed_result = agent.run_sync(
        "승인 결과를 반영해서 최종 상태를 정리해줘.",
        message_history=messages,
        deferred_tool_results=approval_results,
    )
    print("\nfinal output:")
    print(resumed_result.output)


if __name__ == "__main__":
    main()
