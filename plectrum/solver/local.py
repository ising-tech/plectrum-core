"""Traditional in-process local solver implementation."""

import itertools
import time
import uuid
from typing import Any, Dict, Iterable, Tuple

import numpy as np

from plectrum.const import ISING_PROBLEM, QUBO_PROBLEM
from plectrum.exceptions import ClientError
from plectrum.matrix import Matrix
from plectrum.result import Result
from plectrum.solver.base import BaseSolver


class LocalSolver(BaseSolver):
	"""Traditional local solver.

	For small dense problems this solver uses exhaustive search to find the
	exact optimum. For larger problems it falls back to a simple deterministic
	multi-start local search so the interface remains usable without external
	services.
	"""

	def __init__(
		self,
		max_bruteforce_bits: int = 20,
		search_restarts: int = 16,
		random_seed: int = 0,
	):
		super().__init__(api_key=None, host="local://traditional")
		self._max_bruteforce_bits = max_bruteforce_bits
		self._search_restarts = search_restarts
		self._random_seed = random_seed

	def solve(self, task_data: Dict[str, Any]) -> Result:
		csv_string = task_data.get("csv_string")
		if not csv_string:
			raise ClientError("csv_string is required for LocalSolver")

		matrix = Matrix.from_csv_string(csv_string).data
		if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
			raise ClientError(
				"LocalSolver only supports dense square matrices for now"
			)

		params = task_data.get("params", {})
		payload = task_data.get("payload", {})
		question_type = params.get("type")
		if question_type is None:
			question_type = payload.get("questionType")
		if question_type is None:
			question_type = QUBO_PROBLEM

		start_time = time.perf_counter()
		best_state, best_energy = self._solve_dense_problem(matrix, question_type)
		elapsed = time.perf_counter() - start_time

		timestamp = int(time.time() * 1000)
		return Result(
			energy=best_energy,
			spin_config=best_state,
			time=elapsed,
			oepo_time=elapsed,
			e2e_time=elapsed,
			task_id=f"local-{uuid.uuid4().hex[:8]}",
			task_name=payload.get("name"),
			ok=True,
			msg="success",
			timestamp=timestamp,
			solver_name=self.__class__.__name__,
		)

	def get_task(self, task_id: str) -> Dict[str, Any]:
		return {
			"task_id": task_id,
			"status": 1,
			"message": "Traditional local solver returns results synchronously",
		}

	def _solve_dense_problem(
		self,
		matrix: np.ndarray,
		question_type: Any,
	) -> Tuple[list, float]:
		size = matrix.shape[0]
		if size <= self._max_bruteforce_bits:
			return self._solve_by_bruteforce(matrix, question_type)
		return self._solve_by_local_search(matrix, question_type)

	def _solve_by_bruteforce(
		self,
		matrix: np.ndarray,
		question_type: Any,
	) -> Tuple[list, float]:
		candidate_values = self._candidate_values(question_type)
		best_state = None
		best_energy = None

		for state in itertools.product(candidate_values, repeat=matrix.shape[0]):
			energy = self._energy(matrix, state)
			if best_energy is None or energy < best_energy:
				best_energy = energy
				best_state = list(state)

		return best_state, float(best_energy)

	def _solve_by_local_search(
		self,
		matrix: np.ndarray,
		question_type: Any,
	) -> Tuple[list, float]:
		candidate_values = self._candidate_values(question_type)
		rng = np.random.default_rng(self._random_seed)
		size = matrix.shape[0]

		best_state = None
		best_energy = None
		for _ in range(self._search_restarts):
			state = rng.choice(candidate_values, size=size).astype(int)
			improved = True
			while improved:
				improved = False
				current_energy = self._energy(matrix, state)
				for idx in range(size):
					candidate = state.copy()
					candidate[idx] = self._flipped_value(candidate[idx], question_type)
					candidate_energy = self._energy(matrix, candidate)
					if candidate_energy < current_energy:
						state = candidate
						current_energy = candidate_energy
						improved = True
			final_energy = self._energy(matrix, state)
			if best_energy is None or final_energy < best_energy:
				best_energy = final_energy
				best_state = state.astype(int).tolist()

		return best_state, float(best_energy)

	@staticmethod
	def _candidate_values(question_type: Any) -> Tuple[int, int]:
		if question_type == ISING_PROBLEM or str(question_type).lower() == "spin":
			return (-1, 1)
		return (0, 1)

	@staticmethod
	def _flipped_value(value: int, question_type: Any) -> int:
		if question_type == ISING_PROBLEM or str(question_type).lower() == "spin":
			return -int(value)
		return 0 if int(value) else 1

	@staticmethod
	def _energy(matrix: np.ndarray, state: Iterable[int]) -> float:
		vector = np.asarray(list(state), dtype=np.float64)
		return float(np.einsum("i,ij,j->", vector, matrix, vector, optimize=True))


