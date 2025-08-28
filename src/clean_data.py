#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_data.py
---------------------------------
数据清洗模块：专门负责清洗从 data_pipe.py 抓取到的原始新闻数据

功能包括：
- 去除HTML标签和特殊字符
- 统一日期格式
- 文本去重和去空
- 语言检测和过滤
- 数据质量检查

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import re
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import html
import unicodedata


def clean_html_tags(text: str) -> str:
    """
    去除HTML标签和实体字符
    
    Args:
        text: 原始文本
        
    Returns:
        清洗后的文本
    """
    if not isinstance(text, str):
        return ""
    
    # 解码HTML实体
    text = html.unescape(text)
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def normalize_unicode(text: str) -> str:
    """
    标准化Unicode字符
    
    Args:
        text: 原始文本
        
    Returns:
        标准化后的文本
    """
    if not isinstance(text, str):
        return ""
    
    # 标准化Unicode字符
    text = unicodedata.normalize('NFKC', text)
    
    # 去除控制字符
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')
    
    return text


def clean_text_content(text: str) -> str:
    """
    综合文本清洗
    
    Args:
        text: 原始文本
        
    Returns:
        清洗后的文本
    """
    if not isinstance(text, str):
        return ""
    
    # 去除HTML标签
    text = clean_html_tags(text)
    
    # 标准化Unicode
    text = normalize_unicode(text)
    
    # 去除多余的换行符和空格
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def normalize_datetime(date_str: str, time_str: str = None) -> Optional[datetime]:
    """
    统一日期时间格式
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        time_str: 时间字符串 (HH:MM:SS)
        
    Returns:
        标准化的datetime对象，如果解析失败返回None
    """
    try:
        if time_str and str(time_str).lower() not in ['nan', 'none', '']:
            datetime_str = f"{date_str} {time_str}"
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def detect_language(text: str) -> str:
    """
    简单的语言检测（基于字符类型）
    
    Args:
        text: 文本内容
        
    Returns:
        语言代码：'zh' (中文), 'en' (英文), 'ko' (韩文), 'other' (其他)
    """
    if not isinstance(text, str) or len(text) < 10:
        return 'other'
    
    # 统计不同字符类型的数量
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text)
    
    # 计算比例
    chinese_ratio = chinese_chars / total_chars
    korean_ratio = korean_chars / total_chars
    english_ratio = english_chars / total_chars
    
    # 判断主要语言
    if chinese_ratio > 0.3:
        return 'zh'
    elif korean_ratio > 0.3:
        return 'ko'
    elif english_ratio > 0.5:
        return 'en'
    else:
        return 'other'


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    去除重复记录
    
    Args:
        df: 数据框
        subset: 用于判断重复的列名列表
        
    Returns:
        去重后的数据框
    """
    if subset is None:
        subset = ['uri', 'url', 'title']
    
    # 基于指定列去重
    df_clean = df.drop_duplicates(subset=subset, keep='first')
    
    # 记录去重信息
    removed_count = len(df) - len(df_clean)
    if removed_count > 0:
        logging.info(f"去除了 {removed_count} 条重复记录")
    
    return df_clean


def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    数据质量检查
    
    Args:
        df: 数据框
        
    Returns:
        质量检查报告
    """
    report = {
        'total_rows': len(df),
        'missing_values': {},
        'empty_content': 0,
        'invalid_dates': 0,
        'language_distribution': {}
    }
    
    # 检查缺失值
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            report['missing_values'][col] = missing_count
            # 对于文本列，用空字符串填充NaN
            if col in ['body', 'title', 'summary']:
                df[col] = df[col].fillna('')
            # 对于数值列，用0填充NaN
            elif df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(0)
    
    # 检查空内容
    if 'body' in df.columns:
        report['empty_content'] = (df['body'].str.len() < 10).sum()
    
    # 检查无效日期
    if 'date' in df.columns:
        report['invalid_dates'] = df['date'].isna().sum()
    
    # 语言分布
    if 'body' in df.columns:
        languages = df['body'].apply(detect_language)
        report['language_distribution'] = languages.value_counts().to_dict()
    
    return report


