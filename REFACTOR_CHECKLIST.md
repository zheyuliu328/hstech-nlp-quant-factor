# NLP Factor - 文档产品化修改清单

## 修改目标
将 NLP Factor 项目文档重构为标准化用户路径文档，确保用户能在 3/10/30 分钟内完成上手、跑通和真实接入。

---

## 一、README.md 重构

**文件路径**: `nlp-factor/README.md`

**修改内容**:

```markdown
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
```

---

## 二、新建 docs/quickstart.md

**文件路径**: `nlp-factor/docs/quickstart.md`

**内容**:

```markdown
# Quickstart Guide - 10 分钟跑通

> 本指南帮助你在 10 分钟内完整运行 NLP Factor 流水线并验证输出。

---

## 前置要求

- Python 3.8+
- 4GB 可用内存（用于加载 Transformer 模型）
- 网络连接

---

## 步骤 1: 环境准备 (2 分钟)

```bash
# 克隆项目
git clone <repo-url> nlp-factor
cd nlp-factor

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**依赖清单**:
- eventregistry (新闻 API)
- transformers, torch (情绪模型)
- pandas, matplotlib, seaborn (数据处理与可视化)
- yfinance (股价数据)

**安装验证**:
```bash
python -c "import torch; import transformers; print('OK')"
```

---

## 步骤 2: 运行流水线 (5 分钟)

```bash
bash run.sh
```

**这一步会做什么**:
- ✅ 检查环境
- ✅ 运行 Demo 模式（使用样本数据）
- ✅ 生成情绪评分
- ✅ 输出验证报告

**预期输出**:
```
📰 HSTECH NLP Quant Factor - Quick Start
==========================================
✓ Python version: 3.9.0
✓ Dependencies already installed

🎮 Running in DEMO mode (using sample data)...
   To use real data, set ER_API_KEY in .env file

✓ Report saved to: reports/quickstart_report.json
{
  "mode": "DEMO",
  "articles_processed": 50,
  "sentiment_distribution": {
    "positive": 15,
    "negative": 20,
    "neutral": 15
  }
}
```

---

## 步骤 3: 验证输出 (3 分钟)

### 验证 1: 检查报告文件

```bash
ls -lh reports/
```

**预期看到**:
```
quickstart_report.json
figs/
  ├── ic_timeseries.png
  ├── deciles.png
  └── corr_heatmap.png
```

### 验证 2: 查看验证报告

```bash
cat reports/quickstart_report.json
```

**预期看到**:
```json
{
  "mode": "DEMO",
  "articles_processed": 50,
  "sentiment_distribution": {
    "positive": 15,
    "negative": 20,
    "neutral": 15
  },
  "factor_ic": -0.08,
  "t_statistic": -1.30
}
```

### 验证 3: 查看图表

打开 `reports/figs/` 目录下的图片:
- `ic_timeseries.png` - IC 时间序列
- `deciles.png` - 分位数回测
- `corr_heatmap.png` - 风格相关性

---

## 分步运行（可选）

如需分步调试，可手动执行:

```bash
# 1. 构建股票池
python src/hk_universe_builder.py

# 2. 下载股价数据
python src/download_hk_prices.py

# 3. 获取新闻数据（需要 API Key）
python src/data_pipe.py

# 4. 情绪评分
python src/sentiment_top.py

# 5. 生成因子
python src/hk_factor_generator.py

# 6. 验证因子
python src/validate_factor.py
```

---

## 下一步

- [配置真实数据接入](./configuration.md) - 30 分钟接入 EventRegistry API
- [查看 FAQ 常见问题](./faq.md) - 故障排查

---

## 故障速查

| 现象 | 可能原因 | 解决方案 |
|:-----|:---------|:---------|
| `ModuleNotFoundError` | 依赖未安装 | `pip install -r requirements.txt` |
| torch 安装失败 | 平台不兼容 | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| 内存不足 | 模型太大 | 关闭其他程序或增加内存 |
| 图表生成失败 | matplotlib 后端问题 | `export MPLBACKEND=Agg` |

