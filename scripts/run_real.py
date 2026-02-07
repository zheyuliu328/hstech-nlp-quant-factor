#!/usr/bin/env python3
"""
NLP Factor Run-Real Mode
支持用户提供新闻 CSV 进行因子构建
"""
import argparse
import json
import os
import sys
import pandas as pd
from datetime import datetime

def validate_news_csv(csv_path: str) -> dict:
    """验证新闻 CSV 格式"""
    required_columns = ['date', 'headline', 'stock_code']
    
    if not os.path.exists(csv_path):
        return {'valid': False, 'error': f'File not found: {csv_path}'}
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return {'valid': False, 'error': f'Cannot read CSV: {e}'}
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return {'valid': False, 'error': f'Missing columns: {missing}'}
    
    return {'valid': True, 'rows': len(df), 'columns': list(df.columns)}

def run_factor_build(csv_path: str, output_dir: str = 'reports') -> dict:
    """运行因子构建流程"""
    validation = validate_news_csv(csv_path)
    if not validation['valid']:
        print(f"[ERROR] Validation failed: {validation['error']}")
        sys.exit(1)
    
    print(f"[INFO] Validated {validation['rows']} news items")
    
    df = pd.read_csv(csv_path)
    
    # Mock sentiment scoring (in real implementation, use trained model)
    df['sentiment_score'] = df['headline'].apply(
        lambda x: 0.5 if 'profit' in str(x).lower() else -0.5 if 'loss' in str(x).lower() else 0.0
    )
    
    # Aggregate by date and stock
    daily_factors = df.groupby(['date', 'stock_code'])['sentiment_score'].mean().reset_index()
    daily_factors.columns = ['date', 'stock_code', 'sentiment_factor']
    
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    report = {
        'run_id': run_id,
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'input_file': csv_path,
        'news_items_processed': len(df),
        'unique_stocks': daily_factors['stock_code'].nunique(),
        'date_range': [daily_factors['date'].min(), daily_factors['date'].max()]
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, f'factor_report_{run_id}.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    factors_path = os.path.join(output_dir, f'daily_factors_{run_id}.csv')
    daily_factors.to_csv(factors_path, index=False)
    
    print(f"[OK] Report saved: {report_path}")
    print(f"[OK] Factors saved: {factors_path}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description='NLP Factor Run-Real Mode')
    parser.add_argument('csv', help='Input news CSV file path')
    parser.add_argument('--output', '-o', default='reports', help='Output directory')
    parser.add_argument('--validate-only', action='store_true', help='Only validate')
    
    args = parser.parse_args()
    
    if args.validate_only:
        result = validate_news_csv(args.csv)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['valid'] else 1)
    
    run_factor_build(args.csv, args.output)

if __name__ == '__main__':
    main()
