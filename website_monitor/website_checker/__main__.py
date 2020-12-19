import asyncio
import logging
import signal
import sys
from typing import List

from website_monitor.config import KafkaConfig, TargetConfig
from website_monitor.website_checker import MetricsPublisher, WebsiteChecker

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def shutdown(
    publisher: MetricsPublisher,
    checkers: List[WebsiteChecker],
    is_active: asyncio.Future,
):
    logger.info("Shutting down")
    for checker in checkers:
        await checker.stop()
    await publisher.stop()
    is_active.set_result(None)


async def main():
    loop = asyncio.get_event_loop()
    is_active = loop.create_future()

    publisher = MetricsPublisher(kafka_config=KafkaConfig.from_file())
    await publisher.start()
    checkers = []

    for target_config in TargetConfig.from_file():
        checkers.append(
            WebsiteChecker(target_config=target_config, metrics_publisher=publisher)
        )
        await checkers[-1].start()

    for signal_ in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(
            signal_,
            lambda s=signal_: asyncio.create_task(
                shutdown(publisher, checkers, is_active)
            ),
        )

    while not is_active.done():
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
