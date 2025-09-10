#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

# 设置日志文件名
LOG_DATE=$(date +%F)
MAIN_LOG="logs/daily-${LOG_DATE}.log"
PRICE_LOG="logs/price-${LOG_DATE}.log"

echo "=== 开始每日数据更新流程 $(date) ===" | tee -a "$MAIN_LOG"

# 1. 下载最新价格数据（与新闻时间匹配）
echo "步骤 1: 更新价格数据..." | tee -a "$MAIN_LOG"
python src/download_prices.py --debug 2>&1 | tee -a "$PRICE_LOG"

if [ $? -ne 0 ]; then
    echo "ERROR: 价格数据下载失败" | tee -a "$MAIN_LOG"
    exit 1
fi

# 2. 下载新闻数据
echo "步骤 2: 下载新闻数据..." | tee -a "$MAIN_LOG"
python src/data_pipe.py --universe-file "data/universe/hstech_current_constituents.csv" --recent_pages 2 --token_cap 120 --debug --logfile "$MAIN_LOG"

if [ $? -ne 0 ]; then
    echo "ERROR: 新闻数据下载失败" | tee -a "$MAIN_LOG"
    exit 1
fi

# 3. 数据清洗
echo "步骤 3: 清洗新闻数据..." | tee -a "$MAIN_LOG"
python src/clean_data.py --input-file "news_out/articles_recent.jsonl" --output-file "data/processed/articles_recent_cleaned.csv" 2>&1 | tee -a "$MAIN_LOG"

# 4. 情感分析
echo "步骤 4: 情感分析..." | tee -a "$MAIN_LOG"
python src/sentiment_top.py --input-file "data/processed/articles_recent_cleaned.csv" --output-file "data/processed/articles_with_sentiment.csv" 2>&1 | tee -a "$MAIN_LOG"

# 5. 因子生成和评估
echo "步骤 5: 生成因子并评估..." | tee -a "$MAIN_LOG"
python src/pipeline.py 2>&1 | tee -a "$MAIN_LOG"

# 6. 输出运行摘要
echo "步骤 6: 生成运行摘要..." | tee -a "$MAIN_LOG"
python - <<'PY' 2>&1 | tee -a "$MAIN_LOG"
import pandas as pd
import os
from datetime import datetime

try:
    # 检查新闻数据
    if os.path.exists("news_out/run_metrics.csv"):
        news_metrics = pd.read_csv("news_out/run_metrics.csv").tail(1).to_dict(orient="records")[0]
        print(f"新闻数据: {news_metrics}")
    
    # 检查价格数据
    if os.path.exists("data/prices.csv"):
        prices = pd.read_csv("data/prices.csv")
        latest_price_date = prices['date'].max()
        price_count = len(prices)
        unique_stocks = prices['code'].nunique()
        print(f"价格数据: {price_count} 条记录, {unique_stocks} 只股票, 最新日期: {latest_price_date}")
    
    # 检查因子数据
    if os.path.exists("data/processed/daily_sentiment_factors.csv"):
        factors = pd.read_csv("data/processed/daily_sentiment_factors.csv")
        latest_factor_date = factors['date'].max()
        factor_count = len(factors)
        print(f"因子数据: {factor_count} 条记录, 最新日期: {latest_factor_date}")
    
    # 检查IC结果
    if os.path.exists("data/processed/ic_results.csv"):
        ic_results = pd.read_csv("data/processed/ic_results.csv")
        if not ic_results.empty:
            latest_ic = ic_results.tail(1)
            print(f"最新IC: 日期={latest_ic['date'].iloc[0]}, IC={latest_ic['IC'].iloc[0]:.4f}, RankIC={latest_ic['RankIC'].iloc[0]:.4f}")
    
    print(f"\n=== 每日更新完成 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
except Exception as e:
    print(f"生成摘要时出错: {e}")
PY

echo "每日数据更新流程完成！详细日志请查看: $MAIN_LOG" | tee -a "$MAIN_LOG"
