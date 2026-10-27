# 从自然语言任务到本地精确处理

用户明确要求精确源图面、网点构造或本地确定性合成时，先读同一份自然语言任务，确认主体、完整图面、材料、几何、尺寸和验收要求，再选择实际可用算法。AI 生成程序需要的内部参数，保存实际执行证据。

## 自包含印刷工具

常规网点和源空间印刷合成使用 [印刷工具](../modules/print/README.md)。先确定原图平面与真实透明边界，选择实际支持的分色与屏网，把纸边和图面一起变换。检查输出全图、原生细节和几何报告。需要的依赖按该模块实际说明准备。

自然语言方向说明处理目标，内部 JSON 参数卡记录精确尺寸、算法、路径与数值。代码按卡执行，AI 对照任务复核参数，成图效果继续由实际像素判断。

## 已有配套渲染器

另行准备的渲染器先核对实际工程：

```bash
python3 <skill-dir>/scripts/verify_project.py --repo /path/to/lightbox-archive --json
```

区分工程可启动与生产准备状态。需要开发时进入 [工程执行](codex-execution.md)，按用户实际任务读取实现计划。

现有运行时使用自己的素材清单、方向和场景协议，以下资料只在适配该运行时需要时读取：[素材](asset-manifest.md)、[来源](source-analysis.md)、[运行协议](workflow-contract.md)、[方向](visual-direction.md)、[场景](scene-schema.md)、[布局](layout-routing.md)、[构图](composition-recipes.md)、[材质](material-presets.md)。AI 从当前自然语言任务生成对应机器文件，准确主体、标识和文字按源图层保留。

## 实际预览与导出

既有脚本的入参与批准记录由运行时决定：ingest.sh 处理素材，compile_generation_description.py 编译内部方向，preview.sh 保存预览，review.sh 提交实际像素复查，final.sh 导出。精确 CLI 见各脚本和 [运行协议](workflow-contract.md)。

当前用户的真实批准按其范围与实际文件哈希绑定。运行时要求素材与场景批准时，使用已经有效的授权；缺项集中列出，准备具体可审的结果。预览、评审和导出使用同一版本的素材、场景、PNG 与哈希。

实际打开预览和输出，检查来源范围、完整构图、材料、接触和准确文字。程序完成、几何证据、视觉结论、用户接受和发布各自记录。已有输出版本继续保留。
