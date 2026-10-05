"""Markdown documentation generator for parser output."""
from __future__ import annotations

from typing import List
from pathlib import Path
from dataclasses import dataclass

AUTOGEN_START = "<!-- AUTOGEN:START -->"
AUTOGEN_END = "<!-- AUTOGEN:END -->"


def render_functions(functions: List) -> str:
    lines: List[str] = []
    for f in sorted(functions, key=lambda x: x.qualname):
        lines.append(f"### {f.qualname}{f.signature}")
        if f.docstring:
            lines.append("")
            lines.append(f.docstring.strip())
        else:
            lines.append("")
            lines.append("_No docstring provided._")
        lines.append("")
    return "\n".join(lines)


def render_classes(classes: List) -> str:
    lines: List[str] = []
    for c in sorted(classes, key=lambda x: x.name):
        lines.append(f"## Class: {c.name}")
        if c.docstring:
            lines.append("")
            lines.append(c.docstring.strip())
        else:
            lines.append("")
            lines.append("_No class docstring provided._")
        lines.append("")
        if c.methods:
            lines.append("### Methods")
            lines.append("")
            for m in sorted(c.methods, key=lambda x: x.name):
                lines.append(f"- `{m.name}{m.signature}` — { (m.docstring.strip() if m.docstring else '_No docstring_') }")
            lines.append("")
    return "\n".join(lines)


def generate_markdown(parsed: dict) -> str:
    parts: List[str] = []
    functions = parsed.get("functions", [])
    classes = parsed.get("classes", [])
    if functions:
        parts.append("# Functions")
        parts.append("")
        parts.append(render_functions(functions))
    if classes:
        parts.append("# Classes")
        parts.append("")
        parts.append(render_classes(classes))
    return "\n".join(parts)


def update_docs_api(docs_path: Path, generated_fragment: str) -> bool:
    """Update `docs/api.md` between AUTOGEN markers. Returns True if changed."""
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    if not docs_path.exists():
        # create initial file with markers
        docs_path.write_text(f"{AUTOGEN_START}\n{generated_fragment}\n{AUTOGEN_END}\n", encoding="utf-8")
        return True

    text = docs_path.read_text(encoding="utf-8")
    if AUTOGEN_START in text and AUTOGEN_END in text:
        before, rest = text.split(AUTOGEN_START, 1)
        _, after = rest.split(AUTOGEN_END, 1)
        new_text = before + AUTOGEN_START + "\n" + generated_fragment + "\n" + AUTOGEN_END + after
    else:
        # append markers at end
        new_text = text + "\n" + AUTOGEN_START + "\n" + generated_fragment + "\n" + AUTOGEN_END + "\n"

    if new_text != text:
        docs_path.write_text(new_text, encoding="utf-8")
        return True
    return False
