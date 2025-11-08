"""Radarr API client."""

from typing import Any, Optional
from .base import BaseArrClient


class RadarrClient(BaseArrClient):
    """Client for interacting with Radarr API."""

    @property
    def service_name(self) -> str:
        return "Radarr"

    # Movie Management
    async def get_all_movies(self) -> list[dict[str, Any]]:
        """Get all movies in Radarr."""
        return await self.get("movie")

    async def get_movie(self, movie_id: int) -> dict[str, Any]:
        """Get a specific movie by ID."""
        return await self.get(f"movie/{movie_id}")

    async def lookup_movie(self, term: str) -> list[dict[str, Any]]:
        """
        Search for movies.

        Args:
            term: Search term (title or imdb:id or tmdb:id)

        Returns:
            List of matching movies
        """
        return await self.get("movie/lookup", params={"term": term})

    async def add_movie(
        self,
        tmdb_id: int,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        search_for_movie: bool = True,
        minimum_availability: str = "announced",
        **kwargs
    ) -> dict[str, Any]:
        """
        Add a new movie to Radarr.

        Args:
            tmdb_id: TMDB ID of the movie
            quality_profile_id: Quality profile to use
            root_folder_path: Root folder path for the movie
            monitored: Whether to monitor the movie
            search_for_movie: Whether to search for the movie immediately
            minimum_availability: Minimum availability (announced, inCinemas, released)
            **kwargs: Additional movie options

        Returns:
            Added movie data
        """
        # First lookup the movie to get full data
        lookup_results = await self.lookup_movie(f"tmdb:{tmdb_id}")
        if not lookup_results:
            raise ValueError(f"Movie with TMDB ID {tmdb_id} not found")

        movie_data = lookup_results[0]
        movie_data.update({
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
            "minimumAvailability": minimum_availability,
            "addOptions": {
                "searchForMovie": search_for_movie
            },
            **kwargs
        })

        return await self.post("movie", json=movie_data)

    async def update_movie(self, movie_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing movie."""
        return await self.put("movie", json=movie_data)

    async def delete_movie(
        self,
        movie_id: int,
        delete_files: bool = False,
        add_import_exclusion: bool = False
    ) -> None:
        """Delete a movie."""
        await self.delete(
            f"movie/{movie_id}",
            params={
                "deleteFiles": delete_files,
                "addImportExclusion": add_import_exclusion
            }
        )

    async def search_movie(self, movie_id: int) -> dict[str, Any]:
        """Trigger a search for a specific movie."""
        return await self.post(
            "command",
            json={"name": "MoviesSearch", "movieIds": [movie_id]}
        )

    # Collections
    async def get_collections(self) -> list[dict[str, Any]]:
        """Get all movie collections."""
        return await self.get("collection")

    async def get_collection(self, collection_id: int) -> dict[str, Any]:
        """Get a specific collection."""
        return await self.get(f"collection/{collection_id}")

    # Quality Profiles
    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        """Get all quality profiles."""
        return await self.get("qualityprofile")

    async def get_quality_profile(self, profile_id: int) -> dict[str, Any]:
        """Get a specific quality profile."""
        return await self.get(f"qualityprofile/{profile_id}")

    async def create_quality_profile(
        self,
        profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new quality profile."""
        return await self.post("qualityprofile", json=profile_data)

    async def update_quality_profile(
        self,
        profile_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a quality profile."""
        return await self.put("qualityprofile", json=profile_data)

    async def delete_quality_profile(self, profile_id: int) -> None:
        """Delete a quality profile."""
        await self.delete(f"qualityprofile/{profile_id}")

    # Root Folders
    async def get_root_folders(self) -> list[dict[str, Any]]:
        """Get all root folders."""
        return await self.get("rootfolder")

    async def add_root_folder(self, path: str) -> dict[str, Any]:
        """Add a new root folder."""
        return await self.post("rootfolder", json={"path": path})

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

    # Queue
    async def get_queue(
        self,
        page: int = 1,
        page_size: int = 20,
        include_unknown_movies: bool = False
    ) -> dict[str, Any]:
        """Get the download queue."""
        return await self.get(
            "queue",
            params={
                "page": page,
                "pageSize": page_size,
                "includeUnknownMovieItems": include_unknown_movies
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
        movie_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> dict[str, Any]:
        """Get history of downloads and imports."""
        params = {"page": page, "pageSize": page_size}
        if movie_id:
            params["movieId"] = movie_id
        if event_type:
            params["eventType"] = event_type
        return await self.get("history", params=params)

    # Calendar
    async def get_calendar(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get upcoming movies."""
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self.get("calendar", params=params)

    # Commands
    async def refresh_movie(self, movie_id: int) -> dict[str, Any]:
        """Refresh movie information from TMDB."""
        return await self.post(
            "command",
            json={"name": "RefreshMovie", "movieId": movie_id}
        )

    async def rescan_movie(self, movie_id: int) -> dict[str, Any]:
        """Rescan movie files on disk."""
        return await self.post(
            "command",
            json={"name": "RescanMovie", "movieId": movie_id}
        )

    async def rename_movie(self, movie_id: int) -> dict[str, Any]:
        """Rename movie files."""
        return await self.post(
            "command",
            json={"name": "RenameMovie", "movieIds": [movie_id]}
        )

    async def backup_database(self) -> dict[str, Any]:
        """Trigger a database backup."""
        return await self.post("command", json={"name": "Backup"})

    async def refresh_monitored_downloads(self) -> dict[str, Any]:
        """Refresh monitored downloads."""
        return await self.post(
            "command",
            json={"name": "RefreshMonitoredDownloads"}
        )

    async def rss_sync(self) -> dict[str, Any]:
        """Trigger RSS sync."""
        return await self.post("command", json={"name": "RssSync"})

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

    # Import Lists
    async def get_import_lists(self) -> list[dict[str, Any]]:
        """Get all import lists."""
        return await self.get("importlist")

    async def test_import_list(self, list_data: dict[str, Any]) -> dict[str, Any]:
        """Test an import list configuration."""
        return await self.post("importlist/test", json=list_data)

    # Notifications
    async def get_notifications(self) -> list[dict[str, Any]]:
        """Get all notification configurations."""
        return await self.get("notification")

    async def test_notification(
        self,
        notification_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Test a notification configuration."""
        return await self.post("notification/test", json=notification_data)
