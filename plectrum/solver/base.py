"""Base solver abstractions for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseSolver(ABC):
    """Abstract base class for all solvers.

    Solvers can be pure local algorithms or remote service clients,
    but they all expose the same task solving interface.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
    ):
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
    def solve(self, task_data: Dict[str, Any]):
        """Solve a task and return a raw or normalized result."""

    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status or result if supported."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self._host})"

