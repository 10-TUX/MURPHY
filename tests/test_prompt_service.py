from app.services.prompt_service import PromptService


def test_rag_prompt_contains_citation_instructions():
    """RAG prompt should contain citation rules."""

    prompt = PromptService.get_rag_prompt()

    messages = prompt.format_messages(
        context="app/auth/service.py:42-67",
        question="What does login do?",
    )

    system_message = messages[0].content

    assert "[source:start_line-end_line]" in system_message
    assert "Do not fabricate line numbers" in system_message


def test_rag_prompt_contains_uncertainty_instructions():
    """RAG prompt should instruct the model to handle insufficient context."""

    prompt = PromptService.get_rag_prompt()

    messages = prompt.format_messages(
        context="def login(): pass",
        question="How does the database connection work?",
    )

    system_message = messages[0].content

    assert "Never guess" in system_message
    assert "insufficient" in system_message
    assert "inference" in system_message
