# Plectrum Core SDK

[English](#english) | [中文](#中文)

---

## English

### About Plectrum

> *Imagine a musician holding a plectrum (拨片), skillfully playing a melody. Each note falls like jade beads onto a plate — that plate is the Ising Cloud Platform (玉盘伊辛云).*

**Plectrum** is a unified Python SDK that helps you submit optimization problems to cloud or local solvers with elegant simplicity. Just as a plectrum helps musicians create beautiful music, Plectrum helps you solve complex optimization problems with ease.

### Features

- **Unified Interface**: Single API for both cloud and local solvers
- **Flexible Solver Selection**: Choose solver at runtime for easy comparison
- **Multiple Task Types**: QUBO, ISING, general, and template tasks
- **Flexible Input**: Support numpy arrays, pandas DataFrames, and CSV files
- **Robust Error Handling**: Clear exception hierarchy with full stack-trace chaining
- **Well Tested**: 96 %+ unit-test coverage

### Installation

```bash
pip install plectrum-core
```

### Quick Start

```python
from plectrum import CloudSolver, LocalSolver, QuboTask, GEAR_BALANCED
import numpy as np

# Create task directly from numpy array (or pandas DataFrame)
data = np.array([
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
])

task = QuboTask(
    name="my-task",
    data=data,
)

# Use cloud solver (Ising Cloud Platform)
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)
cloud_result = task.solve(solver=cloud_solver)

# Or use local solver with precise mode (runs Simulated Annealing locally)
local_solver = LocalSolver(gear=2)
local_result = task.solve(solver=local_solver)

print(f"Cloud result: {cloud_result}")
print(f"Local result: {local_result}")
```

### Solvers

#### CloudSolver

Submits tasks to the Ising Cloud Platform and polls for results.

```python
from plectrum import CloudSolver, GEAR_BALANCED, AuthenticationError

# With explicit API key
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)

# Or from environment variable PLECTRUM_API_KEY
cloud_solver = CloudSolver()  # reads $PLECTRUM_API_KEY

# Raises AuthenticationError if no API key is found
try:
    solver = CloudSolver(api_key="")
except AuthenticationError as e:
    print(e)  # "API key is required. ..."

# Get task status
task_info = cloud_solver.get_task("task-id")
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str` | `$PLECTRUM_API_KEY` | API key (required) |
| `host` | `str` | `https://api.isingq.com` | Cloud API base URL |
| `computer_type` | `int` | `OEPO_ISING_1601` | Machine ID |
| `gear` | `int` | `GEAR_PRECISE` | Gear mode (0/1/2) |
| `poll_interval` | `int` | `2` | Polling interval (seconds) |
| `timeout` | `int` | `300` | Max wait time (seconds) |

#### LocalSolver

Runs Simulated Annealing locally — no network required.

```python
from plectrum import LocalSolver, GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# Fast mode (speed prioritized, 1 000 iterations)
local_solver = LocalSolver(gear=GEAR_FAST)

# Balanced mode (5 000 iterations)
local_solver = LocalSolver(gear=GEAR_BALANCED)

# Precise mode (quality prioritized, 10 000 iterations) — default
local_solver = LocalSolver(gear=GEAR_PRECISE)
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `gear` | `int` | `GEAR_PRECISE` | Gear mode (0/1/2) |
| `algorithm` | `str` | `"sa"` | Algorithm (`"sa"` = Simulated Annealing) |

#### LocalOepoSolver

Submits tasks to a local OEPO quantum-annealing device or simulator via HTTP.

```python
from plectrum import LocalOepoSolver, OEPO_ISING_1601, GEAR_PRECISE

# Default host (192.168.137.100:5001)
solver = LocalOepoSolver(gear=GEAR_PRECISE)

# Custom host + machine type
solver = LocalOepoSolver(
    host="http://192.168.1.100:5001",
    computer_type=OEPO_ISING_1601,
    gear=GEAR_PRECISE,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `host` | `str` | `http://192.168.137.100:5001` | OEPO device URL |
| `api_path` | `str` | `/api/v1/job/` | API endpoint path |
| `computer_type` | `int` | `None` | Machine ID |
| `gear` | `int` | `None` | Gear mode (0/1/2) |

### Tasks

#### QuboTask

Task for QUBO (Quadratic Unconstrained Binary Optimization) problems — binary variables (0/1).

```python
from plectrum import QuboTask
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = QuboTask(
    name="my-qubo-task",
    data=data,
    shot_count=10,
)
```

#### MinimalIsingEnergyTask

Task for ISING problems — spin variables (-1/+1), minimizes Ising energy.

```python
from plectrum import MinimalIsingEnergyTask
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = MinimalIsingEnergyTask(
    name="my-ising-task",
    data=data,
)
```

#### GeneralTask

Base class for optimization tasks. Use `QuboTask` or `MinimalIsingEnergyTask` for typed convenience.

```python
from plectrum import GeneralTask
import numpy as np

# GeneralTask with explicit data
task = GeneralTask(
    name="my-task",
    data=np.array([[0, 1], [1, 0]]),
)
```

#### TemplateTask

Template-based task for predefined problem types on the cloud platform.

```python
from plectrum import TemplateTask

task = TemplateTask(
    name="my-template-task",
    template_id=10,
    gear=2,
    payload="...",
)
```

### Matrix

The `Matrix` class wraps numpy arrays and handles CSV conversion. Input is validated on creation.

```python
from plectrum import Matrix
import numpy as np

# From numpy array
m = Matrix.from_array(np.eye(3))

# From CSV file
m = Matrix.from_csv("data.csv")

# From CSV string
m = Matrix.from_csv_string("1,0\n0,1")

# Convert back
csv_str = m.to_csv_string()
print(m.shape)  # (3, 3)
```

Raises `MatrixError` for empty data, non-2-D arrays, NaN/Inf values, or non-numeric input.

### Result

All solvers return a unified `Result` via `task.solve()`:

```python
result = task.solve(solver=solver)

print(result["result"]["energy"])       # float — solution energy
print(result["result"]["spin_config"])  # list  — solution vector
print(result["result"]["time"])         # float — computation time (seconds)
print(result["result"]["ok"])           # bool  — success flag
print(result["task_id"])                # str   — task identifier
```

### Gear Modes

Gear modes control the balance between speed and solution quality.

```python
from plectrum import GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# GEAR_FAST = 0      — Fast mode: prioritize speed
# GEAR_BALANCED = 1  — Balanced mode: speed / quality trade-off
# GEAR_PRECISE = 2   — Precise mode: prioritize quality
```

### Error Handling

The SDK provides a clear exception hierarchy. All exceptions chain the original cause via `__cause__` so you always get the full stack trace.

```
PlectrumError                 ← base class, catch-all
├── AuthenticationError       ← missing / invalid API key
├── ClientError               ← HTTP or solver communication failure
│   ├── TimeoutError          ← request or polling timeout
│   └── ConnectionError       ← network-level failure
├── TaskError                 ← task validation or execution failure
├── MatrixError               ← matrix data validation failure
└── ValidationError           ← general input validation failure
```

**Example:**

```python
from plectrum import (
    CloudSolver, QuboTask,
    PlectrumError, AuthenticationError, TimeoutError,
)

try:
    solver = CloudSolver(api_key="your-key")
    task = QuboTask(name="t", data=data)
    result = task.solve(solver=solver)
except AuthenticationError as e:
    print(f"Bad credentials: {e}")
except TimeoutError as e:
    print(f"Timed out: {e}")
except PlectrumError as e:
    print(f"SDK error: {e}")
    # Access the original cause:
    if e.__cause__:
        print(f"Caused by: {e.__cause__}")
```

### Configuration

#### API Key

You can provide an API key in two ways:

1. **Environment Variable** (recommended):
   ```bash
   export PLECTRUM_API_KEY="your-api-key"
   ```

2. **Direct Parameter**:
   ```python
   cloud_solver = CloudSolver(api_key="your-api-key")
   ```

> **Note:** `CloudSolver` raises `AuthenticationError` at init time if no API key is found.

#### Problem Types

```python
from plectrum import QUBO_PROBLEM, ISING_PROBLEM

# QUBO_PROBLEM = 1  (binary variables, 0/1)
# ISING_PROBLEM = 2 (spin variables, -1/+1)
```

### Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=plectrum --cov-report=term-missing
```

### Links

- **Ising Cloud Platform**: https://console.isingq.com/
- **Company Website**: https://www.isingq.com

### License

Apache License 2.0 — See [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Ising Tech. All rights reserved.

---

## 中文

### 关于 Plectrum（拨片）

> *幻想一位音乐家手持拨片，优雅地演奏着旋律。每个音符如同珠子般落入玉盘——那玉盘便是伊辛云平台。*

**Plectrum（拨片）** 是一个统一的 Python SDK，帮助您轻松地将优化问题提交到云端或本地求解器。正如拨片帮助音乐家创造美妙的音乐，Plectrum 帮助您轻松解决复杂的优化问题。

### 特性

- **统一接口**：云端和本地求解器使用同一套 API
- **灵活选择**：运行时可自由切换求解器
- **多种任务类型**：QUBO、ISING、通用任务和模板任务
- **灵活输入**：支持 numpy 数组、pandas DataFrame 和 CSV 文件
- **健壮的错误处理**：清晰的异常层级，完整的堆栈追踪链
- **充分测试**：96%+ 单元测试覆盖率

### 安装

```bash
pip install plectrum-core
```

### 快速开始

```python
from plectrum import CloudSolver, LocalSolver, QuboTask, GEAR_BALANCED
import numpy as np

# 直接使用 numpy 数组创建任务（也支持 pandas DataFrame）
data = np.array([
    [0, 1, 2],
    [1, 0, 3],
    [2, 3, 0]
])

task = QuboTask(
    name="my-task",
    data=data,
)

# 使用云端求解器（伊辛云平台）
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)
cloud_result = task.solve(solver=cloud_solver)

# 或使用本地求解器（本地运行模拟退火算法）
local_solver = LocalSolver(gear=2)
local_result = task.solve(solver=local_solver)

print(f"云端结果: {cloud_result}")
print(f"本地结果: {local_result}")
```

### 求解器

#### CloudSolver

将任务提交至伊辛云平台，并轮询获取结果。

```python
from plectrum import CloudSolver, GEAR_BALANCED, AuthenticationError

# 传入 API Key
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)

