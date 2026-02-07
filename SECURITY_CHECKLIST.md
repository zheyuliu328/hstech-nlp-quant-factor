# NLP-Factor 安全改造清单

## 文件修改清单

### 1. src/utils/guardrails.py (新增)
- **路径**: `nlp-factor/src/utils/guardrails.py`
- **操作**: 复制根目录 guardrails.py

### 2. src/utils/secrets.py (新增)
- **路径**: `nlp-factor/src/utils/secrets.py`
- **操作**: 复制根目录 secrets.py

### 3. src/utils/data_boundary.py (新增)
- **路径**: `nlp-factor/src/utils/data_boundary.py`
- **操作**: 复制根目录 data_boundary.py

### 4. src/data_pipe.py (修改)
- **路径**: `nlp-factor/src/data_pipe.py`
- **修改内容**:

```python
# 在文件顶部添加:
import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils.secrets import get_er_api_key, SecretNotFoundError
from utils.guardrails import PathValidator, AuditLogger
from utils.data_boundary import validate_news_data

# 修改 api_key 获取逻辑:
def main():
    # 使用统一的 secrets 管理
    try:
        api_key = get_er_api_key()
    except SecretNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
    # 添加路径校验
    path_validator = PathValidator([
        str(Path(__file__).parent.parent / "data"),
        str(Path(__file__).parent.parent / "news_out"),
    ])
    
    # 添加审计日志
    audit = AuditLogger()
    audit.log("DATA_PIPE_START", {
        "symbols": args.symbols,
        "years": args.years,
        "recent_pages": args.recent_pages,
        "archive_pages": args.archive_pages
    })
    
    # ... 原有代码 ...
```

### 5. src/pipeline.py (修改)
- **路径**: `nlp-factor/src/pipeline.py`
- **修改内容**:

```python
# 添加数据校验:
from utils.data_boundary import validate_news_data
from utils.guardrails import AuditLogger

def load_news_or_prescored():
    # ... 原有代码 ...
    
    if prescored.exists():
        df = pd.read_csv(prescored, dtype={"code":"string"})
        
        # 添加数据边界校验
        validation_result = validate_news_data(df)
        if not validation_result.is_valid:
            print("[ERROR] Data validation failed:")
            for error in validation_result.errors:
                print(f"  - {error}")
            raise ValueError("Data validation failed")
        
        if validation_result.warnings:
            print("[WARNING] Data validation warnings:")
            for warning in validation_result.warnings:
                print(f"  - {warning}")
    
    # ... 原有代码 ...
```

### 6. .env.example (新增)
- **路径**: `nlp-factor/.env.example`

```bash
# Event Registry API Key
# 获取地址: https://eventregistry.org/
ER_API_KEY=your_api_key_here

# 注意: 复制此文件为 .env 并填入真实值
# .env 文件已添加到 .gitignore，不会被提交
```

### 7. .gitignore (修改)
- **路径**: `nlp-factor/.gitignore`
- **添加内容**:

```gitignore
# Secrets
.env
.env.local
.env.*.local
*.pem
*.key

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Logs
logs/
*.log

# Backups
backups/
```

### 8. pyproject.toml (修改)
- **路径**: `nlp-factor/pyproject.toml`
- **添加内容**:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "ruff>=0.0.200",
    "pre-commit>=2.20.0",
    "bandit>=1.7.0",
]

[tool.bandit]
exclude_dirs = ["tests", "news_out"]
```

### 9. .pre-commit-config.yaml (新增)
- **路径**: `nlp-factor/.pre-commit-config.yaml`
- **内容**: 同 FCT 配置

### 10. .gitleaks.toml (新增)
- **路径**: `nlp-factor/.gitleaks.toml`
- **操作**: 复制根目录 .gitleaks.toml

### 11. docs/SECURITY.md (新增)
- **路径**: `nlp-factor/docs/SECURITY.md`

```markdown
# NLP-Factor 安全指南

## API Key 管理
1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中填入 `ER_API_KEY`
3. 永远不要提交 `.env` 文件

## 数据校验
- 所有输入数据通过 `validate_news_data()` 校验
- 校验失败会抛出异常并停止处理

## 审计日志
- 数据管道操作记录在 `logs/audit_YYYYMMDD.log`
- 包含请求参数和结果统计
```

## 实施步骤

1. **创建工具模块**
   ```bash
   mkdir -p nlp-factor/src/utils
   cp src/utils/guardrails.py nlp-factor/src/utils/
   cp src/utils/secrets.py nlp-factor/src/utils/
   cp src/utils/data_boundary.py nlp-factor/src/utils/
   ```

2. **修改数据管道**
   ```bash
   # 编辑 nlp-factor/src/data_pipe.py
   # 替换 api_key 获取逻辑
   ```

3. **配置环境**
   ```bash
   cd nlp-factor
   cp .env.example .env
   # 编辑 .env 填入 ER_API_KEY
   ```

4. **配置安全扫描**
   ```bash
   cp ../.gitleaks.toml .
   pre-commit install
   ```

5. **验证**
   ```bash
   # 测试 API Key 获取
   python -c "from src.utils.secrets import get_er_api_key; print('OK')"
   
   # 测试数据校验
   python src/pipeline.py
   
   # 测试 gitleaks
   gitleaks detect --source . --verbose
   ```
