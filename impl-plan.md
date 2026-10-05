# Implementation Plan — Automated Documentation Sync

## Overview
This implementation plan breaks the work into prioritized, dependency-ordered tasks for the MVP. Tasks marked as parallelizable can proceed concurrently when their dependencies are satisfied.

## Ordered Tasks and Dependencies

1. Project scaffold (CLI + modules)
   - Deliverables: repository layout, `pyproject.toml` or `requirements.txt`, empty module files (`src/docs_sync/__main__.py`, `parser.py`, `generator.py`, `git_integ.py`, `config.py`), initial `README.md`.
   - Dependencies: none
   - Parallelizable: no

2. Core parser module (AST extraction)
   - Deliverables: `src/docs_sync/parser.py` with functions to parse Python files, extract signatures, docstrings, and detect route decorators.
   - Dependencies: Project scaffold
   - Parallelizable: yes (other tasks can work against stable interfaces)

3. Documentation generator (Markdown renderer)
   - Deliverables: `src/docs_sync/generator.py` that accepts parser output and produces deterministic Markdown fragments; marker-based replace in `docs/api.md`.
   - Dependencies: Project scaffold, Core parser (interface contract)
   - Parallelizable: yes

4. Git integration (branch/commit helpers)
   - Deliverables: `src/docs_sync/git_integ.py` implementing branch creation, staging, commit, and push (dry-run support).
   - Dependencies: Project scaffold
   - Parallelizable: yes

5. CLI orchestration and configuration
   - Deliverables: CLI (`__main__.py`) wiring parser, generator, and git integration; `--dry-run`, `--commit`, `--create-pr`, configuration load from `.docsyncrc`/`pyproject.toml`.
   - Dependencies: Parser, Generator, Git integration
   - Parallelizable: no (final integration step)

6. Optional: GitHub PR creation support
   - Deliverables: PR helper using `PyGithub` or REST API; draft PR creation with summary and parsing errors.
   - Dependencies: Git integration, CLI
   - Parallelizable: yes (can be added after core commit flow)

7. Configuration and exclusion patterns
   - Deliverables: config parsing module and support for exclude patterns, per-project config.
   - Dependencies: CLI and core modules
   - Parallelizable: yes

8. Secret-detection scan (pre-commit check)
   - Deliverables: integration with `detect-secrets` or simple regex scanner to block accidental secret commits.
   - Dependencies: Git integration
   - Parallelizable: yes

9. Unit tests
   - Deliverables: `pytest` tests for parser (AST extraction), generator (deterministic output), and git helpers (mocked operations).
   - Dependencies: Parser, Generator, Git integration
   - Parallelizable: yes

10. Integration tests & dry-run verification
    - Deliverables: small sample repo(s) in `tests/fixtures` and end-to-end tests verifying `--dry-run` outputs and branch creation behavior.
    - Dependencies: CLI, Git integration, Parser, Generator
    - Parallelizable: no (requires integrated components)

11. CI workflow
    - Deliverables: GitHub Actions workflow to run unit tests, run a `--dry-run` against fixtures, and optionally run the tool on push to main in a gated job.
    - Dependencies: Tests, Integration tests
    - Parallelizable: yes

12. Documentation and README
    - Deliverables: Usage examples, CI setup instructions, required GitHub permissions, configuration examples.
    - Dependencies: Core features implemented
    - Parallelizable: yes

13. Release (v0.1)
    - Deliverables: Tag, changelog, release notes
    - Dependencies: All major features and tests passing
    - Parallelizable: no

## Blocked or Parallelizable Tasks
- Blocked: Tasks relying on core parser/generator (CLI integration, integration tests, release).
- Parallelizable: Parser development, generator development, git_integ implementation, and configuration can be worked on concurrently once scaffold is in place.

## Prioritization Notes
- Focus initially on deterministic parser + generator + dry-run commit flow before adding PR creation and secret detection.
- Ensure test coverage for parser and generator to avoid noisy churn in docs.

## Next Steps
1. Create the project scaffold files and a minimal `pyproject.toml` / `requirements.txt` so implementers can run tests locally.
2. Start parser implementation and small unit tests.
