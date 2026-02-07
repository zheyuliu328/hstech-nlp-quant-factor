<div align="center">
  <h1>📰 NLP Sentiment Factor for Hong Kong Equities</h1>
  <p><strong>面向量化研究的港股新闻情绪因子研究框架</strong></p>
  
  <a href="https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/zheyuliu328/hstech-nlp-quant-factor/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://github.com/zheyuliu328/hstech-nlp-quant-factor/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/zheyuliu328/hstech-nlp-quant-factor?style=for-the-badge&logo=github&labelColor=000000&logoColor=FFFFFF&color=0500ff" /></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&labelColor=000000" /></a>
  <a href="https://www.python.org/"><img alt="Python: 3.8+" src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&labelColor=000000&logoColor=FFFFFF" /></a>
</div>

---

## 核心能力

1. **端到端因子流水线**: 从新闻采集、情绪评分到因子验证的完整研究框架
2. **双引擎情绪分析**: Transformer 模型 + 金融词典的混合评分方法
3. **统计严谨验证**: IC 分析、分位数回测、风格相关性检验

---

## Quickstart (3 分钟)

```bash
# 1. 安装依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 运行流水线（Demo 模式）
bash run.sh
```

**输出工件**:
- `reports/quickstart_report.json` - 运行摘要
- `reports/figs/ic_timeseries.png` - IC 时间序列图
- `reports/figs/deciles.png` - 分位数回测图

---

## 关键发现

情绪因子与未来收益呈负相关（IC = -0.08），提示均值回归特征。统计检验显示 t-statistic = -1.30，当前数据量下尚未达到传统显著性阈值（|t| > 2）。

| 指标 | 数值 | 说明 |
|:-----|:-----|:-----|
| Rank IC | -0.08 | 负相关 |
| T-statistic | -1.30 | 不显著 |
| 信息比率 | -0.39 | 低 |

---

## 文档导航

| 文档 | 内容 | 阅读时间 |
|:-----|:-----|:---------|
| [docs/quickstart.md](docs/quickstart.md) | 详细快速入门、预期输出验证 | 10 分钟 |
| [docs/configuration.md](docs/configuration.md) | API 配置、股票池定制 | 30 分钟 |
| [docs/faq.md](docs/faq.md) | 常见问题与故障排查 | 按需查阅 |
| [docs/data_lineage.md](docs/data_lineage.md) | 数据来源与清洗流程 | 参考 |
| [reports/factor_validation_report.md](reports/factor_validation_report.md) | 完整验证报告 | 参考 |

---

## 项目结构

```
nlp-factor/
├── docs/                      # 用户文档
│   ├── quickstart.md         # 10 分钟跑通指南
│   ├── configuration.md      # 30 分钟接入配置
│   ├── faq.md                # 常见问题
│   └── data_lineage.md       # 数据血缘文档
├── src/                       # 源代码
│   ├── data_pipe.py          # 新闻采集
│   ├── sentiment_top.py      # 情绪评分
│   ├── hk_factor_generator.py # 因子生成
│   └── validate_factor.py    # 因子验证
├── reports/                   # 输出报告
│   ├── figs/                 # 图表
│   └── *.md                  # 分析报告
├── data/                      # 数据文件
└── run.sh                     # 一键运行脚本
```

---

## 技术栈

| 工具 | 用途 |
|:-----|:-----|
| Python 3.8+ | 主语言 |
| Transformers (HuggingFace) | 情绪模型 |
| EventRegistry | 新闻 API |
| yfinance | 股价数据 |
| Pandas / NumPy | 数据处理 |

---

## 作者

**Zheyu Liu** - 面向量化研究的工具开发

---

<div align="center">
  <sub>面向风险建模、审计与研究的工具</sub>
</div>
