"""Base task class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from plectrum.client.base import BaseClient


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

    def solve(self, solver: "BaseClient") -> Dict[str, Any]:
        """Submit task to solver for solving.

        Args:
            solver: Solver client (CloudClient, LocalClient, etc.)

        Returns:
            Result dictionary from solver
        """
        task_data = self.to_dict()
        result = solver.solve(task_data)

        # Store task_id if available
        if "task_id" in result:
            self._task_id = result["task_id"]
        elif "data" in result and "taskId" in result["data"]:
            self._task_id = result["data"]["taskId"]

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name})"
