"""Overseerr API client."""

from typing import Any, Optional
from .base import BaseArrClient


class OverseerrClient(BaseArrClient):
    """Client for interacting with Overseerr API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, max_retries: int = 3):
        """Initialize Overseerr client (uses v1 API)."""
        super().__init__(base_url, api_key, timeout, max_retries)
        self._api_version = "v1"  # Overseerr uses v1

    @property
    def service_name(self) -> str:
        return "Overseerr"

    # Requests
    async def get_requests(
        self,
        take: int = 20,
        skip: int = 0,
        filter: Optional[str] = None,
        sort: str = "added"
    ) -> dict[str, Any]:
        """
        Get media requests.

        Args:
            take: Number of requests to return
            skip: Number of requests to skip
            filter: Filter requests (available, pending, processing, approved, declined)
            sort: Sort order (added, modified)

        Returns:
            Paginated request results
        """
        params = {"take": take, "skip": skip, "sort": sort}
        if filter:
            params["filter"] = filter
        return await self.get("request", params=params)

    async def get_request(self, request_id: int) -> dict[str, Any]:
        """Get a specific request by ID."""
        return await self.get(f"request/{request_id}")

    async def create_request(
        self,
        media_type: str,
        media_id: int,
        seasons: Optional[list[int]] = None,
        is_4k: bool = False
    ) -> dict[str, Any]:
        """
        Create a new media request.

        Args:
            media_type: Type of media (movie or tv)
            media_id: TMDB/TVDB ID of the media
            seasons: List of season numbers (for TV shows)
            is_4k: Request 4K quality

        Returns:
            Created request data
        """
        request_data = {
            "mediaType": media_type,
            "mediaId": media_id,
            "is4k": is_4k
        }
        if seasons and media_type == "tv":
            request_data["seasons"] = seasons

        return await self.post("request", json=request_data)

    async def update_request(
        self,
        request_id: int,
        status: str
    ) -> dict[str, Any]:
        """
        Update a request status.

        Args:
            request_id: Request ID
            status: New status (approve or decline)

        Returns:
            Updated request data
        """
        return await self.post(f"request/{request_id}/{status}")

    async def delete_request(self, request_id: int) -> None:
        """Delete a request."""
        await self.delete(f"request/{request_id}")

    async def approve_request(self, request_id: int) -> dict[str, Any]:
        """Approve a pending request."""
        return await self.update_request(request_id, "approve")

    async def decline_request(self, request_id: int) -> dict[str, Any]:
        """Decline a pending request."""
        return await self.update_request(request_id, "decline")

    # Media
    async def get_media(self, media_id: int) -> dict[str, Any]:
        """Get media information by ID."""
        return await self.get(f"media/{media_id}")

    async def search_media(
        self,
        query: str,
        page: int = 1,
        language: str = "en"
    ) -> dict[str, Any]:
        """
        Search for media (movies and TV shows).

        Args:
            query: Search query
            page: Page number
            language: Language code

        Returns:
            Search results
        """
        return await self.get(
            "search",
            params={"query": query, "page": page, "language": language}
        )

    async def discover_movies(
        self,
        page: int = 1,
        language: str = "en",
        genre: Optional[int] = None,
        sort_by: str = "popularity.desc"
    ) -> dict[str, Any]:
        """Discover movies."""
        params = {"page": page, "language": language, "sortBy": sort_by}
        if genre:
            params["genre"] = genre
        return await self.get("discover/movies", params=params)

    async def discover_tv(
        self,
        page: int = 1,
        language: str = "en",
        genre: Optional[int] = None,
        sort_by: str = "popularity.desc"
    ) -> dict[str, Any]:
        """Discover TV shows."""
        params = {"page": page, "language": language, "sortBy": sort_by}
        if genre:
            params["genre"] = genre
        return await self.get("discover/tv", params=params)

    async def get_trending_movies(
        self,
        page: int = 1,
        language: str = "en"
    ) -> dict[str, Any]:
        """Get trending movies."""
        return await self.get(
            "discover/movies/trending",
            params={"page": page, "language": language}
        )

    async def get_trending_tv(
        self,
        page: int = 1,
        language: str = "en"
    ) -> dict[str, Any]:
        """Get trending TV shows."""
        return await self.get(
            "discover/tv/trending",
            params={"page": page, "language": language}
        )

    # Users
    async def get_users(
        self,
        take: int = 20,
        skip: int = 0
    ) -> dict[str, Any]:
        """Get all users."""
        return await self.get("user", params={"take": take, "skip": skip})

    async def get_user(self, user_id: int) -> dict[str, Any]:
        """Get a specific user by ID."""
        return await self.get(f"user/{user_id}")

    async def create_user(
        self,
        email: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        permissions: int = 0
    ) -> dict[str, Any]:
        """Create a new local user."""
        user_data = {"email": email, "permissions": permissions}
        if username:
            user_data["username"] = username
        if password:
            user_data["password"] = password
        return await self.post("user", json=user_data)

    async def update_user(
        self,
        user_id: int,
        user_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a user."""
        return await self.put(f"user/{user_id}", json=user_data)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user."""
        await self.delete(f"user/{user_id}")

    async def get_current_user(self) -> dict[str, Any]:
        """Get currently authenticated user."""
        return await self.get("auth/me")

    # Settings
    async def get_settings(self) -> dict[str, Any]:
        """Get all Overseerr settings."""
        return await self.get("settings/main")

    async def update_settings(
        self,
        settings_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update Overseerr settings."""
        return await self.post("settings/main", json=settings_data)

    async def get_plex_settings(self) -> dict[str, Any]:
        """Get Plex settings."""
        return await self.get("settings/plex")

    async def update_plex_settings(
        self,
        settings_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update Plex settings."""
        return await self.post("settings/plex", json=settings_data)

    async def get_radarr_settings(self) -> list[dict[str, Any]]:
        """Get all Radarr server configurations."""
        return await self.get("settings/radarr")

    async def add_radarr_server(
        self,
        server_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new Radarr server."""
        return await self.post("settings/radarr", json=server_data)

    async def update_radarr_server(
        self,
        server_id: int,
        server_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a Radarr server configuration."""
        return await self.put(f"settings/radarr/{server_id}", json=server_data)

    async def delete_radarr_server(self, server_id: int) -> None:
        """Delete a Radarr server configuration."""
        await self.delete(f"settings/radarr/{server_id}")

    async def get_sonarr_settings(self) -> list[dict[str, Any]]:
        """Get all Sonarr server configurations."""
        return await self.get("settings/sonarr")

    async def add_sonarr_server(
        self,
        server_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new Sonarr server."""
        return await self.post("settings/sonarr", json=server_data)

    async def update_sonarr_server(
        self,
        server_id: int,
        server_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a Sonarr server configuration."""
        return await self.put(f"settings/sonarr/{server_id}", json=server_data)

    async def delete_sonarr_server(self, server_id: int) -> None:
        """Delete a Sonarr server configuration."""
        await self.delete(f"settings/sonarr/{server_id}")

    # System
    async def get_status(self) -> dict[str, Any]:
        """Get Overseerr system status."""
        return await self.get("status")

    async def get_system_health(self) -> dict[str, Any]:
        """Get system health information."""
        return await self.get("status/health")

    # Issues
    async def get_issues(
        self,
        take: int = 20,
        skip: int = 0,
        filter: Optional[str] = None
    ) -> dict[str, Any]:
        """Get reported issues."""
        params = {"take": take, "skip": skip}
        if filter:
            params["filter"] = filter
        return await self.get("issue", params=params)

    async def get_issue(self, issue_id: int) -> dict[str, Any]:
        """Get a specific issue by ID."""
        return await self.get(f"issue/{issue_id}")

    async def create_issue(
        self,
        media_type: str,
        media_id: int,
        issue_type: int,
        message: str
    ) -> dict[str, Any]:
        """Create a new issue."""
        return await self.post(
            "issue",
            json={
                "mediaType": media_type,
                "mediaId": media_id,
                "issueType": issue_type,
                "message": message
            }
        )

    async def update_issue_status(
        self,
        issue_id: int,
        status: str
    ) -> dict[str, Any]:
        """Update an issue status (open, resolved)."""
        return await self.post(f"issue/{issue_id}/{status}")
