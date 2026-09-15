# 本地渲染器工程执行

此文档供 Codex 或其他开发 Agent 执行配套本地渲染器的开发、工程安装或集成任务。终端中的 Python 命令需要 Python 3.10 或更新版本，`<skill-dir>` 替换为本 Skill 的实际目录。

安装本 Skill 请看 [Codex 安装说明](../README.md#codex-安装)，终端调用请看 [Codex CLI 使用](../CLI.md#codex-cli)。常规图片制作从 [Agent 执行说明](../SKILL.md) 进入，ChatGPT 网页普通 Chat 使用 [网页创作说明](../CHATGPT.md)。

## 现有项目

先读取项目的 AGENTS.md 和用户指定任务。按该任务完成实现与对应验证。`python3 <skill-dir>/scripts/verify_project.py --repo <renderer-repo> --json` 可核对本地工程条件。

实现计划按需读取 [实现任务](implementation-plan.md)。任务范围由当前用户请求决定；开发结果采用对应的代码、命令和产物证据报告。

## 新项目交接

```bash
python3 <skill-dir>/scripts/prepare_codex_handoff.py   --repo /path/to/lightbox-archive   --task 1   --copy-plan   --output /path/to/lightbox-archive/CODEX_KICKOFF.md
```

只在用户确实需要建立本地工程时运行。

## Codex Skill 的安装与同步

本 Skill 的安装目录、备份和更新命令统一见 [Codex 其他安装方式](../README.md#codex-其他安装方式)。需要自选目录时，使用安装脚本的 `--target-root` 指定 Codex 能发现的 Skills 根目录。

同步后核对本次实际改动文件。已打开的会话在需要时重新读取 Skill，后续任务加载新的安装内容。配套渲染器的安装和依赖按其工程文档执行。

## 验证

```bash
python3 <skill-dir>/scripts/validate_skill.py <skill-dir>
```

执行改动涉及的测试和类型检查。与图片效果有关的改动，还需实际调用图像工具并检查结果。

本地 schema、素材和审批协议见 [离线工作流](offline-workflow.md)。