# 或通过环境变量 PLECTRUM_API_KEY
cloud_solver = CloudSolver()  # 读取 $PLECTRUM_API_KEY

# 未提供 API Key 时抛出 AuthenticationError
try:
    solver = CloudSolver(api_key="")
except AuthenticationError as e:
    print(e)  # "API key is required. ..."
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `api_key` | `str` | `$PLECTRUM_API_KEY` | API 密钥（必填） |
| `host` | `str` | `https://api.isingq.com` | 云端 API 地址 |
| `computer_type` | `int` | `OEPO_ISING_1601` | 机器类型 ID |
| `gear` | `int` | `GEAR_PRECISE` | 档位模式 (0/1/2) |
| `poll_interval` | `int` | `2` | 轮询间隔（秒） |
| `timeout` | `int` | `300` | 最大等待时间（秒） |

#### LocalSolver

在本地运行模拟退火算法，无需网络。

```python
from plectrum import LocalSolver, GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# 快速模式（优先速度，1,000 次迭代）
local_solver = LocalSolver(gear=GEAR_FAST)

# 均衡模式（5,000 次迭代）
local_solver = LocalSolver(gear=GEAR_BALANCED)

# 精准模式（优先质量，10,000 次迭代）— 默认
local_solver = LocalSolver(gear=GEAR_PRECISE)
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `gear` | `int` | `GEAR_PRECISE` | 档位模式 (0/1/2) |
| `algorithm` | `str` | `"sa"` | 算法（`"sa"` = 模拟退火） |

#### LocalOepoSolver

通过 HTTP 将任务提交至本地 OEPO 量子退火设备或模拟器。

```python
from plectrum import LocalOepoSolver, OEPO_ISING_1601, GEAR_PRECISE

