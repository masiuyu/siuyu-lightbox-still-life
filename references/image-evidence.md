# 原生图片与评审的对应证据

用于已经保存原生图片、实际 imagegen 调用参数和评审的任务，尤其是多版本比较、局部修正与材料近景。方向准备继续使用原两段自然语言接口；实际生成后的文件可用下面的命令连接起来。

## 留存这一次实际对应

先查看本轮原生图和核心观察，确认选中了正确版本。准备实际编译目录、真实调用参数 JSON、原生图片与 review.md。参数文件可以是原始参数对象，也可以是包含 `arguments` 的调用记录；当前命令核对 imagegen 的 `prompt` 与本地 `referenced_image_paths`。

```bash
python3 <skill-dir>/scripts/lightbox.py evidence /path/to/compiled \
  --call /path/to/tool-call.json \
  --image /path/to/image.png \
  --review /path/to/review.md \
  --output /path/to/new-evidence.json

python3 <skill-dir>/scripts/lightbox.py check-evidence /path/to/new-evidence.json
```

`evidence` 先检查原编译包，再比较保存的调用提示词与参考顺序，解码原生图片，读取四列评审，并记录相关文件的位置、大小与 SHA256。选择新的输出文件，已有收据会保留。`check-evidence` 按该收据重查文件与对应关系，指出留存后的替换或修改。

这两项图片证据命令需要带 Pillow 的 Python 环境；compile、check、review 继续使用标准库。当前命令只核对本地文件参考；采用会话图片或其他服务时，按实际接口建立对应记录。

## 把原生裁区连回全图

已有裁区时，可添加 `--detail-index /path/to/native-detail-index.json`。索引沿用当前案例的普通 JSON 列表，每项说明 `source`、`path` 和 `box_xyxy_half_open`；路径可相对索引文件。坐标是原生整数、左上包含、右下不包含，例如 `[100, 80, 260, 200]` 对应 160×120 像素。已有 `size`、`sha256` 时一起核对。

命令只检查 `source` 指向本张原生图的条目，其他来源条目单独计数。每份裁区按坐标提取原生区域，比较模式、尺寸及像素；PNG 压缩方式可以不同，重采样、滤镜或像素改动会使比较失败。至少有一份本图裁区才构成这次裁区检查。

独立生成的近景按自己的原生图建立记录，提供另一张材料模拟的证据。同一全图的原生细节则应能逐像素连回该图。

可补充 `--execution /path/to/execution.md` 或已有 execution.json。普通说明作为附件留存；已有 JSON 含 `workspace_copy` 时，核对它记录的图片路径与 SHA256，以及已提供的尺寸、字节数和评审路径；调用开始时间与标准视觉汇总已记录时也应相符。原始工具输出仍可访问时，一起比较原始文件与项目副本，记录哪些检查实际执行。附件内容由执行者按真实调用填写，生成真实性继续使用对应工具证据。

## 文件核对与视觉判断分别使用

收据保存的是本次选定文件的对应状态。它能发现后续文件变化、调用与编译不一致，以及错误的原生裁区。首次选择的评审是否确实描述这张图、调用记录是否来自真实工具、图片是否完成创作目标，继续由实际工具证据和看图确认。

例如，织物评审记录仍为 REVISE，文件和裁区即使全部一致，也继续保持该视觉状态。相反，一张通过的原生图拥有可核对文件，也只证明相应任务范围。用户接受根据用户的实际反馈记录。

本地路径属于这份快照。文件迁移或新版本编辑后，保留旧收据，再针对实际新位置和本轮评审建立新记录。按 [实物验收](physical-realism.md) 判断效果，按 [创作调用](creative-orchestration.md) 选择下一步修正。
