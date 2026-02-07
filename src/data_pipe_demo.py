#!/usr/bin/env python3
"""
data_pipe_demo.py - Demo mode data loader
Loads sample data without requiring API key
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_sample_news():
    """Load sample news data from JSONL"""
    sample_path = Path(__file__).parent.parent / "data" / "sample" / "news_sample.jsonl"
    
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample data not found: {sample_path}")
    
    with open(sample_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def load_sample_prices():
    """Load sample price data from CSV"""
    sample_path = Path(__file__).parent.parent / "data" / "sample" / "prices_sample.csv"
    
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample data not found: {sample_path}")
    
    return pd.read_csv(sample_path, parse_dates=['date'])

def run_demo_pipeline():
    """Run complete demo pipeline with sample data"""
    print("🎮 Running DEMO mode with sample data...")
    print("=" * 50)
    
    # Load sample data
    news_data = load_sample_news()
    prices_df = load_sample_prices()
    
    print(f"✓ Loaded {len(news_data)} sample news articles")
    print(f"✓ Loaded {len(prices_df)} price records")
    
    # Simulate sentiment analysis (using ground truth for demo)
    results = []
    for article in news_data:
        results.append({
            'date': article['date'],
            'ticker': '00700.HK',  # Simplified for demo
            'sentiment': article.get('sentiment_gt', 'neutral'),
            'title': article['title']
        })
    
    # Save to reports
    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "demo_sentiment_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Results saved to: {output_file}")
    print("=" * 50)
    print("✅ Demo pipeline complete!")
    
    return results

if __name__ == "__main__":
    run_demo_pipeline()
