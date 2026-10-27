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

## 自然语言方向与本地脚本

Python 3.10 或更新版本即可运行常规方向和评审接口。以下命令在包含 SKILL.md 的包目录执行。

让 AI 先查看实际来源，写好 direction.md。把本轮图片逐行放在“参考图片”段，完整提示词写在“成像说明”段，Image N 按图片出现顺序对应。观察、取舍和授权依据保留在其他段落。完整写法见 [执行说明](references/prompt-execution.md)。

```bash
python3 scripts/lightbox.py compile /absolute/path/direction.md --output-dir /absolute/path/new-version
python3 scripts/lightbox.py check /absolute/path/new-version
```

这会保存方向副本、实际提示词、图像工具参数、图片顺序和指纹。输出目录必须是新版本。编译后由 Codex 将 image-job.json 原样传入实际可用图像工具，取得原生图片，再查看全图和原生细节。

```bash
python3 scripts/lightbox.py review /absolute/path/review.md
```

review.md 的核心表记录位置、所见、要求与结论。检查核对汇总一致性，实际像素由看图判断。样例见 [评审文件](assets/review.example.md)。

### 已有图片的证据对应

实际生成和看图后，带 Pillow 的 Python 环境可连接编译包、真实 imagegen 参数、原生图与本轮评审：

```bash
python3 scripts/lightbox.py evidence /absolute/path/compiled --call /absolute/path/tool-call.json --image /absolute/path/image.png --review /absolute/path/review.md --output /absolute/path/new-evidence.json
python3 scripts/lightbox.py check-evidence /absolute/path/new-evidence.json
```

可用 `--detail-index` 逐像素核对原生裁区，用 `--execution` 留存实际执行附件。检查针对文件状态与像素对应，生成真实性、视觉判断和用户接受继续分别确认。详见 [图片证据](references/image-evidence.md)。

### 既有记录与包维护

```bash
python3 scripts/lightbox.py migrate /absolute/path/direction.json --output /absolute/path/new-direction.md
python3 scripts/build_image_job.py /absolute/path/direction.json --output /absolute/path/new-job.json
python3 scripts/validate_image_review.py /absolute/path/generation-record.json
python3 scripts/validate_skill.py .
python3 -B scripts/test_natural_direction.py
python3 -B scripts/test_image_evidence.py
```

迁移保持旧编译正文与参考顺序，设计内容由本轮任务复核。旧文件继续保留。安装脚本沿 [安装说明](README.zh-CN.md#codex-其他安装方式) 使用，程序验证只覆盖实际执行的检查。[迁移说明](references/interface-migration.md) 列出当前接口和证据边界。

<a id="renderer-cli"></a>

## 精确印刷与配套渲染器

精确处理同样先从自然语言目标开始。AI 确定实际算法、源图面、透明边界、尺寸与输出，再生成程序需要的内部参数卡。保存这些实际参数和报告，打开输出图检查。内置印刷算法见 [印刷工具](modules/print/README.md)。

另行准备的配套渲染器使用自己的运行协议，先核对实际工程：

```bash
python3 scripts/verify_project.py --repo /absolute/path/lightbox-archive --json
```

具体执行见 [本地工作流](references/offline-workflow.md)，工程开发见 [工程执行](references/codex-execution.md)。
