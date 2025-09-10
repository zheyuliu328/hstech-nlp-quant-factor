# 项目当前进度与改进路线图（2025-09）

## 当前状态快照
- **市场/范围**: 港股（HSCI/HSTECH），多语言新闻（繁/简/英），覆盖度高，目录/日志/配置完备
- **数据层**: `data/universe/hk` 成分股、`data/hk_prices.csv` 或仓库价格、`news_out/hk` 新闻原文与增量；DuckDB 分层仓库（bronze/silver/gold）已存在
- **因子层**: 情感分析与多窗因子已实现，含港股特色（北水/本地/监管），截面标准化、正交化与前向收益支持
- **验证层**: IC、分位回测、风格相关性三图已产出；日志、脚本与一键运行基本齐备
- **文档层**: 技术README与实施总结齐全，待统一最新口径与产出对齐

## 关键产出（已具备）
- 代码模块：`src/hk_universe_builder.py`、`src/download_hk_prices.py`、`data_pipe_hk.py`、`src/hk_sentiment_analysis.py`、`src/hk_factor_generator.py`、`src/backtest/vectorized.py`
- 数据产物：`data/processed/hk_*.csv`、`news_out/hk/*.json|csv|jsonl`、`reports/figs/*.png`、`data/warehouse/*/*.parquet`
- 自动化脚本：`scripts/setup_hk_market.sh`、`scripts/run_hk_data_collection.sh`、`run.sh`
- 配置与日志：`config/hk_market.yaml`、`logs/hk_*.log`

## 主要结论（截至当前）
- 情感因子展现出**反向预测**迹象，在小盘/科技股敏感度更高
- 与传统风格因子**低相关**，具备独立Alpha潜力
- MVP 回测未计交易成本；进一步稳健性验证有空间（更长历史、行业中性、费用/换手）

## 风险与已知限制
- 历史样本跨度有限（需≥24个月）；部分数据源稳定性依赖外部站点
- 行业/风格中性与风险模型集成尚未完全体系化
- 交易成本、换手与容量未纳入
- 情绪抽取在繁体长文与同义改写上仍有改进空间

## 优先级改进（P0-P2）
- P0: 扩充历史（≥24月）、完善数据契约与断言；统一`articles_with_sentiment`字段口径
- P0: 行业/风格中性与Barra风格去相关（纳入`src/barra_risk_model.py`）
- P1: 交易费用与换手惩罚接入回测（`src/backtest/vectorized.py` 扩展参数）
- P1: 情绪融合：模型分支（Transformer）+ 词典分支加权与迁移学习微调
- P2: 实时/准实时增量（分钟级）与稳态作业编排，失败重试与监控阈值

## 两周路线图（建议）
- 第1周（数据与验证）
  - 扩展历史价格与新闻至24月，重算因子与IC
  - 落地行业/风格中性与因子正交化验收
  - 引入交易成本参数与基础换手约束
- 第2周（稳健与上线）
  - 横截面稳健性：行业/市值分组、滚动窗口显著性
  - 端到端自动化与指标看板（覆盖率、失败率、IC走势）
  - 文档统一：README/报告口径、命令与产物路径一键校验

## 快速操作清单
- 初始化：`bash scripts/setup_hk_market.sh`
- 全量采集：`bash scripts/run_hk_data_collection.sh`
- 情感分析：`python src/hk_sentiment_analysis.py --input-file news_out/hk/hk_news_latest.csv --output-file data/processed/hk/hk_sentiment_analysis.csv --use-pretrained`
- 因子生成：`python src/hk_factor_generator.py --sentiment-file data/processed/hk/hk_sentiment_analysis.csv --price-file data/hk_prices.csv --output-file data/processed/hk/hk_sentiment_factors.csv --include-special-factors --standardize`
- 回测评估：`bash run.sh` 或 `python src/analyze_factors.py`

---

# 港股市场情感因子研究系统 (Hong Kong Market Sentiment Factor Research System)

## 系统概述 (System Overview)

本系统专门针对港股市场构建的完整情感因子研究框架，基于恒生综合指数(HSCI)成分股，整合多语言新闻数据和港股特色因子，为港股量化投资提供alpha信号。

**核心特色**:
- 🇭🇰 **港股专业化**: 针对港股市场特征深度优化
- 🌏 **多语言支持**: 繁体中文、简体中文、英文新闻整合
- 📊 **HSCI全覆盖**: 恒生综合指数约500只成分股
- 🚀 **实时更新**: 支持增量数据更新和实时因子计算
- 🎯 **特色因子**: 北水因子、港股通因子等港股独有信号

## 系统架构 (System Architecture)

