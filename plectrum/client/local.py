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
    GEAR_PRECISE
)
from plectrum.exceptions import ClientError
from plectrum.result import Result

from plectrum.task import GeneralTask, MinimalIsingEnergyTask, QuboTask


class LocalSolver(BaseSolver):
    """Local solver.

    This solver submits tasks to a local solver service.
    """

    SUPPORTED_TASK_TYPES = [GeneralTask, MinimalIsingEnergyTask, QuboTask]

    def __init__(
        self,
        host: str = None,
        api_path: str = None,
        computer_type: int = None,
        gear: int = None,
    ):
        """Initialize local solver.

        Args:
            host: Local solver host URL.
                  If not provided, will use default local host.
            api_path: API path for the solver.
                     If not provided, will use default path.
            computer_type: Computer type (machine ID, e.g., OEPO_ISING_1601=1601).
            gear: Gear mode (0=fast, 1=balanced, 2=precise).
                            If not provided, will use default (1=balanced).
        """
        if host is None:
            host = DEFAULT_LOCAL_HOST

        if api_path is None:
            api_path = DEFAULT_LOCAL_API_PATH

        super().__init__(api_key=None, host=host, computer_type=computer_type, gear=gear)
        self._api_path = api_path
        self._url = host + api_path
        self._gear = gear
        self._session = requests.Session()

    @property
    def api_path(self) -> str:
        """Get API path."""
        return self._api_path

    def solve(self, task_data: dict) -> dict:
        """Submit task to local solver.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary in unified format:
            {
                "result": {...},
                "task_id": "xxx",
                "status": 1
            }
        """
        # Validate task type
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        # Route to appropriate handler
        if task_type == "general":
            return self._create_general_task(task_data)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

    def _create_general_task(self, task_data: dict) -> dict:
        """Create and submit a general task to local solver.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary in unified format
        """
        csv_string = task_data.get("csv_string")
        if csv_string is None:
            raise ClientError("csv_string is required for local solver")

        # Build params for local solver
        params = {}
        
        # Use solver's computer_type (machine) if available
        if self._computer_type is not None:
            params["computer"] = str(self._computer_type)
        
        # Use solver's gear (gear) if available, otherwise fallback to task's
        params["gear"] = self._gear if self._gear else GEAR_PRECISE

        # Handle question_type conversion (QUBO/ISING -> binary/spin)
        question_type = task_data.get("params", {}).get("type")
        if question_type is not None:
            params["type"] = self._convert_question_type(question_type)

        # Submit to local solver
        files = {"data": csv_string}
        try:
            response = self._session.post(
                self._url,
                files=files,
                params=params,
            )
            response.raise_for_status()
            raw_result = response.json()
        except requests.exceptions.RequestException as e:
            raise ClientError(f"Local solver request failed: {e}")

        # Convert to unified format
        task_id = raw_result.get("job_name")
        result = Result.from_local(raw_result, task_id)

        return {
            "result": result.to_dict(),
            "task_id": task_id,
            "status": 1,
        }

    def _convert_question_type(self, question_type) -> str:
        """Convert question type to local solver string format.

        Args:
            question_type: Question type (int or str)

        Returns:
            Local solver type string ('binary' or 'spin')
        """
        if isinstance(question_type, int):
            if question_type == QUBO_PROBLEM:
                return LOCAL_TYPE_QUBO
            elif question_type == ISING_PROBLEM:
                return LOCAL_TYPE_ISING
        return str(question_type)

    def get_task(self, task_id: str) -> dict:
        """Get task status from local solver.

        For local solver, this is not supported.

        Args:
            task_id: Task ID

        Returns:
            Task information
        """
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
