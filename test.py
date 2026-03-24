"""Test case to compare three solver methods."""

import time
import numpy as np

from plectrum import (
    CloudSolver,
    LocalSolver,
    LocalOepoSolver,
    MinimalIsingEnergyTask,
    QuboTask,
    GEAR_BALANCED,
    GEAR_PRECISE,
    OEPO_ISING_1601,
)

# 读取矩阵数据
DATA_PATH = "/Users/jjhao/PycharmProjects/interface_api/dev/Q_norm.csv"
API_KEY = ""


def load_data():
    """Load test matrix data as numpy array."""
    # 直接从 CSV 加载为 numpy array
    data = np.loadtxt(DATA_PATH, delimiter=',')
    print(f"Loaded matrix shape: {data.shape}")
    return data


def test_local_solver():
    """Test LocalSolver with balanced gear."""
    print("\n=== LocalSolver (GEAR_PRECISE) ===")
    data = load_data()
    
    # gear now belongs to solver
    solver = LocalOepoSolver(gear=GEAR_PRECISE)
    task = QuboTask(name="test_qubo_task", data=data)
    
    start_time = time.time()
    result = task.solve(solver=solver)
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_local_oepo_solver():
    """Test LocalOepoSolver with QuboTask."""
    print("\n=== LocalOepoSolver (QuboTask) ===")
    data = load_data()
    
    # computer_type now belongs to solver (machine type), gear is gear mode
    solver = LocalOepoSolver(computer_type=OEPO_ISING_1601, gear=GEAR_PRECISE)
    task = QuboTask(name="test_qubo_task", data=data)
    
    start_time = time.time()
    result = task.solve(solver=solver)
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_local_oepo_solver_ising():
    """Test LocalOepoSolver with MinimalIsingEnergyTask."""
    print("\n=== LocalOepoSolver (MinimalIsingEnergyTask) ===")
    data = load_data()
    
    # computer_type now belongs to solver (machine type), gear is gear mode
    solver = LocalOepoSolver(computer_type=OEPO_ISING_1601, gear=GEAR_PRECISE)
    task = MinimalIsingEnergyTask(name="test_ising_task", data=data)
    
    start_time = time.time()
    result = task.solve(solver=solver)
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_cloud_solver():
    """Test CloudSolver with QuboTask."""
    print("\n=== CloudSolver (QuboTask) ===")
    data = load_data()
    
    # CloudSolver - requires gear
    solver = CloudSolver(api_key=API_KEY, gear=GEAR_BALANCED)
    task = QuboTask(name="test_qubo_task", data=data)
    
    start_time = time.time()
    result = task.solve(solver=solver)
    elapsed_time = time.time() - start_time
    
    print(f"Energy: {result['result']['energy']}")
    print(f"Time: {elapsed_time:.3f}s")
    
    return result


def test_cloud_solver_ising():
    """Test CloudSolver with MinimalIsingEnergyTask."""
    print("\n=== CloudSolver (MinimalIsingEnergyTask) ===")
    data = load_data()
    
    # CloudSolver - requires gear
    solver = CloudSolver(api_key=API_KEY, gear=GEAR_BALANCED)
    task = MinimalIsingEnergyTask(name="test_ising_task", data=data)
    
    start_time = time.time()
    result = task.solve(solver=solver)
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
    
    # Test LocalOepoSolver with MinimalIsingEnergyTask
    try:
        results['LocalOepoSolver-Ising'] = test_local_oepo_solver_ising()
    except Exception as e:
        print(f"LocalOepoSolver-Ising failed: {e}")
        results['LocalOepoSolver-Ising'] = None
    
    # Test CloudSolver
    try:
        results['CloudSolver'] = test_cloud_solver()
    except Exception as e:
        print(f"CloudSolver failed: {e}")
        results['CloudSolver'] = None

    # Test CloudSolver with MinimalIsingEnergyTask
    try:
        results['CloudSolver-Ising'] = test_cloud_solver_ising()
    except Exception as e:
        print(f"CloudSolver-Ising failed: {e}")
        results['CloudSolver-Ising'] = None
    
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
