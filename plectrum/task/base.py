"""Base task class for Plectrum SDK."""

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from plectrum.solver.base import BaseSolver
    from plectrum.client.base import BaseClient
    from plectrum.result import Result


class BaseTask(ABC):
    """Abstract base class for tasks.

    This class defines the interface that all task types
    must implement.
    """

    def __init__(self, name: str = None):
        """Initialize base task.

        Args:
            name: Task name
        """
        self._name = name
        self._task_id = None

    @property
    def name(self) -> str:
        """Get task name."""
        return self._name

    @property
    def task_id(self) -> str:
        """Get task ID."""
        return self._task_id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.

        Returns:
            Task data as dictionary
        """
        pass

    def solve(self, solver: Union["BaseSolver", "BaseClient"]) -> "Result":
        """Submit task to solver for solving.

        Args:
            solver: Solver instance (CloudSolver, LocalOepoSolver,
                    LocalSolver, or legacy BaseClient)

        Returns:
            Result object with solution details
        """
        from plectrum.solver.base import BaseSolver
        from plectrum.result import Result

        task_data = self.to_dict()
        start_time = time.time()

        result = solver.solve(task_data)

        if isinstance(result, Result):
            # New solver API — result is already a Result
            if result._e2e_time is None:
                result._e2e_time = time.time() - start_time
            if result._task_name is None and self._name:
                result._task_name = self._name
            if result.task_id:
                self._task_id = result.task_id
            return result
        else:
            # Legacy client API — result is a dict, wrap it
            e2e_time = time.time() - start_time
            if "task_id" in result:
                self._task_id = result["task_id"]
            elif "data" in result and "taskId" in result.get("data", {}):
                self._task_id = result["data"]["taskId"]

            result_data = result.get("result", {})
            if isinstance(result_data, dict):
                return Result(
                    energy=result_data.get("energy"),
                    spin_config=result_data.get("spin_config"),
                    oepo_time=result_data.get("oepo_time") or result_data.get("time"),
                    e2e_time=e2e_time,
                    task_id=self._task_id,
                    task_name=self._name,
                    ok=result_data.get("ok", True),
                    msg=result_data.get("msg"),
                    timestamp=result_data.get("timestamp"),
                )
            return Result(
                e2e_time=e2e_time,
                task_id=self._task_id,
                task_name=self._name,
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name})"
