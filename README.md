# Hong Kong Equities NLP Sentiment Factor

[![CI](https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml/badge.svg)](https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

An end-to-end, reproducible research system for a news sentiment factor in the Hong Kong equity market. The pipeline automates the entire workflow from data ingestion to factor backtesting and reporting.

![IC Timeseries](reports/figs/ic_timeseries.png)
![Quantile Backtest](reports/figs/deciles.png)
![Style Correlation](reports/figs/corr_heatmap.png)

---

### 🚀 Project Overview

This project investigates a core question: does public news sentiment hold predictive power in the Hong Kong stock market? To answer this, I've built a reproducible, end-to-end quantitative research pipeline that:

- Covers the entire Hang Seng Composite Index (~500 stocks), ingesting and cleaning multi-lingual news.
- Employs a dual-engine sentiment scoring model (Transformer + Financial Lexicon).
- Constructs and validates the sentiment factor using standard quantitative techniques (IC, Quantile Backtests, Style Analysis).

The primary finding is a consistent **mean-reverting signal** (negative correlation with forward returns), which is more pronounced in small-cap and tech stocks. The factor also exhibits low correlation to traditional style factors, suggesting its potential as an independent alpha source.

### ✨ Key Features

- **One-Click Execution**: `run.sh` handles the entire pipeline from data processing to generating final results.
- **Dual-Engine Sentiment Analysis**: Combines the deep semantic understanding of **Transformer models (RoBERTa/FinBERT)** with the stability of a **financial lexicon** for robust multi-lingual analysis.
- **Configuration-Driven**: Easily manage data sources, model weights, and parameters via a central `config/hk_market.yaml`.
- **Optimized Data & Compute**: Uses a layered **DuckDB** warehouse for data management and vectorized operations for high-performance computation.

### 🏁 Quick Start

```bash
# 1. Set up the environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the end-to-end pipeline
bash run.sh
```
The three core charts will be generated in the `reports/figs/` directory.

### 📈 Findings & Roadmap

#### Key Metrics (Sampled)
- **Rank IC**: Approx. **-0.08** (consistent negative signal)
- **T-statistic**: Approx. **-1.3**
- **Information Ratio (IR)**: Approx. **-0.39**
- Low correlation with traditional style factors, confirming its potential as a diversifying alpha source.

#### Current Limitations
- Historical backtest period needs expansion (target: >24 months).
- Backtest does not yet account for transaction costs, slippage, or turnover constraints.
- Risk neutralization (industry, style factors) needs to be more systematic.

#### Next Steps (P0)
- Expand historical dataset and implement data contract assertions.
- Integrate a **Barra-style risk model** for systematic factor neutralization.
- Incorporate transaction costs and turnover constraints into the vectorized backtester.

<details>
<summary>💻 Click to view Detailed Commands & Technical Specifications</summary>

(Place your detailed commands and specs here; previously folded content can be moved into this section.)

</details>
