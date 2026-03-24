"""Base solver class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from plectrum.exceptions import ClientError
from plectrum.task.base import BaseTask


class BaseSolver(ABC):
    """Abstract base class for solvers.

    This class defines the interface that all solvers
    (cloud, local, etc.) must implement.
    """

    # Supported task types - subclasses should override with task classes
    SUPPORTED_TASK_TYPES: List[Type[BaseTask]] = []

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        computer_type: Optional[int] = None,
        gear: Optional[int] = None,
    ):
        """Initialize base solver.

        Args:
            api_key: API key for authentication
            host: Base URL for the solver service
            computer_type: Computer type (machine ID, e.g., OEPO_ISING_1601=1601)
            gear: Gear mode (0=fast, 1=balanced, 2=precise)
        """
        self._api_key = api_key
        self._host = host
        self._computer_type = computer_type
        self._gear = gear

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        return self._api_key

    @property
    def host(self) -> Optional[str]:
        """Get host URL."""
        return self._host

    @property
    def computer_type(self) -> Optional[int]:
        """Get computer type (machine ID)."""
        return self._computer_type

    @property
    def gear(self) -> Optional[int]:
        """Get computer type ID (gear mode)."""
        return self._gear

    def _validate_task_type(self, task_type: str) -> None:
        """Validate if task type is supported by this solver.

        Args:
            task_type: Task type to validate (can be string or task class)

        Raises:
            ClientError: If task type is not supported
        """
        # Convert task class to string if needed
        supported_types = []
        for t in self.SUPPORTED_TASK_TYPES:
            if isinstance(t, type) and issubclass(t, BaseTask):
                supported_types.append(t.TASK_TYPE)
            else:
                supported_types.append(str(t))
        
        # Also check string task_type against supported list
        if task_type not in supported_types:
            raise ClientError(
                f"Task type '{task_type}' is not supported by {self.__class__.__name__}. "
                f"Supported types: {supported_types}"
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
