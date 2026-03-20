"""Exceptions for Plectrum Core SDK."""


class PlectrumError(Exception):
    """Base exception for Plectrum SDK."""
    pass


class AuthenticationError(PlectrumError):
    """Authentication failed."""
    pass


class ClientError(PlectrumError):
    """Client error occurred."""
    pass


class TaskError(PlectrumError):
    """Task error occurred."""
    pass


class MatrixError(PlectrumError):
    """Matrix error occurred."""
    pass
