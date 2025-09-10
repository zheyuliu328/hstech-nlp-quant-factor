#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_factor.py
---------------------------------
快速验证情感因子的脚本

展示我们的第一个量化因子成果！

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import pandas as pd
import json
from pathlib import Path

def main():
    print("🎯 情感因子验证报告")
    print("="*50)
    
    # 检查文件是否存在
    factor_file = "data/processed/daily_sentiment_factors.csv"
    ic_file = "data/processed/ic_results.csv"
    eval_file = "data/processed/factor_evaluation.json"
    
    if not Path(factor_file).exists():
        print("❌ 因子数据文件不存在，请先运行: python3 src/generate_factors.py")
        return
    
    if not Path(ic_file).exists():
        print("❌ IC数据文件不存在，请先运行: python3 src/generate_factors.py")
        return
    
    if not Path(eval_file).exists():
        print("❌ 评估数据文件不存在，请先运行: python3 src/generate_factors.py")
        return
    
    # 加载数据
    factors_df = pd.read_csv(factor_file)
    ic_df = pd.read_csv(ic_file)
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    comp = eval_data['comprehensive']
    
    print(f"✅ 成功加载因子数据!")
    print(f"📊 因子记录数: {len(factors_df):,}")
    print(f"📈 IC计算天数: {comp['total_days']}")
    print(f"🎯 IC均值: {comp['ic_mean']:.4f}")
    print(f"📊 IC t统计量: {comp['ic_t_stat']:.4f}")
    print(f"📈 Rank-IC均值: {comp['rank_ic_mean']:.4f}")
    
    # 显示前几条因子数据
    print(f"\n📋 前5条因子数据:")
    print(factors_df.head().to_string(index=False))
    
    # 显示IC数据
    print(f"\n📊 IC数据:")
    print(ic_df.to_string(index=False))
    
    # 因子有效性评估
    ic_t_stat = abs(comp['ic_t_stat'])
    if ic_t_stat > 2.0:
        effectiveness = "强"
        emoji = "✅"
    elif ic_t_stat > 1.5:
        effectiveness = "中等"
        emoji = "⚠️"
    else:
        effectiveness = "弱"
        emoji = "❌"
    
    print(f"\n{emoji} 因子有效性: {effectiveness} (t统计量: {ic_t_stat:.2f})")
    
    print(f"\n🎉 恭喜！我们成功构建了第一个情感因子！")
    print(f"📁 详细报告请查看: FACTOR_REPORT.md")
    print(f"🔍 详细分析请运行: python3 src/analyze_factors.py")

if __name__ == "__main__":
    main()

