from datetime import datetime

import asyncpg

from website_monitor.config import PostgresConfig
from website_monitor.database_writer.db.constants import (
    METRICS_TABLE_NAME_TMPL,
    METRICS_TABLE_SQL_TMPL,
    TARGETS_TABLE_SQL,
)


def get_metrics_table(
    datetime_: datetime, table_name_tmpl=METRICS_TABLE_NAME_TMPL
) -> str:
    return table_name_tmpl.format(datetime_)


async def get_db_connection(
    postgres_config: PostgresConfig,
) -> asyncpg.connection.Connection:
    return await asyncpg.connect(postgres_config.uri)


async def create_tables_if_needed(
    conn: asyncpg.connection.Connection, datetime_: datetime
) -> None:
    await conn.execute(TARGETS_TABLE_SQL)
    await conn.execute(
        METRICS_TABLE_SQL_TMPL.format(table_name=get_metrics_table(datetime_))
    )
