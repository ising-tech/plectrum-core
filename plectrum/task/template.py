"""Template task class for Plectrum SDK."""

from typing import Any, Dict, Optional

from plectrum.task.base import BaseTask


class TemplateTask(BaseTask):
    """Template task for solving predefined problem types.

    This task type uses predefined templates for common
    optimization problems.
    """

    TASK_TYPE = "template"

    def __init__(
        self,
        name: str = None,
        template_id: int = None,
        gear: int = None,
        payload: str = None,
    ):
        """Initialize template task.

        Args:
            name: Task name
            template_id: Template ID
            gear: Self hosted computer type ID,
            payload: Template payload data
        """
        super().__init__(name=name)
        self._template_id = template_id
        self._gear = gear
        self._payload = payload

    @property
    def template_id(self) -> Optional[int]:
        """Get template ID."""
        return self._template_id

    @property
    def gear(self) -> Optional[int]:
        """Self hosted computer type ID."""
        return self._gear

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
            "computerTypeId": self._gear,
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
