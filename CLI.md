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
Use $siuyu-lightbox-still-life to design a 16:9 light-table still life of a
glass cup.
Keep the cup, matching design drawing, and complete tracing paper in frame,
with light passing upward through single and overlapping sheets.
Generate the image, check the rim, walls, handle connections, and paper
edges, and save the result.
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

## Natural-language directions and local scripts

Python 3.10 or newer is sufficient for the regular direction and review interface. Run the following commands from the package directory containing SKILL.md.

The AI first views the actual sources and authors direction.md. List local Markdown image links under Reference images, and write the complete prompt under Image instructions. Image N follows the image-list order. Keep observations, alternatives and authorization evidence in other sections. See [execution](references/prompt-execution.md).

```bash
python3 scripts/lightbox.py compile /absolute/path/direction.md --output-dir /absolute/path/new-version
python3 scripts/lightbox.py check /absolute/path/new-version
```

The new directory contains the replayable direction, exact prompt, native image-tool arguments, input order and fingerprints. Codex then passes image-job.json to the available image tool, saves the native image and inspects the whole frame and native details. Compilation itself does not generate an image.

```bash
python3 scripts/lightbox.py review /absolute/path/review.md
```

The core table records position, observation, requirement and conclusion. The checker validates the summary; the operator inspects actual pixels. See the [review example](assets/review.example.md).

### Saved image evidence

After generation and visual review, a Python environment with Pillow can bind the compiled job, actual imagegen arguments, native still and review to a new record:

```bash
python3 scripts/lightbox.py evidence /absolute/path/compiled --call /absolute/path/tool-call.json --image /absolute/path/image.png --review /absolute/path/review.md --output /absolute/path/new-evidence.json
python3 scripts/lightbox.py check-evidence /absolute/path/new-evidence.json
```

Add `--detail-index` for exact native-crop verification and `--execution` to bind a saved execution attachment. This checks saved files and pixel correspondence; actual generation evidence, visual judgment and user acceptance remain separate. See the Chinese [image evidence guide](references/image-evidence.md).

### Existing records and maintenance

```bash
python3 scripts/lightbox.py migrate /absolute/path/direction.json --output /absolute/path/new-direction.md
python3 scripts/build_image_job.py /absolute/path/direction.json --output /absolute/path/new-job.json
python3 scripts/validate_image_review.py /absolute/path/generation-record.json
python3 scripts/validate_skill.py .
python3 -B scripts/test_natural_direction.py
python3 -B scripts/test_image_evidence.py
```

Migration retains the old compiled prompt and reference order. Recheck the design against the current task and sources. Preserve previous files. Use the installer through the [installation guide](README.md#codex-installation). See [migration](references/interface-migration.md) for interface and evidence boundaries.

<a id="renderer-cli"></a>

## Precise print processing and companion renderer

Begin precise processing with the same natural-language objective. The AI selects the supported algorithm, source plane, alpha boundary, dimensions and output, then creates the backend's machine parameter card. Preserve those actual parameters and reports, and inspect the output image. See the [print tools](modules/print/README.md).

The separately prepared companion renderer has its own runtime contract. Check the actual project first:

```bash
python3 scripts/verify_project.py --repo /absolute/path/lightbox-archive --json
```

Follow the [local workflow](references/offline-workflow.md) for operation and [engineering workflow](references/codex-execution.md) for explicit development.
