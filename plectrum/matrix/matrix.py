"""Matrix class for handling input data."""

import csv
import io
import numpy as np
from typing import Union, Optional

from plectrum.exceptions import MatrixError


class Matrix:
    """Matrix class for storing and processing input data."""

    def __init__(
        self,
        data: np.ndarray,
        matrix_type: str = "dense",
    ):
        """Initialize Matrix.

        Args:
            data: numpy array containing matrix data
            matrix_type: type of matrix (dense or sparse)
        """
        self._data = np.array(data, dtype=np.float64)
        self._matrix_type = matrix_type

    @classmethod
    def from_csv(
        cls,
        file_path: str,
        delimiter: str = ",",
    ) -> "Matrix":
        """Create Matrix from CSV file.

        Args:
            file_path: path to CSV file
            delimiter: CSV delimiter

        Returns:
            Matrix instance

        Raises:
            MatrixError: if file cannot be read
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                data = np.array(list(reader), dtype=np.float64)
            return cls(data=data)
        except Exception as e:
            raise MatrixError(f"Failed to read CSV file: {e}")

    @classmethod
    def from_csv_string(
        cls,
        csv_string: str,
        delimiter: str = ",",
    ) -> "Matrix":
        """Create Matrix from CSV string.

        Args:
            csv_string: CSV content as string
            delimiter: CSV delimiter

        Returns:
            Matrix instance

        Raises:
            MatrixError: if string cannot be parsed
        """
        try:
            reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
            data = np.array(list(reader), dtype=np.float64)
            return cls(data=data)
        except Exception as e:
            raise MatrixError(f"Failed to parse CSV string: {e}")

    @classmethod
    def from_array(cls, array: np.ndarray) -> "Matrix":
        """Create Matrix from numpy array.

        Args:
            array: numpy array

        Returns:
            Matrix instance
        """
        return cls(data=array)

    @property
    def data(self) -> np.ndarray:
        """Get matrix data as numpy array."""
        return self._data

    @property
    def shape(self) -> tuple:
        """Get matrix shape."""
        return self._data.shape

    @property
    def matrix_type(self) -> str:
        """Get matrix type."""
        return self._matrix_type

    def to_csv_string(self, delimiter: str = ",") -> str:
        """Convert matrix to CSV string.

        Args:
            delimiter: CSV delimiter

        Returns:
            CSV string representation
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)
        for row in self._data:
            writer.writerow(row)
        return output.getvalue()

    def to_list(self) -> list:
        """Convert matrix to list of lists."""
        return self._data.tolist()

    def __repr__(self) -> str:
        return f"Matrix(shape={self.shape}, type={self._matrix_type})"
