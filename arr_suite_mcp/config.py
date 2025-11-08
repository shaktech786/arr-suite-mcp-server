"""Configuration management for arr suite MCP server."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ArrServiceConfig(BaseSettings):
    """Base configuration for arr services."""

    host: str = Field(default="localhost", description="Service host address")
    port: int = Field(description="Service port")
    api_key: str = Field(description="Service API key")
    ssl: bool = Field(default=False, description="Use HTTPS")
    base_path: str = Field(default="", description="Base path for the service")

    @property
    def base_url(self) -> str:
        """Construct the base URL for the service."""
        protocol = "https" if self.ssl else "http"
        base = f"{protocol}://{self.host}:{self.port}"
        if self.base_path:
            base += f"/{self.base_path.strip('/')}"
        return base


class SonarrConfig(ArrServiceConfig):
    """Sonarr-specific configuration."""

    port: int = Field(default=8989)

    model_config = SettingsConfigDict(env_prefix="SONARR_")


class RadarrConfig(ArrServiceConfig):
    """Radarr-specific configuration."""

    port: int = Field(default=7878)

    model_config = SettingsConfigDict(env_prefix="RADARR_")


class ProwlarrConfig(ArrServiceConfig):
    """Prowlarr-specific configuration."""

    port: int = Field(default=9696)

    model_config = SettingsConfigDict(env_prefix="PROWLARR_")


class BazarrConfig(ArrServiceConfig):
    """Bazarr-specific configuration."""

    port: int = Field(default=6767)

    model_config = SettingsConfigDict(env_prefix="BAZARR_")


class OverseerrConfig(ArrServiceConfig):
    """Overseerr-specific configuration."""

    port: int = Field(default=5055)

    model_config = SettingsConfigDict(env_prefix="OVERSEERR_")


class JackettConfig(ArrServiceConfig):
    """Jackett-specific configuration."""

    port: int = Field(default=9117)

    model_config = SettingsConfigDict(env_prefix="JACKETT_")


class PlexConfig(BaseSettings):
    """Plex Media Server configuration."""

    host: str = Field(default="localhost", description="Plex server host address")
    port: int = Field(default=32400, description="Plex server port")
    token: str = Field(description="Plex authentication token")
    ssl: bool = Field(default=False, description="Use HTTPS")

    model_config = SettingsConfigDict(env_prefix="PLEX_")

    @property
    def base_url(self) -> str:
        """Construct the base URL for Plex."""
        protocol = "https" if self.ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"


class ArrSuiteConfig(BaseSettings):
    """Main configuration for the arr suite MCP server."""

    # Service configurations
    sonarr: Optional[SonarrConfig] = None
    radarr: Optional[RadarrConfig] = None
    prowlarr: Optional[ProwlarrConfig] = None
    bazarr: Optional[BazarrConfig] = None
    overseerr: Optional[OverseerrConfig] = None
    jackett: Optional[JackettConfig] = None
    plex: Optional[PlexConfig] = None

    # Global settings
    request_timeout: int = Field(default=30, description="API request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        """Initialize configuration, attempting to load each service."""
        super().__init__(**kwargs)

        # Try to initialize each service config from environment
        try:
            self.sonarr = SonarrConfig()
        except Exception:
            pass

        try:
            self.radarr = RadarrConfig()
        except Exception:
            pass

        try:
            self.prowlarr = ProwlarrConfig()
        except Exception:
            pass

        try:
            self.bazarr = BazarrConfig()
        except Exception:
            pass

        try:
            self.overseerr = OverseerrConfig()
        except Exception:
            pass

        try:
            self.jackett = JackettConfig()
        except Exception:
            pass

        try:
            self.plex = PlexConfig()
        except Exception:
            pass

    @property
    def enabled_services(self) -> list[str]:
        """Return list of enabled services."""
        services = []
        if self.sonarr and self.sonarr.api_key:
            services.append("sonarr")
        if self.radarr and self.radarr.api_key:
            services.append("radarr")
        if self.prowlarr and self.prowlarr.api_key:
            services.append("prowlarr")
        if self.bazarr and self.bazarr.api_key:
            services.append("bazarr")
        if self.overseerr and self.overseerr.api_key:
            services.append("overseerr")
        if self.jackett and self.jackett.api_key:
            services.append("jackett")
        if self.plex and self.plex.token:
            services.append("plex")
        return services
