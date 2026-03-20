"""General task classes for Plectrum SDK."""

from typing import Any, Dict, Optional

from plectrum.task.base import BaseTask
from plectrum.matrix import Matrix
from plectrum.const import QUBO_PROBLEM, ISING_PROBLEM


class GeneralTask(BaseTask):
    """General task for solving optimization problems.

    This task type is used for general optimization problems
    with J matrix and H vector inputs.
    """

    def __init__(
        self,
        name: str = None,
        matrix: Optional[Matrix] = None,
        computer_type_id: int = None,
        question_type: int = None,
        calculate_count: int = None,
        post_process: int = None,
        input_j_file: str = None,
        input_h_file: str = None,
    ):
        """Initialize general task."""
        super().__init__(name=name)
        self._matrix = matrix
        self._computer_type_id = computer_type_id
        self._question_type = question_type
        self._calculate_count = calculate_count
        self._post_process = post_process
        self._input_j_file = input_j_file
        self._input_h_file = input_h_file

    @property
    def matrix(self) -> Optional[Matrix]:
        """Get matrix."""
        return self._matrix

    @property
    def computer_type_id(self) -> Optional[int]:
        """Get computer type ID."""
        return self._computer_type_id

    @property
    def question_type(self) -> Optional[int]:
        """Get question type."""
        return self._question_type

    @property
    def calculate_count(self) -> Optional[int]:
        """Get calculate count."""
        return self._calculate_count

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
        payload = {
            "name": self._name,
            "computerTypeId": self._computer_type_id,
            "inputJFile": self._input_j_file,
            "inputHFile": self._input_h_file,
            "questionType": self._question_type,
            "caculateCount": self._calculate_count,
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
                "gear": self._computer_type_id,
                "type": self._question_type,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneralTask":
        """Create task from dictionary."""
        payload = data.get("payload", {})
        return cls(
            name=payload.get("name"),
            computer_type_id=payload.get("computerTypeId"),
            input_j_file=payload.get("inputJFile"),
            input_h_file=payload.get("inputHFile"),
            question_type=payload.get("questionType"),
            calculate_count=payload.get("calculateCount"),
            post_process=payload.get("postProcess"),
        )


class MinimalIsingEnergyTask(GeneralTask):
    """Minimal Ising Energy Task.

    Task for solving ISING problem (minimizing Ising energy).
    """

    def __init__(
        self,
        name: str = None,
        data: Matrix = None,
        **kwargs,
    ):
        """Initialize MinimalIsingEnergyTask.

        Args:
            name: Task name
            data: Input data matrix
            **kwargs: Additional arguments for GeneralTask
        """
        super().__init__(
            name=name,
            matrix=data,
            question_type=ISING_PROBLEM,
            **kwargs,
        )


class QuboTask(GeneralTask):
    """QUBO Task.

    Task for solving QUBO (Quadratic Unconstrained Binary Optimization) problem.
    """

    def __init__(
        self,
        name: str = None,
        data: Matrix = None,
        **kwargs,
    ):
        """Initialize QuboTask.

        Args:
            name: Task name
            data: Input data matrix
            **kwargs: Additional arguments for GeneralTask
        """
        super().__init__(
            name=name,
            matrix=data,
            question_type=QUBO_PROBLEM,
            **kwargs,
        )
