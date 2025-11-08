"""Bazarr API client."""

from typing import Any, Optional
from .base import BaseArrClient


class BazarrClient(BaseArrClient):
    """Client for interacting with Bazarr API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30, max_retries: int = 3):
        """Initialize Bazarr client (uses v4 API)."""
        super().__init__(base_url, api_key, timeout, max_retries)
        self._api_version = "v4"  # Bazarr uses v4

    @property
    def service_name(self) -> str:
        return "Bazarr"

    # Series Subtitles
    async def get_series(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Get all series managed by Bazarr."""
        return await self.get(
            "series",
            params={"page": page, "pageSize": page_size}
        )

    async def get_series_subtitles(self, series_id: int) -> dict[str, Any]:
        """Get subtitle information for a specific series."""
        return await self.get(f"series/{series_id}")

    async def get_episode_subtitles(self, episode_id: int) -> dict[str, Any]:
        """Get subtitle information for a specific episode."""
        return await self.get(f"episodes/{episode_id}")

    async def search_series_subtitles(
        self,
        series_id: int,
        episode_id: Optional[int] = None
    ) -> dict[str, Any]:
        """Search for subtitles for a series or episode."""
        if episode_id:
            return await self.post(
                "episodes/search",
                json={"episodeId": episode_id}
            )
        return await self.post(
            "series/search",
            json={"seriesId": series_id}
        )

    async def download_series_subtitle(
        self,
        episode_id: int,
        language: str,
        forced: bool = False,
        hi: bool = False
    ) -> dict[str, Any]:
        """Download a subtitle for an episode."""
        return await self.post(
            "episodes/subtitles",
            json={
                "episodeId": episode_id,
                "language": language,
                "forced": forced,
                "hi": hi
            }
        )

    # Movie Subtitles
    async def get_movies(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Get all movies managed by Bazarr."""
        return await self.get(
            "movies",
            params={"page": page, "pageSize": page_size}
        )

    async def get_movie_subtitles(self, movie_id: int) -> dict[str, Any]:
        """Get subtitle information for a specific movie."""
        return await self.get(f"movies/{movie_id}")

    async def search_movie_subtitles(self, movie_id: int) -> dict[str, Any]:
        """Search for subtitles for a movie."""
        return await self.post(
            "movies/search",
            json={"movieId": movie_id}
        )

    async def download_movie_subtitle(
        self,
        movie_id: int,
        language: str,
        forced: bool = False,
        hi: bool = False
    ) -> dict[str, Any]:
        """Download a subtitle for a movie."""
        return await self.post(
            "movies/subtitles",
            json={
                "movieId": movie_id,
                "language": language,
                "forced": forced,
                "hi": hi
            }
        )

    # Subtitle History
    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Get subtitle download history."""
        return await self.get(
            "history",
            params={"page": page, "pageSize": page_size}
        )

    # Languages
    async def get_languages(self) -> list[dict[str, Any]]:
        """Get all available subtitle languages."""
        return await self.get("languages")

    async def get_enabled_languages(self) -> dict[str, Any]:
        """Get currently enabled subtitle languages."""
        return await self.get("languages/enabled")

    # Providers
    async def get_providers(self) -> list[dict[str, Any]]:
        """Get all subtitle providers."""
        return await self.get("providers")

    async def get_enabled_providers(self) -> list[dict[str, Any]]:
        """Get enabled subtitle providers."""
        return await self.get("providers/enabled")

    async def test_provider(self, provider_name: str) -> dict[str, Any]:
        """Test a subtitle provider."""
        return await self.post(
            "providers/test",
            json={"provider": provider_name}
        )

    # System
    async def get_system_status(self) -> dict[str, Any]:
        """Get Bazarr system status."""
        return await self.get("system/status")

    async def get_system_health(self) -> list[dict[str, Any]]:
        """Get system health issues."""
        return await self.get("system/health")

    async def get_system_logs(
        self,
        lines: int = 50
    ) -> list[dict[str, Any]]:
        """Get system logs."""
        return await self.get("system/logs", params={"lines": lines})

    # Config
    async def get_settings(self) -> dict[str, Any]:
        """Get Bazarr settings."""
        return await self.get("system/settings")

    async def update_settings(
        self,
        settings_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update Bazarr settings."""
        return await self.post("system/settings", json=settings_data)

    # Wanted
    async def get_wanted_series(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Get series episodes with wanted/missing subtitles."""
        return await self.get(
            "episodes/wanted",
            params={"page": page, "pageSize": page_size}
        )

    async def get_wanted_movies(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict[str, Any]:
        """Get movies with wanted/missing subtitles."""
        return await self.get(
            "movies/wanted",
            params={"page": page, "pageSize": page_size}
        )

    # Blacklist
    async def get_blacklist(self) -> list[dict[str, Any]]:
        """Get blacklisted subtitles."""
        return await self.get("blacklist")

    async def add_to_blacklist(
        self,
        subtitle_id: str,
        media_type: str
    ) -> dict[str, Any]:
        """Add a subtitle to blacklist."""
        return await self.post(
            "blacklist",
            json={"subtitleId": subtitle_id, "mediaType": media_type}
        )

    async def remove_from_blacklist(self, blacklist_id: int) -> None:
        """Remove a subtitle from blacklist."""
        await self.delete(f"blacklist/{blacklist_id}")
