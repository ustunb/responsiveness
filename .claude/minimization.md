# Minimization

## Purpose
Reduce code size and surface area after behavior is correct and tests pass.
This phase prioritizes deletion, consolidation, and readability through removal.

## Precondition
- Tests pass.
- Public APIs are frozen.
- No new behavior may be introduced.

---

## 1. Delete redundant code aggressively

- Remove unused variables, dead branches, unreachable code, and unused helpers
- Inline helpers that are:
  - single-use, and
  - do not name a conceptual operation
- Prefer removing code to reorganizing it

---

## 2. Collapse verbose control flow

When semantics are unchanged:
- Replace loops with comprehensions or generator expressions
- Replace multi-step mutations with single composed expressions

Deletion is preferred over transformation.

---

## 3. Preserve single exit point

- Each function should have exactly one `return` statement at the end
- Use a single output variable named `out` to collect the result
- Do not convert single-exit functions to early returns
- Exceptions: one-liners and early `raise` for validation errors

---

## 4. Remove defensive programming inside the system boundary

- Remove redundant type checks, conversions, and guards
- Assume internal representations are valid as enforced by tests
- Keep only invariants that are explicitly tested

---

## 5. Deduplicate logic across methods and files

- Merge duplicated computations into a single implementation
- Prefer moving shared logic behind an existing object boundary
- If duplication is trivial (< 5 lines), delete one copy rather than abstracting
- If duplication is non-trivial (>= 5 lines of identical logic), extract a shared helper
  - Prefer module-level functions over new methods
  - This is consolidation, not new abstraction

---

## 6. Reduce naming and structural overhead

- Remove names that are used once and do not clarify meaning
- Inline variables that merely restate expressions
- Remove wrapper methods that only forward arguments

Fewer names is better if meaning is preserved.

---

## 7. Simplify assertions and error handling

- Keep only assertions that enforce invariants
- Remove detailed error messages unless required externally
- Prefer fewer, stronger assertions over many weak ones

---

## 8. Minimize tests by behavior, not by unit

- Remove tests that do not introduce a new failure mode
- Keep one test per behavioral or invariant claim
- Prefer workflow and invariant tests over micro-tests
- Do not introduce new tests during minimization

---

## 9. No redesign, no new abstractions

- Do not introduce new classes, protocols, or layers
- Do not rename public APIs
- Do not change behavior, performance characteristics, or semantics
- Exception: extracting a helper to deduplicate >= 5 lines (per Rule 5) is allowed

If simplification would require redesign, stop.

---

## 10. Use existing Enums for constrained parameters

- If a parameter accepts a fixed set of string values, check if a corresponding Enum exists
- Replace `param: str` with `param: ExistingEnum` when the Enum is already defined
- Do not create new Enums during minimization — only use existing ones

---

## 11. Ensure parallel structure in branches

- Match/if-else branches should assign the same set of variables in the same order
- If branches diverge in structure, flag for review
- Non-parallel branches often indicate missed abstraction or inconsistent handling

---

## Output discipline

- Output only modified code.
- Do not explain changes.
- If unsure whether code is redundant, delete it only if tests still pass.

---

## How this fits with rules.md

- rules.md constrains generation
- minimization.md authorizes destruction
- Overlap is intentional; minimization rules are stricter

---

## What this will catch (based on your diffs)

- Loop-heavy implementations
- Overprotective conversions and checks
- Redundant helpers and forwarding methods
- Duplicate test coverage
- Accidental verbosity introduced by CC
- String parameters that should use existing Enums
- Non-parallel match/if-else branches

This is where CC can safely delete 20-30 percent before you ever look at the code.
