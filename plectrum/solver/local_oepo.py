"""Compatibility wrapper for the local OEPO-backed solver."""

from plectrum.client.local import LocalClient


class LocalOepoSolver(LocalClient):
    """Solver alias for the local OEPO service implementation."""

