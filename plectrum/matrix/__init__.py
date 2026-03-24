"""Matrix module for Plectrum SDK.

This module provides a simple wrapper around numpy arrays for task data.
"""

import csv
import numpy as np
from typing import Optional, Union
from io import StringIO


class Matrix:
    """Matrix wrapper for task data.
    
    This class wraps numpy arrays and provides CSV conversion utilities.
    """

    def __init__(self, data: np.ndarray):
        """Initialize Matrix with numpy array.
        
        Args:
            data: numpy array
        """
        self._data = np.asarray(data)

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
        """
        data = np.loadtxt(file_path, delimiter=',')
        return cls(data)

    @classmethod
    def from_csv_string(cls, csv_string: str) -> "Matrix":
        """Create Matrix from CSV string.
        
        Args:
            csv_string: CSV string
            
        Returns:
            Matrix instance
        """
        data = np.genfromtxt(StringIO(csv_string), delimiter=',')
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
