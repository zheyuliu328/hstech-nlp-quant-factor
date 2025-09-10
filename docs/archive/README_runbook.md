# News Ingestion Quickstart

## 1) Install
```bash
pip install eventregistry pandas python-dateutil
```

## 2) Set API key (不要把 Key 发给任何人)
```bash
export ER_API_KEY="YOUR_API_KEY"
```

## 3) Run examples
近 30 天拉 2 页（每页最多 100 篇），两只股票：
```bash
python data_pipe.py --symbols 0700.HK 9988.HK --recent_pages 2
```

历史 2024 和 2023 年，每年拉 2 页 + 近 30 天拉 1 页：
```bash
python data_pipe.py --symbols 0700.HK 9988.HK --years 2024 2023 --archive_pages 2 --recent_pages 1
```

关键词自由组合：
```bash
python data_pipe.py --keywords "Tencent OR 0700.HK" --years 2023 2022 --archive_pages 3
```

## 4) Outputs
- `news_out/articles_recent.jsonl` / `articles_archive.jsonl`
- `news_out/articles_recent.csv` / `articles_archive.csv`
- `news_out/checkpoint.json` / `seen_uris.jsonl`

## 5) Token 估算（规则简表）
- 近 30 天 Article 搜索：**1 token/页**（<=100 文章/页）
- 历史 Article 搜索：**5 tokens/年/页**
每翻一页都是一次搜索动作。脚本会打印粗略估算，方便你把控。
- 更新：已加入 run_metrics / token_cap / retries / smoke / pytest
