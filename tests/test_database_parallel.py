import pathlib

import h5py
import numpy as np
import pytest

from reachml.database import ReachableSetDatabase


def _read_db(path):
    out = {}
    with h5py.File(path, "r") as db:
        for key in db.keys():
            out[key] = {
                "X": db[key][...],
                "x": db[key].attrs["x"],
                "metadata": db[key].attrs["metadata"],
                "stats": db[key].attrs["stats"],
            }
    return out


def _assert_db_equal(db_a, db_b):
    assert set(db_a.keys()) == set(db_b.keys())
    for key in db_a:
        assert np.array_equal(db_a[key]["X"], db_b[key]["X"])
        assert np.array_equal(db_a[key]["x"], db_b[key]["x"])
        assert np.array_equal(db_a[key]["metadata"], db_b[key]["metadata"])
        assert np.array_equal(db_a[key]["stats"][:2], db_b[key]["stats"][:2])


def _build_db(tmp_path, action_set, method, n_workers, X, **kwargs):
    db_path = pathlib.Path(tmp_path) / f"db_{method}_{n_workers}"
    db = ReachableSetDatabase(action_set, path=db_path, method=method)
    db.generate(X, n_workers=n_workers, **kwargs)
    return _read_db(db_path)


def test_parallel_matches_sequential_enumerate(dataset_actionset_2d, tmp_path):
    X = dataset_actionset_2d["X"].values
    X = np.vstack([X, X[:1]])
    A = dataset_actionset_2d["A"]

    seq = _build_db(tmp_path, A, "enumerate", None, X)
    par = _build_db(tmp_path, A, "enumerate", 2, X)
    _assert_db_equal(seq, par)


def test_parallel_matches_sequential_sample(dataset_actionset_2d, tmp_path):
    X = dataset_actionset_2d["X"].values
    X = np.vstack([X, X[:1]])
    A = dataset_actionset_2d["A"]

    seq = _build_db(tmp_path, A, "sample", None, X, seed=123, n=8)
    par = _build_db(tmp_path, A, "sample", 2, X, seed=123, n=8)
    _assert_db_equal(seq, par)


def test_edge_cases_empty_single_overwrite(dataset_actionset_2d, tmp_path):
    A = dataset_actionset_2d["A"]
    n_features = len(A)

    empty = np.empty((0, n_features))
    db_path = pathlib.Path(tmp_path) / "db_empty"
    db = ReachableSetDatabase(A, path=db_path, method="enumerate")
    with pytest.raises(AssertionError):
        db.generate(empty, n_workers=None)
    with pytest.raises(AssertionError):
        db.generate(empty, n_workers=2)

    single = dataset_actionset_2d["X"].values[:1]
    db_single_path = pathlib.Path(tmp_path) / "db_single"
    db_single = ReachableSetDatabase(A, path=db_single_path, method="enumerate")
    db_single.generate(single, n_workers=2)
    assert len(db_single.keys()) == 1

    sample_path = pathlib.Path(tmp_path) / "db_overwrite"
    db_sample = ReachableSetDatabase(A, path=sample_path, method="sample")
    db_sample.generate(single, n_workers=None, seed=1, n=6)
    before = _read_db(sample_path)
    db_sample.generate(single, n_workers=2, overwrite=True, seed=2, n=6)
    after = _read_db(sample_path)
    assert set(before.keys()) == set(after.keys())
    key = next(iter(before.keys()))
    # When all features are immutable, samples are always identical (copies of x)
    # regardless of seed, so we only check for different results when actionable
    if A.actionable_partition:
        assert not np.array_equal(before[key]["X"], after[key]["X"])


def test_reproducibility_same_seed_parallel(dataset_actionset_2d, tmp_path):
    X = dataset_actionset_2d["X"].values
    A = dataset_actionset_2d["A"]

    first = _build_db(tmp_path, A, "sample", 2, X, seed=999, n=7)
    second = _build_db(tmp_path, A, "sample", 2, X, seed=999, n=7)
    _assert_db_equal(first, second)
