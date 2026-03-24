"""Exceptions for Plectrum Core SDK.

Exception hierarchy:
    PlectrumError
    ├── AuthenticationError   – API key missing / invalid
    ├── ClientError           – HTTP / solver communication failures
    │   ├── TimeoutError      – Polling / request timeout
    │   └── ConnectionError   – Network-level failure
    ├── TaskError             – Task validation / execution failures
    ├── MatrixError           – Matrix data validation failures
    └── ValidationError       – General input validation failures
"""


class PlectrumError(Exception):
    """Base exception for Plectrum SDK.

    All SDK exceptions derive from this class so callers can use a single
    ``except PlectrumError`` to catch every SDK-specific error while still
    having access to the full original traceback via ``__cause__``.
    """

    def __init__(self, message: str = None):
        self.message = message or self.__class__.__doc__ or "An error occurred"
        super().__init__(self.message)


class AuthenticationError(PlectrumError):
    """Authentication failed."""
    pass


class ClientError(PlectrumError):
    """Client error occurred."""
    pass


class TimeoutError(ClientError):
    """Request or polling timeout exceeded."""
    pass


class ConnectionError(ClientError):
    """Network connection failed."""
    pass


class TaskError(PlectrumError):
    """Task error occurred."""
    pass


class MatrixError(PlectrumError):
    """Matrix error occurred."""
    pass


class ValidationError(PlectrumError):
    """Input validation failed."""
    pass
