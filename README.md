# Relative Typography · 中英相对排版 Skill

以 Apple Typography 为研究起点，为模型自动编排网页 UI、Figma frame、文章、演示页、海报与展板建立可复用的中英文字号、字重与页面关系。

核心关系是 **文字字号 = 阅读基准 B × 语义比例 R × 字体光学校准 K**。页面通过 `内容宽度/B` 和 `标题宽度/B` 参与布局；文字不直接跟随整个画布宽度无限缩放。

这套 skill 复用 Apple 的语义层级、字重与动态布局思路，并提出跨媒介映射方法。四类比例、行高区间和容量阈值均为本项目的可调启发式，不是 Apple 官方通用规范，也不声称经过人因实验验证。

## 阅读与使用

- [SKILL.md](skills/relative-typography/SKILL.md)：模型的入口与执行规则。
- [研究与来源](skills/relative-typography/references/research.md)：Apple 原始数据、比值推导、中英分析、证据边界；核验于 2026-10-17。
- [版式规则](skills/relative-typography/references/layout-rules.md)：字重、字面、行高、栏宽、密度与空间的联动。
- [媒介映射与示例](skills/relative-typography/references/adapters-and-examples.md)：Web、Figma、展板与计算器用法。

安装时，将 `skills/relative-typography/` 整个文件夹复制到你的技能目录，例如 `~/.codex/skills/relative-typography/`。在支持该技能目录的工具中调用：

```text
使用 $relative-typography，为这个中英双语页面建立相对字号、字重和留白体系。
先说明正文基准、标题/正文栏宽与阅读情境，再实现并验证布局。
```

仓库不依赖 Figma 或 Apple 专有工具；实际写入设计文件、网页或其他媒介时，使用目标环境已有工具。不会自动安装字体、修改全局配置或授权对外发布。

## 层级示意

均以当前阅读正文 `B=1` 为单位。标题区间随局部标题容量取值；caption 是用途标签，仍须遵守实际可读下限。

|角色|操作密集 compact|通用 balanced|阅读 editorial|展示 display|
|---|---:|---:|---:|---:|
|正文|1.00|1.00|1.00|1.00|
|分区标题|1.29|1.41|1.65|2.00|
|页面主标题|1.42–1.65|1.65–2.00|2.00–2.50|2.40–3.20|
|展示标题|1.80–2.00|2.20–2.80|2.80–3.50|3.20–4.50|

同等重要的中英文共享语义层级；从 K=1 开始，按具体字体对校准。不存在“中文永远乘 1.1”这样的固定规则。展板按距离与实体样张校准 B；Figma 以目标 frame 与目标成品阅读状态确定 B。

## 可直接运行的比例计算器

Python 3.9+，仅标准库；在仓库根目录运行：

```bash
python3 skills/relative-typography/scripts/type_scale.py --profile editorial --language mixed --width-b 36
python3 skills/relative-typography/scripts/type_scale.py --profile display --width-b 40 --body-value 5 --unit mm
```

输出 JSON tokens，保留比例、字重意图和相对行高。第二条的 5 mm 只是演算锚点，不是展板字号建议。脚本没有字体测量、自动断行或可读性判断；不支持以计算结果代替实际渲染。

## 验证

```bash
python3 -m unittest discover -s tests -v
```

覆盖比例缩放、局部容器映射、标题增长上限、正文保持、标题装不下的重排提示与非法输入。Skill frontmatter 另用 skill-creator 的校验器检查。这些检查验证计算逻辑与包结构；具体成品仍须在目标媒介中验证。

## License

本项目原创内容与代码使用 [MIT License](LICENSE)。Apple/W3C 的外部文档、商标与任何第三方字体保留各自权利；本仓库不包含字体文件或完整规范副本。
