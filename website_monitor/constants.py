import os
from pathlib import Path

APP_DIR = Path(
    os.environ.get("WEBSITE_MONITOR_CONFIG_PATH", Path(__file__).parent.absolute())
)
CONFIG_DIR = APP_DIR / ".." / "config"
KAFKA_CONFIG_DIR = CONFIG_DIR / "kafka"
CONFIG_PATH = CONFIG_DIR / "config.yml"
TEST_CONFIG_PATH = CONFIG_DIR / "config.test.yml"
