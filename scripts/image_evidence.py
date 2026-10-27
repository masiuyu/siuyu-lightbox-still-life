#!/usr/bin/env python3
"""Bind saved imagegen arguments, native pixels and a Markdown review to a bundle."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from natural_direction import STATUS_NAMES, check_bundle, digest, validate_markdown_review


def file_record(role: str, path: Path) -> dict:
    path = path.resolve()
    data = path.read_bytes()
    return {"role": role, "path": str(path), "bytes": len(data), "sha256": digest(data)}


def open_raster(path: Path):
    try:
        from PIL import Image
    except ImportError as error:
        raise ValueError("image evidence needs a Python runtime with Pillow; compile/check/review do not") from error
    try:
        with Image.open(path) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("use a single native still image for this evidence record")
            image.load()
            info = {"path": str(path.resolve()), "width": image.width, "height": image.height,
                    "mode": image.mode, "format": image.format}
            return image.copy(), info
    except (OSError, SyntaxError) as error:
        raise ValueError(f"cannot decode image: {path}") from error


def same_pixels(first, second) -> bool:
    return (first.size == second.size and first.mode == second.mode
            and first.tobytes() == second.tobytes()
            and (first.mode != "P" or first.getpalette() == second.getpalette()))


def collect_evidence(bundle: Path, call: Path, image: Path, review: Path,
                     detail_index: Path | None = None, execution: Path | None = None) -> dict:
    bundle, call, image, review = (path.resolve() for path in (bundle, call, image, review))
    checked = check_bundle(bundle)
    job = json.loads((bundle / "image-job.json").read_text(encoding="utf-8-sig"))
    saved_call = json.loads(call.read_text(encoding="utf-8-sig"))
    if not isinstance(saved_call, dict):
        raise ValueError("the saved imagegen call must be a JSON object")
    arguments = saved_call.get("arguments", saved_call)
    if not isinstance(arguments, dict) or arguments.get("prompt") != job["prompt"]:
        raise ValueError("the saved call prompt differs from the compiled job")
    expected_references = job.get("referenced_image_paths", [])
    actual_references = arguments.get("referenced_image_paths")
    if actual_references is None:
        actual_references = []
    if actual_references != expected_references:
        raise ValueError("the saved call references differ from the compiled order")
    if arguments.get("num_last_images_to_include") not in (None, 0):
        raise ValueError("conversation-image references need their own mapping; this command binds local-file references")
    native, image_info = open_raster(image)
    review_info = validate_markdown_review(review.read_text(encoding="utf-8-sig"))
    records = []
    for name in ("compilation.json", "direction.md", "image-job.json", "actual-prompt.txt", "input-order.md"):
        records.append(file_record("compiled:" + name, bundle / name))
    for number, path in enumerate(expected_references, 1):
        records.append(file_record(f"reference:{number}", Path(path)))
    records.extend((file_record("tool_call", call), file_record("native_image", image), file_record("review", review)))
    execution_copy_matches = None
    native_tool_copy_matches = None
    if execution is not None:
        execution = execution.resolve()
        records.append(file_record("execution_attachment", execution))
        if execution.suffix.lower() == '.json':
            execution_data = json.loads(execution.read_text(encoding='utf-8-sig'))
            if isinstance(execution_data, dict) and 'workspace_copy' in execution_data:
                copy = execution_data['workspace_copy']
                if not isinstance(copy, dict) or not isinstance(copy.get('path'), str):
                    raise ValueError('the execution workspace_copy needs its actual image path and fingerprint')
                copy_path = (execution.parent / copy['path']).resolve()
                image_file = file_record('native_image', image)
                if copy_path != image or copy.get('sha256') != image_file['sha256']:
                    raise ValueError('the execution image path or fingerprint differs from the selected native image')
                if copy.get('bytes', image_file['bytes']) != image_file['bytes']:
                    raise ValueError('the execution image size differs from the native file')
                if copy.get('dimensions', [native.width, native.height]) != [native.width, native.height]:
                    raise ValueError('the execution dimensions differ from the native image')
                if execution_data.get('review_record') is not None and (execution.parent / execution_data['review_record']).resolve() != review:
                    raise ValueError('the execution review path differs from the selected review')
                if saved_call.get('started_at') and execution_data.get('started_at') and saved_call['started_at'] != execution_data['started_at']:
                    raise ValueError('the saved call and execution identify different start times')
                declared_status = execution_data.get('visual_review')
                if isinstance(declared_status, str) and declared_status in STATUS_NAMES and STATUS_NAMES[declared_status] != review_info['overall_status']:
                    raise ValueError('the execution visual summary differs from the selected review')
                execution_copy_matches = True
                original = execution_data.get('native_tool_path')
                if isinstance(original, str):
                    original = (execution.parent / original).resolve()
                    if original.is_file():
                        original_file = file_record('native_tool_output', original)
                        if original_file['sha256'] != image_file['sha256']:
                            raise ValueError('the native tool output differs from the selected image copy')
                        records.append(original_file)
                        native_tool_copy_matches = True
    details = {"index_path": None, "crops": [], "other_source_entries": 0}
    if detail_index is not None:
        detail_index = detail_index.resolve()
        entries = json.loads(detail_index.read_text(encoding="utf-8-sig"))
        if not isinstance(entries, list):
            raise ValueError("the detail index must be a list of source, path and box_xyxy_half_open records")
        records.append(file_record("detail_index", detail_index))
        details["index_path"] = str(detail_index)
        seen_crops = set()
        for item in entries:
            if not isinstance(item, dict) or not isinstance(item.get("source"), str):
                raise ValueError("each detail entry needs a source path")
            source = Path(item["source"])
            source = (detail_index.parent / source).resolve() if not source.is_absolute() else source.resolve()
            if source != image:
                details["other_source_entries"] += 1
                continue
            box = item.get("box_xyxy_half_open")
            if (not isinstance(box, list) or len(box) != 4
                    or any(type(value) is not int for value in box)
                    or not (0 <= box[0] < box[2] <= native.width and 0 <= box[1] < box[3] <= native.height)):
                raise ValueError("native detail coordinates must be integer half-open bounds inside the source image")
            if not isinstance(item.get("path"), str):
                raise ValueError("each native detail needs its actual file path")
            path = Path(item["path"])
            path = (detail_index.parent / path).resolve() if not path.is_absolute() else path.resolve()
            if path in seen_crops:
                raise ValueError("list each detail image once for the current native source")
            seen_crops.add(path)
            crop, crop_info = open_raster(path)
            if not same_pixels(native.crop(tuple(box)), crop):
                raise ValueError(f"detail pixels differ from the source crop: {path}")
            record = file_record("native_crop", path)
            if item.get("sha256") is not None and item["sha256"] != record["sha256"]:
                raise ValueError(f"detail fingerprint differs from the index: {path}")
            if item.get("size") is not None and item["size"] != [crop.width, crop.height]:
                raise ValueError(f"detail dimensions differ from the index: {path}")
            records.append(record)
            details["crops"].append({"path": str(path), "box_xyxy_half_open": box,
                                     "width": crop_info["width"], "height": crop_info["height"]})
        if not details["crops"]:
            raise ValueError("the detail index has no crops bound to this native image")
    return {
        "schema": "lightbox-image-evidence-v1", "bundle": str(bundle), "files": records,
        "call": {"path": str(call), "extra_argument_names": sorted(set(arguments) - set(job))},
        "image": image_info, "review": {"path": str(review), **review_info},
        "details": details, "execution_attachment": str(execution) if execution is not None else None,
        "checks": {"bundle_consistent": checked["bundle_consistent"], "tool_arguments_match_compiled_job": True,
                   "native_raster_readable": True, "native_crops_match": True if details["crops"] else None,
                   "execution_copy_matches": execution_copy_matches, "native_tool_copy_matches": native_tool_copy_matches},
        "generation_authenticity_checked": False, "visual_quality_checked": False,
        "user_acceptance_checked": False,
    }


def write_evidence(bundle: Path, call: Path, image: Path, review: Path, output: Path,
                   detail_index: Path | None = None, execution: Path | None = None) -> dict:
    result = collect_evidence(bundle, call, image, review, detail_index, execution)
    result["recorded_at"] = datetime.now(timezone.utc).isoformat()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return {"evidence_record": str(output.resolve()), "files_bound": len(result["files"]),
            "native_crops_checked": len(result["details"]["crops"]),
            "recorded_visual_status": result["review"]["overall_status"],
            "generation_authenticity_checked": False, "visual_quality_checked": False,
            "user_acceptance_checked": False}


def check_evidence(path: Path) -> dict:
    saved = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(saved, dict) or saved.get("schema") != "lightbox-image-evidence-v1":
        raise ValueError("this is not an image evidence record")
    if not isinstance(saved.get("files"), list) or not saved["files"]:
        raise ValueError("the image evidence inventory is incomplete")
    for item in saved["files"]:
        if file_record(item["role"], Path(item["path"])) != item:
            raise ValueError(f"bound evidence file changed: {item['path']}")
    current = collect_evidence(Path(saved["bundle"]), Path(saved["call"]["path"]),
                               Path(saved["image"]["path"]), Path(saved["review"]["path"]),
                               Path(saved["details"]["index_path"]) if saved["details"]["index_path"] else None,
                               Path(saved["execution_attachment"]) if saved["execution_attachment"] else None)
    if {key: value for key, value in saved.items() if key != "recorded_at"} != current:
        raise ValueError("the evidence inventory or recorded interpretation differs from the current files")
    return {"evidence_consistent": True, "files_bound": len(current["files"]),
            "native_crops_checked": len(current["details"]["crops"]),
            "recorded_visual_status": current["review"]["overall_status"],
            "generation_authenticity_checked": False, "visual_quality_checked": False,
            "user_acceptance_checked": False}
