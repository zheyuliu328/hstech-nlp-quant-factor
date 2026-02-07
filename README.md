<div align="center">
  <h1>📰 NLP Sentiment Factor for Hong Kong Equities</h1>
  <p><strong>面向量化研究的港股情绪因子分析工具</strong></p>
  
  <a href="https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://github.com/zheyuliu328/hstech-nlp-quant-factor/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/zheyuliu328/hstech-nlp-quant-factor?style=for-the-badge&logo=github&labelColor=000000&logoColor=FFFFFF&color=0500ff" /></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&labelColor=000000" /></a>
  <a href="https://www.python.org/"><img alt="Python: 3.8+" src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&labelColor=000000&logoColor=FFFFFF" /></a>
</div>

<br>

## 一句话定位

面向量化研究的港股情绪因子分析工具，演示 NLP 情感评分与因子验证的完整研究流程。

---

## 核心能力

1. **双引擎情感分析**: 融合 RoBERTa Transformer 与金融词典，对新闻文本进行情感评分
2. **因子验证框架**: 计算 IC、Rank-IC、t 统计量，评估因子预测能力与统计显著性
3. **成本敏感性分析**: 建模交易成本与换手率，评估策略实盘可行性

---

## 快速开始

```bash
# 1. 安装依赖
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. 运行完整流程
bash run.sh

# 3. 查看验证报告
cat reports/factor_validation_report.md
```

### 输出工件

运行后生成：
- `reports/factor_validation_report.md` - 因子验证完整报告（IC、统计检验、回测）
- `reports/trading_cost_analysis.md` - 交易成本与容量分析
- `reports/figs/*.png` - IC 时序图、分位数收益图、相关性热力图
- `data/processed/daily_sentiment_factors.csv` - 日度情绪因子值

---

## 关键发现

情绪因子与下期收益呈负相关（均值回归效应），但**统计显著性不足**：

| 指标 | 数值 | 评估 |
|:-----|:-----|:-----|
| Rank-IC | -0.08 | 弱负相关 |
| t-statistic | -1.30 | 不显著 (\|t\|<2) |
| p-value | 0.194 | 不显著 (p>0.05) |
| 年化换手率 | 3.8-6.3x | 中等 |
| 估计年化成本 | 200-350 bps | 显著侵蚀收益 |

**结论**: 当前结果不满足传统因子标准，需进一步优化验证。

---

## 项目结构

```
hstech-nlp-quant-factor/
├── src/
│   ├── hk_universe_builder.py    # 股票池构建
│   ├── download_hk_prices.py     # 股价数据获取
│   ├── data_pipe.py              # 新闻数据获取
│   ├── clean_data.py             # 数据清洗
│   ├── sentiment_top.py          # 情感评分
│   ├── hk_factor_generator.py    # 因子构建
│   ├── validate_factor.py        # 因子验证
│   ├── statistical_tests.py      # 统计检验
│   └── backtest/                 # 回测引擎
│       └── vectorized.py
├── config/
│   └── hk_market.yaml            # 配置文件
├── data/
│   ├── universe/                 # 股票列表
│   └── processed/                # 处理后数据
├── reports/
│   ├── figs/                     # 图表输出
│   ├── factor_validation_report.md   # 验证报告
│   └── trading_cost_analysis.md      # 成本分析
├── docs/
│   ├── glossary.md               # 术语表
│   ├── limitations.md            # 限制说明
│   └── data_lineage.md           # 数据血缘
├── tests/                        # 单元测试
├── run.sh                        # 主入口
└── requirements.txt
```

---

## 文档索引

| 文档 | 说明 |
|:-----|:-----|
| [docs/glossary.md](docs/glossary.md) | 术语表（IC、Rank-IC、IR、bps 等） |
| [docs/limitations.md](docs/limitations.md) | 项目限制与统计结论 |
| [docs/data_lineage.md](docs/data_lineage.md) | 数据来源与清洗流程 |
| [reports/factor_validation_report.md](reports/factor_validation_report.md) | 完整因子验证报告 |
| [reports/trading_cost_analysis.md](reports/trading_cost_analysis.md) | 交易成本分析 |

---

## 项目定位与限制

### 项目性质

**本项目是面向量化研究的因子分析演示工具，非实盘交易系统**。

### 明确限制

| 限制项 | 说明 |
|:-------|:-----|
| ❌ 统计不显著 | 当前 IC 统计不显著（t=-1.30，\|t\|<2），不满足传统因子标准 |
| ❌ 样本期短 | 回测期约 6 个月，未覆盖完整市场周期（建议 24 个月+） |
| ❌ 覆盖不均 | 新闻数据源覆盖度不均，小盘股数据稀疏 |
| ❌ 无风险模型 | 未实现风险中性化（无 Barra 风格模型） |

### 统计结论

- **Rank-IC**: -0.08（弱负相关，均值回归信号）
- **t-statistic**: -1.30（不显著，p=0.194）
- **年化换手率**: 3.8-6.3x（中等，成本侵蚀显著）

### 适用场景

- ✅ 量化研究岗位面试项目演示
- ✅ NLP 因子构建方法论学习
- ✅ 因子验证流程参考

### 实盘前需完成

1. 扩展数据至 24 个月以上
2. 实施流动性筛选（ADV > 5000 万港币）
3. 降低调仓频率至周度
4. 小规模纸面交易验证成本模型

---

## 技术栈

| 工具 | 用途 |
|:-----|:-----|
| Python 3.8+ | 主语言 |
| Transformers (HuggingFace) | 情感模型 |
| DuckDB | 数据仓库 |
| Pandas / NumPy | 数据处理 |
| Matplotlib | 可视化 |
| EventRegistry | 新闻 API |
| yfinance | 股价数据 |

---

## 作者

**Zheyu Liu**

面向量化研究的教育项目，演示系统性因子研究方法论。

---

<div align="center">
  <sub>面向量化研究 • 演示级实现 • 非实盘系统</sub>
</div>
