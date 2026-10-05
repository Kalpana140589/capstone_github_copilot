Automated Documentation Sync — Requirements

## Overview
Automated Documentation Sync watches source code for changes to API endpoints and function signatures, regenerates `docs/api.md` to match the implementation, and creates a commit or draft PR with the updates so documentation does not drift from code.

## Goals (MVP)
- Support Python projects (FastAPI, Flask, or generic Python modules).
- Provide a CLI tool that can run locally or in CI to scan a repository and update `docs/api.md`.
- Detect changes via git diffs or by parsing source files for function signatures and docstrings.
- When mismatches or errors are detected, create a branch/commit (or draft PR) containing documentation updates for human review.

## Functional Requirements
1. Discovery
   - Locate Python source files under a repository root (configurable path).
   - Optionally accept a list of entry points or modules to scan.

2. Change Detection
   - Use `git diff` (between current HEAD and target branch/commit) to identify changed files.
   - Fallback: full repository scan to detect signature or docstring changes.

3. Parsing and Extraction
   - Parse Python functions and classes to extract signatures and docstrings.
   - Detect common web framework route decorators for FastAPI and Flask (e.g., `@app.get`, `@router.post`, `@app.route`).

4. Documentation Generation
   - Generate or update `docs/api.md` with a structured summary of endpoints and function signatures.
   - Preserve existing manual sections where possible and only update generated sections (demarcated by markers).

5. Commit/PR Workflow
   - Create a new branch (configurable naming) and commit documentation changes.
   - Optionally open a draft PR (GitHub) or leave a branch for the user to review in the MVP.

6. Error Handling
   - On parsing errors or ambiguous signatures, log errors and include a clear summary in the commit/PR description.
   - If documentation is missing, generate a best-effort entry and mark it for human review.

## Non-Functional Requirements
- Implemented in Python as a CLI script/library with minimal dependencies.
- Configurable via a `pyproject.toml` section or a `.docsyncrc` file.
- Runs deterministically in CI and locally.

## Constraints & Assumptions
- MVP focuses on Python; additional language support is out of scope for Step 1.
- Integration with GitHub PR creation is optional for MVP; creating a branch+commit is required.

## Next Steps
1. Create project scaffold (CLI entry, parser module, git integration). 
2. Prototype parsing and mark-up generation for `docs/api.md`.
3. Add branch/commit creation and optional draft PR support.
