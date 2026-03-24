"""Task module for Plectrum Core SDK."""

from plectrum.task.base import BaseTask
from plectrum.task.general import GeneralTask, MinimalIsingEnergyTask, QuboTask
from plectrum.task.template import TemplateTask

__all__ = [
    "BaseTask",
    "GeneralTask",
    "MinimalIsingEnergyTask",
    "QuboTask",
    "TemplateTask",
]
