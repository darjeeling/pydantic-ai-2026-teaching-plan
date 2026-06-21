import asyncio
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UnexpectedModelBehavior,
    UserPromptPart,
)

load_dotenv()

THIS_DIR = Path(__file__).parent
DB_PATH = THIS_DIR / "chat_messages.sqlite"
model = os.getenv("COURSE_MODEL") or os.getenv("OPENAI_MODEL", "openai:gpt-5.5")
AGENT_TIMEOUT_SECONDS = float(os.getenv("AGENT_TIMEOUT_SECONDS", "45"))

agent = Agent(
    model,
    instructions=(
        "You are a helpful Pydantic AI course chatbot. "
        "Answer in Korean. Prefer practical backend examples."
    ),
)

app = FastAPI(title="Pydantic AI Course Chatbot")


class ChatRequest(BaseModel):
    request_id: str = Field(min_length=8, max_length=80)
    message: str


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    timestamp: str
    content: str


@dataclass
class ChatStore:
    path: Path

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, check_same_thread=False)
        con.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "message_list BLOB NOT NULL)"
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS chat_requests ("
            "request_id TEXT PRIMARY KEY, "
            "status TEXT NOT NULL, "
            "response_json TEXT, "
            "error TEXT, "
            "created_at TEXT NOT NULL, "
            "completed_at TEXT)"
        )
        con.commit()
        return con

    def begin_request(self, request_id: str) -> dict[str, object] | None:
        now = datetime.now(UTC).isoformat()
        with self.connect() as con:
            try:
                con.execute(
                    "INSERT INTO chat_requests (request_id, status, created_at) VALUES (?, ?, ?)",
                    (request_id, "running", now),
                )
                con.commit()
                return None
            except sqlite3.IntegrityError:
                row = con.execute(
                    "SELECT status, response_json, error FROM chat_requests WHERE request_id = ?",
                    (request_id,),
                ).fetchone()

        if row is None:
            raise HTTPException(status_code=409, detail="request_id conflict")

        status, response_json, error = row
        if status == "completed" and response_json is not None:
            return json.loads(response_json)
        if status == "failed":
            raise HTTPException(status_code=502, detail=error or "Previous request failed")
        raise HTTPException(status_code=409, detail="Request is already running")

    def complete_request(self, request_id: str, response: dict[str, object]) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE chat_requests SET status = ?, response_json = ?, completed_at = ? "
                "WHERE request_id = ?",
                (
                    "completed",
                    json.dumps(response, ensure_ascii=False),
                    datetime.now(UTC).isoformat(),
                    request_id,
                ),
            )
            con.commit()

    def fail_request(self, request_id: str, error: str) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE chat_requests SET status = ?, error = ?, completed_at = ? "
                "WHERE request_id = ?",
                ("failed", error, datetime.now(UTC).isoformat(), request_id),
            )
            con.commit()

    def add_messages(self, messages: bytes) -> None:
        with self.connect() as con:
            con.execute("INSERT INTO messages (message_list) VALUES (?)", (messages,))
            con.commit()

    def get_model_messages(self) -> list[ModelMessage]:
        messages: list[ModelMessage] = []
        with self.connect() as con:
            rows = con.execute("SELECT message_list FROM messages ORDER BY id").fetchall()
        for (raw_messages,) in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(raw_messages))
        return messages

    def get_transcript(self) -> list[ChatMessage]:
        transcript: list[ChatMessage] = []
        for message in self.get_model_messages():
            transcript.append(to_chat_message(message))
        return transcript


store = ChatStore(DB_PATH)


def to_chat_message(message: ModelMessage) -> ChatMessage:
    first_part = message.parts[0]
    if isinstance(message, ModelRequest) and isinstance(first_part, UserPromptPart):
        assert isinstance(first_part.content, str)
        return ChatMessage(
            role="user",
            timestamp=first_part.timestamp.isoformat(),
            content=first_part.content,
        )
    if isinstance(message, ModelResponse) and isinstance(first_part, TextPart):
        return ChatMessage(
            role="model",
            timestamp=message.timestamp.isoformat(),
            content=first_part.content,
        )
    raise UnexpectedModelBehavior(f"Unexpected message type: {message!r}")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(THIS_DIR / "static" / "index.html")


@app.get("/messages")
async def messages() -> list[ChatMessage]:
    return store.get_transcript()


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, object]:
    cached_response = store.begin_request(request.request_id)
    if cached_response is not None:
        return cached_response

    history = store.get_model_messages()
    try:
        result = await asyncio.wait_for(
            agent.run(request.message, message_history=history),
            timeout=AGENT_TIMEOUT_SECONDS,
        )
    except TimeoutError as exc:
        store.fail_request(request.request_id, f"Agent timed out after {AGENT_TIMEOUT_SECONDS}s")
        raise HTTPException(status_code=504, detail="Agent request timed out") from exc
    except Exception as exc:
        store.fail_request(request.request_id, str(exc))
        raise

    store.add_messages(result.new_messages_json())
    response: dict[str, object] = {
        "request_id": request.request_id,
        "reply": result.output,
        "timestamp": datetime.now(UTC).isoformat(),
        "messages": [message.model_dump() for message in store.get_transcript()],
    }
    store.complete_request(request.request_id, response)
    return response
