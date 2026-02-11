"""Build a clean public repo snapshot from whitelisted files and force-push it."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# directories to include (all contents recursively)
WHITELIST_DIRS = [
    "responsiveness/",
    "tests/",
    "scripts/demos/",
    "docs/",
    ".github/workflows/",
]

# individual files to include
WHITELIST_FILES = [
    "data/givemecredit_cts.csv",
    "data/credit.csv",
    "pyproject.toml",
    "README.md",
    "LICENSE",
]

# patterns to exclude even within whitelisted directories
EXCLUDE_PATTERNS = {"__pycache__", ".pyc", ".DS_Store"}


def get_repo_root():
    """Return the repo root (parent of this script's directory)."""
    return Path(__file__).resolve().parent.parent


def get_version(repo_root):
    """Read the package version via hatchling."""
    result = subprocess.run(
        [sys.executable, "-m", "hatchling", "version"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    out = result.stdout.strip() if result.returncode == 0 else None
    return out


def _is_excluded(path):
    """Return True if any path component matches an exclude pattern."""
    return any(part in EXCLUDE_PATTERNS or part.endswith(".pyc") for part in path.parts)


def collect_files(repo_root):
    """Walk repo_root and return sorted list of relative paths matching the whitelist."""
    matched = []
    for dirpath in WHITELIST_DIRS:
        abs_dir = repo_root / dirpath
        if not abs_dir.is_dir():
            continue
        for root, _dirs, files in os.walk(abs_dir):
            for f in files:
                rel = Path(root, f).relative_to(repo_root)
                if not _is_excluded(rel):
                    matched.append(rel)

    for filepath in WHITELIST_FILES:
        abs_file = repo_root / filepath
        if abs_file.is_file():
            matched.append(Path(filepath))

    out = sorted(set(matched))
    return out


def copy_files(file_list, repo_root, dest):
    """Copy files from repo_root to dest, preserving directory structure."""
    for rel_path in file_list:
        src = repo_root / rel_path
        dst = dest / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def git_init_and_push(dest, remote_url, version):
    """Initialize a git repo in dest, commit all files, and force-push."""
    tag = f"v{version}" if version else None
    commit_msg = f"public release {tag}" if tag else "public release"

    commands = [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", commit_msg],
    ]
    if tag:
        commands.append(["git", "tag", tag])
    commands.append(["git", "remote", "add", "origin", remote_url])
    commands.append(["git", "push", "--force", "origin", "main"])
    if tag:
        commands.append(["git", "push", "--force", "origin", tag])

    for cmd in commands:
        subprocess.run(cmd, cwd=dest, check=True)


def main():
    """Entry point for building and pushing a public repo snapshot."""
    parser = argparse.ArgumentParser(description="Create a clean public repo snapshot.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the file list without creating or pushing anything.",
    )
    parser.add_argument(
        "--remote-url",
        type=str,
        default=None,
        help="Remote URL for the public repo (required unless --dry-run).",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.remote_url:
        parser.error("--remote-url is required unless --dry-run is set")

    repo_root = get_repo_root()
    version = get_version(repo_root)
    file_list = collect_files(repo_root)

    print(f"repo root : {repo_root}")
    print(f"version   : {version or '(unknown)'}")
    print(f"files     : {len(file_list)}")
    print()

    for f in file_list:
        print(f"  {f}")

    if args.dry_run:
        print("\n[dry-run] no files copied, nothing pushed.")
        return

    tmp_dir = Path(tempfile.mkdtemp(prefix="public_repo_"))
    print(f"\ntemp dir  : {tmp_dir}")

    copy_files(file_list, repo_root, tmp_dir)
    print(f"copied {len(file_list)} files")

    git_init_and_push(tmp_dir, args.remote_url, version)
    print(f"\npushed to {args.remote_url}")

    shutil.rmtree(tmp_dir)
    print("temp dir cleaned up")


if __name__ == "__main__":
    main()
