# 批量化生产功能使用指南

## 概述

`data_pipe.py` 现在支持批量化生产模式，可以自动从股票池文件中读取股票代码，无需手动输入每只股票。

## 新增功能

### 1. `--universe_file` 参数

新增了 `--universe_file` 参数，用于指定包含股票代码的CSV文件：

```bash
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --recent_pages 2
```

### 2. 股票池文件格式

股票池CSV文件必须包含 `symbol` 列，示例格式：

```csv
symbol,name,sector,market_cap
0700.HK,腾讯控股,信息技术,3500000000000
9988.HK,阿里巴巴-SW,信息技术,2800000000000
3690.HK,美团-W,信息技术,1200000000000
```

### 3. 混合使用模式

可以同时使用股票池文件和手动输入的股票代码：

```bash
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --symbols 0001.HK 0002.HK --recent_pages 1
```

## 使用示例

### 示例1：仅使用股票池文件
```bash
# 抓取股票池中所有股票的最近新闻（2页）
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --recent_pages 2

# 抓取股票池中所有股票的历史新闻（2024年和2023年，每年1页）
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --years 2024 2023 --archive_pages 1
```

### 示例2：混合模式
```bash
# 股票池 + 手动输入的股票代码
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --symbols 0001.HK 0002.HK --recent_pages 1
```

### 示例3：估算模式（不实际抓取）
```bash
# 仅估算token消耗，不实际调用API
python3 data_pipe.py --universe_file data/universe/hstech_current_constituents.csv --recent_pages 2 --estimate_only
```

## 错误处理

脚本会自动处理以下错误情况：

1. **文件不存在**：如果指定的股票池文件不存在，脚本会报错并退出
2. **格式错误**：如果CSV文件缺少 `symbol` 列，脚本会报错并退出
3. **读取错误**：如果CSV文件格式有问题，脚本会报错并退出

## 日志输出

使用股票池文件时，脚本会输出详细的日志信息：

```
2025-08-27 10:56:06,086 INFO Loaded 10 symbols from universe file: data/universe/hstech_current_constituents.csv
2025-08-27 10:56:06,086 INFO Universe symbols: ['0700.HK', '9988.HK', '3690.HK', '9618.HK', '1810.HK', '1024.HK', '9868.HK', '9888.HK', '9999.HK', '9696.HK']
```

## Token 估算

脚本会自动计算token消耗：

- **最近新闻**：1 token/页/股票
- **历史新闻**：5 tokens/年/页/股票

例如，10只股票抓取2页最近新闻 = 10 × 2 × 1 = 20 tokens

## 输出文件

所有输出文件保存在 `news_out/` 目录下：

- `articles_recent.jsonl` - 最近新闻（JSONL格式）
- `articles_recent.csv` - 最近新闻（CSV格式）
- `articles_archive.jsonl` - 历史新闻（JSONL格式）
- `articles_archive.csv` - 历史新闻（CSV格式）
- `checkpoint.json` - 检查点文件
- `seen_uris.jsonl` - 已处理的文章URI

## 注意事项

1. 确保设置了 `ER_API_KEY` 环境变量
2. 股票池文件必须是UTF-8编码的CSV格式
3. 建议先用 `--estimate_only` 模式估算token消耗
4. 可以使用 `--token_cap` 参数限制单次运行的最大token消耗
