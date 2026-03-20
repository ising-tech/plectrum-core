"""
Example usage of the Plectrum Core SDK.

Demonstrates the calling pattern for both cloud and local solvers,
using config-file-based client initialization and direct Result access.
"""

import numpy as np

from plectrum import CloudClient, LocalClient, GeneralTask, Matrix, QUBO_PROBLEM


def test_local():
    """Test local solver."""
    # Initialize local client from config file
    client = LocalClient.from_config("config/cloud.ini")

    # Build a small QUBO matrix using numpy
    data = np.array([
        [0, -1, -1],
        [-1, 0, -1],
        [-1, -1, 0],
    ])
    matrix = Matrix.from_array(data)

    # Create task
    task = GeneralTask(
        name="test-local",
        matrix=matrix,
        computer_type_id=2,
        question_type=QUBO_PROBLEM,
        calculate_count=10,
        post_process=1,
    )

    # Submit and receive Result directly
    result = task.solve(client)

    print("=== Local Solver Result ===")
    print(f"Energy      : {result.energy}")
    print(f"Spin config : {result.spin_config}")
    print(f"Time        : {result.time}s")
    print(f"Task ID     : {result.task_id}")
    print(f"OK          : {result.ok}")
    return result


def test_cloud():
    """Test cloud solver."""
    # Initialize cloud client from config file
    client = CloudClient.from_config("config/cloud.ini")

    # Build a small QUBO matrix using numpy
    data = np.array([
        [0, -1, -1],
        [-1, 0, -1],
        [-1, -1, 0],
    ])
    matrix = Matrix.from_array(data)

    # Create task
    task = GeneralTask(
        name="test-cloud",
        matrix=matrix,
        computer_type_id=2,
        question_type=QUBO_PROBLEM,
        calculate_count=10,
        post_process=1,
    )

    # Submit and receive Result directly
    result = task.solve(client)

    print("=== Cloud Solver Result ===")
    print(f"Energy      : {result.energy}")
    print(f"Spin config : {result.spin_config}")
    print(f"Time        : {result.time}s")
    print(f"Task ID     : {result.task_id}")
    print(f"OK          : {result.ok}")
    return result


if __name__ == "__main__":
    test_local()
    test_cloud()
