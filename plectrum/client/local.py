"""Local solver for Plectrum SDK."""

import time
import random
import uuid
import numpy as np

from plectrum.client.base import BaseSolver
from plectrum.const import (
    DEFAULT_LOCAL_HOST,
    DEFAULT_LOCAL_API_PATH,
    QUBO_PROBLEM,
    ISING_PROBLEM,
    GEAR_FAST,
    GEAR_BALANCED,
    GEAR_PRECISE,
)
from plectrum.exceptions import ClientError
from plectrum.result import Result

from plectrum.task import GeneralTask, MinimalIsingEnergyTask, QuboTask


class LocalSolver(BaseSolver):
    """Local solver using classical algorithms.
    
    This solver runs optimization algorithms locally:
    - Simulated Annealing (SA)
    - Parallel Tempering (PT)
    """

    SUPPORTED_TASK_TYPES = [GeneralTask, MinimalIsingEnergyTask, QuboTask]

    def __init__(
        self,
        gear: int = GEAR_PRECISE,
        algorithm: str = "sa",
    ):
        """Initialize local solver.

        Args:
            gear: Gear mode (0=fast, 1=balanced, 2=precise).
                  Affects the number of iterations.
            algorithm: Algorithm to use ("sa" for Simulated Annealing).
        """
        super().__init__(api_key=None, host=None, computer_type=None, gear=gear)
        self._algorithm = algorithm
        self._iteration_config = {
            GEAR_FAST: 1000,
            GEAR_BALANCED: 5000,
            GEAR_PRECISE: 10000,
        }

    def solve(self, task_data: dict) -> dict:
        """Solve task using local algorithm.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary in unified format
        """
        # Validate task type
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        if task_type == "general":
            return self._solve_general_task(task_data)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

    def _solve_general_task(self, task_data: dict) -> dict:
        """Solve general task using local algorithm.
        
        Args:
            task_data: Task data dictionary
            
        Returns:
            Result dictionary
        """
        csv_string = task_data.get("csv_string")
        if csv_string is None:
            raise ClientError("csv_string is required for local solver")
        
        # Parse CSV data
        matrix = self._parse_csv_string(csv_string)
        
        # Get question type
        question_type = task_data.get("params", {}).get("type", QUBO_PROBLEM)
        
        # Get iterations from gear
        iterations = self._iteration_config.get(self._gear, 5000)
        
        # Run simulated annealing
        start_time = time.time()
        
        if question_type == ISING_PROBLEM:
            # ISING problem (spin variables: -1, 1)
            best_state, best_energy = self._simulated_annealing_ising(matrix, iterations)
        else:
            # QUBO problem (binary variables: 0, 1)
            best_state, best_energy = self._simulated_annealing_qubo(matrix, iterations)
        
        elapsed_time = time.time() - start_time
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        return {
            "result": {
                "energy": best_energy,
                "spin_config": best_state,
                "time": elapsed_time,
                "task_id": task_id,
                "task_name": task_id,
                "ok": True,
                "msg": "success",
                "timestamp": int(time.time() * 1000),
            },
            "task_id": task_id,
            "status": 1,
        }

    def _parse_csv_string(self, csv_string: str) -> np.ndarray:
        """Parse CSV string to numpy array.
        
        Args:
            csv_string: CSV data string
            
        Returns:
            Numpy array (matrix)
        """
        lines = csv_string.strip().split('\n')
        data = []
        for line in lines:
            row = [float(x) for x in line.split(',')]
            data.append(row)
        return np.array(data)

    def _simulated_annealing_qubo(self, matrix: np.ndarray, iterations: int) -> tuple:
        """Simulated Annealing for QUBO problem.
        
        Args:
            matrix: QUBO matrix (upper triangular)
            iterations: Number of iterations
            
        Returns:
            (best_state, best_energy)
        """
        n = matrix.shape[0]
        
        # Initial random state (binary: 0 or 1)
        current_state = np.random.randint(0, 2, n)
        current_energy = self._calculate_qubo_energy(matrix, current_state)
        
        best_state = current_state.copy()
        best_energy = current_energy
        
        # Temperature schedule
        T0 = 100.0
        Tf = 0.01
        T = T0
        
        for i in range(iterations):
            # Generate neighbor by flipping one bit
            flip_idx = random.randint(0, n - 1)
            new_state = current_state.copy()
            new_state[flip_idx] = 1 - new_state[flip_idx]
            
            new_energy = self._calculate_qubo_energy(matrix, new_state)
            
            # Acceptance probability
            delta = new_energy - current_energy
            
            if delta < 0 or random.random() < np.exp(-delta / T):
                current_state = new_state
                current_energy = new_energy
                
                if current_energy < best_energy:
                    best_state = current_state.copy()
                    best_energy = current_energy
            
            # Cool down
            T = T0 * (Tf / T0) ** (i / iterations)
        
        return best_state.tolist(), best_energy

    def _simulated_annealing_ising(self, matrix: np.ndarray, iterations: int) -> tuple:
        """Simulated Annealing for ISING problem.
        
        Args:
            matrix: ISING interaction matrix (J matrix)
            iterations: Number of iterations
            
        Returns:
            (best_state, best_energy)
        """
        n = matrix.shape[0]
        
        # Initial random state (spin: -1 or 1)
        current_state = np.random.choice([-1, 1], n)
        current_energy = self._calculate_ising_energy(matrix, current_state)
        
        best_state = current_state.copy()
        best_energy = current_energy
        
        # Temperature schedule
        T0 = 100.0
        Tf = 0.01
        T = T0
        
        for i in range(iterations):
            # Generate neighbor by flipping one spin
            flip_idx = random.randint(0, n - 1)
            new_state = current_state.copy()
            new_state[flip_idx] = -new_state[flip_idx]
            
            new_energy = self._calculate_ising_energy(matrix, new_state)
            
            # Acceptance probability
            delta = new_energy - current_energy
            
            if delta < 0 or random.random() < np.exp(-delta / T):
                current_state = new_state
                current_energy = new_energy
                
                if current_energy < best_energy:
                    best_state = current_state.copy()
                    best_energy = current_energy
            
            # Cool down
            T = T0 * (Tf / T0) ** (i / iterations)
        
        return best_state.tolist(), best_energy

    def _calculate_qubo_energy(self, matrix: np.ndarray, state: np.ndarray) -> float:
        """Calculate QUBO energy: E = sum(Q_ij * x_i * x_j)
        
        Args:
            matrix: QUBO matrix (upper triangular)
            state: Binary state vector (0 or 1)
            
        Returns:
            Energy value
        """
        # For upper triangular matrix: E = sum(Q_ij * x_i * x_j)
        n = len(state)
        energy = 0.0
        for i in range(n):
            for j in range(i, n):
                energy += matrix[i, j] * state[i] * state[j]
        return float(energy)

    def _calculate_ising_energy(self, matrix: np.ndarray, state: np.ndarray) -> float:
        """Calculate ISING energy: E = sum(J_ij * s_i * s_j)
        
        Args:
            matrix: ISING interaction matrix (upper triangular)
            state: Spin state vector (-1 or 1)
            
        Returns:
            Energy value
        """
        # For upper triangular matrix: E = sum(J_ij * s_i * s_j)
        n = len(state)
        energy = 0.0
        for i in range(n):
            for j in range(i, n):
                energy += matrix[i, j] * state[i] * state[j]
        return float(energy)

    def get_task(self, task_id: str) -> dict:
        """Get task status from local solver.
        
        Local solver runs synchronously, so task is always complete.

        Args:
            task_id: Task ID

        Returns:
            Task information
        """
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "Local solver runs synchronously",
        }


