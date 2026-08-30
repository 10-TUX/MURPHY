from app.utils.code_cleaner import clean_code


def test_normalize_line_endings():
    source_code = "line one\r\nline two\r\nline three\r\n"
    cleaned_code = clean_code(source_code)
    assert cleaned_code == "line one\nline two\nline three\n"


def test_remove_trailing_whitespace():
    source_code = "def hello():\nprint('hello')\t\t\n"
    cleaned_code = clean_code(source_code)
    assert cleaned_code == "def hello():\nprint('hello')\n"


def test_preserve_blank_lines():
    source_code = "def first():\n" "    pass\n" "\n" "\n" "def second():\n" "    pass\n"

    cleaned_code = clean_code(source_code)

    assert cleaned_code == source_code


def test_preserve_whitespace_inside_strings():
    source_code = 'message = "hello world"\n' "text = 'keep    these spaces'\n"
    cleaned_code = clean_code(source_code)
    assert cleaned_code == source_code


def test_preserve_comments():
    source_code = "# this is a comment \n" "x = 10 # Important values \n"
    cleaned_code = clean_code(source_code)
    assert cleaned_code == ("# this is a comment\n" "x = 10 # Important values\n")
