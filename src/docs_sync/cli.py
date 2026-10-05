"""CLI for the docs sync tool."""
from __future__ import annotations

import argparse
from pathlib import Path
from .parser import parse_file
from .generator import generate_markdown, update_docs_api


def main(argv=None):
    p = argparse.ArgumentParser(prog="docs-sync")
    p.add_argument("root", help="Repository root or path to scan")
    p.add_argument("--file", help="Single Python file to parse (for testing)")
    p.add_argument("--docs", default="docs/api.md", help="Path to docs/api.md")
    p.add_argument("--dry-run", action="store_true", help="Do not write files or commit")
    args = p.parse_args(argv)

    root = Path(args.root)
    docs_path = Path(args.docs)

    parsed = {"functions": [], "classes": []}
    if args.file:
        res = parse_file(args.file)
        parsed = res
    else:
        for py in root.rglob("*.py"):
            if py.name == "__init__.py":
                continue
            try:
                res = parse_file(str(py), module=str(py.relative_to(root)))
            except Exception:
                continue
            parsed["functions"].extend(res.get("functions", []))
            parsed["classes"].extend(res.get("classes", []))

    fragment = generate_markdown(parsed)
    if args.dry_run:
        print(fragment)
        return 0

    changed = update_docs_api(docs_path, fragment)
    if changed:
        print(f"Updated {docs_path}")
    else:
        print("No changes required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
