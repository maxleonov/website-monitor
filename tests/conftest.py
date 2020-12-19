import asyncio
import contextlib
import re
import time
from datetime import datetime
from typing import Any, Callable, List, Mapping, NamedTuple

import asyncpg
import pytest
from aiohttp.test_utils import TestServer
from aiohttp.web_app import Application
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from yarl import URL

from website_monitor.config import KafkaConfig, PostgresConfig, TargetConfig
from website_monitor.constants import TEST_CONFIG_PATH
from website_monitor.database_writer import MetricsConsumer
from website_monitor.database_writer.db import get_db_connection
from website_monitor.metrics import WebsiteAvailabilityMetrics
from website_monitor.website_checker import MetricsPublisher, WebsiteChecker


class HttpRequest(NamedTuple):
    method: str
    path: str
    headers: Mapping[str, str] = {}
    data: Any = None


@pytest.fixture
def website_stub_requests() -> List[HttpRequest]:
    http_requests: List[HttpRequest] = []
    yield http_requests


async def wait_for_website_stub_requests(
    website_stub_requests: List[HttpRequest],
    min_count: int = 1,
    timeout_s: float = 5.0,
) -> None:
    end_time = time.time() + timeout_s
    count = -1

    while time.time() < end_time:
        await asyncio.sleep(0)
        count = len(website_stub_requests)
        if count >= min_count:
            return

    raise TimeoutError(
        f"Expected at least {min_count} website server stub request(s), "
        f"got {count} instead. Waited for {timeout_s} second(s)."
    )


@pytest.fixture
async def website_stub(
    aiohttp_server: Callable[[], TestServer],
    website_stub_requests: List[HttpRequest],
) -> TestServer:
    async def root_handler(request: Request) -> Response:
        body = await request.text()
        website_stub_requests.append(
            HttpRequest(
                method=request.method,
                path=request.rel_url,
                headers=request.headers,
                data=body,
            )
        )
        return Response(body="<h1>Test Website</h1>", status=201)

    app = Application()

    app.router.add_get("/", root_handler)

    server = await aiohttp_server(app)

    async with server:
        yield server


@pytest.fixture
def website_stub_url(website_stub: TestServer) -> URL:
    yield URL.build(scheme="http", host=website_stub.host, port=website_stub.port)


@pytest.fixture
def target_config(website_stub_url: URL) -> TargetConfig:
    return TargetConfig(
        name="test",
        url=website_stub_url,
        check_interval_seconds=0.0,
        regexp=re.compile(".*Test.*"),
    )


@pytest.fixture
def kafka_config() -> KafkaConfig:
    return KafkaConfig.from_file(TEST_CONFIG_PATH)


@pytest.fixture
def postgres_config() -> PostgresConfig:
    return PostgresConfig.from_file(TEST_CONFIG_PATH)


@pytest.fixture
async def website_checker(
    target_config: TargetConfig,
    metrics_publisher: MetricsPublisher,
) -> WebsiteChecker:
    checker = WebsiteChecker(
        target_config=target_config, metrics_publisher=metrics_publisher
    )
    await checker.start()
    yield checker
    await checker.stop()


@pytest.fixture
async def metrics_publisher(kafka_config: KafkaConfig) -> MetricsPublisher:
    metrics_publisher = MetricsPublisher(kafka_config)
    await metrics_publisher.start()
    yield metrics_publisher
    await metrics_publisher.stop()


@pytest.fixture
async def metrics_consumer(kafka_config: KafkaConfig) -> MetricsConsumer:
    metrics_consumer = MetricsConsumer(kafka_config)
    await metrics_consumer.start()
    yield metrics_consumer
    await metrics_consumer.stop()


@pytest.fixture
def metrics() -> WebsiteAvailabilityMetrics:
    return WebsiteAvailabilityMetrics(
        datetime=datetime(2020, 12, 18, 17, 42, 47, 14361),
        target="test",
        http_response_time=0.28101205825805664,
        http_status=200,
        regexp_match=None,
    )


@pytest.fixture
async def db_connection(
    postgres_config: PostgresConfig,
) -> asyncpg.connection.Connection:
    conn = await get_db_connection(postgres_config)
    yield conn
    await conn.close()


@pytest.fixture
async def drop_tables(db_connection: asyncpg.connection.Connection) -> None:
    rows = await db_connection.fetchrow(
        "SELECT tablename FROM pg_catalog.pg_tables where tablename like 'metrics_%';"
    )
    for tablename in rows or []:
        await db_connection.execute(f"DROP TABLE {tablename};")
    with contextlib.suppress(asyncpg.exceptions.UndefinedTableError):
        await db_connection.execute("DROP TABLE targets")
    yield
