"""Tests for plectrum.client.cloud.CloudSolver."""
import unittest
from unittest import mock
import os
from io import BytesIO

import numpy as np
import requests

from plectrum import Matrix, MinimalIsingEnergyTask, OEPO_ISING_4095, QuboTask
from plectrum.client.cloud import CloudSolver, CloudClient, DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT
from plectrum.exceptions import (
    AuthenticationError, ClientError, TimeoutError, ConnectionError,
)
from plectrum.const import OEPO_ISING_1601, GEAR_PRECISE


class TestCloudSolverInit(unittest.TestCase):

    def test_no_api_key_raises(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AuthenticationError):
                CloudSolver(api_key=None)

    def test_empty_api_key_raises(self):
        with self.assertRaises(AuthenticationError):
            CloudSolver(api_key="")

    def test_env_api_key(self):
        with mock.patch.dict(os.environ, {"PLECTRUM_API_KEY": "env-key"}):
            solver = CloudSolver()
        self.assertEqual(solver.api_key, "env-key")

    def test_explicit_api_key(self):
        solver = CloudSolver(api_key="my-key")
        self.assertEqual(solver.api_key, "my-key")

    def test_backward_compat_alias(self):
        self.assertIs(CloudClient, CloudSolver)


class TestCloudSolverRequest(unittest.TestCase):

    def setUp(self):
        self.solver = CloudSolver(api_key="test-key")

    @mock.patch.object(requests.Session, "request")
    def test_happy_json(self, mock_req):
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": {"id": "123"}}
        mock_resp.raise_for_status = mock.MagicMock()
        mock_req.return_value = mock_resp
        result = self.solver._request("GET", "tasks/123")
        self.assertEqual(result["data"]["id"], "123")

    @mock.patch.object(requests.Session, "request")
    def test_401_raises_auth_error(self, mock_req):
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 401
        mock_req.return_value = mock_resp
        with self.assertRaises(AuthenticationError):
            self.solver._request("GET", "tasks/x")

    @mock.patch.object(requests.Session, "request")
    def test_500_raises_client_error(self, mock_req):
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_resp
        )
        mock_req.return_value = mock_resp
        with self.assertRaises(ClientError):
            self.solver._request("GET", "tasks/x")

    @mock.patch.object(requests.Session, "request")
    def test_non_json_raises(self, mock_req):
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = mock.MagicMock()
        mock_resp.json.side_effect = ValueError("No JSON")
        mock_resp.text = "not json"
        mock_req.return_value = mock_resp
        with self.assertRaises(ClientError) as ctx:
            self.solver._request("GET", "endpoint")
        self.assertIn("Non-JSON", str(ctx.exception))

    @mock.patch.object(requests.Session, "request")
    def test_timeout_raises(self, mock_req):
        mock_req.side_effect = requests.exceptions.Timeout("timed out")
        with self.assertRaises(TimeoutError):
            self.solver._request("GET", "endpoint")

    @mock.patch.object(requests.Session, "request")
    def test_connection_error_raises(self, mock_req):
        mock_req.side_effect = requests.exceptions.ConnectionError("refused")
        with self.assertRaises(ConnectionError):
            self.solver._request("GET", "endpoint")

    @mock.patch.object(requests.Session, "request")
    def test_generic_request_error_raises(self, mock_req):
        mock_req.side_effect = requests.exceptions.RequestException("generic")
        with self.assertRaises(ClientError):
            self.solver._request("GET", "endpoint")


