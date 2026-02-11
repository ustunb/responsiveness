# Docstrings

## Scope

Applies only when generating or editing docstrings.
- Modify docstrings only.
- Do not change code, tests, or formatting.
- Docstrings must not introduce new behavior or new invariants.
- If unsure, omit rather than speculate.

---

## 1. Class docstrings must list representation invariants

Every public class must include an explicit list of representation invariants.
- Invariants must be declarative and checkable.
- Invariants must be enforced by tests or constructors.
- Invariants are normative and must not be omitted.

If invariants are unclear or missing, stop and ask one question.

---

## 2. Docstring structure is mandatory

Class docstrings must follow this structure exactly.

```
First line: one-sentence summary.

Representation invariants:
- invariant 1
- invariant 2
- invariant 3

----

Optional explanatory text.
```

Rules:
- Everything above `----` is normative.
- Everything below `----` is optional and explanatory.
- Nothing below `----` may introduce new invariants or constraints.
- Tests may rely on content above `----`.

---

## 3. No docstring-driven changes

- Do not modify code or tests to satisfy a docstring.
- If a discrepancy exists, fix or remove the docstring content.

---

## 4. Representation invariants are authoritative

- Tests may rely on invariants stated in class docstrings.
- Code may assume invariants hold after construction.
- Refactors must preserve stated invariants.

If code or tests contradict an invariant, correct or remove the invariant.

---

## 5. Method docstrings are optional and constrained

Method docstrings may be omitted.

If present, they may include only:
- input and output contracts
- externally visible side effects

Do not include:
- representation invariants
- implementation details
- control flow descriptions

---

## 6. Examples are optional and subordinate

- Examples are allowed only below `----`.
- At most one example per class or method.
- Examples must be copied from existing tests.
- Do not invent usage patterns.

If no suitable test exists, omit the example.

---

## 7. Do not restate type annotations

- Do not duplicate information already present in signatures or type hints.
- Prefer omission to redundancy.

---

## Output discipline

- Modify docstrings only.
- Do not change code, tests, or formatting.
- Do not explain changes.
