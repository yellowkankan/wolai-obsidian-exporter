# wolai-obsidian-exporter 项目规则

## 项目定位

这是一个本地优先的 Wolai → Obsidian 导出工具。目标是把 Wolai 页面、原始 JSON、图片、文件、视频、音频导出到本地 Obsidian 友好的目录结构。

## 安全规则

- 不把真实 token、Authorization、Bearer、cookie、session、auth_key、download_url 写入仓库。
- 不提交真实 wolai 页面内容、真实 page_id、真实 block_id 或真实附件 URL。
- `.env`、`exports/`、`.wolai-export-state/`、真实配置文件必须被 gitignore。
- 测试 fixture 必须是人工构造或脱敏样例。
- 发布 GitHub、push、创建 release 前必须再次得到用户明确确认。

## 开发规则

- 使用 Python 3.9+。
- CLI 入口为 `wolai-obsidian-export`。
- token 只从环境变量 `WOLAI_TOKEN` 或用户本地未提交配置读取。
- 所有批量任务必须支持断点续跑。
- 附件下载前必须重新获取 block，不能依赖旧 JSON 里的过期 `download_url`。
- stdout 不输出完整下载 URL 或密钥相关内容。
- 导出失败不能中断整个任务，应写入 failures 报告。

## 验证命令

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
python scripts/check_no_secrets.py
```
