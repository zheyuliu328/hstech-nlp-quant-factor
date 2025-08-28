#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_factors.py
---------------------------------
生成情感因子并进行评估的主脚本

功能包括：
- 从情感分析数据生成日度因子
- 计算因子与未来收益的IC
- 输出因子数据和评估结果

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import pandas as pd
import numpy as np
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

# 导入我们的模块
from factors import daily_factor_from_sentiment
from eval import add_fwd_return, ic_by_day, comprehensive_evaluation, monthly_summary

# --- 配置 ---
DEFAULT_SENTIMENT_FILE = 'data/processed/articles_with_sentiment.csv'
DEFAULT_PRICES_FILE = 'data/prices.csv'
DEFAULT_FACTOR_OUTPUT = 'data/processed/daily_sentiment_factors.csv'
DEFAULT_IC_OUTPUT = 'data/processed/ic_results.csv'
DEFAULT_EVAL_OUTPUT = 'data/processed/factor_evaluation.json'
# --- 结束配置 ---

def load_sentiment_data(sentiment_file: str) -> pd.DataFrame:
    """
    加载情感分析数据
    
    Args:
        sentiment_file: 情感分析数据文件路径
        
    Returns:
        加载的数据框
    """
    logging.info(f"加载情感分析数据: {sentiment_file}")
    
    if not Path(sentiment_file).exists():
        raise FileNotFoundError(f"情感分析数据文件不存在: {sentiment_file}")
    
    try:
        df = pd.read_csv(sentiment_file, encoding='utf-8-sig')
        logging.info(f"成功加载 {len(df)} 条情感分析记录")
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # 检查必要的列
        required_cols = ['date', 'code', 'sentiment_score']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少必要的列: {missing_cols}")
        
        return df
        
    except Exception as e:
        raise ValueError(f"加载情感分析数据时出错: {e}")


