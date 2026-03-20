"""Test case to compare three solver methods."""

import time
import numpy as np

from plectrum import (
    CloudSolver,
    LocalSolver,
    LocalOepoSolver,
    MinimalIsingEnergyTask,
    QuboTask,
    GeneralTask,
    Matrix,
    QUBO_PROBLEM,
    ISING_PROBLEM,
)

# 读取矩阵数据
DATA_PATH = "/Users/jjhao/PycharmProjects/interface_api/dev/Q_norm.csv"
API_KEY = "7842b01e504a48bd983d4cb936dbb777"  # 从 config/cloud.ini 读取


def load_data():
    """Load test matrix data."""
    matrix = Matrix.from_csv(DATA_PATH)
    print(f"Loaded matrix: {matrix.shape}")
    return matrix


def test_local_solver():
    """Test LocalSolver."""
    print("\n=== LocalSolver ===")
    data = load_data()
    
    task = QuboTask(name="test_qubo_task", data=data, computer_type_id=1)
    
    start_time = time.time()
    result = task.solve(solver=LocalSolver())
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_local_oepo_solver():
    """Test LocalOepoSolver."""
    print("\n=== LocalOepoSolver ===")
    data = load_data()
    
    task = QuboTask(name="test_qubo_task", data=data, computer_type_id=2)
    
    start_time = time.time()
    result = task.solve(solver=LocalOepoSolver())
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_cloud_solver():
    """Test CloudSolver."""
    print("\n=== CloudSolver ===")
    data = load_data()
    
    task = QuboTask(name="test_qubo_task", data=data, computer_type_id=1)
    
    start_time = time.time()
    result = task.solve(solver=CloudSolver(api_key=API_KEY))
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def compare_results():
    """Compare results from different solvers."""
    print("=" * 50)
    print("Comparing Solver Results")
    print("=" * 50)
    
    results = {}
    
    # Test LocalSolver
    try:
        results['LocalSolver'] = test_local_solver()
    except Exception as e:
        print(f"LocalSolver failed: {e}")
        results['LocalSolver'] = None
    
    # Test LocalOepoSolver
    try:
        results['LocalOepoSolver'] = test_local_oepo_solver()
    except Exception as e:
        print(f"LocalOepoSolver failed: {e}")
        results['LocalOepoSolver'] = None
    
    # Test CloudSolver
    try:
        results['CloudSolver'] = test_cloud_solver()
    except Exception as e:
        print(f"CloudSolver failed: {e}")
        results['CloudSolver'] = None
    
    # Print comparison table
    print("\n" + "=" * 50)
    print("Results Comparison")
    print("=" * 50)
    print(f"{'Solver':<20} {'Energy':<20} {'Status'}")
    print("-" * 50)
    
    for name, result in results.items():
        if result is not None:
            energy = result['result']['energy']
            print(f"{name:<20} {energy:<20.6f} OK")
        else:
            print(f"{name:<20} {'N/A':<20} FAILED")
    
    # Find best result
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        best = min(valid_results.items(), key=lambda x: x[1]['result']['energy'])
        print(f"\nBest solver: {best[0]} with energy: {best[1]['result']['energy']:.6f}")
    
    return results


if __name__ == "__main__":
    compare_results()
