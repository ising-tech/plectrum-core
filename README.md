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
- **Multiple Task Types**: Support for general and template tasks
- **Flexible Input**: Support numpy arrays and pandas DataFrames

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
# Set gear mode (gear) on solver: 0=fast, 1=balanced, 2=precise
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)
cloud_result = task.solve(solver=cloud_solver)

# Or use local solver with precise mode
local_solver = LocalSolver(gear=2)
local_result = task.solve(solver=local_solver)

print(f"Cloud result: {cloud_result}")
print(f"Local result: {local_result}")
```

### Solvers

#### CloudSolver

Submits tasks to the Ising Cloud Platform.

```python
from plectrum import CloudSolver, GEAR_BALANCED

# With API key and gear mode
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)

# Or from environment variable PLECTRUM_API_KEY
cloud_solver = CloudSolver(gear=2)  # precise mode

# Get task status
task_info = cloud_solver.get_task("task-id")
```

#### LocalSolver

Submits tasks to a local solver service.

```python
from plectrum import LocalSolver, GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# Default host with gear mode
local_solver = LocalSolver(gear=GEAR_BALANCED)

# Fast mode (speed prioritized)
local_solver = LocalSolver(gear=GEAR_FAST)

# Precise mode (quality prioritized)
local_solver = LocalSolver(gear=GEAR_PRECISE)

# Custom host
local_solver = LocalSolver(host="http://192.168.137.100:5001")
```

#### LocalOepoSolver

Alias for LocalSolver (for backward compatibility).

### Tasks

#### QuboTask

Task for QUBO (Quadratic Unconstrained Binary Optimization) problems.

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

Task for ISING problems (minimizing Ising energy).

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

General task for optimization problems.

```python
from plectrum import GeneralTask, QUBO_PROBLEM, ISING_PROBLEM
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = GeneralTask(
    name="my-task",
    data=data,
    question_type=QUBO_PROBLEM,  # 1 = QUBO, 2 = ISING
)
```

### Gear Modes

Gear (gear) modes control the balance between speed and solution quality.

```python
from plectrum import GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# GEAR_FAST = 0      # 快速模式 (Fast mode) - prioritize speed
# GEAR_BALANCED = 1  # 均衡模式 (Balanced mode) - balance between speed and quality
# GEAR_PRECISE = 2   # 精准模式 (Precise mode) - prioritize quality
```

### Configuration

#### API Key

You can provide API key in two ways:

1. **Environment Variable** (recommended):
   ```bash
   export PLECTRUM_API_KEY="your-api-key"
   ```

2. **Direct Parameter**:
   ```python
   cloud_solver = CloudSolver(api_key="your-api-key")
   ```

#### Problem Types

```python
from plectrum import QUBO_PROBLEM, ISING_PROBLEM

# QUBO = 1 (binary variables, 0/1)
# ISING = 2 (spin variables, -1/+1)
```

### Links

- **Ising Cloud Platform**: https://console.isingq.com/
- **Company Website**: https://www.isingq.com

### License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Ising Tech. All rights reserved.

---

## 中文

### 关于 Plectrum（拨片）

> *幻想一位音乐家手持拨片，优雅地演奏着旋律。每个音符如同珠子般落入玉盘——那玉盘便是伊辛云平台。*

**Plectrum（拨片）** 是一个统一的 Python SDK，帮助您轻松地将优化问题提交到云端或本地求解器。正如拨片帮助音乐家创造美妙的音乐，Plectrum 帮助您轻松解决复杂的优化问题。

### 特性

- **统一接口**：云端和本地求解器使用同一套 API
- **灵活选择**：运行时可自由切换求解器
- **多种任务类型**：支持通用任务和模板任务
- **灵活输入**：支持 numpy 数组和 pandas DataFrame

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
# 在求解器上设置 gear 模式：0=快速，1=均衡，2=精准
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)
cloud_result = task.solve(solver=cloud_solver)

# 或使用本地求解器，精准模式
local_solver = LocalSolver(gear=2)
local_result = task.solve(solver=local_solver)

print(f"云端结果: {cloud_result}")
print(f"本地结果: {local_result}")
```

### 求解器

#### CloudSolver

将任务提交至伊辛云平台。

```python
from plectrum import CloudSolver, GEAR_BALANCED

# 传入 API Key 和 gear 模式
cloud_solver = CloudSolver(api_key="your-api-key", gear=GEAR_BALANCED)

# 或通过环境变量 PLECTRUM_API_KEY
cloud_solver = CloudSolver(gear=2)  # 精准模式

# 获取任务状态
task_info = cloud_solver.get_task("task-id")
```

#### LocalSolver

将任务提交至本地求解服务。

```python
from plectrum import LocalSolver, GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# 默认地址 + gear 模式
local_solver = LocalSolver(gear=GEAR_BALANCED)

# 快速模式（优先速度）
local_solver = LocalSolver(gear=GEAR_FAST)

# 精准模式（优先质量）
local_solver = LocalSolver(gear=GEAR_PRECISE)

# 自定义地址
local_solver = LocalSolver(host="http://192.168.137.100:5001")
```

#### LocalOepoSolver

LocalSolver 的别名（向后兼容）。

### 任务

#### QuboTask

用于 QUBO（二次无约束二进制优化）问题。

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

用于 ISING 问题（最小化伊辛能量）。

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

通用优化任务。

```python
from plectrum import GeneralTask, QUBO_PROBLEM, ISING_PROBLEM
import numpy as np

data = np.array([[0, 1], [1, 0]])
task = GeneralTask(
    name="my-task",
    data=data,
    question_type=QUBO_PROBLEM,  # 1 = QUBO, 2 = ISING
)
```

### Gear 模式

Gear (gear) 模式控制求解速度和质量的平衡。

```python
from plectrum import GEAR_FAST, GEAR_BALANCED, GEAR_PRECISE

# GEAR_FAST = 0      # 快速模式 - 优先速度
# GEAR_BALANCED = 1  # 均衡模式 - 速度和质量平衡
# GEAR_PRECISE = 2   # 精准模式 - 优先质量
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

#### 问题类型

```python
from plectrum import QUBO_PROBLEM, ISING_PROBLEM

# QUBO = 1（二进制变量，0/1）
# ISING = 2（自旋变量，-1/+1）
```

### 相关链接

- **伊辛云平台**：https://console.isingq.com/
- **公司官网**：https://www.isingq.com

### 许可证

Apache 许可证 2.0 - 详见 [LICENSE](LICENSE) 文件。

版权所有 (c) 2026 Ising Tech。保留所有权利。
