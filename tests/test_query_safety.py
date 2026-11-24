"""Regression tests for Overseerr query encoding and Jackett indexer validation."""

from unittest.mock import AsyncMock

import httpx
import pytest

from arr_suite_mcp.clients.jackett import JackettClient
from arr_suite_mcp.clients.overseerr import OverseerrClient


@pytest.mark.asyncio
async def test_overseerr_search_encodes_query_once_with_percent20():
    client = OverseerrClient("http://overseerr:5055", "key")
    sent = {}

    async def fake_send(request, **kwargs):
        sent["url"] = str(request.url)
        return httpx.Response(200, json={"results": []}, request=request)

    client.client.send = fake_send
    await client.search_media("star wars: the 'empire' & co!")

    url = sent["url"]
    assert "query=star%20wars%3A%20the%20%27empire%27%20%26%20co%21" in url
    assert "+" not in url.split("?", 1)[1]
    assert "%25" not in url
    assert "page=1" in url and "language=en" in url


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", ["../server/config", "..", "all/../x", "a b", ""])
async def test_jackett_search_rejects_path_like_indexer_ids(bad):
    client = JackettClient("http://jackett:9117", "key")
    client._request = AsyncMock()
    with pytest.raises(ValueError):
        await client.search("ubuntu", indexer=bad)
    client._request.assert_not_called()


@pytest.mark.asyncio
async def test_jackett_search_accepts_normal_indexer_ids():
    client = JackettClient("http://jackett:9117", "key")
    client._request = AsyncMock(return_value={"Results": []})
    await client.search("ubuntu", indexer="1337x")
    assert client._request.call_args.args[1] == "indexers/1337x/results"
