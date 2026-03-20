"""Base client class for Plectrum SDK."""

from abc import abstractmethod
from typing import Any, Dict

from plectrum.solver.base import BaseSolver


class BaseClient(BaseSolver):
    """Abstract base class for solver clients.

    This class defines the interface that all solver clients
    (cloud, local, etc.) must implement.
    """

    @abstractmethod
    def solve(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a task for solving.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary from the solver
        """
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status or result.

        Args:
            task_id: Task ID

        Returns:
            Task information dictionary
        """
        raise NotImplementedError
