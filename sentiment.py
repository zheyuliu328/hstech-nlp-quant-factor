#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sentiment.py
---------------------------------
情感分析模块：为清洗后的新闻数据添加情感分数

功能包括：
- 读取清洗后的新闻数据
- 使用 cardiffnlp/twitter-roberta-base-sentiment-latest 模型进行情感分析
- 将情感标签转换为数值分数
- 保存带有 sentiment_score 列的结果

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import pandas as pd
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time
try:
    import torch
    from transformers import pipeline
except ImportError as e:
    print(f"警告: 无法导入 torch 或 transformers: {e}")
    print("请安装: pip install torch transformers")
    torch = None
    pipeline = None

# --- 配置 ---
DEFAULT_INPUT_FILE = 'data/processed/articles_recent_cleaned.csv'
DEFAULT_OUTPUT_FILE = 'data/processed/articles_with_sentiment.csv'
DEFAULT_TEXT_COLUMN = 'body'  # 清洗后数据中的文本列名
DEFAULT_BATCH_SIZE = 32  # 根据内存情况调整
MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
# --- 结束配置 ---

def convert_sentiment_to_score(sentiment_label: str, confidence: float) -> float:
    """
    将情感标签转换为数值分数
    
    Args:
        sentiment_label: 情感标签 ('LABEL_0', 'LABEL_1', 'LABEL_2' 或 'NEGATIVE', 'NEUTRAL', 'POSITIVE')
        confidence: 置信度分数
        
    Returns:
        情感分数 (-1.0 到 1.0，负数表示负面，正数表示正面，0表示中性)
    """
    # 处理不同的标签格式
    if sentiment_label in ['LABEL_0', 'NEGATIVE', 'negative']:
        return -confidence  # 负面情感，置信度越高分数越负
    elif sentiment_label in ['LABEL_1', 'NEUTRAL', 'neutral']:
        return 0.0  # 中性情感，分数为0
    elif sentiment_label in ['LABEL_2', 'POSITIVE', 'positive']:
        return confidence  # 正面情感，置信度越高分数越正
    else:
        logging.warning(f"未知的情感标签: {sentiment_label}")
        return 0.0


def load_cleaned_data(input_file: str, text_column: str) -> pd.DataFrame:
    """
    加载清洗后的数据
    
    Args:
        input_file: 输入文件路径
        text_column: 文本列名
        
    Returns:
        加载的数据框
    """
    logging.info(f"开始加载数据: {input_file}")
    
    if not Path(input_file).exists():
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    try:
        # 尝试不同的编码方式
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                logging.info(f"成功使用 {encoding} 编码加载数据")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("无法使用任何编码方式读取文件")
            
    except Exception as e:
        raise ValueError(f"加载文件时出错: {e}")
    
    # 检查文本列是否存在
    if text_column not in df.columns:
        available_cols = df.columns.tolist()
        raise ValueError(f"文本列 '{text_column}' 在文件中未找到。可用列: {available_cols}")
    
    # 清理数据：删除文本列为空或只有空格的行
    original_rows = len(df)
    df = df.dropna(subset=[text_column])
    df = df[df[text_column].astype(str).str.strip() != '']
    rows_after_cleaning = len(df)
    
    if rows_after_cleaning < original_rows:
        logging.info(f"清理数据：删除了 {original_rows - rows_after_cleaning} 行空文本")
    
    logging.info(f"找到 {rows_after_cleaning} 条有效新闻进行情感分析")
    
    return df

def load_sentiment_model() -> pipeline:
    """
    加载情感分析模型
    
    Returns:
        加载的pipeline对象
    """
    logging.info("正在加载 Transformer 情感分析模型 (可能需要几分钟)...")
    start_load_time = time.time()
    
    # 检查是否有可用的GPU
    if torch is None:
        raise RuntimeError("torch 未安装，请运行: pip install torch")
    
    device_num = 0 if torch.cuda.is_available() else -1
    device_name = "GPU" if device_num == 0 else "CPU"
    logging.info(f"将使用设备: {device_name}")
    
    try:
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME,
            device=device_num
        )
        
        load_time = time.time() - start_load_time
        logging.info(f"模型加载完成，耗时: {load_time:.2f} 秒")
        
        return sentiment_pipeline
        
    except Exception as e:
        logging.error(f"加载模型时出错: {e}")
        raise RuntimeError("请检查网络连接和库安装情况")


