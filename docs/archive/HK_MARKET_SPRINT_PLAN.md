# 港股市场一周冲刺实战计划 (Hong Kong Market Sprint Plan)

## 计划概述 (Plan Overview)

**核心目标**: "聚焦港股，扩大战果" - 基于HSCI成分股构建完整的港股情感因子研究体系

**时间安排**: 7天冲刺计划
- 第1-2天: 数据工程冲刺 (HK Data Engineering)
- 第3-4天: 因子构建与优化 (Factor Construction & Optimization)  
- 第5-6天: 回测与验证 (Backtesting & Validation)
- 第7天: 报告与部署 (Reporting & Deployment)

## 第一、二天：数据工程冲刺 (Day 1-2: HK Data Engineering)

### 目标 (Objectives)
获取至少1-2年的、覆盖**恒生综合指数（HSCI）**成分股的历史数据

### 1. 股票池构建 (Stock Universe Construction)

#### 1.1 HSCI成分股获取
```bash
# 创建港股股票池目录
mkdir -p data/universe/hk/

# 获取HSCI成分股列表 (约500只股票)
python src/hk_universe_builder.py --index HSCI --output data/universe/hk/hsci_constituents.csv
```

**数据源选择**:
- **主要**: AkShare库 (`ak.stock_hk_index_constituent_df()`)
- **备选**: Yahoo Finance, Wind API, 港交所官方数据
- **格式**: CSV文件，包含股票代码、名称、行业、市值等信息

#### 1.2 股票代码标准化
港股代码特点：
- 5位数字格式：如 00700.HK (腾讯控股)
- 统一后缀：.HK
- 处理特殊股票：H股、红筹股、窝轮等

### 2. 股票行情数据收集 (Stock Price Data Collection)

#### 2.1 数据源配置
```python
# 主要数据源优先级
DATA_SOURCES = [
    'akshare',      # 首选：对港股支持最好
    'yfinance',     # 备选：国际化程度高  
    'tushare_pro',  # 备选：专业金融数据
]
```

#### 2.2 数据字段要求
```csv
date,code,open,high,low,close,adj_close,volume,market_cap,turnover
2022-01-01,00700.HK,550.0,555.0,545.0,552.0,552.0,12500000,5250000000000,0.025
```

#### 2.3 时间范围设置
- **目标期间**: 2022年1月1日 - 2024年12月31日 (2-3年数据)
- **数据频率**: 日度数据
- **复权处理**: 后复权价格 (adj_close)

#### 2.4 实施脚本
```bash
# 下载港股价格数据
python src/download_hk_prices.py \
  --universe-file data/universe/hk/hsci_constituents.csv \
  --start-date 2022-01-01 \
  --end-date 2024-12-31 \
  --output-file data/hk_prices.csv \
  --source akshare \
  --debug
```

### 3. 新闻数据收集 (News Data Collection)

#### 3.1 港股新闻源配置

**香港本地财经媒体**:
```python
HK_NEWS_SOURCES = {
    'aastocks': {
        'name': '阿斯达克财经网',
        'url': 'http://www.aastocks.com',
        'language': 'zh-hk',
        'priority': 1
    },
    'etnet': {
        'name': '经济通',
        'url': 'http://www.etnet.com.hk',
        'language': 'zh-hk',
        'priority': 1
    },
    'hkej': {
        'name': '信报财经新闻',
        'url': 'http://www.hkej.com',
        'language': 'zh-hk',
        'priority': 1
    },
    'hket': {
        'name': '香港经济日报',
        'url': 'http://www.hket.com',
        'language': 'zh-hk',
        'priority': 1
    }
}
```

**内地覆盖港股媒体**:
```python
MAINLAND_HK_SOURCES = {
    'eastmoney': {
        'name': '东方财富',
        'section': 'hk',
        'priority': 2
    },
    'cls': {
        'name': '财联社',
        'section': 'hkstock', 
        'priority': 2
    },
    'sina_hk': {
        'name': '新浪港股',
        'priority': 2
    }
}
```

#### 3.2 新闻爬取策略

