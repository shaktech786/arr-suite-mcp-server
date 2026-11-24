"""Jackett API client.

Jackett exposes two API surfaces:
- Admin REST API (/api/v2.0/indexers, /api/v2.0/server/config): requires a
  browser session when called from non-localhost IPs even with a valid apikey.
- Results/search API (/api/v2.0/indexers/{id}/results): accepts ?apikey= and
  is accessible from any IP.

This client uses only the results API, which is the meaningful surface for an
MCP tool (search and indexer status). Admin operations are out of scope.
"""

from typing import Any, Optional
from .base import BaseArrClient


class JackettClient(BaseArrClient):
    """Client for interacting with Jackett's results API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, max_retries: int = 3):
        """Initialize Jackett client (v2.0 results API, query-param auth)."""
        super().__init__(base_url, api_key, timeout, max_retries)
        self._api_version = "v2.0"

    @property
    def service_name(self) -> str:
        return "Jackett"

    def _build_url(self, endpoint: str) -> str:
        """Jackett uses /api/v2.0/<endpoint>."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/api/{self._api_version}/{endpoint}"

    def _get_headers(self) -> dict[str, str]:
        """Jackett results API uses query-param auth, not X-Api-Key header."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _inject_api_key(self, params: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Return params dict with apikey injected."""
        result = dict(params) if params else {}
        result["apikey"] = self.api_key
        return result

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """GET with apikey injected as query param."""
        return await self._request("GET", endpoint, params=self._inject_api_key(params))

    async def post(self, endpoint: str, json: Optional[dict[str, Any]] = None) -> Any:
        """POST with apikey injected as query param."""
        return await self._request("POST", endpoint, params=self._inject_api_key(None), json=json)

    async def search(
        self,
        query: str,
        indexer: str = "all",
        categories: Optional[list[int]] = None,
    ) -> dict[str, Any]:
        """Search for releases via the results endpoint.

        Args:
            query: Search term
            indexer: Indexer ID to target (default "all")
            categories: Optional list of Torznab category IDs to filter by

        Returns:
            Dict with "Results" (release list) and "Indexers" (per-indexer stats)
        """
        params: dict[str, Any] = {"Query.SearchTerm": query}
        if categories:
            params["Category[]"] = categories
        return await self.get(f"indexers/{indexer}/results", params=params)

    async def get_all_indexers(self) -> list[dict[str, Any]]:
        """Return configured indexers with live status via the results API.

        Jackett's admin indexer-list endpoint requires a browser session from
        non-localhost IPs. Instead, we probe the results API with an empty
        query and extract the per-indexer status from the response.
        """
        response = await self.get(
            "indexers/all/results",
            params={"Query.SearchTerm": ""},
        )
        return response.get("Indexers", []) if isinstance(response, dict) else []

    async def get_system_status(self) -> dict[str, Any]:
        """Return high-level Jackett status derived from an indexer probe."""
        response = await self.get(
            "indexers/all/results",
            params={"Query.SearchTerm": ""},
        )
        indexers = response.get("Indexers", []) if isinstance(response, dict) else []
        healthy = [i for i in indexers if i.get("Status") == 2]
        return {
            "online": True,
            "total_indexers": len(indexers),
            "healthy_indexers": len(healthy),
            "errored_indexers": len(indexers) - len(healthy),
        }