```
港股情感因子研究系统
├── 数据收集层 (Data Collection)
│   ├── HSCI成分股池管理
│   ├── 港股价格数据 (AkShare/yfinance)
│   └── 多源新闻数据 (港股本地+内地媒体)
├── 数据处理层 (Data Processing)
│   ├── 多语言情感分析
│   ├── 港股专业术语处理
│   └── 数据清洗和标准化
├── 因子构建层 (Factor Construction)
│   ├── 基础情感因子 (多时间窗口)
│   ├── 港股特色因子 (北水、监管等)
│   └── 因子正交化和风险调整
└── 应用层 (Application)
    ├── 因子有效性验证
    ├── 策略回测
    └── 实时信号生成
```

## 快速开始 (Quick Start)

### 1. 环境设置

```bash
# 克隆项目
git clone <your-repo-url>
cd nlp_quant_factor

# 初始化港股市场环境
bash scripts/setup_hk_market.sh
```

### 2. 运行完整数据收集

```bash
# 一键运行港股数据收集
bash scripts/run_hk_data_collection.sh
```

### 3. 生成情感因子

```bash
# 情感分析
python src/hk_sentiment_analysis.py \
    --input-file news_out/hk/hk_news_latest.csv \
    --output-file data/processed/hk/hk_sentiment_analysis.csv \
    --use-pretrained

# 因子生成
python src/hk_factor_generator.py \
    --sentiment-file data/processed/hk/hk_sentiment_analysis.csv \
    --price-file data/hk_prices.csv \
    --output-file data/processed/hk/hk_sentiment_factors.csv \
    --include-special-factors \
    --standardize
```

## 核心组件 (Core Components)

### 1. 股票池管理 (`src/hk_universe_builder.py`)

**功能**: 
- 获取HSCI成分股列表
- 股票代码标准化 (.HK格式)
- 基本面数据收集

**使用方法**:
```bash
python src/hk_universe_builder.py \
    --output-dir data/universe/hk/ \
    --with-basic-info \
    --debug
```

**输出**: `data/universe/hk/hsci_constituents.csv`

### 2. 价格数据下载 (`src/download_hk_prices.py`)

**功能**:
- 多数据源支持 (AkShare优先，yfinance备选)
- 并行下载优化
- 港股交易日历处理
- 数据质量验证

**使用方法**:
```bash
python src/download_hk_prices.py \
    --universe-file data/universe/hk/hsci_constituents.csv \
    --start-date 2022-01-01 \
    --end-date 2024-12-31 \
    --source auto \
    --with-derived
```

**输出**: `data/hk_prices.csv`

### 3. 新闻数据收集 (`data_pipe_hk.py`)

**功能**:
- 港股本地新闻源 (阿斯达克、经济通、信报等)
- 内地港股新闻源 (东方财富、财联社)
- 多语言新闻处理
- 股票代码智能匹配

**新闻源配置**:
```python
HK_NEWS_SOURCES = {
    'aastocks': '阿斯达克财经网',
    'etnet': '经济通', 
    'hkej': '信报财经新闻',
    'hket': '香港经济日报',
    'eastmoney_hk': '东方财富港股',
    'cls_hk': '财联社港股'
}
```

**使用方法**:
```bash
python data_pipe_hk.py \
    --universe-file data/universe/hk/hsci_constituents.csv \
    --start-date 2022-01-01 \
    --max-articles-per-stock 1000 \
    --output-dir news_out/hk/
```

### 4. 情感分析 (`src/hk_sentiment_analysis.py`)

**功能**:
- 多语言情感分析 (中文+英文)
- 港股专业术语词典
- 预训练模型支持 (FinBERT)
- 情感强度量化

**港股情感词典示例**:
```python
HK_SENTIMENT_DICT = {
    'positive': ['上涨', '升', '涨', '北水', '港股通', '买入'],
    'negative': ['下跌', '跌', '风险', '退市', '除牌', '卖出'],
    'neutral': ['公布', '发布', '宣布', '维持']
}
```

### 5. 因子构建 (`src/hk_factor_generator.py`)

**功能**:
- 多时间窗口情感因子 (1d, 3d, 5d, 10d, 20d)
- 港股特色因子 (北水因子、监管因子等)
- 因子标准化和正交化
- 前向收益率计算

**因子类型**:

#### 基础情感因子
- `sentiment_mean_Nd`: N天情感均值
- `sentiment_std_Nd`: N天情感标准差
- `sentiment_trend_Nd`: N天情感趋势
- `sentiment_intensity_Nd`: N天情感强度
- `news_count_Nd`: N天新闻数量

#### 港股特色因子
- `northbound_sentiment`: 北水情感因子
- `hk_local_sentiment`: 港股本地情感
- `regulatory_sentiment`: 监管情感因子
- `weighted_sentiment`: 语言加权情感

## 数据结构 (Data Structure)

### 目录结构
```
data/
├── universe/hk/              # 港股股票池
│   └── hsci_constituents.csv
├── processed/hk/             # 港股处理数据
│   ├── hk_sentiment_analysis.csv
│   └── hk_sentiment_factors.csv
├── hk_prices.csv            # 港股价格数据
news_out/hk/                 # 港股新闻数据
├── hk_news_YYYYMMDD_HHMMSS.csv
└── hk_news_YYYYMMDD_HHMMSS.jsonl
reports/hk/                  # 港股分析报告
logs/                        # 日志文件
config/
└── hk_market.yaml          # 港股市场配置
```

