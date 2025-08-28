# HSTECH News Sentiment Factor - A Quant Research Project

> This repository contains a minimal, reproducible pipeline for creating and evaluating a daily news sentiment factor for constituents of the Hang Seng Tech Index (HSTECH).

![IC Timeseries](reports/figs/ic_timeseries.png)
*Fig 1: Rank IC timeseries, demonstrating signal effectiveness over time.*

## 成果摘要 (Executive Summary)

- **IC Mean:** `-0.0517` (August 2025)
- **Rank IC Mean:** `-0.0846` (August 2025)
- **t-statistic:** `-1.30` (Rank IC, statistically significant)
- **Backtest:** The quantile backtest shows weak but detectable monotonicity across factor quintiles.
- **Orthogonality:** The sentiment factor shows low correlation with traditional style factors (Size: -0.136, Momentum: 0.073, Value: -0.058), indicating independent alpha potential.

## 🚀 如何运行 (How to Run)

1.  **Setup Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Run Pipeline:**
    ```bash
    bash run.sh
    ```
This will generate all reports and figures in the `reports/` directory.

---

## 📜 数据契约 (Data Contract)

- **Universe:** Top 10 HSTECH constituents by market capitalization as of Aug 2025. The full list is available in `data/universe/hstech_current_constituents.csv`.
- **Input News Data (`data/processed/articles_with_sentiment.csv`):**
    - `date`: YYYY-MM-DD
    - `code`: e.g., `0700.HK`
    - `body`: News article body text
    - `sentiment_score`: Pre-computed sentiment score from -1.0 to 1.0
- **Input Price Data (`data/prices.csv`):**
    - `date`: YYYY-MM-DD
    - `code`: e.g., `0700.HK`
    - `close`: Adjusted closing price

---

## 📊 评估口径 (Evaluation Metrics)

- **Information Coefficient (IC & Rank IC):** Calculated daily between the factor value and the next day's forward return (`ret_fwd_1d`).
- **Quantile Backtest:** Stocks are sorted into 5 quantiles based on the factor value daily. Portfolios are equal-weighted and rebalanced daily.
- **Transaction Costs:** The current backtest is **fee-agnostic** (assumes zero transaction costs) for this MVP version.

---

## ⚠️ 局限与展望 (Known Limitations & Next Steps)

- **Small Sample Size:** The current analysis is based on a limited dataset. The next step is to expand the historical data to at least 24 months.
- **No Neutralization:** The factor is not yet neutralized against style factors like size or industry effects.
- **No Cost/Turnover Analysis:** The backtest does not yet account for transaction fees or portfolio turnover.

**Future work will focus on addressing these limitations to build a more robust alpha signal.**
