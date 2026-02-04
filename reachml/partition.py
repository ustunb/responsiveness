"""Partition abstractions for enumeration and sampling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .mip import BaseMIP
from .utils import DEFAULT_SOLVER


@dataclass
class GeneratorConfig:
    """Configuration options for sampling over partitions."""

    solver: str = DEFAULT_SOLVER
    seed: Optional[int] = None
    min_binary: Optional[int] = None


class Partition(ABC):
    """Abstract partition over a subset of features."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize partition with action set, point, and optional RNG/config."""
        from .action_set import ActionSet

        assert isinstance(action_set, ActionSet)
        assert isinstance(x, (list, np.ndarray))
        x = np.array(x).flatten()
        assert len(x) == len(action_set)

        self._action_set = action_set
        self._x = x
        self._rng = rng
        self._config = config if config is not None else GeneratorConfig()
        self._complete = False

    @property
    def action_set(self):
        """Partition action set."""
        return self._action_set

    @property
    def x(self):
        """Partition feature vector."""
        return self._x

    @property
    def rng(self):
        """Random generator for this partition."""
        return self._rng

    @rng.setter
    def rng(self, value):
        self._rng = value

    @property
    def config(self):
        """Sampling config for this partition."""
        return self._config

    @property
    def part_size(self):
        """Number of features in this partition."""
        return len(self._action_set)

    @property
    def complete(self):
        """Whether enumeration has completed for this partition."""
        return self._complete

    @property
    def feasible_actions(self):
        """Feasible action vectors for this partition."""
        raise NotImplementedError()

    @classmethod
    def from_action_set(cls, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Factory for partition objects based on action set structure."""
        n_features = len(action_set)
        assert n_features > 0, "action_set must be non-empty"

        if n_features == 1:
            if action_set[0].discrete:
                return SingleDiscretePartition(action_set, x, rng=rng, config=config)
            return SingleContinuousPartition(action_set, x, rng=rng, config=config)

        discrete_flags = [e.discrete for e in action_set]
        if all(discrete_flags):
            return JointDiscretePartition(action_set, x, rng=rng, config=config)
        if any(discrete_flags):
            return MixedPartition(action_set, x, rng=rng, config=config)
        return JointContinuousPartition(action_set, x, rng=rng, config=config)

    @abstractmethod
    def enumerate(self, **kwargs) -> np.ndarray:
        """Enumerate feasible actions for this partition."""
        raise NotImplementedError()

    @abstractmethod
    def sample(self, n, **kwargs) -> np.ndarray:
        """Sample points for this partition."""
        raise NotImplementedError()

    def _get_rng(self):
        if self._rng is None:
            self._rng = np.random.default_rng(self._config.seed)
        return self._rng

    def _check_feasibility(self, samples):
        """Check feasibility of samples via MIP feasibility checks."""
        mip_obj = BaseMIP(self.action_set, self.x)
        actions = samples - self.x

        out = []
        for a in actions:
            for i, a_i in enumerate(a):
                mip_obj.add_linear_constraint(
                    name=f"match_c[{i}]",
                    terms=[("c", i, 1.0)],
                    sense="E",
                    rhs=float(a_i),
                )

            mip_obj.solve_model()
            out.append(bool(mip_obj.solution_exists))

            for i in range(len(a)):
                mip_obj.delete_constraint(f"match_c[{i}]")

        return out


class SingleDiscretePartition(Partition):
    """Singleton discrete partition."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize single discrete partition."""
        super().__init__(action_set, x, rng=rng, config=config)
        assert len(action_set) == 1
        self._feasible_actions = (
            action_set[0].reachable_grid(self.x[0], return_actions=True).reshape(-1, 1)
        )
        self._values = action_set[0].reachable_grid(self.x[0], return_actions=False)
        self._complete = True

    @property
    def feasible_actions(self):
        """Return feasible actions for this partition."""
        return self._feasible_actions

    def enumerate(self, **kwargs) -> np.ndarray:
        """Return pre-computed feasible actions."""
        return self._feasible_actions

    def sample(self, n, **kwargs) -> np.ndarray:
        """Sample n points uniformly from reachable grid."""
        rng = self._get_rng()
        out = rng.choice(self._values, n, replace=True).reshape(-1, 1)
        return out


class SingleContinuousPartition(Partition):
    """Singleton continuous partition."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize single continuous partition."""
        super().__init__(action_set, x, rng=rng, config=config)
        assert len(action_set) == 1
        self._lb, self._ub = action_set[0].feasible_bound(self.x[0], return_actions=False)

    def enumerate(self, **kwargs) -> np.ndarray:
        """Enumerate not supported for continuous partitions."""
        raise NotImplementedError()

    def sample(self, n, **kwargs) -> np.ndarray:
        """Sample n points uniformly from feasible bounds."""
        rng = self._get_rng()
        out = rng.uniform(self._lb, self._ub, n).reshape(-1, 1)
        return out


class JointDiscretePartition(Partition):
    """Joint discrete partition with more than one feature."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize joint discrete partition with MIP enumerator."""
        super().__init__(action_set, x, rng=rng, config=config)
        # Eagerly create enumerator to check constraint feasibility
        self._enumerator = self._create_enumerator()

    @property
    def feasible_actions(self):
        """Return feasible actions from enumerator."""
        if self._enumerator is None:
            return np.zeros((1, len(self.x)))
        return self._enumerator.feasible_actions

    def _create_enumerator(self):
        from .enumeration import ReachableSetEnumerationMIP

        return ReachableSetEnumerationMIP(
            action_set=self.action_set,
            x=self.x,
            print_flag=False,
            solver=self.config.solver,
        )

    def _should_enumerate(self) -> bool:
        return any(
            constraint.prefer_enumeration_for_sampling()
            for constraint in self.action_set.constraints
        )

    def enumerate(self, max_points=float("inf"), time_limit=None, node_limit=None, **kwargs):
        """Enumerate feasible actions using MIP solver."""
        self._enumerator.enumerate(
            max_points=max_points, time_limit=time_limit, node_limit=node_limit
        )
        self._complete = self._enumerator.complete
        return self._enumerator.feasible_actions

    def sample(self, n, **kwargs) -> np.ndarray:
        """Sample n points, using enumeration or rejection sampling."""
        if self._should_enumerate():
            return self._sample_enumerate(n)
        return self._sample_reject(n)

    def _sample_reject(self, n):
        n_remaining = n
        out = []

        while n_remaining > 0:
            samples = np.hstack([self._sample_1d(j, n_remaining) for j in range(self.part_size)])
            keep = self._check_feasibility(samples)
            out.append(samples[keep])
            n_remaining -= np.sum(keep)

        return np.vstack(out)

    def _sample_enumerate(self, n):
        rng = self._get_rng()
        self._enumerator.enumerate()
        actions = np.array(self._enumerator.feasible_actions)
        values = self.x + actions
        return rng.choice(values, n, replace=True)

    def _sample_1d(self, j, n):
        rng = self._get_rng()
        acts = self.action_set[j].reachable_grid(self.x[j], relax=True, return_actions=False)
        return rng.choice(acts, n, replace=True).reshape(-1, 1).astype(np.float32)


class JointContinuousPartition(Partition):
    """Joint continuous partition with more than one feature."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize joint continuous partition with bounds."""
        super().__init__(action_set, x, rng=rng, config=config)
        bounds = np.array(
            [self.action_set[j].feasible_bound(self.x[j]) for j in range(self.part_size)]
        )
        self._lbs = bounds[:, 0]
        self._ubs = bounds[:, 1]

    def enumerate(self, **kwargs) -> np.ndarray:
        """Enumerate not supported for continuous partitions."""
        raise NotImplementedError()

    def sample(self, n, check=True, **kwargs) -> np.ndarray:
        """Sample n points with optional feasibility checking."""
        rng = self._get_rng()
        n_remaining = n
        out = []
        while n_remaining > 0:
            samples = rng.uniform(self._lbs, self._ubs, (n_remaining, self.part_size))
            keep = self._check_feasibility(samples) if check else np.ones(n_remaining, dtype=bool)
            out.append(samples[keep])
            n_remaining -= np.sum(keep)

        return np.vstack(out)


class MixedPartition(Partition):
    """Partition with mixed discrete and continuous features."""

    def __init__(self, action_set, x, rng=None, config: Optional[GeneratorConfig] = None):
        """Initialize mixed partition with separate discrete/continuous samplers."""
        super().__init__(action_set, x, rng=rng, config=config)
        self.disc_part = [i for i, a in enumerate(self.action_set) if a.discrete]
        self.cts_part = list(set(range(len(self.action_set))) - set(self.disc_part))

        rng = self._get_rng()
        disc_rng, cts_rng = rng.spawn(2)
        self.samplers = {
            "disc": JointDiscretePartition(
                self.action_set[self.disc_part],
                self.x[self.disc_part],
                disc_rng,
                self.config,
            ),
            "cts": JointContinuousPartition(
                self.action_set[self.cts_part],
                self.x[self.cts_part],
                cts_rng,
                self.config,
            ),
        }

    def enumerate(self, **kwargs) -> np.ndarray:
        """Enumerate not supported for mixed partitions."""
        raise NotImplementedError()

    def sample(self, n, **kwargs) -> np.ndarray:
        """Sample n points by combining discrete and continuous samples."""
        n_remaining = n
        out = []
        while n_remaining > 0:
            disc_samples = self.samplers["disc"].sample(n_remaining)
            cts_samples = self.samplers["cts"].sample(n_remaining, check=False)
            samples = np.hstack([disc_samples, cts_samples])
            keep = self._check_feasibility(samples)
            out.append(samples[keep])
            n_remaining -= np.sum(keep)
        return np.vstack(out)
