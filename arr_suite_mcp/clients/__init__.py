"""API clients for arr services."""

from .base import (
    BaseArrClient,
    ArrClientError,
    ArrClientConnectionError,
    ArrClientAuthError,
    ArrClientNotFoundError
)
from .sonarr import SonarrClient
from .radarr import RadarrClient
from .prowlarr import ProwlarrClient
from .bazarr import BazarrClient
from .overseerr import OverseerrClient
from .plex import PlexClient

__all__ = [
    "BaseArrClient",
    "ArrClientError",
    "ArrClientConnectionError",
    "ArrClientAuthError",
    "ArrClientNotFoundError",
    "SonarrClient",
    "RadarrClient",
    "ProwlarrClient",
    "BazarrClient",
    "OverseerrClient",
    "PlexClient",
]
