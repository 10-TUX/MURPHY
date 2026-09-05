from app.services.prompt_service import PromptService


def test_get_rag_prompt_returns_prompt():
    """RAG prompt should be created successfully."""

    prompt = PromptService.get_rag_prompt()

    assert prompt is not None


def test_rag_prompt_contains_context_and_question():
    """RAG prompt should contain context and question variables."""

    prompt = PromptService.get_rag_prompt()

    assert "context" in prompt.input_variables
    assert "question" in prompt.input_variables


def test_rag_prompt_contains_murphy_instructions():
    """RAG prompt should contain MURPHY-specific instructions."""

    prompt = PromptService.get_rag_prompt()

    messages = prompt.format_messages(
        context="def login(): pass",
        question="What does login do?",
    )

    system_message = messages[0].content

    assert "MURPHY" in system_message
    assert "repository context" in system_message
    assert "Do not invent" in system_message
    assert "file paths" in system_message
