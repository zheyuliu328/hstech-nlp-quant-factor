#!/usr/bin/env bash
set -euo pipefail
python src/data_pipe.py --symbols 0700.HK --recent_pages 1 --estimate_only
python src/data_pipe.py --symbols 0700.HK --recent_pages 1 --token_cap 50 --debug --logfile logs/smoke.log
python - <<'PY'
import os, pandas as pd; 
f="news_out/run_metrics.csv"
assert os.path.exists(f), "run_metrics.csv missing"
df=pd.read_csv(f); 
assert len(df)>=1, "no metrics rows"
print("Smoke OK. last row:", df.tail(1).to_dict(orient="records")[0])
PY
