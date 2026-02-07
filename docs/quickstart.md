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
