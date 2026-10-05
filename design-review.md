# Design Review — Automated Documentation Sync

## Summary
This review evaluates the architecture described in `architecture.md` and identifies potential risks, security gaps, edge cases, recommended mitigations, agreed design decisions, and action items for the MVP.

## Risks and Edge Cases

1. Malformed or Missing Docstrings
   - Risk: `ast` parsing will succeed but docstrings may be missing, malformed, or contain non-API content leading to incomplete or incorrect docs.
   - Mitigation: Treat docstring extraction defensively: if a docstring is missing, generate a placeholder entry flagged for human review. Validate docstring formats (e.g., Google/NumPy/reST patterns) where possible and include parsing warnings in PR descriptions.

2. Private or Internal Endpoints Exposure
   - Risk: Internal/private functions or endpoints may be documented and exposed unintentionally.
   - Mitigation: Respect conventions (leading underscore) and framework-specific flags. Allow configuration to exclude modules, packages, or decorators (e.g., `@internal`), and default to excluding names prefixed with `_`.

3. Route Decorator Ambiguities
   - Risk: Decorator-based routing (wrapping functions, composition) may hide signatures or dynamically generate endpoints at runtime, causing false negatives/positives.
   - Mitigation: Support common decorator patterns for FastAPI/Flask and provide a heuristics layer that falls back to scanning imported router registrations. Document limitations and recommend runtime-openapi check for completeness.

4. Merge Conflicts on `docs/api.md`
   - Risk: Simultaneous updates (human edits + generated updates) may create merge conflicts.
   - Mitigation: Use generator markers to localize changes. When committing, use a branch per run and leave conflicts for manual resolution; include clear commit messages and PR descriptions. Optionally support an automated merge attempt: rebase target branch and re-apply generated changes, failing fast if conflicts remain.

5. Inconsistent Ordering Causing Noise
   - Risk: Non-deterministic ordering of extracted items (due to filesystem iteration) will cause churn in generated docs.
   - Mitigation: Sort extracted items deterministically (module path, class, function name) before rendering. Normalize types and default values consistently.

6. Large Repositories / Performance
   - Risk: Full-scan mode on large repos may be slow and resource heavy.
   - Mitigation: Default to git-diff mode; add concurrency with worker pools for parsing; provide `--paths` filter and caching (e.g., file mtime + content hash) to skip unchanged files.

7. Sensitive Data Leakage
   - Risk: Docstrings or code comments may inadvertently contain secrets (API keys, internal URLs) that get committed to a public repo.
   - Mitigation: Provide a pre-commit scrub step or scan using regex/secret-detection (e.g., `detect-secrets`) and block publishing when high-confidence secrets are found; redact or flag low-confidence matches in PR description.

8. Git / Auth Failures for PR Creation
   - Risk: Lack of credentials or insufficient permissions will fail PR creation or pushes in CI.
   - Mitigation: Fall back to creating a branch and commit only; surface clear error messages in logs and PR description template. Document required permissions and environment variables for GitHub integration.

9. Partial Failures and Rollbacks
   - Risk: Mid-run failures (parser crash, IO error) could leave partial changes or branches.
   - Mitigation: Run generation in a temporary working tree or branch, only move to final branch after successful end-to-end run. Clean up temporary branches on failure and include failure artifacts in an artifact store or PR description.

10. Conflicting Configurations Across Projects
   - Risk: Monorepos with multiple services may need different configs; a single default may be inappropriate.
   - Mitigation: Support per-project `.docsyncrc` and repository-level defaults; allow CLI override flags for CI jobs.

## Recommended Design Decisions (Agreed)

- Use `ast` for deterministic parsing and optionally support `libcst` for more advanced rewriting needs later.
- Default behavior: `git-diff` mode; `--scan-all` opt-in. Deterministic sort of extracted items before rendering.
- Use explicit delimiters in `docs/api.md` for generated sections and only update content within those markers.
- Create a branch per run; commit changes; do not auto-merge in MVP. Optionally create a draft PR when credentials are available.
- Exclude private names (leading underscore) by default and provide configurable exclusion patterns.
- Run all transformations in a temporary branch/worktree and only push when generation succeeds completely.

## Action Items

1. Implement placeholder handling for missing docstrings and include warnings in PR descriptions. (Owner: Implementation)
2. Implement configuration support for exclusion patterns and per-project configs. (Owner: Implementation)
3. Add deterministic sorting and normalization to the generator. (Owner: Implementation)
4. Add a `--dry-run` mode that produces a patch/diff without committing. (Owner: Implementation)
5. Add secret-detection scan before committing; fail or redact matches. (Owner: Implementation)
6. Implement temporary branch/worktree workflow to ensure atomic generation and safe cleanup on failure. (Owner: Implementation)
7. Document required GitHub permissions and CI environment variables in `README.md`. (Owner: Documentation)
