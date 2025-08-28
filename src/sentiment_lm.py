#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sentiment_lm.py
---------------------------------
Loughran & McDonald sentiment analysis using lexicon approach
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict

def load_lexicon(file_path: str) -> List[str]:
    """加载情感词典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        return words
    except FileNotFoundError:
        print(f"Warning: Lexicon file {file_path} not found")
        return []

def lm_score_news(news_df: pd.DataFrame, positive_file: str, negative_file: str) -> pd.DataFrame:
    """
    使用Loughran & McDonald词典对新闻进行情感分析
    
    Args:
        news_df: 包含 'headline' 列的新闻数据框
        positive_file: 正面词典文件路径
        negative_file: 负面词典文件路径
        
    Returns:
        包含 'score_lm' 列的数据框
    """
    # 加载词典
    positive_words = load_lexicon(positive_file)
    negative_words = load_lexicon(negative_file)
    
    def calculate_sentiment_score(text: str) -> float:
        if not isinstance(text, str):
            return 0.0
        
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        # 计算情感分数 (正面词数 - 负面词数) / 总词数
        score = (positive_count - negative_count) / total_words
        return score
    
    # 计算情感分数
    news_df = news_df.copy()
    news_df['score_lm'] = news_df['headline'].apply(calculate_sentiment_score)
    
    return news_df
