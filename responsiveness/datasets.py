"""Helpers for loading small example datasets."""

import pandas as pd

GH_DATA_URL = "https://raw.githubusercontent.com/ustunb/reachml/main/data/"


def givemecredit_cts_slim(n=100, label=None):
    """Load a slimmed GiveMeCredit dataset sample.

    Args:
        n: Number of rows to sample.
        label: Desired label encoding, e.g. ``[-1, 1]`` or ``[0, 1]``.

    Returns:
        Tuple of (X, y) with features and labels.
    """
    if label is None:
        label = [-1, 1]
    filename = "givemecredit_cts.csv"
    data_df = pd.read_csv(GH_DATA_URL + filename)
    data_df = data_df.sample(n=n, random_state=0).astype(float)

    if list(label) == [0, 1]:
        data_df.iloc[:, 0] = data_df.iloc[:, 0].replace(-1, 0)

    X, y = data_df.iloc[:, 1:], data_df.iloc[:, 0]

    return X, y


def credit():
    """Load the credit dataset.

    Returns:
        Tuple of (X, y) with features and labels.
    """
    filename = "credit.csv"
    data_df = pd.read_csv(GH_DATA_URL + filename)

    X, y = data_df.iloc[:, 1:], data_df.iloc[:, 0]

    return X, y
