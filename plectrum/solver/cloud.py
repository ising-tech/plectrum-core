"""Cloud solver for Plectrum SDK."""

import os
import time
import uuid
import requests
from typing import Optional, Dict, Any

from plectrum.solver.base import BaseSolver
from plectrum.const import (
    DEFAULT_CLOUD_HOST,
    DEFAULT_API_KEY_ENV,
    DEFAULT_CHANNEL,
)
from plectrum.exceptions import AuthenticationError, ClientError
from plectrum.result import Result


# Default polling configuration
DEFAULT_POLL_INTERVAL = 2  # seconds
DEFAULT_TIMEOUT = 300  # seconds (5 minutes)


class CloudSolver(BaseSolver):
    """Cloud solver that submits tasks to the cloud platform API.

    Example:
        solver = CloudSolver(api_key="your_api_key")
        result = task.solve(solver=solver)
    """

    def __init__(
        self,
        api_key: str = None,
        host: str = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize cloud solver.

        Args:
            api_key: API key for authentication.
                     If not provided, reads from env var PLECTRUM_API_KEY.
            host: Cloud API base URL. Defaults to https://api.isingq.com.
            poll_interval: Polling interval in seconds (default: 2).
            timeout: Maximum wait time in seconds (default: 300).
        """
        super().__init__(gear=None)

        if api_key is None:
            api_key = os.environ.get(DEFAULT_API_KEY_ENV)

        if host is None:
            host = DEFAULT_CLOUD_HOST

        self._api_key = api_key
        self._host = host
        self._poll_interval = poll_interval
        self._timeout = timeout
        self._session = requests.Session()

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        return self._api_key

    @property
    def host(self) -> Optional[str]:
        """Get host URL."""
        return self._host

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to cloud API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON data

        Raises:
            AuthenticationError: If authentication fails
            ClientError: If request fails
        """
        url = f"{self._host}/{endpoint}"
        headers = kwargs.get("headers", {})
        headers["Authorization"] = self._api_key
        headers["channel"] = DEFAULT_CHANNEL
        kwargs["headers"] = headers

        try:
            response = self._session.request(method, url, **kwargs)
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed: Invalid API key")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ClientError(f"API request failed: {e}")

    def solve(self, task_data: Dict[str, Any]) -> Result:
        """Submit task to cloud solver and wait for result.

        Steps:
        1. Upload matrix file to OSS (if csv_string provided)
        2. Create the task via API
        3. Poll for result until completion

        Args:
            task_data: Task data dictionary

        Returns:
            Result object

        Raises:
            ClientError: If task fails or times out
        """
        start_time = time.time()

        task_type = task_data.get("task_type", "general")
        payload = task_data.get("payload", {}).copy()
        csv_string = task_data.get("csv_string")

        # Cloud API requires a valid computerTypeId (solver type).
        # Default to 1 when task does not specify one.
        if not payload.get("computerTypeId"):
            payload["computerTypeId"] = 1

        # Upload matrix to OSS if csv_string is provided
        if csv_string:
            filename = payload.get("name", "task") + ".csv"
            upload_result = self._upload_file(
                file_bytes=csv_string.encode("utf-8"),
                original_filename=filename,
            )
            file_url = upload_result.get("data", {}).get("fileUrl")
            payload["inputJFile"] = file_url

        task_data_copy = task_data.copy()
        task_data_copy["payload"] = payload

        # Submit task
        if task_type == "general":
            submit_result = self._create_general_task(task_data_copy)
        elif task_type == "template":
            submit_result = self._create_template_task(task_data_copy)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

        # Extract task ID
        task_id = submit_result.get("data", {}).get("id") or submit_result.get("id")
        if not task_id:
            raise ClientError("Failed to get task ID from response")

        # Poll for result
        result = self._poll_for_result(task_id)
        result._e2e_time = time.time() - start_time
        return result

    def _poll_for_result(self, task_id: str) -> Result:
        """Poll for task result until completion."""
        start_time = time.time()
        completed_statuses = [1, 2, 3]

        while True:
            elapsed = time.time() - start_time
            if elapsed > self._timeout:
                raise ClientError(f"Task polling timeout after {self._timeout}s")

            response = self._get_task(task_id)
            # API wraps task data inside "data" key
            task_info = response.get("data", response)
            status = task_info.get("status")

            if status in completed_statuses:
                result_data = task_info.get("result")
                if result_data is None:
                    message = task_info.get("message") or response.get("message", "Task failed")
                    raise ClientError(f"Task failed: {message}")

                return Result.from_cloud(result_data, task_id)

            time.sleep(self._poll_interval)

    def _create_general_task(self, task_data: dict) -> dict:
        """Create general task via API."""
        return self._request("POST", "tasks/create-general", json=task_data.get("payload"))

    def _create_template_task(self, task_data: dict) -> dict:
        """Create template task via API."""
        return self._request("POST", "tasks/create-template", json=task_data.get("payload"))

    def _get_task(self, task_id: str) -> dict:
        """Get task status from cloud."""
        return self._request("GET", f"tasks/{task_id}")

    def get_task_list(self, page_no: int = 1, page_size: int = 10) -> dict:
        """Get task list from cloud."""
        return self._request("POST", "tasks/list", json={"page_no": page_no, "page_size": page_size})

    def _upload_file(self, file_bytes: bytes, original_filename: str) -> dict:
        """Upload file to OSS storage.

        Args:
            file_bytes: File content as bytes
            original_filename: Original filename

        Returns:
            Upload result with file URL

        Raises:
            ClientError: If upload fails
        """
        # Get OSS upload signature
        signature_response = self._request("GET", "files/getPostSignatureForOssUpload")
        sig = signature_response["data"]

        file_uuid = str(uuid.uuid4())[:8]
        file_key = f"{file_uuid}/{original_filename}"

        form_data = {
            "success_action_status": "200",
            "policy": sig["policy"],
            "x-oss-signature": sig["signature"],
            "x-oss-signature-version": "OSS4-HMAC-SHA256",
            "x-oss-credential": sig["x_oss_credential"],
            "x-oss-date": sig["x_oss_date"],
            "key": file_key,
            "x-oss-security-token": sig["security_token"],
        }

        try:
            files = {"file": (original_filename, file_bytes)}
            headers = {
                "Authorization": self._api_key,
                "channel": DEFAULT_CHANNEL,
            }

            oss_response = requests.post(
                sig["host"], data=form_data, files=files, headers=headers,
            )
            if oss_response.status_code != 200:
                raise ClientError(f"OSS upload failed: {oss_response.status_code}")

            file_url = f"{sig['host']}/{file_key}"
            return {
                "success": True,
                "data": {
                    "fileUrl": file_url,
                    "originalFileName": original_filename,
                },
            }
        except Exception as e:
            raise ClientError(f"Upload failed: {e}")

    def __repr__(self) -> str:
        return f"CloudSolver(host={self._host})"







