# 本地渲染器工程执行

此文档适用于明确的本地渲染器开发、安装或集成任务。正常图片制作从 [Skill 入口](../SKILL.md) 的图像成片流程执行。

## 现有项目

先读取项目的 AGENTS.md 和用户指定任务。按该任务完成实现与对应验证。`scripts/verify_project.py --repo <repo> --json` 可核对本地工程条件。

实现计划按需读取 [实现任务](implementation-plan.md)。任务范围由当前用户请求决定；开发结果采用对应的代码、命令和产物证据报告。

## 新项目交接

```bash
python <skill-dir>/scripts/prepare_codex_handoff.py   --repo /path/to/lightbox-archive   --task 1   --copy-plan   --output /path/to/lightbox-archive/CODEX_KICKOFF.md
```

只在用户确实需要建立本地工程时运行。

## 安装与同步

首次安装到空目标可用：

```bash
python <skill-dir>/scripts/install_skill.py --target-root /absolute/path/to/skills
```

默认目标为 `$CODEX_HOME/skills`，环境未设置时为 `~/.codex/skills`。更新已有安装时先核对 canonical 来源、备份已有文件，再按精确文件清单覆盖和新增；保留目标中其余文件。需要目标目录写权限时，使用环境提供的审批机制。

同步后核对文件哈希。已打开的会话在需要时重新读取 Skill，后续任务加载新的安装内容。

## 验证

```bash
python <skill-dir>/scripts/validate_skill.py <skill-dir>
```

执行改动涉及的测试和类型检查。与图片效果有关的改动，还需实际调用图像工具并检查结果。

本地 schema、素材和审批协议见 [离线工作流](offline-workflow.md)。
