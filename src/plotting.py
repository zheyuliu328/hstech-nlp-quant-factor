import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_ic_timeseries(ic_daily_path: Path, ic_monthly_path: Path, output_path: Path):
    """
    绘制IC时间序列图，并叠加月度均值。
    """
    try:
        ic_daily = pd.read_csv(ic_daily_path, parse_dates=['date'])
        ic_monthly = pd.read_csv(ic_monthly_path)
        logging.info(f"成功读取IC数据: {ic_daily_path} 和 {ic_monthly_path}")
    except FileNotFoundError as e:
        logging.error(f"IC数据文件未找到: {e}")
        return

    # 使用兼容的样式名称
    try:
        plt.style.use('seaborn-v0_8-grid')
    except OSError:
        try:
            plt.style.use('seaborn')
        except OSError:
            plt.style.use('default')  # 如果都失败，使用默认样式
    
    fig, ax = plt.subplots(figsize=(12, 6))

    # 绘制每日IC散点图
    ax.plot(ic_daily['date'], ic_daily['RankIC'], 
            alpha=0.6, linestyle='none', marker='.', markersize=5, label='Daily Rank IC')
    
    # 绘制每日IC的30天移动平均线
    ax.plot(ic_daily['date'], ic_daily['RankIC'].rolling(window=30, min_periods=10).mean(), 
            color='red', linewidth=2, label='30-Day Moving Average')

    # 绘制月度IC均值水平线
    for _, row in ic_monthly.iterrows():
        month_start = pd.to_datetime(f"{row['month']}-01")
        # hlines 对于每个月绘制一条水平线
        ax.hlines(y=row['RankIC_mean'], xmin=month_start, 
                  xmax=month_start + pd.offsets.MonthEnd(1), 
                  color='black', linestyle='--', linewidth=2)

    ax.axhline(0, color='gray', linestyle=':', linewidth=1.5)
    ax.set_title('Rank IC Timeseries (Daily with 30D MA & Monthly Mean)', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Rank IC', fontsize=12)
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logging.info(f"✅ 图一 (IC时序图) 已保存至: {output_path}")

if __name__ == '__main__':
    # 这是一个可以直接运行此文件进行测试的入口
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    FIGS_DIR = REPORTS_DIR / "figs"

    plot_ic_timeseries(
        ic_daily_path=REPORTS_DIR / "ic_daily.csv",
        ic_monthly_path=REPORTS_DIR / "ic_monthly.csv",
        output_path=FIGS_DIR / "ic_timeseries.png"
    )
