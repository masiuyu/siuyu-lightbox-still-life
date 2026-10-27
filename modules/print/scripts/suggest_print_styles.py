#!/usr/bin/env python3
"""Return a short, process-aware menu of compatible print style pairs."""

from __future__ import annotations

import argparse
import json

from style_profiles import load_catalog, style_recommendations


def main() -> int:
    catalog = load_catalog()
    goals = sorted(catalog["recommendation_sets"])
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", choices=goals, default="generic_print")
    parser.add_argument("--json", action="store_true", help="emit machine-readable recommendations")
    args = parser.parse_args()
    options = style_recommendations(args.goal)
    if args.json:
        print(json.dumps({"goal": args.goal, "recommendations": options}, ensure_ascii=False, indent=2))
        return 0
    print(f"PRINT STYLE OPTIONS — {args.goal}")
    print("Option 1 is the recommended starting point. Process and art direction are independent choices.")
    for index, option in enumerate(options, 1):
        print(f"\n{index}. {option['label']}")
        print(f"   process: {option['process']}")
        print(f"   art direction: {option['art']}")
        print(f"   reason: {option['reason']}")
        print(f"   tradeoff: {option['tradeoff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
