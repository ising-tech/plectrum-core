"""Local solver for Plectrum SDK."""

import time
import random
import uuid
import numpy as np
import requests

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
from plectrum.exceptions import (
    ClientError,
    TimeoutError,
    ConnectionError,
)
from plectrum.result import Result
from plectrum.task import GeneralTask, MinimalIsingEnergyTask, QuboTask


# ---------------------------------------------------------------------------
# LocalSolver — runs SA locally, no network
# ---------------------------------------------------------------------------

class LocalSolver(BaseSolver):
    """Local solver using classical algorithms.

    This solver runs optimization algorithms locally:
    - Simulated Annealing (SA)
    """

    SUPPORTED_TASK_TYPES = [GeneralTask, MinimalIsingEnergyTask, QuboTask]

    def __init__(self, gear: int = GEAR_PRECISE, algorithm: str = "sa"):
        """Initialize local solver.

        Args:
            gear: Gear mode (0=fast, 1=balanced, 2=precise).
            algorithm: Algorithm to use ("sa" for Simulated Annealing).
        """
        super().__init__(api_key=None, host=None, computer_type=None, gear=gear)
        self._algorithm = algorithm
        self._iteration_config = {
            GEAR_FAST: 1000,
            GEAR_BALANCED: 5000,
            GEAR_PRECISE: 10000,
        }

    # -- public API --

    def solve(self, task_data: dict) -> dict:
        """Solve task using local algorithm."""
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        if task_type == "general":
            return self._solve_general_task(task_data)
        raise ClientError(f"Unknown task type: {task_type}")

    def get_task(self, task_id: str) -> dict:
        """Local solver runs synchronously — task is always complete."""
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "Local solver runs synchronously",
        }

    # -- internal: general task --

    def _solve_general_task(self, task_data: dict) -> dict:
        csv_string = task_data.get("csv_string")
        if not csv_string:
            raise ClientError("csv_string is required for local solver")

        matrix = self._parse_csv_string(csv_string)
        question_type = task_data.get("params", {}).get("type", QUBO_PROBLEM)
        iterations = self._iteration_config.get(self._gear, 5000)

        start_time = time.time()
        if question_type == ISING_PROBLEM:
            best_state, best_energy = self._simulated_annealing_ising(matrix, iterations)
        else:
            best_state, best_energy = self._simulated_annealing_qubo(matrix, iterations)
        elapsed_time = time.time() - start_time

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

    # -- CSV parsing --

    @staticmethod
    def _parse_csv_string(csv_string: str) -> np.ndarray:
        """Parse CSV string to numpy array.

        Raises:
            ClientError: On malformed CSV data.
        """
        try:
            lines = csv_string.strip().split('\n')
            data = []
            for line in lines:
                row = [float(x) for x in line.split(',')]
                data.append(row)
            return np.array(data)
        except (ValueError, TypeError) as e:
            raise ClientError(f"Failed to parse CSV data: {e}") from e

    # -- Simulated Annealing: QUBO --

    def _simulated_annealing_qubo(self, matrix: np.ndarray, iterations: int) -> tuple:
        """Simulated Annealing for QUBO problem (binary 0/1)."""
        n = matrix.shape[0]
        current_state = np.random.randint(0, 2, n)
        current_energy = self._calculate_qubo_energy(matrix, current_state)
        best_state, best_energy = current_state.copy(), current_energy

        T0, Tf = 100.0, 0.01
        for i in range(iterations):
            T = T0 * (Tf / T0) ** (i / iterations)
            new_state = current_state.copy()
            new_state[random.randint(0, n - 1)] ^= 1
            new_energy = self._calculate_qubo_energy(matrix, new_state)
            delta = new_energy - current_energy

            if delta < 0 or random.random() < np.exp(-delta / T):
                current_state, current_energy = new_state, new_energy
                if current_energy < best_energy:
                    best_state, best_energy = current_state.copy(), current_energy

        return best_state.tolist(), best_energy

    # -- Simulated Annealing: ISING --

    def _simulated_annealing_ising(self, matrix: np.ndarray, iterations: int) -> tuple:
        """Simulated Annealing for ISING problem (spin -1/+1)."""
        n = matrix.shape[0]
        current_state = np.random.choice([-1, 1], n)
        current_energy = self._calculate_ising_energy(matrix, current_state)
        best_state, best_energy = current_state.copy(), current_energy

        T0, Tf = 100.0, 0.01
        for i in range(iterations):
            T = T0 * (Tf / T0) ** (i / iterations)
            flip_idx = random.randint(0, n - 1)
            new_state = current_state.copy()
            new_state[flip_idx] = -new_state[flip_idx]
            new_energy = self._calculate_ising_energy(matrix, new_state)
            delta = new_energy - current_energy

            if delta < 0 or random.random() < np.exp(-delta / T):
                current_state, current_energy = new_state, new_energy
                if current_energy < best_energy:
                    best_state, best_energy = current_state.copy(), current_energy

        return best_state.tolist(), best_energy

    # -- energy calculations --

    @staticmethod
    def _calculate_qubo_energy(matrix: np.ndarray, state: np.ndarray) -> float:
        """E = x^T Q x  (upper-triangular Q)."""
        return float(state @ matrix @ state)

    @staticmethod
    def _calculate_ising_energy(matrix: np.ndarray, state: np.ndarray) -> float:
        """E = s^T J s  (upper-triangular J)."""
        return float(state @ matrix @ state)


