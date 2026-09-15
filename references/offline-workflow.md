# 离线与精确源图层工作流

此文档适用于已有配套本地渲染器工程，并明确选择确定性渲染或精确源图层合成的任务。下文的 CLI 专指该工程的 `@lightbox/cli`；本 Skill 中的 Shell 脚本负责调用它。运行需要单独准备渲染器工程及其 Node.js、pnpm 和工程依赖。命令分类与工程定位见 [渲染器 CLI 说明](../CLI.md#renderer-cli)。

Codex 常规图像创作从 [Agent 执行说明](../SKILL.md) 进入；ChatGPT 网页普通 Chat 使用 [网页创作说明](../CHATGPT.md)。

## 选择本地项目

在本地终端执行 `python3 <skill-dir>/scripts/verify_project.py --repo <renderer-repo> --json`，其中 `<skill-dir>` 是本 Skill 的实际目录，`<renderer-repo>` 是配套渲染器工程目录。区分 `bootstrapReady` 与 `productionReady`。已有项目可用时按以下步骤执行；用户请求开发项目时读取 [工程执行](codex-execution.md) 和指定的 [实现任务](implementation-plan.md)。

## 素材与方向

1. 收集主体、准确文字、素材用途和尺度证据。读取 [来源分析](source-analysis.md) 与 [素材清单](asset-manifest.md)。
2. 执行 `bash <skill-dir>/scripts/ingest.sh PROJECT_ID INPUT_DIRECTORY DATA_ROOT [HINTS_JSON]`。
3. 展示素材清单和联系表。CLI 要求当前 manifest 的真实人工批准记录；使用用户已明确给出的批准，保持哈希绑定。具体格式见 [工作流协议](workflow-contract.md)。
4. 创建 `visual-direction.json`。只读取本次涉及的 [方向 schema](visual-direction.md)、[布局路由](layout-routing.md)、[构图](composition-recipes.md)、[场景](scene-schema.md) 和 [材质](material-presets.md)。

已有运行时使用 `VisualDirection → BuildSceneRequest → SceneSpec`。SceneSpec 定义确定性输出；准确产品、Logo 和文字按源图层约定保留。用户明确要求全部内容可见时，使用 `merge_all` 并逐项核对 `requiredVisibleAssetIds`。参考用途和尺寸证据按 schema 记录。

本地桥接器要求一个合格的 exact 产品素材。只有风格参考时，先说明本地输入还缺少什么；若用户另选图像生成，则回到 Skill 的图像成片流程。

## 编译、预览与像素检查

```bash
python3 <skill-dir>/scripts/compile_generation_description.py   /path/to/visual-direction.json   --manifest /path/to/manifest.json   --workflow /path/to/workflow.json   --output /path/to/generation-description.txt

bash <skill-dir>/scripts/preview.sh PROJECT_ID DATA_ROOT VISUAL_DIRECTION_JSON [SEED]
```

此编译器产生供本地 SceneSpec 使用的规划控制文档。已有模板为 `archive_research_v1`、`product_focus_v1`、`art_lab_v1`，具体语义由当前运行时决定。

打开实际保存的预览图片，核对 `PreviewEvidenceRecord` 的 scene、PNG 和哈希，再依据像素写入 `PreviewQualityReviewRecord`。检查构图、主体、材料、接触和文字。存在问题时先修正；工程验证与视觉评估各自记录。

```bash
bash <skill-dir>/scripts/review.sh PROJECT_ID SCENE_ID DATA_ROOT REVIEW_JSON
```

查看 [像素复查样例](../assets/preview-quality-review.example.json) 和 [离线验收表](acceptance-checklist.md)。

## 导出

CLI 使用两份真实的 `approvedBy: human` 记录：manifest 批准和选定场景批准。场景批准绑定当前预览和像素复查。采用当前有效的授权；审批数据由实际批准产生。

```bash
bash <skill-dir>/scripts/final.sh PROJECT_ID DATA_ROOT
```

导出前重新验证 manifest、场景、预览与审核哈希。已授权的精确源图层合成保留源产品与文字，背景控制束按当前渲染器支持的接口处理。交付本地导出图、必要图层和已知限制。

报告应准确区分确定性导出、实际使用的生成能力、像素评估和用户审美接受。公开示例另按实际授权和素材权利办理。
