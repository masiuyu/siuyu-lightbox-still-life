#!/usr/bin/env python3
"""Validate the portable siuyu-lightbox-still-life skill without third-party packages."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REQUIRED = {
    "SKILL.md",
    "README.md",
    "ASSET_SOURCES.md",
    "agents/openai.yaml",
    "references/image-art-direction.md",
    "references/prompt-execution.md",
    "references/photography.md",
    "references/material-color.md",
    "references/object-relations.md",
    "scripts/build_image_job.py",
    "scripts/validate_image_review.py",
    "assets/image-direction.example.json",
    "assets/photography-profiles.json",
    "references/offline-workflow.md",
    "references/workflow-contract.md",
    "references/source-analysis.md",
    "references/asset-manifest.md",
    "references/layout-routing.md",
    "references/composition-recipes.md",
    "references/scene-schema.md",
    "references/material-presets.md",
    "references/acceptance-checklist.md",
    "references/codex-execution.md",
    "references/visual-direction.md",
    "references/implementation-plan.md",
    "scripts/install_skill.py",
    "scripts/verify_project.py",
    "scripts/prepare_codex_handoff.py",
    "scripts/ingest.sh",
    "scripts/preview.sh",
    "scripts/review.sh",
    "scripts/final.sh",
    "scripts/compile_generation_description.py",
    "assets/project-brief.example.json",
    "assets/asset-hints.example.json",
    "assets/asset-manifest.example.json",
    "assets/workflow.example.json",
    "assets/visual-direction.example.json",
    "assets/concept-asset-brief.example.json",
    "assets/preview-quality-review.example.json",
    "evals/evals.json",
}


def fail(message: str) -> None:
    print(f"INVALID: {message}")
    raise SystemExit(1)


def parse_simple_yaml_mapping(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            fail(f"unsupported YAML line: {raw_line}")
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = json.loads(value)
        result[key.strip()] = value
    return result


def parse_openai_interface(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "interface:":
        fail("agents/openai.yaml must start with interface:")
    return parse_simple_yaml_mapping("\n".join(lines[1:]))


def main() -> None:
    skill = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    if not skill.is_dir():
        fail(f"skill directory not found: {skill}")

    missing = sorted(rel for rel in REQUIRED if not (skill / rel).is_file())
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    content = (skill / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        fail("invalid SKILL.md frontmatter")
    frontmatter = parse_simple_yaml_mapping(match.group(1))
    if set(frontmatter) != {"name", "description"}:
        fail("frontmatter must contain only name and description")
    name = frontmatter["name"]
    description = frontmatter["description"]
    if name != "siuyu-lightbox-still-life" or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        fail("invalid skill name")
    if not description.startswith("Use when") or len(description) > 1024:
        fail("description must start with 'Use when' and be <=1024 characters")
    if len(content.splitlines()) > 500:
        fail("SKILL.md exceeds 500 lines")
    if "TODO" in content or "TBD" in content:
        fail("placeholder marker found")

    pending = [skill / "SKILL.md", skill / "README.md", skill / "ASSET_SOURCES.md"]
    visited: set[Path] = set()
    while pending:
        document = pending.pop()
        if document in visited:
            continue
        visited.add(document)
        markdown = document.read_text(encoding="utf-8")
        markdown = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", markdown):
            if re.match(r"^[a-z][a-z0-9+.-]*://", link):
                continue
            relative = link.split("#", 1)[0]
            if not relative:
                continue
            target = (document.parent / relative).resolve()
            if skill not in target.parents and target != skill:
                fail(f"link escapes skill directory: {document.name}: {link}")
            if not target.exists():
                fail(f"broken link: {document.name}: {link}")
            if target.suffix == ".md":
                pending.append(target)

    interface = parse_openai_interface((skill / "agents/openai.yaml").read_text(encoding="utf-8"))
    if not (25 <= len(interface.get("short_description", "")) <= 64):
        fail("openai.yaml short_description must be 25-64 characters")
    if not re.search(r"\$" + re.escape(name) + r"(?![a-z0-9-])", interface.get("default_prompt", "")):
        fail("openai.yaml default_prompt must mention the skill")
    for key in ("icon_small", "icon_large"):
        value = interface.get(key)
        if value and not (skill / value).is_file():
            fail(f"openai.yaml {key} asset is missing")
    if "visual direction" not in interface.get("default_prompt", ""):
        fail("openai.yaml default_prompt must request visual direction")

    for example in [
        "project-brief.example.json",
        "asset-hints.example.json",
        "asset-manifest.example.json",
        "workflow.example.json",
        "visual-direction.example.json",
        "concept-asset-brief.example.json",
        "preview-quality-review.example.json",
    ]:
        json.loads((skill / "assets" / example).read_text(encoding="utf-8"))

    image_job = subprocess.run(
        [sys.executable, "-B", str(skill / "scripts/build_image_job.py"),
         str(skill / "assets/image-direction.example.json")],
        capture_output=True, text=True, check=False,
    )
    if image_job.returncode != 0:
        fail(f"image direction example does not compile: {image_job.stderr.strip()}")
    compiled_job = json.loads(image_job.stdout)
    if not isinstance(compiled_job.get("prompt"), str) or not compiled_job["prompt"].strip():
        fail("image direction example must emit a prompt")

    compiler = skill / "scripts" / "compile_generation_description.py"
    direction_example = skill / "assets" / "visual-direction.example.json"
    manifest_example = skill / "assets" / "asset-manifest.example.json"
    workflow_example = skill / "assets" / "workflow.example.json"
    compiler_command = [
        sys.executable,
        str(compiler),
        str(direction_example),
        "--manifest",
        str(manifest_example),
        "--workflow",
        str(workflow_example),
    ]
    first = subprocess.run(
        compiler_command,
        check=False,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        compiler_command,
        check=False,
        capture_output=True,
        text=True,
    )
    if first.returncode != 0:
        fail(f"visual-direction example does not compile: {first.stderr.strip()}")
    if first.stdout != second.stdout:
        fail("visual-direction compiler output is not deterministic")
    for marker in [
        "SceneSpec 规划控制文档",
        "【交付载体】",
        "【素材整合】",
        "【版式路由】",
        "【素材表现】",
        "【统一柔光箱环境】",
        "【参考影响边界】",
        "【优化动作（按优先级）】",
        "【质量门】",
    ]:
        if marker not in first.stdout:
            fail(f"compiled visual direction is missing marker: {marker}")

    eval_payload = json.loads((skill / "evals" / "evals.json").read_text(encoding="utf-8"))
    if eval_payload.get("skill_name") != name:
        fail("evals/evals.json skill_name must match the skill")
    evals = eval_payload.get("evals")
    if not isinstance(evals, list) or not evals:
        fail("evals/evals.json must contain evaluation cases")
    eval_ids: set[str] = set()
    for case in evals:
        if not isinstance(case, dict):
            fail("every eval case must be an object")
        if set(case) != {"id", "prompt", "expected_output", "files"}:
            fail("every eval case must contain id, prompt, expected_output, and files")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id or case_id in eval_ids:
            fail("eval IDs must be non-empty and unique")
        eval_ids.add(case_id)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            fail(f"eval {case_id} has an empty prompt")
        if not isinstance(case["expected_output"], str) or not case["expected_output"].strip():
            fail(f"eval {case_id} has an empty expected_output")
        if not isinstance(case["files"], list):
            fail(f"eval {case_id} files must be a list")
    for script in (skill / "scripts").iterdir():
        if script.suffix in {".py", ".sh"} and not os.access(script, os.R_OK):
            fail(f"script is not readable: {script.name}")

    print(f"VALID: {skill}")


if __name__ == "__main__":
    main()
