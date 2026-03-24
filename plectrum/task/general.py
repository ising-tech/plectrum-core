"""General task classes for Plectrum SDK."""

from typing import Any, Dict, Optional, Union

import numpy as np

from plectrum.const import OEPO_ISING_1601, GEAR_PRECISE
# Import Matrix for type checking and conversion
from plectrum.matrix import Matrix
from plectrum.task.base import BaseTask
from plectrum.const import QUBO_PROBLEM, ISING_PROBLEM


def _convert_to_matrix(data) -> Optional[Matrix]:
    """Convert various data types to Matrix.
    
    Args:
        data: Input data (np.ndarray, pd.DataFrame, Matrix, or None)
    
    Returns:
        Matrix object or None
    """
    if data is None:
        return None
    
    if isinstance(data, Matrix):
        return data
    
    if isinstance(data, np.ndarray):
        return Matrix.from_array(data)
    
    # Check for pandas DataFrame
    try:
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            return Matrix.from_array(data.values)
    except ImportError:
        pass
    
    # If already a Matrix-like object with to_csv_string method
    if hasattr(data, 'to_csv_string'):
        return data
    
    raise ValueError(
        f"data must be np.ndarray, pd.DataFrame, or Matrix, got {type(data)}"
    )


class GeneralTask(BaseTask):
    """General task for solving optimization problems.

    This task type is used for general optimization problems
    with J matrix and H vector inputs.
    """

    TASK_TYPE = "general"
    
    # Subclasses should override this
    QUESTION_TYPE: int = None

    def __init__(
        self,
        name: str = None,
        data: Union[np.ndarray, Matrix, Any] = None,
        shot_count: int = None,
        post_process: int = None,
        input_j_file: str = None,
        input_h_file: str = None,
    ):
        """Initialize general task.
        
        Args:
            name: Task name
            data: Input data (np.ndarray, pd.DataFrame, or Matrix)
            shot_count: Number of calculation iterations
            post_process: Post process flag
            input_j_file: URL to J matrix file
            input_h_file: URL to H vector file
        """
        super().__init__(name=name)
        self._matrix = _convert_to_matrix(data)
        self._question_type = self.QUESTION_TYPE
        self._shot_count = shot_count
        self._post_process = post_process
        self._input_j_file = input_j_file
        self._input_h_file = input_h_file

    @property
    def name(self) -> Optional[str]:
        """Get task name."""
        return self._name

    @property
    def matrix(self) -> Optional[Matrix]:
        """Get matrix."""
        return self._matrix

    @property
    def question_type(self) -> Optional[int]:
        """Get question type."""
        return self._question_type

    @property
    def shot_count(self) -> Optional[int]:
        """Get shot count (number of calculation iterations)."""
        return self._shot_count

    # Backward compatibility alias
    @property
    def calculate_count(self) -> Optional[int]:
        """Get calculate count (alias for shot_count)."""
        return self._shot_count

    @property
    def post_process(self) -> Optional[int]:
        """Get post process flag."""
        return self._post_process

    @property
    def input_j_file(self) -> Optional[str]:
        """Get input J file URL."""
        return self._input_j_file

    @property
    def input_h_file(self) -> Optional[str]:
        """Get input H file URL."""
        return self._input_h_file

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        # Build payload for cloud
        # Note: "caculateCount" is kept as-is for API compatibility
        payload = {
            "name": self._name,
            "inputJFile": self._input_j_file,
            "inputHFile": self._input_h_file,
            "questionType": self._question_type,
            "caculateCount": self._shot_count,
            "postProcess": self._post_process,
        }

        # Include CSV string for local solver
        csv_string = None
        if self._matrix is not None:
            csv_string = self._matrix.to_csv_string()

        return {
            "task_type": "general",
            "payload": payload,
            "csv_string": csv_string,
            "params": {
                "type": self._question_type,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneralTask":
        """Create task from dictionary."""
        payload = data.get("payload", {})
        shot_count = payload.get("shot_count") or payload.get("caculateCount")
        return cls(
            name=payload.get("name"),
            input_j_file=payload.get("inputJFile"),
            input_h_file=payload.get("inputHFile"),
            shot_count=shot_count,
            post_process=payload.get("postProcess"),
        )


class MinimalIsingEnergyTask(GeneralTask):
    """Minimal Ising Energy Task.

    Task for solving ISING problem (minimizing Ising energy).
    """
    
    QUESTION_TYPE = ISING_PROBLEM


class QuboTask(GeneralTask):
    """QUBO Task.

    Task for solving QUBO (Quadratic Unconstrained Binary Optimization) problem.
    """
    
    QUESTION_TYPE = QUBO_PROBLEM
