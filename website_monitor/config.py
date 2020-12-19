import re
from pathlib import Path
from ssl import SSLContext
from typing import Dict, Generator, NamedTuple, Optional

import yaml
from aiokafka.helpers import create_ssl_context
from yarl import URL

from website_monitor.constants import CONFIG_PATH, KAFKA_CONFIG_DIR


class KafkaConfig(NamedTuple):
    bootstrap_servers: str
    metrics_topic: str
    ssl_context: SSLContext
    security_protocol: str = "SSL"

    @staticmethod
    def from_file(
        path: Path = CONFIG_PATH,
    ) -> "KafkaConfig":
        with open(str(path), "r") as file:
            config_yml: Dict = yaml.safe_load(file)
        ssl_context: SSLContext = create_ssl_context(
            cafile=KAFKA_CONFIG_DIR / "ca.pem",
            certfile=KAFKA_CONFIG_DIR / "service.cert",
            keyfile=KAFKA_CONFIG_DIR / "service.key",
        )
        return KafkaConfig(
            bootstrap_servers=config_yml["kafka"]["bootstrap_servers"],
            metrics_topic=config_yml["kafka"]["metrics_topic"],
            ssl_context=ssl_context,
        )


class PostgresConfig(NamedTuple):
    uri: str

    @staticmethod
    def from_file(
        path: Path = CONFIG_PATH,
    ) -> "PostgresConfig":
        with open(str(path), "r") as file:
            config_yml: Dict = yaml.safe_load(file)
        return PostgresConfig(
            uri=config_yml["postgres"]["uri"],
        )


class TargetConfig(NamedTuple):
    name: str
    url: URL
    check_interval_seconds: float
    regexp: Optional[re.Pattern]

    @staticmethod
    def from_file(
        path: Path = CONFIG_PATH,
    ) -> Generator["TargetConfig", None, None]:
        with open(str(path), "r") as file:
            config_yml: Dict = yaml.safe_load(file)

        for target_yml in config_yml["targets"]:
            interval = target_yml["check_interval_seconds"]
            regexp = (
                re.compile(target_yml["regexp"], re.DOTALL)
                if "regexp" in target_yml
                else None
            )
            yield TargetConfig(
                name=target_yml["name"],
                url=URL(target_yml["target"]),
                check_interval_seconds=float(interval),
                regexp=regexp,
            )
