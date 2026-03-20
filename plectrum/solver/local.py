"""Local solver using classical optimization algorithms (simulated annealing).

This solver runs entirely locally using numpy — no network connection required.
"""

import csv
import io
import time
import numpy as np
from typing import Dict, Any, Optional

from plectrum.solver.base import BaseSolver
from plectrum.const import QUBO_PROBLEM, ISING_PROBLEM
from plectrum.result import Result


class LocalSolver(BaseSolver):
    """Local solver using simulated annealing.

    Solves QUBO / Ising problems locally using a simulated annealing
    algorithm. No network connection or external hardware is required.

    Example:
        solver = LocalSolver(num_reads=50, max_iter=2000)
        result = task.solve(solver=solver)
    """

    def __init__(
        self,
        num_reads: int = 20,
        max_iter: int = 1000,
        initial_temp: float = 10.0,
        cooling_rate: float = 0.995,
        seed: Optional[int] = None,
    ):
        """Initialize local solver.

        Args:
            num_reads: Number of independent SA runs (default: 20).
            max_iter: Maximum iterations per run (default: 1000).
            initial_temp: Initial temperature for SA (default: 10.0).
            cooling_rate: Temperature cooling rate per step (default: 0.995).
            seed: Random seed for reproducibility (default: None).
        """
        super().__init__(gear=None)
        self._num_reads = num_reads
        self._max_iter = max_iter
        self._initial_temp = initial_temp
        self._cooling_rate = cooling_rate
        self._seed = seed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def solve(self, task_data: Dict[str, Any]) -> Result:
        """Solve the task using simulated annealing.

        Args:
            task_data: Task data dictionary (from task.to_dict())

        Returns:
            Result object with best solution found
        """
        start_time = time.time()

        # Parse matrix from csv_string
        csv_string = task_data.get("csv_string")
        if csv_string is None:
            raise ValueError("csv_string is required for LocalSolver")

        matrix = self._parse_csv(csv_string)

        # Determine problem type
        question_type = task_data.get("params", {}).get("type")
        if question_type == ISING_PROBLEM:
            best_energy, best_config = self._solve_ising(matrix)
        else:
            # Default to QUBO
            best_energy, best_config = self._solve_qubo(matrix)

        calc_time = time.time() - start_time

        task_name = task_data.get("payload", {}).get("name")
        return Result(
            energy=float(best_energy),
            spin_config=best_config.tolist(),
            oepo_time=calc_time,
            e2e_time=calc_time,
            task_name=task_name,
            ok=True,
            msg="success (simulated annealing)",
        )

    # ------------------------------------------------------------------
    # QUBO solver: x ∈ {0, 1}^n,  E(x) = x^T Q x
    # ------------------------------------------------------------------

    def _solve_qubo(self, Q: np.ndarray):
        """Solve QUBO problem via simulated annealing.

        Args:
            Q: QUBO matrix (n x n)

        Returns:
            (best_energy, best_config) tuple
        """
        rng = np.random.default_rng(self._seed)
        n = Q.shape[0]

        # Precompute symmetric interaction: h_ij = Q_ij + Q_ji
        Q_sym = Q + Q.T  # off-diagonal interactions doubled, diag doubled
        diag = np.diag(Q).copy()  # original diagonal

        best_energy = float("inf")
        best_config = None

        for _ in range(self._num_reads):
            x = rng.integers(0, 2, size=n)
            energy = float(x @ Q @ x)
            T = self._initial_temp

            for _ in range(self._max_iter):
                k = rng.integers(n)

                # Efficient delta energy for flipping x_k
                # ΔE = (1 - 2*x_k) * (diag_k + Σ_{j≠k} (Q_kj + Q_jk) * x_j)
                delta = Q_sym[k] @ x - Q_sym[k, k] * x[k] + diag[k]
                dE = (1 - 2 * x[k]) * delta

                if dE < 0 or rng.random() < np.exp(-dE / max(T, 1e-10)):
                    x[k] = 1 - x[k]
                    energy += dE

                if energy < best_energy:
                    best_energy = energy
                    best_config = x.copy()

                T *= self._cooling_rate

        return best_energy, best_config

    # ------------------------------------------------------------------
    # Ising solver: s ∈ {-1, +1}^n,  E(s) = s^T J s
    # ------------------------------------------------------------------

    def _solve_ising(self, J: np.ndarray):
        """Solve Ising problem via simulated annealing.

        Args:
            J: Ising coupling matrix (n x n)

        Returns:
            (best_energy, best_config) tuple
        """
        rng = np.random.default_rng(self._seed)
        n = J.shape[0]

        # Precompute symmetric interaction
        J_sym = J + J.T

        best_energy = float("inf")
        best_config = None

        for _ in range(self._num_reads):
            s = rng.choice([-1, 1], size=n)
            energy = float(s @ J @ s)
            T = self._initial_temp

            for _ in range(self._max_iter):
                k = rng.integers(n)

                # Flipping s_k → -s_k
                # ΔE = -2 * s_k * (Σ_j J_sym[k,j] * s_j - J_sym[k,k] * s_k)
                #     + J[k,k] * ((-s_k)^2 - s_k^2) = 0 since s_k^2 = 1
                # Simplified:  ΔE = -2 * s_k * (J_sym[k] @ s - J_sym[k,k] * s_k)
                field = J_sym[k] @ s - J_sym[k, k] * s[k]
                dE = -2 * s[k] * field

                if dE < 0 or rng.random() < np.exp(-dE / max(T, 1e-10)):
                    s[k] = -s[k]
                    energy += dE

                if energy < best_energy:
                    best_energy = energy
                    best_config = s.copy()

                T *= self._cooling_rate

        return best_energy, best_config

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_csv(csv_string: str) -> np.ndarray:
        """Parse CSV string into numpy array."""
        reader = csv.reader(io.StringIO(csv_string))
        return np.array(list(reader), dtype=np.float64)

    def __repr__(self) -> str:
        return (
            f"LocalSolver(num_reads={self._num_reads}, "
            f"max_iter={self._max_iter}, "
            f"initial_temp={self._initial_temp}, "
            f"cooling_rate={self._cooling_rate})"
        )

