# GitHub / Social Promo Draft

## 中文

我做了一个本地优先的 Wolai → Obsidian 导出工具。

它可以把 Wolai 页面导出成 Markdown、原始 JSON，并把图片、文件、视频、音频下载到本地，支持断点续跑和失败报告。

一个关键处理是：资源下载前会重新获取 block 里的最新 download_url，因为 Wolai 的媒体链接会过期。

仓库：<发布后填写>

## English

I built a local-first CLI for exporting Wolai pages into an Obsidian-friendly folder.

It exports Markdown, raw JSON, and local assets, with resume support and safety reports.

The key detail: media URLs are refreshed right before download, because Wolai asset URLs can expire quickly.

Repo: <add after publishing>
