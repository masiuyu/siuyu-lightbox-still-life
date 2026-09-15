# 命令行使用说明

[简体中文](CLI.zh-CN.md) | [English](CLI.md)

本文适合在终端使用 Codex 或执行本仓库脚本的用户。以下 Shell 命令以 macOS、Linux 或 Windows WSL 为例；把示例路径换成自己的实际路径。

[Codex 安装](README.zh-CN.md#codex-安装) · [Codex 图像创作](README.zh-CN.md#codex-使用) · [ChatGPT 网页 Chat](CHATGPT.zh-CN.md)

## 先确认命令属于哪个工具

| 命令 | 使用的软件 | 执行位置与作用 |
|---|---|---|
| `codex` | OpenAI Codex CLI | 在系统终端启动 Codex 对话，读取 Skill、处理素材并执行任务 |
| `/skills`、`$siuyu-lightbox-still-life` | Codex 的交互界面 | 在 Codex 输入框查看或调用 Skill |
| `npx skills add ...` | 第三方 skills 安装工具 | 在系统终端下载并安装 Skill，参数指定 Codex |
| `python3 scripts/...` | 本仓库的 Python 脚本 | 在本地终端安装、编译方向或检查记录，具体输入与输出见下表 |
| `pnpm ... --filter @lightbox/cli ...` | 配套本地渲染器 CLI | 在单独准备的渲染器工程中处理素材、预览和导出 |

<a id="codex-cli"></a>

## Codex CLI

先按 [Codex CLI 官方说明](https://learn.chatgpt.com/docs/codex/cli) 安装客户端并登录，再按 [本项目的 Codex 安装说明](README.zh-CN.md#codex-安装) 安装 Skill。

### 进入对话后调用

在要保存本次作品的工作目录打开终端，运行：

```bash
codex
```

在出现的 Codex 输入框中发送 `/skills`，检查 `siuyu-lightbox-still-life` 是否已加载，再输入：

```text
使用 $siuyu-lightbox-still-life，设计一张 16:9 的玻璃杯光台静物图。
杯子、对应设计稿和完整描图纸共同入镜，底光穿过单层与叠层纸张。
请生成图片，检查杯口、杯壁、把手连接和纸张边缘，并保存结果。
```

### 带参考图片启动

在系统终端运行；将图片路径换成自己的文件：

```bash
codex --image /absolute/path/reference.png '使用 $siuyu-lightbox-still-life，根据这张参考图生成一张 16:9 的光台静物图，保留主体结构，搭配对应设计稿和完整透光纸层。'
```

Shell 命令中的任务文字用单引号包围，以保留 `$siuyu-lightbox-still-life` 的原样内容。在 Codex 对话框里输入任务时，直接输入正文即可。`--image` 用于提供参考图；成图由当前会话实际可用的图像生成工具完成。图片输入与生成见 [官方图像功能说明](https://learn.chatgpt.com/docs/image-generation)。

<a id="skills-installer"></a>

## skills 安装工具

需要 Node.js 与 npm。在要使用本 Skill 的项目目录运行：

```bash
npx skills add https://github.com/masiuyu/siuyu-lightbox-still-life --skill siuyu-lightbox-still-life --agent codex
```

这条命令安装当前项目的 Codex Skill，项目入口位于 `.agents/skills/`。安装完成后，在同一项目中启动 Codex。用户级安装及备份更新见 [Codex 其他安装方式](README.zh-CN.md#codex-其他安装方式)；第三方工具的参数见 [skills 官方仓库](https://github.com/vercel-labs/skills)。

<a id="python-scripts"></a>

## 本仓库的 Python 脚本

需要 Python 3.10 或更新版本。以下相对路径命令在本仓库根目录执行，也就是包含 `SKILL.md` 的目录。

| 脚本 | 实际作用与输出 |
|---|---|
| `scripts/install_skill.py` | 复制完整 Skill 到指定目录，支持备份已有版本 |
| `scripts/validate_skill.py` | 校验 Skill 包结构、文档链接、样例和编译器 |
| `scripts/build_image_job.py` | 读取 `direction.json`，输出含提示词与参考图片顺序的 `image-job.json` |
| `scripts/validate_image_review.py` | 检查已有生成记录中视觉评审条目和汇总状态是否一致 |
| `scripts/verify_project.py` | 检查另行准备的本地渲染器工程条件 |

包校验：

```bash
python3 scripts/validate_skill.py .
```

编译已经准备好的方向文件：

```bash
python3 scripts/build_image_job.py /absolute/path/direction.json --output /absolute/path/image-job.json
```

取得任务 JSON 后，由 Codex 或适配的 Agent 将其中的提示词与图片顺序传入图像生成工具。方向字段、调用接口和记录方法见 [Python 方向编译与成像调用](references/prompt-execution.md)。

检查已经保存的生成与看图记录：

```bash
python3 scripts/validate_image_review.py /absolute/path/generation-record.json
```

这项检查核对记录的一致性，图像质量仍由实际打开图片后判断。

<a id="renderer-cli"></a>

## 配套本地渲染器 CLI

本节面向需要确定性渲染、精确源图层合成或工程开发的用户。`@lightbox/cli` 属于另行准备的渲染器工程，运行前需要该工程及其 Node.js、pnpm 和依赖；本仓库提供 Skill、文档与调用脚本。

先在本地终端核对渲染器工程：

```bash
python3 /absolute/path/siuyu-lightbox-still-life/scripts/verify_project.py --repo /absolute/path/lightbox-archive --json
```

本 Skill 的 `ingest.sh`、`preview.sh`、`review.sh`、`final.sh` 通过 `pnpm --filter @lightbox/cli` 调用工程。脚本按 `LIGHTBOX_REPO_ROOT` 指定的路径定位渲染器，或从当前目录向上寻找包含 `pnpm-workspace.yaml` 与 `apps/cli/package.json` 的工程根目录。

已具备工程时，按 [本地渲染器工作流](references/offline-workflow.md) 执行；需要开发或集成工程时，按 [本地渲染器工程开发](references/codex-execution.md) 处理。
