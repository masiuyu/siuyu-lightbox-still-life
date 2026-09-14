# Siuyu Lightbox Still Life

**让光穿过纸，让物件呈现质地。**

把你的主体与参考，做成一张结构清楚、材料可信、构图完整的光台研究静物图。支持底光透射、柔光纸层、色场主视觉、工作台动作与材质近摄；横幅采用 16:9，竖幅采用 9:16，也可以指定其他画幅。

调用名：`$siuyu-lightbox-still-life` · 作者：siuyu · 版本：`1.0.0-rc.1`

[快速安装](#快速安装) · [查看完整图库](references/example-gallery.md) · [使用方法](#用一句话开始) · [素材来源](ASSET_SOURCES.md)

![剪刀与硫酸纸的底光透射研究](assets/showcase/transmitted-paper.png)

*底光透过硫酸纸；交叠处密度加深，下层笔迹在覆盖处变淡，深色剪刀保留实体表面。此图使用两张用户提供的画面作为光线参考，生成来源见 [配图说明](ASSET_SOURCES.md)。*

## 快速安装

在终端执行：

```bash
npx skills add https://github.com/masiuyu/siuyu-lightbox-still-life --skill siuyu-lightbox-still-life
```

安装时选择 Codex，然后在新对话中使用 `$siuyu-lightbox-still-life`。运行环境需要具备图片查看和图像生成工具，方向编译需要 Python 3.10 或更新版本。

也可以把下面这段话交给 Codex：

```text
请从 https://github.com/masiuyu/siuyu-lightbox-still-life 安装这个 Skill。
读取仓库说明，校验包结构，再安装到我的 Codex Skills 目录。
如果已有同名版本，先完整备份。完成后告诉我实际安装位置和调用方式。
```

## 用一句话开始

安装后，将主体照片或风格参考附在对话中，发送：

```text
使用 $siuyu-lightbox-still-life，根据附件生成一张 16:9 光台研究静物图。
以主体实物和对应图稿组织画面，硫酸纸铺在透光箱上，光线从下面透入。
主体结构清楚，桌面连续干净，物件完整，留白有层次。
实际生成图片并查看结果。
```

只有文字想法也可以开始：

```text
使用 $siuyu-lightbox-still-life，自主设计一张 9:16 的玻璃杯材料研究图。
用杯子的轮廓图、玻璃样片和透光纸层展开研究，保持真实的器物结构。
```

## 五种画面方向

| 方向 | 画面重点 | 可以这样说 |
|---|---|---|
| 底光透射研究 | 发光台面、透射密度、实体明暗和薄片交叠 | “光从下面穿过硫酸纸，物件正面保留较深的明暗。” |
| 柔光纸层档案 | 乳白扩散光、细腻纸面、轮廓与笔迹的遮叠 | “做成柔和的描图纸研究档案，纸层关系清楚。” |
| 色场主视觉 | 集中的主体、明确色场、克制的材料搭配 | “用一块蓝灰色桌面衬托白瓷杯，建立清楚的主次。” |
| 工作台动作 | 描绘、摆放或手持图稿的真实操作 | “加入一只正在沿图稿描绘的手，动作与工具相接。” |
| 材质近摄 | 金属反射、纸纤维、表面工艺与细节 | “近看咖啡勺的抛光勺碗和拉丝长柄。” |

这些方向会依据当前主体重新组织图稿、样片与构图。主体身份、实际部件和用户指定内容来自本轮输入。

## 横幅与竖幅，分别构图

| 16:9 横向研究 | 9:16 竖向研究 |
|---|---|
| ![咖啡勺横幅](assets/examples/real-objects-20260913/02-spoon-paper/landscape/image.png) | ![咖啡勺竖幅](assets/examples/real-objects-20260913/02-spoon-paper/portrait/image.png) |

横幅用横向分组展开实物与图稿，竖幅沿纵向建立观看顺序。每张图分别安排物件、纸层和留白，交付记录保留实际像素尺寸。

## 随包提供的案例

内含九组十八张横竖案例，以及上方一张底光硫酸纸展示图。案例各有实际生成和看图记录；在 [完整图库](references/example-gallery.md) 中并排查看横竖构图。

| 案例 | 观察重点 |
|---|---|
| [玻璃杯透光研究](references/example-gallery.md#example-01) | 杯口、杯底、把手和玻璃样片的透射关系 |
| [咖啡勺轮廓与纸层](references/example-gallery.md#example-02) | 实体轮廓与石墨图稿的对应 |
| [瓷杯色场主视觉](references/example-gallery.md#example-03) | 主体、色场与观看重点 |
| [咖啡勺描绘操作](references/example-gallery.md#example-04) | 手、笔尖和纸稿的实际接触 |
| [咖啡勺表面近摄](references/example-gallery.md#example-05) | 抛光与拉丝表面的光响应 |
| [咖啡勺工艺比较](references/example-gallery.md#example-06) | 金属样片与表面研究的联系 |
| [手持咖啡勺图稿](references/example-gallery.md#example-07) | 手持纸层、下层笔迹与覆盖边界 |
| [棉纸字形压纹](references/example-gallery.md#example-08) | 压纹高差和棉纸纤维 |
| [柔光箱透光纸层](references/example-gallery.md#example-09) | 单层、叠层及被覆盖笔迹的明暗变化 |

## 它怎样工作

1. **读懂主体。** 查看本轮照片，确定实际对象、部件及参考用途；模型、图稿和样片围绕这份范围设计。
2. **组织画面并成像。** 选择光线、构图、材料与研究关系，保存方向记录，编译后调用当前环境的图像生成工具。
3. **查看实际结果。** 对照图片检查主体结构、纸层透光、构图和接触关系，再根据具体问题调整。

常规交付包含图片、方向、实际成像任务和简短看图记录。生成结果、视觉复查与用户审美选择分别记录。

## 安装与开始

### 运行条件

| 环节 | 条件 |
|---|---|
| 已验证的使用环境 | Codex，具有本地文件读写、图片查看和内置图像生成工具 |
| `npx skills` 安装 | 已安装 Node.js 与 npm |
| 方向编译与记录检查 | Python 3.10 或更新版本；使用标准库 |
| 查看介绍和图库 | 在 GitHub 阅读 README 与完整图库 |
| 本地确定性渲染 | 需另行准备配套渲染器工程，见 [离线工作流](references/offline-workflow.md) |

Skill 提供指导流程、提示词编译和检查脚本。图像生成能力由运行它的环境提供。其他 Agent 可按自身工具接口适配，兼容情况以实际验证为准。

### 克隆仓库安装

```bash
git clone https://github.com/masiuyu/siuyu-lightbox-still-life.git
cd siuyu-lightbox-still-life
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py
```

### 从压缩包安装

将 ZIP 解压，进入解压后的 `siuyu-lightbox-still-life` 文件夹，运行：

```bash
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py
```

默认安装到 `~/.codex/skills/siuyu-lightbox-still-life`；已设置 `CODEX_HOME` 时采用该目录下的 `skills/siuyu-lightbox-still-life`。安装后重新加载 Skills，或重新打开 Codex，再用 `$siuyu-lightbox-still-life` 调用。

更新同名安装时，运行 `python3 scripts/install_skill.py --backup-existing`。此前版本完整保存在 Skills 目录旁的 `skill-backups/` 中；安装脚本会输出实际保存位置。也可以用 `--target-root /path/to/skills` 指定安装根目录。

也可以把解压后的整个 `siuyu-lightbox-still-life` 文件夹放到自己的 Codex Skills 目录，并在新对话中调用。

### 让 Agent 帮你安装

将解压目录交给有本地文件权限的 Codex，发送：

```text
请安装这个文件夹里的 siuyu-lightbox-still-life Skill。
先检查 SKILL.md、agents、scripts、references 和 assets，运行包校验，
再执行 scripts/install_skill.py。目标位置已有同名版本时先向我说明，
完成后告诉我实际安装位置和调用方式。
```

## 几种实用请求

```text
使用 $siuyu-lightbox-still-life，把附件中的产品做成光台材料研究图。
保留产品的实际结构和颜色，图稿解释其轮廓，材料样片解释其表面工艺。
```

```text
使用 $siuyu-lightbox-still-life，为同一主体分别设计一张 16:9 和一张 9:16。
两张图保持材料和色调一致，分别安排完整构图。
```

```text
使用 $siuyu-lightbox-still-life，继续修改这一版。
保持主体与图稿位置，增强底光穿过硫酸纸的效果，
让叠层密度和覆盖区域的笔迹变化更清楚。
```

## 包内结构

```text
siuyu-lightbox-still-life/
├── SKILL.md                 # Agent 工作入口
├── README.md                # 介绍与使用方法
├── ASSET_SOURCES.md         # 配图来源
├── agents/openai.yaml       # 名称、图标与默认调用
├── assets/                  # 字段样例、摄影预设与实际成图
├── references/              # 美术、光路、结构、评估与进阶文档
├── scripts/                 # 安装、编译和检查脚本
└── evals/                   # 行为评估场景
```

## 常见问题

**一定要上传照片吗？** 具体主体可通过照片绑定身份；自主概念可从文字开始。风格参考按指定的光线、颜色或布局用途使用。

**画幅能指定精确尺寸吗？** 可以提出目标尺寸，交付时核对工具返回的实际像素。随包原生成图为 1672×941 或 941×1672，与目标画幅有整数取整差。

**预设是不是固定摆法？** 预设定义摄影和材料关系。物件、结构研究和布局随任务设计，也可以指定当前要保持的部分。

**图片是否随包提供？** 是。十九张实际生成图片及相关来源说明在 `assets/` 内，解压后即可本地浏览。

## 配图与发布信息

案例图片均为实际 AI 生成产物。九组横竖案例由文字概念生成；底光展示图使用两张用户提供的光线参考。详细情况见 [素材来源](ASSET_SOURCES.md)。当前版本为 `1.0.0-rc.1`。
