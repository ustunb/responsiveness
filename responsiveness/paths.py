"""Path helpers for data, results, and derived artifacts.

Defines directory constants and filename generators used across the project.
"""

from pathlib import Path

# Directories

# path to the GitHub repository
repo_dir = Path(__file__).resolve().parent.parent

# path to the Python package
pkg_dir = repo_dir / "responsiveness/"

# directory where we store datasets
data_dir = repo_dir / "data/"

# path to the Python package
tests_dir = repo_dir / "tests/"

# directory where we store results
results_dir = repo_dir / "results/"

# create local directories if they do not exist
results_dir.mkdir(exist_ok=True)


# Naming Functions
def get_data_csv_file(data_name, **kwargs):
    """Return the processed CSV file path for a dataset.

    Args:
        data_name: Dataset name.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the processed CSV file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    f = data_dir / data_name / f"{data_name}_processed.csv"
    return f


def get_data_file(data_name, action_set_name, **kwargs):
    """Return the serialized dataset file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the dataset file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    f = data_dir / f"{data_name}_{action_set_name}.data"
    return f


def get_action_set_file(data_name, action_set_name, **kwargs):
    """Return the action set file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the action set file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    f = data_dir / f"{data_name}_{action_set_name}.actionset"
    return f


def get_model_file(data_name, action_set_name, model_type, **kwargs):
    """Return the model file path for a dataset/action set.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        model_type: Model type identifier.
        **kwargs: Optional parameters such as `n_features` or `model_number`.

    Returns:
        Path to the model file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0

    f = f"{data_name}_{action_set_name}_{model_type}"

    if kwargs.get("n_features") is not None:
        assert isinstance(kwargs.get("n_features"), int)
        assert kwargs.get("meta_features") is not None
        n_feat = kwargs.get("n_features")
        meta_features = kwargs.get("meta_features")
        f += f"_n_feat_{n_feat}_{'+'.join([str(s) for s in meta_features])}"

    if kwargs.get("model_number") is not None:  # for glm
        assert isinstance(kwargs.get("model_number"), int)
        model_number = kwargs.get("model_number")
        f += f"_{model_number}"

    return results_dir / f"{f}.model"


def get_benchmark_results_file(data_name, action_set_name, method_name, model_type, **kwargs):
    """Return the benchmark results file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        method_name: Method name.
        model_type: Model type identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the benchmark results file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(method_name, str) and len(action_set_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    f = results_dir / f"{data_name}_{action_set_name}_{model_type}_{method_name}.results"
    return f


def get_audit_results_file(data_name, action_set_name, model_type, **kwargs):
    """Return the audit results file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        model_type: Model type identifier.
        **kwargs: Optional parameters such as `model_number`, `resp_thresh`, and `alpha`.

    Returns:
        Path to the audit results file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0

    f = f"{data_name}_{action_set_name}_{model_type}"

    if kwargs.get("model_number") is not None:  # for glm
        assert isinstance(kwargs.get("model_number"), int)
        model_number = kwargs.get("model_number")
        f += f"_model_{model_number}"

    if kwargs.get("resp_thresh") is not None:
        resp_thresh = kwargs.get("resp_thresh")
        f += f"_epsilon_{resp_thresh}"

    if kwargs.get("alpha") is not None:
        alpha = kwargs.get("alpha")
        f += f"_alpha_{alpha}"

    if kwargs.get("n") is not None:
        sample_size = kwargs.get("n")
        f += f"_n_{sample_size}"

    if kwargs.get("trial") is not None:
        trial = kwargs.get("trial")
        f += f"_trial_{trial}"

    return results_dir / f"{f}.audit"


def get_demo_results_file(data_name, action_set_name, **kwargs):
    """Return the demo results file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        **kwargs: Optional parameters for response threshold and model type.

    Returns:
        Path to the demo results file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0

    f = f"{data_name}_{action_set_name}"

    if kwargs.get("resp_thresh") is not None:
        resp_thresh = kwargs.get("resp_thresh")
        f += f"_epsilon_{resp_thresh}"
    if kwargs.get("model_type") is not None:
        model_type = kwargs.get("model_type")
        f += f"_{model_type}"

    f = f"{f}_demo.results"

    if kwargs.get("csv"):
        f += ".csv"

    return results_dir / f"{f}"


def get_stats_file(data_name, action_set_name, method_name, model_type, **kwargs):
    """Return the statistics file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        method_name: Method name.
        model_type: Model type identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the stats file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(method_name, str) and len(method_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    f = results_dir / f"{data_name}_{action_set_name}_{model_type}_{method_name}.stats"
    return f


def get_reachable_db_file(data_name, action_set_name, **kwargs):
    """Return the reachable set database path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the reachable set database.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0

    f = f"{data_name}_{action_set_name}"

    return results_dir / f"{f}.database"


def get_explainer_file(data_name, model_type, explainer_type, action_set_name=None, **kwargs):
    """Return the explainer object file path.

    Args:
        data_name: Dataset name.
        model_type: Model type identifier.
        explainer_type: Explainer type identifier.
        action_set_name: Optional action set name.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the explainer file.
    """
    if "actionAware" in explainer_type:
        header = f"{data_name}_{action_set_name}_{model_type}_{explainer_type}"
    else:
        header = f"{data_name}_{model_type}_{explainer_type}"
    f = results_dir / f"{header}.explainer"
    return f


def get_metrics_file(data_name, action_set_name, model_type=None, explainer_type=None, **kwargs):
    """Return the metrics file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        model_type: Optional model type identifier.
        explainer_type: Optional explainer type identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the metrics file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    header = f"{data_name}_{action_set_name}"
    if model_type is not None:
        header = f"{header}_{model_type}"
    if explainer_type is not None:
        header = f"{header}_{explainer_type}"
    f = results_dir / f"{header}.metrics"
    return f


def get_rij_file(data_name, action_set_name, **kwargs):
    """Return the R_ij data file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the R_ij data file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    f = results_dir / f"{data_name}_{action_set_name}_rij.df"
    return f


def get_plot_data_file(data_name, action_set_name, model_type, explainer_type, **kwargs):
    """Return the plot data file path.

    Args:
        data_name: Dataset name.
        action_set_name: Action set identifier.
        model_type: Model type identifier.
        explainer_type: Explainer type identifier.
        **kwargs: Unused; accepted for API compatibility.

    Returns:
        Path to the plot data file.
    """
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    assert isinstance(model_type, str) and len(model_type) > 0
    f = results_dir / f"{data_name}_{action_set_name}_{model_type}_{explainer_type}_plot_data.df"
    return f


def get_plot_file(data_name, action_set_name, model_type, explainer_type, plot_name, **kwargs):
    """Return file name of a plot (without extension)."""
    assert isinstance(data_name, str) and len(data_name) > 0
    assert isinstance(action_set_name, str) and len(action_set_name) > 0
    assert isinstance(model_type, str) and len(model_type) > 0
    assert isinstance(plot_name, str)
    f = (
        results_dir
        / f"{data_name}_{action_set_name}_{model_type}_{explainer_type}_plot_{plot_name}"
    )
    return f
