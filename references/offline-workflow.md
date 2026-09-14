# 离线与精确源图层工作流

此文档适用于用户明确选择本地确定性渲染或精确源图层合成的任务。它描述已有 CLI 的实际运行协议。成像任务的默认路线由上级 [Skill 入口](../SKILL.md) 决定。

## 选择本地项目

执行 `scripts/verify_project.py --repo <repo> --json`，区分 `bootstrapReady` 与 `productionReady`。已有项目可用时按以下步骤执行；用户请求开发项目时读取 [工程执行](codex-execution.md) 和指定的 [实现任务](implementation-plan.md)。

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
