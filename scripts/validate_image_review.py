#!/usr/bin/env python3
"""Check that an image review's declared summary follows its core conclusions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


STATUSES = ("PASS", "UNVERIFIED", "REVISE")


def validate_record(record: dict) -> dict:
    review = record.get("visual_review") if isinstance(record, dict) else None
    if not isinstance(review, dict):
        raise ValueError("visual_review must be an object")
    groups = [name for name in ("core_checks", "object_checks") if name in review]
    if len(groups) != 1:
        raise ValueError("provide one core_checks list (or an existing object_checks list)")
    checks = review[groups[0]]
    if not isinstance(checks, list) or not checks:
        raise ValueError("core checks must be a non-empty list")

    counts = dict.fromkeys(STATUSES, 0)
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(f"core check {index + 1} must be an object")
        values = [check[name] for name in ("conclusion", "status") if name in check]
        if not values or any(value not in STATUSES for value in values):
            raise ValueError(f"core check {index + 1} needs PASS, REVISE or UNVERIFIED")
        if any(value != values[0] for value in values):
            raise ValueError(f"core check {index + 1} has conflicting conclusions")
        counts[values[0]] += 1

    expected = next(status for status in reversed(STATUSES) if counts[status])
    summaries = {name: review[name] for name in ("overall_status", "core_status") if name in review}
    if not summaries:
        raise ValueError(f"visual_review.overall_status is required; expected {expected}")
    for name, declared in summaries.items():
        if declared != expected:
            raise ValueError(f"{name} is {declared!r}; expected {expected} from core checks")
    return {"record_consistent": True, "overall_status": expected,
            "core_count": len(checks), "counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="Generation record containing visual_review")
    args = parser.parse_args()
    try:
        result = validate_record(json.loads(args.record.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        print(json.dumps({"record_consistent": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
