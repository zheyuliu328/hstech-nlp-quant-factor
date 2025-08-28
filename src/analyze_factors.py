#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_factors.py
---------------------------------
分析情感因子表现的详细脚本

功能包括：
- 加载因子数据和IC结果
- 生成详细的统计报告
- 可视化因子表现

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import pandas as pd
import numpy as np
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

# --- 配置 ---
DEFAULT_FACTOR_FILE = 'data/processed/daily_sentiment_factors.csv'
DEFAULT_IC_FILE = 'data/processed/ic_results.csv'
DEFAULT_EVAL_FILE = 'data/processed/factor_evaluation.json'
# --- 结束配置 ---

def load_factor_data(factor_file: str) -> pd.DataFrame:
    """
    加载因子数据
    
    Args:
        factor_file: 因子数据文件路径
        
    Returns:
        因子数据框
    """
    logging.info(f"加载因子数据: {factor_file}")
    
    if not Path(factor_file).exists():
        raise FileNotFoundError(f"因子数据文件不存在: {factor_file}")
    
    df = pd.read_csv(factor_file, encoding='utf-8-sig')
    df['date'] = pd.to_datetime(df['date'])
    
    logging.info(f"成功加载 {len(df)} 条因子记录")
    return df


def load_ic_data(ic_file: str) -> pd.DataFrame:
    """
    加载IC数据
    
    Args:
        ic_file: IC数据文件路径
        
    Returns:
        IC数据框
    """
    logging.info(f"加载IC数据: {ic_file}")
    
    if not Path(ic_file).exists():
        raise FileNotFoundError(f"IC数据文件不存在: {ic_file}")
    
    df = pd.read_csv(ic_file, encoding='utf-8-sig')
    df['date'] = pd.to_datetime(df['date'])
    
    logging.info(f"成功加载 {len(df)} 条IC记录")
    return df


def load_evaluation_data(eval_file: str) -> Dict[str, Any]:
    """
    加载评估数据
    
    Args:
        eval_file: 评估数据文件路径
        
    Returns:
        评估结果字典
    """
    logging.info(f"加载评估数据: {eval_file}")
    
    if not Path(eval_file).exists():
        raise FileNotFoundError(f"评估数据文件不存在: {eval_file}")
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    logging.info("成功加载评估数据")
    return eval_data


def analyze_factor_distribution(factors_df: pd.DataFrame) -> Dict[str, Any]:
    """
    分析因子分布
    
    Args:
        factors_df: 因子数据框
        
    Returns:
        分布分析结果
    """
    logging.info("分析因子分布...")
    
    # 基本统计
    sentiment_stats = factors_df['sentiment_factor'].describe()
    weighted_stats = factors_df['weighted_factor'].describe()
    news_count_stats = factors_df['news_count'].describe()
    
    # 因子值分布
    sentiment_positive = (factors_df['sentiment_factor'] > 0).mean()
    sentiment_negative = (factors_df['sentiment_factor'] < 0).mean()
    sentiment_neutral = (factors_df['sentiment_factor'] == 0).mean()
    
    # 新闻数量分布
    high_news = (factors_df['news_count'] >= 3).mean()
    medium_news = ((factors_df['news_count'] >= 2) & (factors_df['news_count'] < 3)).mean()
    low_news = (factors_df['news_count'] == 1).mean()
    
    return {
        'sentiment_stats': sentiment_stats.to_dict(),
        'weighted_stats': weighted_stats.to_dict(),
        'news_count_stats': news_count_stats.to_dict(),
        'sentiment_distribution': {
            'positive': round(sentiment_positive, 4),
            'negative': round(sentiment_negative, 4),
            'neutral': round(sentiment_neutral, 4)
        },
        'news_count_distribution': {
            'high_news': round(high_news, 4),
            'medium_news': round(medium_news, 4),
            'low_news': round(low_news, 4)
        }
    }


