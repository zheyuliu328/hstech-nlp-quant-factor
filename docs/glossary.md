# 术语表 (Glossary)

## 通用术语

| 术语 | 英文 | 定义 |
|:-----|:-----|:-----|
| 信息系数 | Information Coefficient (IC) | 因子值与下期收益的相关系数，衡量预测能力 |
| 信息比率 | Information Ratio (IR) | IC 均值除以 IC 标准差，衡量因子稳定性 |
| t 统计量 | t-statistic | 检验均值显著性的统计量，\|t\|>2 通常认为显著 |
| p 值 | p-value | 显著性水平，<0.05 通常认为统计显著 |
| Newey-West 调整 | Newey-West Adjustment | 异方差和自相关一致的标准误调整 |

## nlp-factor 专用术语

| 术语 | 英文 | 定义 |
|:-----|:-----|:-----|
| Rank-IC | Rank Information Coefficient | Spearman 秩相关系数，对异常值更稳健的 IC 计算 |
| 分位数回测 | Quantile Backtest | 按因子值分组后检验各组收益差异 |
| 换手率 | Turnover | 组合持仓变化的频率，影响交易成本 |
| ADV | Average Daily Volume | 日均成交量，流动性指标 |
| bps | Basis Points | 基点，0.01% |
| 均值回归 | Mean Reversion | 价格倾向于回归均值的统计现象 |
| 多空组合 | Long-Short Portfolio | 做多高分位股票、做空低分位股票的策略 |
| 夏普比率 | Sharpe Ratio | 风险调整后收益指标 |
| 最大回撤 | Maximum Drawdown | 策略从峰值到谷底的最大亏损 |
| 风格因子 | Style Factor | 市值、价值、动量等系统性风险因子 |

## 情感分析术语

| 术语 | 定义 |
|:-----|:-----|
| RoBERTa | 基于 Transformer 的预训练语言模型 |
| Loughran-McDonald | 金融领域专用情感词典 |
| Z-Score | 横截面标准化方法 |

## 参考

- [项目限制说明](limitations.md)
- [数据血缘文档](data_lineage.md)
- [因子验证报告](../reports/factor_validation_report.md)