# ---------------------------------------------------------------------------
# LocalOepoSolver — HTTP to a local OEPO device / simulator
# ---------------------------------------------------------------------------

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
            api_path: API path for the solver.
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
        self._session = requests.Session()

    # -- public API --

    def solve(self, task_data: dict) -> dict:
        """Submit task to local OEPO solver."""
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        if task_type == "general":
            return self._create_general_task(task_data)
        raise ClientError(f"Unknown task type: {task_type}")

    def get_task(self, task_id: str) -> dict:
        """Get task status (not supported by OEPO)."""
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Local OEPO solver does not support task retrieval",
        }

    # -- internal --

    def _create_general_task(self, task_data: dict) -> dict:
        """Submit general task to local OEPO solver.

        Raises:
            ClientError: On missing data, HTTP failure, or server error.
            TimeoutError: On request timeout.
            ConnectionError: On network failure.
        """
        csv_string = task_data.get("csv_string")
        if not csv_string:
            raise ClientError("csv_string is required for local solver")

        params = self._build_params(task_data)
        raw_result = self._post_job(csv_string, params)

        # Server may return {"error": "..."} with status 500
        if "error" in raw_result:
            raise ClientError(f"Local OEPO solver error: {raw_result['error']}")

        task_id = raw_result.get("job_name")
        result = Result.from_local(raw_result, task_id)
        return {
            "result": result.to_dict(),
            "task_id": task_id,
            "status": 1,
        }

    def _build_params(self, task_data: dict) -> dict:
        """Build query params for the OEPO API."""
        params = {}
        if self._computer_type is not None:
            params["computer"] = str(self._computer_type)
        params["gear"] = self._gear if self._gear else GEAR_PRECISE

        question_type = task_data.get("params", {}).get("type")
        if question_type == QUBO_PROBLEM:
            params["type"] = "binary"
        elif question_type == ISING_PROBLEM:
            params["type"] = "spin"
        return params

    def _post_job(self, csv_string: str, params: dict) -> dict:
        """POST to the OEPO job endpoint.

        Raises:
            TimeoutError, ConnectionError, ClientError
        """
        try:
            response = self._session.post(
                self._url, files={"data": csv_string}, params=params,
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Local OEPO request timed out: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self._url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ClientError(f"Local OEPO solver request failed: {e}") from e

        try:
            return response.json()
        except ValueError as e:
            raise ClientError(
                f"Non-JSON response from local OEPO "
                f"(status {response.status_code}): {response.text[:200]}"
            ) from e


# Backward compatibility
LocalClient = LocalSolver
