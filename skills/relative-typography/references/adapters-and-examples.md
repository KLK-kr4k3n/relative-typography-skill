# 媒介映射与计算示例

## 同一模型，三种不同输入

下列数字都是演算样例，不是推荐的绝对字号。页面宽、有效内容宽与正文基准应分别记录。

|示例|阅读基准 B|标题容器 Cₜ|Cₜ/B|profile|主标题 R|结果|
|---|---:|---:|---:|---|---:|---|
|工具界面窄栏|由现有正文 token 确定|24B|24|compact|1.443|1.443B|
|中英文章|由用户阅读偏好确定|36B|36|editorial|2.200|2.200B|
|展板近读区|假设现场样张校准为 5 mm em|200 mm|40|display|2.800|14 mm em|

第三例中的 5 mm 是假设已有的校准结果，不是建议所有展板使用该字号。实际可见字形高度还受字体字面影响。字号输出 14 mm 不等于所有字形外接框高 14 mm。

标题拟合例：`Cₜ/B=24`，目标字号下测得标题在 B 时总 advance 为 `A=30em`，允许两行，则 `R_fit≈2×24/30=1.6`。balanced 默认容量映射得 1.685，需要低于其下限 1.65 才可能装下。应先扩宽或允许更多行，不在没有说明的情况下缩成 1.6。即使总字宽可装，词边界仍可能使实际排版需要更多行。

## Web：把 B 留在根字号体系内

以下是 `balanced、Cₜ/B=40` 的静态 token 例，对应标题比例 1.825。尺寸单位只在适配器中出现；模型保持无单位比例。实际响应式页面应依据自己的容器测量/布局模式调整标题比例，不能把这个固定示例冒充完整流体排版方案。

```css
html { font-size: 100%; }

.page {
  --body: 1rem;
  --r-title: 1.825;
  --r-section: 1.41;
  --r-caption: 0.82;
  font-family: system-ui, "PingFang SC", "Noto Sans CJK SC", sans-serif;
  font-size: var(--body);
  line-height: 1.6;
  font-optical-sizing: auto;
  padding: 1.5em;
}

.reading {
  max-inline-size: 36em; /* body em；中文栏宽初始样例 */
  min-inline-size: 0;
}

.page h1 {
  font-size: calc(var(--body) * var(--r-title));
  font-weight: 600;
  line-height: 1.2;
  margin-block: 0 0.65em;
}

.page h2 {
  font-size: calc(var(--body) * var(--r-section));
  font-weight: 600;
  line-height: 1.3;
  margin-block: 1.5em 0.6em;
}

.caption {
  font-size: calc(var(--body) * var(--r-caption));
  line-height: 1.5;
}

.actions { display: flex; flex-wrap: wrap; gap: 0.75em; }
button, input, select, textarea { font: inherit; }
button { padding: 0.55em 0.9em; }
```

保持语义化 HTML。字体栈只是示例，目标地区为繁体或香港时调整字体与 `lang`；不把 SC 字体用于所有中文地区。英文阅读块可以改栏宽和行高，需用实际文本验证。不要插入大段手工空格来模拟中英间距。

若采用 `clamp()` 或容器单位，保留可随用户字号增长的相对下限和上限；检查浏览器 zoom、文本放大与容器变窄的共同作用。仅有 `rem` 或 `clamp` 并不能证明满足放大要求。禁止用 transform 缩放整个页面以“适配”。

## Figma：以目标 frame 为页面

在已有文件中，先检查 text styles 与 variables。把 frame 的目标媒介、预期阅读缩放、B 与比例写入说明；再落成 `type/body`、`type/section`、`type/title` 等角色样式，字重用字体实际可用的命名，行高确认使用百分比还是绝对值。

同一 profile 可使用诸如 Compact / Balanced / Editorial / Display 的变量模式或样式组，前提是当前工具和库结构支持。不是必须创建一套新库；现有组件与 token 有优先权。使用任何 Figma 写入工具时，遵循对应工具的操作要求。

设计阶段的 frame 坐标只是逻辑坐标；它们如何对应 CSS 像素、导出尺寸或印刷单位，需要目标媒介的映射约定。不要根据设计师当前把画布缩放到 25% 就放大 frame 内文字。无限画布的 frame 外标题和产品 UI 文字是两个层面，应分别确定阅读任务。

应用 Auto Layout/文本自适应高度，并在最窄 frame、长文本、放大版本检查裁切。若仅创建了归一化规格，说明尚未写入 Figma，也没有完成 Figma 渲染验证。

## 展板、海报与演示页

先明确物理/显示尺寸、预计观看距离、字号校准依据、近读/远读任务。若只有“1920×1080”而没有实际显示与距离，无法由像素判断最后可读性；可以先选 display 并输出相对方案。

近读区放解释正文，远读区放标题、主图与必要结论。需要两个 B 时，明确 `B_near` 与 `B_far` 的依据和对应角色，不逐段任意缩放。远读正文无法舒适容纳时，优先减少密度、增加版面或将细节移至近读区；修改原文内容须在用户授权范围内。

印刷最终换算：`1 pt = 25.4/72 mm`。这是排印点单位换算，不用于把 Apple 平台逻辑 pt 直接当作印刷实物尺寸。导出后检查实际物理尺寸并打样；演示页在预期设备和距离下检查，不以编辑器预览代替观看验证。

## 计算器

在仓库根目录运行：

```bash
python3 skills/relative-typography/scripts/type_scale.py --profile compact --width-b 24
python3 skills/relative-typography/scripts/type_scale.py --profile editorial --language mixed --width-b 36
python3 skills/relative-typography/scripts/type_scale.py --profile display --width-b 40 --body-value 5 --unit mm
python3 skills/relative-typography/scripts/type_scale.py --profile balanced --width-b 24 --title-advance-em 30 --title-lines 2
```

可选 `--title-width-b` 单独指定标题区宽度。`--minimum-ratio` 可抬升过小文字到已校准的下限；必须 `0<下限≤1`，若正文也不够大，应先重新校准 B。`--body-value` 与 `--unit` 同时提供，仅用于把关系求值到项目自己的单位。

计算器只实现 K=1 的名义比例和初始行高，不加载字体，也不替你测标题。`--title-advance-em` 必须来自目标标题字体和字重的测量，不能直接填字符数。拟合状态为估算；所有输出都要经过实际排版。原生 Apple App 应使用相应平台语义样式/缩放能力，不用本包固定比值替代系统 Dynamic Type。

## 交付记录样式

```text
媒介与任务：中英文章网页，优先连续阅读
B 的依据：沿用已有 body token，尊重用户根字号
几何：正文 C=36B；标题 Cₜ=36B；不按全页 W 缩放文字
profile：editorial；title=2.2B；section=1.65B；body=1B
字重：正文 Regular；标题 Medium；分区 Semibold（按实际字体映射）
语言：中文/英文同语义层级，K 初始为 1，分别检查字面与行高
适应策略：变窄保持 B，标题可到区间低端，布局堆叠
验证：写明实际检查的渲染、字体与宽度；未执行的检查列为未验证
```
