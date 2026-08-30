from app.utils.language_detector import detect_language


def test_detect_common_languages():
    assert detect_language("main.py") == "python"
    assert detect_language("app.js") == "javascript"
    assert detect_language("component.tsx") == "typescript"
    assert detect_language("main.cpp") == "cpp"
    assert detect_language("server.go") == "go"
    assert detect_language("README.md") == "markdown"
    assert detect_language("config.json") == "json"


def test_detect_special_files():
    assert detect_language("Dockerfile") == "dockerfile"
    assert detect_language("Makefile") == "makefile"
    assert detect_language(".env") == "dotenv"


def test_detect_case_insensitive_extension():
    assert detect_language("SCRIPT.PY") == "python"
    assert detect_language("README.MD") == "markdown"


def test_unknown_extension_defaults_to_text():
    assert detect_language("notes.xyz") == "text"