# 默认地址 (192.168.137.100:5001)
solver = LocalOepoSolver(gear=GEAR_PRECISE)

# 自定义地址 + 机器类型
solver = LocalOepoSolver(
    host="http://192.168.1.100:5001",
    computer_type=OEPO_ISING_1601,
    gear=GEAR_PRECISE,
)
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `host` | `str` | `http://192.168.137.100:5001` | OEPO 设备地址 |
| `api_path` | `str` | `/api/v1/job/` | API 端点路径 |
| `computer_type` | `int` | `None` | 机器类型 ID |
| `gear` | `int` | `None` | 档位模式 (0/1/2) |

### 任务

#### QuboTask

用于 QUBO（二次无约束二进制优化）问题 — 二进制变量 (0/1)。

```python
from plectrum import QuboTask
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = QuboTask(
    name="my-qubo-task",
    data=data,
    shot_count=10,
)
```

#### MinimalIsingEnergyTask

用于 ISING 问题 — 自旋变量 (-1/+1)，最小化伊辛能量。

```python
from plectrum import MinimalIsingEnergyTask
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = MinimalIsingEnergyTask(
    name="my-ising-task",
    data=data,
)
```

#### GeneralTask

优化任务的基类。建议使用 `QuboTask` 或 `MinimalIsingEnergyTask` 替代。

