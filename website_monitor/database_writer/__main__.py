import asyncio
import logging
import signal
import sys

import asyncpg

from website_monitor.config import KafkaConfig, PostgresConfig
from website_monitor.database_writer import MetricsConsumer, save_metrics_to_db
from website_monitor.database_writer.db import get_db_connection

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def shutdown(
    consumer: MetricsConsumer,
    db_connection: asyncpg.connection.Connection,
    is_active: asyncio.Future,
):
    logger.info("Shutting down")
    await consumer.stop()
    await db_connection.close()
    is_active.set_result(None)


async def main():
    loop = asyncio.get_event_loop()
    is_active = loop.create_future()

    db_connection = await get_db_connection(postgres_config=PostgresConfig.from_file())
    consumer = MetricsConsumer(kafka_config=KafkaConfig.from_file())

    for signal_ in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(
            signal_,
            lambda s=signal_: asyncio.create_task(
                shutdown(consumer, db_connection, is_active)
            ),
        )

    await consumer.start()
    async for metrics in consumer.consume():
        await save_metrics_to_db(db_connection, metrics)


if __name__ == "__main__":
    asyncio.run(main())
