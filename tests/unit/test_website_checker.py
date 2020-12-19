from typing import List

import pytest
from yarl import URL

from tests.conftest import HttpRequest, wait_for_website_stub_requests
from website_monitor.website_checker import WebsiteChecker


@pytest.mark.asyncio
async def test_website_checker_sends_request_to_target(
    website_checker: WebsiteChecker,
    website_stub_requests: List[HttpRequest],
    website_stub_url: URL,
) -> None:
    await wait_for_website_stub_requests(website_stub_requests)

    assert len(website_stub_requests) == 1
    assert website_stub_requests[0].method == "GET"
    assert str(website_stub_requests[0].path) == website_stub_url.path
    assert website_stub_requests[0].data == ""
