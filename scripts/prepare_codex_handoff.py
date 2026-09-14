#!/usr/bin/env python3
"""Copy the implementation plan into a repository and generate a task-scoped Codex prompt."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PLAN_NAME = "2026-08-04-siuyu-lightbox-still-life-mvp.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--task", type=int, default=1)
    parser.add_argument("--copy-plan", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.task < 1 or args.task > 20:
        raise SystemExit("--task must be between 1 and 20")

    repo = args.repo.expanduser().resolve()
    repo.mkdir(parents=True, exist_ok=True)
    source_plan = Path(__file__).resolve().parents[1] / "references" / "implementation-plan.md"
    plan_path = source_plan
    if args.copy_plan:
        plan_path = repo / "docs" / "superpowers" / "plans" / PLAN_NAME
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_plan, plan_path)

    prompt = f"""Use $siuyu-lightbox-still-life in Implementation mode.
Repository: {repo}
Read AGENTS.md if present and read the implementation plan in full: {plan_path}
Execute Task {args.task} only.
Follow its test-first steps in order. Confirm the intended failing test before implementation.
Do not implement later tasks or introduce excluded dependencies.
Run the task-specific verification and pnpm typecheck before committing.
Commit with the exact message from the plan.
Report changed files, verification output summary, commit hash, and unresolved risks.
"""
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(prompt, encoding="utf-8")
        print(output)
    else:
        print(prompt, end="")


if __name__ == "__main__":
    main()
