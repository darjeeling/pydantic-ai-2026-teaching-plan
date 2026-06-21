"""Raw function-calling loop, without Pydantic AI.

This file demystifies the "tools in a loop" mechanic at the HTTP wire level,
two ways:

- Part A: OpenAI Chat Completions ``tools`` / ``tool_calls``
- Part B: OpenAI Responses API ``function_call`` / ``function_call_output``

Both expose the same ``list_lesson_ids`` tool and run one full loop: send the
tool definitions -> the model asks us to call the function -> we run it ->
feed the result back -> the model returns the final answer.

The model never runs our code. It only emits a request to call a named
function with arguments; our harness runs the function and feeds the result
back. That round-trip is the loop.

This is intentionally OpenAI-only and verbose for teaching. Use Pydantic AI
(see ``tool_agent.py``) for real code; this file just shows the protocol.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

RAW_LOG_FILE = Path(
    os.getenv("COURSE_RAW_FUNCTION_LOG_FILE", "logs/httpx-raw-function-call.log")
)
PROMPT = os.getenv("COURSE_RAW_FUNCTION_PROMPT", "이 과정에 어떤 회차들이 있는지 id로 알려줘.")
TOOL_NAME = "list_lesson_ids"


def openai_model_id() -> str:
    course_model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL") or "openai:gpt-5.5"
    prefix, separator, model_id = course_model.partition(":")
    if not separator:
        return course_model
    if prefix not in {"openai", "openai-chat", "openai-responses"}:
        raise ValueError(
            "raw_function_call.py is intentionally OpenAI-only. "
            "Use COURSE_MODEL=openai:gpt-5.5 for this raw function-calling exercise."
        )
    return model_id


def base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


def auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def log_step(label: str, payload: Any) -> None:
    """Append one wire-level step to the raw log and print a short marker."""
    RAW_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": datetime.now(UTC).isoformat(), "step": label, "payload": payload}
    with RAW_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  - {label}")


# The actual local function the model is allowed to "call".
def list_lesson_ids() -> list[str]:
    return ["01", "02", "03", "04", "05"]


def run_tool(name: str, arguments_json: str) -> Any:
    """Dispatch a model-requested tool call to a real local function."""
    args = json.loads(arguments_json or "{}")
    if name == TOOL_NAME:
        return list_lesson_ids()
    raise ValueError(f"unknown tool requested by model: {name} args={args}")


def part_a_chat_completions(client: httpx.Client, headers: dict[str, str], model: str) -> str:
    """OpenAI Chat Completions: tools -> tool_calls -> tool message -> answer."""
    url = f"{base_url()}/chat/completions"
    tools = [
        {
            "type": "function",
            "function": {
                "name": TOOL_NAME,
                "description": "List available lesson ids in this course.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }
    ]
    messages: list[dict[str, Any]] = [{"role": "user", "content": PROMPT}]

    # 1) Send the question together with the tool definitions.
    log_step("A.request_with_tools", {"messages": messages, "tools": tools})
    first = client.post(
        url, headers=headers, json={"model": model, "messages": messages, "tools": tools}
    )
    first.raise_for_status()
    message: dict[str, Any] = first.json()["choices"][0]["message"]

    # 2) The model does not run code; it asks us to call the function.
    tool_calls = message.get("tool_calls") or []
    log_step("A.model_requested_tool_calls", tool_calls)
    if not tool_calls:
        return message.get("content") or "(no tool call, no content)"

    # 3) Run each requested function, feed results back as tool messages.
    messages.append(message)
    for call in tool_calls:
        fn = call["function"]
        result = run_tool(fn["name"], fn.get("arguments", "{}"))
        log_step("A.local_tool_result", {"name": fn["name"], "result": result})
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    # 4) Second call: the model now answers using the tool result.
    second = client.post(
        url, headers=headers, json={"model": model, "messages": messages, "tools": tools}
    )
    second.raise_for_status()
    final = second.json()["choices"][0]["message"].get("content") or ""
    log_step("A.final_answer", final)
    return final


def part_b_responses(client: httpx.Client, headers: dict[str, str], model: str) -> str:
    """OpenAI Responses API: function_call -> function_call_output -> answer."""
    url = f"{base_url()}/responses"
    tools = [
        {
            "type": "function",
            "name": TOOL_NAME,
            "description": "List available lesson ids in this course.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
    ]
    input_items: list[dict[str, Any]] = [{"role": "user", "content": PROMPT}]

    # 1) Send the question together with the tool definitions.
    log_step("B.request_with_tools", {"input": input_items, "tools": tools})
    first = client.post(
        url, headers=headers, json={"model": model, "input": input_items, "tools": tools}
    )
    first.raise_for_status()
    output: list[dict[str, Any]] = first.json().get("output", [])

    # 2) Find the function_call item(s) the model emitted.
    function_calls = [item for item in output if item.get("type") == "function_call"]
    log_step("B.model_requested_function_calls", function_calls)
    if not function_calls:
        return first.json().get("output_text") or "(no function call)"

    # 3) Run each function; append the call and its output back into the input.
    for call in function_calls:
        result = run_tool(call["name"], call.get("arguments", "{}"))
        log_step("B.local_tool_result", {"name": call["name"], "result": result})
        input_items.append(call)
        input_items.append(
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(result, ensure_ascii=False),
            }
        )

    # 4) Second call: the model answers using the tool result.
    second = client.post(
        url, headers=headers, json={"model": model, "input": input_items, "tools": tools}
    )
    second.raise_for_status()
    final = second.json().get("output_text") or ""
    log_step("B.final_answer", final)
    return final


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for the raw function-calling exercise.")
    model = openai_model_id()
    headers = auth_headers(api_key)

    with httpx.Client(timeout=60) as client:
        print("=== Part A: Chat Completions (tools / tool_calls) ===")
        print(part_a_chat_completions(client, headers, model))
        print()
        print("=== Part B: Responses API (function_call / function_call_output) ===")
        print(part_b_responses(client, headers, model))

    print(f"\nwire-level log: {RAW_LOG_FILE}")


if __name__ == "__main__":
    main()
