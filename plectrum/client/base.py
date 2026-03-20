"""Base client class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from plectrum.result import Result


class BaseClient(ABC):
    """Abstract base class for solver clients.

    This class defines the interface that all solver clients
    (cloud, local, etc.) must implement.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
    ):
        """Initialize base client.

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

    @abstractmethod
    def solve(self, task_data: Dict[str, Any]) -> "Result":
        """Submit a task for solving.

        Args:
            task_data: Task data dictionary

        Returns:
            Result object from the solver
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
