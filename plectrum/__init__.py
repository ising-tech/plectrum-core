# Plectrum Core SDK
# A unified SDK for submitting solving requests to cloud or local solvers

from plectrum.matrix import Matrix
from plectrum.client import BaseClient, CloudClient, LocalClient
from plectrum.solver import BaseSolver, CloudSolver, LocalOepoSolver, LocalSolver
from plectrum.task import BaseTask, GeneralTask, TemplateTask
from plectrum.result import Result
from plectrum.const import (
    QUBO_PROBLEM,
    ISING_PROBLEM,
)
from plectrum.exceptions import (
    PlectrumError,
    AuthenticationError,
    ClientError,
)

__version__ = "0.2.0"

__all__ = [
    # Matrix
    "Matrix",
    # Solvers (new API)
    "BaseSolver",
    "CloudSolver",
    "LocalOepoSolver",
    "LocalSolver",
    # Clients (legacy, backward-compatible)
    "BaseClient",
    "CloudClient",
    "LocalClient",
    # Task
    "BaseTask",
    "GeneralTask",
    "TemplateTask",
    # Result
    "Result",
    # Constants
    "QUBO_PROBLEM",
    "ISING_PROBLEM",
    # Exceptions
    "PlectrumError",
    "AuthenticationError",
    "ClientError",
]
