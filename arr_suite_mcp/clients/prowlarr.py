"""Prowlarr API client."""

from typing import Any, Optional
from .base import BaseArrClient


class ProwlarrClient(BaseArrClient):
    """Client for interacting with Prowlarr API."""

    @property
    def service_name(self) -> str:
        return "Prowlarr"

    # Indexer Management
    async def get_all_indexers(self) -> list[dict[str, Any]]:
        """Get all configured indexers."""
        return await self.get("indexer")

    async def get_indexer(self, indexer_id: int) -> dict[str, Any]:
        """Get a specific indexer by ID."""
        return await self.get(f"indexer/{indexer_id}")

    async def add_indexer(self, indexer_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new indexer."""
        return await self.post("indexer", json=indexer_data)

    async def update_indexer(self, indexer_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing indexer."""
        return await self.put("indexer", json=indexer_data)

    async def delete_indexer(self, indexer_id: int) -> None:
        """Delete an indexer."""
        await self.delete(f"indexer/{indexer_id}")

    async def test_indexer(self, indexer_data: dict[str, Any]) -> dict[str, Any]:
        """Test an indexer configuration."""
        return await self.post("indexer/test", json=indexer_data)

    async def test_all_indexers(self) -> list[dict[str, Any]]:
        """Test all configured indexers."""
        return await self.post("indexer/testall")

    # Search
    async def search(
        self,
        query: str,
        indexer_ids: Optional[list[int]] = None,
        categories: Optional[list[int]] = None,
        type: str = "search"
    ) -> list[dict[str, Any]]:
        """
        Search for releases across indexers.

        Args:
            query: Search query
            indexer_ids: List of indexer IDs to search (None for all)
            categories: List of category IDs to filter
            type: Search type (search, tvsearch, movie)

        Returns:
            List of release results
        """
        params = {"query": query, "type": type}
        if indexer_ids:
            params["indexerIds"] = ",".join(map(str, indexer_ids))
        if categories:
            params["categories"] = ",".join(map(str, categories))

        return await self.get("search", params=params)

    # Applications (Sonarr, Radarr, etc.)
    async def get_applications(self) -> list[dict[str, Any]]:
        """Get all connected applications."""
        return await self.get("applications")

    async def get_application(self, app_id: int) -> dict[str, Any]:
        """Get a specific application by ID."""
        return await self.get(f"applications/{app_id}")

    async def add_application(self, app_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new application connection."""
        return await self.post("applications", json=app_data)

    async def update_application(self, app_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing application connection."""
        return await self.put("applications", json=app_data)

    async def delete_application(self, app_id: int) -> None:
        """Delete an application connection."""
        await self.delete(f"applications/{app_id}")

    async def test_application(self, app_data: dict[str, Any]) -> dict[str, Any]:
        """Test an application connection."""
        return await self.post("applications/test", json=app_data)

    async def sync_application(self, app_id: int) -> dict[str, Any]:
        """Sync indexers to a specific application."""
        return await self.post(
            "command",
            json={"name": "ApplicationSync", "applicationId": app_id}
        )

    async def sync_all_applications(self) -> dict[str, Any]:
        """Sync indexers to all applications."""
        return await self.post(
            "command",
            json={"name": "ApplicationSync"}
        )

    # Tags
    async def get_tags(self) -> list[dict[str, Any]]:
        """Get all tags."""
        return await self.get("tag")

    async def create_tag(self, label: str) -> dict[str, Any]:
        """Create a new tag."""
        return await self.post("tag", json={"label": label})

    async def delete_tag(self, tag_id: int) -> None:
        """Delete a tag."""
        await self.delete(f"tag/{tag_id}")

    # History
    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        indexer_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> dict[str, Any]:
        """Get indexer query history."""
        params = {"page": page, "pageSize": page_size}
        if indexer_id:
            params["indexerId"] = indexer_id
        if event_type:
            params["eventType"] = event_type
        return await self.get("history", params=params)

    # Statistics
    async def get_indexer_stats(self) -> dict[str, Any]:
        """Get statistics for all indexers."""
        return await self.get("indexerstats")

    # Download Clients
    async def get_download_clients(self) -> list[dict[str, Any]]:
        """Get all configured download clients."""
        return await self.get("downloadclient")

    async def add_download_client(
        self,
        client_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new download client."""
        return await self.post("downloadclient", json=client_data)

    async def update_download_client(
        self,
        client_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a download client."""
        return await self.put("downloadclient", json=client_data)

    async def delete_download_client(self, client_id: int) -> None:
        """Delete a download client."""
        await self.delete(f"downloadclient/{client_id}")

    async def test_download_client(
        self,
        client_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Test a download client configuration."""
        return await self.post("downloadclient/test", json=client_data)

    # Notifications
    async def get_notifications(self) -> list[dict[str, Any]]:
        """Get all notification configurations."""
        return await self.get("notification")

    async def add_notification(
        self,
        notification_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new notification."""
        return await self.post("notification", json=notification_data)

    async def update_notification(
        self,
        notification_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a notification."""
        return await self.put("notification", json=notification_data)

    async def delete_notification(self, notification_id: int) -> None:
        """Delete a notification."""
        await self.delete(f"notification/{notification_id}")

    async def test_notification(
        self,
        notification_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Test a notification configuration."""
        return await self.post("notification/test", json=notification_data)

    # Config
    async def get_config(self, section: str) -> dict[str, Any]:
        """Get configuration for a specific section."""
        return await self.get(f"config/{section}")

    async def update_config(
        self,
        section: str,
        config_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update configuration for a specific section."""
        return await self.put(f"config/{section}", json=config_data)
