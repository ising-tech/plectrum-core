# 发布到 PyPI 教程

本文档介绍如何将 plectrum-core 发布到 PyPI。

## 准备工作

### 1. 安装必要工具

```bash
pip install build twine
```

### 2. 配置 PyPI 账号

在 `~/.pypirc` 文件中配置认证信息:

```ini
[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
username = __token__
password = <your-test-pypi-token>
```

> **注意**: 推荐使用 API Token 作为密码，而不是真实密码。可以在 PyPI 网站创建。

## 发布流程

### 方式一: 使用构建脚本 (推荐)

```bash
# 1. 进入项目目录
cd /Users/jjhao/PycharmProjects/plectrum-core

# 2. 运行发布脚本
chmod +x deploy.sh
./deploy.sh
```

### 方式二: 手动发布

```bash
# 1. 进入项目目录
cd /Users/jjhao/PycharmProjects/plectrum-core

# 2. 清理旧构建
rm -rf dist/ build/ *.egg-info/

# 3. 构建包 (会生成 dist/ 目录)
python3 -m build

# 4. 检查构建产物
ls -la dist/

# 5. 先上传到 Test PyPI (可选，测试用)
twine upload --repository testpypi dist/*

# 6. 正式发布到 PyPI
twine upload dist/*
```

## 版本管理

在 `setup.py` 中修改版本号:

```python
VERSION = "0.1.0"  # 修改这个版本号
```

版本号规范:
- `0.1.0` - 初始版本
- `0.1.1` - 修复 bug
- `0.2.0` - 新功能 (向后兼容)
- `1.0.0` - 正式版本

## 验证发布

```bash
# 从 PyPI 安装验证
pip install plectrum-core

# 验证导入
python3 -c "from plectrum import CloudSolver, LocalSolver; print('OK')"
```

## 常见问题

### 1. twine 上传失败

```bash
# 检查包是否有效
twine check dist/*
```

### 2. 包名冲突

如果包名已被使用，需要在 `setup.py` 中修改 `name`:

```python
setup(
    name="plectrum-core",  # 更改包名
    ...
)
```

### 3. 上传失败权限

确认 PyPI 账号有上传权限，且 token 正确。