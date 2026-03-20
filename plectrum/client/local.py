"""Local solver for Plectrum SDK."""

import requests

from plectrum.client.base import BaseSolver
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


class LocalSolver(BaseSolver):
    """Local solver.

    This solver submits tasks to a local solver service.
    """

    def __init__(
        self,
        host: str = None,
        api_path: str = None,
    ):
        """Initialize local solver.

        Args:
            host: Local solver host URL.
                  If not provided, will use default local host.
            api_path: API path for the solver.
                     If not provided, will use default path.
        """
        if host is None:
            host = DEFAULT_LOCAL_HOST

        if api_path is None:
            api_path = DEFAULT_LOCAL_API_PATH

        super().__init__(api_key=None, host=host)
        self._api_path = api_path
        self._url = host + api_path
        self._session = requests.Session()

    @property
    def api_path(self) -> str:
        """Get API path."""
        return self._api_path

    def solve(self, task_data: dict) -> dict:
        """Submit task to local solver."""
        csv_string = task_data.get("csv_string")

        if csv_string is None:
            raise ClientError("csv_string is required for local solver")

        # Build params for local solver
        params = {}
        computer_type_id = task_data.get("params", {}).get("gear")
        question_type = task_data.get("params", {}).get("type")

        if computer_type_id is not None:
            params["gear"] = str(computer_type_id)
        if question_type is not None:
            # Convert question_type to local solver string
            # Cloud: 1=QUBO (binary), 2=ISING (spin)
            if isinstance(question_type, int):
                if question_type == QUBO_PROBLEM:
                    params["type"] = LOCAL_TYPE_QUBO
                elif question_type == ISING_PROBLEM:
                    params["type"] = LOCAL_TYPE_ISING
                else:
                    params["type"] = str(question_type)
            else:
                params["type"] = str(question_type)

        # Prepare files and params
        files = {"data": csv_string}

        try:
            response = self._session.post(
                self._url,
                files=files,
                params=params,
            )
            response.raise_for_status()
            raw_result = response.json()

            # Convert to unified format using Result class
            task_id = raw_result.get("job_name")

            # Create unified Result
            result = Result.from_local(raw_result, task_id)

            return {
                "result": result.to_dict(),
                "task_id": task_id,
                "status": 1,  # Completed status
            }
        except requests.exceptions.RequestException as e:
            raise ClientError(f"Local solver request failed: {e}")

    def get_task(self, task_id: str) -> dict:
        """Get task status from local solver."""
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Local solver does not support task retrieval",
        }


class LocalOepoSolver(LocalSolver):
    """Local OEPO solver (alias for LocalSolver)."""
    pass


# Backward compatibility
LocalClient = LocalSolver
