# GitHub Actions CI/CD 配置

本项目配置了 GitHub Actions 工作流，实现以下功能：

## 功能

1. **单元测试 (UT)** - 每次 PR 和 push 到 main 分支时自动运行
2. **代码覆盖率检查** - 要求覆盖率 ≥ 90%
3. **代码扫描 (Lint)** - 使用 flake8 检查语法错误
4. **自动发布** - 合并到 main 分支且通过测试后自动发布到 PyPI

## 配置步骤

### 1. 添加 PyPI API Token

1. 登录 [PyPI](https://pypi.org/)
2. 进入 Account Settings → API tokens
3. 创建一个新 token，Scope 选择 "Entire account"
4. 复制 token

### 2. 添加 GitHub Secrets

1. 进入项目仓库: https://github.com/ising-tech/plectrum-core
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Secret: 粘贴刚才创建的 PyPI token

### 3. 启用 GitHub Actions

首次 push 后，Actions 会自动启用。

## 工作流说明

`.github/workflows/ci.yml`:

```yaml
# 触发条件
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# 作业:
# 1. test - 运行 pytest + 覆盖率报告
# 2. lint - 运行 flake8 代码检查
# 3. build-and-publish - 只有前两个 job 成功才执行
```

## 查看结果

- **Tests**: Actions 页面查看测试结果
- **Coverage**: Codecov 页面查看覆盖率详情
- **PyPI**: https://pypi.org/project/plectrum-core/