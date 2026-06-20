# RAG

RAG는 Retrieval-Augmented Generation의 약자다. 모델이 모르는 문서를 먼저 검색하고, 검색된 문맥을 바탕으로 답변하도록 만드는 패턴이다.

일반적인 RAG pipeline은 문서 수집, chunking, embedding 생성, vector database 저장, 질문 embedding, 유사도 검색, 답변 생성 순서로 구성된다.

pgvector는 Postgres에서 vector embedding을 저장하고 거리 연산으로 유사 문서를 검색할 수 있게 해준다.

좋은 RAG 답변은 검색된 문맥에 없는 내용을 억지로 만들지 않고, source를 함께 제공한다.

