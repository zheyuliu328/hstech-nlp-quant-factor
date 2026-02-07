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
- 参考 [factor_validation_report.md](../reports/factor_validation_report.md)

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
