"""Build the pip package and verify correctness."""

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_DIR / "dist"


def clean_dist():
    """Remove all files in dist/ directory."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    print(f"cleaned {DIST_DIR}")


def run_build():
    """Run uv build and return the process result."""
    result = subprocess.run(
        ["uv", "build"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("uv build failed:")
        print(result.stderr)
        sys.exit(1)
    print("uv build succeeded")
    out = result
    return out


def verify_wheel(wheel_path: Path):
    """Assert that no ext/ files are included in the wheel."""
    ext_files = [name for name in zipfile.ZipFile(wheel_path).namelist() if "/ext/" in name]
    assert len(ext_files) == 0, f"wheel contains ext/ files: {ext_files}"
    print(f"verified: {wheel_path.name} contains no ext/ files")


def print_summary():
    """Print summary of built artifacts in dist/."""
    artifacts = sorted(p for p in DIST_DIR.iterdir() if p.suffix in (".whl", ".gz"))
    print(f"\nbuilt {len(artifacts)} artifact(s) in {DIST_DIR}:")
    for path in artifacts:
        size_kb = path.stat().st_size / 1024
        print(f"  {path.name} ({size_kb:.1f} KB)")


def upload(test_pypi: bool):
    """Upload dist/ artifacts via twine."""
    cmd = ["uvx", "twine", "upload", "dist/*"]
    if test_pypi:
        cmd += ["--repository-url", "https://test.pypi.org/legacy/"]
    result = subprocess.run(cmd, cwd=REPO_DIR)
    if result.returncode != 0:
        sys.exit(1)
    print("upload succeeded")


def main():
    """Build pip package and optionally publish."""
    parser = argparse.ArgumentParser(description="Build and optionally publish the pip package.")
    parser.add_argument("--publish", action="store_true", help="Upload to PyPI via twine after build.")
    parser.add_argument("--test-pypi", action="store_true", help="Upload to TestPyPI instead of PyPI.")
    args = parser.parse_args()

    clean_dist()
    run_build()

    wheels = list(DIST_DIR.glob("*.whl"))
    for whl in wheels:
        verify_wheel(whl)

    print_summary()

    if args.publish:
        upload(test_pypi=args.test_pypi)


if __name__ == "__main__":
    main()
