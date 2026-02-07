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
