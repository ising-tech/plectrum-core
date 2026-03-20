"""Cloud client for Plectrum SDK."""

import os
import time
import uuid
import requests
from typing import Optional

from plectrum.client.base import BaseClient
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


class CloudClient(BaseClient):
    """Cloud solver client.

    This client submits tasks to the cloud platform API
    and polls for results.
    """

    def __init__(
        self,
        api_key: str = None,
        host: str = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Initialize cloud client.

        Args:
            api_key: API key for authentication.
                    If not provided, will try to get from env var PLECTRUM_API_KEY.
            host: Cloud API base URL.
                  If not provided, will use default cloud host.
            poll_interval: Polling interval in seconds (default: 2).
            timeout: Maximum wait time in seconds (default: 300).
        """
        # Get API key from param or environment variable
        if api_key is None:
            api_key = os.environ.get(DEFAULT_API_KEY_ENV)

        if host is None:
            host = DEFAULT_CLOUD_HOST

        super().__init__(api_key=api_key, host=host)
        self._poll_interval = poll_interval
        self._timeout = timeout
        self._session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:
        """Make HTTP request to cloud API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for request

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
                raise AuthenticationError(
                    "Authentication failed: Invalid API key"
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ClientError(f"API request failed: {e}")

    def solve(self, task_data: dict) -> dict:
        """Submit task to cloud solver and wait for result.

        This method:
        1. Uploads the matrix file to OSS (if provided)
        2. Creates the task with the file URL
        3. Polls for the result until completion

        Args:
            task_data: Task data dictionary

        Returns:
            Result dictionary from cloud solver (unified format)

        Raises:
            ClientError: If task fails or timeout
        """
        task_type = task_data.get("task_type", "general")
        
        # Get payload and potentially upload file
        payload = task_data.get("payload", {}).copy()
        csv_string = task_data.get("csv_string")
        
        # If csv_string is provided, upload to OSS and get file URL
        if csv_string:
            filename = payload.get("name", "task") + ".csv"
            upload_result = self.upload_file(
                file_path_or_bytes=csv_string.encode('utf-8'),
                original_filename=filename,
            )
            file_url = upload_result.get("data", {}).get("fileUrl")
            # Use the file URL as inputJFile
            payload["inputJFile"] = file_url
        
        # Update task_data with modified payload
        task_data = task_data.copy()
        task_data["payload"] = payload
        
        # Submit task
        if task_type == "general":
            submit_result = self._create_general_task(task_data)
        elif task_type == "template":
            submit_result = self._create_template_task(task_data)
        else:
            raise ClientError(f"Unknown task type: {task_type}")

        # Extract task ID from response
        # Create task API returns {data: {id: ...}}, get task returns {id: ...}
        task_id = submit_result.get("data", {}).get("id") or submit_result.get("id")
        if not task_id:
            raise ClientError("Failed to get task ID from response")

        # Poll for result
        return self._poll_for_result(task_id)

    def _poll_for_result(self, task_id: str) -> dict:
        """Poll for task result until completion.

        Args:
            task_id: Task ID

        Returns:
            Result dictionary in unified format

        Raises:
            ClientError: If timeout or task fails
        """
        start_time = time.time()
        completed_statuses = [1, 2, 3]  # Task completion statuses

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self._timeout:
                raise ClientError(
                    f"Task polling timeout after {self._timeout} seconds"
                )

            # Get task status
            response = self.get_task(task_id)
            # API wraps task data inside "data" key
            task_info = response.get("data", response)
            status = task_info.get("status")

            # Check if task is completed
            if status in completed_statuses:
                # Get raw result data
                result_data = task_info.get("result")
                if result_data is None:
                    # Task might have failed
                    message = task_info.get("message") or response.get("message", "Task failed")
                    raise ClientError(f"Task failed: {message}")

                # Convert to unified Result format
                result = Result.from_cloud(result_data, task_id)
                
                return {
                    "result": result.to_dict(),
                    "task_id": task_id,
                    "status": status,
                }

            # Wait before next poll
            time.sleep(self._poll_interval)

    def _create_general_task(self, task_data: dict) -> dict:
        """Create general task.

        Args:
            task_data: Task data

        Returns:
            Task submission response
        """
        return self._request(
            "POST",
            "tasks/create-general",
            json=task_data.get("payload"),
        )

    def _create_template_task(self, task_data: dict) -> dict:
        """Create template task.

        Args:
            task_data: Task data

        Returns:
            Task submission response
        """
        return self._request(
            "POST",
            "tasks/create-template",
            json=task_data.get("payload"),
        )

    def get_task(self, task_id: str) -> dict:
        """Get task status from cloud.

        Args:
            task_id: Task ID

        Returns:
            Task information
        """
        return self._request("GET", f"tasks/{task_id}")

    def get_task_list(
        self,
        page_no: int = 1,
        page_size: int = 10,
    ) -> dict:
        """Get task list from cloud.

        Args:
            page_no: Page number
            page_size: Page size

        Returns:
            Task list
        """
        return self._request(
            "POST",
            "tasks/list",
            json={"page_no": page_no, "page_size": page_size},
        )

    def upload_file(
        self,
        file_path_or_bytes,
        original_filename: str = None,
    ) -> dict:
        """Upload file to OSS storage.

        Args:
            file_path_or_bytes: File path (str) or file bytes
            original_filename: Original filename (required if uploading bytes)

        Returns:
            Upload result with file URL

        Raises:
            ClientError: If upload fails
        """
        # Step 1: Get OSS upload signature
        signature_response = self._request(
            "GET",
            "files/getPostSignatureForOssUpload",
        )
        signature_data = signature_response["data"]

        # Step 2: Build OSS upload form data
        form_data = {}
        file_uuid = str(uuid.uuid4())[:8]
        file_key = f"{file_uuid}/{original_filename}"

        form_data["success_action_status"] = "200"
        form_data["policy"] = signature_data["policy"]
        form_data["x-oss-signature"] = signature_data["signature"]
        form_data["x-oss-signature-version"] = "OSS4-HMAC-SHA256"
        form_data["x-oss-credential"] = signature_data["x_oss_credential"]
        form_data["x-oss-date"] = signature_data["x_oss_date"]
        form_data["key"] = file_key
        form_data["x-oss-security-token"] = signature_data["security_token"]

        # Step 3: Upload file
        try:
            if isinstance(file_path_or_bytes, str):
                with open(file_path_or_bytes, "rb") as f:
                    file_data = f.read()
                if original_filename is None:
                    original_filename = (
                        file_path_or_bytes.split("/")[-1]
                    )
            else:
                file_data = file_path_or_bytes

            files = {"file": (original_filename, file_data)}
            headers = {}
            headers["Authorization"] = self._api_key
            headers["channel"] = DEFAULT_CHANNEL

            oss_response = requests.post(
                signature_data["host"],
                data=form_data,
                files=files,
                headers=headers,
            )

            if oss_response.status_code != 200:
                raise ClientError(
                    f"OSS upload failed: {oss_response.status_code}"
                )

            file_url = f"{signature_data['host']}/{file_key}"
            return {
                "success": True,
                "data": {
                    "fileUrl": file_url,
                    "originalFileName": original_filename,
                },
            }
        except Exception as e:
            raise ClientError(f"Upload failed: {e}")
