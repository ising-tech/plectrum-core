# Plectrum Core SDK

A unified Python SDK for submitting solving requests to cloud or local solvers.

## Features

- **Unified Interface**: Single API for both cloud and local solvers
- **Flexible Solver Selection**: Choose solver at runtime for easy comparison
- **Config-File Initialization**: Create clients directly from `config/cloud.ini`
- **Multiple Task Types**: Support for general and template tasks
- **Matrix Support**: Easy input with CSV files or numpy arrays
- **Direct Result Access**: `task.solve()` returns a `Result` object with typed attributes

## Installation

```bash
pip install plectrum-core
```

## Quick Start

```python
import numpy as np
from plectrum import CloudClient, LocalClient, GeneralTask, Matrix, QUBO_PROBLEM

# Initialize clients from config file (reads config/cloud.ini)
cloud_client = CloudClient.from_config("config/cloud.ini")
local_client = LocalClient.from_config("config/cloud.ini")

# Build matrix from numpy array
data = np.array([
    [0, -1, -1],
    [-1, 0, -1],
    [-1, -1, 0],
])
matrix = Matrix.from_array(data)

# Create task
task = GeneralTask(
    name="my-task",
    matrix=matrix,
    computer_type_id=2,
    question_type=QUBO_PROBLEM,
    calculate_count=10,
    post_process=1,
)

# Solve with local solver — Result object returned directly
result = task.solve(local_client)
print(f"Energy: {result.energy}")
print(f"Spin config: {result.spin_config}")
print(f"Time: {result.time}s")

# Solve with cloud solver
result = task.solve(cloud_client)
print(f"Energy: {result.energy}")
print(f"Spin config: {result.spin_config}")
```

## Configuration

Create `config/cloud.ini`:

```ini
[CLOUD]
HOST: https://api.isingq.com
API_KEY: your-api-key

[LOCAL]
HOST: http://192.168.137.100:5001
```

### Alternative: Direct Parameters

```python
cloud_client = CloudClient(api_key="your-api-key", host="https://api.isingq.com")
local_client = LocalClient(host="http://192.168.137.100:5001")
```

### Alternative: Environment Variable

```bash
export PLECTRUM_API_KEY="your-api-key"
```

```python
cloud_client = CloudClient()  # reads PLECTRUM_API_KEY from environment
```

## API Reference

### Matrix

```python
from plectrum import Matrix
import numpy as np

# From CSV file
matrix = Matrix.from_csv("data.csv")

# From CSV string
matrix = Matrix.from_csv_string(csv_string)

# From numpy array
array = np.array([[1, 2], [3, 4]])
matrix = Matrix.from_array(array)
```

### Client

```python
from plectrum import CloudClient, LocalClient

# From config file (recommended)
cloud = CloudClient.from_config("config/cloud.ini")
local = LocalClient.from_config("config/cloud.ini")

# Cloud client with explicit parameters
cloud = CloudClient(api_key="your-key", host="https://api.isingq.com")

# Local client with explicit host
local = LocalClient(host="http://192.168.137.100:5001")
```

### Task

```python
from plectrum import GeneralTask, TemplateTask, QUBO_PROBLEM

# General task with matrix
task = GeneralTask(
    name="my-task",
    matrix=matrix,
    computer_type_id=2,
    question_type=QUBO_PROBLEM,
    calculate_count=10,
    post_process=1,
)

# Template task
task = TemplateTask(
    name="my-template-task",
    template_id=1,
    computer_type_id=2,
    payload="{}",
)

# Submit to solver — returns Result object directly
result = task.solve(client)
```

### Result

`task.solve()` returns a `Result` object with the following attributes:

| Attribute     | Type    | Description                    |
|---------------|---------|--------------------------------|
| `energy`      | `float` | Optimal energy value           |
| `spin_config` | `list`  | Spin/variable configuration    |
| `time`        | `float` | Computation time in seconds    |
| `task_id`     | `str`   | Task identifier                |
| `task_name`   | `str`   | Task name                      |
| `ok`          | `bool`  | Whether the solve succeeded    |
| `msg`         | `str`   | Status message                 |
| `timestamp`   | `int`   | Result timestamp (ms)          |

```python
result = task.solve(client)
print(result.energy)       # -3.0
print(result.spin_config)  # [1, -1, 1]
print(result.time)         # 0.134
print(result.ok)           # True
```

## Architecture

The SDK is organized into the following modules:

- `plectrum.matrix`: Matrix data handling
- `plectrum.client`: Solver clients (Cloud, Local)
- `plectrum.task`: Task definitions (General, Template)
- `plectrum.result`: Unified `Result` class

## License

MIT License