class LocalOepoSolver(BaseSolver):
    """Local OEPO solver.
    
    This solver submits tasks to a local OEPO solver service
    (quantum annealing hardware or simulator).
    """

    SUPPORTED_TASK_TYPES = [GeneralTask, MinimalIsingEnergyTask, QuboTask]

    def __init__(
        self,
        host: str = None,
        api_path: str = None,
        computer_type: int = None,
        gear: int = None,
    ):
        """Initialize local OEPO solver.

        Args:
            host: Local solver host URL.
                  If not provided, will use default local host.
            api_path: API path for the solver.
                     If not provided, will use default path.
            computer_type: Computer type (machine ID).
            gear: Gear mode (0=fast, 1=balanced, 2=precise).
        """
        if host is None:
            host = DEFAULT_LOCAL_HOST

        if api_path is None:
            api_path = DEFAULT_LOCAL_API_PATH

        super().__init__(api_key=None, host=host, computer_type=computer_type, gear=gear)
        self._api_path = api_path
        self._url = host + api_path

        import requests
        self._session = requests.Session()

    def solve(self, task_data: dict) -> dict:
        """Submit task to local OEPO solver.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary in unified format
        """
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        if task_type == "general":
            return self._create_general_task(task_data)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

    def _create_general_task(self, task_data: dict) -> dict:
        """Submit general task to local OEPO solver.
        
        Args:
            task_data: Task data dictionary
            
        Returns:
            Result dictionary
        """
        csv_string = task_data.get("csv_string")
        if csv_string is None:
            raise ClientError("csv_string is required for local solver")

        # Build params
        params = {}
        if self._computer_type is not None:
            params["computer"] = str(self._computer_type)
        params["gear"] = self._gear if self._gear else GEAR_PRECISE

        # Handle question_type
        question_type = task_data.get("params", {}).get("type")
        if question_type is not None:
            if question_type == QUBO_PROBLEM:
                params["type"] = "binary"
            elif question_type == ISING_PROBLEM:
                params["type"] = "spin"

        # Submit
        files = {"data": csv_string}
        try:
            response = self._session.post(self._url, files=files, params=params)
            response.raise_for_status()
            raw_result = response.json()
        except Exception as e:
            raise ClientError(f"Local OEPO solver request failed: {e}")

        task_id = raw_result.get("job_name")
        result = Result.from_local(raw_result, task_id)

        return {
            "result": result.to_dict(),
            "task_id": task_id,
            "status": 1,
        }

    def get_task(self, task_id: str) -> dict:
        """Get task status."""
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Local OEPO solver does not support task retrieval",
        }


# Backward compatibility
LocalClient = LocalSolver
