"""Local client for Plectrum SDK."""

import configparser
import requests

from plectrum.client.base import BaseClient
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


class LocalClient(BaseClient):
    """Local solver client.

    This client submits tasks to a local solver service.
    """

    def __init__(
        self,
        host: str = None,
        api_path: str = None,
    ):
        """Initialize local client.

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

    @classmethod
    def from_config(
        cls,
        config_path: str = "config/cloud.ini",
        **kwargs,
    ) -> "LocalClient":
        """Create LocalClient from a config file.

        Args:
            config_path: Path to the INI config file.
                         Expected sections and keys::

                             [LOCAL]
                             HOST: http://192.168.137.100:5001

            **kwargs: Additional keyword arguments passed to the constructor
                      (e.g. api_path).

        Returns:
            LocalClient instance configured from the file.
        """
        config = configparser.ConfigParser()
        config.read(config_path)
        host = config.get("LOCAL", "HOST", fallback=None)
        if host is not None:
            host = host.strip() or None
        return cls(host=host, **kwargs)

    @property
    def api_path(self) -> str:
        """Get API path."""
        return self._api_path

    def solve(self, task_data: dict) -> Result:
        """Submit task to local solver.

        Args:
            task_data: Task data dictionary

        Returns:
            Result object from the local solver
        """
        # Get matrix data from task_data
        csv_string = task_data.get("csv_string")

        if csv_string is None:
            raise ClientError("csv_string is required for local solver")

        # Build params for local solver
        # Use string values as per original implementation
        params = {}
        computer_type_id = task_data.get("params", {}).get("gear")
        question_type = task_data.get("params", {}).get("type")

        if computer_type_id is not None:
            params["gear"] = 2
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

            # Convert to unified Result format using Result class
            # Local solver returns: {job_name: "...", result: {...}}
            task_id = raw_result.get("job_name")

            return Result.from_local(raw_result, task_id)
        except requests.exceptions.RequestException as e:
            raise ClientError(f"Local solver request failed: {e}")

    def get_task(self, task_id: str) -> dict:
        """Get task status from local solver.

        For local solver, this might not be supported.

        Args:
            task_id: Task ID

        Returns:
            Task information
        """
        # Local solver might not support task retrieval
        # Return a placeholder response
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Local solver does not support task retrieval",
        }
