"""MIP backend interface, settings, and shared helpers.

Defines the `MIPBackend` protocol implemented by solver backends (CPLEX/SCIP),
common helpers, and the `load_backend` registry used by the public MIP facade.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol, Tuple

import numpy as np

from ..action_set import ActionSet


@dataclass(frozen=True)
class MIPSettings:
    """Solver settings shared across backends."""

    eps_min: float = 0.5
    round_precision: int = 8


class MIPBackend(Protocol):
    """Protocol each solver backend must implement."""

    solver_name: str

    # Build/configure
    def build_model(
        self, action_set: ActionSet, x: np.ndarray, actionable_indices: List[int]
    ) -> Tuple[object, object]:
        """Build and return the solver model and indices."""
        ...

    def configure(self, model: object, print_flag: bool) -> object:
        """Configure solver parameters for output and stability."""
        ...

    def add_constraints(
        self, model: object, indices: object, action_set: ActionSet, x: np.ndarray
    ) -> Tuple[object, object]:
        """Add action set constraints to the solver model."""
        ...

    # Solve/inspect
    def solve(self, model: object) -> None:
        """Solve the optimization model."""
        ...

    def has_solution(self, model: object) -> bool:
        """Return True if the model has a feasible solution."""
        ...

    def read_vectors(
        self, model: object, indices: object, names: List[str]
    ) -> Dict[str, np.ndarray]:
        """Read solution vectors by name from the model."""
        ...

    def add_nogood(
        self,
        model: object,
        indices: object,
        actions: List[np.ndarray],
        actionable_indices: List[int],
        settings: MIPSettings,
    ) -> Tuple[object, object, int]:
        """Add nogood constraints to exclude prior solutions."""
        ...

    def stats(self, model: object) -> Dict:
        """Return solver statistics for the model."""
        ...

    # Generic constraint operations
    def add_linear_constraint(
        self,
        model: object,
        indices: object,
        name: str,
        terms: List[tuple[str, int, float]],
        sense: str,
        rhs: float,
    ) -> None:
        """Add a linear constraint defined by indexed terms."""
        ...

    def delete_constraint(self, model: object, indices: object, name: str) -> None:
        """Delete a named constraint from the model."""
        ...

    def solution_status(self, model: object) -> str:
        """Return solver-native solution status."""
        ...


# --------------- Common checks/helpers ---------------


def check_bounds(values: np.ndarray, lb: np.ndarray, ub: np.ndarray, tol: float = 1e-9) -> bool:
    """Return True if values are within [lb, ub] with tolerance."""
    values = np.array(values)
    lb = np.array(lb)
    ub = np.array(ub)
    return np.all(values >= lb - tol) and np.all(values <= ub + tol)


def check_abs_decomposition(
    a: np.ndarray, a_pos: np.ndarray, a_neg: np.ndarray, tol: float = 1e-9
) -> bool:
    """Return True if a == a_pos - a_neg and |a| == a_pos + a_neg."""
    a = np.array(a)
    a_pos = np.array(a_pos)
    a_neg = np.array(a_neg)
    return np.allclose(a, a_pos - a_neg, atol=tol) and np.allclose(
        np.abs(a), a_pos + a_neg, atol=tol
    )


def check_nogood_dp_dn(
    sign: np.ndarray, dp: np.ndarray, dn: np.ndarray, eps_min: float, tol: float = 1e-9
) -> bool:
    """Return True if nogood sign/abs constraints are satisfied."""
    l1 = np.sum(dp + dn, axis=1)
    if not np.all(l1 >= eps_min - tol):
        return False
    if np.any(np.logical_and(dp > tol, dn > tol)):
        return False
    if not np.allclose(sign[dp > tol], 1.0, atol=tol):
        return False
    if not np.allclose(sign[dn > tol], 0.0, atol=tol):
        return False
    return True


def load_backend(name: str) -> MIPBackend:
    """Dynamically import and return the backend implementation for ``name``."""
    if name == "cplex":
        from .backends.cplex import CplexBackend

        return CplexBackend()
    if name == "scip":
        from .backends.scip import ScipBackend

        return ScipBackend()
    raise ValueError(f"unknown solver backend: {name}")
