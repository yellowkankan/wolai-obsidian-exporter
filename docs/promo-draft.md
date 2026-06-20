# GitHub / Social Promo Draft

## 中文

最近在把以前沉淀在 Wolai 里的知识库迁到 Obsidian，顺手做了一个小工具：Wolai Obsidian Exporter。

它不是只导出文字，而是会把页面 Markdown、原始 JSON、图片、文件、视频和音频一起镜像到本地。

我遇到的核心问题是：Wolai 里的媒体链接是临时签名 URL，会过期。所以这个工具会在下载附件前重新读取 block，拿到最新 download_url，再立刻保存到本地，并把 Markdown 链接改成本地相对路径。

适合想把 Wolai 资料做成本地长期归档、再放进 Obsidian 搜索和整理的人。

Repo: https://github.com/yellowkankan/wolai-obsidian-exporter

## English

I built Wolai Obsidian Exporter while moving an old Wolai knowledge base into Obsidian.

The tricky part was not text export. It was preserving the actual assets: screenshots, files, videos, and audio. Wolai media URLs are signed and can expire quickly, so the exporter refreshes each media block before downloading it locally.

The result is a local archive with Markdown, raw JSON, assets, resume state, and reports.

Repo: https://github.com/yellowkankan/wolai-obsidian-exporter
