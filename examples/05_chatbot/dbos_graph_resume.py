from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from dbos import DBOS, DBOSConfig
from pydantic_graph import GraphBuilder, StepContext

BASE_DIR = Path(__file__).resolve().parent
STATE_DB = BASE_DIR / "dbos_graph_state.sqlite"
DBOS_DB = BASE_DIR / "dbos_graph.sqlite"

dbos_config: DBOSConfig = {
    "name": "pai_graph_resume",
    "system_database_url": f"sqlite:///{DBOS_DB}",
}
DBOS(config=dbos_config)

NextNode = Literal["retrieve", "draft", "review", "done"]
RunStatus = Literal["running", "paused", "completed"]
StopAfter = Literal["retrieve", "draft", "review"]


@dataclass
class CourseGraphState:
    question: str
    context: str | None = None
    draft: str | None = None
    review_notes: str | None = None
    output: str | None = None
    visited: list[str] = field(default_factory=list)


@dataclass
class GraphCheckpoint:
    run_id: str
    state: CourseGraphState
    next_node: NextNode
    status: RunStatus


@dataclass
class GraphRunReport:
    run_id: str
    status: RunStatus
    next_node: NextNode
    state: CourseGraphState
    output: str | None = None


def _connect_state_db() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB)
    conn.execute(
        """
        create table if not exists graph_runs (
            run_id text primary key,
            state_json text not null,
            next_node text not null,
            status text not null,
            updated_at text not null default current_timestamp
        )
        """
    )
    return conn


def _state_to_json(state: CourseGraphState) -> str:
    return json.dumps(asdict(state), ensure_ascii=False, sort_keys=True)


def _state_from_json(raw: str) -> CourseGraphState:
    return CourseGraphState(**json.loads(raw))


def retrieve_context(question: str) -> str:
    return f"Course notes: '{question}' needs agent state, RAG sources, and retry policy."


def write_draft(question: str, context: str) -> str:
    return f"Draft answer for [{question}] using [{context}]"


def review_answer(draft: str) -> tuple[str, str]:
    if "Course notes" not in draft:
        return "Rejected: answer did not use retrieved context.", "missing retrieved context"
    return f"Approved: {draft}", "used retrieved context"


graph_builder = GraphBuilder(state_type=CourseGraphState, input_type=str, output_type=str)


@graph_builder.step(node_id="retrieve")
async def retrieve(ctx: StepContext[CourseGraphState, None, str]) -> str:
    ctx.state.question = ctx.inputs
    ctx.state.context = retrieve_context(ctx.inputs)
    ctx.state.visited.append("retrieve")
    return ctx.state.context


@graph_builder.step(node_id="draft")
async def draft(ctx: StepContext[CourseGraphState, None, str]) -> str:
    ctx.state.draft = write_draft(ctx.state.question, ctx.inputs)
    ctx.state.visited.append("draft")
    return ctx.state.draft


@graph_builder.step(node_id="review")
async def review(ctx: StepContext[CourseGraphState, None, str]) -> str:
    ctx.state.output, ctx.state.review_notes = review_answer(ctx.inputs)
    ctx.state.visited.append("review")
    return ctx.state.output


graph_builder.add(
    graph_builder.edge_from(graph_builder.start_node).to(retrieve),
    graph_builder.edge_from(retrieve).to(draft),
    graph_builder.edge_from(draft).to(review),
    graph_builder.edge_from(review).to(graph_builder.end_node),
)
course_graph = graph_builder.build()