def clean_news_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗新闻数据框
    
    Args:
        df: 原始数据框
        
    Returns:
        清洗后的数据框
    """
    logging.info(f"开始清洗数据，原始记录数: {len(df)}")
    
    # 创建数据副本
    df_clean = df.copy()
    
    # 1. 清洗文本内容
    text_columns = ['title', 'body']
    for col in text_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].apply(clean_text_content)
            logging.info(f"清洗了 {col} 列")
    
    # 2. 统一日期格式
    if 'date' in df_clean.columns and 'time' in df_clean.columns:
        df_clean['datetime_clean'] = df_clean.apply(
            lambda row: normalize_datetime(row['date'], row['time']), axis=1
        )
        logging.info("统一了日期时间格式")
    
    # 3. 添加语言检测
    if 'body' in df_clean.columns:
        df_clean['detected_lang'] = df_clean['body'].apply(detect_language)
        logging.info("添加了语言检测")
    
    # 4. 去除重复记录
    df_clean = remove_duplicates(df_clean)
    
    # 5. 过滤空内容
    if 'body' in df_clean.columns:
        before_count = len(df_clean)
        df_clean = df_clean[df_clean['body'].str.len() >= 10]
        after_count = len(df_clean)
        if before_count != after_count:
            logging.info(f"过滤了 {before_count - after_count} 条空内容记录")
    
    # 6. 数据质量检查
    quality_report = validate_data_quality(df_clean)
    logging.info(f"数据质量报告: {quality_report}")
    
    logging.info(f"清洗完成，最终记录数: {len(df_clean)}")
    
    return df_clean


def clean_and_save_news(
    input_file: str,
    output_file: str = None,
    output_dir: str = "data/processed",
    file_type: str = "csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    清洗新闻数据并保存
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件名（可选）
        output_dir: 输出目录
        file_type: 输出文件类型 ("csv" 或 "json")
        
    Returns:
        (清洗后的数据框, 质量报告)
    """
    # 检查输入文件
    if not Path(input_file).exists():
        raise FileNotFoundError(f"输入文件不存在: {input_file}")
    
    logging.info(f"读取输入文件: {input_file}")
    
    # 读取数据
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.jsonl'):
            df = pd.read_json(input_file, lines=True)
        else:
            raise ValueError(f"不支持的文件格式: {input_file}")
    except Exception as e:
        raise ValueError(f"读取文件失败: {e}")
    
    # 清洗数据
    df_clean = clean_news_dataframe(df)
    
    # 生成输出文件名
    if output_file is None:
        input_name = Path(input_file).stem
        output_file = f"{input_name}_cleaned.{file_type}"
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存清洗后的数据
    full_output_path = output_path / output_file
    
    try:
        if file_type == "csv":
            df_clean.to_csv(full_output_path, index=False, encoding='utf-8')
        elif file_type == "json":
            df_clean.to_json(full_output_path, orient='records', lines=True, force_ascii=False)
        else:
            raise ValueError(f"不支持的输出格式: {file_type}")
        
        logging.info(f"清洗后的数据已保存到: {full_output_path}")
        
    except Exception as e:
        raise ValueError(f"保存文件失败: {e}")
    
    # 生成质量报告
    quality_report = validate_data_quality(df_clean)
    
    return df_clean, quality_report


def main():
    """
    命令行入口函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="清洗新闻数据")
    parser.add_argument("--input", "-i", required=True, help="输入文件路径")
    parser.add_argument("--output", "-o", help="输出文件名")
    parser.add_argument("--output_dir", "-d", default="data/processed", help="输出目录")
    parser.add_argument("--format", "-f", choices=["csv", "json"], default="csv", help="输出格式")
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
        # 执行清洗
        df_clean, quality_report = clean_and_save_news(
            input_file=args.input,
            output_file=args.output,
            output_dir=args.output_dir,
            file_type=args.format
        )
        
        print(f"\n✅ 数据清洗完成!")
        print(f"📊 处理记录数: {quality_report['total_rows']}")
        print(f"🌍 语言分布: {quality_report['language_distribution']}")
        if quality_report['missing_values']:
            print(f"⚠️  缺失值: {quality_report['missing_values']}")
        
    except Exception as e:
        logging.error(f"清洗失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())