class TestCloudSolverSolve(unittest.TestCase):

    def setUp(self):
        self.solver = CloudSolver(api_key="test-key", timeout=1, poll_interval=0.1)

    @mock.patch.object(CloudSolver, "_request")
    def test_unsupported_task_type(self, mock_req):
        with self.assertRaises(ClientError):
            self.solver.solve({"task_type": "unknown"})

    @mock.patch.object(CloudSolver, "_poll_for_result")
    @mock.patch.object(CloudSolver, "_upload_file")
    @mock.patch.object(CloudSolver, "_request")
    def test_general_happy_with_csv(self, mock_req, mock_upload, mock_poll):
        mock_upload.return_value = {"data": {"fileUrl": "http://oss/file.csv"}}
        mock_req.return_value = {"data": {"id": "task-1"}}
        mock_poll.return_value = {"result": {}, "task_id": "task-1", "status": 1}
        result = self.solver.solve({
            "task_type": "general",
            "csv_string": "1,0\n0,1",
            "payload": {"name": "test"},
            "params": {},
        })
        self.assertEqual(result["task_id"], "task-1")

    @mock.patch.object(CloudSolver, "_poll_for_result")
    @mock.patch.object(CloudSolver, "_request")
    def test_general_passes_payment_flags_through(self, mock_req, mock_poll):
        mock_req.return_value = {"data": {"id": "task-1"}}
        mock_poll.return_value = {"result": {}, "task_id": "task-1", "status": 1}

        result = self.solver.solve({
            "task_type": "general",
            "csv_string": None,
            "payload": {
                "name": "test",
                "useCoupon": True,
                "useCredit": True,
            },
            "params": {},
        })

        request_json = mock_req.call_args.kwargs["json"]
        self.assertEqual(result["task_id"], "task-1")
        self.assertTrue(request_json["useCoupon"])
        self.assertTrue(request_json["useCredit"])

    @mock.patch.object(CloudSolver, "_request")
    @mock.patch.object(Matrix, "to_csv_string", side_effect=AssertionError("Unexpected CSV"))
    def test_s4095_solves_full_size_matrix_as_npz(self, mock_csv, mock_req):
        self.assertEqual(OEPO_ISING_4095, 8)
        solver = CloudSolver(api_key="test-key", computer_type=OEPO_ISING_4095, poll_interval=0)
        matrix = np.zeros((4095, 4095), dtype=np.int8)
        matrix[0, 1] = matrix[1, 0] = -1
        task = MinimalIsingEnergyTask(name="s4095", data=matrix, shot_count=1, post_process=1)
        mock_req.side_effect = [
            {"data": {
                "host": "https://oss.example.com",
                "dir": "open-api/test/",
                "policy": "p",
                "signature": "s",
                "x_oss_credential": "c",
                "x_oss_date": "d",
                "security_token": "t",
            }},
            {"data": {"id": "s4095-task"}},
            {"status": 1, "result": None},
            {"status": 2, "result": {"energy": -2, "spin_config": [1] * 4095}},
        ]
        with mock.patch("plectrum.client.cloud.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            result = task.solve(solver)

        mock_csv.assert_not_called()
        self.assertEqual(task.task_id, "s4095-task")
        self.assertEqual(len(result["result"]["spin_config"]), 4095)
        upload = mock_post.call_args.kwargs
        self.assertNotIn("headers", upload)
        filename, binary = upload["files"]["file"]
        self.assertEqual(filename, "matrix.npz")
        with np.load(BytesIO(binary), allow_pickle=False) as archive:
            self.assertEqual(archive.files, ["matrix"])
            np.testing.assert_array_equal(archive["matrix"], matrix)

        key = upload["data"]["key"]
        self.assertTrue(key.startswith("open-api/test/"))
        self.assertEqual(mock_req.call_args_list[1], mock.call(
            "POST", "tasks/create-general",
            json={
                "name": "s4095", "questionType": 2, "computerTypeId": 8,
                "inputJFile": f"https://oss.example.com/{key}",
                "caculateCount": 1, "postProcess": 1,
                "useCoupon": False, "useCredit": False,
            },
        ))
        self.assertEqual(mock_req.call_args_list[2:], [mock.call("GET", "tasks/s4095-task")] * 2)

    @mock.patch.object(CloudSolver, "_request")
    def test_s4095_rejects_4095_variable_qubo_before_upload(self, mock_req):
        solver = CloudSolver(api_key="test-key", computer_type=OEPO_ISING_4095)
        task = QuboTask(data=np.broadcast_to(0.0, (4095, 4095)))
        with self.assertRaisesRegex(ClientError, "1 to 4094"):
            task.solve(solver)
        mock_req.assert_not_called()

    def test_s4095_keeps_coefficients_that_require_float64(self):
        matrix = Matrix.from_array(np.array([[0.1]]))
        binary = CloudSolver._encode_s4095_matrix(matrix, question_type=1)
        with np.load(BytesIO(binary), allow_pickle=False) as archive:
            self.assertEqual(archive["matrix"].dtype, np.float64)
            np.testing.assert_array_equal(archive["matrix"], matrix.data)

    def test_s4095_rejects_an_archive_over_the_upload_limit(self):
        matrix = Matrix.from_array(np.array([[0.1]]))
        with mock.patch("plectrum.client.cloud.MAX_NPZ_UPLOAD_BYTES", 1):
            with self.assertRaisesRegex(ClientError, "100 MiB upload limit"):
                CloudSolver._encode_s4095_matrix(matrix, question_type=1)

    @mock.patch.object(CloudSolver, "_request")
    def test_general_no_task_id_raises(self, mock_req):
        mock_req.return_value = {"data": {}}
        with self.assertRaises(ClientError):
            self.solver.solve({
                "task_type": "general",
                "csv_string": None,
                "payload": {"name": "test"},
                "params": {},
            })

    @mock.patch.object(CloudSolver, "_poll_for_result")
    @mock.patch.object(CloudSolver, "_request")
    def test_template_happy(self, mock_req, mock_poll):
        mock_req.return_value = {"data": {"id": "t-1"}}
        mock_poll.return_value = {"result": {}, "task_id": "t-1", "status": 1}
        result = self.solver.solve({
            "task_type": "template",
            "payload": {"name": "tmpl"},
        })
        self.assertEqual(result["task_id"], "t-1")


class TestCloudSolverPoll(unittest.TestCase):

    def setUp(self):
        self.solver = CloudSolver(api_key="test-key", timeout=1, poll_interval=0.05)

    @mock.patch.object(CloudSolver, "get_task")
    def test_poll_success(self, mock_get):
        mock_get.return_value = {
            "status": 1,
            "result": {"energy": -1.0, "spin_config": [0], "oepo_time": "0.1s"},
        }
        result = self.solver._poll_for_result("tid")
        self.assertEqual(result["task_id"], "tid")

    @mock.patch.object(CloudSolver, "get_task")
    def test_poll_timeout(self, mock_get):
        mock_get.return_value = {"status": 0}
        with self.assertRaises(TimeoutError):
            self.solver._poll_for_result("tid")

    @mock.patch.object(CloudSolver, "get_task")
    def test_poll_task_failed(self, mock_get):
        mock_get.return_value = {"status": 3, "result": {"ok": False}, "message": "err"}
        with self.assertRaisesRegex(ClientError, "err"):
            self.solver._poll_for_result("tid")

    @mock.patch.object(CloudSolver, "get_task")
    def test_poll_success_requires_result(self, mock_get):
        mock_get.return_value = {"status": 2, "result": None}
        with self.assertRaisesRegex(ClientError, "Task failed"):
            self.solver._poll_for_result("tid")


class TestCloudSolverUpload(unittest.TestCase):

    def setUp(self):
        self.solver = CloudSolver(api_key="test-key")

    @mock.patch("plectrum.client.cloud.requests.post")
    @mock.patch.object(CloudSolver, "_request")
    def test_upload_happy(self, mock_req, mock_post):
        mock_req.return_value = {
            "data": {
                "host": "http://oss.example.com",
                "policy": "p",
                "signature": "s",
                "x_oss_credential": "c",
                "x_oss_date": "d",
                "security_token": "t",
            }
        }
        mock_post_resp = mock.MagicMock()
        mock_post_resp.status_code = 200
        mock_post.return_value = mock_post_resp

        result = self.solver._upload_file(b"data", "test.csv")
        self.assertTrue(result["success"])
        self.assertIn("fileUrl", result["data"])

    @mock.patch.object(CloudSolver, "_request")
    def test_upload_missing_signature_data(self, mock_req):
        mock_req.return_value = {"data": None}
        with self.assertRaises(ClientError):
            self.solver._upload_file(b"data", "test.csv")

    @mock.patch.object(CloudSolver, "_request")
    def test_upload_missing_keys(self, mock_req):
        mock_req.return_value = {"data": {"host": "h"}}
        with self.assertRaises(ClientError) as ctx:
            self.solver._upload_file(b"data", "test.csv")
        self.assertIn("missing keys", str(ctx.exception))

    @mock.patch("plectrum.client.cloud.requests.post")
    @mock.patch.object(CloudSolver, "_request")
    def test_upload_oss_non_200(self, mock_req, mock_post):
        mock_req.return_value = {
            "data": {
                "host": "http://oss.example.com",
                "policy": "p", "signature": "s",
                "x_oss_credential": "c", "x_oss_date": "d",
                "security_token": "t",
            }
        }
        mock_post_resp = mock.MagicMock()
        mock_post_resp.status_code = 403
        mock_post.return_value = mock_post_resp

        with self.assertRaises(ClientError):
            self.solver._upload_file(b"data", "test.csv")

    def test_read_file_bytes_from_bytes(self):
        result = CloudSolver._read_file_bytes(b"hello", "f.csv")
        self.assertEqual(result, b"hello")

    def test_read_file_bytes_bad_path(self):
        with self.assertRaises(ClientError):
            CloudSolver._read_file_bytes("/nonexistent/path.bin", "f.bin")


class TestCloudSolverUploadFilePublic(unittest.TestCase):

    @mock.patch.object(CloudSolver, "_upload_file")
    def test_upload_file_delegates(self, mock_internal):
        mock_internal.return_value = {"success": True}
        solver = CloudSolver(api_key="test-key")
        result = solver.upload_file(b"data", "test.csv")
        mock_internal.assert_called_once()


class TestCloudSolverGetTaskList(unittest.TestCase):

    @mock.patch.object(CloudSolver, "_request")
    def test_get_task_list(self, mock_req):
        mock_req.return_value = {"data": []}
        solver = CloudSolver(api_key="test-key")
        result = solver.get_task_list(page_no=1, page_size=5)
        mock_req.assert_called_once()


class TestCloudSolverUploadNoFileUrl(unittest.TestCase):

    @mock.patch.object(CloudSolver, "_upload_file")
    @mock.patch.object(CloudSolver, "_request")
    def test_no_file_url_raises(self, mock_req, mock_upload):
        mock_upload.return_value = {"data": {}}
        mock_req.return_value = {"data": {"id": "task-1"}}
        solver = CloudSolver(api_key="test-key")
        with self.assertRaises(ClientError):
            solver.solve({
                "task_type": "general",
                "csv_string": "1,0\n0,1",
                "payload": {"name": "test"},
                "params": {},
            })


if __name__ == "__main__":
    unittest.main()
