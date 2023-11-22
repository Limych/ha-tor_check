"""Constants for tests."""
from typing import Final

from custom_components.tor_check import CONF_TOR_HOST, CONF_TOR_PORT

# Mock config data to be used across multiple tests
MOCK_CONFIG: Final = {
    CONF_TOR_HOST: "localhost",
    CONF_TOR_PORT: 9050,
}
