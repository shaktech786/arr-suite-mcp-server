"""Tests for Plex collection management methods."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from arr_suite_mcp.clients.plex import PlexClient


MACHINE_ID = "abc123def456"

COLLECTION_RESPONSE = {
    "MediaContainer": {
        "Metadata": [
            {
                "ratingKey": "999",
                "title": "Test Collection",
                "type": "collection",
                "childCount": 2,
            }
        ]
    }
}

ITEMS_RESPONSE = {
    "MediaContainer": {
        "Metadata": [
            {"ratingKey": "101", "title": "The Sting", "year": 1973, "type": "movie"},
            {"ratingKey": "102", "title": "Casablanca", "year": 1942, "type": "movie"},
        ]
    }
}

IDENTITY_RESPONSE = {
    "MediaContainer": {
        "machineIdentifier": MACHINE_ID
    }
}


class TestPlexCollections:
    """Test cases for Plex collection management methods."""

    @pytest.fixture
    def client(self):
        """Create a PlexClient with mocked HTTP."""
        return PlexClient("http://localhost:32400", "fake-token")

    @pytest.fixture
    def client_with_machine_id(self, client):
        """Create a PlexClient with machine identifier pre-cached."""
        client._machine_identifier = MACHINE_ID
        return client

    async def test_get_collections(self, client_with_machine_id):
        """Test listing collections in a library section."""
        client_with_machine_id._request = AsyncMock(return_value={
            "MediaContainer": {
                "Metadata": [
                    {"ratingKey": "999", "title": "Test Collection", "childCount": 2},
                    {"ratingKey": "998", "title": "Another Collection", "childCount": 5},
                ]
            }
        })

        result = await client_with_machine_id.get_collections(4)

        assert len(result) == 2
        assert result[0]["title"] == "Test Collection"
        assert result[1]["childCount"] == 5
        client_with_machine_id._request.assert_called_once_with(
            "GET", "library/sections/4/all", params={"type": "18"}
        )

    async def test_get_collection_items(self, client_with_machine_id):
        """Test retrieving items from a collection."""
        client_with_machine_id._request = AsyncMock(return_value=ITEMS_RESPONSE)

        result = await client_with_machine_id.get_collection_items("999")

        assert len(result) == 2
        assert result[0]["title"] == "The Sting"
        assert result[1]["year"] == 1942
        client_with_machine_id._request.assert_called_once_with(
            "GET", "library/collections/999/children", params=None
        )

    async def test_create_collection(self, client_with_machine_id):
        """Test creating a new collection with items."""
        client_with_machine_id._request = AsyncMock(return_value=COLLECTION_RESPONSE)

        result = await client_with_machine_id.create_collection(4, "Test Collection", ["101", "102"])

        assert result["ratingKey"] == "999"
        assert result["title"] == "Test Collection"

        call_args = client_with_machine_id._request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "library/collections"
        params = call_args[1]["params"]
        assert params["title"] == "Test Collection"
        assert params["sectionId"] == "4"
        assert params["smart"] == "0"
        assert MACHINE_ID in params["uri"]
        assert "101" in params["uri"]
        assert "102" in params["uri"]

    async def test_create_collection_returns_empty_on_no_metadata(self, client_with_machine_id):
        """Test create_collection returns empty dict when response has no Metadata."""
        client_with_machine_id._request = AsyncMock(return_value={"MediaContainer": {}})

        result = await client_with_machine_id.create_collection(4, "Empty", ["101"])

        assert result == {}

    async def test_add_to_collection(self, client_with_machine_id):
        """Test adding items to an existing collection."""
        client_with_machine_id._request = AsyncMock(return_value=None)

        await client_with_machine_id.add_to_collection("999", ["103", "104"])

        call_args = client_with_machine_id._request.call_args
        assert call_args[0][0] == "PUT"
        assert "library/collections/999/items" in call_args[0][1]
        assert MACHINE_ID in call_args[1]["params"]["uri"]
        assert "103" in call_args[1]["params"]["uri"]
        assert "104" in call_args[1]["params"]["uri"]

    async def test_remove_from_collection_single(self, client_with_machine_id):
        """Test removing a single item from a collection."""
        client_with_machine_id._request = AsyncMock(return_value=None)

        await client_with_machine_id.remove_from_collection("999", ["101"])

        client_with_machine_id._request.assert_called_once_with(
            "DELETE", "library/collections/999/items/101", params=None
        )

    async def test_remove_from_collection_multiple(self, client_with_machine_id):
        """Test removing multiple items calls DELETE once per item."""
        client_with_machine_id._request = AsyncMock(return_value=None)

        await client_with_machine_id.remove_from_collection("999", ["101", "102", "103"])

        assert client_with_machine_id._request.call_count == 3
        calls = [c[0][1] for c in client_with_machine_id._request.call_args_list]
        assert "library/collections/999/items/101" in calls
        assert "library/collections/999/items/102" in calls
        assert "library/collections/999/items/103" in calls

    async def test_delete_collection(self, client_with_machine_id):
        """Test deleting a collection."""
        client_with_machine_id._request = AsyncMock(return_value=None)

        await client_with_machine_id.delete_collection("999")

        client_with_machine_id._request.assert_called_once_with(
            "DELETE", "library/collections/999", params=None
        )

    async def test_get_machine_identifier_cached(self, client):
        """Test that machine identifier is fetched once and cached."""
        client._request = AsyncMock(return_value=IDENTITY_RESPONSE)

        id1 = await client._get_machine_identifier()
        id2 = await client._get_machine_identifier()

        assert id1 == MACHINE_ID
        assert id2 == MACHINE_ID
        assert client._request.call_count == 1

    async def test_build_item_uri(self, client_with_machine_id):
        """Test URI building for item references."""
        uri = await client_with_machine_id._build_item_uri(["101", "102"])

        assert f"server://{MACHINE_ID}" in uri
        assert "101,102" in uri
        assert "com.plexapp.plugins.library" in uri
