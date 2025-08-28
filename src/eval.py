#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eval.py
---------------------------------
Evaluation metrics and performance analysis
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def add_fwd_return(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    添加前瞻收益率
    
    Args:
        prices_df: 包含 'date', 'code', 'close' 列的价格数据框
        
    Returns:
        添加了 'ret_fwd_1d' 列的数据框
    """
    df = prices_df.copy()
    df = df.sort_values(['code', 'date'])
    
    # 计算1日前瞻收益率
    df['close_next'] = df.groupby('code')['close'].shift(-1)
    df['ret_fwd_1d'] = (df['close_next'] / df['close']) - 1
    
    # 删除辅助列
    df = df.drop('close_next', axis=1)
    
    return df

def ic_by_day(factors_df: pd.DataFrame, returns_df: pd.DataFrame, factor_col: str = 'sentiment_factor') -> pd.DataFrame:
    """
    计算每日IC和Rank-IC
    
    Args:
        factors_df: 包含 'date', 'code' 和因子列的因子数据框
        returns_df: 包含 'date', 'code', 'ret_fwd_1d' 列的收益率数据框
        factor_col: 因子列名，默认为 'sentiment_factor'
        
    Returns:
        包含 'date', 'IC', 'RankIC' 列的数据框
    """
    # 合并数据
    merged = factors_df.merge(returns_df[['date', 'code', 'ret_fwd_1d']], 
                             on=['date', 'code'], how='inner')
    
    # 按日期计算IC
    ic_results = []
    for date, group in merged.groupby('date'):
        # 稳健性检查：最小样本数
        if len(group) < 5:
            continue
        
        # 稳健性检查：因子标准差不能为0
        if group[factor_col].std() == 0:
            continue
            
        # 稳健性检查：收益率标准差不能为0
        if group['ret_fwd_1d'].std() == 0:
            continue
            
        # 计算Pearson相关系数 (IC)
        ic = group[factor_col].corr(group['ret_fwd_1d'])
        
        # 计算Spearman相关系数 (Rank-IC)
        rank_ic = group[factor_col].corr(group['ret_fwd_1d'], method='spearman')
        
        ic_results.append({
            'date': date,
            'IC': ic if not np.isnan(ic) else 0,
            'RankIC': rank_ic if not np.isnan(rank_ic) else 0
        })
    
    return pd.DataFrame(ic_results)


def ic_by_day_legacy(factors_df: pd.DataFrame, returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    计算每日IC和Rank-IC (兼容旧版本)
    
    Args:
        factors_df: 包含 'date', 'code', 'factor_lm' 列的因子数据框
        returns_df: 包含 'date', 'code', 'ret_fwd_1d' 列的收益率数据框
        
    Returns:
        包含 'date', 'IC', 'RankIC' 列的数据框
    """
    return ic_by_day(factors_df, returns_df, 'factor_lm')

def monthly_summary(ic_daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    计算月度IC统计摘要
    
    Args:
        ic_daily_df: 包含 'date', 'IC', 'RankIC' 列的日度IC数据框
        
    Returns:
        包含月度统计的数据框
    """
    if ic_daily_df.empty:
        return pd.DataFrame()
    
    df = ic_daily_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    # 按月聚合
    monthly_stats = df.groupby('month').agg({
        'IC': ['mean', 'std', 'count'],
        'RankIC': ['mean', 'std']
    }).round(4)
    
    # 展平列名
    monthly_stats.columns = ['IC_mean', 'IC_std', 'IC_count', 'RankIC_mean', 'RankIC_std']
    monthly_stats = monthly_stats.reset_index()
    
    # 计算t统计量
    monthly_stats['IC_t'] = monthly_stats['IC_mean'] / (monthly_stats['IC_std'] / np.sqrt(monthly_stats['IC_count']))
    monthly_stats['RankIC_t'] = monthly_stats['RankIC_mean'] / (monthly_stats['RankIC_std'] / np.sqrt(monthly_stats['IC_count']))
    
    return monthly_stats


def comprehensive_evaluation(ic_daily_df: pd.DataFrame) -> Dict[str, Any]:
    """
    综合评估因子表现
    
    Args:
        ic_daily_df: 包含 'date', 'IC', 'RankIC' 列的日度IC数据框
        
    Returns:
        包含综合评估指标的字典
    """
    if ic_daily_df.empty:
        return {
            'total_days': 0,
            'ic_mean': 0,
            'ic_std': 0,
            'ic_t_stat': 0,
            'ic_ir': 0,
            'rank_ic_mean': 0,
            'rank_ic_std': 0,
            'rank_ic_t_stat': 0,
            'rank_ic_ir': 0,
            'positive_ic_ratio': 0,
            'positive_rank_ic_ratio': 0
        }
    
    # 基本统计
    total_days = len(ic_daily_df)
    
    # IC统计
    ic_mean = ic_daily_df['IC'].mean()
    ic_std = ic_daily_df['IC'].std()
    ic_t_stat = ic_mean / (ic_std / np.sqrt(total_days)) if ic_std > 0 else 0
    ic_ir = ic_mean / ic_std if ic_std > 0 else 0
    
    # Rank-IC统计
    rank_ic_mean = ic_daily_df['RankIC'].mean()
    rank_ic_std = ic_daily_df['RankIC'].std()
    rank_ic_t_stat = rank_ic_mean / (rank_ic_std / np.sqrt(total_days)) if rank_ic_std > 0 else 0
    rank_ic_ir = rank_ic_mean / rank_ic_std if rank_ic_std > 0 else 0
    
    # 正IC比例
    positive_ic_ratio = (ic_daily_df['IC'] > 0).mean()
    positive_rank_ic_ratio = (ic_daily_df['RankIC'] > 0).mean()
    
    return {
        'total_days': total_days,
        'ic_mean': round(ic_mean, 4),
        'ic_std': round(ic_std, 4),
        'ic_t_stat': round(ic_t_stat, 4),
        'ic_ir': round(ic_ir, 4),
        'rank_ic_mean': round(rank_ic_mean, 4),
        'rank_ic_std': round(rank_ic_std, 4),
        'rank_ic_t_stat': round(rank_ic_t_stat, 4),
        'rank_ic_ir': round(rank_ic_ir, 4),
        'positive_ic_ratio': round(positive_ic_ratio, 4),
        'positive_rank_ic_ratio': round(positive_rank_ic_ratio, 4)
    }
