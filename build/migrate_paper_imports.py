"""Migrate imports in paper research directories from old names to new package names."""

import argparse
from pathlib import Path

# Replacements applied in order; earlier rules take priority over later ones.
REPLACEMENTS = [
    ("from reachml", "from responsiveness"),
    ("import reachml", "import responsiveness"),
    ("from src.ext", "from responsiveness.ext"),
    ("from src.paths", "from responsiveness.paths"),
    ("from src import", "from responsiveness.ext import"),
    ("from src.", "from responsiveness.ext."),
]


def migrate_line(line):
    """Apply the first matching replacement to a single line."""
    for old, new in REPLACEMENTS:
        if old in line:
            return line.replace(old, new, 1)
    return line


def migrate_file(path, *, dry_run):
    """Migrate imports in a single file. Return list of change records."""
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    changes = []
    new_lines = []
    for i, line in enumerate(lines, start=1):
        new_line = migrate_line(line)
        if new_line != line:
            changes.append({"file": str(path), "line": i, "old": line.rstrip("\n"), "new": new_line.rstrip("\n")})
        new_lines.append(new_line)
    if changes and not dry_run:
        path.write_text("".join(new_lines))
    return changes


def main():
    parser = argparse.ArgumentParser(description="Migrate old imports to new package names in .py files.")
    parser.add_argument("directory", type=Path, help="Root directory to scan for .py files.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without modifying files.")
    args = parser.parse_args()

    root = args.directory.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    all_changes = []
    for py_file in sorted(root.rglob("*.py")):
        all_changes.extend(migrate_file(py_file, dry_run=args.dry_run))

    if not all_changes:
        print("no changes needed")
        return

    mode = "would change" if args.dry_run else "changed"
    for c in all_changes:
        print(f"{c['file']}:{c['line']}")
        print(f"  - {c['old']}")
        print(f"  + {c['new']}")
        print()
    print(f"{len(all_changes)} line(s) {mode} across {len({c['file'] for c in all_changes})} file(s)")


if __name__ == "__main__":
    main()
