"""Tests for sonarr_get_calendar and radarr_get_calendar MCP tools."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from arr_suite_mcp.server import ArrSuiteMCPServer


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config.sonarr.enabled = True
    config.sonarr.url = "http://localhost:8989"
    config.sonarr.api_key = "test-key"
    config.radarr.enabled = True
    config.radarr.url = "http://localhost:7878"
    config.radarr.api_key = "test-key"
    config.prowlarr.enabled = False
    config.bazarr.enabled = False
    config.overseerr.enabled = False
    config.plex.enabled = False
    return config


@pytest.fixture
def mock_sonarr_calendar_response():
    """Sample Sonarr calendar response."""
    return [
        {
            "id": 1,
            "seriesId": 10,
            "title": "Pilot",
            "seasonNumber": 1,
            "episodeNumber": 1,
            "airDateUtc": "2026-03-15T02:00:00Z",
            "hasFile": False,
            "series": {"title": "Some Show"},
        }
    ]


@pytest.fixture
def mock_radarr_calendar_response():
    """Sample Radarr calendar response."""
    return [
        {
            "id": 1,
            "title": "Some Movie",
            "year": 2026,
            "physicalRelease": "2026-03-17T00:00:00Z",
            "digitalRelease": "2026-03-15T00:00:00Z",
            "hasFile": False,
        }
    ]


class TestSonarrGetCalendar:
    """Tests for sonarr_get_calendar tool."""

    def test_sonarr_calendar_tool_is_registered(self, mock_config):
        """Verify sonarr_get_calendar is listed as an available tool."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            tools = server._get_sonarr_tools()
            tool_names = [t.name for t in tools]
            assert "sonarr_get_calendar" in tool_names

    def test_sonarr_calendar_tool_schema(self, mock_config):
        """Verify sonarr_get_calendar has correct input schema."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            tools = server._get_sonarr_tools()
            tool = next(t for t in tools if t.name == "sonarr_get_calendar")
            props = tool.inputSchema["properties"]
            assert "start" in props
            assert "end" in props
            assert props["start"]["type"] == "string"
            assert props["end"]["type"] == "string"
            # start and end are optional — not in required
            assert "required" not in tool.inputSchema

    @pytest.mark.asyncio
    async def test_sonarr_calendar_default_dates(
        self, mock_config, mock_sonarr_calendar_response
    ):
        """Verify sonarr_get_calendar calls get_calendar with no args when none provided."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = mock_sonarr_calendar_response
            server.clients["sonarr"] = mock_client

            result = await server._handle_sonarr_tool("sonarr_get_calendar", {})

            mock_client.get_calendar.assert_called_once_with(start=None, end=None)
            assert result == mock_sonarr_calendar_response

    @pytest.mark.asyncio
    async def test_sonarr_calendar_with_date_range(
        self, mock_config, mock_sonarr_calendar_response
    ):
        """Verify sonarr_get_calendar passes start/end dates to client."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = mock_sonarr_calendar_response
            server.clients["sonarr"] = mock_client

            result = await server._handle_sonarr_tool(
                "sonarr_get_calendar",
                {"start": "2026-03-14", "end": "2026-03-21"},
            )

            mock_client.get_calendar.assert_called_once_with(
                start="2026-03-14", end="2026-03-21"
            )
            assert result == mock_sonarr_calendar_response

    @pytest.mark.asyncio
    async def test_sonarr_calendar_empty_results(self, mock_config):
        """Verify sonarr_get_calendar handles empty calendar gracefully."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = []
            server.clients["sonarr"] = mock_client

            result = await server._handle_sonarr_tool("sonarr_get_calendar", {})

            assert result == []


class TestRadarrGetCalendar:
    """Tests for radarr_get_calendar tool."""

    def test_radarr_calendar_tool_is_registered(self, mock_config):
        """Verify radarr_get_calendar is listed as an available tool."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            tools = server._get_radarr_tools()
            tool_names = [t.name for t in tools]
            assert "radarr_get_calendar" in tool_names

    def test_radarr_calendar_tool_schema(self, mock_config):
        """Verify radarr_get_calendar has correct input schema."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            tools = server._get_radarr_tools()
            tool = next(t for t in tools if t.name == "radarr_get_calendar")
            props = tool.inputSchema["properties"]
            assert "start" in props
            assert "end" in props
            assert props["start"]["type"] == "string"
            assert props["end"]["type"] == "string"
            assert "required" not in tool.inputSchema

    @pytest.mark.asyncio
    async def test_radarr_calendar_default_dates(
        self, mock_config, mock_radarr_calendar_response
    ):
        """Verify radarr_get_calendar calls get_calendar with no args when none provided."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = mock_radarr_calendar_response
            server.clients["radarr"] = mock_client

            result = await server._handle_radarr_tool("radarr_get_calendar", {})

            mock_client.get_calendar.assert_called_once_with(start=None, end=None)
            assert result == mock_radarr_calendar_response

    @pytest.mark.asyncio
    async def test_radarr_calendar_with_date_range(
        self, mock_config, mock_radarr_calendar_response
    ):
        """Verify radarr_get_calendar passes start/end dates to client."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = mock_radarr_calendar_response
            server.clients["radarr"] = mock_client

            result = await server._handle_radarr_tool(
                "radarr_get_calendar",
                {"start": "2026-03-14", "end": "2026-03-21"},
            )

            mock_client.get_calendar.assert_called_once_with(
                start="2026-03-14", end="2026-03-21"
            )
            assert result == mock_radarr_calendar_response

    @pytest.mark.asyncio
    async def test_radarr_calendar_empty_results(self, mock_config):
        """Verify radarr_get_calendar handles empty calendar gracefully."""
        with patch.object(ArrSuiteMCPServer, "_initialize_clients"):
            server = ArrSuiteMCPServer(mock_config)
            mock_client = AsyncMock()
            mock_client.get_calendar.return_value = []
            server.clients["radarr"] = mock_client

            result = await server._handle_radarr_tool("radarr_get_calendar", {})

            assert result == []
