"""Tests for plectrum.client.base.BaseSolver."""
import unittest
from plectrum.client.base import BaseSolver, BaseClient
from plectrum.exceptions import ClientError
from plectrum.task.general import QuboTask, GeneralTask


class ConcreteSolver(BaseSolver):
    SUPPORTED_TASK_TYPES = [GeneralTask, QuboTask]

    def solve(self, task_data):
        return {"ok": True}

    def get_task(self, task_id):
        return {}


class TestBaseSolver(unittest.TestCase):

    def test_properties(self):
        s = ConcreteSolver(api_key="k", host="h", computer_type=1, gear=2)
        self.assertEqual(s.api_key, "k")
        self.assertEqual(s.host, "h")
        self.assertEqual(s.computer_type, 1)
        self.assertEqual(s.gear, 2)

    def test_validate_task_type_accepts(self):
        s = ConcreteSolver()
        s._validate_task_type("general")  # should not raise

    def test_validate_task_type_rejects(self):
        s = ConcreteSolver()
        with self.assertRaises(ClientError):
            s._validate_task_type("template")

    def test_repr(self):
        s = ConcreteSolver(host="http://localhost")
        self.assertIn("http://localhost", repr(s))

    def test_backward_compat_alias(self):
        self.assertIs(BaseClient, BaseSolver)


if __name__ == "__main__":
    unittest.main()
