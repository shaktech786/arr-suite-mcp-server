"""Base API client for arr services."""

import logging
from typing import Any, Optional
import httpx
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class ArrClientError(Exception):
    """Base exception for arr client errors."""
    pass


class ArrClientConnectionError(ArrClientError):
    """Connection error to arr service."""
    pass


class ArrClientAuthError(ArrClientError):
    """Authentication error with arr service."""
    pass


class ArrClientNotFoundError(ArrClientError):
    """Resource not found error."""
    pass


class BaseArrClient(ABC):
    """Base client for interacting with arr services."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the base arr client.

        Args:
            base_url: Base URL of the arr service
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        self._api_version = "v3"  # Most arr services use v3

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the name of the service."""
        pass

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/api/{self._api_version}/{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Any:
        """
        Make an HTTP request to the arr service.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            retry_count: Current retry attempt

        Returns:
            JSON response from the API

        Raises:
            ArrClientConnectionError: If connection fails
            ArrClientAuthError: If authentication fails
            ArrClientNotFoundError: If resource not found
            ArrClientError: For other errors
        """
        url = self._build_url(endpoint)
        headers = self._get_headers()

        try:
            logger.debug(f"{self.service_name}: {method} {url}")
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )

            if response.status_code == 401:
                raise ArrClientAuthError(
                    f"{self.service_name}: Authentication failed. Check your API key."
                )
            elif response.status_code == 404:
                raise ArrClientNotFoundError(
                    f"{self.service_name}: Resource not found at {endpoint}"
                )
            elif response.status_code >= 400:
                raise ArrClientError(
                    f"{self.service_name}: HTTP {response.status_code} - {response.text}"
                )

            response.raise_for_status()

            # Some endpoints return empty responses
            if not response.content:
                return None

            return response.json()

        except httpx.ConnectError as e:
            if retry_count < self.max_retries:
                logger.warning(
                    f"{self.service_name}: Connection failed, retrying "
                    f"({retry_count + 1}/{self.max_retries})..."
                )
                return await self._request(
                    method, endpoint, params, json, retry_count + 1
                )
            raise ArrClientConnectionError(
                f"{self.service_name}: Could not connect to {self.base_url}"
            ) from e
        except httpx.TimeoutException as e:
            raise ArrClientConnectionError(
                f"{self.service_name}: Request timed out after {self.timeout}s"
            ) from e

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make a POST request."""
        return await self._request("POST", endpoint, json=json)

    async def put(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make a PUT request."""
        return await self._request("PUT", endpoint, json=json)

    async def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None
    ) -> Any:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint, params=params)

    async def test_connection(self) -> bool:
        """
        Test connection to the arr service.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            await self.get("system/status")
            logger.info(f"{self.service_name}: Connection test successful")
            return True
        except Exception as e:
            logger.error(f"{self.service_name}: Connection test failed - {e}")
            return False

    async def get_system_status(self) -> dict[str, Any]:
        """Get system status information."""
        return await self.get("system/status")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