---

*最后更新: 2026-02-08*
```

---

## 三、新建 docs/configuration.md

**文件路径**: `nlp-factor/docs/configuration.md`

**内容**:

```markdown
# Configuration Guide - 30 分钟真实接入

> 本指南帮助你接入 EventRegistry API 获取真实新闻数据，并定制股票池。

---

## 前置要求

- 已完成 [Quickstart](./quickstart.md)
- EventRegistry 账号（免费版即可）
- 了解目标股票列表

---

## 一、API 密钥配置

### 1.1 获取 API Key

1. 访问 https://eventregistry.org/
2. 注册账号
3. 在 Dashboard 获取 API Key

### 1.2 配置环境变量

创建 `.env` 文件:

```bash
# 在项目根目录
echo "ER_API_KEY=your_api_key_here" > .env
```

或设置环境变量:

```bash
# Linux/Mac
export ER_API_KEY="your_api_key_here"

# Windows PowerShell
$env:ER_API_KEY="your_api_key_here"
```

### 1.3 验证配置

```bash
python -c "import os; print('OK' if os.getenv('ER_API_KEY') else 'Missing API Key')"
```

---

## 二、股票池配置

### 2.1 默认股票池

默认覆盖恒生综合指数约 500 只股票。

### 2.2 自定义股票池

编辑 `src/hk_universe_builder.py`:

```python
# 方式1: 使用自定义列表
CUSTOM_UNIVERSE = [
    '0700.HK',  # 腾讯
    '0005.HK',  # 汇丰
    '1299.HK',  # 友邦
    '9988.HK',  # 阿里
]

# 方式2: 从 CSV 读取
import pandas as pd
df = pd.read_csv('my_universe.csv')
CUSTOM_UNIVERSE = df['ticker'].tolist()
```

### 2.3 股票代码格式

| 格式 | 示例 | 说明 |
|:-----|:-----|:-----|
| Yahoo Finance | `0700.HK` | 港股标准格式 |
| Bloomberg | `700 HK` | 需转换 |
| 纯数字 | `00700` | 需添加 `.HK` 后缀 |

---

## 三、数据时间范围配置

### 3.1 修改采集时间范围

编辑 `src/data_pipe.py`:

```python
# 修改获取新闻的时间范围
start_date = "2024-01-01"  # 建议至少24个月数据
end_date = "2026-01-01"
```

### 3.2 采集模式选择

| 模式 | 命令 | 适用场景 |
|:-----|:-----|:---------|
| 近期数据 | `--recent_pages 5` | 每日更新 |
| 历史数据 | `--years 2023 2024 --archive_pages 3` | 首次填充 |
| 全量采集 | `--universe_file data/universe/hstech_current_constituents.csv` | 完整回测 |

### 3.3 运行生产采集

```bash
# 采集近期数据（最近30天）
python src/data_pipe.py --symbols 0700.HK --recent_pages 10

# 采集历史数据
python src/data_pipe.py --symbols 0700.HK --years 2023 2024 --archive_pages 3

# 采集全股票池
python src/data_pipe.py \
    --universe_file data/universe/hstech_current_constituents.csv \
    --years 2023 2024 --archive_pages 2
```

---

## 四、字段映射规范

### 4.1 新闻数据字段

| 源字段 | 内部字段 | 说明 |
|:-------|:---------|:-----|
| uri | uri | 唯一标识符 |
| title | title | 新闻标题 |
| body | body | 新闻正文 |
| date | date | 发布日期 |
| source.title | source_title | 来源媒体 |

### 4.2 股价数据字段

| 源字段 | 内部字段 | 说明 |
|:-------|:---------|:-----|
| Date | date | 交易日期 |
| Close | close | 收盘价 |
| Volume | volume | 成交量 |
| Adjusted Close | adj_close | 调整后收盘价 |

---

## 五、常见失败点

### 5.1 API Key 无效

