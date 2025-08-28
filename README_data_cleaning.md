# 数据清洗模块使用指南

## 概述

`src/clean_data.py` 是一个专门的数据清洗模块，负责清洗从 `data_pipe.py` 抓取到的原始新闻数据。该模块将数据获取和数据清洗两个环节解耦，使代码结构更清晰、更易于维护。

## 主要功能

### 1. 文本清洗
- **HTML标签清理**：去除HTML标签和实体字符
- **Unicode标准化**：统一字符编码格式
- **空白字符处理**：去除多余的换行符和空格
- **特殊字符过滤**：去除控制字符

### 2. 日期时间处理
- **格式统一**：将分散的日期和时间字段合并为标准datetime格式
- **有效性检查**：验证日期时间的有效性

### 3. 数据质量提升
- **去重处理**：基于URI、URL、标题等字段去除重复记录
- **空内容过滤**：过滤掉内容过短的记录
- **语言检测**：自动检测文本语言（中文、英文、韩文等）

### 4. 质量报告
- **统计信息**：记录处理前后的数据量变化
- **质量指标**：缺失值统计、语言分布等
- **详细日志**：完整的处理过程记录

## 使用方法

### 命令行使用

```bash
# 基本用法：清洗CSV文件
python3 src/clean_data.py --input news_out/articles_recent.csv

# 指定输出文件名和目录
python3 src/clean_data.py --input news_out/articles_recent.csv --output my_cleaned_data.csv --output_dir data/processed

# 输出JSON格式
python3 src/clean_data.py --input news_out/articles_recent.csv --format json

# 详细日志模式
python3 src/clean_data.py --input news_out/articles_recent.csv --verbose
```

### 参数说明

- `--input, -i`：输入文件路径（必需）
- `--output, -o`：输出文件名（可选，默认自动生成）
- `--output_dir, -d`：输出目录（默认：data/processed）
- `--format, -f`：输出格式，csv或json（默认：csv）
- `--verbose, -v`：详细日志模式

### 编程接口使用

```python
from src.clean_data import clean_and_save_news

# 清洗数据并保存
df_clean, quality_report = clean_and_save_news(
    input_file="news_out/articles_recent.csv",
    output_file="cleaned_news.csv",
    output_dir="data/processed",
    file_type="csv"
)

print(f"处理了 {quality_report['total_rows']} 条记录")
print(f"语言分布: {quality_report['language_distribution']}")
```

## 输入数据格式

模块支持以下输入格式：

### CSV文件
```csv
uri,url,title,body,lang,source_title,dateTime,date,time
8809691303,https://example.com,标题,内容,zh,来源,2025-08-10T21:21:03Z,2025-08-10,21:21:03
```

### JSONL文件
```json
{"uri": "8809691303", "url": "https://example.com", "title": "标题", "body": "内容", "lang": "zh", "source_title": "来源", "dateTime": "2025-08-10T21:21:03Z", "date": "2025-08-10", "time": "21:21:03"}
```

## 输出数据格式

清洗后的数据包含以下字段：

### 原始字段
- `uri`：文章唯一标识符
- `url`：文章链接
- `title`：文章标题（已清洗）
- `body`：文章内容（已清洗）
- `lang`：原始语言标识
- `source_title`：来源媒体
- `dateTime`：原始日期时间
- `date`：日期
- `time`：时间

### 新增字段
- `datetime_clean`：标准化的日期时间对象
- `detected_lang`：自动检测的语言（zh/en/ko/other）

## 清洗效果示例

### 清洗前
```
title: "<h1>腾讯控股</h1>发布<strong>Q3财报</strong>"
body: "腾讯控股有限公司（0700.HK）今日发布了2024年第三季度财报...\n\n\n详细内容..."
```

### 清洗后
```
title: "腾讯控股发布Q3财报"
body: "腾讯控股有限公司（0700.HK）今日发布了2024年第三季度财报...\n详细内容..."
detected_lang: "zh"
```

## 质量报告示例

```json
{
  "total_rows": 99,
  "missing_values": {},
  "empty_content": 0,
  "invalid_dates": 0,
  "language_distribution": {
    "zh": 49,
    "en": 44,
    "ko": 3,
    "other": 3
  }
}
```

## 处理流程

1. **读取数据**：支持CSV和JSONL格式
2. **文本清洗**：去除HTML标签、标准化Unicode、处理空白字符
3. **日期处理**：合并日期时间字段，验证有效性
4. **语言检测**：基于字符类型自动检测语言
5. **去重处理**：基于关键字段去除重复记录
6. **质量过滤**：过滤空内容和无效数据
7. **质量检查**：生成详细的质量报告
8. **保存结果**：输出清洗后的数据

## 注意事项

1. **文件编码**：输入文件必须是UTF-8编码
2. **内存使用**：大文件处理时注意内存使用情况
3. **备份原数据**：建议在处理前备份原始数据
4. **语言检测**：语言检测基于字符类型，可能不够精确
5. **日期格式**：要求输入日期格式为YYYY-MM-DD

## 扩展功能

模块设计为可扩展的，可以轻松添加新的清洗功能：

- 情感分析
- 关键词提取
- 实体识别
- 文本摘要
- 多语言翻译

## 错误处理

模块包含完善的错误处理机制：

- 文件不存在检查
- 格式错误处理
- 数据验证
- 详细的错误日志

## 性能优化

- 使用pandas进行高效的数据处理
- 批量操作减少I/O开销
- 内存友好的处理方式
- 可配置的处理参数
