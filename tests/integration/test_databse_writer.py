from datetime import datetime

import asyncpg
import pytest

from website_monitor.database_writer import save_metrics_to_db
from website_monitor.database_writer.db import get_metrics_table
from website_monitor.metrics import WebsiteAvailabilityMetrics


@pytest.mark.usefixtures("drop_tables")
@pytest.mark.asyncio
async def test_save_metrics_to_db(
    db_connection: asyncpg.connection.Connection,
    metrics: WebsiteAvailabilityMetrics,
):
    await save_metrics_to_db(db_connection, metrics)

    row = await db_connection.fetchrow("SELECT * from targets;")
    assert row["id"] == 1
    assert row["target"] == metrics.target

    metrics_table = get_metrics_table(metrics.datetime)
    row = await db_connection.fetchrow(f"SELECT * from {metrics_table};")
    assert row["id"] == 1
    assert row["target_id"] == 1
    assert row["timestamp"] == metrics.datetime
    assert row["http_response_time"] == metrics.http_response_time
    assert row["http_status"] == metrics.http_status
    assert row["regexp_match"] == metrics.regexp_match
