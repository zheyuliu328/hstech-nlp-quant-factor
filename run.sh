#!/bin/bash
# 新版 run.sh，带有详细的进度汇报和性能优化
set -euo pipefail  # 更严格的错误检查

echo "🚀 Day 4: 启动最小可行闭环 (MVP) 生成流水线..."
echo "" # 空一行，为了好看

# --- 准备工作 ---
echo "STEP 0: 激活本地虚拟环境并检查依赖..."
source ~/.venvs/nlpqf/bin/activate
export PYTHONDONTWRITEBYTECODE=1   # 避免在项目目录写 .pyc，加速 Dropbox 目录的导入

# 智能依赖安装：只在需要时安装
if [ ! -f .deps_ok ]; then
    echo "📦 首次运行，正在安装依赖包..."
    pip install -r requirements.txt --disable-pip-version-check
    touch .deps_ok
    echo "✅ 依赖安装完成。"
else
    echo "✅ 依赖已就绪，跳过安装。"
fi
echo "✅ STEP 0: 环境就绪。"
echo ""

# --- 生成可视化图表 ---
echo "STEP 1: 正在生成图一 (IC时序图)..."
python3 src/plotting.py
echo "✅ STEP 1: 图一生成完毕。"
echo ""

echo "STEP 2: 正在生成图二 (分层回测图)..."
python3 src/backtest/vectorized.py
echo "✅ STEP 2: 图二生成完毕。"
echo ""

echo "STEP 3: 正在生成图三 (风格相关性热力图)..."
python3 src/analysis/factor_corr.py
echo "✅ STEP 3: 图三生成完毕。"
echo ""

# --- 最终验收 ---
echo "🎉 流水线完成！所有图表已生成在 reports/figs/ 目录下。"
echo "----------------------------------------------------"
ls -l reports/figs/
echo "----------------------------------------------------"