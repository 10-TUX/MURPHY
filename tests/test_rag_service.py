from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document
from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from app.services.rag_service import RAGService


class FakeRetriever(BaseRetriever):
    """Simple retriever used for RAG service tests."""

    documents: list[Document]

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        return self.documents


def create_rag_service() -> tuple[RAGService, FakeRetriever, FakeMessagesListChatModel]:
    """Create a RAG service with fake dependencies."""

    documents = [
        Document(
            page_content="def hello():\n    return 'Hello'",
            metadata={
                "source": "example.py",
                "start_line": 1,
                "end_line": 2,
            },
        )
    ]

    retriever = FakeRetriever(documents=documents)

    llm = FakeMessagesListChatModel(
        responses=[AIMessage(content="The hello function returns a greeting.")]
    )

    vector_store = MagicMock()

    service = RAGService(
        vector_store=vector_store,
        llm=llm,
        retriever=retriever,
    )

    return service, retriever, llm


def test_retrieve_returns_relevant_documents():
    """RAG service should retrieve documents from the retriever."""

    service, _, _ = create_rag_service()

    documents = service.retrieve("What does hello do?")

    assert len(documents) == 1
    assert documents[0].page_content.startswith("def hello")
    assert documents[0].metadata["source"] == "example.py"


def test_retrieve_empty_question_returns_empty_list():
    """Empty retrieval questions should return no documents."""

    service, _, _ = create_rag_service()

    assert service.retrieve("") == []
    assert service.retrieve("   ") == []


def test_invoke_runs_complete_rag_pipeline():
    """RAG service should retrieve context and generate an answer."""

    service, _, _ = create_rag_service()

    response = service.invoke("What does hello do?")

    assert response == "The hello function returns a greeting."


def test_invoke_rejects_empty_question():
    """RAG invocation should reject empty questions."""

    service, _, _ = create_rag_service()

    with pytest.raises(ValueError, match="Question cannot be empty"):
        service.invoke("")


def test_invoke_rejects_whitespace_question():
    """RAG invocation should reject whitespace-only questions."""

    service, _, _ = create_rag_service()

    with pytest.raises(ValueError, match="Question cannot be empty"):
        service.invoke("   ")


def test_format_docs_includes_source_and_line_range():
    """Formatted context should include source and line metadata."""

    documents = [
        Document(
            page_content="def hello():\n    return 'Hello'",
            metadata={
                "source": "example.py",
                "start_line": 10,
                "end_line": 11,
            },
        )
    ]

    formatted = RAGService._format_docs(documents)

    assert formatted == ("[example.py:10-11]\n" "def hello():\n" "    return 'Hello'")


def test_format_docs_supports_multiple_documents():
    """Multiple documents should be separated clearly."""

    documents = [
        Document(
            page_content="def first():\n    pass",
            metadata={
                "source": "first.py",
                "start_line": 1,
                "end_line": 2,
            },
        ),
        Document(
            page_content="def second():\n    pass",
            metadata={
                "source": "second.py",
                "start_line": 5,
                "end_line": 6,
            },
        ),
    ]

    formatted = RAGService._format_docs(documents)

    assert "[first.py:1-2]" in formatted
    assert "[second.py:5-6]" in formatted
    assert "\n\n[second.py:5-6]\ndef second()" in formatted


def test_format_docs_does_not_fabricate_line_numbers():
    """Missing line metadata should not produce fake line numbers."""

    documents = [
        Document(
            page_content="def hello():\n    pass",
            metadata={
                "source": "example.py",
            },
        )
    ]

    formatted = RAGService._format_docs(documents)

    assert formatted == ("[example.py]\n" "def hello():\n" "    pass")
    assert ":1-1" not in formatted


def test_format_docs_handles_missing_source():
    """Missing source metadata should not produce a fabricated citation."""

    documents = [
        Document(
            page_content="def hello():\n    pass",
            metadata={
                "start_line": 1,
                "end_line": 2,
            },
        )
    ]

    formatted = RAGService._format_docs(documents)

    assert formatted == ("def hello():\n" "    pass")


def test_format_docs_handles_empty_documents():
    """Empty document lists should produce empty context."""

    assert RAGService._format_docs([]) == ""


def test_chat_history_starts_empty():
    """A new RAG service should have no conversation history."""

    service, _, _ = create_rag_service()

    assert service.chat_history == []


def test_invoke_updates_chat_history():
    """A successful invocation should store the user question and AI response."""

    service, _, _ = create_rag_service()

    response = service.invoke("What does hello do?")

    assert len(service.chat_history) == 2

    assert isinstance(service.chat_history[0], HumanMessage)
    assert service.chat_history[0].content == "What does hello do?"

    assert isinstance(service.chat_history[1], AIMessage)
    assert service.chat_history[1].content == response


def test_chat_history_preserves_message_order():
    """Conversation history should preserve human → AI ordering."""

    service, _, _ = create_rag_service()

    service.invoke("What does hello do?")

    assert service.chat_history[0].type == "human"
    assert service.chat_history[1].type == "ai"