@DBOS.step()
def load_checkpoint(run_id: str) -> GraphCheckpoint | None:
    with _connect_state_db() as conn:
        row = conn.execute(
            "select state_json, next_node, status from graph_runs where run_id = ?",
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    state_json, next_node, status = row
    return GraphCheckpoint(
        run_id=run_id,
        state=_state_from_json(state_json),
        next_node=next_node,
        status=status,
    )


@DBOS.step()
def save_checkpoint(
    run_id: str,
    state: CourseGraphState,
    next_node: NextNode,
    status: RunStatus,
) -> GraphCheckpoint:
    with _connect_state_db() as conn:
        conn.execute(
            """
            insert into graph_runs (run_id, state_json, next_node, status, updated_at)
            values (?, ?, ?, ?, current_timestamp)
            on conflict(run_id) do update set
                state_json = excluded.state_json,
                next_node = excluded.next_node,
                status = excluded.status,
                updated_at = current_timestamp
            """,
            (run_id, _state_to_json(state), next_node, status),
        )

    return GraphCheckpoint(run_id=run_id, state=state, next_node=next_node, status=status)


@DBOS.step()
def run_retrieve_node(state: CourseGraphState) -> CourseGraphState:
    state.context = retrieve_context(state.question)
    state.visited.append("retrieve")
    return state


@DBOS.step()
def run_draft_node(state: CourseGraphState) -> CourseGraphState:
    if state.context is None:
        raise ValueError("retrieve must run before draft")
    state.draft = write_draft(state.question, state.context)
    state.visited.append("draft")
    return state


@DBOS.step()
def run_review_node(state: CourseGraphState) -> CourseGraphState:
    if state.draft is None:
        raise ValueError("draft must run before review")
    state.output, state.review_notes = review_answer(state.draft)
    state.visited.append("review")
    return state


@DBOS.workflow(name="course_graph.run_or_resume")
def run_or_resume_graph(
    run_id: str,
    question: str | None = None,
    stop_after: StopAfter | None = None,
) -> GraphRunReport:
    checkpoint = load_checkpoint(run_id)

    if checkpoint is None:
        if question is None:
            raise ValueError("question is required when no checkpoint exists")
        state = CourseGraphState(question=question)
        next_node: NextNode = "retrieve"
    else:
        state = checkpoint.state
        next_node = checkpoint.next_node
        if checkpoint.status == "completed":
            return GraphRunReport(run_id, "completed", "done", state, state.output)

    while next_node != "done":
        if next_node == "retrieve":
            state = run_retrieve_node(state)
            next_node = "draft"
            completed_node: StopAfter = "retrieve"
        elif next_node == "draft":
            state = run_draft_node(state)
            next_node = "review"
            completed_node = "draft"
        elif next_node == "review":
            state = run_review_node(state)
            next_node = "done"
            completed_node = "review"

        status: RunStatus = "completed" if next_node == "done" else "running"
        save_checkpoint(run_id, state, next_node, status)

        if stop_after == completed_node and next_node != "done":
            save_checkpoint(run_id, state, next_node, "paused")
            return GraphRunReport(run_id, "paused", next_node, state, state.output)

    return GraphRunReport(run_id, "completed", "done", state, state.output)


def delete_checkpoint(run_id: str) -> None:
    with _connect_state_db() as conn:
        conn.execute("delete from graph_runs where run_id = ?", (run_id,))


def print_report(report: GraphRunReport) -> None:
    print(f"run_id: {report.run_id}")
    print(f"status: {report.status}")
    print(f"next_node: {report.next_node}")
    print(f"visited: {', '.join(report.state.visited)}")
    print(f"context: {report.state.context}")
    print(f"draft: {report.state.draft}")
    print(f"review_notes: {report.state.review_notes}")
    print(f"output: {report.output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Persist and resume a Pydantic Graph run with DBOS step boundaries.",
    )
    parser.add_argument("--run-id", default="demo-graph")
    parser.add_argument("--question", default="RAG는 언제 쓰나요?")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--stop-after", choices=["retrieve", "draft", "review"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.render:
        print(course_graph.render(title="Durable Course Graph", direction="LR"))
        return

    if args.reset:
        delete_checkpoint(args.run_id)

    DBOS.launch()
    question = None if args.resume else args.question
    report = run_or_resume_graph(args.run_id, question=question, stop_after=args.stop_after)
    print_report(report)


if __name__ == "__main__":
    main()
