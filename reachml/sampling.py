"""Sampling utilities for reachable sets and partitions."""

from functools import reduce

import numpy as np

from .partition import GeneratorConfig
from .utils import DEFAULT_SOLVER


class ReachableSetSampler:
    """Object to sample from the reachable set for a point x."""

    _RND_PRECISION = 4

    def __init__(self, action_set, x, solver=DEFAULT_SOLVER, **kwargs):
        """Initialize the sampler with an action set and point `x`."""
        self._action_set = action_set
        self._x = x
        self._solver = solver

        # random seed
        default_seed = abs(
            hash(x.astype(np.float32).round(ReachableSetSampler._RND_PRECISION).tobytes())
        )
        seed = kwargs.get("seed", default_seed)
        rng = np.random.default_rng(seed)
        self._master_rng = rng
        self._seed = seed

        self._config = GeneratorConfig(solver=self._solver, seed=seed)
        self._partitions = self._action_set.get_partitions(self.x, rng, config=self._config)

    @property
    def action_set(self):
        """Action set whose partitions are sampled."""
        return self._action_set

    @property
    def partition(self):
        """Actionable partitions of the action set."""
        return self._action_set.actionable_partition

    @property
    def x(self):
        """Current point being sampled around."""
        return self._x

    @property
    def seed(self):
        """Seed used for the random number generator."""
        return self._seed

    @x.setter
    def x(self, value):
        self._x = value

    @seed.setter
    def seed(self, value):
        self._seed = value
        self._master_rng = np.random.default_rng(value)

        for p in self._partitions:
            p.rng = self._master_rng.spawn(1)[0]

    def sample(self, n):
        """Sample `n` full points by stitching per-partition samples."""
        Xs = np.repeat(self.x.reshape(1, -1), n, axis=0)

        # Handle empty partition (no actionable features)
        if not self.partition:
            return Xs

        part_samples = [p.sample(n) for p in self._partitions]
        part_idx = reduce(lambda x, y: x + y, self.partition)
        Xs[:, part_idx] = np.hstack(part_samples)  # update the sampled part

        # do we want to return or store the samples in the object?
        return Xs

    def reset_rng(self):
        """Reset the random number generator."""
        ReachableSetSampler.generate_seed(self.x)

    @staticmethod
    def generate_seed(x):
        """Generate a deterministic seed from a numeric vector `x`."""
        return abs(hash(x.astype(np.float32).round(ReachableSetSampler._RND_PRECISION).tobytes()))
