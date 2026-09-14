# Siuyu Lightbox Still Life 配图来源

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
- 随包内容：生成后的展示图与成图记录。
- 记录用途：`provenance.json` 是此次实际生成的来源摘要；新的成像任务应根据当次输入重新建立方向。

## 品牌标记

`assets/brand/siuyu-mark.svg` 以相叠的纸面和研究线条构成，用于 Skill 界面及项目介绍。

## 记录状态

视觉复查记录由主助手查看实际图片后填写。用户审美接受仍按真实反馈记录；包结构和文件校验各有独立证据。图片来源记录与发布许可分别管理，正式发布许可由作者指定。
