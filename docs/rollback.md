# Rollback Guide

## Version Rollback

### Git Tag Rollback

```bash
# List available tags
git tag --list

# Checkout specific version
git checkout v1.9.0

# Verify make verify passes
make verify
```

## Rollback演练记录

### 演练1: Git Tag 回滚

```bash
# 当前版本
git log -1 --oneline
# aadf35b Add run-real path for news factor building

# 回滚到上一版本
git checkout 51c9a3c

# 验证
make verify
# [OK] All checks passed!

# 回到最新版本
git checkout main
```
