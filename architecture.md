# Automated Documentation Sync — Architecture

## Summary
This document describes a high-level architecture for the Automated Documentation Sync tool (MVP). The design follows a modular CLI-first approach implemented in Python and suitable for local or CI execution.

## Components

1. Core Parser
   - Responsibility: Parse Python source files to extract function/class signatures, type hints, and docstrings; identify web framework route decorators for FastAPI/Flask.
   - Key features: AST-based parsing for deterministic extraction; pluggable extractors for frameworks.

2. Git / File Watcher
   - Responsibility: Determine which files changed and trigger documentation update runs.
   - Modes: (a) Git-diff mode (recommended): use `git` to compute changed files between HEAD and target branch/commit; (b) Full-scan mode: traverse files under the repo root.
   - Implementation: Use `GitPython` or invoking `git` subprocess for diffs. For local watch (optional), use `watchdog`.

3. Doc Generator
   - Responsibility: Render extracted metadata to Markdown and insert/update generated sections in `docs/api.md` while preserving manual content.
   - Features: Use explicit markers to delimit generated content, idempotent updates, and best-effort formatting.

4. Git / PR Integrator
   - Responsibility: Create a branch, commit documentation changes, and optionally open a draft PR (GitHub) or leave branch for review.
   - Implementation: Use `GitPython` for branch/commit operations and optionally `PyGithub` or the GitHub REST API for PR creation.

5. CLI / Orchestration Layer
   - Responsibility: Provide a user-facing CLI, configuration parsing, logging, and orchestration across components.
   - Features: Support flags for `--target-branch`, `--scan-all`, `--dry-run`, `--commit`, and `--create-pr`.

6. Error Reporting & Logs
   - Responsibility: Aggregate parsing errors, generation warnings, and git operation failures into a summary included in commit messages or PR descriptions.

## Technology Choices
- Language: Python 3.10+ (type hints, pattern matching benefits).
- Parsing: Python `ast` module for robust, dependency-free parsing; optionally `libcst` or `parso` if preserving formatting is required.
- Git integration: `GitPython` for programmatic git operations; fallback to shell `git` where appropriate.
- File watching (optional): `watchdog`.
- Markdown generation: `markdown` or `markdown2` for parsing; generation can be string/template based (Jinja2) or structured using `mistune` for advanced needs.
- HTTP/GitHub API: `PyGithub` or use `requests` to call the GitHub REST API directly for PR creation.
- CLI: `click` or `argparse` for command-line interface.
- Testing: `pytest` for unit tests.

## Data Flow

1. Invocation
   - CLI invoked manually or in CI with options (e.g., `--target-branch=origin/main`).

2. Change Detection
   - Git/Watcher computes changed files (git-diff between current HEAD and target branch, or full-scan).

3. Parsing
   - For each relevant Python file, the Core Parser uses `ast.parse()` to build an AST, then extracts functions, classes, signatures, type hints, and docstrings. Route decorators are recognized and mapped to endpoint entries.

4. Document Generation
   - Extracted metadata is rendered into a Markdown fragment. The Doc Generator reads `docs/api.md`, locates generator markers (e.g., `<!-- AUTOGEN:START -->` / `<!-- AUTOGEN:END -->`), replaces the generated section, and writes the updated file to disk (or produces a diff in `--dry-run`).

5. Commit / PR
   - If changes exist, the Git Integrator creates a branch (e.g., `docs-sync/<timestamp>`), stages and commits the updated `docs/api.md`. If `--create-pr` is set, it creates a draft PR with a summary of changes and any parsing errors included in the description.

6. Review
   - Human reviewer inspects the branch/PR, requests changes, or merges.

## Operational Concerns
- Idempotence: Generated sections must be deterministic; run should not flip content on repeated runs.
- Partial fails: On parser failures, include partial documentation and list errors in PR description.
- Config: Allow configuration via `.docsyncrc` or `pyproject.toml` with keys for `docs_path`, `branch_prefix`, `pr_target`, and `frameworks`.

## Minimal File Layout (MVP)

```
docs/                # target documentation
  api.md
src/
  docs_sync/
    __main__.py      # CLI entrypoint
    parser.py        # AST extraction logic
    generator.py     # Markdown generation
    git_integ.py     # Git branch/commit and PR helpers
    config.py        # config loading
pyproject.toml
requirements.txt
README.md
```

## Next Steps
1. Scaffold project structure and create initial CLI and parser module.
2. Implement basic `ast`-based parser and generator that updates `docs/api.md` in dry-run mode.
3. Add git commit/branch behavior and optional PR creation.
