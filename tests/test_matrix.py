"""Tests for plectrum.matrix.Matrix."""
import unittest
import os
import tempfile
import numpy as np
from plectrum.matrix import Matrix
from plectrum.exceptions import MatrixError


class TestMatrixFromArray(unittest.TestCase):

    def test_happy_path(self):
        arr = np.array([[1.0, 2.0], [3.0, 4.0]])
        m = Matrix.from_array(arr)
        self.assertEqual(m.shape, (2, 2))
        np.testing.assert_array_equal(m.data, arr)

    def test_empty_raises(self):
        with self.assertRaises(MatrixError):
            Matrix(np.array([]))

    def test_1d_raises(self):
        with self.assertRaises(MatrixError):
            Matrix(np.array([1.0, 2.0]))

    def test_nan_raises(self):
        with self.assertRaises(MatrixError):
            Matrix(np.array([[1.0, float("nan")]]))

    def test_inf_raises(self):
        with self.assertRaises(MatrixError):
            Matrix(np.array([[1.0, float("inf")]]))

    def test_non_numeric_raises(self):
        with self.assertRaises(MatrixError):
            Matrix(np.array([["a", "b"], ["c", "d"]]))


class TestMatrixCsvRoundTrip(unittest.TestCase):

    def test_to_csv_string(self):
        m = Matrix(np.array([[1.0, 2.0], [3.0, 4.0]]))
        csv_str = m.to_csv_string()
        self.assertIn("1.0", csv_str)
        self.assertIn("4.0", csv_str)

    def test_from_csv_string_happy(self):
        csv_str = "1.0,2.0\n3.0,4.0"
        m = Matrix.from_csv_string(csv_str)
        self.assertEqual(m.shape, (2, 2))

    def test_from_csv_string_empty_raises(self):
        with self.assertRaises(MatrixError):
            Matrix.from_csv_string("")

    def test_from_csv_string_whitespace_raises(self):
        with self.assertRaises(MatrixError):
            Matrix.from_csv_string("   ")


class TestMatrixFromCsvFile(unittest.TestCase):

    def test_happy_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("1.0,2.0\n3.0,4.0\n")
            path = f.name
        try:
            m = Matrix.from_csv(path)
            self.assertEqual(m.shape, (2, 2))
        finally:
            os.unlink(path)

    def test_file_not_found_raises(self):
        with self.assertRaises(MatrixError) as ctx:
            Matrix.from_csv("/nonexistent/path.csv")
        self.assertIsNotNone(ctx.exception.__cause__)

    def test_bad_csv_content_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\nc,d\n")
            path = f.name
        try:
            with self.assertRaises(MatrixError):
                Matrix.from_csv(path)
        finally:
            os.unlink(path)


class TestMatrixRepr(unittest.TestCase):

    def test_repr(self):
        m = Matrix(np.array([[1.0, 2.0], [3.0, 4.0]]))
        self.assertIn("2, 2", repr(m))


if __name__ == "__main__":
    unittest.main()
