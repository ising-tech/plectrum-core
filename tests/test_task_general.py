"""Tests for plectrum.task.general."""
import unittest
import numpy as np
from plectrum.task.general import GeneralTask, QuboTask, MinimalIsingEnergyTask, _convert_to_matrix
from plectrum.matrix import Matrix
from plectrum.exceptions import TaskError
from plectrum.const import QUBO_PROBLEM, ISING_PROBLEM


class TestConvertToMatrix(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(_convert_to_matrix(None))

    def test_ndarray(self):
        arr = np.array([[1.0, 0.0], [0.0, 1.0]])
        m = _convert_to_matrix(arr)
        self.assertIsInstance(m, Matrix)

    def test_matrix_passthrough(self):
        m = Matrix(np.eye(2))
        self.assertIs(_convert_to_matrix(m), m)

    def test_unsupported_type_raises_task_error(self):
        with self.assertRaises(TaskError):
            _convert_to_matrix("bad input")

    def test_duck_typed_to_csv_string(self):
        class FakeMatrix:
            def to_csv_string(self):
                return "1,0\n0,1"
        fm = FakeMatrix()
        self.assertIs(_convert_to_matrix(fm), fm)


class TestQuboTask(unittest.TestCase):

    def setUp(self):
        self.data = np.array([[1.0, 0.5], [0.5, -1.0]])
        self.task = QuboTask(name="q1", data=self.data)

    def test_task_type(self):
        self.assertEqual(self.task.task_type, "general")
        self.assertEqual(self.task.QUESTION_TYPE, QUBO_PROBLEM)

    def test_to_dict(self):
        d = self.task.to_dict()
        self.assertEqual(d["task_type"], "general")
        self.assertIsNotNone(d["csv_string"])
        self.assertEqual(d["params"]["type"], QUBO_PROBLEM)
        self.assertEqual(d["payload"]["name"], "q1")

    def test_properties(self):
        self.assertEqual(self.task.name, "q1")
        self.assertIsNotNone(self.task.matrix)
        self.assertIsNone(self.task.shot_count)
        self.assertIsNone(self.task.calculate_count)


class TestMinimalIsingEnergyTask(unittest.TestCase):

    def test_question_type(self):
        t = MinimalIsingEnergyTask(name="i1", data=np.eye(2))
        self.assertEqual(t.QUESTION_TYPE, ISING_PROBLEM)


class TestGeneralTaskFromDict(unittest.TestCase):

    def test_from_dict(self):
        d = {"payload": {"name": "test", "caculateCount": 100}}
        t = GeneralTask.from_dict(d)
        self.assertEqual(t.name, "test")
        self.assertEqual(t.shot_count, 100)


class TestGeneralTaskNoData(unittest.TestCase):

    def test_no_data_to_dict_csv_string_is_none(self):
        t = GeneralTask(name="nodata")
        d = t.to_dict()
        self.assertIsNone(d["csv_string"])

    def test_with_input_j_file(self):
        t = GeneralTask(name="f1", input_j_file="http://example.com/f.csv")
        d = t.to_dict()
        self.assertEqual(d["payload"]["inputJFile"], "http://example.com/f.csv")


if __name__ == "__main__":
    unittest.main()
