"""Template task class for Plectrum SDK."""

from typing import Any, Dict, Optional

from plectrum.task.base import BaseTask


class TemplateTask(BaseTask):
    """Template task for solving predefined problem types.

    This task type uses predefined templates for common
    optimization problems.
    """

    def __init__(
        self,
        name: str = None,
        template_id: int = None,
        computer_type_id: int = None,
        gear: int = None,
        payload: str = None,
    ):
        """Initialize template task.

        Args:
            name: Task name
            template_id: Template ID
            computer_type_id: Computer type ID
            gear: Local/cloud gear alias, equivalent to computer_type_id
            payload: Template payload data
        """
        super().__init__(name=name)
        if (
            gear is not None
            and computer_type_id is not None
            and gear != computer_type_id
        ):
            raise ValueError("gear and computer_type_id must match when both set")
        self._template_id = template_id
        self._computer_type_id = (
            gear if gear is not None else computer_type_id
        )
        self._payload = payload

    @property
    def template_id(self) -> Optional[int]:
        """Get template ID."""
        return self._template_id

    @property
    def computer_type_id(self) -> Optional[int]:
        """Get computer type ID."""
        return self._computer_type_id

    @property
    def gear(self) -> Optional[int]:
        """Get gear alias for local/cloud solver selection."""
        return self._computer_type_id

    @property
    def payload(self) -> Optional[str]:
        """Get payload."""
        return self._payload

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary.

        Returns:
            Task data as dictionary
        """
        payload = {
            "name": self._name,
            "templateId": self._template_id,
            "computerTypeId": self._computer_type_id,
            "payload": self._payload,
        }

        return {
            "task_type": "template",
            "payload": payload,
            "csv_string": None,
            "params": {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateTask":
        """Create task from dictionary.

        Args:
            data: Task data dictionary

        Returns:
            TemplateTask instance
        """
        payload = data.get("payload", {})
        return cls(
            name=payload.get("name"),
            template_id=payload.get("templateId"),
            gear=payload.get("computerTypeId"),
            payload=payload.get("payload"),
        )
