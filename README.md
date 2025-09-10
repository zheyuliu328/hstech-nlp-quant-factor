# Hong Kong Equities NLP Sentiment Factor

[![CI](https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml/badge.svg)](https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

This repository contains an end-to-end, reproducible research pipeline for a news sentiment factor in the Hong Kong equity market. The system automates the entire workflow from data ingestion to factor backtesting and reporting.

| IC Timeseries | Quantile Backtest | Style Correlation |
| :---: | :---: | :---: |
| <img src="reports/figs/ic_timeseries.png" width="250"/> | <img src="reports/figs/deciles.png" width="250"/> | <img src="reports/figs/corr_heatmap.png" width="250"/> |

---

## Project Overview

This project develops and tests a quantitative hypothesis: does public news sentiment hold predictive power in the Hong Kong stock market? To answer this, I have built a reproducible, end-to-end research pipeline that:

- Covers the entire Hang Seng Composite Index (~500 stocks), ingesting and cleaning multi-lingual news data.
- Employs a dual-engine sentiment scoring model, combining a Transformer-based model with a financial lexicon.
- Constructs and validates the sentiment factor using standard quantitative techniques (Information Coefficient, Quantile Backtests, and Style Factor Analysis).

The primary finding is a consistent **mean-reverting signal** (a negative correlation with forward returns), which is more pronounced in small-cap and tech stocks. The factor also exhibits a low correlation to traditional style factors, suggesting its potential as a source of independent alpha.

## Key Features

- **End-to-End Automation**: A single `run.sh` script handles the entire pipeline from data processing to generating final results and visualizations.
- **Dual-Engine Sentiment Analysis**: Combines the deep semantic understanding of **Transformer models (RoBERTa/FinBERT)** with the stability of a **financial lexicon** for robust multi-lingual analysis.
- **Configuration-Driven**: Key parameters such as data sources, model weights, and lookback windows are managed via a central `config/hk_market.yaml`.
- **Optimized Data & Compute**: Utilizes a layered **DuckDB** data warehouse for efficient queries and vectorized **Pandas/NumPy** operations for high-performance computation.

## Quick Start

```bash
# 1. Set up the virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the end-to-end pipeline
bash run.sh
```
The resulting charts and analysis files will be generated in the `reports/` directory.

## Findings & Roadmap

#### Key Metrics (Sampled)
- **Rank IC**: Approx. **-0.08** (consistent negative signal)
- **T-statistic**: Approx. **-1.3**
- **Information Ratio (IR)**: Approx. **-0.39**
- Low correlation with traditional style factors, confirming its potential as a diversifying alpha source.

#### Current Limitations
- The historical backtest period requires expansion (target: >24 months) for robust validation across different market regimes.
- The current backtest does not account for transaction costs, slippage, or portfolio turnover constraints.
- Risk neutralization against industry and style factors needs to be implemented more systematically.

#### Next Steps
- Expand the historical dataset and implement data contract assertions for quality control.
- Integrate a **Barra-style risk model** for systematic factor neutralization to isolate pure alpha.
- Incorporate realistic transaction cost models into the vectorized backtester to generate net performance metrics.

<details>
<summary><strong>Advanced Usage & Technical Details</strong></summary>

While `bash run.sh` is the main entry point, the pipeline consists of modular scripts that can be executed independently for debugging or specific tasks.

```bash
# Universe management (HSCI example)
python src/hk_universe_builder.py --output-dir data/universe/hk/

# Price download for a given universe
python src/download_hk_prices.py --universe-file data/universe/hk/hsci_constituents.csv

# News ingestion (EventRegistry)
python src/data_pipe.py --universe_file data/universe/hk/hsci_constituents.csv --recent_pages 2

# Sentiment analysis (Transformer + lexicon pipeline)
python src/sentiment_top.py --input-file news_out/hk/hk_news_latest.csv --output-file data/processed/hk/hk_sentiment_analysis.csv

# Factor generation and standardization
python src/hk_factor_generator.py --sentiment-file data/processed/hk/hk_sentiment_analysis.csv --price-file data/hk_prices.csv --standardize

# Factor validation (IC, quantiles)
python src/validate_factor.py
```

</details>
