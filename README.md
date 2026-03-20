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
from plectrum import CloudClient, LocalClient, GeneralTask, Matrix

# Create matrix from CSV
matrix = Matrix.from_csv("data.csv")

# Create task
task = GeneralTask(
    name="my-task",
    matrix=matrix,
    computer_type_id=1,
    question_type=1,
)

# Use cloud solver
cloud_solver = CloudClient(api_key="your-api-key")
cloud_result = task.solve(solver=cloud_solver)

# Or use local solver
local_solver = LocalClient(host="http://192.168.137.100:5001")
local_result = task.solve(solver=local_solver)

print(f"Cloud result: {cloud_result}")
print(f"Local result: {local_result}")
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
   cloud_solver = CloudClient(api_key="your-api-key")
   ```

### Local Solver Host

```python
# Use default local host
local_solver = LocalClient()

# Or specify custom host
local_solver = LocalClient(host="http://192.168.137.100:5001")
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

# Cloud client (uses default cloud API)
cloud = CloudClient()

# Cloud client with custom API key
cloud = CloudClient(api_key="your-key")

# Local client (uses default local host)
local = LocalClient()

# Local client with custom host
local = LocalClient(host="http://192.168.137.100:5001")
```

### Task

```python
from plectrum import GeneralTask, TemplateTask

# General task with matrix
task = GeneralTask(
    name="my-task",
    matrix=matrix,
    computer_type_id=1,
    question_type=1,
)

# Template task
task = TemplateTask(
    name="my-template-task",
    template_id=1,
    computer_type_id=1,
    payload="{}",
)

# Submit to solver
result = task.solve(solver=client)
```

## Architecture

The SDK is organized into the following modules:

- `plectrum.matrix`: Matrix data handling
- `plectrum.client`: Solver clients (Cloud, Local)
- `plectrum.task`: Task definitions (General, Template)

## License

MIT License