```python
from plectrum import GeneralTask
import numpy as np

task = GeneralTask(
    name="my-task",
    data=np.array([[0, 1], [1, 0]]),
)
```

#### TemplateTask

基于模板的任务，用于云平台预定义的问题类型。

```python
from plectrum import TemplateTask

task = TemplateTask(
    name="my-template-task",
    template_id=10,
    gear=2,
    payload="...",
)
```

### 矩阵 (Matrix)

`Matrix` 类封装 numpy 数组并处理 CSV 转换。创建时自动验证输入。

```python
from plectrum import Matrix
import numpy as np

# 从 numpy 数组创建
m = Matrix.from_array(np.eye(3))

# 从 CSV 文件创建
m = Matrix.from_csv("data.csv")

# 从 CSV 字符串创建
m = Matrix.from_csv_string("1,0\n0,1")

# 转换回 CSV 字符串
csv_str = m.to_csv_string()
print(m.shape)  # (3, 3)
```

空数据、非二维数组、NaN/Inf 值或非数字输入会抛出 `MatrixError`。

### 结果 (Result)

所有求解器通过 `task.solve()` 返回统一的结果格式：

```python
result = task.solve(solver=solver)

print(result["result"]["energy"])       # float — 解的能量值
print(result["result"]["spin_config"])  # list  — 解向量
print(result["result"]["time"])         # float — 计算时间（秒）
print(result["result"]["ok"])           # bool  — 是否成功
print(result["task_id"])                # str   — 任务标识符
```

### 档位模式 (Gear)

Gear 模式控制求解速度和质量的平衡。

```python
from plectrum import GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# GEAR_FAST = 0      — 快速模式：优先速度
# GEAR_BALANCED = 1  — 均衡模式：速度与质量平衡
# GEAR_PRECISE = 2   — 精准模式：优先质量
```

### 错误处理

SDK 提供清晰的异常层级。所有异常通过 `__cause__` 链接原始原因，确保完整的堆栈追踪。

```
PlectrumError                 ← 基类，可统一捕获
├── AuthenticationError       ← API 密钥缺失或无效
├── ClientError               ← HTTP 或求解器通信失败
│   ├── TimeoutError          ← 请求或轮询超时
│   └── ConnectionError       ← 网络连接失败
├── TaskError                 ← 任务验证或执行失败
├── MatrixError               ← 矩阵数据验证失败
└── ValidationError           ← 通用输入验证失败
```

**示例：**

```python
from plectrum import (
    CloudSolver, QuboTask,
    PlectrumError, AuthenticationError, TimeoutError,
)

try:
    solver = CloudSolver(api_key="your-key")
    task = QuboTask(name="t", data=data)
    result = task.solve(solver=solver)
except AuthenticationError as e:
    print(f"认证失败: {e}")
except TimeoutError as e:
    print(f"超时: {e}")
except PlectrumError as e:
    print(f"SDK 错误: {e}")
    if e.__cause__:
        print(f"原因: {e.__cause__}")
```

### 配置

#### API Key

可以通过两种方式配置：

1. **环境变量**（推荐）：
   ```bash
   export PLECTRUM_API_KEY="your-api-key"
   ```

2. **直接传入参数**：
   ```python
   cloud_solver = CloudSolver(api_key="your-api-key")
   ```

> **注意：** 如果未找到 API Key，`CloudSolver` 会在初始化时抛出 `AuthenticationError`。

#### 问题类型

```python
from plectrum import QUBO_PROBLEM, ISING_PROBLEM

# QUBO_PROBLEM = 1（二进制变量，0/1）
# ISING_PROBLEM = 2（自旋变量，-1/+1）
```

### 开发

```bash
# 以可编辑模式安装，包含开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 运行测试并查看覆盖率
pytest tests/ --cov=plectrum --cov-report=term-missing
```

### 相关链接

- **伊辛云平台**：https://console.isingq.com/
- **公司官网**：https://www.isingq.com

### 许可证

Apache 许可证 2.0 — 详见 [LICENSE](LICENSE) 文件。

版权所有 (c) 2026 Ising Tech。保留所有权利。