**现象**: `Authentication failed` 或 `Invalid API key`

**排查步骤**:
1. 检查 `.env` 文件格式: `ER_API_KEY=your_key` (无引号)
2. 确认 Key 未过期
3. 检查账户配额是否用完

### 5.2 API 请求限制

**现象**: `Rate limit exceeded` 或 `Quota exhausted`

**解决方案**:
```python
# 在 data_pipe.py 中添加延迟
import time
time.sleep(1)  # 每秒请求一次
```

**EventRegistry 配额**:
- 免费版: 每日有限请求数
- 近期数据: 1 token/page
- 历史数据: 5 tokens/year/page

### 5.3 股价数据下载失败

**现象**: `yfinance` 返回空数据或报错

**排查步骤**:
1. 检查股票代码格式（需 `.HK` 后缀）
2. 确认股票在查询时间段内已上市
3. 检查网络连接（Yahoo Finance 可能需要代理）

**使用代理**:
```bash
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
python src/download_hk_prices.py
```

### 5.4 情绪评分结果为 NaN

**现象**: 情绪评分列全为 NaN

**排查步骤**:
1. 检查新闻数据是否为空:
```bash
ls -lh data/processed/news_*.csv
head data/processed/news_*.csv
```

2. 检查模型加载是否成功:
```python
python -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('test'))"
```

3. 检查文本编码（需 UTF-8）

### 5.5 内存不足

**现象**: `MemoryError` 或进程被杀死

**解决方案**:
1. 使用更小模型:
```python
# 修改 sentiment_top.py
model_name = "distilbert-base-uncased-finetuned-sst-2-english"  # 更小模型
```

2. 分批处理:
```python
BATCH_SIZE = 32  # 减小批大小
```

3. 增加系统内存或使用服务器

---

## 六、验证清单

接入完成后，验证以下项目:

- [ ] API Key 配置正确，可正常获取数据
- [ ] 新闻数据采集成功，记录数符合预期
- [ ] 股价数据下载完整，无缺失日期
- [ ] 情绪评分正常运行，无 NaN 值
- [ ] 因子生成成功，IC 计算完成
- [ ] 图表正常生成，可查看

---

## 七、生产环境建议

### 7.1 数据存储

- 使用 DuckDB 或 PostgreSQL 替代 CSV
- 配置自动备份
- 保留原始数据（便于重新处理）

### 7.2 定时任务

```bash
# 每日凌晨采集新闻
crontab -e
0 2 * * * cd /path/to/nlp-factor && python src/data_pipe.py --recent_pages 5
```

### 7.3 监控

- 监控 API 配额使用情况
- 设置数据质量告警（如某日新闻数为 0）
- 跟踪模型性能衰减

---

*最后更新: 2026-02-08*
```

---

## 四、新建 docs/faq.md

**文件路径**: `nlp-factor/docs/faq.md`

**内容**:

```markdown
# FAQ - 常见问题

---

## 安装问题

### Q: `run.sh` 报错 "eventregistry module not found"

**A**: 安装依赖:
```bash
pip install eventregistry
# 或
pip install -r requirements.txt
```

### Q: torch 安装失败

**A**: 根据平台选择安装方式:

