"""Tests for plectrum.client.local (LocalSolver and LocalOepoSolver)."""
import unittest
from unittest import mock
import numpy as np
import requests

from plectrum.client.local import LocalSolver, LocalOepoSolver, LocalClient
from plectrum.exceptions import ClientError, TimeoutError, ConnectionError
from plectrum.const import GEAR_FAST, GEAR_PRECISE, QUBO_PROBLEM, ISING_PROBLEM


SMALL_CSV = "1.0,0.5\n0.5,-1.0"


class TestLocalSolverParseCsv(unittest.TestCase):

    def test_happy(self):
        m = LocalSolver._parse_csv_string(SMALL_CSV)
        self.assertEqual(m.shape, (2, 2))

    def test_malformed_raises(self):
        with self.assertRaises(ClientError) as ctx:
            LocalSolver._parse_csv_string("a,b\nc,d")
        self.assertIsNotNone(ctx.exception.__cause__)


class TestLocalSolverSolve(unittest.TestCase):

    def setUp(self):
        self.solver = LocalSolver(gear=GEAR_FAST)

    def test_qubo_happy(self):
        task_data = {
            "task_type": "general",
            "csv_string": SMALL_CSV,
            "params": {"type": QUBO_PROBLEM},
        }
        result = self.solver.solve(task_data)
        self.assertIn("result", result)
        self.assertTrue(result["result"]["ok"])
        self.assertIsInstance(result["result"]["energy"], float)

    def test_ising_happy(self):
        task_data = {
            "task_type": "general",
            "csv_string": SMALL_CSV,
            "params": {"type": ISING_PROBLEM},
        }
        result = self.solver.solve(task_data)
        self.assertIn("result", result)

    def test_missing_csv_raises(self):
        task_data = {"task_type": "general", "csv_string": None, "params": {}}
        with self.assertRaises(ClientError):
            self.solver.solve(task_data)

    def test_empty_csv_raises(self):
        task_data = {"task_type": "general", "csv_string": "", "params": {}}
        with self.assertRaises(ClientError):
            self.solver.solve(task_data)

    def test_unsupported_task_type_raises(self):
        task_data = {"task_type": "template"}
        with self.assertRaises(ClientError):
            self.solver.solve(task_data)


class TestLocalSolverGetTask(unittest.TestCase):

    def test_get_task(self):
        s = LocalSolver()
        info = s.get_task("some-id")
        self.assertEqual(info["status"], "completed")


class TestLocalSolverEnergy(unittest.TestCase):

    def test_qubo_energy_known(self):
        m = np.array([[2.0, -1.0], [-1.0, 2.0]])
        state = np.array([1, 0])
        e = LocalSolver._calculate_qubo_energy(m, state)
        expected = float(state @ m @ state)
        self.assertAlmostEqual(e, expected)

    def test_ising_energy_known(self):
        m = np.array([[0.0, -1.0], [-1.0, 0.0]])
        state = np.array([1, -1])
        e = LocalSolver._calculate_ising_energy(m, state)
        expected = float(state @ m @ state)
        self.assertAlmostEqual(e, expected)


class TestLocalOepoSolverHappy(unittest.TestCase):

    @mock.patch("plectrum.client.local.requests.Session")
    def test_happy_path(self, MockSession):
        mock_resp = mock.MagicMock()
        mock_resp.json.return_value = {
            "job_name": "j1",
            "result": {
                "energy": -2.0,
                "spin_config": [1, -1],
                "isingCalcMs": 500,
                "ok": True,
                "msg": "done",
                "ts": 111,
            }
        }
        MockSession.return_value.post.return_value = mock_resp

        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {
            "task_type": "general",
            "csv_string": SMALL_CSV,
            "params": {"type": QUBO_PROBLEM},
        }
        result = solver.solve(task_data)
        self.assertEqual(result["task_id"], "j1")

    @mock.patch("plectrum.client.local.requests.Session")
    def test_server_error_json(self, MockSession):
        mock_resp = mock.MagicMock()
        mock_resp.json.return_value = {"error": "could not convert string"}
        MockSession.return_value.post.return_value = mock_resp

        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {"task_type": "general", "csv_string": SMALL_CSV, "params": {}}
        with self.assertRaises(ClientError) as ctx:
            solver.solve(task_data)
        self.assertIn("could not convert", str(ctx.exception))

    @mock.patch("plectrum.client.local.requests.Session")
    def test_timeout_raises(self, MockSession):
        MockSession.return_value.post.side_effect = requests.exceptions.Timeout("timeout")
        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {"task_type": "general", "csv_string": SMALL_CSV, "params": {}}
        with self.assertRaises(TimeoutError):
            solver.solve(task_data)

    @mock.patch("plectrum.client.local.requests.Session")
    def test_connection_error_raises(self, MockSession):
        MockSession.return_value.post.side_effect = requests.exceptions.ConnectionError("refused")
        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {"task_type": "general", "csv_string": SMALL_CSV, "params": {}}
        with self.assertRaises(ConnectionError):
            solver.solve(task_data)

    @mock.patch("plectrum.client.local.requests.Session")
    def test_non_json_response_raises(self, MockSession):
        mock_resp = mock.MagicMock()
        mock_resp.json.side_effect = ValueError("No JSON")
        mock_resp.status_code = 200
        mock_resp.text = "not json"
        MockSession.return_value.post.return_value = mock_resp

        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {"task_type": "general", "csv_string": SMALL_CSV, "params": {}}
        with self.assertRaises(ClientError):
            solver.solve(task_data)

    def test_missing_csv_raises(self):
        solver = LocalOepoSolver(host="http://fake:5001")
        task_data = {"task_type": "general", "csv_string": None, "params": {}}
        with self.assertRaises(ClientError):
            solver.solve(task_data)

    def test_unsupported_task_type(self):
        solver = LocalOepoSolver(host="http://fake:5001")
        with self.assertRaises(ClientError):
            solver.solve({"task_type": "template"})

    def test_get_task(self):
        solver = LocalOepoSolver(host="http://fake:5001")
        info = solver.get_task("x")
        self.assertEqual(info["status"], "unknown")


class TestLocalOepoBuildParams(unittest.TestCase):

    @mock.patch("plectrum.client.local.requests.Session")
    def test_ising_type_param(self, MockSession):
        solver = LocalOepoSolver(host="http://fake:5001", computer_type=1, gear=2)
        params = solver._build_params({"params": {"type": ISING_PROBLEM}})
        self.assertEqual(params["type"], "spin")
        self.assertEqual(params["computer"], "1")

    @mock.patch("plectrum.client.local.requests.Session")
    def test_qubo_type_param(self, MockSession):
        solver = LocalOepoSolver(host="http://fake:5001")
        params = solver._build_params({"params": {"type": QUBO_PROBLEM}})
        self.assertEqual(params["type"], "binary")

    @mock.patch("plectrum.client.local.requests.Session")
    def test_no_type_param(self, MockSession):
        solver = LocalOepoSolver(host="http://fake:5001")
        params = solver._build_params({"params": {}})
        self.assertNotIn("type", params)


class TestBackwardCompat(unittest.TestCase):

    def test_local_client_alias(self):
        self.assertIs(LocalClient, LocalSolver)


if __name__ == "__main__":
    unittest.main()
