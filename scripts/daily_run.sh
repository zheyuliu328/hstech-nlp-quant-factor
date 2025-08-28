#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python data_pipe.py --symbols 0700.HK 9988.HK 3690.HK --recent_pages 2 --token_cap 120 --debug --logfile "logs/daily-$(date +%F).log"
python - <<'PY'
import pandas as pd; m=pd.read_csv("news_out/run_metrics.csv").tail(1).to_dict(orient="records")[0]
print("DAILY OK:", m)
PY
