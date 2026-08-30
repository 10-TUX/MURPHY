import ast
import io
import tokenize
from app.parsers.base import Parser
from app.models.parsed_file import (
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    CommentInfo,
    ParsedFile,
)


class PythonParser(Parser):
    """Parser for Python source files using the built-in AST module."""

    def _parse_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> FunctionInfo:
        """Convert an AST function node in Functioninfo."""
        arguments = []
        # Positional-only arguments
        arguments.extend(argument.arg for argument in node.args.posonlyargs)

        # Regular arguments
        arguments.extend(argument.arg for argument in node.args.args)

        # *args
        if node.args.vararg:
            arguments.append(f"*{node.args.vararg.arg}")

        # Keyword-only arguments
        arguments.extend(argument.arg for argument in node.args.kwonlyargs)

        # **kwargs
        if node.args.kwarg:
            arguments.append(f"**{node.args.kwarg.arg}")

        return_type = ast.unparse(node.returns) if node.returns else None

        return FunctionInfo(
            name=node.name,
            arguments=arguments,
            return_type=return_type,
            docstring=ast.get_docstring(node),
            start_line=node.lineno,
            end_line=node.end_lineno,
        )

    def _parse_comments(self, source_code: str) -> list[CommentInfo]:
        """Extract comments from source code."""
        comments = []
        io_wrapper = io.StringIO(source_code)

        for token_info in tokenize.generate_tokens(io_wrapper.readline):
            token_type = token_info.type
            token_string = token_info.string
            start_pos = token_info.start
            end_pos = token_info.end

            if token_type == tokenize.COMMENT:
                # Remove '#' and strip whitespace
                comment_text = token_string[1:].strip()
                comments.append(
                    CommentInfo(
                        content=comment_text,
                        start_line=start_pos[0],
                        end_line=end_pos[0],
                    )
                )

        return comments

    def parse(self, source_code: str, file_path: str) -> ParsedFile:
        """Parse Python source code into a structured representation."""

        tree = ast.parse(source_code)

        comments = self._parse_comments(source_code)

        imports = []
        classes = []
        functions = []

        for node in tree.body:

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]

                imports.append(
                    ImportInfo(
                        module=node.module or "",
                        names=names,
                    )
                )

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._parse_function(node))

            elif isinstance(node, ast.ClassDef):
                methods = [
                    self._parse_function(child)
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]

                bases = [ast.unparse(base) for base in node.bases]

                classes.append(
                    ClassInfo(
                        name=node.name,
                        bases=bases,
                        docstring=ast.get_docstring(node),
                        methods=methods,
                        start_line=node.lineno,
                        end_line=node.end_lineno,
                    )
                )

        return ParsedFile(
            file_path=file_path,
            language="python",
            content=source_code,
            module_docstring=ast.get_docstring(tree),
            imports=imports,
            functions=functions,
            classes=classes,
            comments=comments,
        )