def analyze_ic_performance(ic_df: pd.DataFrame) -> Dict[str, Any]:
    """
    分析IC表现
    
    Args:
        ic_df: IC数据框
        
    Returns:
        IC分析结果
    """
    logging.info("分析IC表现...")
    
    if ic_df.empty:
        return {'error': 'IC数据为空'}
    
    # IC时间序列分析
    ic_trend = ic_df['IC'].diff().mean() if len(ic_df) > 1 else 0
    
    # 最大最小IC
    max_ic = ic_df['IC'].max()
    min_ic = ic_df['IC'].min()
    max_ic_date = ic_df.loc[ic_df['IC'].idxmax(), 'date']
    min_ic_date = ic_df.loc[ic_df['IC'].idxmin(), 'date']
    
    # Rank-IC分析
    max_rank_ic = ic_df['RankIC'].max()
    min_rank_ic = ic_df['RankIC'].min()
    
    return {
        'ic_trend': round(ic_trend, 4),
        'max_ic': round(max_ic, 4),
        'min_ic': round(min_ic, 4),
        'max_ic_date': str(max_ic_date),
        'min_ic_date': str(min_ic_date),
        'max_rank_ic': round(max_rank_ic, 4),
        'min_rank_ic': round(min_rank_ic, 4),
        'ic_range': round(max_ic - min_ic, 4)
    }


