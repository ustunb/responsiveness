import numpy as np
import pytest

from reachml.action_set import ActionSet
from reachml.partition import (
    GeneratorConfig,
    JointContinuousPartition,
    JointDiscretePartition,
    MixedPartition,
    Partition,
    SingleContinuousPartition,
    SingleDiscretePartition,
)
from reachml.utils import SUPPORTED_SOLVERS


def test_single_discrete_partition_enumerate_and_sample():
    X = np.array([[0], [1]])
    A = ActionSet(X, names=["x0"])
    x = np.array([1])
    rng = np.random.default_rng(0)

    part = Partition.from_action_set(A, x=x, rng=rng, config=GeneratorConfig())
    assert isinstance(part, SingleDiscretePartition)

    actions = part.enumerate()
    assert set(map(tuple, actions.astype(int))) == {(0,), (-1,)}

    samples = part.sample(10)
    assert samples.shape == (10, 1)
    assert set(np.unique(samples).tolist()).issubset({0, 1})


def test_single_continuous_partition_sample():
    X = np.array([[0.2], [2.4]])
    A = ActionSet(X, names=["x0"])
    x = np.array([1.0])
    rng = np.random.default_rng(1)

    part = Partition.from_action_set(A, x=x, rng=rng, config=GeneratorConfig())
    assert isinstance(part, SingleContinuousPartition)

    samples = part.sample(5)
    assert samples.shape == (5, 1)
    assert np.all(samples >= A[0].lb)
    assert np.all(samples <= A[0].ub)

    with pytest.raises(NotImplementedError):
        part.enumerate()


@pytest.mark.parametrize("solver", SUPPORTED_SOLVERS)
def test_joint_discrete_partition_enumerate_and_sample(solver):
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    A = ActionSet(X, names=["x0", "x1"])
    x = np.array([1, 1])
    rng = np.random.default_rng(2)

    part = Partition.from_action_set(
        A,
        x=x,
        rng=rng,
        config=GeneratorConfig(solver=solver),
    )
    assert isinstance(part, JointDiscretePartition)

    actions = part.enumerate()
    assert set(map(tuple, actions.astype(int))) == {(0, 0), (0, -1), (-1, 0), (-1, -1)}

    samples = part.sample(10)
    assert samples.shape == (10, 2)
    assert set(np.unique(samples[:, 0]).tolist()).issubset({0, 1})
    assert set(np.unique(samples[:, 1]).tolist()).issubset({0, 1})


@pytest.mark.parametrize("solver", SUPPORTED_SOLVERS)
def test_joint_continuous_partition_sample(solver):
    X = np.array([[0.1, 0.2], [1.3, 2.7]])
    A = ActionSet(X, names=["x0", "x1"])
    x = np.array([0.5, 1.0])
    rng = np.random.default_rng(3)

    part = Partition.from_action_set(
        A,
        x=x,
        rng=rng,
        config=GeneratorConfig(solver=solver),
    )
    assert isinstance(part, JointContinuousPartition)

    samples = part.sample(5, check=True)
    assert samples.shape == (5, 2)
    assert np.all(samples[:, 0] >= A[0].lb)
    assert np.all(samples[:, 0] <= A[0].ub)
    assert np.all(samples[:, 1] >= A[1].lb)
    assert np.all(samples[:, 1] <= A[1].ub)

    with pytest.raises(NotImplementedError):
        part.enumerate()


@pytest.mark.parametrize("solver", SUPPORTED_SOLVERS)
def test_mixed_partition_sample(solver):
    X = np.array([[0, 0.3], [1, 1.7]])
    A = ActionSet(X, names=["b", "c"])
    x = np.array([0, 0.5])
    rng = np.random.default_rng(4)

    part = Partition.from_action_set(
        A,
        x=x,
        rng=rng,
        config=GeneratorConfig(solver=solver),
    )
    assert isinstance(part, MixedPartition)

    samples = part.sample(5)
    assert samples.shape == (5, 2)
    assert set(np.unique(samples[:, 0]).tolist()).issubset({0, 1})
    assert np.all(samples[:, 1] >= A[1].lb)
    assert np.all(samples[:, 1] <= A[1].ub)
