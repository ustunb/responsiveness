# Coding Rules

## Purpose
Prevent structural bloat while preserving clear representations.
These rules apply to all code changes unless explicitly overridden.

---

## 1. Prefer composed expressions over verbose control flow

When semantics are unchanged and there are no side effects:
- Prefer comprehensions, generator expressions, and built-ins (any, all, sum)
- Prefer single composed expressions over multi-step mutations

---

## 2. Single exit point per function

- Each function should have exactly one `return` statement at the end
- Use a single output variable named `out` to collect the result
- Structure logic as if/elif/else assigning to `out`, then `return out`
- Exceptions: one-liners and early `raise` for validation errors

---

## 3. Avoid defensive checks unless crossing a public API boundary

- Do not add defensive type conversions or verbose assertions in internal code
- Internal code may assume representations enforced by tests
- Assertions should enforce invariants, not produce detailed diagnostics

---

## 4. Introduce helpers only to name concepts or enable reuse

- Inline single-use helpers that do not name a concept
- Extract a helper if it:
  - represents a conceptual operation, or
  - clarifies an object's responsibility, or
  - is reused in multiple places

---

## 5. Do not add behavior that is not enforced by tests

- New checks, branches, or invariants require test coverage
- Simplifying or weakening assertions is allowed if invariants remain enforced

---

## 6. Prefer deletion over refactoring when simplifying

- Remove redundant logic, dead code, and unnecessary indirection
- Deletion is preferred to restructuring equivalent logic

---

## 7. Prefer explicit representations over ad hoc structures

- Replace dictionaries and magic values with structured objects and named constants
- Move implicit structure into explicit attributes or methods

---

## 8. Centralize representation checks behind `__check_rep__` when used

- If representation invariants require runtime validation, implement them in a dedicated `__check_rep__` method.
- Do not scatter invariant checks across methods.
- `__check_rep__` must:
  - check invariants only
  - have no side effects
  - return `True`
- Calls to `__check_rep__` should be wrapped in `assert` (e.g., `assert self.__check_rep__()`)
- Calls should be explicit and limited (e.g., constructor, mutation boundaries).

Do not introduce `__check_rep__` unless invariants are nontrivial and cannot be enforced structurally or by tests alone.

---

## 9. Prefer vectorized NumPy over Python loops

- Prefer vectorized NumPy/SciPy operations over Python loops for array computations
- Use `np.isfinite`, `np.isclose`, `np.allclose` over manual comparisons
- Use broadcasting, fancy indexing, and ufuncs instead of element-wise iteration
- Exception: loops are acceptable when iteration order matters or operations have side effects

---

## 10. Dataclass conventions

- Use `@dataclass` for data-holding classes
- Use `__post_init__` for derived attributes and validation
- Use `field(default_factory=...)` for mutable defaults
- Do not use bare mutable defaults (lists, dicts, sets) in dataclass fields

---

## 11. ABC polymorphism

- Use `ABC` + `@abstractmethod` for constraint and strategy polymorphism
- Concrete subclasses must implement all abstract methods
- Do not duck-type where an ABC exists
- Type hints should reference the ABC, not concrete subclasses

---

## 12. Solver abstraction boundary

- Solver-specific code stays behind `BaseMIP`
- Never import CPLEX or SCIP directly outside `mip/`
- All solver interaction goes through the `BaseMIP` interface
- New solver features require extending `BaseMIP`, not bypassing it
