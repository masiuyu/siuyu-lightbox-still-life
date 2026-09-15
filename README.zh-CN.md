# Siuyu Lightbox Still Life

[简体中文](README.zh-CN.md) | [English](README.md)

**用光台静物图，呈现物件的结构与质感。**

Siuyu Lightbox Still Life 是面向 Codex 的图像创作 Skill。上传物件照片和风格参考，或从文字想法开始，设计构图、生成图片，再检查结构、光线和材料细节。仓库也提供适合 ChatGPT 网页普通 Chat 阅读的创作说明。

默认风格是**底光透射**：从明亮乳白、略偏冷的光台正上方俯拍，把主体与对应图稿、材料样片有序摆放。光从下方穿过纸张和薄片，交叠处更暗，被覆盖的线稿更淡；实体保留暗部与真实反光。纸张采用完整矩形，主体、工具和纸张四周留出余量。你也可以指定柔光纸层、单件主视觉、操作场景或材质特写。

Codex 调用名：`$siuyu-lightbox-still-life` · 作者：siuyu · 版本：`1.0.0-rc.1`

[Codex 安装](#codex-安装) · [Codex 使用](#codex-使用) · [Codex CLI](#codex-cli-使用) · [ChatGPT 网页版](#chatgpt-网页版使用) · [完整图库](references/example-gallery.zh-CN.md)

![剪刀与硫酸纸的底光透射研究](assets/showcase/transmitted-paper.png)

*光从下方透过硫酸纸。两张纸交叠的区域更暗，被覆盖的铅笔线条也更淡，剪刀表面仍能看见金属反光。图片信息见 [配图说明](ASSET_SOURCES.md)。*

## 选择使用方式

| 使用的软件或环境 | 怎样开始 | 对应说明 |
|---|---|---|
| Codex 桌面端、IDE 扩展 | 安装 Skill，在 Codex 对话中调用 | [Codex 安装](#codex-安装)与[使用示例](#codex-使用) |
| Codex CLI | 安装 Skill，在终端启动 `codex` 后输入任务 | [Codex CLI 使用](#codex-cli-使用) |
| ChatGPT 网页普通 Chat | 把文档链接与参考图发进对话，按说明创作 | [ChatGPT 网页版使用](#chatgpt-网页版使用) |
| 本地脚本、配套渲染器 | 在终端执行对应程序，编译方向、检查记录或运行渲染器 | [命令行工具说明](CLI.zh-CN.md) |

## Codex 安装

适用于已能访问本地文件的 Codex 桌面端、CLI 和 IDE 扩展。下面两种方式任选一种。首次使用 Codex CLI，可先阅读 [Codex CLI 官方安装说明](https://learn.chatgpt.com/docs/codex/cli)。

### 在 Codex 对话中安装

把下面这段话发送给 Codex：

```text
请从 https://github.com/masiuyu/siuyu-lightbox-still-life 安装这个 Skill。
先读取仓库说明并运行包校验，将完整 Skill 安装到 ~/.agents/skills/siuyu-lightbox-still-life。
如果已有同名版本，先完整备份。完成后检查 Codex 是否能发现它，告诉我实际安装位置和调用方式。
```

安装完成后新建 Codex 对话，使用 `$siuyu-lightbox-still-life`。尚未显示时重新启动 Codex。用户级与项目级目录见 [Codex 安装位置与更新](#codex-安装位置与更新)。

### 用终端安装到当前项目

已安装 Node.js 与 npm 时，在需要使用这个 Skill 的项目目录打开终端，运行：

```bash
npx skills add https://github.com/masiuyu/siuyu-lightbox-still-life --skill siuyu-lightbox-still-life --agent codex
```

这里使用第三方 [skills 安装工具](https://github.com/vercel-labs/skills)，`--agent codex` 指定目标软件，当前项目的安装入口为 `.agents/skills/`。完成后在同一项目中打开 Codex。

下载 ZIP 或使用 Python 脚本安装到用户目录，请看 [Codex 其他安装方式](#codex-其他安装方式)。

## Codex 使用

以下文字发送到已经加载本 Skill 的 Codex 对话中。`$siuyu-lightbox-still-life` 用于调用 Skill；参考照片作为附件上传。

有明确的物件时，可以这样描述：

```text
使用 $siuyu-lightbox-still-life，根据附件生成一张 16:9 的光台研究静物图。
从台面正上方俯拍，保留主体的实际结构，在旁边安排对应的轮廓图和材料样片。
硫酸纸平铺在透光台面上，光从下面穿过纸张，交叠处的明暗差别清楚。
台面铺满画面四周，主体和图稿完整入镜，物件之间留出间距。
请实际生成图片，并打开结果检查。
```

还没有照片时，可以先描述想做的物件：

```text
使用 $siuyu-lightbox-still-life，自主设计一张 9:16 的玻璃杯材料研究图。
杯子的开口、杯壁、杯底和把手都要清楚可辨。
在杯子旁边安排轮廓图、玻璃样片和透光纸层，展示杯子的结构与玻璃的透光效果。
```

## Codex CLI 使用

在终端使用 Codex 时，先完成上面的 Skill 安装，再进入要保存本次作品的工作目录，运行：

```bash
codex
```

在打开的 Codex 交互界面中输入 `/skills` 检查已加载的 Skill，再发送上方 [Codex 使用示例](#codex-使用)。带图片启动、直接传入任务及脚本用法见 [命令行使用说明](CLI.zh-CN.md#codex-cli)。

## 五种画面方向

| 画面方向 | 适合怎样的画面 |
|---|---|
| **底光透射（默认）** | 明亮乳白光台从下方照亮纸张和透明薄片，交叠处更暗，下层线稿更淡，实体物件保留表面反光与暗部。 |
| 柔光纸层 | 乳白台面上铺着描图纸，用柔和光线呈现纸张纹理，以及下层线条透过上层纸张的效果。 |
| 色场主视觉 | 用大面积的统一底色衬托物件，例如以蓝灰色台面突出白瓷杯的轮廓与明暗。 |
| 工作台动作 | 把描图、摆放或手持纸稿的动作放入画面，表现手、工具与物件的实际接触。 |
| 材质近摄 | 靠近物件，观察金属反光、拉丝纹理或纸张纤维，围绕指定细节安排取景。 |

直接描述主体即可采用底光透射默认风格；也可以按表中的其他方向提出要求。图稿、样片、工具和摆放方式围绕本次主体设计，横竖画幅分别安排完整构图。

## 横幅与竖幅，分别构图

| 16:9 横幅 | 9:16 竖幅 |
|---|---|
| ![咖啡勺横幅](assets/examples/real-objects-20260913/02-spoon-paper/landscape/image.png) | ![咖啡勺竖幅](assets/examples/real-objects-20260913/02-spoon-paper/portrait/image.png) |

横幅和竖幅各自安排主体、图稿与纸层的位置。制作一组图片时，可以保持物件、材料和色调一致，再根据画幅调整分组和间距。

## 随包提供的案例

图库收录九组主题，每组各有一张横幅和一张竖幅，共十八张图片。你可以在 [完整图库](references/example-gallery.zh-CN.md) 中并排查看构图，并打开每张图的生成记录和看图记录。

| 案例 | 观察重点 |
|---|---|
| [玻璃杯透光研究](references/example-gallery.zh-CN.md#example-01) | 杯口、杯底和把手怎样连接，玻璃样片叠放后怎样透光。 |
| [咖啡勺轮廓与纸层](references/example-gallery.zh-CN.md#example-02) | 勺子的轮廓怎样对应纸上的石墨图稿。 |
| [瓷杯色场主视觉](references/example-gallery.zh-CN.md#example-03) | 蓝灰色台面怎样衬托白瓷杯与杯碟。 |
| [咖啡勺描绘操作](references/example-gallery.zh-CN.md#example-04) | 一只手压住纸张，另一只手握笔描绘时的接触位置。 |
| [咖啡勺表面近摄](references/example-gallery.zh-CN.md#example-05) | 勺碗的抛光反射与长柄的拉丝纹理。 |
| [咖啡勺工艺比较](references/example-gallery.zh-CN.md#example-06) | 抛光钢片、拉丝钢片和纸上铅笔排线之间的比较。 |
| [手持咖啡勺图稿](references/example-gallery.zh-CN.md#example-07) | 双手托起纸稿时的纸张弯曲，以及下层线条在覆盖区域内外的深浅。 |
| [棉纸字形压纹](references/example-gallery.zh-CN.md#example-08) | 字母压纹的深浅、纸张纤维与切边。 |
| [柔光箱透光纸层](references/example-gallery.zh-CN.md#example-09) | 单层纸与叠层纸的明暗差别，以及跨过纸边界的铅笔线条。 |

## 它怎样工作

1. **确认主体与参考用途。** 查看你提供的附件，确认物件的部件和外形，以及各张参考用于说明什么。只有文字要求时，先确定要呈现的物件及其结构。
2. **设计并生成画面。** 安排光线、材料和物件的位置，整理完整提示词，再调用当前环境的图像生成工具。Codex 完整流程会保存方向记录，并通过脚本编译图像任务。
3. **打开图片检查。** 核对主体结构、纸层透光和构图，再检查物件与台面的接触，以及操作场景中手与工具的位置。有具体问题时，再据此调整画面。

在 Codex 中，常规交付包含生成图片、画面方向、实际成像任务和简短的看图记录。网页版按当前对话的能力提供成图、提示词和必要说明，见 [ChatGPT 网页 Chat 创作说明](CHATGPT.zh-CN.md)。

## Codex 常用请求

以下示例发送到 Codex 对话。ChatGPT 网页 Chat 的复制指令见[对应入口](#chatgpt-网页版使用)。

**保留产品的外形和材料特点：**

```text
使用 $siuyu-lightbox-still-life，把附件中的产品做成光台材料研究图。
保留产品的实际结构和颜色，纸上图稿与产品轮廓对应，
材料样片选用与产品表面相符的材质。
```

**制作一组横幅和竖幅：**

```text
使用 $siuyu-lightbox-still-life，为同一主体分别设计一张 16:9 和一张 9:16 的图片。
两张图保持材料和色调一致，根据各自的画幅安排物件、纸层和周围的留白。
```

**调整已有图片的透光效果：**

```text
使用 $siuyu-lightbox-still-life，继续修改这一版。
保持主体与图稿的位置，增强光线从下方穿过硫酸纸的效果。
两张纸交叠的位置要比单层更暗，被盖住的铅笔线条要更淡。
请查看修改后的图片，核对这两处变化。
```

## ChatGPT 网页版使用

打开 [ChatGPT](https://chatgpt.com/)，新建普通 **Chat** 对话，上传参考图片，再把下面这段话发送给模型。网页方式通过读取创作说明在当前对话中使用；准备好链接和附件即可开始。

```text
请读取 Siuyu Lightbox Still Life 的 ChatGPT 网页创作说明：
https://github.com/masiuyu/siuyu-lightbox-still-life/blob/main/CHATGPT.zh-CN.md

按照文档要求，根据附件生成一张 16:9 的光台静物图。
保留主体结构，搭配对应设计稿和完整的矩形描图纸。
底光透过单层与叠层纸张，主体、工具和全部纸边完整入镜，物件之间留出自然间距。
请实际生成图片，并按我的反馈继续调整。
```

把主体、画幅和画面要求换成自己的需求。完整操作与更多示例见 [ChatGPT 网页 Chat 创作说明](CHATGPT.zh-CN.md)。

### 链接读取与图片生成

- **链接读取失败：** 打开 [CHATGPT.zh-CN.md](CHATGPT.zh-CN.md)，把全文粘贴到对话，或下载后作为附件上传，再发送创作要求。
- **当前对话只能处理文字：** 可以先索取完整提示词，再交给自己选用的图像工具；需要在 ChatGPT 内完成成图时，使用支持图像生成的对话。功能可用性取决于套餐与工作区设置，见 [ChatGPT 图像功能说明](https://learn.chatgpt.com/docs/image-generation)。
- **用量：** 普通 Chat 按当前账号的消息与图像用量规则使用。ChatGPT Work 与 Codex 共享使用额度，具体规则见 [OpenAI 用量说明](https://learn.chatgpt.com/docs/pricing)。

## 运行环境

Skill 提供创作流程与配套脚本。各软件负责提供文件访问、图片查看及图像生成能力。

| 使用方式 | 所需条件 |
|---|---|
| Codex 桌面端、CLI、IDE 扩展的完整流程 | Codex 能加载 Skill、读写文件并查看图片；Python 3.10 或更新版本；实际成图需要可调用的图像生成工具 |
| 通过 `npx skills` 安装 | 终端、Node.js 与 npm；安装命令指定 Codex |
| 运行仓库 Python 脚本 | 本地 Python 3.10 或更新版本，脚本使用标准库；各命令的输入与输出见 [Python 脚本说明](CLI.zh-CN.md#python-scripts) |
| ChatGPT 网页普通 Chat | 能读取链接、粘贴文本或上传文档；实际成图需要当前对话支持图像生成 |
| 配套本地渲染器 | 单独准备并验证渲染器工程、Node.js、pnpm 及工程依赖，见 [渲染器 CLI](CLI.zh-CN.md#renderer-cli) |

本项目的完整图像流程已在 Codex 桌面环境验证；其他客户端按实际工具配置使用。需要适配其他 Agent 时，按其 Skills 目录、附件接口、脚本执行和图像工具要求配置。

## Codex 其他安装方式

以下命令在 macOS、Linux 或 Windows WSL 终端执行。目标是将本 Skill 安装到 Codex 可发现的用户目录，供本机各项目使用。

### 从 GitHub 克隆后安装

需要 Git 与 Python 3.10 或更新版本：

```bash
git clone https://github.com/masiuyu/siuyu-lightbox-still-life.git
cd siuyu-lightbox-still-life
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills"
```

### 从 ZIP 安装

下载仓库 ZIP，解压后在包含 `SKILL.md` 的目录打开终端，再运行：

```bash
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills"
```

### Codex 安装位置与更新

上面的用户级安装位置为 `~/.agents/skills/siuyu-lightbox-still-life`。项目级安装放在该项目的 `.agents/skills/siuyu-lightbox-still-life`。目录规则见 [Codex Skills 官方说明](https://learn.chatgpt.com/docs/build-skills)。

更新通过本仓库 Python 脚本安装的版本时，先取得最新仓库文件，再在仓库目录运行：

```bash
python3 scripts/validate_skill.py .
python3 scripts/install_skill.py --target-root "$HOME/.agents/skills" --backup-existing
```

旧版完整保存在目标 Skills 目录旁的 `skill-backups/` 中，脚本会输出实际位置。使用自定义目录时，将 `--target-root` 换成当前安装位置的父目录。通过第三方 `skills` 工具安装的版本，按该工具的更新方式管理。

脚本自身未指定 `--target-root` 时，使用 `$CODEX_HOME/skills`，或环境变量未设置时的 `~/.codex/skills`。上述命令通过显式指定目录，与当前 Codex 本地 Skills 目录说明保持一致。安装后新建对话；Skill 尚未显示时重新启动 Codex。

## 按用途查阅文档

| 文档 | 适合谁阅读 |
|---|---|
| [Codex 安装与调用](#codex-安装) | 在 Codex 桌面端、CLI 或 IDE 扩展中使用本 Skill 的用户 |
| [命令行使用说明](CLI.zh-CN.md) | 使用 Codex CLI、安装工具、Python 脚本或配套渲染器的用户 |
| [ChatGPT 网页 Chat 创作说明](CHATGPT.zh-CN.md) | 通过文档链接、粘贴或上传方式创作的网页用户 |
| [Agent 执行说明](SKILL.md) | 执行本 Skill 的 Codex，或正在适配完整流程的 Agent |
| [Python 方向编译与成像调用](references/prompt-execution.md) | 需要整理方向文件、编译图像任务和保存生成记录的操作者 |
| [配套渲染器工作流](references/offline-workflow.md) | 已有本地渲染器工程、需要确定性导出或源图层合成的开发者 |
| [本地渲染器工程开发](references/codex-execution.md) | 需要开发、安装或集成配套渲染器的开发者 |
| [示例图库](references/example-gallery.zh-CN.md) | 查看成图、构图与材料表现的所有读者 |

## 包内结构

```text
siuyu-lightbox-still-life/
├── SKILL.md                 # Codex 与适配 Agent 的中文执行说明
├── README.md                # 英文项目介绍与安装说明
├── README.zh-CN.md          # 中文项目介绍与安装说明
├── CLI.md                   # 英文命令行说明
├── CLI.zh-CN.md             # 中文命令行说明
├── CHATGPT.md               # ChatGPT 网页英文创作说明
├── CHATGPT.zh-CN.md          # ChatGPT 网页中文创作说明
├── ASSET_SOURCES.md         # 配图信息
├── agents/openai.yaml       # 名称、图标与默认调用
├── assets/                  # 配置样例、摄影预设与生成图片
├── references/              # 中英文图库与详细创作指南
├── scripts/                 # 安装、编译和检查脚本
└── evals/                   # 行为评估场景
```

## 常见问题

**一定要上传照片吗？** 如果想保留某件物品的外形，请上传它的照片；如果是探索新的设计，可以从文字开始。附上多张参考时，请说明哪张用于确认物件结构，哪张用于参考光线、颜色或构图。

**能指定比例和像素尺寸吗？** 默认横幅为 16:9，竖幅为 9:16，也接受其他比例或目标像素尺寸。实际尺寸取决于图像工具的输出，交付记录会注明。随包案例的原生尺寸为 1672×941 或 941×1672，与目标比例有像素取整造成的细小差异。

**每次都会采用同样的摆法吗？** 摄影预设提供光线和材料的处理方式，具体物件、图稿和布局根据本次要求设计。修改已有图片时，可以说明哪些位置、颜色或材料需要保持。

**案例图片可以下载吗？** 可以。十九张生成图片随仓库保存在 `assets/` 中，克隆或下载 ZIP 后即可在本地查看，生成来源见 [素材来源](ASSET_SOURCES.md)。

## 配图与发布信息

随包的十九张静物图片均由 AI 图像工具生成。九组横竖案例与底光硫酸纸展示图分别呈现器物结构、纸层和材料细节。各图的生成方式与图片信息见 [配图说明](ASSET_SOURCES.md)。当前版本为 `1.0.0-rc.1`。
