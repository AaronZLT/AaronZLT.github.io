```text
AaronZLT.github.io/
├── .github/workflows/
│   └── pages.yml        自动构建与手动发布
├── assets/              头像与微信二维码
├── content/             网站文字与列表
├── site.json            网站地址与搜索引擎元数据
├── templates/
│   ├── page.html        页面结构与栏目顺序
│   ├── header.html      顶部导航
│   ├── sidebar.html     个人资料侧栏
│   ├── footer.html      页脚
│   ├── sections/        栏目模板
│   └── items/           重复条目模板
├── styles/              按用途拆分的 CSS
├── scripts/
│   ├── build.py         静态构建
│   └── preview.py       刷新时自动构建的本机预览
└── dist/                静态页面输出
```

本地预览：

```bash
python3 scripts/preview.py
```

打开 http://127.0.0.1:4173/ 。修改内容、模板或样式后，刷新页面即可重新构建。

静态构建：

```bash
python3 scripts/build.py
```

内容按页面区域分别维护：

| 文件 | 展示内容 |
| --- | --- |
| `content/profile.json` | 侧栏头像、姓名、身份、学校、研究方向 |
| `content/about.json` | 简介与四个联系方式 |
| `content/publications.json` | 论文标题、作者、发表信息 |
| `content/education.json` | 教育经历 |
| `content/experience.json` | 工作与实习经历 |
| `content/services.json` | 审稿与助教经历 |

简介与经历描述中的链接使用 `[文字](https://...)` 格式。

构建输出包含主页、样式、图片、`robots.txt`、`sitemap.xml` 和 Google 站点验证文件。正式主页地址由 `site.json` 中的 `url` 统一配置，用于 canonical、Open Graph、人物结构化数据和站点地图。

发布使用 `.github/workflows/pages.yml`：push 到 `main` 只构建，手动运行 `Build and deploy GitHub Pages` 才会部署。

搜索引擎配置：

1. 部署后，在 [Bing Webmaster Tools](https://www.bing.com/webmasters/) 和 [Google Search Console](https://search.google.com/search-console/) 分别验证 `https://aaronzlt.github.io/`。Google 验证文件已随构建保留。
2. 在两个后台提交 `https://aaronzlt.github.io/sitemap.xml`，并使用 URL 检查工具检查主页，按后台结果请求抓取或索引。
3. 在 GitHub、Google Scholar、LinkedIn 和学校个人资料中使用一致的姓名 Longteng Zhang，并链接到正式主页。

站点地图帮助发现页面；具体收录原因以站长后台为准，收录与排名由搜索引擎决定。参考 [Bing 索引说明](https://www.bing.com/webmasters/help/why-is-my-site-not-in-the-index-2141dfab) 和 [Google 搜索指南](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)。
