"""Tests for intent router."""

import pytest
from arr_suite_mcp.routers import IntentRouter
from arr_suite_mcp.routers.intent_router import ArrService, OperationType


class TestIntentRouter:
    """Test cases for the IntentRouter."""

    @pytest.fixture
    def router(self):
        """Create a router instance."""
        return IntentRouter()

    def test_parse_tv_show_add(self, router):
        """Test parsing TV show addition requests."""
        intent = router.parse_intent("Add Breaking Bad to my TV shows")

        assert intent.service == ArrService.SONARR
        assert intent.operation == OperationType.ADD
        assert "Breaking Bad" in intent.context.get("title", "")

    def test_parse_movie_search(self, router):
        """Test parsing movie search requests."""
        intent = router.parse_intent("Search for the movie The Matrix")

        assert intent.service == ArrService.RADARR
        assert intent.operation == OperationType.SEARCH
        assert "Matrix" in intent.context.get("title", "")

    def test_parse_indexer_list(self, router):
        """Test parsing indexer listing requests."""
        intent = router.parse_intent("Show all indexers")

        assert intent.service == ArrService.PROWLARR
        assert intent.operation == OperationType.LIST

    def test_parse_subtitle_download(self, router):
        """Test parsing subtitle download requests."""
        intent = router.parse_intent("Download English subtitles for Dune")

        assert intent.service == ArrService.BAZARR
        assert intent.operation == OperationType.DOWNLOAD
        assert "Dune" in intent.context.get("title", "")

    def test_parse_media_request(self, router):
        """Test parsing media request."""
        intent = router.parse_intent("Request Inception")

        assert intent.service == ArrService.OVERSEERR
        assert intent.operation == OperationType.REQUEST
        assert "Inception" in intent.context.get("title", "")

    def test_parse_with_year(self, router):
        """Test parsing queries with year."""
        intent = router.parse_intent("Add The Matrix from 1999")

        assert "1999" in intent.context.get("year", "")

    def test_parse_with_quality(self, router):
        """Test parsing queries with quality."""
        intent = router.parse_intent("Add Dune in 4K")

        assert intent.context.get("is_4k") is True

    def test_parse_season_episode(self, router):
        """Test parsing season and episode numbers."""
        intent = router.parse_intent("Get Breaking Bad season 5 episode 14")

        assert "5" in intent.context.get("season", "")
        assert "14" in intent.context.get("episode", "")

    def test_route_method(self, router):
        """Test the route convenience method."""
        service, operation, context = router.route("Add the show The Office")

        assert service == ArrService.SONARR
        assert operation == OperationType.ADD
        assert "Office" in context.get("title", "")

    def test_explain_intent(self, router):
        """Test intent explanation."""
        explanation = router.explain_intent("Search for movies from 2023")

        assert "radarr" in explanation.lower()
        assert "search" in explanation.lower()
        assert "2023" in explanation

    def test_generic_search_without_media_type_goes_to_overseerr(self, router):
        """Without a movie/TV keyword the router can't know the type; Overseerr searches both."""
        intent = router.parse_intent("Search for The Matrix")

        assert intent.service == ArrService.OVERSEERR
        assert intent.operation == OperationType.SEARCH
        assert intent.context.get("title") == "The Matrix"

    def test_verbs_are_not_service_keywords(self, router):
        """'show' as a verb must not route to Sonarr, and keywords match whole words only."""
        assert router.parse_intent("Show all indexers").service == ArrService.PROWLARR
        assert router.parse_intent("Show me the subtitle settings").service == ArrService.BAZARR

    def test_title_strips_trailing_qualifiers(self, router):
        """Year, quality, season and destination phrases are not part of the title."""
        assert router.parse_intent("Add The Matrix from 1999").context["title"] == "The Matrix"
        assert router.parse_intent("Add Dune in 4K").context["title"] == "Dune"
        assert router.parse_intent("Get Breaking Bad season 5 episode 14").context["title"] == "Breaking Bad"

    def test_season_episode_shorthand(self, router):
        """S05E14 shorthand is parsed; stray 's' + digits elsewhere is not."""
        ctx = router.parse_intent("Get Breaking Bad S05E14").context
        assert ctx.get("season") == "05" and ctx.get("episode") == "14"
        assert "season" not in router.parse_intent("Add Ocean's 11").context
