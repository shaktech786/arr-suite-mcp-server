"""Main MCP server implementation for arr suite."""

import logging
import asyncio
from typing import Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .config import ArrSuiteConfig
from .clients import (
    SonarrClient,
    RadarrClient,
    ProwlarrClient,
    BazarrClient,
    OverseerrClient,
    PlexClient,
    ArrClientError
)
from .routers import IntentRouter, ArrIntent
from .routers.intent_router import ArrService, OperationType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArrSuiteMCPServer:
    """MCP Server for the arr suite with intelligent routing."""

    def __init__(self, config: Optional[ArrSuiteConfig] = None):
        """Initialize the MCP server."""
        self.config = config or ArrSuiteConfig()
        self.server = Server("arr-suite-mcp")
        self.router = IntentRouter()

        # Initialize clients
        self.clients: dict[str, Any] = {}
        self._initialize_clients()

        # Register MCP handlers
        self._register_handlers()

        logger.info(f"Arr Suite MCP Server initialized with services: {self.config.enabled_services}")

    def _initialize_clients(self) -> None:
        """Initialize API clients for enabled services."""
        if self.config.sonarr and self.config.sonarr.api_key:
            self.clients["sonarr"] = SonarrClient(
                base_url=self.config.sonarr.base_url,
                api_key=self.config.sonarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.radarr and self.config.radarr.api_key:
            self.clients["radarr"] = RadarrClient(
                base_url=self.config.radarr.base_url,
                api_key=self.config.radarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.prowlarr and self.config.prowlarr.api_key:
            self.clients["prowlarr"] = ProwlarrClient(
                base_url=self.config.prowlarr.base_url,
                api_key=self.config.prowlarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.bazarr and self.config.bazarr.api_key:
            self.clients["bazarr"] = BazarrClient(
                base_url=self.config.bazarr.base_url,
                api_key=self.config.bazarr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.overseerr and self.config.overseerr.api_key:
            self.clients["overseerr"] = OverseerrClient(
                base_url=self.config.overseerr.base_url,
                api_key=self.config.overseerr.api_key,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

        if self.config.plex and self.config.plex.token:
            self.clients["plex"] = PlexClient(
                base_url=self.config.plex.base_url,
                token=self.config.plex.token,
                timeout=self.config.request_timeout,
                max_retries=self.config.max_retries
            )

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available MCP tools."""
            tools = [
                Tool(
                    name="arr_execute",
                    description=(
                        "Execute arr suite operations using natural language. "
                        "Intelligently routes to the correct service (Sonarr, Radarr, "
                        "Prowlarr, Bazarr, or Overseerr) based on your request. "
                        "Examples: 'add Breaking Bad', 'search for The Matrix', "
                        "'download English subtitles for Dune', 'list all indexers', "
                        "'request Inception'"
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query describing what you want to do"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="arr_explain_intent",
                    description=(
                        "Explain how a natural language query would be interpreted "
                        "and routed to arr services. Useful for understanding what "
                        "the system will do before executing."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query to explain"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="arr_list_services",
                    description="List all configured and available arr services",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="arr_get_system_status",
                    description="Get system status for all configured arr services",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]

            # Add service-specific tools
            if "sonarr" in self.clients:
                tools.extend(self._get_sonarr_tools())
            if "radarr" in self.clients:
                tools.extend(self._get_radarr_tools())
            if "prowlarr" in self.clients:
                tools.extend(self._get_prowlarr_tools())
            if "bazarr" in self.clients:
                tools.extend(self._get_bazarr_tools())
            if "overseerr" in self.clients:
                tools.extend(self._get_overseerr_tools())
            if "plex" in self.clients:
                tools.extend(self._get_plex_tools())

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                # Route to appropriate handler
                if name == "arr_execute":
                    result = await self._handle_arr_execute(arguments["query"])
                elif name == "arr_explain_intent":
                    result = self._handle_explain_intent(arguments["query"])
                elif name == "arr_list_services":
                    result = self._handle_list_services()
                elif name == "arr_get_system_status":
                    result = await self._handle_system_status()
                # Service-specific tools
                elif name.startswith("sonarr_"):
                    result = await self._handle_sonarr_tool(name, arguments)
                elif name.startswith("radarr_"):
                    result = await self._handle_radarr_tool(name, arguments)
                elif name.startswith("prowlarr_"):
                    result = await self._handle_prowlarr_tool(name, arguments)
                elif name.startswith("bazarr_"):
                    result = await self._handle_bazarr_tool(name, arguments)
                elif name.startswith("overseerr_"):
                    result = await self._handle_overseerr_tool(name, arguments)
                elif name.startswith("plex_"):
                    result = await self._handle_plex_tool(name, arguments)
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    def _get_sonarr_tools(self) -> list[Tool]:
        """Get Sonarr-specific tools."""
        return [
            Tool(
                name="sonarr_search_series",
                description="Search for TV series in Sonarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "Search term"}
                    },
                    "required": ["term"]
                }
            ),
            Tool(
                name="sonarr_add_series",
                description="Add a new TV series to Sonarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tvdb_id": {"type": "integer", "description": "TVDB ID"},
                        "quality_profile_id": {"type": "integer", "description": "Quality profile ID"},
                        "root_folder_path": {"type": "string", "description": "Root folder path"},
                        "monitored": {"type": "boolean", "description": "Monitor series", "default": True}
                    },
                    "required": ["tvdb_id", "quality_profile_id", "root_folder_path"]
                }
            ),
            Tool(
                name="sonarr_get_series",
                description="Get all series or a specific series",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "series_id": {"type": "integer", "description": "Optional series ID"}
                    }
                }
            ),
        ]

    def _get_radarr_tools(self) -> list[Tool]:
        """Get Radarr-specific tools."""
        return [
            Tool(
                name="radarr_search_movie",
                description="Search for movies in Radarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "Search term"}
                    },
                    "required": ["term"]
                }
            ),
            Tool(
                name="radarr_add_movie",
                description="Add a new movie to Radarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tmdb_id": {"type": "integer", "description": "TMDB ID"},
                        "quality_profile_id": {"type": "integer", "description": "Quality profile ID"},
                        "root_folder_path": {"type": "string", "description": "Root folder path"},
                        "monitored": {"type": "boolean", "description": "Monitor movie", "default": True}
                    },
                    "required": ["tmdb_id", "quality_profile_id", "root_folder_path"]
                }
            ),
            Tool(
                name="radarr_get_movies",
                description="Get all movies or a specific movie",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "movie_id": {"type": "integer", "description": "Optional movie ID"}
                    }
                }
            ),
        ]

    def _get_prowlarr_tools(self) -> list[Tool]:
        """Get Prowlarr-specific tools."""
        return [
            Tool(
                name="prowlarr_search",
                description="Search for releases across all indexers",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "type": {"type": "string", "description": "Search type (search, tvsearch, movie)", "default": "search"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="prowlarr_get_indexers",
                description="Get all configured indexers",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="prowlarr_sync_apps",
                description="Sync indexers to all connected applications",
                inputSchema={"type": "object", "properties": {}}
            ),
        ]

    def _get_bazarr_tools(self) -> list[Tool]:
        """Get Bazarr-specific tools."""
        return [
            Tool(
                name="bazarr_search_subtitles",
                description="Search for subtitles for a movie or episode",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or series"},
                        "media_id": {"type": "integer", "description": "Media ID"},
                        "episode_id": {"type": "integer", "description": "Episode ID (for series)"}
                    },
                    "required": ["media_type", "media_id"]
                }
            ),
            Tool(
                name="bazarr_download_subtitle",
                description="Download a subtitle",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or episode"},
                        "media_id": {"type": "integer"},
                        "language": {"type": "string", "description": "Language code (e.g., 'en')"}
                    },
                    "required": ["media_type", "media_id", "language"]
                }
            ),
        ]

    def _get_overseerr_tools(self) -> list[Tool]:
        """Get Overseerr-specific tools."""
        return [
            Tool(
                name="overseerr_search",
                description="Search for movies and TV shows",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="overseerr_request",
                description="Request a movie or TV show",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "media_type": {"type": "string", "description": "movie or tv"},
                        "media_id": {"type": "integer", "description": "TMDB/TVDB ID"},
                        "is_4k": {"type": "boolean", "default": False}
                    },
                    "required": ["media_type", "media_id"]
                }
            ),
            Tool(
                name="overseerr_get_requests",
                description="Get all media requests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "Filter (pending, approved, available)"}
                    }
                }
            ),
        ]

    async def _handle_arr_execute(self, query: str) -> dict[str, Any]:
        """Handle natural language arr execution."""
        # Parse intent
        service, operation, context = self.router.route(query)

        # Check if service is available
        if service.value not in self.clients:
            return {
                "error": f"{service.value.capitalize()} is not configured",
                "available_services": list(self.clients.keys())
            }

        client = self.clients[service.value]

        # Execute operation based on service and operation type
        try:
            result = await self._execute_operation(client, service, operation, context)
            return {
                "service": service.value,
                "operation": operation.value,
                "result": result
            }
        except ArrClientError as e:
            return {
                "error": str(e),
                "service": service.value,
                "operation": operation.value
            }

    async def _execute_operation(
        self,
        client: Any,
        service: ArrService,
        operation: OperationType,
        context: dict
    ) -> Any:
        """Execute the appropriate operation on the client."""
        # This is a simplified implementation - you would expand this
        # with more sophisticated routing logic

        if service == ArrService.SONARR:
            if operation == OperationType.SEARCH:
                term = context.get("title", "")
                return await client.lookup_series(term)
            elif operation == OperationType.LIST:
                return await client.get_all_series()

        elif service == ArrService.RADARR:
            if operation == OperationType.SEARCH:
                term = context.get("title", "")
                return await client.lookup_movie(term)
            elif operation == OperationType.LIST:
                return await client.get_all_movies()

        elif service == ArrService.PROWLARR:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search(query)
            elif operation == OperationType.LIST:
                return await client.get_all_indexers()

        elif service == ArrService.OVERSEERR:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search_media(query)
            elif operation == OperationType.REQUEST:
                # Would need more context to execute
                return {"message": "Please use overseerr_request tool with media_type and media_id"}

        elif service == ArrService.PLEX:
            if operation == OperationType.SEARCH:
                query = context.get("title", "")
                return await client.search(query)
            elif operation == OperationType.LIST or operation == OperationType.GET:
                return await client.get_libraries()
            elif operation == OperationType.SCAN:
                return {"message": "Please use plex_scan_library tool with section_id"}
            elif operation == OperationType.PLAY:
                return await client.get_sessions()
            elif operation == OperationType.REFRESH:
                return await client.get_recently_added()

        return {"message": f"Operation {operation.value} not yet implemented for {service.value}"}

    def _handle_explain_intent(self, query: str) -> dict[str, Any]:
        """Explain how a query would be interpreted."""
        explanation = self.router.explain_intent(query)
        return {"explanation": explanation}

    def _handle_list_services(self) -> dict[str, Any]:
        """List all configured services."""
        return {
            "enabled_services": self.config.enabled_services,
            "services": {
                name: {
                    "configured": name in self.clients,
                    "url": getattr(self.config, name).base_url if hasattr(self.config, name) and getattr(self.config, name) else None
                }
                for name in ["sonarr", "radarr", "prowlarr", "bazarr", "overseerr"]
            }
        }

    async def _handle_system_status(self) -> dict[str, Any]:
        """Get system status for all services."""
        statuses = {}
        for name, client in self.clients.items():
            try:
                status = await client.get_system_status()
                statuses[name] = {
                    "online": True,
                    "status": status
                }
            except Exception as e:
                statuses[name] = {
                    "online": False,
                    "error": str(e)
                }
        return statuses

    async def _handle_sonarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Sonarr-specific tools."""
        client = self.clients["sonarr"]

        if name == "sonarr_search_series":
            return await client.lookup_series(arguments["term"])
        elif name == "sonarr_add_series":
            return await client.add_series(**arguments)
        elif name == "sonarr_get_series":
            if "series_id" in arguments:
                return await client.get_series(arguments["series_id"])
            return await client.get_all_series()

    async def _handle_radarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Radarr-specific tools."""
        client = self.clients["radarr"]

        if name == "radarr_search_movie":
            return await client.lookup_movie(arguments["term"])
        elif name == "radarr_add_movie":
            return await client.add_movie(**arguments)
        elif name == "radarr_get_movies":
            if "movie_id" in arguments:
                return await client.get_movie(arguments["movie_id"])
            return await client.get_all_movies()

    async def _handle_prowlarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Prowlarr-specific tools."""
        client = self.clients["prowlarr"]

        if name == "prowlarr_search":
            return await client.search(**arguments)
        elif name == "prowlarr_get_indexers":
            return await client.get_all_indexers()
        elif name == "prowlarr_sync_apps":
            return await client.sync_all_applications()

    async def _handle_bazarr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Bazarr-specific tools."""
        client = self.clients["bazarr"]

        if name == "bazarr_search_subtitles":
            if arguments["media_type"] == "series":
                return await client.search_series_subtitles(
                    arguments["media_id"],
                    arguments.get("episode_id")
                )
            return await client.search_movie_subtitles(arguments["media_id"])
        elif name == "bazarr_download_subtitle":
            if arguments["media_type"] == "episode":
                return await client.download_series_subtitle(
                    arguments["media_id"],
                    arguments["language"]
                )
            return await client.download_movie_subtitle(
                arguments["media_id"],
                arguments["language"]
            )

    async def _handle_overseerr_tool(self, name: str, arguments: dict) -> Any:
        """Handle Overseerr-specific tools."""
        client = self.clients["overseerr"]

        if name == "overseerr_search":
            return await client.search_media(arguments["query"])
        elif name == "overseerr_request":
            return await client.create_request(**arguments)
        elif name == "overseerr_get_requests":
            return await client.get_requests(filter=arguments.get("filter"))

    def _get_plex_tools(self) -> list[Tool]:
        """Get Plex-specific tools."""
        return [
            Tool(
                name="plex_get_libraries",
                description="Get all Plex libraries",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="plex_search",
                description="Search Plex for media",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="plex_get_recently_added",
                description="Get recently added media",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max items", "default": 50}
                    }
                }
            ),
            Tool(
                name="plex_get_on_deck",
                description="Get On Deck (in progress) media",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="plex_get_sessions",
                description="Get currently playing sessions",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="plex_scan_library",
                description="Scan a Plex library for new content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "section_id": {"type": "integer", "description": "Library section ID"}
                    },
                    "required": ["section_id"]
                }
            ),
            Tool(
                name="plex_mark_watched",
                description="Mark media as watched",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "rating_key": {"type": "string", "description": "Media rating key"}
                    },
                    "required": ["rating_key"]
                }
            ),
        ]

    async def _handle_plex_tool(self, name: str, arguments: dict) -> Any:
        """Handle Plex-specific tools."""
        client = self.clients["plex"]

        if name == "plex_get_libraries":
            return await client.get_libraries()
        elif name == "plex_search":
            return await client.search(arguments["query"])
        elif name == "plex_get_recently_added":
            return await client.get_recently_added(limit=arguments.get("limit", 50))
        elif name == "plex_get_on_deck":
            return await client.get_on_deck()
        elif name == "plex_get_sessions":
            return await client.get_sessions()
        elif name == "plex_scan_library":
            return await client.scan_library(arguments["section_id"])
        elif name == "plex_mark_watched":
            return await client.mark_watched(arguments["rating_key"])

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point."""
    import sys

    # Load configuration
    config = ArrSuiteConfig()

    # Create and run server
    server = ArrSuiteMCPServer(config)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
