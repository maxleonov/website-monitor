METRICS_TABLE_NAME_TMPL = "metrics_{:%Y_%m}"
TARGETS_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS targets ("
    "id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
    "target varchar(128) UNIQUE,"
    "created_at timestamp NOT NULL DEFAULT NOW()"
    ");"
)
METRICS_TABLE_SQL_TMPL = (
    "CREATE TABLE IF NOT EXISTS {table_name} ("
    "id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,"
    "target_id integer references targets(id) ON DELETE CASCADE,"
    "timestamp timestamp NOT NULL,"
    "http_response_time real NOT NULL,"
    "http_status smallint NOT NULL,"
    "regexp_match boolean"
    ");"
)
