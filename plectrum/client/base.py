"""Base solver class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from plectrum.exceptions import ClientError


class BaseSolver(ABC):
    """Abstract base class for solvers.

    This class defines the interface that all solvers
    (cloud, local, etc.) must implement.
    """

    # Supported task types - subclasses should override
    SUPPORTED_TASK_TYPES: List[str] = []

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
    ):
        """Initialize base solver.

        Args:
            api_key: API key for authentication
            host: Base URL for the solver service
        """
        self._api_key = api_key
        self._host = host

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        return self._api_key

    @property
    def host(self) -> Optional[str]:
        """Get host URL."""
        return self._host

    def _validate_task_type(self, task_type: str) -> None:
        """Validate if task type is supported by this solver.

        Args:
            task_type: Task type to validate

        Raises:
            ClientError: If task type is not supported
        """
        if task_type not in self.SUPPORTED_TASK_TYPES:
            raise ClientError(
                f"Task type '{task_type}' is not supported by {self.__class__.__name__}. "
                f"Supported types: {self.SUPPORTED_TASK_TYPES}"
            )

    @abstractmethod
    def solve(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a task for solving.

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary from the solver
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status or result.

        Args:
            task_id: Task ID

        Returns:
            Task information dictionary
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self._host})"


# Backward compatibility
BaseClient = BaseSolver
