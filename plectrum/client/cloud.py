"""Cloud solver for Plectrum SDK."""

import os
import time
import uuid
import requests

from plectrum.client.base import BaseSolver
from plectrum.const import (
    DEFAULT_CLOUD_HOST,
    DEFAULT_API_KEY_ENV,
    DEFAULT_CHANNEL,
    OEPO_ISING_1601,
    GEAR_PRECISE
)
from plectrum.exceptions import (
    AuthenticationError,
    ClientError,
    TimeoutError,
    ConnectionError,
)
from plectrum.result import Result
from plectrum.task import GeneralTask, MinimalIsingEnergyTask, QuboTask, TemplateTask


# Default polling configuration
DEFAULT_POLL_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 300  # seconds (5 minutes)


class CloudSolver(BaseSolver):
    """Cloud solver.

    This solver submits tasks to the cloud platform API
    and polls for results.
    """

    SUPPORTED_TASK_TYPES = [GeneralTask, MinimalIsingEnergyTask, QuboTask, TemplateTask]

    def __init__(
        self,
        api_key: str = None,
        host: str = None,
        computer_type: int = OEPO_ISING_1601,
        gear: int = GEAR_PRECISE,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize cloud solver.

        Args:
            api_key: API key for authentication.
                    If not provided, will try to get from env var PLECTRUM_API_KEY.
            host: Cloud API base URL.
            computer_type: Computer type (machine ID).
            gear: Gear mode (0=fast, 1=balanced, 2=precise).
            poll_interval: Polling interval in seconds (default: 2).
            timeout: Maximum wait time in seconds (default: 300).

        Raises:
            AuthenticationError: If no API key is provided or found.
        """
        if api_key is None:
            api_key = os.environ.get(DEFAULT_API_KEY_ENV)
        if not api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key= or set the "
                f"{DEFAULT_API_KEY_ENV} environment variable."
            )

        if host is None:
            host = DEFAULT_CLOUD_HOST

        super().__init__(api_key=api_key, host=host, computer_type=computer_type, gear=gear)
        self._poll_interval = poll_interval
        self._timeout = timeout
        self._session = requests.Session()

    # -- HTTP layer --

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to cloud API.

        Raises:
            AuthenticationError: On 401 responses.
            TimeoutError: On request timeout.
            ConnectionError: On network-level failures.
            ClientError: On any other HTTP / parse error.
        """
        url = f"{self._host}/{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = self._api_key
        headers["channel"] = DEFAULT_CHANNEL
        kwargs["headers"] = headers

        try:
            response = self._session.request(method, url, **kwargs)
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request to {url} timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {url}: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ClientError(f"API request failed: {e}") from e

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed: Invalid API key")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ClientError(
                f"HTTP {response.status_code} from {url}: {response.text[:200]}"
            ) from e

        try:
            return response.json()
        except ValueError as e:
            raise ClientError(
                f"Non-JSON response from {url}: {response.text[:200]}"
            ) from e

    # -- solve dispatch --

    def solve(self, task_data: dict) -> dict:
        """Submit task to cloud solver and wait for result."""
        task_type = task_data.get("task_type", "general")
        self._validate_task_type(task_type)

        if task_type == "general":
            return self._create_general_task(task_data)
        elif task_type == "template":
            return self._create_template_task(task_data)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

    # -- general task --

    def _create_general_task(self, task_data: dict) -> dict:
        """Create and submit a general task to cloud solver."""
        payload = task_data.get("payload", {}).copy()
        csv_string = task_data.get("csv_string")

        if csv_string:
            filename = payload.get("name", "task") + ".csv"
            upload_result = self._upload_file(
                file_path_or_bytes=csv_string.encode('utf-8'),
                original_filename=filename,
            )
            file_url = upload_result.get("data", {}).get("fileUrl")
            if not file_url:
                raise ClientError("Upload succeeded but no fileUrl returned")
            payload["inputJFile"] = file_url

        payload = {k: v for k, v in payload.items() if v is not None}
        payload["computerTypeId"] = self._computer_type

        submit_result = self._request("POST", "tasks/create-general", json=payload)

        task_id = submit_result.get("data", {}).get("id") or submit_result.get("id")
        if not task_id:
            raise ClientError("Failed to get task ID from response")

        return self._poll_for_result(task_id)

    # -- template task --

    def _create_template_task(self, task_data: dict) -> dict:
        """Create and submit a template task to cloud solver."""
        payload = task_data.get("payload", {})

        submit_result = self._request("POST", "tasks/create-template", json=payload)

        task_id = submit_result.get("data", {}).get("id") or submit_result.get("id")
        if not task_id:
            raise ClientError("Failed to get task ID from response")

        return self._poll_for_result(task_id)

    # -- polling --

    def _poll_for_result(self, task_id: str) -> dict:
        """Poll for task result until completion.

        Raises:
            TimeoutError: If polling exceeds *self._timeout*.
            ClientError: If the completed task has no result data.
        """
        start_time = time.time()
        completed_statuses = [1, 2, 3]

        while True:
            elapsed = time.time() - start_time
            if elapsed > self._timeout:
                raise TimeoutError(
                    f"Task {task_id} polling timeout after {self._timeout}s"
                )

            response = self.get_task(task_id)
            status = response.get("status")

            if status in completed_statuses:
                result_data = response.get("result")
                if result_data is None:
                    message = response.get("message", "Task failed")
                    raise ClientError(f"Task failed: {message}")

                result = Result.from_cloud(result_data, task_id)
                return {
                    "result": result.to_dict(),
                    "task_id": task_id,
                    "status": status,
                }

            time.sleep(self._poll_interval)

    # -- file upload --

    def _upload_file(self, file_path_or_bytes, original_filename: str = None) -> dict:
        """Upload file to OSS storage.

        Raises:
            ClientError: On signature retrieval, upload, or I/O failure.
        """
        signature_response = self._request("GET", "files/getPostSignatureForOssUpload")

        signature_data = signature_response.get("data")
        if not signature_data:
            raise ClientError("OSS signature response missing 'data' field")

        required_keys = ("host", "policy", "signature", "x_oss_credential",
                         "x_oss_date", "security_token")
        missing = [k for k in required_keys if k not in signature_data]
        if missing:
            raise ClientError(f"OSS signature missing keys: {missing}")

        form_data = self._build_oss_form(signature_data, original_filename)
        file_data = self._read_file_bytes(file_path_or_bytes, original_filename)

        try:
            files = {"file": (original_filename, file_data)}
            headers = {"Authorization": self._api_key, "channel": DEFAULT_CHANNEL}
            oss_response = requests.post(
                signature_data["host"], data=form_data,
                files=files, headers=headers,
            )
            if oss_response.status_code != 200:
                raise ClientError(
                    f"OSS upload failed with status {oss_response.status_code}"
                )
        except ClientError:
            raise
        except requests.exceptions.RequestException as e:
            raise ClientError(f"OSS upload request failed: {e}") from e

        file_key = form_data["key"]
        file_url = f"{signature_data['host']}/{file_key}"
        return {
            "success": True,
            "data": {"fileUrl": file_url, "originalFileName": original_filename},
        }

    @staticmethod
    def _build_oss_form(signature_data: dict, filename: str) -> dict:
        """Build the OSS upload form-data dict."""
        file_key = f"{str(uuid.uuid4())[:8]}/{filename}"
        return {
            "success_action_status": "200",
            "policy": signature_data["policy"],
            "x-oss-signature": signature_data["signature"],
            "x-oss-signature-version": "OSS4-HMAC-SHA256",
            "x-oss-credential": signature_data["x_oss_credential"],
            "x-oss-date": signature_data["x_oss_date"],
            "key": file_key,
            "x-oss-security-token": signature_data["security_token"],
        }

    @staticmethod
    def _read_file_bytes(file_path_or_bytes, original_filename: str = None) -> bytes:
        """Return raw bytes from a file path or bytes-like object."""
        if isinstance(file_path_or_bytes, str):
            try:
                with open(file_path_or_bytes, "rb") as f:
                    return f.read()
            except OSError as e:
                raise ClientError(f"Failed to read file: {e}") from e
        return file_path_or_bytes

    # -- query helpers --

    def get_task(self, task_id: str) -> dict:
        """Get task status from cloud."""
        return self._request("GET", f"tasks/{task_id}")

    def get_task_list(self, page_no: int = 1, page_size: int = 10) -> dict:
        """Get task list from cloud."""
        return self._request(
            "POST", "tasks/list",
            json={"page_no": page_no, "page_size": page_size},
        )

    def upload_file(self, file_path_or_bytes, original_filename: str = None) -> dict:
        """Upload file to OSS storage (public method)."""
        return self._upload_file(file_path_or_bytes, original_filename)


# Backward compatibility
CloudClient = CloudSolver
