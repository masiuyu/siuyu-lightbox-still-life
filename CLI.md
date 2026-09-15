<a id="命令行使用说明"></a>

# Command-line guide

[简体中文](CLI.zh-CN.md) | [English](CLI.md)

For users running Codex or this repository's scripts from a terminal. The shell examples target macOS, Linux, or Windows WSL. Replace example paths with your actual paths.

[Codex installation](README.md#codex-installation) · [Create images in Codex](README.md#codex-usage) · [ChatGPT web](CHATGPT.md)

<a id="先确认命令属于哪个工具"></a>

## Choose the right tool

| Command | Software | Where it runs and what it does |
|---|---|---|
| `codex` | OpenAI Codex CLI | Starts a Codex conversation from the system terminal to read skills, work with assets, and perform tasks |
| `/skills`, `$siuyu-lightbox-still-life` | Codex interactive interface | Lists or invokes a skill from the Codex input box |
| `npx skills add ...` | Third-party skills installer | Downloads and installs a skill from the system terminal; arguments select Codex |
| `python3 scripts/...` | This repository's Python scripts | Installs the skill, compiles a direction, or checks records locally; see the script table below |
| `pnpm ... --filter @lightbox/cli ...` | Companion local renderer CLI | In a separately prepared renderer project, processes assets, creates previews, and exports images |

<a id="codex-cli"></a>

## Codex CLI

Install and sign in to the client using the [official Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli), then follow this project's [Codex installation instructions](README.md#codex-installation) to install the skill.

<a id="进入对话后调用"></a>

### Invoke it in an interactive conversation

Open a terminal in the working directory where you want to save the images:

```bash
codex
```

Enter `/skills` in the Codex input box to check that `siuyu-lightbox-still-life` is loaded, then send:

```text
Use $siuyu-lightbox-still-life to design a 16:9 light-table still life of a glass cup.
Keep the cup, matching design drawing, and complete tracing paper in frame, with light passing upward through single and overlapping sheets.
Generate the image, check the rim, walls, handle connections, and paper edges, and save the result.
```

<a id="带参考图片启动"></a>

### Start with a reference image

Run this in the system terminal, replacing the image path with your file:

```bash
codex --image /absolute/path/reference.png 'Use $siuyu-lightbox-still-life to create a 16:9 light-table still life from this reference. Preserve the subject structure and arrange a matching design drawing with complete translucent paper layers.'
```

Single quotes keep `$siuyu-lightbox-still-life` literal in the shell command. When typing in a Codex conversation, enter the request directly. `--image` supplies the reference; generation uses the image tool actually available in that session. See the [official image guide](https://learn.chatgpt.com/docs/image-generation).

<a id="skills-installer"></a>

<a id="skills-安装工具"></a>

## skills installer

Requires Node.js and npm. Run in the project where you want to use the skill:

```bash
npx skills add https://github.com/masiuyu/siuyu-lightbox-still-life --skill siuyu-lightbox-still-life --agent codex
```

This installs the skill for Codex in the current project, available through `.agents/skills/`. Start Codex in the same project after installation. For user-level installation and updates with a backup, see [other Codex installation methods](README.md#other-codex-installation-methods). Installer arguments are documented in the [skills repository](https://github.com/vercel-labs/skills).

<a id="python-scripts"></a>

<a id="本仓库的-python-脚本"></a>

## Repository Python scripts

Requires Python 3.10 or newer. Run the following relative-path commands from this repository's root, the directory containing `SKILL.md`.

| Script | Purpose and output |
|---|---|
| `scripts/install_skill.py` | Copies the complete skill to the chosen directory and can back up an existing version |
| `scripts/validate_skill.py` | Validates the skill package, documentation links, examples, and compiler |
| `scripts/build_image_job.py` | Reads `direction.json` and produces `image-job.json` with the prompt and ordered reference images |
| `scripts/validate_image_review.py` | Checks that visual review entries and the overall status agree in an existing generation record |
| `scripts/verify_project.py` | Checks prerequisites for a separately prepared local renderer project |

Validate the package:

```bash
python3 scripts/validate_skill.py .
```

Compile a direction file you have prepared:

```bash
python3 scripts/build_image_job.py /absolute/path/direction.json --output /absolute/path/image-job.json
```

Codex or an adapted agent passes the resulting prompt and ordered images to its image tool. For direction fields, invocation, and records, see [direction compilation and image invocation (Chinese)](references/prompt-execution.md).

Check a saved generation and visual review record:

```bash
python3 scripts/validate_image_review.py /absolute/path/generation-record.json
```

This checks consistency in the record. Image quality is assessed by opening and inspecting the actual image.

<a id="renderer-cli"></a>

<a id="配套本地渲染器-cli"></a>

## Companion local renderer CLI

For deterministic rendering, precise source-layer composition, or renderer development. `@lightbox/cli` belongs to a separately prepared renderer project and requires that project, Node.js, pnpm, and its dependencies. This repository supplies the skill, documentation, and wrapper scripts.

Check the renderer project from a local terminal first:

```bash
python3 /absolute/path/siuyu-lightbox-still-life/scripts/verify_project.py --repo /absolute/path/lightbox-archive --json
```

The skill's `ingest.sh`, `preview.sh`, `review.sh`, and `final.sh` call the project through `pnpm --filter @lightbox/cli`. They locate the renderer using `LIGHTBOX_REPO_ROOT`, or search upward from the current directory for a project containing `pnpm-workspace.yaml` and `apps/cli/package.json`.

With the project ready, follow the [local renderer workflow (Chinese)](references/offline-workflow.md). For development or integration, use the [renderer development guide (Chinese)](references/codex-execution.md).
