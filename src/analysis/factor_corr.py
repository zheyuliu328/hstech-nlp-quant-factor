# src/analysis/factor_corr.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

def create_style_factors(prices_df: pd.DataFrame, universe_df: pd.DataFrame) -> pd.DataFrame:
    """从价格和市值数据创建基础的风格因子代理"""
    # 动量 Momentum (过去20天收益)
    prices_df = prices_df.sort_values(by=['code', 'date'])
    prices_df['momentum'] = prices_df.groupby('code')['close'].pct_change(periods=20).shift(1)
    
    # 合并市值 Size
    style_df = pd.merge(prices_df, universe_df[['symbol', 'market_cap']], left_on='code', right_on='symbol', how='left')
    style_df['size'] = np.log(style_df['market_cap'])
    
    # 价值 Value (简单的市净率代理 E/P)
    style_df['value'] = 1 / style_df['close'] # 这是一个非常粗糙的代理
    
    return style_df[['date', 'code', 'momentum', 'size', 'value']]

def run_style_correlation_analysis(factor_df: pd.DataFrame, prices_df: pd.DataFrame, universe_df: pd.DataFrame, output_path: Path):
    """计算情绪因子与风格因子的相关性并绘制热力图"""
    style_factors = create_style_factors(prices_df, universe_df)
    
    merged_df = pd.merge(factor_df, style_factors, on=['date', 'code'], how='inner')
    
    # 计算相关性矩阵
    correlation_matrix = merged_df[['factor_value', 'momentum', 'size', 'value']].corr()
    sentiment_correlations = correlation_matrix[['factor_value']].drop('factor_value')

    # 绘制热力图
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(6, 8))
    
    cax = ax.matshow(sentiment_correlations, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    
    ax.set_xticks(np.arange(1))
    ax.set_yticks(np.arange(len(sentiment_correlations.index)))
    ax.set_xticklabels(['Sentiment Factor'])
    ax.set_yticklabels(sentiment_correlations.index)
    
    # 在格子上标注数值
    for (i, j), val in np.ndenumerate(sentiment_correlations):
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', color='white' if abs(val) > 0.5 else 'black')

    ax.set_title('Correlation with Style Factors', pad=20)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logging.info(f"✅ 图三 (风格相关性热力图) 已保存至: {output_path}")

if __name__ == '__main__':
    ROOT = Path(__file__).resolve().parent.parent.parent
    REPORTS_DIR = ROOT / "reports"
    FIGS_DIR = REPORTS_DIR / "figs"
    
    factors = pd.read_csv(REPORTS_DIR / "daily_sentiment_factors.csv")
    prices = pd.read_csv(ROOT / "data" / "prices.csv")
    universe = pd.read_csv(ROOT / "data" / "universe" / "hstech_current_constituents.csv")
    
    run_style_correlation_analysis(
        factor_df=factors,
        prices_df=prices,
        universe_df=universe,
        output_path=FIGS_DIR / "corr_heatmap.png"
    )
