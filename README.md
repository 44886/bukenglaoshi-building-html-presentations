# bukenglaoshi-building-html-presentations

一个用于创建和编辑 HTML 单文件演示文稿的 Codex Skill。它会根据受众、场景、讲述节奏和拍照需求选择视觉方向，而不是把所有内容套进同一种模板。

生成的演示文稿是可离线打开的单个 `.html` 文件，支持翻页笔、键盘、触摸、分步叙事、图表、时间轴、图片与打印布局。

## 主要能力

- 13 种视觉方向，涵盖编辑叙事、信息设计、教育表达、技术系统、产品演示和发布会风格。
- 发布会风格只是可选方向，不是默认模板。
- 支持 PageUp、PageDown、方向键以及常见翻页笔映射。
- 页面内部步骤优先于整页切换，并支持反向撤回和返回状态恢复。
- 图片、字体、ECharts 和本地媒体均可嵌入最终 HTML。
- 使用稳定的 Slide ID，适合持续增删、调序和局部修改。
- 自带构建器、离线验证器、单元测试和 Playwright 浏览器测试。

## 安装

在 Codex 中直接输入：

```text
请安装这个 GitHub Skill：
https://github.com/44886/bukenglaoshi-building-html-presentations
```

也可以手动克隆到 Codex Skills 目录：

```powershell
git clone https://github.com/44886/bukenglaoshi-building-html-presentations.git `
  "$env:USERPROFILE\.codex\skills\bukenglaoshi-building-html-presentations"
```

安装后，在新任务中调用：

```text
使用 $bukenglaoshi-building-html-presentations，把下面的逐页内容制作成 HTML 单文件演示文稿……
```

## 工作方式

Skill 会先判断：

1. 演示目的、受众和使用环境。
2. 是否由演讲者控制、是否需要家长或观众拍照留存。
3. 每页承担的是封面、观点、证据、时间轴、比较、流程、参考页、图库还是结论。
4. 哪些内容确实需要分步，哪些内容应该一屏完整展示。
5. 哪一种视觉家族最适合内容。

未指定风格时，Skill 会给出三个明显不同的候选方向。Apple/Xiaomi 式发布会风格只有在用户明确选择或场景确实匹配时才会启用。

## 构建格式

演示内容使用 UTF-8 JSON 保存，并通过构建器生成单文件 HTML：

```powershell
python scripts/build_presentation.py deck.json --out presentation.html
python scripts/validate_deck.py presentation.html
```

本地素材在 JSON 中使用 `asset:` 相对路径，例如：

```html
<img src="asset:media/cover.jpg" alt="演示封面">
```

构建时会自动转成 Data URI，因此最终只需交付一个 HTML 文件。

## 开发与测试

```powershell
python -m unittest discover -s tests -v
cd tests/browser
npm install
npm test
```

浏览器测试覆盖翻页笔按键、内部步骤、反向导航、返回页几何稳定、时间轴、图表、窄屏、离线资源和 reduced motion。

## 目录

- `SKILL.md`：Skill 入口和强制规则。
- `references/`：内容架构、风格目录、组件、发布会专项和 JSON 规范。
- `assets/`：HTML 运行时模板及本地 ECharts。
- `scripts/`：构建与验证脚本。
- `examples/`：示例 deck。
- `tests/`：单元和浏览器测试。

## License

项目代码使用 [Apache License 2.0](LICENSE)。内置 Apache ECharts 保留其原始许可证及第三方组件声明。
