from __future__ import annotations

import asyncio
from dataclasses import dataclass

from pydantic_graph import BaseNode, End, GraphBuilder, GraphRunContext, StepContext


@dataclass
class Retrieve(BaseNode[None, None, str]):
    question: str

    async def run(self, ctx: GraphRunContext) -> Draft:
        context = f"Retrieved course notes for: {self.question}"
        return Draft(question=self.question, context=context)


@dataclass
class Draft(BaseNode[None, None, str]):
    question: str
    context: str

    async def run(self, ctx: GraphRunContext) -> Review:
        answer = f"Draft answer based on [{self.context}]"
        return Review(answer=answer)


@dataclass
class Review(BaseNode[None, None, str]):
    answer: str

    async def run(self, ctx: GraphRunContext) -> End[str]:
        if "Retrieved" not in self.answer:
            return End("Rejected: answer did not use retrieved context.")
        return End(f"Approved: {self.answer}")


builder = GraphBuilder(input_type=str, output_type=str)


@builder.step
async def start(ctx: StepContext[None, None, str]) -> Retrieve:
    return Retrieve(question=ctx.inputs)


builder.add(
    builder.node(Retrieve),
    builder.node(Draft),
    builder.node(Review),
    builder.edge_from(builder.start_node).to(start),
)

course_graph = builder.build()


async def main() -> None:
    result = await course_graph.run(inputs="RAG는 언제 쓰나요?")
    print(result)
    print(course_graph.render())


if __name__ == "__main__":
    asyncio.run(main())

