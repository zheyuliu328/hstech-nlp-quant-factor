# Real Data Guide

## 真实数据接入路径

### 支持的数据格式

新闻 CSV，必须包含以下字段：

| 字段名 | 类型 | 说明 |
|:-------|:-----|:-----|
| date | string | 日期 (YYYY-MM-DD) |
| headline | string | 新闻标题 |
| stock_code | string | 股票代码 (e.g., 0001.HK) |

### 快速开始

```bash
# 运行因子构建
make run-real CSV=path/to/news.csv

# 仅验证
python scripts/run_real.py path/to/news.csv --validate-only
```

### 示例 CSV

```csv
date,headline,stock_code
2024-01-15,Company reports strong profit growth,0001.HK
2024-01-16,Market faces unexpected losses,0002.HK
```

### API Key 配置（可选）

如需实时获取新闻，设置环境变量：
```bash
export ER_API_KEY=your_key_here
```

无 API key 时，系统使用本地 CSV 文件，不阻断离线运行。

### 输出工件

- `reports/factor_report_{run_id}.json` - 因子构建报告
- `reports/daily_factors_{run_id}.csv` - 日度情绪因子
