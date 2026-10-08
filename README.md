# Longteng Zhang

个人学术站点，使用 Python 3 标准库生成静态 HTML 和 CSS。

## 本机预览

在仓库根目录运行：

```sh
python3 scripts/preview.py
```

打开 <http://127.0.0.1:4173/>。修改内容、模板或样式后，刷新页面会重新构建并显示修改。按 `Ctrl+C` 停止预览。

## 编辑内容

| 文件 | 内容 |
| --- | --- |
| `content/profile.json` | 姓名、邮箱、个人卡片、首页标题与按钮、Bio、导航、联系方式与页面元信息 |
| `content/experience.json` | 教育与研究工作经历 |
| `content/research.json` | 研究定位、三个研究方向、协同设计方法、证据与来源 |
| `content/publications.json` | 论文标题、作者和发表信息 |
| `content/service.json` | 审稿与教学服务 |

内容填写普通文字，构建脚本会转义 HTML 特殊字符。首页标题中的 `emphasis: true` 表示使用斜体强调。

`profile.json` 中的 `hero.scholar` 保存 Google Scholar 按钮的文字和链接。

底部联系方式中的 `contact.linkedin` 保存领英链接，`contact.wechat` 保存微信二维码路径、替代文字和提示。替换 `assets/wechat.jpg` 即可更新二维码。微信图标悬停或聚焦时，在上方显示完整图片。

教育与工作经历的 `description` 可以填写一段文字，也可以用文字与链接组成的数组：

```json
"description": [
  "Supervisors: ",
  {"text": "Prof. Xiaowen Chu", "url": "https://sites.google.com/view/chuxiaowen/home"},
  " and ",
  {"text": "Prof. Qiong Luo", "url": "https://cse.hkust.edu.hk/~luo/"}
]
```

添加论文时，在 `publications.json` 数组中增加一条记录：

```json
{
  "title": "Paper title",
  "authors": ["A. Author", "L. Zhang", "B. Author"],
  "author_position": 2,
  "venue": "Conference, 2026"
}
```

`author_position` 从 1 开始，表示需要加粗的作者位置。同名作者也按位置区分。记录顺序就是页面顺序。

### 编辑成本图表

`content/research.json` 中的 `evidence` 保存图表和服务时间线：

- `operating_costs`：每月请求量、每次输入与输出 token 数，以及模型的每百万 token 价格。构建脚本根据这些值计算月度 API 账单和柱长。
- `charts`：价格变化图；`metrics.rows` 保存名称与数值，`max` 控制从零开始的坐标范围。`tone` 使用 `reference`（浅紫）或 `efficient`（绿）。
- `timeline.years`：按年份组织的服务事件、日期与来源。
- `performance_context`：辅助性能背景；`limitations`：图表的统计口径。

每张图的日期、说明和来源也保存在对应对象中。图表由 HTML/CSS 绘制，模板位于 `templates/items/chart-*.html` 和 `cost-chart.html`。

## 编辑布局和样式

`templates/page.html` 控制整体页面与栏目顺序。调整 `$about`、`$research` 等占位符的位置即可调整对应栏目；移除占位符即可隐藏该栏目。隐藏有导航链接的栏目时，同步移除 `content/profile.json` 中对应的 `navigation` 条目。

`templates/sections/` 中每个 HTML 文件对应一个栏目。`templates/items/` 控制论文、时间线条目、研究卡片等重复元素的布局。模板使用 Python 标准库 `string.Template` 的 `$变量名` 占位符。

| 文件 | 用途 |
| --- | --- |
| `styles/theme.css` | 灰白、绿色与浅紫色主题，字体与颜色变量；强调色也用于页面图标 |
| `styles/base.css` | 正文、标题、链接等基础样式 |
| `styles/layout.css` | 导航、栏目、网格及页脚布局 |
| `styles/components.css` | 个人卡片、按钮、论文、时间线和证据区域 |
| `styles/responsive.css` | 平板、手机与减少动态效果的样式 |

## 生成静态文件

```sh
python3 scripts/build.py
```

输出为 `dist/index.html`、`dist/assets/style.css` 和微信二维码图片。`dist/` 是构建产物，内容修改应在上面的源码文件中进行。构建与预览命令只操作本机文件。

## GitHub Pages 部署

仓库：[AaronZLT/AaronZLT.github.io](https://github.com/AaronZLT/AaronZLT.github.io)。部署后的地址为 <https://aaronzlt.github.io/>。

推送到 `main` 会自动构建网站并保存部署产物。发布使用手动入口：

1. 在仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。
2. 打开 **Actions → Build and deploy GitHub Pages → Run workflow**，选择 `main` 并运行。

工作流使用 Python 3.13 构建，只部署 `dist/`。本机参考资料保存在 `.local/`，构建产物和本机资料不进入 Git 提交。

```text
AaronZLT.github.io/
├── .github/workflows/
│   └── pages.yml        自动构建与手动发布
├── assets/              微信二维码图片源码
├── content/             网站文字与列表
├── templates/
│   ├── page.html        页面结构与栏目顺序
│   ├── header.html      顶部导航
│   ├── footer.html      页脚
│   ├── sections/        栏目模板
│   └── items/           重复条目模板
├── styles/              按用途拆分的 CSS
├── scripts/
│   ├── build.py         静态构建
│   └── preview.py       刷新时自动构建的本机预览
└── dist/                静态页面输出
```
