# Plectrum Core SDK

A unified Python SDK for submitting solving requests to cloud or local solvers.

## Features

- **Unified Interface**: Single API for both cloud and local solvers
- **Flexible Solver Selection**: Choose solver at runtime for easy comparison
- **Multiple Task Types**: Support for general and template tasks
- **Matrix Support**: Easy input with CSV files or numpy arrays

## Installation

```bash
pip install plectrum-core
```

## Quick Start

```python
from plectrum import (
    CloudSolver,
    GeneralTask,
    LocalOepoSolver,
    LocalSolver,
    Matrix,
    QUBO_PROBLEM,
)

# Create matrix from CSV
matrix = Matrix.from_csv("data.csv")

# Create task
task = GeneralTask(
    name="my-task",
    matrix=matrix,
    gear=1,
    question_type=QUBO_PROBLEM,
)

# Use traditional local solver
local_result = task.solve(solver=LocalSolver())

# Or use local OEPO solver service
local_oepo_result = task.solve(
    solver=LocalOepoSolver(host="http://192.168.137.100:5001")
)

# Or use cloud solver (defaults to gear=2 if task gear is omitted)
cloud_task = GeneralTask(
    name="my-cloud-task",
    matrix=matrix,
    question_type=QUBO_PROBLEM,
)
cloud_result = cloud_task.solve(solver=CloudSolver(api_key="your-api-key"))

print(local_result.energy)
print(local_oepo_result.energy)
print(cloud_result.energy)
```

## Configuration

### API Key

You can provide API key in three ways:

1. **Environment Variable** (recommended):
   ```bash
   export PLECTRUM_API_KEY="your-api-key"
   ```

2. **Direct Parameter**:
   ```python
   from plectrum import CloudSolver

   cloud_solver = CloudSolver(api_key="your-api-key")
   ```

### Local Solver Host

```python
from plectrum import LocalOepoSolver

# Use default local host
local_solver = LocalOepoSolver()

# Or specify custom host
custom_local_solver = LocalOepoSolver(host="http://192.168.137.100:5001")
```

### Gear Selection

- Local OEPO solver preserves the `gear` set on `GeneralTask` / `TemplateTask`
- Cloud solver keeps the same interface, and when `gear` is omitted it defaults to `2`

```python
import numpy as np

from plectrum import GeneralTask, Matrix

matrix = Matrix.from_array(np.array([[1.0, -2.0], [-2.0, 1.0]]))
task = GeneralTask(name="local-task", matrix=matrix, gear=1)
cloud_task = GeneralTask(name="cloud-task", matrix=matrix)
```

## API Reference

### Matrix

```python
from plectrum import Matrix
import numpy as np

csv_string = "1,2\n3,4\n"

# From CSV file
matrix_from_file = Matrix.from_csv("data.csv")

# From CSV string
matrix_from_string = Matrix.from_csv_string(csv_string)

# From numpy array
array = np.array([[1, 2], [3, 4]])
matrix_from_array = Matrix.from_array(array)
```

### Client

```python
from plectrum import CloudSolver, LocalOepoSolver, LocalSolver

# Traditional local solver (in process)
local = LocalSolver()

# Cloud solver (uses default cloud API)
cloud = CloudSolver(api_key="your-key")

# Local OEPO solver (uses default local host)
local_oepo = LocalOepoSolver()

# Local OEPO solver with custom host
custom_local_oepo = LocalOepoSolver(host="http://192.168.137.100:5001")
```

### Task

```python
import numpy as np

from plectrum import GeneralTask, LocalSolver, Matrix, TemplateTask

matrix = Matrix.from_array(np.array([[1.0, -2.0], [-2.0, 1.0]]))

# General task with matrix
general_task = GeneralTask(
    name="my-task",
    matrix=matrix,
    gear=1,
    question_type=1,
)

# Template task
template_task = TemplateTask(
    name="my-template-task",
    template_id=1,
    computer_type_id=1,
    payload="{}",
)

# Submit to solver
result = general_task.solve(solver=LocalSolver())
```

## Architecture

The SDK is organized into the following modules:

- `plectrum.matrix`: Matrix data handling
- `plectrum.client`: Backward-compatible service clients (Cloud, Local)
- `plectrum.solver`: Solver-oriented API (CloudSolver, LocalOepoSolver, LocalSolver)
- `plectrum.task`: Task definitions (General, Template)

## License

MIT License
