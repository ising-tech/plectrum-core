# GitHub Actions CI/CD 配置

本项目配置了 GitHub Actions 工作流，实现以下功能：

## 功能

1. **单元测试 (UT)** - 每次 PR 和 push 到 main 分支时自动运行
2. **代码覆盖率检查** - 要求覆盖率 ≥ 90%
3. **代码扫描 (Lint)** - 使用 flake8 检查语法错误
4. **自动发布** - 合并到 main 分支且通过测试后自动发布到 PyPI (使用 Trusted Publisher)

## 配置步骤 (Trusted Publisher)

### 1. 在 PyPI 上配置 Trusted Publisher

1. 登录 [PyPI](https://pypi.org/)
2. 进入 Account Settings → Publishing
3. 点击 "Add a new publisher"
4. 选择 "GitHub Actions"
5. 填写:
   - Owner: `ising-tech`
   - Repository name: `plectrum-core`
   - Workflow filename: `ci.yml`

### 2. 在 PyPI 项目中添加 Trusted Publisher

1. 进入 https://pypi.org/manage/project/plectrum-core/
2. 点击 "Publishing"
3. 点击 "Add a new publisher"
4. 选择 "GitHub Actions"
5. 选择 owner 和 repository

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
#    使用 Trusted Publisher OIDC 认证，无需 token
```

## 查看结果

- **Tests**: Actions 页面查看测试结果
- **Coverage**: Codecov 页面查看覆盖率详情
- **PyPI**: https://pypi.org/project/plectrum-core/