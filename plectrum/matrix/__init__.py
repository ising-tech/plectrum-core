"""Matrix module for Plectrum SDK.

This module provides a simple wrapper around numpy arrays for task data.
"""

import csv
import numpy as np
from io import StringIO

from plectrum.exceptions import MatrixError


class Matrix:
    """Matrix wrapper for task data.
    
    This class wraps numpy arrays and provides CSV conversion utilities.
    """

    def __init__(self, data: np.ndarray):
        """Initialize Matrix with numpy array.
        
        Args:
            data: numpy array
            
        Raises:
            MatrixError: If data is empty, not 2-D, or contains non-numeric values.
        """
        try:
            arr = np.asarray(data, dtype=float)
        except (ValueError, TypeError) as e:
            raise MatrixError(f"Matrix data must be numeric: {e}") from e

        if arr.size == 0:
            raise MatrixError("Matrix data must not be empty")

        if arr.ndim != 2:
            raise MatrixError(
                f"Matrix data must be 2-D, got {arr.ndim}-D with shape {arr.shape}"
            )

        if np.isnan(arr).any() or np.isinf(arr).any():
            raise MatrixError("Matrix data contains NaN or Inf values")

        self._data = arr

    @property
    def shape(self) -> tuple:
        """Get matrix shape."""
        return self._data.shape

    @property
    def data(self) -> np.ndarray:
        """Get underlying numpy array."""
        return self._data

    def to_csv_string(self) -> str:
        """Convert matrix to CSV string format.
        
        Returns:
            CSV string representation
        """
        output = StringIO()
        writer = csv.writer(output)
        for row in self._data:
            writer.writerow(row)
        return output.getvalue()

    @classmethod
    def from_csv(cls, file_path: str) -> "Matrix":
        """Create Matrix from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Matrix instance
            
        Raises:
            MatrixError: If file cannot be read or parsed.
        """
        try:
            data = np.loadtxt(file_path, delimiter=',')
        except FileNotFoundError as e:
            raise MatrixError(f"CSV file not found: {file_path}") from e
        except Exception as e:
            raise MatrixError(f"Failed to parse CSV file '{file_path}': {e}") from e
        return cls(data)

    @classmethod
    def from_csv_string(cls, csv_string: str) -> "Matrix":
        """Create Matrix from CSV string.
        
        Args:
            csv_string: CSV string
            
        Returns:
            Matrix instance
            
        Raises:
            MatrixError: If CSV string cannot be parsed.
        """
        if not csv_string or not csv_string.strip():
            raise MatrixError("CSV string must not be empty")
        try:
            data = np.genfromtxt(StringIO(csv_string), delimiter=',')
        except Exception as e:
            raise MatrixError(f"Failed to parse CSV string: {e}") from e
        return cls(data)

    @classmethod
    def from_array(cls, array: np.ndarray) -> "Matrix":
        """Create Matrix from numpy array.
        
        Args:
            array: numpy array
            
        Returns:
            Matrix instance
        """
        return cls(array)

    def __repr__(self) -> str:
        return f"Matrix(shape={self._data.shape})"
