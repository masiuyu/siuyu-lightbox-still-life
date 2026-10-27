#!/usr/bin/env python3
"""Transport an authored Markdown image brief, without interpreting its design."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


IMAGE_HEADINGS = {"参考图片", "Reference images"}
PROMPT_HEADINGS = {"成像说明", "Image instructions"}
CORE_HEADINGS = {"核心观察", "Core observations"}
IMAGE_LINK = re.compile(r"^\s*!\[([^\]\n]+)\]\((<[^>\n]+>|[^\s()]+)\)\s*$")
IMAGE_NUMBER = re.compile(r"(?<!\w)Image\s+(\d+)(?!\d)", re.IGNORECASE)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".heif", ".tif", ".tiff", ".bmp"}
STATUS_NAMES = {"通过": "PASS", "需要修正": "REVISE", "待确认": "UNVERIFIED",
                "PASS": "PASS", "REVISE": "REVISE", "UNVERIFIED": "UNVERIFIED"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sections(text: str) -> dict[str, list[str]]:
    """Recognize top-level sections; preserve prose and subordinate headings."""
    result: dict[str, list[str]] = {}
    current = None
    fenced = False
    fence_char = ""
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            if not fenced:
                fenced, fence_char = True, stripped[0]
            elif stripped[0] == fence_char:
                fenced = False
            if current is not None:
                result[current].append(line)
            continue
        heading = re.match(r"^##\s+(.+?)\s*#*\s*$", line) if not fenced else None
        if heading:
            current = heading.group(1).strip()
            if current in result:
                raise ValueError(f"duplicate section: {current}")
            result[current] = []
        elif not fenced and re.match(r"^#\s+", line):
            current = None
        elif current is not None:
            result[current].append(line)
    return result


def one_section(parts: dict, choices: set[str], label: str) -> str:
    matches = [key for key in parts if key in choices]
    if len(matches) != 1:
        raise ValueError(f"provide exactly one {label} section")
    return "".join(parts[matches[0]])


def compile_markdown(text: str, base: Path) -> tuple[dict, dict, str]:
    parts = sections(text)
    images = one_section(parts, IMAGE_HEADINGS, "参考图片 / Reference images")
    if any(line.lstrip().startswith(("```", "~~~")) for line in images.splitlines()):
        raise ValueError("write the actual image links directly in the reference-images section, outside code fences")
    prompt = one_section(parts, PROMPT_HEADINGS, "成像说明 / Image instructions").strip()
    if not prompt:
        raise ValueError("the image instructions are empty")
    if "![" in prompt:
        raise ValueError("put image links in the reference-images section")
    inputs, paths, replacements = [], [], {}
    for line in images.splitlines():
        match = IMAGE_LINK.fullmatch(line)
        if not match:
            if "![" in line:
                raise ValueError("each reference needs a complete standalone Markdown image link; use <...> around paths with spaces")
            continue
        label, raw = match.groups()
        raw = raw[1:-1] if raw.startswith("<") else raw
        if re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.IGNORECASE):
            raise ValueError("reference images must be local file paths")
        path = Path(raw).expanduser()
        path = (base / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_file():
            raise ValueError(f"reference image is missing: {path}")
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"unsupported reference file extension: {path}")
        if str(path) in paths:
            raise ValueError("list each physical reference file once and describe its combined uses in the prose")
        if any(char in str(path) for char in "<>\n\r"):
            raise ValueError("the reference path cannot be represented by this Markdown interface")
        paths.append(str(path))
        data = path.read_bytes()
        inputs.append({"image_number": len(paths), "label": label,
                       "path": str(path), "sha256": digest(data), "bytes": len(data)})
        replacements[line] = f"![{label}](<{path}>)"
    mentioned = {int(match.group(1)) for match in IMAGE_NUMBER.finditer(prompt)}
    expected = set(range(1, len(paths) + 1))
    if mentioned != expected:
        raise ValueError(f"Image N bindings differ from the reference order: expected {sorted(expected)}, found {sorted(mentioned)}")
    # Image numbering is the only binding syntax. The prose remains the author's.
    job = {"prompt": prompt}
    if paths:
        job["referenced_image_paths"] = paths
    normalized = "".join(replacements.get(line.rstrip("\r\n"), line.rstrip("\r\n")) +
                         ("\n" if line.endswith(("\n", "\r")) else "")
                         for line in text.splitlines(keepends=True))
    return job, {"interface": "natural-language-v1", "inputs": inputs,
                 "prompt_sha256": digest(prompt.encode("utf-8")),
                 "semantic_review": "Operator checks the actual sources, scope, materials, composition and authorization."}, normalized


def compile_file(path: Path) -> tuple[dict, dict, str]:
    path = path.resolve()
    data = path.read_bytes()
    text = data.decode("utf-8-sig")
    job, evidence, normalized = compile_markdown(text, path.parent)
    evidence.update({"original_direction": str(path), "original_direction_sha256": digest(data)})
    return job, evidence, normalized


def write_bundle(path: Path, output: Path) -> dict:
    job, evidence, normalized = compile_file(path)
    payloads = {
        "direction.md": normalized.encode("utf-8"),
        "image-job.json": (json.dumps(job, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        "actual-prompt.txt": job["prompt"].encode("utf-8"),
    }
    order = "# 实际图片顺序\n\n"
    if not evidence["inputs"]:
        order += "本次采用纯文字方向。\n"
    for item in evidence["inputs"]:
        order += f"- Image {item['image_number']}：{item['label']}；[实际文件](<{item['path']}>). SHA256 `{item['sha256']}`。\n"
    payloads["input-order.md"] = order.encode("utf-8")
    evidence.update({"state": "COMPILED", "image_generation": "NOT_RUN",
                     "visual_review": "UNVERIFIED", "user_acceptance": "PENDING_USER_REVIEW",
                     "files": {name: digest(data) for name, data in payloads.items()}})
    payloads["compilation.json"] = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        with (output / name).open("xb") as handle:
            handle.write(data)
    return {"state": "COMPILED", "workspace": str(output), "reference_count": len(evidence["inputs"]),
            "prompt_sha256": evidence["prompt_sha256"], "image_generation": "NOT_RUN"}


def check_bundle(output: Path) -> dict:
    output = output.resolve()
    evidence = json.loads((output / "compilation.json").read_text(encoding="utf-8"))
    if evidence.get("interface") != "natural-language-v1":
        raise ValueError("this is not a natural-language bundle")
    required = {"direction.md", "image-job.json", "actual-prompt.txt", "input-order.md"}
    if set(evidence.get("files", {})) != required:
        raise ValueError("the compiled-file inventory is incomplete")
    for name, expected in evidence["files"].items():
        if digest((output / name).read_bytes()) != expected:
            raise ValueError(f"compiled file changed: {name}")
    job, current, _ = compile_file(output / "direction.md")
    saved = json.loads((output / "image-job.json").read_text(encoding="utf-8"))
    if job != saved or current["inputs"] != evidence.get("inputs"):
        raise ValueError("the direction, reference bytes or actual job differ from the compilation evidence")
    if (output / "actual-prompt.txt").read_bytes() != job["prompt"].encode("utf-8"):
        raise ValueError("the saved prompt differs from the actual job")
    if current["prompt_sha256"] != evidence.get("prompt_sha256"):
        raise ValueError("the prompt fingerprint differs from the compilation evidence")
    return {"bundle_consistent": True, "reference_count": len(current["inputs"]),
            "image_generation_checked": False, "visual_quality_checked": False}


def table_cells(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [cell.strip().replace("\\|", "|") for cell in cells]


def validate_markdown_review(text: str) -> dict:
    core = one_section(sections(text), CORE_HEADINGS, "核心观察 / Core observations")
    rows = [line for line in core.splitlines() if line.strip().startswith("|")]
    if len(rows) < 3:
        raise ValueError("provide a core-observation table with position, observation, requirement and conclusion")
    separator = table_cells(rows[1])
    if len(table_cells(rows[0])) != 4 or len(separator) != 4 or not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in separator):
        raise ValueError("the core-observation table needs four columns and a Markdown separator")
    counts = dict.fromkeys(("PASS", "REVISE", "UNVERIFIED"), 0)
    for row in rows[2:]:
        cells = table_cells(row)
        if len(cells) != 4 or any(not cell for cell in cells):
            raise ValueError("every core observation needs position, observed result, requirement and conclusion")
        status = STATUS_NAMES.get(cells[3])
        if status is None:
            raise ValueError(f"unknown core conclusion: {cells[3]}")
        counts[status] += 1
    overall = "REVISE" if counts["REVISE"] else "UNVERIFIED" if counts["UNVERIFIED"] else "PASS"
    declared = re.findall(r"^(?:总体|Overall)\s*[:：]\s*(\S+)\s*$", text, re.MULTILINE)
    if len(declared) > 1 or declared and STATUS_NAMES.get(declared[0]) != overall:
        raise ValueError(f"the declared overall conclusion must agree with the core observations: {overall}")
    return {"record_consistent": True, "overall_status": overall,
            "core_count": sum(counts.values()), "counts": counts,
            "visual_quality_checked": False, "user_acceptance_checked": False}
