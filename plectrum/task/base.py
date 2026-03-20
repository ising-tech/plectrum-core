"""Base task class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

from plectrum.result import Result

if TYPE_CHECKING:
    from plectrum.solver.base import BaseSolver


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

    def solve(self, solver: "BaseSolver") -> Result:
        """Submit task to solver for solving.

        Args:
            solver: Solver instance (cloud, local service or local algorithm)

        Returns:
            Normalized Result object
        """
        task_data = self.to_dict()
        raw_result = solver.solve(task_data)
        result = Result.from_solver_response(raw_result, task_name=self._name)

        if result.task_id:
            self._task_id = result.task_id

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._name})"
