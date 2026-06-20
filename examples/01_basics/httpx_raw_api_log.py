from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

RAW_LOG_FILE = Path(os.getenv("COURSE_RAW_HTTPX_LOG_FILE", "logs/httpx-raw-api.log"))
DEFAULT_PROMPT = "Pydantic AI를 처음 배우는 사람에게 한 문단으로 설명해줘."


def openai_model_id() -> str:
    course_model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL") or "openai:gpt-5.2"
    prefix, separator, model_id = course_model.partition(":")
    if not separator:
        return course_model
    if prefix not in {"openai", "openai-chat", "openai-responses"}:
        raise ValueError(
            "httpx_raw_api_log.py is intentionally OpenAI-only. "
            "Use COURSE_MODEL=openai:gpt-5.2 for this raw HTTP exercise."
        )
    return model_id


def write_jsonl(record: dict[str, Any]) -> None:
    RAW_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RAW_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def now() -> str:
    return datetime.now(UTC).isoformat()


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    if "Authorization" in redacted:
        redacted["Authorization"] = "Bearer ***"
    return redacted


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for the raw HTTPX exercise.")

    model = openai_model_id()
    prompt = os.getenv("COURSE_RAW_HTTPX_PROMPT", DEFAULT_PROMPT)
    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "input": prompt,
    }

    write_jsonl(
        {
            "event": "raw_httpx_request",
            "ts": now(),
            "method": "POST",
            "url": url,
            "headers": redact_headers(headers),
            "body": body,
        }
    )

    with httpx.Client(timeout=60) as client:
        response = client.post(url, headers=headers, json=body)

    write_jsonl(
        {
            "event": "raw_httpx_response",
            "ts": now(),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
        }
    )

    print(f"raw httpx log file: {RAW_LOG_FILE}")
    print(f"status: {response.status_code}")
    response.raise_for_status()

    data = response.json()
    print(data.get("output_text") or data)


if __name__ == "__main__":
    main()
