"""Parallel worker utilities for reachable set generation."""

from __future__ import annotations

import time
from copy import deepcopy
from typing import Sequence

import cloudpickle
import numpy as np

from .reachable_set import EnumeratedReachableSet, SampledReachableSet


def _pack_result(key: str, x: np.ndarray, reachable_set, final_time: float):
    stats = {
        "n_points": len(reachable_set),
        "complete": reachable_set.complete,
        "time": final_time,
    }
    metadata_values = reachable_set._get_metadata().astype(np.float32).values
    return (
        key,
        np.array(x),
        reachable_set.X,
        metadata_values,
        stats,
    )


def _parallel_generate_sibling_group(
    action_set_bytes: bytes,
    keys: Sequence[str],
    sibling_indices: Sequence[int],
    U_subset: np.ndarray,
    seed_sequences: Sequence[object],
    immutable: Sequence[int],
    method: str,
    kwargs: dict,
):
    """Generate reachable sets for a sibling group in a worker process."""
    action_set = cloudpickle.loads(action_set_bytes)
    reachable_set_cls = EnumeratedReachableSet if method == "enumerate" else SampledReachableSet

    sibling_indices = list(sibling_indices)
    if len(sibling_indices) != U_subset.shape[0]:
        raise ValueError("Sibling indices and U_subset length mismatch.")

    results = []
    base_kwargs = dict(kwargs)
    base_kwargs["seed"] = seed_sequences[0] if seed_sequences else None

    start_time = time.time()
    base_rs = reachable_set_cls(action_set, U_subset[0], **base_kwargs)
    base_rs.generate(**base_kwargs)
    final_time = time.time() - start_time
    results.append(_pack_result(keys[0], U_subset[0], base_rs, final_time))

    for idx in range(1, U_subset.shape[0]):
        x = U_subset[idx]
        local_kwargs = dict(kwargs)
        local_kwargs["seed"] = seed_sequences[idx] if seed_sequences else None

        start_time = time.time()
        if method == "enumerate":
            sib_rs = reachable_set_cls(action_set, x, values=base_rs.X, **local_kwargs)
            sib_rs.X[:, immutable] = x[immutable]
            sib_rs._complete = True
        else:
            sib_rs = deepcopy(base_rs)
            sib_rs.seed = local_kwargs.get("seed", sib_rs.seed)
            sib_rs.x = x
            sib_rs.reset()
            sib_rs.generate(**local_kwargs)

        final_time = time.time() - start_time
        results.append(_pack_result(keys[idx], x, sib_rs, final_time))

    return results
