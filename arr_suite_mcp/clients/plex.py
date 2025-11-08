"""Plex Media Server API client."""

from typing import Any, Optional
import httpx
from .base import ArrClientError


class PlexClient:
    """Client for interacting with Plex Media Server API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Plex client.

        Args:
            base_url: Base URL of Plex server (e.g., http://localhost:32400)
            token: Plex authentication token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    @property
    def service_name(self) -> str:
        return "Plex"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-Plex-Token": self.token,
            "Accept": "application/json"
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Any:
        """Make an HTTP request to Plex."""
        url = self._build_url(endpoint)
        headers = self._get_headers()

        # Add token to params for Plex
        if params is None:
            params = {}
        params["X-Plex-Token"] = self.token

        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )

            if response.status_code == 401:
                raise ArrClientError(f"{self.service_name}: Authentication failed. Check your token.")
            elif response.status_code == 404:
                raise ArrClientError(f"{self.service_name}: Resource not found at {endpoint}")
            elif response.status_code >= 400:
                raise ArrClientError(f"{self.service_name}: HTTP {response.status_code}")

            response.raise_for_status()

            if not response.content:
                return None

            return response.json()

        except httpx.ConnectError as e:
            if retry_count < self.max_retries:
                return await self._request(method, endpoint, params, json, retry_count + 1)
            raise ArrClientError(f"{self.service_name}: Could not connect to {self.base_url}") from e
        except httpx.TimeoutException as e:
            raise ArrClientError(f"{self.service_name}: Request timed out") from e

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json: Optional[dict[str, Any]] = None) -> Any:
        """Make a POST request."""
        return await self._request("POST", endpoint, json=json)

    async def put(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make a PUT request."""
        return await self._request("PUT", endpoint, params=params)

    async def delete(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint, params=params)

    # Server Information
    async def get_server_identity(self) -> dict[str, Any]:
        """Get server identity information."""
        return await self.get("identity")

    async def get_server_capabilities(self) -> dict[str, Any]:
        """Get server capabilities."""
        return await self.get("")

    async def get_system_accounts(self) -> dict[str, Any]:
        """Get system accounts."""
        return await self.get("accounts")

    # Library Management
    async def get_libraries(self) -> list[dict[str, Any]]:
        """Get all libraries."""
        response = await self.get("library/sections")
        return response.get("MediaContainer", {}).get("Directory", [])

    async def get_library(self, section_id: int) -> dict[str, Any]:
        """Get specific library by section ID."""
        response = await self.get(f"library/sections/{section_id}")
        return response.get("MediaContainer", {})

    async def get_library_items(
        self,
        section_id: int,
        item_type: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get all items in a library.

        Args:
            section_id: Library section ID
            item_type: Filter by type (movie, show, artist, photo)
        """
        params = {}
        if item_type:
            params["type"] = item_type

        response = await self.get(f"library/sections/{section_id}/all", params=params)
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def refresh_library(self, section_id: int) -> None:
        """Refresh a library section."""
        await self.get(f"library/sections/{section_id}/refresh")

    async def scan_library(self, section_id: int) -> None:
        """Force scan a library section."""
        await self.get(f"library/sections/{section_id}/refresh?force=1")

    async def empty_library_trash(self, section_id: int) -> None:
        """Empty trash for a library section."""
        await self.put(f"library/sections/{section_id}/emptyTrash")

    async def optimize_database(self) -> None:
        """Optimize the Plex database."""
        await self.put("library/optimize")

    async def clean_bundles(self) -> None:
        """Clean old bundles."""
        await self.put("library/clean/bundles")

    # Search
    async def search(
        self,
        query: str,
        section_id: Optional[int] = None,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Search for media.

        Args:
            query: Search query
            section_id: Limit to specific library section
            limit: Maximum results
        """
        params = {"query": query, "limit": limit}
        if section_id:
            params["sectionId"] = section_id

        response = await self.get("search", params=params)
        return response.get("MediaContainer", {}).get("Metadata", [])

    # Media Items
    async def get_metadata(self, rating_key: str) -> dict[str, Any]:
        """Get metadata for a specific item."""
        response = await self.get(f"library/metadata/{rating_key}")
        return response.get("MediaContainer", {}).get("Metadata", [{}])[0]

    async def get_children(self, rating_key: str) -> list[dict[str, Any]]:
        """Get children of an item (e.g., seasons of a show)."""
        response = await self.get(f"library/metadata/{rating_key}/children")
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def mark_watched(self, rating_key: str) -> None:
        """Mark an item as watched."""
        await self.get(f":/scrobble?key={rating_key}&identifier=com.plexapp.plugins.library")

    async def mark_unwatched(self, rating_key: str) -> None:
        """Mark an item as unwatched."""
        await self.get(f":/unscrobble?key={rating_key}&identifier=com.plexapp.plugins.library")

    async def update_metadata(
        self,
        rating_key: str,
        **fields
    ) -> dict[str, Any]:
        """
        Update metadata fields for an item.

        Args:
            rating_key: Item rating key
            **fields: Fields to update (title, summary, etc.)
        """
        return await self.put(f"library/metadata/{rating_key}", params=fields)

    async def delete_metadata(self, rating_key: str) -> None:
        """Delete an item from library."""
        await self.delete(f"library/metadata/{rating_key}")

    # Recently Added
    async def get_recently_added(
        self,
        section_id: Optional[int] = None,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get recently added items."""
        if section_id:
            response = await self.get(
                f"library/sections/{section_id}/recentlyAdded",
                params={"X-Plex-Container-Start": 0, "X-Plex-Container-Size": limit}
            )
        else:
            response = await self.get("library/recentlyAdded")

        return response.get("MediaContainer", {}).get("Metadata", [])

    async def get_on_deck(self) -> list[dict[str, Any]]:
        """Get On Deck items (in progress)."""
        response = await self.get("library/onDeck")
        return response.get("MediaContainer", {}).get("Metadata", [])

    # Playlists
    async def get_playlists(self) -> list[dict[str, Any]]:
        """Get all playlists."""
        response = await self.get("playlists")
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def get_playlist(self, playlist_id: str) -> dict[str, Any]:
        """Get specific playlist."""
        response = await self.get(f"playlists/{playlist_id}")
        return response.get("MediaContainer", {})

    async def get_playlist_items(self, playlist_id: str) -> list[dict[str, Any]]:
        """Get items in a playlist."""
        response = await self.get(f"playlists/{playlist_id}/items")
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def create_playlist(
        self,
        title: str,
        items: list[str],
        smart: bool = False
    ) -> dict[str, Any]:
        """
        Create a new playlist.

        Args:
            title: Playlist title
            items: List of rating keys
            smart: Whether it's a smart playlist
        """
        params = {
            "title": title,
            "type": "video",
            "smart": "1" if smart else "0",
            "uri": f"server://{{machineIdentifier}}/com.plexapp.plugins.library/library/metadata/{','.join(items)}"
        }
        return await self.post("playlists", params=params)

    # Sessions (Currently Playing)
    async def get_sessions(self) -> list[dict[str, Any]]:
        """Get current active sessions (what's playing)."""
        response = await self.get("status/sessions")
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def get_session_history(
        self,
        account_id: Optional[int] = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get session history (watch history)."""
        params = {"sort": "viewedAt:desc"}
        if account_id:
            params["accountID"] = account_id
        if limit:
            params["X-Plex-Container-Size"] = limit

        response = await self.get("status/sessions/history/all", params=params)
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def terminate_session(self, session_id: str, reason: str = "Terminated by admin") -> None:
        """Terminate an active session."""
        await self.delete(f"status/sessions/{session_id}", params={"reason": reason})

    # Users and Sharing
    async def get_users(self) -> list[dict[str, Any]]:
        """Get all shared users."""
        response = await self.get("accounts")
        return response.get("MediaContainer", {}).get("Account", [])

    async def get_user_servers(self, user_id: str) -> list[dict[str, Any]]:
        """Get servers shared with a user."""
        response = await self.get(f"accounts/{user_id}/servers")
        return response.get("MediaContainer", {}).get("Server", [])

    # Transcoding
    async def get_transcode_sessions(self) -> list[dict[str, Any]]:
        """Get active transcode sessions."""
        response = await self.get("transcode/sessions")
        return response.get("MediaContainer", {}).get("TranscodeSession", [])

    async def kill_transcode_session(self, session_key: str) -> None:
        """Kill a transcode session."""
        await self.delete(f"transcode/sessions/{session_key}")

    # Statistics
    async def get_server_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        response = await self.get("statistics/media")
        return response.get("MediaContainer", {})

    async def get_bandwidth_stats(
        self,
        timespan: int = 6
    ) -> dict[str, Any]:
        """
        Get bandwidth statistics.

        Args:
            timespan: Timespan in months
        """
        response = await self.get(f"statistics/bandwidth?timespan={timespan}")
        return response.get("MediaContainer", {})

    async def get_resources_stats(self) -> dict[str, Any]:
        """Get resource usage statistics."""
        response = await self.get("statistics/resources")
        return response.get("MediaContainer", {})

    # Notifications and Activities
    async def get_activities(self) -> list[dict[str, Any]]:
        """Get current background activities."""
        response = await self.get("activities")
        return response.get("MediaContainer", {}).get("Activity", [])

    async def cancel_activity(self, activity_uuid: str) -> None:
        """Cancel a background activity."""
        await self.delete(f"activities/{activity_uuid}")

    # Preferences
    async def get_preferences(self) -> list[dict[str, Any]]:
        """Get server preferences."""
        response = await self.get(":/prefs")
        return response.get("MediaContainer", {}).get("Setting", [])

    async def update_preference(self, pref_id: str, value: str) -> None:
        """Update a server preference."""
        await self.put(f":/prefs?{pref_id}={value}")

    # Butler (Scheduled Tasks)
    async def get_butler_tasks(self) -> list[dict[str, Any]]:
        """Get Butler scheduled tasks."""
        response = await self.get("butler")
        return response.get("ButlerTasks", {}).get("ButlerTask", [])

    async def start_butler_task(self, task_name: str) -> None:
        """
        Start a Butler task.

        Args:
            task_name: Task name (e.g., BackupDatabase, OptimizeDatabase, CleanOldBundles)
        """
        await self.post(f"butler/{task_name}")

    # Media Analysis
    async def analyze_media(self, rating_key: str) -> None:
        """Analyze media file (thumbnails, etc.)."""
        await self.put(f"library/metadata/{rating_key}/analyze")

    async def refresh_metadata(self, rating_key: str) -> None:
        """Refresh metadata for an item."""
        await self.put(f"library/metadata/{rating_key}/refresh")

    async def match_media(self, rating_key: str) -> None:
        """Match media to metadata."""
        await self.put(f"library/metadata/{rating_key}/match")

    # Collections
    async def get_collections(self, section_id: int) -> list[dict[str, Any]]:
        """Get collections in a library."""
        response = await self.get(f"library/sections/{section_id}/collections")
        return response.get("MediaContainer", {}).get("Metadata", [])

    async def create_collection(
        self,
        section_id: int,
        title: str,
        items: list[str]
    ) -> dict[str, Any]:
        """
        Create a new collection.

        Args:
            section_id: Library section ID
            title: Collection title
            items: List of rating keys
        """
        params = {
            "type": "1",
            "title": title,
            "smart": "0",
            "sectionId": section_id,
            "uri": f"server://{{machineIdentifier}}/com.plexapp.plugins.library/library/metadata/{','.join(items)}"
        }
        return await self.post("library/collections", params=params)

    async def add_to_collection(self, collection_key: str, rating_key: str) -> None:
        """Add an item to a collection."""
        await self.put(f"library/collections/{collection_key}/items", params={"uri": f"server://{{machineIdentifier}}/com.plexapp.plugins.library/library/metadata/{rating_key}"})

    # Webhooks
    async def test_webhook(self, url: str) -> dict[str, Any]:
        """Test a webhook URL."""
        return await self.get(":/webhook/test", params={"url": url})

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
