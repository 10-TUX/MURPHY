"""MURPHY - RAG Service

Combines retrieval, prompt construction, and LLM generation
into a single Retrieval-Augmented Generation pipeline.
"""

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.vector_store_service import VectorStoreService


class RAGService:
    """Service responsible for the MURPHY RAG pipeline."""

    def __init__(
        self,
        vector_store: VectorStoreService,
        llm: BaseChatModel | None = None,
        retriever: Runnable | None = None,
        top_k: int = 4,
    ) -> None:
        """Initialize the RAG service."""

        self.vector_store = vector_store
        self.llm = llm if llm is not None else LLMService().get_llm()

        if top_k <= 0:
            raise ValueError("Top_k must be greater than 0.")

        self.retriever = (
            retriever if retriever is not None else vector_store.get_retriever(k=top_k)
        )

        self.prompt = PromptService.get_rag_prompt()
        self.chat_history: list[HumanMessage | AIMessage] = []

        self.chain = (
            {
                "context": (lambda x: x["question"])
                | self.retriever
                | self._format_docs,
                "question": lambda x: x["question"],
                "chat_history": lambda x: self.chat_history,
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    @staticmethod
    def _format_docs(docs: list[Document]) -> str:
        """Format documents for the RAG prompt."""
        formatted = []
        for doc in docs:
            source = doc.metadata.get("source")
            if source is None:
                formatted.append(doc.page_content)
                continue

            start_line = doc.metadata.get("start_line")
            end_line = doc.metadata.get("end_line")

            if start_line is not None and end_line is not None:
                citation = f"[{source}:{start_line}-{end_line}]"
                formatted.append(f"{citation}\n{doc.page_content}")
            else:
                formatted.append(f"[{source}]\n{doc.page_content}")

        return "\n\n".join(formatted)

    def retrieve(self, question: str) -> list[Document]:
        """Retrieve relevant documents for a question."""

        if not question.strip():
            return []

        return self.retriever.invoke(question)

    def invoke(self, question: str):
        """Run the complete RAG pipeline and update conversation history."""

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        response = self.chain.invoke(
            {
                "question": question,
            }
        )
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=response))

        return response
