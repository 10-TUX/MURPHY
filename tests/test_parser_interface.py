from app.parsers.base import Parser
from app.parsers.generic_parser import GenericParser
from app.parsers.python_parser import PythonParser


def test_python_parser_implements_parser_interface():
    parser = PythonParser()

    assert isinstance(parser, Parser)


def test_generic_parser_implements_parser_interface():
    parser = GenericParser()

    assert isinstance(parser, Parser)
