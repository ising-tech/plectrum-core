"""Solver module for Plectrum Core SDK."""

__all__ = [
    "BaseSolver",
    "CloudSolver",
    "LocalSolver",
    "LocalOepoSolver",
]


def __getattr__(name):
    if name == "BaseSolver":
        from plectrum.solver.base import BaseSolver

        return BaseSolver
    if name == "CloudSolver":
        from plectrum.solver.cloud import CloudSolver

        return CloudSolver
    if name == "LocalSolver":
        from plectrum.solver.local import LocalSolver

        return LocalSolver
    if name == "LocalOepoSolver":
        from plectrum.solver.local_oepo import LocalOepoSolver

        return LocalOepoSolver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


