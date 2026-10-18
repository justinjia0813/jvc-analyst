# README 图示

这四张图对应 README 的具体说明，不包含项目数据或宣传口号。

| 图 | 用途 | 生成规格 | 可编辑文件 |
| --- | --- | --- | --- |
| [工作方式](how-it-works.png) | 问题、材料、AI 助手、检查和交付物的关系 | [JSON](specs/how-it-works.json) | [Excalidraw](how-it-works.excalidraw) |
| [推荐工作流](workflows.png) | 五条可独立选用的工作路径，以及访谈反馈 | [JSON](specs/workflows.json) | [Excalidraw](workflows.excalidraw) |
| [项目文件组织](project-files.png) | 原始材料、交付物和中间文件分别放在哪里 | [JSON](specs/project-files.json) | [Excalidraw](project-files.excalidraw) |
| [投决预审与终版](ic-review.png) | 严格审查、用户批准、保真校验和返工条件 | [JSON](specs/ic-review.json) | [Excalidraw](ic-review.excalidraw) |

README 嵌入 PNG，点击可查看同名 SVG。SVG 内嵌字体，PNG 不依赖浏览器字体或在线图表服务。正文和图片替代文本保留完整含义。

## 修改与重新生成

生成工具为 Archscribe，使用浅色 `paper` 风格和静态输出。`specs/*.json` 是生成来源；修改流程时先更新规格。Excalidraw 文件可用于手工编辑，但重新生成会覆盖同名导出。

安装 Archscribe 后，将 `ARCHSCRIBE_ROOT` 设置为它的目录。在本仓库根目录执行，例如：

```bash
python3 "$ARCHSCRIBE_ROOT/scripts/render_animated_diagram.py" \
  --spec assets/readme/specs/workflows.json \
  --outdir assets/readme --basename workflows \
  --formats png,svg,excalidraw --renderer browser --check --strict-formats
```

逐张检查中文断行、文字大小、箭头与卡片是否重叠、返工方向是否正确。然后在 README 中检查图片加载和点击链接。SVG 另保留以文件名为前缀的 `title`、`desc` 和 `aria-labelledby`，供辅助阅读工具使用。

## 字体与图标许可

SVG 内嵌的 Excalifont 和 Noto Sans SC 字体使用 SIL Open Font License，线条图标来自 MIT 许可的 Tabler 子集。对应版权与许可保留在 [licenses](licenses/) 中。