def test_chat_history_starts_empty():
    """A new RAG service should have no conversation history."""

    service, _, _ = create_rag_service()

    assert service.chat_history == []


def test_invoke_updates_chat_history():
    """A successful invocation should store the user question and AI response."""

    service, _, _ = create_rag_service()

    response = service.invoke("What does hello do?")

    assert len(service.chat_history) == 2

    assert isinstance(service.chat_history[0], HumanMessage)
    assert service.chat_history[0].content == "What does hello do?"

    assert isinstance(service.chat_history[1], AIMessage)
    assert service.chat_history[1].content == response


def test_chat_history_preserves_message_order():
    """Conversation history should preserve human → AI ordering."""

    service, _, _ = create_rag_service()

    service.invoke("What does hello do?")

    assert service.chat_history[0].type == "human"
    assert service.chat_history[1].type == "ai"


def test_end_to_end_rag_pipeline():
    """The complete RAG pipeline should retrieve context and generate an answer."""

    documents = [
        Document(
            page_content=(
                "class UserService:\n"
                "    def get_user(self, user_id):\n"
                "        return self.repository.find(user_id)"
            ),
            metadata={
                "source": "app/services/user_service.py",
                "start_line": 10,
                "end_line": 12,
            },
        ),
        Document(
            page_content=(
                "class UserRepository:\n"
                "    def find(self, user_id):\n"
                "        return self.db.query(user_id)"
            ),
            metadata={
                "source": "app/repositories/user_repository.py",
                "start_line": 20,
                "end_line": 22,
            },
        ),
    ]

    retriever = FakeRetriever(documents=documents)

    llm = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content=("UserService retrieves a user through " "UserRepository.")
            )
        ]
    )

    vector_store = MagicMock()

    service = RAGService(
        vector_store=vector_store,
        llm=llm,
        retriever=retriever,
    )

    response = service.invoke("How does UserService retrieve a user?")

    assert response == ("UserService retrieves a user through " "UserRepository.")

    assert len(service.chat_history) == 2
    assert service.chat_history[0].content == ("How does UserService retrieve a user?")
    assert service.chat_history[1].content == response


def test_end_to_end_rag_pipeline():
    """The complete RAG pipeline should retrieve context and generate an answer."""

    documents = [
        Document(
            page_content=(
                "class UserService:\n"
                "    def get_user(self, user_id):\n"
                "        return self.repository.find(user_id)"
            ),
            metadata={
                "source": "app/services/user_service.py",
                "start_line": 10,
                "end_line": 12,
            },
        ),
        Document(
            page_content=(
                "class UserRepository:\n"
                "    def find(self, user_id):\n"
                "        return self.db.query(user_id)"
            ),
            metadata={
                "source": "app/repositories/user_repository.py",
                "start_line": 20,
                "end_line": 22,
            },
        ),
    ]

    retriever = FakeRetriever(documents=documents)

    llm = FakeMessagesListChatModel(
        responses=[
            AIMessage(
                content=("UserService retrieves a user through " "UserRepository.")
            )
        ]
    )

    vector_store = MagicMock()

    service = RAGService(
        vector_store=vector_store,
        llm=llm,
        retriever=retriever,
    )

    response = service.invoke("How does UserService retrieve a user?")

    assert response == ("UserService retrieves a user through " "UserRepository.")

    assert len(service.chat_history) == 2
    assert service.chat_history[0].content == ("How does UserService retrieve a user?")
    assert service.chat_history[1].content == response


def test_end_to_end_context_contains_retrieved_metadata():
    """Retrieved documents should become citation-ready RAG context."""

    documents = [
        Document(
            page_content="def calculate_total(items):\n    return sum(items)",
            metadata={
                "source": "app/utils/calculator.py",
                "start_line": 15,
                "end_line": 16,
            },
        )
    ]

    retriever = FakeRetriever(documents=documents)

    llm = FakeMessagesListChatModel(
        responses=[AIMessage(content="The function calculates the total of the items.")]
    )

    service = RAGService(
        vector_store=MagicMock(),
        llm=llm,
        retriever=retriever,
    )

    response = service.invoke("What does calculate_total do?")

    assert response == ("The function calculates the total of the items.")

    formatted_context = service._format_docs(
        service.retrieve("What does calculate_total do?")
    )

    assert "[app/utils/calculator.py:15-16]" in formatted_context
    assert "def calculate_total(items):" in formatted_context


def test_rag_service_passes_top_k_to_retriever():
    """RAG service should pass top_k to the vector store retriever."""

    vector_store = MagicMock()

    llm = FakeMessagesListChatModel(responses=[AIMessage(content="test response")])

    RAGService(
        vector_store=vector_store,
        llm=llm,
        top_k=6,
    )

    vector_store.get_retriever.assert_called_once_with(k=6)


def test_rag_service_rejects_invalid_top_k():
    """RAG service should reject non-positive top_k values."""

    vector_store = MagicMock()

    llm = FakeMessagesListChatModel(responses=[AIMessage(content="test response")])

    with pytest.raises(ValueError, match="Top_k must be greater than 0"):
        RAGService(
            vector_store=vector_store,
            llm=llm,
            top_k=0,
        )
