#!/usr/bin/env python3
"""Install this skill by copying real files into a Codex-compatible skill root."""
from __future__ import annotations

import argparse
import datetime
import os
import shutil
from pathlib import Path

SKILL_NAME = "siuyu-lightbox-still-life"


def default_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


def copy_skill(source: Path, target_root: Path, backup_existing: bool) -> Path:
    source = source.resolve()
    target_root = target_root.expanduser().resolve()
    destination = target_root / SKILL_NAME
    if source in destination.parents:
        raise ValueError("installation target must be outside the source skill directory")
    target_root.mkdir(parents=True, exist_ok=True)
    if destination == source:
        print(f"Already installed at {destination}")
        return destination
    if destination.exists():
        if not backup_existing:
            raise FileExistsError(f"destination exists: {destination}; use --backup-existing to preserve it before installing")
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_root = target_root.parent / "skill-backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        backup = backup_root / f"{SKILL_NAME}-{stamp}"
        if backup.exists():
            raise FileExistsError(f"backup destination already exists: {backup}")
        shutil.move(str(destination), str(backup))
        print(f"Previous version preserved at {backup}")
    shutil.copytree(source, destination, symlinks=False,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"))
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", type=Path, default=default_root())
    parser.add_argument("--backup-existing", action="store_true", help="preserve an existing version in a sibling skill-backups directory before installing")
    parser.add_argument("--also-agents", action="store_true", help="also copy to ~/.agents/skills")
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1]
    installed = [copy_skill(source, args.target_root, args.backup_existing)]
    if args.also_agents:
        agents_root = Path.home() / ".agents" / "skills"
        if agents_root.resolve() != args.target_root.expanduser().resolve():
            installed.append(copy_skill(source, agents_root, args.backup_existing))

    for path in installed:
        print(f"Installed {SKILL_NAME} at {path}")
    print("Restart Codex or force skill reload before invoking the skill.")


if __name__ == "__main__":
    main()
