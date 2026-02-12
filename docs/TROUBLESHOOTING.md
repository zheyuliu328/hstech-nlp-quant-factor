# Troubleshooting Guide - 常见故障与修复

> 10 条常见失败与一行修复方案

---

## 🔴 严重错误（阻止运行）

### 1. ModuleNotFoundError: No module named 'torch'
**现象**: 运行 `bash run.sh` 时报错
```
ModuleNotFoundError: No module named 'torch'
```
**修复**:
```bash
pip install -r requirements.txt
# 或单独安装 torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 2. Transformer 模型下载失败
**现象**: 运行情感分析时下载模型超时
**修复**:
```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com
python src/sentiment_top.py
```

### 3. 内存不足（OOM）
**现象**: 运行时报 "Killed" 或内存错误
**修复**:
```bash
# 减少批处理大小
export BATCH_SIZE=8
python src/sentiment_top.py
# 或关闭其他程序释放内存
```

---

## 🟡 警告错误（功能受限）

### 4. EventRegistry API Key 无效
**现象**: 运行 `src/data_pipe.py` 时报 API 错误
**修复**:
```bash
# 使用 Demo 模式
echo "DEMO_MODE=true" > .env
bash run.sh
```

### 5. 图表生成失败
**现象**: reports/figs/ 目录下没有图片
**修复**:
```bash
export MPLBACKEND=Agg
mkdir -p reports/figs
python src/validate_factor.py
```

### 6. yfinance 数据下载失败
**现象**: 股价数据为空或报错
**修复**:
```bash
# 检查网络连接
python -c "import yfinance; print(yfinance.Ticker('0700.HK').info)"
# 或使用代理
export HTTP_PROXY=http://proxy.company.com:8080
```

---

## 🟢 环境问题

### 7. Python 版本不兼容
**现象**: 运行时报语法错误
**修复**:
```bash
# 检查 Python 版本
python --version  # 需要 3.8+
# 使用 pyenv 切换版本
pyenv install 3.9.0
pyenv local 3.9.0
```

### 8. 虚拟环境未激活
**现象**: 提示找不到已安装的包
**修复**:
```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 9. 权限错误（Linux/Mac）
**现象**: Permission denied 错误
**修复**:
```bash
chmod +x run.sh
./run.sh
```

### 10. 报告目录不存在
**现象**: 运行时报 "No such file or directory: 'reports/'"
**修复**:
```bash
mkdir -p reports/figs
bash run.sh
```

---

## 快速诊断命令

```bash
# 检查环境
python -c "import torch, transformers, pandas; print('OK')"

# 检查报告
ls -lh reports/

# 检查数据
ls -lh data/processed/

# 验证 API Key
grep ER_API_KEY .env
```

---

*最后更新: 2026-02-08*