```bash
# CPU 版本（推荐，体积小）
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Mac M1/M2
pip install torch

# CUDA 版本（如有 GPU）
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Q: Python 版本要求

**A**: 需要 Python 3.8+。检查版本:
```bash
python --version
```

---

## API 问题

### Q: API Key 无效 / 请求限制

**A**: 
- 检查 `.env` 文件格式: `ER_API_KEY=your_key` (无引号)
- EventRegistry 免费版有每日请求限制
- 考虑升级付费计划或降低请求频率

### Q: 如何查看 API 配额使用情况?

**A**: 登录 EventRegistry Dashboard 查看剩余配额。

### Q: 采集数据太慢

**A**: 
1. 减少股票数量
2. 减少时间范围
3. 降低 `archive_pages` 参数
4. 升级 API 套餐

---

## 数据问题

### Q: 股价数据下载失败

**A**: 使用代理或更换数据源:
```bash
# 设置代理
export HTTP_PROXY=http://proxy:port
python src/download_hk_prices.py
```

### Q: 情绪评分结果为 NaN

**A**: 检查新闻数据是否为空:
```bash
# 查看原始数据
ls -lh data/processed/news_*.csv
head data/processed/news_*.csv
```

### Q: 如何解释负 IC 值?

**A**: 
- IC = -0.08 表示负相关
- 高情绪 → 低未来收益 (均值回归)
- 策略: 情绪最高分位做空，最低分位做多

### Q: 统计不显著怎么办?

**A**: 
- 当前 t-statistic = -1.30，未达到 |t| > 2 的显著性阈值
- 需要扩展数据至 24 个月以上
- 参考 [factor_validation_report.md](reports/factor_validation_report.md)

---

## 运行问题

### Q: 内存不足 (OOM)

**A**: 
1. 使用更小模型:
```python
# 修改 sentiment_top.py
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
```

2. 减小批大小:
```python
BATCH_SIZE = 16
```

3. 关闭其他程序释放内存

### Q: 图表生成失败

**A**: 设置 matplotlib 后端:
```bash
export MPLBACKEND=Agg
python src/validate_factor.py
```

### Q: 如何只运行部分股票?

**A**: 编辑 `src/hk_universe_builder.py`:
```python
CUSTOM_UNIVERSE = ['0700.HK', '0005.HK']  # 只运行这两只
```

---

## 因子研究问题

### Q: 如何添加新的情绪模型?

**A**: 编辑 `src/sentiment_top.py`:
```python
# 添加新模型
new_model = pipeline("sentiment-analysis", model="your-model-name")
```

### Q: 如何修改因子计算方式?

**A**: 编辑 `src/hk_factor_generator.py`:
```python
# 修改因子聚合逻辑
df['sentiment_factor'] = df.groupby('date')['sentiment'].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

### Q: 如何扩展回测周期?

**A**: 
1. 修改时间范围:
```python
start_date = "2022-01-01"  # 延长至24个月+
```

2. 重新采集数据:
```bash
python src/data_pipe.py --years 2022 2023 2024 --archive_pages 5
```

---

## 其他问题

### Q: 如何导出因子数据?

**A**: 
```python
import pandas as pd
df = pd.read_csv('data/processed/daily_sentiment_factors.csv')
df.to_excel('factor_output.xlsx', index=False)
```

### Q: 如何贡献代码?

**A**: 
1. Fork 仓库
2. 创建 feature 分支
3. 提交 PR

### Q: 项目是否支持 A 股?

**A**: 当前专注于港股，但框架可扩展:
1. 修改股票代码格式（A 股无 `.HK` 后缀）
2. 更换新闻数据源（EventRegistry 支持中文新闻）
3. 更换股价数据源（使用 akshare 等 A 股数据源）

---

*最后更新: 2026-02-08*
```

---

## 五、文件创建/修改清单总结

| 文件路径 | 操作 | 说明 |
|:---------|:-----|:-----|
| `nlp-factor/README.md` | 修改 | 重构为标准化结构 |
| `nlp-factor/docs/quickstart.md` | 新建 | 10 分钟跑通指南 |
| `nlp-factor/docs/configuration.md` | 新建 | 30 分钟接入配置 |
| `nlp-factor/docs/faq.md` | 新建 | 常见问题解答 |

---

## 关键纠偏落实

1. **监管合规描述**: 已将 "Production-grade factor research framework" 修改为 "面向量化研究的港股新闻情绪因子研究框架"

2. **统计严谨性**: 明确标注当前统计结果不显著（t-statistic = -1.30 < 2），避免误导性陈述

3. **移除夸大描述**: 
   - 删除了 "Production-grade" 等可能暗示生产就绪的词汇
   - 统一使用 "面向风险建模、审计与研究" 作为定位描述
