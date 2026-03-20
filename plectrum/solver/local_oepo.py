"""Local OEPO hardware solver for Plectrum SDK."""

import time
import requests
from typing import Dict, Any

from plectrum.solver.base import BaseSolver
from plectrum.const import (
    DEFAULT_LOCAL_HOST,
    DEFAULT_LOCAL_API_PATH,
    QUBO_PROBLEM,
    ISING_PROBLEM,
    LOCAL_TYPE_QUBO,
    LOCAL_TYPE_ISING,
)
from plectrum.exceptions import ClientError
from plectrum.result import Result


class LocalOepoSolver(BaseSolver):
    """Local OEPO hardware solver.

    Submits tasks to a local OEPO solver service via HTTP.

    Example:
        solver = LocalOepoSolver(host="http://192.168.137.100:5001", gear=1)
        result = task.solve(solver=solver)
    """

    def __init__(
        self,
        host: str = None,
        api_path: str = None,
        gear: int = None,
    ):
        """Initialize local OEPO solver.

        Args:
            host: Local solver host URL. Defaults to http://192.168.137.100:5001.
            api_path: API path for the solver. Defaults to /api/v1/job/.
            gear: Computation gear level. Controls computation intensity.
        """
        super().__init__(gear=gear)

        if host is None:
            host = DEFAULT_LOCAL_HOST
        if api_path is None:
            api_path = DEFAULT_LOCAL_API_PATH

        self._host = host
        self._api_path = api_path
        self._url = host + api_path
        self._session = requests.Session()

    @property
    def host(self) -> str:
        """Get host URL."""
        return self._host

    @property
    def api_path(self) -> str:
        """Get API path."""
        return self._api_path

    def solve(self, task_data: Dict[str, Any]) -> Result:
        """Submit task to local OEPO solver.

        Args:
            task_data: Task data dictionary

        Returns:
            Result object

        Raises:
            ClientError: If csv_string missing or request fails
        """
        start_time = time.time()

        csv_string = task_data.get("csv_string")
        if csv_string is None:
            raise ClientError("csv_string is required for local OEPO solver")

        # Build request params
        params = {}
        task_params = task_data.get("params", {})

        # Gear: use task's gear if set, otherwise solver's gear
        gear = task_params.get("gear")
        if gear is None:
            gear = self._gear
        if gear is not None:
            params["gear"] = gear

        # Question type: convert to local solver string format
        question_type = task_params.get("type")
        if question_type is not None:
            if isinstance(question_type, int):
                if question_type == QUBO_PROBLEM:
                    params["type"] = LOCAL_TYPE_QUBO
                elif question_type == ISING_PROBLEM:
                    params["type"] = LOCAL_TYPE_ISING
                else:
                    params["type"] = str(question_type)
            else:
                params["type"] = str(question_type)

        files = {"data": csv_string}

        try:
            response = self._session.post(self._url, files=files, params=params)
            response.raise_for_status()
            raw_result = response.json()

            # Parse result: local returns {job_name: "...", result: {...}}
            task_id = raw_result.get("job_name")
            result = Result.from_local(raw_result, task_id)
            result._e2e_time = time.time() - start_time
            return result

        except requests.exceptions.RequestException as e:
            raise ClientError(f"Local OEPO solver request failed: {e}")

    def __repr__(self) -> str:
        return f"LocalOepoSolver(host={self._host}, gear={self._gear})"