### 数据字段说明

#### HSCI成分股 (`hsci_constituents.csv`)
```csv
symbol,name,sector,market_cap
00700.HK,腾讯控股,信息技术,3500000000000
09988.HK,阿里巴巴-SW,信息技术,2800000000000
```

#### 港股价格数据 (`hk_prices.csv`)
```csv
date,symbol,open,high,low,close,volume,return_1d
2024-01-01,00700.HK,350.0,355.0,348.0,352.0,12500000,0.015
```

#### 情感分析结果 (`hk_sentiment_analysis.csv`)
```csv
date,title,content,symbol,sentiment_score,sentiment_label,language
2024-01-01,腾讯业绩超预期,腾讯控股公布...,00700.HK,0.75,positive,zh-cn
```

#### 情感因子 (`hk_sentiment_factors.csv`)
```csv
date,symbol,sentiment_mean_1d,sentiment_mean_5d,northbound_sentiment,return_1d
2024-01-01,00700.HK,0.65,0.58,0.82,0.025
```

## 配置文件 (Configuration)

### 港股市场配置 (`config/hk_market.yaml`)
```yaml
market: "HK"
index: "HSCI"
trading_calendar: "XHKG"
timezone: "Asia/Hong_Kong"
currency: "HKD"

data_sources:
  prices:
    primary: "akshare"
    fallback: ["yfinance"]
  news:
    local_hk: ["aastocks", "etnet", "hkej"]
    mainland: ["eastmoney_hk", "cls_hk"]

collection:
  price_data:
    start_date: "2022-01-01"
    end_date: "2024-12-31"
  news_data:
    max_articles_per_stock: 1000
    languages: ["zh-hk", "zh-cn", "en"]

factors:
  sentiment_window: [1, 3, 5, 10, 20]
  language_weights:
    zh-tw: 1.2  # 港股本地新闻权重更高
    zh-cn: 1.0
    en: 0.8
```

## 性能优化 (Performance Optimization)

### 数据收集优化
- **并行下载**: 最多5个并发线程
- **增量更新**: 只下载缺失的数据
- **数据缓存**: 避免重复请求
- **异常处理**: 自动重试和降级

### 计算优化
- **向量化计算**: 使用pandas和numpy优化
- **内存管理**: 分批处理大数据集
- **多进程**: 情感分析并行计算

## 监控和日志 (Monitoring & Logging)

### 日志文件
```
logs/
├── hk_universe_builder.log     # 股票池构建日志
├── hk_price_download.log       # 价格下载日志
├── hk_news_pipeline.log        # 新闻收集日志
├── hk_sentiment_analysis.log   # 情感分析日志
└── hk_factor_generator.log     # 因子生成日志
```

### 关键指标监控
- **数据覆盖率**: HSCI成分股覆盖 > 95%
- **数据质量**: 价格异常值 < 0.1%
- **处理速度**: > 1000条新闻/分钟
- **因子有效性**: IC > 0.05

## 扩展功能 (Extensions)

### 1. 实时数据更新
```bash
# 每日增量更新
python src/daily_hk_update.py
```

### 2. 因子有效性验证
```bash
# IC分析和因子回测
python src/hk_factor_validation.py
```

### 3. 策略信号生成
```bash
# 生成交易信号
python src/hk_signal_generator.py
```

## 常见问题 (FAQ)

### Q: 如何处理港股停牌股票？
A: 系统自动识别停牌股票，在因子计算时会排除停牌期间的数据。

### Q: 繁体中文新闻如何处理？
A: 系统使用zhconv库自动进行繁简体转换，并在情感分析时给予港股本地新闻更高权重。

### Q: 如何添加新的新闻源？
A: 在`data_pipe_hk.py`中的`HK_NEWS_SOURCES`配置中添加新源，并实现对应的爬虫方法。

### Q: 因子更新频率是多少？
A: 支持日度更新，可以通过cron设置自动化更新。

## 技术支持 (Technical Support)

### 依赖库版本
- Python >= 3.8
- pandas >= 1.3.0
- numpy >= 1.21.0
- akshare >= 1.12.0
- yfinance >= 0.1.70
- transformers >= 4.20.0
- jieba >= 0.42.1
- zhconv >= 1.4.3

### 硬件建议
- **内存**: >= 8GB (推荐16GB)
- **存储**: >= 10GB可用空间
- **CPU**: 多核心处理器 (推荐8核)
- **GPU**: 可选，用于加速情感分析模型

### 联系方式
- **项目维护**: HK Market Alpha NLP Factor Study Team
- **技术支持**: 请提交GitHub Issue
- **文档更新**: 请查看最新版README

---

**免责声明**: 本系统仅用于学术研究和技术验证，不构成投资建议。使用者应自行承担投资风险。

