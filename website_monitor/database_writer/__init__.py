import logging
from typing import AsyncGenerator

import asyncpg
from aiokafka import AIOKafkaConsumer

from website_monitor.config import KafkaConfig
from website_monitor.database_writer.db import (
    create_tables_if_needed,
    get_metrics_table,
)
from website_monitor.metrics import WebsiteAvailabilityMetrics

logger = logging.getLogger(__name__)


class MetricsConsumer:
    def __init__(self, kafka_config: KafkaConfig) -> None:
        self._consumer = AIOKafkaConsumer(
            kafka_config.metrics_topic,
            bootstrap_servers=kafka_config.bootstrap_servers,
            security_protocol=kafka_config.security_protocol,
            ssl_context=kafka_config.ssl_context,
            group_id="my-group",
            auto_offset_reset="earliest",
        )

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    async def consume(self) -> AsyncGenerator[WebsiteAvailabilityMetrics, None]:
        async for msg in self._consumer:
            try:
                yield WebsiteAvailabilityMetrics.deserialize(msg.value)
            except Exception:
                logger.exception("Failed to consume metrics")


async def select_or_insert_target_id(
    conn: asyncpg.connection.Connection, target: str
) -> int:
    # source: https://stackoverflow.com/a/6722460/964762
    sql = (
        "WITH new_row AS ("
        "INSERT INTO targets (target) "
        "SELECT $1"
        "WHERE NOT EXISTS (SELECT id FROM targets WHERE target = $2) "
        "RETURNING id"
        ") "
        "SELECT id FROM new_row "
        "UNION "
        "SELECT id FROM targets WHERE target = $3;"
    )
    row = await conn.fetchrow(sql, target, target, target)
    return row["id"]


async def save_metrics_to_db(
    conn: asyncpg.connection.Connection, metrics: WebsiteAvailabilityMetrics
) -> None:
    await create_tables_if_needed(conn, metrics.datetime)
    target_id = await select_or_insert_target_id(conn, metrics.target)
    metrics_table = get_metrics_table(metrics.datetime)
    sql = (
        f"INSERT INTO {metrics_table}"
        "(target_id, timestamp, http_response_time, http_status, regexp_match) "
        "VALUES($1, $2, $3, $4, $5)"
    )
    await conn.execute(
        sql,
        target_id,
        metrics.datetime,
        metrics.http_response_time,
        metrics.http_status,
        metrics.regexp_match,
    )
