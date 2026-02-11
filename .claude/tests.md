# Tests

## Purpose
Define what kinds of tests are allowed and what they must justify.
Tests exist to enforce invariants and workflows, not to mirror implementation structure.

## Scope
Applies whenever CC writes, edits, or reviews tests.

---

## 1. Tests must correspond to explicit invariants or workflows

- Every test must enforce at least one:
  - representation invariant, or
  - end-to-end workflow behavior
- If a test does not introduce a new failure mode, it should not exist

---

## 2. Structure tests around strategy dimensions

- Write tests as parametrized functions, not classes
- Parameters should map to dimensions of a test strategy (e.g., `d`, `model_type`, `signed`)
- Each parameter combination represents a distinct test case

Two parametrization styles are supported:
- **Parametrized fixtures** (`@pytest.fixture(params=...)`): preferred when the same generated data is shared across multiple test functions in a file or across files
- **`@pytest.mark.parametrize`**: preferred for simple dimension sweeps within a single test function

Use helper functions for shared construction logic.

```python
# Good: parametrize for simple sweeps within one test
@pytest.mark.parametrize("model_type", ["linear", "checklist", "rulelist"])
@pytest.mark.parametrize("d", [2, 3, 4])
def test_labelling_is_monotonic(model_type, d):
    labellings = load_labellings(model_type, d)
    assert check_monotonic(labellings, d)

# Good: parametrized fixture for shared data across tests
@pytest.fixture(params=[2, 3, 4])
def partition(request):
    return build_partition(d=request.param)

def test_partition_is_complete(partition):
    assert partition.is_complete()

def test_partition_is_disjoint(partition):
    assert partition.is_disjoint()
```

Do not introduce test classes. Parametrization expresses the test space.

---

## 3. Separate invariant tests from workflow tests

- Invariant tests:
  - validate object state, representation constraints, or consistency conditions
- Workflow tests:
  - validate that objects can be constructed, used, saved, and reused correctly

Do not mix invariant checks and workflow logic in the same test unless necessary.

---

## 4. Do not test implementation details

- Do not test private methods directly unless they define a representation invariant
- Do not test intermediate variables, internal helpers, or control flow
- Tests should remain valid under refactoring that preserves behavior

---

## 5. One behavioral claim per test

- A test should fail for one clear reason
- Prefer multiple small tests over one test with many assertions
- Avoid tests that assert many loosely related conditions

Exception: invariant tests may assert multiple closely related conditions.

---

## 6. Do not invent new invariants during test writing

- All invariants must be agreed upon during test design
- If an invariant is unclear or missing, stop and ask one question
- Do not "discover" invariants opportunistically while writing tests

---

## 7. Keep tests minimal and readable

- Avoid excessive setup inside tests
- Extract shared construction into helper functions
- Remove redundant assertions and overlapping tests

Deletion is preferred to expansion.

---

## 8. Test failures should be informative but minimal

- Assertion messages are optional
- Prefer simple assertions over verbose error strings
- Clarity comes from test structure, not error text
