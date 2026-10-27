#!/usr/bin/env python3
"""Compile natural-language image directions and check saved execution evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from natural_direction import check_bundle, validate_markdown_review, write_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compile_command = commands.add_parser("compile", help="Turn direction.md into a new versioned job bundle; does not generate an image")
    compile_command.add_argument("direction", type=Path)
    compile_command.add_argument("--output-dir", required=True, type=Path)
    check_command = commands.add_parser("check", help="Compare the brief, prompt, ordered images and fingerprints")
    check_command.add_argument("workspace", type=Path)
    review_command = commands.add_parser("review", help="Summarize the core observations in review.md; does not inspect image pixels")
    review_command.add_argument("record", type=Path)
    framing_command = commands.add_parser("framing", help="Estimate coplanar layout margins and detail pixels from a declared plan; does not inspect or generate images")
    framing_command.add_argument("plan", type=Path)
    framing_command.add_argument("--output", type=Path)
    evidence_command = commands.add_parser("evidence", help="Bind a compiled job, saved imagegen arguments, native still and review to a new evidence record")
    evidence_command.add_argument("workspace", type=Path)
    evidence_command.add_argument("--call", required=True, type=Path)
    evidence_command.add_argument("--image", required=True, type=Path)
    evidence_command.add_argument("--review", required=True, type=Path)
    evidence_command.add_argument("--output", required=True, type=Path)
    evidence_command.add_argument("--detail-index", type=Path)
    evidence_command.add_argument("--execution", type=Path)
    evidence_check = commands.add_parser("check-evidence", help="Recheck the files and native crops bound to an existing evidence record")
    evidence_check.add_argument("record", type=Path)
    migrate_command = commands.add_parser("migrate", help="Transport an existing JSON direction into Markdown for subsequent operator review")
    migrate_command.add_argument("direction", type=Path)
    migrate_command.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "compile":
            result = write_bundle(args.direction, args.output_dir)
        elif args.command == "check":
            result = check_bundle(args.workspace)
        elif args.command == "review":
            result = validate_markdown_review(args.record.read_text(encoding="utf-8-sig"))
        elif args.command == "framing":
            from framing_plan import framing_report
            result = framing_report(args.plan, args.output)
        elif args.command == "evidence":
            from image_evidence import write_evidence
            result = write_evidence(args.workspace, args.call, args.image, args.review,
                                    args.output, args.detail_index, args.execution)
        elif args.command == "check-evidence":
            from image_evidence import check_evidence
            result = check_evidence(args.record)
        else:
            from legacy_image_job import build_job
            original = args.direction.resolve()
            plan = json.loads(original.read_text(encoding="utf-8"))
            job = build_job(plan, original.parent)
            images = "\n".join(f"![{item['id']} — {item['role']}](<{path}>)"
                               for item, path in zip(plan.get("inputs", []), job.get("referenced_image_paths", [])))
            markdown = "# 既有方向的自然语言副本\n\n## 参考图片\n\n" + (images or "本次采用纯文字方向。")
            markdown += "\n\n## 成像说明\n\n" + job["prompt"]
            markdown += f"\n\n## 工作记录\n\n[原始方向](<{original}>)。正文沿用该方向实际编译内容；重新使用前对照当前请求与来源复核。\n"
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(markdown)
            result = {"state": "MIGRATED", "output": str(args.output.resolve()),
                      "image_generation": "NOT_RUN", "semantic_review": "PENDING_OPERATOR_REVIEW"}
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