def print_detailed_report(factors_df: pd.DataFrame, ic_df: pd.DataFrame, 
                         eval_data: Dict[str, Any], dist_analysis: Dict[str, Any], 
                         ic_analysis: Dict[str, Any]) -> None:
    """
    打印详细报告
    
    Args:
        factors_df: 因子数据框
        ic_df: IC数据框
        eval_data: 评估数据
        dist_analysis: 分布分析结果
        ic_analysis: IC分析结果
    """
    comp = eval_data['comprehensive']
    
    print("\n" + "="*80)
    print("📊 情感因子详细分析报告")
    print("="*80)
    
    # 数据概览
    print(f"\n📈 数据概览:")
    print(f"   • 因子记录数: {len(factors_df):,}")
    print(f"   • 覆盖交易日: {factors_df['date'].nunique()}")
    print(f"   • 覆盖股票数: {factors_df['code'].nunique()}")
    print(f"   • IC计算天数: {comp['total_days']}")
    
    # 因子分布
    print(f"\n🎯 因子分布分析:")
    print(f"   • 情感因子均值: {dist_analysis['sentiment_stats']['mean']:.4f}")
    print(f"   • 情感因子标准差: {dist_analysis['sentiment_stats']['std']:.4f}")
    print(f"   • 情感因子范围: [{dist_analysis['sentiment_stats']['min']:.4f}, {dist_analysis['sentiment_stats']['max']:.4f}]")
    print(f"   • 正因子比例: {dist_analysis['sentiment_distribution']['positive']:.2%}")
    print(f"   • 负因子比例: {dist_analysis['sentiment_distribution']['negative']:.2%}")
    print(f"   • 中性因子比例: {dist_analysis['sentiment_distribution']['neutral']:.2%}")
    
    # 新闻数量分布
    print(f"\n📰 新闻数量分布:")
    print(f"   • 平均新闻数: {dist_analysis['news_count_stats']['mean']:.2f}")
    print(f"   • 高新闻量比例 (≥3条): {dist_analysis['news_count_distribution']['high_news']:.2%}")
    print(f"   • 中新闻量比例 (2条): {dist_analysis['news_count_distribution']['medium_news']:.2%}")
    print(f"   • 低新闻量比例 (1条): {dist_analysis['news_count_distribution']['low_news']:.2%}")
    
    # IC表现
    print(f"\n📊 IC表现分析:")
    print(f"   • IC均值: {comp['ic_mean']:.4f}")
    print(f"   • IC标准差: {comp['ic_std']:.4f}")
    print(f"   • IC t统计量: {comp['ic_t_stat']:.4f}")
    print(f"   • IC信息比率: {comp['ic_ir']:.4f}")
    print(f"   • 正IC比例: {comp['positive_ic_ratio']:.2%}")
    
    if 'error' not in ic_analysis:
        print(f"   • 最大IC: {ic_analysis['max_ic']:.4f} ({ic_analysis['max_ic_date']})")
        print(f"   • 最小IC: {ic_analysis['min_ic']:.4f} ({ic_analysis['min_ic_date']})")
        print(f"   • IC范围: {ic_analysis['ic_range']:.4f}")
    
    # Rank-IC表现
    print(f"\n📈 Rank-IC表现分析:")
    print(f"   • Rank-IC均值: {comp['rank_ic_mean']:.4f}")
    print(f"   • Rank-IC标准差: {comp['rank_ic_std']:.4f}")
    print(f"   • Rank-IC t统计量: {comp['rank_ic_t_stat']:.4f}")
    print(f"   • Rank-IC信息比率: {comp['rank_ic_ir']:.4f}")
    print(f"   • 正Rank-IC比例: {comp['positive_rank_ic_ratio']:.2%}")
    
    # 因子有效性评估
    print(f"\n🎯 因子有效性评估:")
    ic_t_stat = abs(comp['ic_t_stat'])
    rank_ic_t_stat = abs(comp['rank_ic_t_stat'])
    
    if ic_t_stat > 2.0:
        ic_effectiveness = "强"
    elif ic_t_stat > 1.5:
        ic_effectiveness = "中等"
    else:
        ic_effectiveness = "弱"
    
    if rank_ic_t_stat > 2.0:
        rank_ic_effectiveness = "强"
    elif rank_ic_t_stat > 1.5:
        rank_ic_effectiveness = "中等"
    else:
        rank_ic_effectiveness = "弱"
    
    print(f"   • IC有效性: {ic_effectiveness} (t统计量: {ic_t_stat:.2f})")
    print(f"   • Rank-IC有效性: {rank_ic_effectiveness} (t统计量: {rank_ic_t_stat:.2f})")
    
    # 投资建议
    print(f"\n💡 投资建议:")
    if ic_t_stat > 2.0 and comp['ic_mean'] > 0:
        print("   ✅ 因子显示强正向预测能力，建议用于选股")
    elif ic_t_stat > 1.5 and comp['ic_mean'] > 0:
        print("   ⚠️  因子显示中等正向预测能力，可谨慎使用")
    elif ic_t_stat > 2.0 and comp['ic_mean'] < 0:
        print("   ✅ 因子显示强负向预测能力，可用于反向选股")
    else:
        print("   ❌ 因子预测能力较弱，需要更多数据或改进方法")
    
    print("="*80)


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="分析情感因子表现")
    parser.add_argument("--factor_file", "-f", default=DEFAULT_FACTOR_FILE, 
                       help="因子数据文件路径")
    parser.add_argument("--ic_file", "-i", default=DEFAULT_IC_FILE, 
                       help="IC数据文件路径")
    parser.add_argument("--eval_file", "-e", default=DEFAULT_EVAL_FILE, 
                       help="评估数据文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    try:
        # 1. 加载数据
        factors_df = load_factor_data(args.factor_file)
        ic_df = load_ic_data(args.ic_file)
        eval_data = load_evaluation_data(args.eval_file)
        
        # 2. 分析因子分布
        dist_analysis = analyze_factor_distribution(factors_df)
        
        # 3. 分析IC表现
        ic_analysis = analyze_ic_performance(ic_df)
        
        # 4. 打印详细报告
        print_detailed_report(factors_df, ic_df, eval_data, dist_analysis, ic_analysis)
        
        print(f"\n✅ 因子分析完成!")
        
    except Exception as e:
        logging.error(f"因子分析失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
