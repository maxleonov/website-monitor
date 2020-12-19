import logging
import sys

import pytest

from website_monitor.database_writer import MetricsConsumer
from website_monitor.metrics import WebsiteAvailabilityMetrics
from website_monitor.website_checker import MetricsPublisher

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_metrics_delivery(
    metrics_publisher: MetricsPublisher,
    metrics_consumer: MetricsConsumer,
    metrics: WebsiteAvailabilityMetrics,
) -> None:
    await metrics_publisher.publish(metrics)
    metrics_ = await metrics_consumer.consume().__anext__()
    assert metrics_ == metrics
