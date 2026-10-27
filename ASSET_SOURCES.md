# Siuyu Lightbox Still Life配图来源

本文件记录随包图片的实际生成来源。成图用于展示物件结构、光线和材料关系；各图的实际像素、生成工具和视觉复查可在相应记录中核对。

## 九组横竖案例

- 位置：`assets/examples/real-objects-20260913/`。
- 数量：十八张，九组主体方向，各有横幅和竖幅构图。
- 生成方式：内置 `image_gen.imagegen`，以文字编写现实器物、纸张和操作场景；这些调用的图像输入数量为零。
- 原生尺寸：横幅 1672×941，竖幅 941×1672。
- 记录：每张图片旁保留 `direction.json`、`image-job.json`、`generation-record.json` 和 `visual-review.md`；[图库目录](assets/examples/catalog.json) 汇总实际哈希、尺寸与观察重点。

## 底光硫酸纸展示图

- 图片：[transmitted-paper.png](assets/showcase/transmitted-paper.png)。
- 记录：[provenance.json](assets/showcase/provenance.json)。
- 生成方式：内置 `image_gen.imagegen`；剪刀、石墨图稿、硫酸纸和蓝色薄片按本轮文字方向生成。
- 图像输入：两张用户提供的画面用于观察从下方向上透射的光线、实体明暗与材料密度关系。
- 参考文件名称：`KIMI K3 — an exploration of intelligence as an invisible force. a launch film created in collabo.jpg`；`KIMI K3 — an exploration of intelligence as an invisible force. a launch film created in collabo-4.jpg`。
- 分发内容：生成后的展示图与可移植来源记录。参考文件由原提供者保管。
- 记录用途：`provenance.json` 是此次实际生成的来源摘要；新的成像任务应根据当次输入重新建立方向。

## 品牌标记

`assets/brand/siuyu-mark.svg` 以相叠的纸面和研究线条构成，用于 Skill 界面及介绍页。

## 记录状态

视觉复查记录由主助手查看实际图片后填写。用户审美接受仍按真实反馈记录；包结构和文件校验各有独立证据。图片来源记录与发布许可分别管理，正式发布许可由作者指定。

## 2026-10-27 跨题材样张

`assets/showcase/20261027/` 收录材料摄影、雨夜人物叙事与温室水彩三张独立成图。实际生成工具为内置 image_gen.imagegen，三次调用的图像输入数量均为零，模型名称按工具未披露记录。每例保留 image.png 原生图、direction.md、tool-call.json、review.md 与 provenance.json；preview.jpg 由原生文件按原尺寸导出 JPEG，供网页显示。

三张原生尺寸分别为 1448×1086、1122×1402 和 1536×1024。记录中的 SHA256 对应实际文件，可见评审由主助手查看全图与原生细节后填写；用户接受沿真实反馈记录。具体图像由当前任务文字形成，方法研究的来源归属见 [方法来源与贡献](references/method-sources.md)。
