# NLP Factor - 用户体验文档

## 📋 项目概述
**NLP Factor** 是一个端到端的量化因子研究框架，将新闻情绪转化为港股交易信号。覆盖恒生综合指数约500只股票，使用 Transformer 模型和金融词典进行情绪评分。

---

## 🚀 3分钟上手

### 步骤1: Clone & Install
```bash
git clone <repo-url> nlp-factor
cd nlp-factor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**依赖清单**:
- eventregistry (新闻 API)
- transformers, torch (情绪模型)
- pandas, matplotlib, seaborn (数据处理与可视化)
- python-dotenv (环境配置)

### 步骤2: 运行第一个输出
```bash
bash run.sh
```

**预期输出** (Demo 模式):
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

## 🎯 10分钟跑通

### 核心功能理解

| 模块 | 功能 | 运行命令 |
|------|------|----------|
| `data_pipe.py` | 新闻数据获取 | `python src/data_pipe.py` |
| `sentiment_top.py` | 情绪评分 | `python src/sentiment_top.py` |
| `hk_factor_generator.py` | 因子构建 | `python src/hk_factor_generator.py` |
| `validate_factor.py` | 因子验证 | `python src/validate_factor.py` |

### 完整运行流程

```bash
# 方式1: 使用 run.sh 一键运行
bash run.sh

# 方式2: 分步运行
python src/hk_universe_builder.py      # 构建股票池
python src/download_hk_prices.py       # 下载股价数据
python src/data_pipe.py                # 获取新闻数据
python src/sentiment_top.py            # 情绪评分
python src/hk_factor_generator.py      # 生成因子
python src/validate_factor.py          # 验证因子
```

**关键发现**:
- Rank IC: -0.08 (负相关，均值回归信号)
- T-statistic: -1.30 (不显著，需更多数据)
- 策略: 做空高情绪股票，做多低情绪股票

---

## 📊 30分钟接入真实数据

### 配置说明

#### 1. API 密钥配置
创建 `.env` 文件:
```bash
cp .env.example .env  # 如果不存在则直接创建
```

编辑 `.env`:
```
ER_API_KEY=your_eventregistry_api_key_here
```

获取 API Key:
1. 访问 https://eventregistry.org/
2. 注册账号
3. 在 Dashboard 获取 API Key

#### 2. 股票池配置
编辑 `src/hk_universe_builder.py`:
```python
# 默认覆盖恒生综合指数约500只股票
# 可自定义股票列表:
CUSTOM_UNIVERSE = ['0700.HK', '0005.HK', '1299.HK']  # 腾讯、汇丰、友邦
```

#### 3. 数据时间范围配置
编辑 `src/data_pipe.py`:
```python
# 修改获取新闻的时间范围
start_date = "2024-01-01"  # 建议至少24个月数据
end_date = "2026-01-01"
```

### 真实数据运行步骤

```bash
# 1. 配置 API Key
echo "ER_API_KEY=your_key" > .env

# 2. 运行生产模式（自动检测 .env）
bash run.sh

# 或手动运行:
python src/data_pipe.py --symbols 0700.HK --recent_pages 10
```

### 数据映射

| 数据源 | 字段 | 说明 |
|--------|------|------|
| EventRegistry | title, body | 新闻标题和正文 |
| EventRegistry | date | 发布时间 |
| Yahoo Finance | Close | 收盘价 |
| Yahoo Finance | Volume | 成交量 |

---

## ❓ FAQ (5个最常见问题)

### Q1: `run.sh` 报错 "eventregistry module not found"
**A**: 安装依赖:
```bash
pip install eventregistry
# 或
pip install -r requirements.txt
```

### Q2: API Key 无效 / 请求限制
**A**: 
- 检查 `.env` 文件格式: `ER_API_KEY=your_key` (无引号)
- EventRegistry 免费版有每日请求限制
- 考虑升级付费计划或降低请求频率

### Q3: 股价数据下载失败
**A**: 使用代理或更换数据源:
```bash
# 设置代理
export HTTP_PROXY=http://proxy:port
python src/download_hk_prices.py
```

### Q4: 情绪评分结果为 NaN
**A**: 检查新闻数据是否为空:
```bash
# 查看原始数据
ls -lh data/processed/news_*.csv
head data/processed/news_*.csv
```

### Q5: 如何解释负 IC 值?
**A**: 
- IC = -0.08 表示负相关
- 高情绪 → 低未来收益 (均值回归)
- 策略: 情绪最高分位做空，最低分位做多

---

## 🚧 上手阻断点清单

### P0 (阻断性)
| 问题 | 影响 | 解决方案 |
|------|------|----------|
| EventRegistry API Key 缺失 | 无法获取新闻 | 注册获取免费 API Key |
| torch 安装失败 | 无法运行情绪模型 | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| Python < 3.8 | 依赖不兼容 | 升级 Python |

### P1 (高优先级)
| 问题 | 影响 | 解决方案 |
|------|------|----------|
| API 请求频率限制 | 数据获取缓慢 | 添加 time.sleep(1) 降低频率 |
| 新闻覆盖度不均 | 小盘股数据缺失 | 添加流动性筛选 (ADV > HK$50M) |
| 内存不足 (大模型) | Transformers 加载失败 | 使用 smaller model 或增加内存 |

### P2 (中优先级)
| 问题 | 影响 | 解决方案 |
|------|------|----------|
| 回测周期太短 | 统计不显著 | 扩展至24个月+数据 |
| 交易成本未考虑 | 收益高估 | 参考 `trading_cost_analysis.md` |
| 时区不一致 | 时间戳错误 | 统一使用 HKT (UTC+8) |

---

## 📸 截图计划

| 截图位置 | 描述 | 优先级 |
|----------|------|--------|
| `reports/figs/ic_timeseries.png` | IC 时间序列 | P0 |
| `reports/figs/deciles.png` | 分位数回测 | P0 |
| `reports/figs/corr_heatmap.png` | 风格相关性热力图 | P1 |
| 情绪分布图 | 正/负/中性占比 | P1 |
| 新闻样本展示 | 原始新闻数据 | P2 |

---

## 🔗 相关文档

- [reports/factor_validation_report.md](reports/factor_validation_report.md) - 完整因子验证报告
- [reports/trading_cost_analysis.md](reports/trading_cost_analysis.md) - 交易成本分析
- [docs/data_lineage.md](docs/data_lineage.md) - 数据血缘文档

---

## 📈 生产就绪检查清单

| 组件 | 状态 | 说明 |
|------|------|------|
| 统计检验 (t-stat, p-value) | ✅ 完成 | Newey-West 调整 |
| 信息比率计算 | ✅ 完成 | 日度和年化 IR |
| 交易成本分析 | ✅ 完成 | 换手率、冲击成本 |
| 数据血缘文档 | ✅ 完成 | Event Registry API |
| 扩展回测周期 | ⚠️ 待办 | 需24个月+数据 |
| 风险模型集成 | ❌ 未开始 | 需 Barra 风格模型 |
