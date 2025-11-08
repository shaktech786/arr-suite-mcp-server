"""Sonarr API client."""

from typing import Any, Optional
from .base import BaseArrClient


class SonarrClient(BaseArrClient):
    """Client for interacting with Sonarr API."""

    @property
    def service_name(self) -> str:
        return "Sonarr"

    # Series Management
    async def get_all_series(self) -> list[dict[str, Any]]:
        """Get all series in Sonarr."""
        return await self.get("series")

    async def get_series(self, series_id: int) -> dict[str, Any]:
        """Get a specific series by ID."""
        return await self.get(f"series/{series_id}")

    async def lookup_series(self, term: str) -> list[dict[str, Any]]:
        """Search for series by name."""
        return await self.get("series/lookup", params={"term": term})

    async def add_series(
        self,
        tvdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        search_for_missing: bool = True,
        season_folder: bool = True,
        **kwargs
    ) -> dict[str, Any]:
        """
        Add a new series to Sonarr.

        Args:
            tvdb_id: TVDB ID of the series
            quality_profile_id: Quality profile to use
            root_folder_path: Root folder path for the series
            monitored: Whether to monitor the series
            search_for_missing: Whether to search for missing episodes
            season_folder: Whether to use season folders
            **kwargs: Additional series options

        Returns:
            Added series data
        """
        # First lookup the series to get full data
        lookup_results = await self.lookup_series(f"tvdb:{tvdb_id}")
        if not lookup_results:
            raise ValueError(f"Series with TVDB ID {tvdb_id} not found")

        series_data = lookup_results[0]
        series_data.update({
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
            "seasonFolder": season_folder,
            "addOptions": {
                "searchForMissingEpisodes": search_for_missing
            },
            **kwargs
        })

        return await self.post("series", json=series_data)

    async def update_series(self, series_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing series."""
        return await self.put("series", json=series_data)

    async def delete_series(
        self,
        series_id: int,
        delete_files: bool = False
    ) -> None:
        """Delete a series."""
        await self.delete(
            f"series/{series_id}",
            params={"deleteFiles": delete_files}
        )

    # Episode Management
    async def get_episodes(self, series_id: int) -> list[dict[str, Any]]:
        """Get all episodes for a series."""
        return await self.get("episode", params={"seriesId": series_id})

    async def get_episode(self, episode_id: int) -> dict[str, Any]:
        """Get a specific episode by ID."""
        return await self.get(f"episode/{episode_id}")

    async def update_episode(self, episode_data: dict[str, Any]) -> dict[str, Any]:
        """Update an episode."""
        return await self.put("episode", json=episode_data)

    async def search_episode(self, episode_id: int) -> dict[str, Any]:
        """Trigger a search for a specific episode."""
        return await self.post(
            "command",
            json={"name": "EpisodeSearch", "episodeIds": [episode_id]}
        )

    async def search_series(self, series_id: int) -> dict[str, Any]:
        """Trigger a search for all missing episodes in a series."""
        return await self.post(
            "command",
            json={"name": "SeriesSearch", "seriesId": series_id}
        )

    # Quality Profiles
    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        """Get all quality profiles."""
        return await self.get("qualityprofile")

    async def get_quality_profile(self, profile_id: int) -> dict[str, Any]:
        """Get a specific quality profile."""
        return await self.get(f"qualityprofile/{profile_id}")

    # Root Folders
    async def get_root_folders(self) -> list[dict[str, Any]]:
        """Get all root folders."""
        return await self.get("rootfolder")

    # Tags
    async def get_tags(self) -> list[dict[str, Any]]:
        """Get all tags."""
        return await self.get("tag")

    async def create_tag(self, label: str) -> dict[str, Any]:
        """Create a new tag."""
        return await self.post("tag", json={"label": label})

    # Queue
    async def get_queue(
        self,
        page: int = 1,
        page_size: int = 20,
        include_unknown_series: bool = False
    ) -> dict[str, Any]:
        """Get the download queue."""
        return await self.get(
            "queue",
            params={
                "page": page,
                "pageSize": page_size,
                "includeUnknownSeriesItems": include_unknown_series
            }
        )

    async def delete_queue_item(
        self,
        queue_id: int,
        remove_from_client: bool = True,
        blocklist: bool = False
    ) -> None:
        """Remove an item from the queue."""
        await self.delete(
            f"queue/{queue_id}",
            params={
                "removeFromClient": remove_from_client,
                "blocklist": blocklist
            }
        )

    # History
    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        series_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> dict[str, Any]:
        """Get history of downloads and imports."""
        params = {"page": page, "pageSize": page_size}
        if series_id:
            params["seriesId"] = series_id
        if event_type:
            params["eventType"] = event_type
        return await self.get("history", params=params)

    # Calendar
    async def get_calendar(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get upcoming episodes."""
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("calendar", params=params)

    # Commands
    async def refresh_series(self, series_id: int) -> dict[str, Any]:
        """Refresh series information from TVDB."""
        return await self.post(
            "command",
            json={"name": "RefreshSeries", "seriesId": series_id}
        )

    async def rescan_series(self, series_id: int) -> dict[str, Any]:
        """Rescan series files on disk."""
        return await self.post(
            "command",
            json={"name": "RescanSeries", "seriesId": series_id}
        )

    async def rename_series(self, series_id: int) -> dict[str, Any]:
        """Rename series files."""
        return await self.post(
            "command",
            json={"name": "RenameSeries", "seriesIds": [series_id]}
        )

    async def backup_database(self) -> dict[str, Any]:
        """Trigger a database backup."""
        return await self.post("command", json={"name": "Backup"})

    # Config
    async def get_config(self, section: str) -> dict[str, Any]:
        """
        Get configuration for a specific section.

        Args:
            section: Config section (e.g., 'ui', 'naming', 'mediamanagement')
        """
        return await self.get(f"config/{section}")

    async def update_config(
        self,
        section: str,
        config_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update configuration for a specific section."""
        return await self.put(f"config/{section}", json=config_data)
