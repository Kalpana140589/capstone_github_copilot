"""AST-based parser for extracting Python module metadata."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FunctionInfo:
    module: str
    qualname: str
    name: str
    signature: str
    docstring: Optional[str]
    decorators: List[str]


@dataclass
class ClassInfo:
    module: str
    qualname: str
    name: str
    docstring: Optional[str]
    methods: List[FunctionInfo]


def _get_decorator_names(node: ast.AST) -> List[str]:
    names: List[str] = []
    if not hasattr(node, "decorator_list"):
        return names
    for d in node.decorator_list:  # type: ignore[attr-defined]
        if isinstance(d, ast.Name):
            names.append(d.id)
        elif isinstance(d, ast.Attribute):
            # e.g. app.get
            parts = []
            cur = d
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            names.append(".".join(reversed(parts)))
        else:
            names.append(ast.dump(d))
    return names


def _format_signature(node: ast.FunctionDef) -> str:
    # Simple signature formatter using arg names and defaults.
    parts: List[str] = []
    args = node.args
    defaults = []
    if args.defaults:
        for d in args.defaults:
            try:
                defaults.append(ast.unparse(d))
            except Exception:
                defaults.append("<default>")
    def_count = len(defaults)
    total_args = len(args.args)
    non_default_count = total_args - def_count
    def_names = [None] * non_default_count + defaults
    for arg, default in zip(args.args, def_names):
        if arg.arg == 'self':
            continue
        if default is not None:
            parts.append(f"{arg.arg}={default}")
        else:
            parts.append(arg.arg)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for kw, default in zip(args.kwonlyargs, args.kw_defaults if hasattr(args, 'kw_defaults') else []):
        parts.append(kw.arg)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return f"({', '.join(parts)})"


def parse_file(path: str, module: str = "") -> dict:
    """Parse a Python file and return dict with functions and classes."""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src, filename=path)
    functions: List[FunctionInfo] = []
    classes: List[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            sig = _format_signature(node)
            doc = ast.get_docstring(node)
            decs = _get_decorator_names(node)
            fi = FunctionInfo(module=module, qualname=node.name, name=node.name, signature=sig, docstring=doc, decorators=decs)
            functions.append(fi)
        elif isinstance(node, ast.ClassDef):
            c_doc = ast.get_docstring(node)
            methods: List[FunctionInfo] = []
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    sig = _format_signature(sub)
                    doc = ast.get_docstring(sub)
                    decs = _get_decorator_names(sub)
                    methods.append(FunctionInfo(module=module, qualname=f"{node.name}.{sub.name}", name=sub.name, signature=sig, docstring=doc, decorators=decs))
            classes.append(ClassInfo(module=module, qualname=node.name, name=node.name, docstring=c_doc, methods=methods))

    return {"functions": functions, "classes": classes}
