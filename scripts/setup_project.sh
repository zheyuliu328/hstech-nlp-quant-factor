#!/usr/bin/env bash
# setup_project.sh
# 项目初始化脚本 - 确保项目可以完全自动化运行

set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== 项目初始化开始 ==="

# 1. 检查并创建必要的目录
echo "步骤 1: 创建必要的目录..."
mkdir -p logs
mkdir -p data/processed
mkdir -p data/raw
mkdir -p reports/figs
mkdir -p news_out

# 2. 检查环境变量
echo "步骤 2: 检查环境配置..."
if [ -z "${ER_API_KEY:-}" ]; then
    echo "WARNING: ER_API_KEY 环境变量未设置"
    echo "请运行: export ER_API_KEY=你的API密钥"
    echo "或者创建 .env 文件"
fi

# 3. 检查虚拟环境
echo "步骤 3: 检查虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python -m venv .venv
fi

source .venv/bin/activate

# 4. 安装依赖
echo "步骤 4: 安装依赖..."
pip install -U pip
pip install -r requirements.txt

# 5. 检查股票池文件
echo "步骤 5: 检查股票池配置..."
UNIVERSE_FILE="data/universe/hstech_current_constituents.csv"
if [ ! -f "$UNIVERSE_FILE" ]; then
    echo "ERROR: 股票池文件不存在: $UNIVERSE_FILE"
    echo "请确保该文件存在并包含正确的股票代码"
    exit 1
else
    echo "股票池文件存在: $UNIVERSE_FILE"
    # 显示股票池内容
    echo "股票池内容:"
    head -5 "$UNIVERSE_FILE"
fi

# 6. 初始数据下载
echo "步骤 6: 初始数据下载..."

# 下载初始价格数据（最近30天）
echo "下载价格数据..."
python src/download_prices.py --debug

# 下载初始新闻数据
echo "下载新闻数据..."
python src/data_pipe.py --universe-file "$UNIVERSE_FILE" --recent_pages 2 --token_cap 100 --debug

# 7. 数据处理流水线
echo "步骤 7: 运行完整数据处理流水线..."

# 清洗数据
if [ -f "news_out/articles_recent.jsonl" ]; then
    echo "清洗新闻数据..."
    python src/clean_data.py --input-file "news_out/articles_recent.jsonl" --output-file "data/processed/articles_recent_cleaned.csv"
fi

# 情感分析
if [ -f "data/processed/articles_recent_cleaned.csv" ]; then
    echo "进行情感分析..."
    python src/sentiment_top.py --input-file "data/processed/articles_recent_cleaned.csv" --output-file "data/processed/articles_with_sentiment.csv"
fi

# 因子生成和评估
echo "生成因子并评估..."
python src/pipeline.py

# 8. 验证设置
echo "步骤 8: 验证项目设置..."
python - <<'PY'
import pandas as pd
import os
from pathlib import Path

print("=== 项目设置验证 ===")

# 检查关键文件
files_to_check = [
    "data/universe/hstech_current_constituents.csv",
    "data/prices.csv",
    "data/processed/articles_with_sentiment.csv",
    "data/processed/daily_sentiment_factors.csv",
    "reports/ic_daily.csv"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            print(f"✅ {file_path}: {len(df)} 条记录")
        except:
            print(f"⚠️  {file_path}: 文件存在但无法读取")
    else:
        print(f"❌ {file_path}: 文件不存在")

# 检查关键目录
dirs_to_check = ["logs", "data/processed", "reports/figs", "news_out"]
for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        print(f"✅ 目录 {dir_path}: 存在")
    else:
        print(f"❌ 目录 {dir_path}: 不存在")

print("\n=== 验证完成 ===")
PY

# 9. 设置定时任务提示
echo "步骤 9: 定时任务设置提示..."
echo ""
echo "=== 项目初始化完成 ==="
echo ""
echo "后续使用说明:"
echo "1. 每日更新: ./scripts/daily_run.sh"
echo "2. 手动下载价格: python src/download_prices.py"
echo "3. 查看日志: tail -f logs/daily-$(date +%F).log"
echo ""
echo "可选: 设置定时任务（每日上午8点运行）"
echo "crontab -e"
echo "0 8 * * * cd $(pwd) && ./scripts/daily_run.sh"
echo ""
echo "项目已就绪！🚀"
