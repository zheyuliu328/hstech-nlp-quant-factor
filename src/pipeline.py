import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sentiment_lm import lm_score_news              # 仍保留 L&M 作为 fallback
from factors import daily_factor_from_headlines
from eval import add_fwd_return, ic_by_day, monthly_summary
from backtest.vectorized import make_deciles_nav, plot_deciles
from analysis.factor_corr import run_factor_corr

ROOT = Path(__file__).resolve().parents[1]

def maybe_filter_universe(df: pd.DataFrame) -> pd.DataFrame:
    univ_path = ROOT / "data" / "universe" / "hstech_current_constituents.csv"
    if univ_path.exists():
        univ = pd.read_csv(univ_path, dtype={"symbol":"string"})
        if "code" in df.columns:
            df = df[df["code"].astype("string").isin(univ["symbol"])]
    return df

def load_prices():
    prices = pd.read_csv(ROOT / "data" / "prices.csv", dtype={"code":"string"})
    prices["date"] = pd.to_datetime(prices["date"]).dt.strftime("%Y-%m-%d")
    prices = maybe_filter_universe(prices)
    return prices

def load_news_or_prescored():
    """
    优先使用你 sentiment.py 的输出：
      data/processed/articles_with_sentiment.csv
      必含列: date, code, sentiment_score
    若不存在，则回退到 data/news.csv + L&M 词典线
    """
    prescored = ROOT / "data" / "processed" / "articles_with_sentiment.csv"
    if prescored.exists():
        df = pd.read_csv(prescored, dtype={"code":"string"})
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df = maybe_filter_universe(df)
        if "sentiment_score" not in df.columns:
            raise ValueError("Pre-scored file found but missing 'sentiment_score' column.")
        # 与下游接口对齐：改名为 score_lm（仅为了复用聚合函数）
        out = df[["date","code","sentiment_score"]].rename(columns={"sentiment_score":"score_lm"})
        return out, True
    else:
        news = pd.read_csv(ROOT / "data" / "news.csv", dtype={"code":"string"})
        news["date"] = pd.to_datetime(news["date"]).dt.strftime("%Y-%m-%d")
        news = maybe_filter_universe(news)
        scored = lm_score_news(
            news,
            str(ROOT / "data" / "lm_positive.txt"),
            str(ROOT / "data" / "lm_negative.txt"),
        )
        return scored, False

def main():
    scored, used_prescored = load_news_or_prescored()
    prices = load_prices()

    # headline 级别 → (date, code) 聚合 → 横截面 winsorize + z-score
    factors = daily_factor_from_headlines(scored)   # -> columns: date, code, factor_lm
    rets = add_fwd_return(prices)                   # -> adds ret_fwd_1d
    ic_daily = ic_by_day(factors, rets)             # -> daily IC/Rank-IC
    ic_month = monthly_summary(ic_daily)            # -> monthly avg + t

    # 保存报表
    reports = ROOT / "reports"; figs = reports / "figs"
    reports.mkdir(exist_ok=True); figs.mkdir(exist_ok=True, parents=True)
    ic_daily.to_csv(reports / "ic_daily.csv", index=False)
    ic_month.to_csv(reports / "ic_monthly.csv", index=False)

    # 图1：IC 时序（叠加月均虚线）
    plt.figure(figsize=(9,4.5))
    if not ic_daily.empty:
        plt.plot(pd.to_datetime(ic_daily["date"]), ic_daily["IC"], marker="o", linewidth=1)
    m = ic_month.copy()
    if not m.empty:
        plt.hlines(m["IC_mean"], xmin=pd.to_datetime(m["month"] + "-01"),
                   xmax=pd.to_datetime(m["month"] + "-28"), linestyles="dashed")
    title_suffix = " (pre-scored)" if used_prescored else " (lexicon)"
    plt.title("Daily IC" + title_suffix)
    plt.xlabel("Date"); plt.ylabel("IC"); plt.tight_layout()
    plt.savefig(figs / "ic_timeseries.png", dpi=160); plt.close()

    # 图2：Q1…Q5 分层净值
    nav_cum = make_deciles_nav(factors, rets, n_deciles=5)
    if not nav_cum.empty:
        nav_cum.to_csv(reports / "deciles_nav.csv")
        plot_deciles(nav_cum, figs / "deciles.png")

    # 图3：相关性热力图 vs Momentum/Size/Value
    try:
        univ = pd.read_csv(ROOT / "data" / "universe" / "hstech_current_constituents.csv")
        _corrs = run_factor_corr(factors, prices, univ, reports)
        print("[corr] style correlations:", _corrs)
    except Exception as e:
        print("[corr] skipped due to:", e)

    print("[pipeline] used prescored sentiment:", used_prescored)
    print("IC Daily head:"); print(ic_daily.head())
    print("\nMonthly summary:"); print(ic_month)

if __name__ == "__main__":
    main()
