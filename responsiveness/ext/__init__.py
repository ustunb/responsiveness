"""Research extensions for responsiveness (not included in pip package).

These modules require additional dependencies. Install them with:
    uv sync --group ext
"""

try:
    from . import cv, data, debug, fileutils, metrics, training
except ImportError as e:
    raise ImportError(
        f"responsiveness.ext requires additional dependencies: {e}\n"
        "Install them with: uv sync --group ext"
    ) from e
