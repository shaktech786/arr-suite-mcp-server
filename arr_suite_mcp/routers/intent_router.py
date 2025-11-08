"""Intelligent intent-based routing for arr suite operations."""

import re
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class ArrService(Enum):
    """Available arr services."""
    SONARR = "sonarr"
    RADARR = "radarr"
    PROWLARR = "prowlarr"
    BAZARR = "bazarr"
    OVERSEERR = "overseerr"
    PLEX = "plex"


class OperationType(Enum):
    """Types of operations that can be performed."""
    SEARCH = "search"
    ADD = "add"
    DELETE = "delete"
    UPDATE = "update"
    LIST = "list"
    GET = "get"
    CONFIGURE = "configure"
    MONITOR = "monitor"
    DOWNLOAD = "download"
    REQUEST = "request"
    APPROVE = "approve"
    SYNC = "sync"
    BACKUP = "backup"
    PLAY = "play"
    SCAN = "scan"
    REFRESH = "refresh"
    WATCH = "watch"


@dataclass
class ArrIntent:
    """Represents a parsed user intent."""
    service: ArrService
    operation: OperationType
    confidence: float
    context: dict[str, any]


class IntentRouter:
    """
    Intelligent router that analyzes natural language to determine
    which arr service and operation to use.
    """

    # Keywords that indicate specific services
    SERVICE_KEYWORDS = {
        ArrService.SONARR: [
            "tv", "show", "series", "episode", "season", "sonarr",
            "television", "tvdb", "anime"
        ],
        ArrService.RADARR: [
            "movie", "film", "radarr", "tmdb", "collection", "cinema"
        ],
        ArrService.PROWLARR: [
            "indexer", "prowlarr", "tracker", "search engine",
            "torrent site", "usenet"
        ],
        ArrService.BAZARR: [
            "subtitle", "subs", "caption", "bazarr", "language",
            "translation"
        ],
        ArrService.OVERSEERR: [
            "request", "overseerr", "approve", "decline", "user",
            "discover", "trending"
        ],
        ArrService.PLEX: [
            "plex", "library", "libraries", "playing", "sessions",
            "watch", "watched", "on deck", "recently added", "playlist",
            "collection", "transcode", "stream", "server", "media server"
        ]
    }

    # Keywords that indicate specific operations
    OPERATION_KEYWORDS = {
        OperationType.SEARCH: [
            "search", "find", "lookup", "query", "locate"
        ],
        OperationType.ADD: [
            "add", "create", "new", "insert", "import"
        ],
        OperationType.DELETE: [
            "delete", "remove", "unmonitor", "destroy"
        ],
        OperationType.UPDATE: [
            "update", "modify", "change", "edit", "set"
        ],
        OperationType.LIST: [
            "list", "show all", "get all", "display", "view"
        ],
        OperationType.GET: [
            "get", "retrieve", "fetch", "show", "details"
        ],
        OperationType.CONFIGURE: [
            "configure", "config", "settings", "setup", "customize"
        ],
        OperationType.MONITOR: [
            "monitor", "watch", "track", "follow"
        ],
        OperationType.DOWNLOAD: [
            "download", "grab", "get subtitle", "fetch subtitle"
        ],
        OperationType.REQUEST: [
            "request", "want", "need", "ask for"
        ],
        OperationType.APPROVE: [
            "approve", "accept", "decline", "reject"
        ],
        OperationType.SYNC: [
            "sync", "synchronize", "update apps"
        ],
        OperationType.BACKUP: [
            "backup", "save", "export database"
        ],
        OperationType.PLAY: [
            "play", "playing", "stream", "streaming"
        ],
        OperationType.SCAN: [
            "scan", "analyze", "index"
        ],
        OperationType.REFRESH: [
            "refresh", "reload", "update library"
        ],
        OperationType.WATCH: [
            "mark watched", "mark as watched", "scrobble"
        ]
    }

    # Context patterns for extracting additional information
    CONTEXT_PATTERNS = {
        "title": [
            r"(?:titled?|named?|called)\s+['\"]([^'\"]+)['\"]",
            r"['\"]([^'\"]+)['\"]",
            r"(?:movie|show|series)\s+([A-Z][^\.,;]+)"
        ],
        "year": [
            r"\b(19\d{2}|20\d{2})\b"
        ],
        "season": [
            r"season\s+(\d+)",
            r"s(\d+)"
        ],
        "episode": [
            r"episode\s+(\d+)",
            r"e(\d+)"
        ],
        "quality": [
            r"(?:in\s+)?(\d+[kp]|4k|1080p|720p|sd|hd|uhd)",
        ],
        "language": [
            r"(?:in\s+)?(\w+)\s+(?:language|subtitle|subs?)"
        ]
    }

    def __init__(self):
        """Initialize the intent router."""
        pass

    def parse_intent(self, query: str) -> ArrIntent:
        """
        Parse natural language query to determine intent.

        Args:
            query: Natural language query from user

        Returns:
            ArrIntent object with service, operation, and context

        Examples:
            "Add Breaking Bad to my TV shows" -> (SONARR, ADD, {...})
            "Search for The Matrix" -> (RADARR, SEARCH, {title: "The Matrix"})
            "Download English subtitles for episode 3" -> (BAZARR, DOWNLOAD, {...})
            "Show all indexers" -> (PROWLARR, LIST, {})
            "Request Dune" -> (OVERSEERR, REQUEST, {title: "Dune"})
        """
        query_lower = query.lower()

        # Determine service
        service, service_confidence = self._identify_service(query_lower)

        # Determine operation
        operation, op_confidence = self._identify_operation(query_lower, service)

        # Extract context
        context = self._extract_context(query)

        # Calculate overall confidence
        confidence = (service_confidence + op_confidence) / 2

        return ArrIntent(
            service=service,
            operation=operation,
            confidence=confidence,
            context=context
        )

    def _identify_service(self, query: str) -> tuple[ArrService, float]:
        """Identify which arr service to use based on keywords."""
        scores = {service: 0.0 for service in ArrService}

        for service, keywords in self.SERVICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    # Longer keywords get higher weight
                    weight = len(keyword.split()) * 0.2 + 1.0
                    scores[service] += weight

        # Determine best match
        if all(score == 0 for score in scores.values()):
            # Default to Overseerr for generic requests
            return ArrService.OVERSEERR, 0.3

        max_service = max(scores, key=scores.get)
        max_score = scores[max_service]

        # Normalize confidence to 0-1
        confidence = min(max_score / 3.0, 1.0)

        return max_service, confidence

    def _identify_operation(
        self,
        query: str,
        service: ArrService
    ) -> tuple[OperationType, float]:
        """Identify which operation to perform."""
        scores = {op: 0.0 for op in OperationType}

        for operation, keywords in self.OPERATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    weight = len(keyword.split()) * 0.2 + 1.0
                    scores[operation] += weight

        # Apply service-specific defaults
        if all(score == 0 for score in scores.values()):
            # Default operations based on service
            default_ops = {
                ArrService.SONARR: OperationType.SEARCH,
                ArrService.RADARR: OperationType.SEARCH,
                ArrService.PROWLARR: OperationType.LIST,
                ArrService.BAZARR: OperationType.SEARCH,
                ArrService.OVERSEERR: OperationType.REQUEST,
                ArrService.PLEX: OperationType.GET,
            }
            return default_ops.get(service, OperationType.LIST), 0.5

        max_operation = max(scores, key=scores.get)
        max_score = scores[max_operation]

        confidence = min(max_score / 2.0, 1.0)

        return max_operation, confidence

    def _extract_context(self, query: str) -> dict[str, any]:
        """Extract contextual information from the query."""
        context = {}

        for key, patterns in self.CONTEXT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    context[key] = match.group(1)
                    break

        # Extract boolean flags
        context["monitored"] = "unmonitor" not in query.lower()
        context["search_on_add"] = "don't search" not in query.lower()

        # Extract quality preferences
        if "4k" in query.lower():
            context["is_4k"] = True

        return context

    def route(self, query: str) -> tuple[ArrService, OperationType, dict]:
        """
        Route a query to the appropriate service and operation.

        Args:
            query: Natural language query

        Returns:
            Tuple of (service, operation, context)
        """
        intent = self.parse_intent(query)
        return intent.service, intent.operation, intent.context

    def explain_intent(self, query: str) -> str:
        """
        Provide a human-readable explanation of the parsed intent.

        Args:
            query: Natural language query

        Returns:
            Explanation string
        """
        intent = self.parse_intent(query)

        explanation = (
            f"Service: {intent.service.value.capitalize()} "
            f"({intent.confidence*100:.0f}% confident)\n"
            f"Operation: {intent.operation.value.capitalize()}\n"
        )

        if intent.context:
            explanation += "Context:\n"
            for key, value in intent.context.items():
                explanation += f"  - {key}: {value}\n"

        return explanation
