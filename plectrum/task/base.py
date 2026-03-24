"""Base task class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from plectrum.client.base import BaseSolver


class BaseTask(ABC):
    """Abstract base class for tasks.

    This class defines the interface that all task types
    must implement.
    """

    # Task type identifier - subclasses should override
    TASK_TYPE: Optional[str] = None

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

    @property
    def task_type(self) -> Optional[str]:
        """Get task type identifier."""
        return self.TASK_TYPE

    def solve(self, solver: "BaseSolver") -> Dict[str, Any]:
        """Submit task to solver for solving.

        Args:
            solver: Solver client (CloudSolver, LocalSolver, etc.)

        Returns:
            Result dictionary from solver
        """
        # Validate solver supports this task type
        if hasattr(solver, 'SUPPORTED_TASK_TYPES'):
            # Check if task class is in supported list
            task_classes = solver.SUPPORTED_TASK_TYPES
            task_type = self.TASK_TYPE
            
            # Check by class or by TASK_TYPE string
            is_supported = False
            for t in task_classes:
                if t is type(self) or (hasattr(t, 'TASK_TYPE') and t.TASK_TYPE == task_type):
                    is_supported = True
                    break
            
            if not is_supported:
                from plectrum.exceptions import ClientError
                supported_types = [t.TASK_TYPE if hasattr(t, 'TASK_TYPE') else str(t) for t in task_classes]
                raise ClientError(
                    f"Task type '{task_type}' is not supported by {solver.__class__.__name__}. "
                    f"Supported types: {supported_types}"
                )
        
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
