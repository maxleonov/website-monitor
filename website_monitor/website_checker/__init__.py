import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Optional

import pytz
from aiohttp import ClientSession
from aiokafka import AIOKafkaProducer

from website_monitor.config import KafkaConfig, TargetConfig
from website_monitor.metrics import WebsiteAvailabilityMetrics

logger = logging.getLogger(__name__)


class MetricsPublisher:
    def __init__(self, kafka_config: KafkaConfig) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            security_protocol=kafka_config.security_protocol,
            ssl_context=kafka_config.ssl_context,
        )
        self._kafka_config = kafka_config

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(self, metrics: WebsiteAvailabilityMetrics) -> None:
        await self._producer.send(self._kafka_config.metrics_topic, metrics.serialize())


class WebsiteChecker:
    def __init__(
        self,
        target_config: TargetConfig,
        metrics_publisher: MetricsPublisher,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._config = target_config
        self._metrics_publisher = metrics_publisher
        self._loop = loop or asyncio.get_event_loop()
        self._is_active: Optional[asyncio.Future[None]] = None
        self._task: Optional[asyncio.Future[None]] = None

    async def start(self) -> None:
        logger.info(f"Starting WebsiteChecker: {self._config}")
        await self._init_task()

    async def stop(self) -> None:
        logger.info("Stopping WebsiteChecker")
        assert self._is_active
        self._is_active.set_result(None)

        assert self._task
        await self._task

        await self._http_client_session.close()

        self._task = None
        self._is_active = None

    async def _init_task(self) -> None:
        assert not self._is_active
        assert not self._task

        self._http_client_session = ClientSession()

        self._is_active = self._loop.create_future()
        self._task = asyncio.ensure_future(self._run(), loop=self._loop)
        await asyncio.sleep(0, loop=self._loop)

    async def _run(self) -> None:
        assert self._is_active
        while not self._is_active.done():
            logger.debug(f"WebsiteChecker iteration: {self._config}")
            await asyncio.gather(
                self._check_and_publish_website_metrics(), self._wait(), loop=self._loop
            )

    async def _wait(self) -> None:
        assert self._is_active
        await asyncio.wait(
            (self._is_active,),
            loop=self._loop,
            timeout=self._config.check_interval_seconds,
        )

    async def _check_and_publish_website_metrics(self) -> None:
        metrics: WebsiteAvailabilityMetrics = await self._check_website()
        await self._publish_metrics(metrics)

    async def _check_website(self) -> WebsiteAvailabilityMetrics:
        start_time = time.time()
        async with self._http_client_session.get(self._config.url) as response:
            http_response_time = time.time() - start_time
            body = await response.text()
            if self._config.regexp:
                match = bool(re.match(self._config.regexp, body))
            else:
                match = None
            return WebsiteAvailabilityMetrics(
                datetime=datetime.now(tz=pytz.utc),
                target=self._config.name,
                http_response_time=http_response_time,
                http_status=response.status,
                regexp_match=match,
            )

    async def _publish_metrics(self, metrics: WebsiteAvailabilityMetrics) -> None:
        await self._metrics_publisher.publish(metrics)