**针对性爬取**:
```bash
# 基于HSCI股票池的定向新闻爬取
python data_pipe_hk.py \
  --universe-file data/universe/hk/hsci_constituents.csv \
  --sources aastocks,etnet,hkej,eastmoney \
  --start-date 2022-01-01 \
  --end-date 2024-12-31 \
  --lang zh-hk \
  --output-dir news_out/hk/ \
  --max-articles-per-stock 1000
```

**多语言处理**:
- 繁体中文：港股本地新闻主要语言
- 简体中文：内地媒体报道
- 英文：国际媒体和研报

#### 3.3 数据存储结构
```
news_out/hk/
├── articles_hsci_2022.jsonl    # 2022年新闻数据
├── articles_hsci_2023.jsonl    # 2023年新闻数据  
├── articles_hsci_2024.jsonl    # 2024年新闻数据
├── checkpoint_hk.json          # 爬取进度检查点
└── metrics_hk.csv             # 爬取统计指标
```

### 4. 数据质量控制 (Data Quality Control)

#### 4.1 价格数据验证
```python
# 数据完整性检查
def validate_hk_price_data(df):
    checks = {
        'date_continuity': check_trading_days_hk(df),
        'price_reasonableness': check_price_bounds(df),
        'volume_consistency': check_volume_patterns(df),
        'corporate_actions': detect_splits_dividends(df)
    }
    return checks
```

#### 4.2 新闻数据清洗
```python
# 港股新闻特殊处理
HK_CLEANING_RULES = {
    'language_detection': True,    # 自动检测繁简体
    'stock_code_mapping': True,    # 股票代码标准化
    'hk_financial_terms': True,   # 港股专业术语处理
    'currency_normalization': True # 港币/人民币/美元统一
}
```

### 5. 基础设施配置 (Infrastructure Setup)

#### 5.1 环境依赖更新
```bash
# 添加港股专用依赖
pip install akshare>=1.12.0
pip install jieba
pip install zhconv  # 繁简体转换
pip install langdetect
```

#### 5.2 配置文件模板
```yaml
# config/hk_market.yaml
market: "HK"
index: "HSCI"
trading_calendar: "XHKG"  # 港交所交易日历
timezone: "Asia/Hong_Kong"
currency: "HKD"

data_sources:
  prices:
    primary: "akshare"
    fallback: ["yfinance", "tushare"]
  news:
    local_hk: ["aastocks", "etnet", "hkej"]
    mainland: ["eastmoney", "cls"]
    
sentiment_models:
  chinese: "FinBERT-HK"  # 港股中文情感模型
  english: "FinBERT-EN"  # 英文金融情感模型
```

## 数据产出目标 (Data Output Targets)

### 第1天结束时
- [x] HSCI成分股列表 (500只股票)
- [x] 港股价格数据框架搭建
- [x] 新闻源配置完成

### 第2天结束时  
- [x] 完整的2022-2024年HSCI价格数据 (约365,000条记录)
- [x] 至少50,000条港股相关新闻数据
- [x] 数据质量验证报告

## 技术实现路线图 (Technical Implementation Roadmap)

### 优先级1: 核心数据收集
1. `src/hk_universe_builder.py` - HSCI成分股获取
2. `src/download_hk_prices.py` - 港股价格数据下载  
3. `data_pipe_hk.py` - 港股新闻数据收集

### 优先级2: 数据处理适配
1. `src/clean_hk_data.py` - 港股数据清洗
2. `src/hk_sentiment_analysis.py` - 港股情感分析
3. `src/hk_factor_generator.py` - 港股因子生成

### 优先级3: 系统集成
1. 港股交易日历集成
2. 多语言情感分析支持  
3. 港股特色因子开发

## 成功标准 (Success Criteria)

### 数据覆盖度
- ✅ HSCI成分股覆盖率 > 95%
- ✅ 价格数据完整率 > 98%  
- ✅ 新闻数据时间连续性 > 90%

### 数据质量
- ✅ 价格异常值 < 0.1%
- ✅ 新闻重复率 < 5%
- ✅ 股票代码匹配率 > 99%

### 技术指标
- ✅ 数据下载成功率 > 95%
- ✅ 处理速度 > 1000条/分钟
- ✅ 存储效率优化 > 50%

---

**下一步行动**: 立即开始第1天的数据工程冲刺，重点完成HSCI成分股获取和价格数据框架搭建。

