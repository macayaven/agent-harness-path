"""Execute a named notebook function without running unrelated reactive cells."""

import ast
from pathlib import Path


def notebook_function(path: Path, name: str, namespace: dict | None = None):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == name)
    function.decorator_list = []
    scope = dict(namespace or {})
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), scope)
    return scope[name]
