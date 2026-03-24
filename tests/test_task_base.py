"""Tests for plectrum.task.base.BaseTask.solve()."""
import unittest
from unittest import mock
import numpy as np
from plectrum.task.general import QuboTask
from plectrum.task.template import TemplateTask
from plectrum.client.local import LocalSolver
from plectrum.exceptions import ClientError, TaskError, PlectrumError
from plectrum.const import GEAR_FAST


class TestBaseTaskSolve(unittest.TestCase):

    def test_happy_path_stores_task_id(self):
        solver = LocalSolver(gear=GEAR_FAST)
        task = QuboTask(name="test", data=np.eye(3))
        result = task.solve(solver)
        self.assertIn("task_id", result)
        self.assertIsNotNone(task.task_id)

    def test_unsupported_task_type_raises(self):
        solver = LocalSolver(gear=GEAR_FAST)
        task = TemplateTask(name="unsupported", template_id=1)
        with self.assertRaises(ClientError):
            task.solve(solver)

    def test_unexpected_exception_wrapped_in_task_error(self):
        solver = mock.MagicMock()
        solver.SUPPORTED_TASK_TYPES = []
        solver.solve.side_effect = RuntimeError("boom")
        task = QuboTask(name="test", data=np.eye(3))
        # Remove SUPPORTED_TASK_TYPES to bypass validation
        del solver.SUPPORTED_TASK_TYPES
        with self.assertRaises(TaskError) as ctx:
            task.solve(solver)
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_plectrum_error_reraised_directly(self):
        solver = mock.MagicMock()
        del solver.SUPPORTED_TASK_TYPES
        solver.solve.side_effect = ClientError("direct")
        task = QuboTask(name="test", data=np.eye(3))
        with self.assertRaises(ClientError):
            task.solve(solver)

    def test_repr(self):
        task = QuboTask(name="repr_test")
        self.assertIn("repr_test", repr(task))


if __name__ == "__main__":
    unittest.main()
