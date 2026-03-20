# Plectrum Core SDK
# A unified SDK for submitting solving requests to cloud or local solvers

from plectrum.matrix import Matrix
from plectrum.client import BaseClient, CloudClient, LocalClient
from plectrum.solver.base import BaseSolver
from plectrum.solver.cloud import CloudSolver
from plectrum.solver.local import LocalSolver
from plectrum.solver.local_oepo import LocalOepoSolver
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

__version__ = "0.1.0"

__all__ = [
    # Matrix
    "Matrix",
    # Client
    "BaseClient",
    "CloudClient",
    "LocalClient",
    # Solver
    "BaseSolver",
    "CloudSolver",
    "LocalSolver",
    "LocalOepoSolver",
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
