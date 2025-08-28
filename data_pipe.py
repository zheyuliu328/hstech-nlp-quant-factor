    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_pipe.py
---------------------------------
Event Registry (NewsAPI.ai) ingestion pipeline with:
- stock/keyword loop
- recent (last 30 days) + historical by year
- pagination with token-aware budgeting
- de-duplication (by article 'uri' and URL hash)
- checkpoint/resume
- clean JSONL and CSV outputs

Usage
-----
1) Install deps:
   pip install eventregistry pandas python-dateutil

2) Set API key (recommended via env var):
   export ER_API_KEY="YOUR_API_KEY"

3) Run (examples):
   python data_pipe.py --symbols 0700.HK 9988.HK --years 2024 2023 --recent_pages 2 --archive_pages 2
   python data_pipe.py --keywords "Tencent OR 0700.HK" --years 2022 2021 --archive_pages 3

Notes
-----
- Token rules (per official docs, 2025-08):
  * Recent (last 30 days) Article search: 1 token / page (<=100 articles)
  * Archive (since 2014) Article search: 5 tokens / year / page (<=100 articles)
- Each page fetch is a separate "search" operation.
- This script keeps a checkpoint and a seen set to avoid re-pulling duplicates.

Author: ChatGPT (Market Alpha: NLP-Driven Factor Study)
"""

import argparse
import csv
import hashlib
import json
import logging
import os
import sys
import time
import random
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

def with_retries(fn, *, max_retries=3, base=1.5):
    for i in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            if i == max_retries:
                raise
            sleep = (base ** i) + random.random()
            logging.warning("Call failed (%s). retry %d/%d in %.1fs", e.__class__.__name__, i+1, max_retries, sleep)
            time.sleep(sleep)
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional

import pandas as pd
from dateutil import tz

def log_run_metrics(out_dir, *, mode, symbols, years, recent_pages, archive_pages,
                    items_written_recent, items_written_archive,
                    tokens_recent_est, tokens_archive_est, extra=None):
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    row = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,                               # recent / archive / mixed
        "symbols": ",".join(symbols or []),
        "years": ",".join(map(str, years or [])),
        "recent_pages": recent_pages or 0,
        "archive_pages": archive_pages or 0,
        "items_recent": items_written_recent or 0,
        "items_archive": items_written_archive or 0,
        "tokens_recent_est": tokens_recent_est or 0,
        "tokens_archive_est": tokens_archive_est or 0,
        "extra": extra or ""
    }
    f = Path(out_dir) / "run_metrics.csv"
    new = not f.exists()
    with f.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row.keys()))
        if new: w.writeheader()
        w.writerow(row)

try:
    from eventregistry import EventRegistry, QueryArticlesIter, RequestArticlesInfo
    from dotenv import load_dotenv
    load_dotenv()  # 加载 .env 文件
except Exception as e:
    print("Failed to import 'eventregistry'. Install it first: pip install eventregistry", file=sys.stderr)
    raise

# ----------------------- Configuration -----------------------

DEFAULT_OUTDIR = "news_out"
CHECKPOINT_FILE = "checkpoint.json"
SEEN_FILE = "seen_uris.jsonl"

# ----------------------- Utilities -----------------------

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def now_iso() -> str:
    return datetime.now(tz=tz.tzlocal()).isoformat(timespec="seconds")

def write_jsonl(path: str, items: Iterable[Dict[str, Any]]) -> int:
    n = 0
    with open(path, "a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            n += 1
    return n

def to_rows_for_csv(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for a in articles:
        rows.append({
            "uri": a.get("uri"),
            "url": a.get("url"),
            "title": a.get("title"),
            "body": a.get("body"),
            "lang": a.get("lang"),
            "source_title": (a.get("source") or {}).get("title"),
            "dateTime": a.get("dateTime"),
            "date": a.get("date"),
            "time": a.get("time"),
        })
    return rows

def write_csv(path: str, rows: List[Dict[str, Any]]) -> int:
    if not rows:
        return 0
    fieldnames = list(rows[0].keys())
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)

# ----------------------- Token Estimator -----------------------

def estimate_tokens_recent(pages:int) -> int:
    # 1 token per page (<=100 articles) for last-30-days
    return max(0, int(pages))

def estimate_tokens_archive(pages:int, years:int) -> int:
    # 5 tokens per year per page
    return max(0, 5 * int(years) * int(pages))

# ----------------------- Fetchers -----------------------

def build_req(return_body: bool = True, return_concepts: bool = True) -> RequestArticlesInfo:
    from eventregistry import ReturnInfo
    returnInfo = ReturnInfo()
    returnInfo.articleInfo.body = return_body
    returnInfo.articleInfo.concepts = return_concepts
    return RequestArticlesInfo(returnInfo=returnInfo)

def pull_articles_iter(
    er: EventRegistry,
    keywords: str,
    lang: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    is_duplicate_filter: str = "skipDuplicates",
    max_items: int = 100,
) -> Iterable[Dict[str, Any]]:
    it = QueryArticlesIter(
        keywords=keywords,
        lang=lang,
        isDuplicateFilter=is_duplicate_filter,
        dataType=["news"],
        dateStart=date_start,
        dateEnd=date_end,
    )
    req = build_req(return_body=True, return_concepts=True)
    for art in it.execQuery(er, maxItems=max_items, req=req):
        yield art

@dataclass
class PipeConfig:
    keywords: Optional[str]
    symbols: List[str]
    years: List[int]
    recent_pages: int
    archive_pages: int
    lang: Optional[str]
    outdir: str
    sleep_sec: float = 0.4

@dataclass
class PipeState:
    run_started_at: str
    last_written_recent: int = 0
    last_written_archive: int = 0

# ----------------------- Pipeline -----------------------

class NewsPipeline:
    def __init__(self, api_key: str, cfg: PipeConfig):
        self.er = EventRegistry(apiKey=api_key)
        self.cfg = cfg
        ensure_dir(cfg.outdir)
        self.ckpt_path = os.path.join(cfg.outdir, CHECKPOINT_FILE)
        self.seen_path = os.path.join(cfg.outdir, SEEN_FILE)
        self.recent_jsonl = os.path.join(cfg.outdir, "articles_recent.jsonl")
        self.archive_jsonl = os.path.join(cfg.outdir, "articles_archive.jsonl")
        self.recent_csv = os.path.join(cfg.outdir, "articles_recent.csv")
        self.archive_csv = os.path.join(cfg.outdir, "articles_archive.csv")

        self.state = self._load_state()
        self.seen_uris = self._load_seen()

    # ---------- state ----------
    def _load_state(self) -> PipeState:
        if os.path.exists(self.ckpt_path):
            with open(self.ckpt_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PipeState(**data)
        return PipeState(run_started_at=now_iso())

    def _save_state(self) -> None:
        with open(self.ckpt_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.state), f, ensure_ascii=False, indent=2)

    # ---------- seen set ----------
    def _load_seen(self) -> set:
        seen = set()
        if os.path.exists(self.seen_path):
            with open(self.seen_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        uri = obj.get("uri")
                        if uri:
                            seen.add(uri)
                    except:
                        pass
        return seen

    def _append_seen(self, articles: List[Dict[str, Any]]):
        # append minimal objects (uri only) to seen file
        with open(self.seen_path, "a", encoding="utf-8") as f:
            for a in articles:
                uri = a.get("uri")
                if uri:
                    f.write(json.dumps({"uri": uri}) + "\n")

    # ---------- core steps ----------
    def _filter_new(self, arts: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fresh = []
        for a in arts:
            uri = a.get("uri")
            if not uri:
                # fallback to url hash as pseudo-unique id
                url = a.get("url", "")
                if not url:
                    continue
                uri = "urlsha1:" + sha1(url)
                a["uri"] = uri

            if uri in self.seen_uris:
                continue
            self.seen_uris.add(uri)
            fresh.append(a)
        return fresh

    def _pull_pages(self, keywords: str, pages: int, date_start: Optional[str], date_end: Optional[str]) -> List[Dict[str, Any]]:
        all_new = []
        for p in range(pages):
            logging.debug("Fetching page %d for %s ...", p + 1, keywords)
            arts_page = list(pull_articles_iter(
                er=self.er,
                keywords=keywords,
                lang=self.cfg.lang,
                date_start=date_start,
                date_end=date_end,
                is_duplicate_filter="skipDuplicates",
                max_items=100,
            ))
            new_items = self._filter_new(arts_page)
            logging.debug("Got %d items this page; total so far=%d", len(new_items), len(all_new))
            if not new_items and not arts_page:
                # nothing came back — likely no more pages matching
                logging.debug("No more pages matching, stopping")
                break

            all_new.extend(new_items)
            # persist seen incrementally
            self._append_seen(new_items)

            # polite pacing
            time.sleep(self.cfg.sleep_sec)
        return all_new

    # ---------- public runners ----------
    def run_recent(self) -> int:
        total_written = 0
        targets: List[str] = []
        if self.cfg.keywords:
            targets.append(self.cfg.keywords)
        targets.extend(self.cfg.symbols)

        for tgt in targets:
            logging.info("Processing RECENT target: %s", tgt)
            articles = self._pull_pages(
                keywords=tgt,
                pages=self.cfg.recent_pages,
                date_start=None,
                date_end=None,
            )
            if not articles:
                logging.warning("No articles found for target: %s", tgt)
                continue
            logging.info("Writing %d articles for target: %s", len(articles), tgt)
            total_written += write_jsonl(self.recent_jsonl, articles)
            total_written += write_csv(self.recent_csv, to_rows_for_csv(articles))

        self.state.last_written_recent += total_written
        self._save_state()
        return total_written

    def run_archive(self) -> int:
        total_written = 0
        targets: List[str] = []
        if self.cfg.keywords:
            targets.append(self.cfg.keywords)
        targets.extend(self.cfg.symbols)

        years = self.cfg.years or []
        for year in years:
            ds, de = f"{year}-01-01", f"{year}-12-31"
            logging.info("Processing ARCHIVE year: %s (%s to %s)", year, ds, de)
            for tgt in targets:
                logging.info("Processing ARCHIVE target: %s for year %s", tgt, year)
                articles = self._pull_pages(
                    keywords=tgt,
                    pages=self.cfg.archive_pages,
                    date_start=ds, date_end=de
                )
                if not articles:
                    logging.warning("No articles found for target: %s in year %s", tgt, year)
                    continue
                logging.info("Writing %d articles for target: %s in year %s", len(articles), tgt, year)
                total_written += write_jsonl(self.archive_jsonl, articles)
                total_written += write_csv(self.archive_csv, to_rows_for_csv(articles))

        self.state.last_written_archive += total_written
        self._save_state()
        return total_written

# ----------------------- CLI -----------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Event Registry ingestion pipeline")
    ap.add_argument("--keywords", type=str, default=None, help='Free-text keywords, e.g., "Tencent OR 0700.HK"')
    ap.add_argument("--symbols", type=str, nargs="*", default=[], help="List of symbols/keywords to query (space-separated)")
    ap.add_argument("--years", type=int, nargs="*", default=[], help="Historical years to fetch, e.g., 2024 2023 2022")
    ap.add_argument("--recent_pages", type=int, default=0, help="How many pages to fetch for recent (last 30 days). 1 page ≈ up to 100 articles.")
    ap.add_argument("--archive_pages", type=int, default=0, help="How many pages per year to fetch for archive.")
    ap.add_argument("--lang", type=str, default=None, help="Language code (e.g., eng, zho, jpn). Default: all languages.")
    ap.add_argument("--outdir", type=str, default=DEFAULT_OUTDIR, help=f"Output folder (default: {DEFAULT_OUTDIR})")
    ap.add_argument("--debug", action="store_true", help="verbose debug logs")
    ap.add_argument("--estimate_only", action="store_true", help="only print token estimate, do not call API")
    ap.add_argument("--logfile", type=str, default=None, help="write logs to this file")
    ap.add_argument("--max_retries", type=int, default=3, help="max retries for API calls")
    ap.add_argument("--token_cap", type=int, default=400, help="hard stop if estimated tokens > cap for this run")
    ap.add_argument("--universe_file", type=str, default=None, help="CSV file containing stock symbols to process (e.g., data/universe/hstech_current_constituents.csv)")
    return ap.parse_args()

def main():
    api_key = os.getenv("ER_API_KEY")
    if not api_key:
        print("ERROR: Please export ER_API_KEY before running (export ER_API_KEY=...)",
              file=sys.stderr)
        sys.exit(1)

    args = parse_args()
    
    # 统一的日志配置
    log_level = logging.DEBUG if args.debug else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    if args.logfile:
        Path("logs").mkdir(exist_ok=True)
        handlers.append(RotatingFileHandler(args.logfile, maxBytes=5_000_000, backupCount=5, encoding="utf-8"))
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers)
    
    # 处理股票池文件
    symbols = list(args.symbols)  # 复制原有symbols列表
    if args.universe_file:
        if not os.path.exists(args.universe_file):
            logging.error("Universe file not found: %s", args.universe_file)
            sys.exit(1)
        
        try:
            df_universe = pd.read_csv(args.universe_file)
            if 'symbol' not in df_universe.columns:
                logging.error("Universe file must contain 'symbol' column")
                sys.exit(1)
            
            universe_symbols = df_universe['symbol'].tolist()
            symbols.extend(universe_symbols)
            logging.info("Loaded %d symbols from universe file: %s", len(universe_symbols), args.universe_file)
            logging.info("Universe symbols: %s", universe_symbols[:10] + (['...'] if len(universe_symbols) > 10 else []))
            
        except Exception as e:
            logging.error("Failed to read universe file %s: %s", args.universe_file, e)
            sys.exit(1)
    
    cfg = PipeConfig(
        keywords=args.keywords,
        symbols=symbols,  # 使用处理后的symbols
        years=args.years,
        recent_pages=max(0, args.recent_pages),
        archive_pages=max(0, args.archive_pages),
        lang=args.lang,
        outdir=args.outdir,
    )
    pipe = NewsPipeline(api_key=api_key, cfg=cfg)

    # Token budgeting (rough estimate, for your awareness)
    est_recent = estimate_tokens_recent(cfg.recent_pages) * (len(cfg.symbols) + (1 if cfg.keywords else 0))
    est_archive = estimate_tokens_archive(cfg.archive_pages, len(cfg.years)) * (len(cfg.symbols) + (1 if cfg.keywords else 0))
    print(f"[INFO] Estimated tokens -> recent: {est_recent}, archive: {est_archive}, total: {est_recent + est_archive}")
    
    # 在原有"token 估算"打印之后，加：
    logging.info("[PLAN] recent_pages=%s archive_pages=%s years=%s symbols=%s keywords=%s lang=%s",
                 getattr(args, "recent_pages", None), getattr(args, "archive_pages", None),
                 getattr(args, "years", None), getattr(args, "symbols", None),
                 getattr(args, "keywords", None), getattr(args, "lang", None))

    # Token 上限保护
    est_total = (est_recent or 0) + (est_archive or 0)
    if args.token_cap and est_total > args.token_cap and not args.estimate_only:
        logging.error("Estimated tokens %s > token_cap %s. Aborting to protect quota.", est_total, args.token_cap)
        sys.exit(2)

    # 支持"干跑"，只估算token、不真正请求
    if args.estimate_only:
        logging.info("Estimate-only run finished (no API calls).")
        sys.exit(0)

    wrote_recent = 0
    wrote_archive = 0
    if cfg.recent_pages > 0:
        wrote_recent = pipe.run_recent()
        print(f"[DONE] Recent written (jsonl+csv rows): {wrote_recent}")
    if cfg.archive_pages > 0 and cfg.years:
        wrote_archive = pipe.run_archive()
        print(f"[DONE] Archive written (jsonl+csv rows): {wrote_archive}")

    print(f"[OK] Outputs at: {cfg.outdir}")
    print(" - recent JSONL:", pipe.recent_jsonl)
    print(" - archive JSONL:", pipe.archive_jsonl)
    print(" - recent CSV   :", pipe.recent_csv)
    print(" - archive CSV  :", pipe.archive_csv)
    print(" - checkpoint   :", pipe.ckpt_path)
    print(" - seen         :", pipe.seen_path)
    
    # 记录运行指标
    mode = "mixed" if cfg.recent_pages > 0 and cfg.archive_pages > 0 else ("recent" if cfg.recent_pages > 0 else "archive")
    universe_info = f"universe={args.universe_file}" if args.universe_file else "manual"
    log_run_metrics(
        out_dir="news_out",
        mode=mode,
        symbols=symbols,  # 使用处理后的symbols
        years=args.years,
        recent_pages=args.recent_pages,
        archive_pages=args.archive_pages,
        items_written_recent=wrote_recent,
        items_written_archive=wrote_archive,
        tokens_recent_est=est_recent,
        tokens_archive_est=est_archive,
        extra=f"lang={args.lang or 'all'}, {universe_info}"
    )

if __name__ == "__main__":
    main()
