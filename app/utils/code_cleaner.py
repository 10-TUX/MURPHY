def clean_code(source_code: str) -> str:
    """Clean source code without changing it's meaning."""
    normalized = source_code.replace("\r\n", "\n").replace("\r", "\n")

    had_trailing_newline = normalized.endswith("\n")

    lines = normalized.splitlines()

    cleaned = "\n".join(line.rstrip(" \t") for line in lines)
    if had_trailing_newline:
        cleaned += "\n"
    return cleaned
