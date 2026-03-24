# Plectrum Core SDK
# A unified SDK for submitting solving requests to cloud or local solvers

from plectrum.matrix import Matrix
from plectrum.client import BaseSolver, CloudSolver, LocalSolver, LocalOepoSolver
from plectrum.task import BaseTask, GeneralTask, MinimalIsingEnergyTask, QuboTask, TemplateTask
from plectrum.result import Result
from plectrum.const import (
    QUBO_PROBLEM,
    ISING_PROBLEM,
    GEAR_FAST,
    GEAR_BALANCED,
    GEAR_PRECISE,
    OEPO_ISING_1601,
)
from plectrum.exceptions import (
    PlectrumError,
    AuthenticationError,
    ClientError,
    TimeoutError,
    ConnectionError,
    TaskError,
    MatrixError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    # Matrix
    "Matrix",
    # Solver
    "BaseSolver",
    "CloudSolver",  # Cloud solver
    "LocalSolver",  # Local traditional algorithm solver
    "LocalOepoSolver",  # Local OEPO solver
    # Task
    "BaseTask",
    "MinimalIsingEnergyTask",  # ISING problem task
    "QuboTask",  # QUBO problem task
    "TemplateTask",
    # Result
    "Result",
    # Constants
    "QUBO_PROBLEM",
    "ISING_PROBLEM",
    "GEAR_FAST",
    "GEAR_BALANCED",
    "GEAR_PRECISE",
    "OEPO_ISING_1601",
    # Exceptions
    "PlectrumError",
    "AuthenticationError",
    "ClientError",
    "TimeoutError",
    "ConnectionError",
    "TaskError",
    "MatrixError",
    "ValidationError",
]
