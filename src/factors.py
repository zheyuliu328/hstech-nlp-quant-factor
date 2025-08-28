#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factors.py
---------------------------------
Factor construction and processing
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def daily_factor_from_sentiment(sentiment_df: pd.DataFrame) -> pd.DataFrame:
    """
    从情感分析数据聚合到日度因子
    
    Args:
        sentiment_df: 包含 'date', 'code', 'sentiment_score' 列的数据框
        
    Returns:
        包含 'date', 'code', 'sentiment_factor' 列的数据框
    """
    # 按日期和股票代码聚合
    daily_factors = sentiment_df.groupby(['date', 'code'])['sentiment_score'].agg([
        'mean',  # 平均情感分数
        'count', # 新闻数量
        'std',   # 标准差
        'sum'    # 总情感分数
    ]).reset_index()
    
    # 重命名列
    daily_factors.columns = ['date', 'code', 'sentiment_factor', 'news_count', 'sentiment_std', 'sentiment_sum']
    
    # 处理缺失值
    daily_factors['sentiment_std'] = daily_factors['sentiment_std'].fillna(0)
    
    # 创建加权因子：考虑新闻数量
    daily_factors['weighted_factor'] = daily_factors['sentiment_factor'] * np.log1p(daily_factors['news_count'])
    
    # 横截面标准化 (按日期分组)
    def winsorize_and_zscore(group):
        # 对主要因子进行Winsorize (截尾处理) - 收紧到2%-98%
        q2, q98 = group['sentiment_factor'].quantile([0.02, 0.98])
        group['sentiment_factor'] = group['sentiment_factor'].clip(lower=q2, upper=q98)
        
        # 对加权因子进行Winsorize
        q2_w, q98_w = group['weighted_factor'].quantile([0.02, 0.98])
        group['weighted_factor'] = group['weighted_factor'].clip(lower=q2_w, upper=q98_w)
        
        # Z-score标准化
        mean_val = group['sentiment_factor'].mean()
        std_val = group['sentiment_factor'].std()
        if std_val > 0:
            group['sentiment_factor'] = (group['sentiment_factor'] - mean_val) / std_val
        else:
            group['sentiment_factor'] = 0
            
        # 加权因子标准化
        mean_w = group['weighted_factor'].mean()
        std_w = group['weighted_factor'].std()
        if std_w > 0:
            group['weighted_factor'] = (group['weighted_factor'] - mean_w) / std_w
        else:
            group['weighted_factor'] = 0
        
        return group
    
    # 保存日期列
    dates = daily_factors['date'].copy()
    daily_factors = daily_factors.groupby('date').apply(winsorize_and_zscore, include_groups=False).reset_index(drop=True)
    
    # 确保日期列存在
    if 'date' not in daily_factors.columns:
        daily_factors['date'] = dates
    
    return daily_factors[['date', 'code', 'sentiment_factor', 'weighted_factor', 'news_count', 'sentiment_std']]


def daily_factor_from_headlines(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    从新闻标题级别聚合到日度因子 (兼容旧版本)
    
    Args:
        scored_df: 包含 'date', 'code', 'score_lm' 列的数据框
        
    Returns:
        包含 'date', 'code', 'factor_lm' 列的数据框
    """
    # 按日期和股票代码聚合
    daily_factors = scored_df.groupby(['date', 'code'])['score_lm'].agg([
        'mean',  # 平均情感分数
        'count', # 新闻数量
        'std'    # 标准差
    ]).reset_index()
    
    # 重命名列
    daily_factors.columns = ['date', 'code', 'factor_lm', 'news_count', 'sentiment_std']
    
    # 处理缺失值
    daily_factors['sentiment_std'] = daily_factors['sentiment_std'].fillna(0)
    
    # 横截面标准化 (按日期分组)
    def winsorize_and_zscore(group):
        # Winsorize (截尾处理) - 收紧到2%-98%
        q2, q98 = group['factor_lm'].quantile([0.02, 0.98])
        group['factor_lm'] = group['factor_lm'].clip(lower=q2, upper=q98)
        
        # Z-score标准化
        mean_val = group['factor_lm'].mean()
        std_val = group['factor_lm'].std()
        if std_val > 0:
            group['factor_lm'] = (group['factor_lm'] - mean_val) / std_val
        else:
            group['factor_lm'] = 0
        
        return group
    
    # 保存日期列
    dates = daily_factors['date'].copy()
    daily_factors = daily_factors.groupby('date').apply(winsorize_and_zscore, include_groups=False).reset_index(drop=True)
    
    # 确保日期列存在
    if 'date' not in daily_factors.columns:
        daily_factors['date'] = dates
    
    return daily_factors[['date', 'code', 'factor_lm']]