def analyze_sentiment_batch(
    texts: List[str], 
    sentiment_pipeline: pipeline, 
    batch_size: int = DEFAULT_BATCH_SIZE
) -> List[Dict[str, Any]]:
    """
    批量进行情感分析
    
    Args:
        texts: 文本列表
        sentiment_pipeline: 情感分析pipeline
        batch_size: 批处理大小
        
    Returns:
        情感分析结果列表
    """
    logging.info(f"开始情感分析 (分批处理，每批 {batch_size} 条)...")
    logging.info("这可能需要较长时间，尤其是在CPU上。请耐心等待...")
    
    all_results = []
    analysis_start_time = time.time()
    
    # 分批处理
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            # 使用pipeline进行情感分析
            results = sentiment_pipeline(batch, truncation=True, max_length=512)
            all_results.extend(results)
            
        except Exception as e:
            logging.error(f"处理批次 {i//batch_size + 1} 时出错: {e}")
            # 如果一批出错，用默认值填充
            error_results = [{'label': 'LABEL_1', 'score': 0.5} for _ in batch]
            all_results.extend(error_results)
        
        # 打印进度
        if (i // batch_size + 1) % 10 == 0 or i + len(batch) >= len(texts):
            elapsed_time = time.time() - analysis_start_time
            processed = min(i + len(batch), len(texts))
            estimated_total_time = (elapsed_time / processed) * len(texts) if processed > 0 else 0
            logging.info(f"已处理 {processed} / {len(texts)} 条新闻。"
                        f"耗时: {elapsed_time:.1f}s (预计总耗时: {estimated_total_time:.1f}s)")
    
    analysis_time = time.time() - analysis_start_time
    logging.info(f"情感分析完成，总耗时: {analysis_time:.2f} 秒")
    
    return all_results

def add_sentiment_scores(
    df: pd.DataFrame, 
    sentiment_results: List[Dict[str, Any]], 
    text_column: str
) -> pd.DataFrame:
    """
    将情感分析结果添加到数据框
    
    Args:
        df: 原始数据框
        sentiment_results: 情感分析结果
        text_column: 文本列名
        
    Returns:
        添加了情感分数列的数据框
    """
    if len(sentiment_results) != len(df):
        raise ValueError(f"情感分析结果数量 ({len(sentiment_results)}) 与数据行数 ({len(df)}) 不匹配")
    
    # 创建结果数据框
    df_result = df.copy()
    
    # 提取情感标签和置信度
    sentiment_labels = [result['label'] for result in sentiment_results]
    sentiment_scores = [result['score'] for result in sentiment_results]
    
    # 转换为数值分数
    numeric_scores = [
        convert_sentiment_to_score(label, score) 
        for label, score in zip(sentiment_labels, sentiment_scores)
    ]
    
    # 添加新列
    df_result['sentiment_label'] = sentiment_labels
    df_result['sentiment_confidence'] = sentiment_scores
    df_result['sentiment_score'] = numeric_scores
    
    # 统计情感分布
    sentiment_distribution = pd.Series(sentiment_labels).value_counts()
    logging.info(f"情感标签分布:\n{sentiment_distribution}")
    
    # 统计分数分布
    score_stats = pd.Series(numeric_scores).describe()
    logging.info(f"情感分数统计:\n{score_stats}")
    
    return df_result


def save_results(df: pd.DataFrame, output_file: str) -> None:
    """
    保存结果到文件
    
    Args:
        df: 结果数据框
        output_file: 输出文件路径
    """
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"正在将结果保存到: {output_file}")
    
    try:
        # 使用 utf-8-sig 编码以便 Excel 能更好地识别 UTF-8
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logging.info("文件保存成功")
        
    except Exception as e:
        logging.error(f"保存文件时出错: {e}")
        raise


def process_sentiment_analysis(
    input_file: str,
    output_file: str,
    text_column: str = DEFAULT_TEXT_COLUMN,
    batch_size: int = DEFAULT_BATCH_SIZE
) -> pd.DataFrame:
    """
    执行完整的情感分析流程
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        text_column: 文本列名
        batch_size: 批处理大小
        
    Returns:
        处理后的数据框
    """
    # 1. 加载数据
    df = load_cleaned_data(input_file, text_column)
    
    # 2. 加载模型
    sentiment_pipeline = load_sentiment_model()
    
    # 3. 获取文本列表
    texts = df[text_column].astype(str).tolist()
    
    # 4. 进行情感分析
    sentiment_results = analyze_sentiment_batch(texts, sentiment_pipeline, batch_size)
    
    # 5. 添加情感分数
    df_with_sentiment = add_sentiment_scores(df, sentiment_results, text_column)
    
    # 6. 保存结果
    save_results(df_with_sentiment, output_file)
    
    return df_with_sentiment


def main():
    """
    命令行入口函数
    """
    parser = argparse.ArgumentParser(description="为新闻数据添加情感分数")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT_FILE, help="输入文件路径")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_FILE, help="输出文件路径")
    parser.add_argument("--text_column", "-t", default=DEFAULT_TEXT_COLUMN, help="文本列名")
    parser.add_argument("--batch_size", "-b", type=int, default=DEFAULT_BATCH_SIZE, help="批处理大小")
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
        # 执行情感分析
        df_result = process_sentiment_analysis(
            input_file=args.input,
            output_file=args.output,
            text_column=args.text_column,
            batch_size=args.batch_size
        )
        
        print(f"\n✅ 情感分析完成!")
        print(f"📊 处理记录数: {len(df_result)}")
        print(f"📈 情感分数范围: {df_result['sentiment_score'].min():.3f} 到 {df_result['sentiment_score'].max():.3f}")
        print(f"📁 结果已保存到: {args.output}")
        
    except Exception as e:
        logging.error(f"情感分析失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())