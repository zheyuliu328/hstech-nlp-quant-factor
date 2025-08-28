import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

def add_fwd_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """为价格数据计算未来1日收益率"""
    prices_df = prices_df.sort_values(by=['code', 'date'])
    prices_df['ret_fwd_1d'] = prices_df.groupby('code')['close'].shift(-1) / prices_df['close'] - 1
    return prices_df

def run_quantile_backtest(factor_df: pd.DataFrame, prices_df: pd.DataFrame, output_path: Path, n_quantiles: int = 5):
    """
    执行分位数回测并绘制净值曲线图。
    """
    try:
        # 确保因子和价格数据已加载
        if factor_df.empty or prices_df.empty:
            raise ValueError("因子或价格数据为空。")
        logging.info(f"开始分位数回测，使用 {len(factor_df)} 条因子数据和 {len(prices_df)} 条价格数据。")
    except Exception as e:
        logging.error(f"回测数据准备失败: {e}")
        return
        
    prices_with_returns = add_fwd_returns(prices_df)
    
    # 合并因子和未来收益
    merged_df = pd.merge(factor_df, prices_with_returns[['date', 'code', 'ret_fwd_1d']], on=['date', 'code'], how='inner')
    merged_df.dropna(subset=['factor_value', 'ret_fwd_1d'], inplace=True)

    if merged_df.empty:
        logging.warning("合并因子和收益后数据为空，无法进行回测。")
        return
        
    # 按天分组，计算每个分位数的收益
    daily_quantile_returns = merged_df.groupby('date').apply(
        lambda x: x.groupby(pd.qcut(x['factor_value'], n_quantiles, labels=False, duplicates='drop'))['ret_fwd_1d'].mean()
    ).unstack()

    # 确保结果是DataFrame格式
    if isinstance(daily_quantile_returns, pd.Series):
        daily_quantile_returns = daily_quantile_returns.to_frame()
    
    # 计算净值曲线
    nav_curves = (1 + daily_quantile_returns.fillna(0)).cumprod()
    nav_curves.columns = [f'Q{i+1}' for i in range(len(nav_curves.columns))]

    # 绘制图表
    plt.style.use('default')  # 使用默认样式避免兼容性问题
    fig, ax = plt.subplots(figsize=(12, 6))

    for quantile in nav_curves.columns:
        ax.plot(pd.to_datetime(nav_curves.index), nav_curves[quantile], label=quantile)

    ax.set_title(f'Factor Quantile Backtest (Top {n_quantiles} Portfolios)', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Return (NAV)', fontsize=12)
    ax.legend(title='Quantile')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logging.info(f"✅ 图二 (分层回测图) 已保存至: {output_path}")

if __name__ == '__main__':
    ROOT = Path(__file__).resolve().parent.parent.parent
    REPORTS_DIR = ROOT / "reports"
    FIGS_DIR = REPORTS_DIR / "figs"

    # 加载Day 3生成的数据进行测试
    factors = pd.read_csv(REPORTS_DIR / "daily_sentiment_factors.csv")
    prices = pd.read_csv(ROOT / "data" / "prices.csv")
    
    run_quantile_backtest(
        factor_df=factors,
        prices_df=prices,
        output_path=FIGS_DIR / "deciles.png"
    )