def load_price_data(prices_file: str) -> pd.DataFrame:
    """
    加载价格数据
    
    Args:
        prices_file: 价格数据文件路径
        
    Returns:
        加载的数据框
    """
    logging.info(f"加载价格数据: {prices_file}")
    
    if not Path(prices_file).exists():
        raise FileNotFoundError(f"价格数据文件不存在: {prices_file}")
    
    try:
        df = pd.read_csv(prices_file, encoding='utf-8-sig')
        logging.info(f"成功加载 {len(df)} 条价格记录")
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # 检查必要的列
        required_cols = ['date', 'code', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少必要的列: {missing_cols}")
        
        return df
        
    except Exception as e:
        raise ValueError(f"加载价格数据时出错: {e}")


def generate_factors(sentiment_df: pd.DataFrame) -> pd.DataFrame:
    """
    生成日度因子
    
    Args:
        sentiment_df: 情感分析数据框
        
    Returns:
        日度因子数据框
    """
    logging.info("开始生成日度因子...")
    
    # 使用我们的因子生成函数
    factors_df = daily_factor_from_sentiment(sentiment_df)
    
    logging.info(f"生成了 {len(factors_df)} 个日度因子记录")
    logging.info(f"覆盖 {factors_df['date'].nunique()} 个交易日")
    logging.info(f"覆盖 {factors_df['code'].nunique()} 只股票")
    
    return factors_df


def calculate_ic(factors_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    计算IC
    
    Args:
        factors_df: 因子数据框
        prices_df: 价格数据框
        
    Returns:
        IC结果数据框
    """
    logging.info("开始计算IC...")
    
    # 添加前瞻收益率
    prices_with_returns = add_fwd_return(prices_df)
    
    # 计算IC
    ic_results = ic_by_day(factors_df, prices_with_returns, 'sentiment_factor')
    
    logging.info(f"计算了 {len(ic_results)} 个交易日的IC")
    
    return ic_results


def evaluate_factors(ic_df: pd.DataFrame) -> Dict[str, Any]:
    """
    评估因子表现
    
    Args:
        ic_df: IC数据框
        
    Returns:
        评估结果字典
    """
    logging.info("开始评估因子表现...")
    
    # 综合评估
    eval_results = comprehensive_evaluation(ic_df)
    
    # 月度摘要
    monthly_stats = monthly_summary(ic_df)
    
    return {
        'comprehensive': eval_results,
        'monthly_stats': monthly_stats.to_dict('records') if not monthly_stats.empty else []
    }


def save_results(factors_df: pd.DataFrame, ic_df: pd.DataFrame, 
                eval_results: Dict[str, Any], 
                factor_output: str, ic_output: str, eval_output: str) -> None:
    """
    保存结果
    
    Args:
        factors_df: 因子数据框
        ic_df: IC数据框
        eval_results: 评估结果
        factor_output: 因子输出文件路径
        ic_output: IC输出文件路径
        eval_output: 评估输出文件路径
    """
    # 确保输出目录存在
    for output_file in [factor_output, ic_output, eval_output]:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 保存因子数据
    logging.info(f"保存因子数据到: {factor_output}")
    factors_df.to_csv(factor_output, index=False, encoding='utf-8-sig')
    
    # 保存IC数据
    logging.info(f"保存IC数据到: {ic_output}")
    ic_df.to_csv(ic_output, index=False, encoding='utf-8-sig')
    
    # 保存评估结果
    logging.info(f"保存评估结果到: {eval_output}")
    import json
    with open(eval_output, 'w', encoding='utf-8') as f:
        json.dump(eval_results, f, ensure_ascii=False, indent=2)


def print_evaluation_summary(eval_results: Dict[str, Any]) -> None:
    """
    打印评估摘要
    
    Args:
        eval_results: 评估结果字典
    """
    comp = eval_results['comprehensive']
    
    print("\n" + "="*60)
    print("🎯 情感因子评估结果")
    print("="*60)
    
    print(f"📊 数据概览:")
    print(f"   • 总交易日数: {comp['total_days']}")
    
    print(f"\n📈 IC统计:")
    print(f"   • IC均值: {comp['ic_mean']:.4f}")
    print(f"   • IC标准差: {comp['ic_std']:.4f}")
    print(f"   • IC t统计量: {comp['ic_t_stat']:.4f}")
    print(f"   • IC信息比率: {comp['ic_ir']:.4f}")
    print(f"   • 正IC比例: {comp['positive_ic_ratio']:.2%}")
    
    print(f"\n📊 Rank-IC统计:")
    print(f"   • Rank-IC均值: {comp['rank_ic_mean']:.4f}")
    print(f"   • Rank-IC标准差: {comp['rank_ic_std']:.4f}")
    print(f"   • Rank-IC t统计量: {comp['rank_ic_t_stat']:.4f}")
    print(f"   • Rank-IC信息比率: {comp['rank_ic_ir']:.4f}")
    print(f"   • 正Rank-IC比例: {comp['positive_rank_ic_ratio']:.2%}")
    
    # 判断因子有效性
    if abs(comp['ic_t_stat']) > 2.0:
        print(f"\n✅ 因子有效性: 强 (|t统计量| = {abs(comp['ic_t_stat']):.2f} > 2.0)")
    elif abs(comp['ic_t_stat']) > 1.5:
        print(f"\n⚠️  因子有效性: 中等 (|t统计量| = {abs(comp['ic_t_stat']):.2f} > 1.5)")
    else:
        print(f"\n❌ 因子有效性: 弱 (|t统计量| = {abs(comp['ic_t_stat']):.2f} < 1.5)")
    
    print("="*60)


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="生成情感因子并进行评估")
    parser.add_argument("--sentiment_file", "-s", default=DEFAULT_SENTIMENT_FILE, 
                       help="情感分析数据文件路径")
    parser.add_argument("--prices_file", "-p", default=DEFAULT_PRICES_FILE, 
                       help="价格数据文件路径")
    parser.add_argument("--factor_output", "-fo", default=DEFAULT_FACTOR_OUTPUT, 
                       help="因子输出文件路径")
    parser.add_argument("--ic_output", "-io", default=DEFAULT_IC_OUTPUT, 
                       help="IC输出文件路径")
    parser.add_argument("--eval_output", "-eo", default=DEFAULT_EVAL_OUTPUT, 
                       help="评估输出文件路径")
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
        sentiment_df = load_sentiment_data(args.sentiment_file)
        prices_df = load_price_data(args.prices_file)
        
        # 2. 生成因子
        factors_df = generate_factors(sentiment_df)
        
        # 3. 计算IC
        ic_df = calculate_ic(factors_df, prices_df)
        
        # 4. 评估因子
        eval_results = evaluate_factors(ic_df)
        
        # 5. 保存结果
        save_results(factors_df, ic_df, eval_results, 
                    args.factor_output, args.ic_output, args.eval_output)
        
        # 6. 打印摘要
        print_evaluation_summary(eval_results)
        
        print(f"\n✅ 因子生成和评估完成!")
        print(f"📁 因子数据: {args.factor_output}")
        print(f"📁 IC数据: {args.ic_output}")
        print(f"📁 评估结果: {args.eval_output}")
        
    except Exception as e:
        logging.error(f"因子生成和评估失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

