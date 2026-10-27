#!/usr/bin/env python3
"""Compile a natural-language Markdown direction into native image-tool arguments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from natural_direction import compile_file
# This import keeps existing callers and saved JSON directions executable.
from legacy_image_job import build_job


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", type=Path, help="direction.md; existing direction.json is accepted for replay")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.direction.suffix.lower() == ".json":
            job = build_job(json.loads(args.direction.read_text(encoding="utf-8")), args.direction.resolve().parent)
        else:
            job, _, _ = compile_file(args.direction)
        result = json.dumps(job, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(result)
        else:
            print(result, end="")
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
