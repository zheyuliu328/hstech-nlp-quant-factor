
# NLP量化因子分析系统

## What this repo ships
- **News-Sentiment Alpha for HSTECH**: prescored RoBERTa pipeline, IC/Rank-IC and decile backtest, style correlation
- **3-Figure Pack**: IC timeseries, decile backtest, correlation heatmap vs Momentum/Size/Value
- **Universe-driven batch mode**: 10 HSTECH names with token-cap, logging, and dry-run

## Known limitations
- Single-source headlines, no industry/size neutralization, fee-agnostic backtest
- Pilot sample: 10 names × 1 month, target ≥ +0.05 IC after neutralization

## 系统概述
基于新闻情感分析的量化因子研究系统，使用RoBERTa模型进行情感分析，支持股票池过滤和因子回测。

## 核心功能
- **新闻数据抓取**: Event Registry API集成
- **数据清洗**: HTML标签清理、语言检测、去重
- **情感分析**: RoBERTa模型 + L&M词典备选
- **因子构建**: 日度聚合、横截面标准化
- **回测评估**: IC分析、分层回测、图表生成

## 数据合约 (Data Contract)
- **Universe**: 10 HSTECH names (see `data/universe/hstech_current_constituents.csv`)
- **News**: 清洗后的新闻数据 (`data/processed/articles_recent_cleaned.csv`)
- **Sentiment**: RoBERTa情感分数 (`data/processed/articles_with_sentiment.csv`)
- **Prices**: 股票价格数据 (`data/prices.csv`)

## 快速开始

### 1) 环境设置
```bash
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -U pip
pip install -r requirements.txt
```

### 2) 配置环境变量
```
ER_API_KEY=YOUR_KEY
```

### 3) 运行完整pipeline
```bash
# 一键运行完整分析
./run.sh
```

### 4) 输出结果
- `reports/ic_daily.csv` - 日度IC数据
- `reports/ic_monthly.csv` - 月度IC统计
- `reports/figs/ic_timeseries.png` - 图1: IC时序图
- `reports/figs/deciles.png` - 图2: 分层回测图
- `reports/figs/corr_heatmap.png` - 图3: 相关性热力图
- `reports/factor_style_correlation.csv` - 风格相关性数据

## 评估指标
- **Metrics**: IC / Rank-IC on 1D forward excess (fee-agnostic)
- **Backtest**: Q1–Q5 等权、日频调仓、无费率（脚注说明将做 10–30 bps 敏感性）
- **Figure 3**: pooled cross-sectional correlation vs Momentum(5D)、Size(log mcap)、Value(1/price)
- **Proxies**: Momentum = past 5D return (t-5→t-1), Size = log(market cap), Value = 1/price（占位，后续替换为 E/P、B/P）
- **Limitations**: 单源新闻，未做中性化

## 模块说明
- `sentiment.py` - RoBERTa情感分析
- `src/pipeline.py` - 主pipeline
- `src/factors.py` - 因子构建
- `src/eval.py` - 评估指标
- `src/backtest/vectorized.py` - 回测模块
- `src/analysis/factor_corr.py` - 风格相关性分析

## 开发调试
- Run tasks: `Terminal → Run Task…` → pick a task (e.g., **Run: data_pipe recent**)
- Debug: `Run and Debug` panel → **Debug data_pipe (archive+recent)**

## 5) Optional: Dev Container
If teammates are on different OS or you want full reproducibility, open the folder in container:
- Install "Dev Containers" extension (Cursor works with VS Code extensions)
- `Ctrl/Cmd+Shift+P` → **Dev Containers: Reopen in Container**

## Notes
- On Windows replace Python path in `.vscode/tasks.json` with `.venv\\Scripts\\python.exe`
- Cursor uses the `.env` automatically when `envFile` is set in `launch.json`
- Keep `.venv/`, `.env/`, and generated outputs out of git (`.gitignore` included here)
