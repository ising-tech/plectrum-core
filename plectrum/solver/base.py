"""Base solver class for Plectrum SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from plectrum.result import Result


class BaseSolver(ABC):
    """Abstract base class for all solvers.

    All solver implementations (cloud, local OEPO, local SA, etc.)
    must inherit from this class and implement the solve() method.
    """

    def __init__(self, gear: Optional[int] = None):
        """Initialize base solver.

        Args:
            gear: Computation gear/level setting. Higher values may yield
                  better results but take longer.
        """
        self._gear = gear

    @property
    def gear(self) -> Optional[int]:
        """Get gear setting."""
        return self._gear

    @abstractmethod
    def solve(self, task_data: Dict[str, Any]) -> "Result":
        """Solve a task and return a Result.

        Args:
            task_data: Task data dictionary from task.to_dict()

        Returns:
            Result object with solution details
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(gear={self._gear})"

