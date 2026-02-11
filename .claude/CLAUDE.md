# Repo Instructions

## Always load
- `.claude/rules.md`

## Optional constraint files
- `.claude/minimization.md`
- `.claude/tests.md`
- `.claude/docstrings.md`

## Activation rules

Load an optional constraint file only when explicitly activated.

Explicit activation means:
- a slash command (e.g., `/minimize`, `/test-review`)
- a flag (e.g., `--minimize`, `--tests`, `--docstrings`)
- an exact phrase (e.g., "load minimization rules")

Not explicit:
- "clean up", "refactor", "tidy", "improve", or similar vague language

Slash commands implicitly load their corresponding constraint file without confirmation.

Mid-session explicit requests take effect immediately.

## Session-start behavior

If the user's initial request is ambiguous, ask once which optional constraints to load.

Do not ask if:
- the request includes a slash command or flag
- intent is clear from context

Never infer or auto-activate constraints. Ask at most once per session.

## Default

If unsure: baseline only, do less, ask at most one question.

## Plans

Store in `.claude/plans/next/`. Move to `.claude/plans/` when work begins.
