"""DataUpdateCoordinator for TOR Check custom integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .api import (
    TorCheckApiClient,
    TorCheckApiClientAuthenticationError,
    TorCheckApiClientCommunicationError,
    TorCheckApiClientError,
)
from .const import DOMAIN, LOGGER

_LOGGER: Final = logging.getLogger(__name__)


KEY_TOR_EXIT_NODES = "tor_exit_nodes"
KEY_MY_TOR_IP = "my_tor_ip"
KEY_MY_IP = "my_ip"
KEY_TOR_CONNECTED = "tor_connected"


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class TorCheckDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    _cache: dict[str : list[datetime, any]] = {}

    def __init__(
        self,
        hass: HomeAssistant,
        client: TorCheckApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    def _cache_get(self, key: str, default: any = None) -> any:
        """Get data from cache by key."""
        if key in self._cache:
            if self._cache[key][0] < dt_util.utcnow():
                del self._cache[key]
                return default
            return self._cache[key][1]
        return default

    def _cache_set(
        self, key: str, data: any, timeout: timedelta = timedelta(minutes=15)
    ) -> any:
        """Store data to cache by key for some time."""
        self._cache[key] = [dt_util.utcnow() + timeout, data]
        return data

    async def _async_update_data(self):
        """Update data via library."""
        data = {
            KEY_TOR_EXIT_NODES: self._cache_get(KEY_TOR_EXIT_NODES, {}),
            KEY_MY_TOR_IP: self._cache_get(KEY_MY_TOR_IP),
            KEY_MY_IP: self._cache_get(KEY_MY_IP),
        }
        try:
            if data[KEY_TOR_EXIT_NODES] == {}:
                data[KEY_TOR_EXIT_NODES] = self._cache_set(
                    KEY_TOR_EXIT_NODES,
                    await self.client.async_get_tor_exit_nodes(),
                    timedelta(days=1),
                )
            if data[KEY_MY_TOR_IP] is None:
                data[KEY_MY_TOR_IP] = self._cache_set(
                    KEY_MY_TOR_IP,
                    await self.client.async_get_my_tor_ip(),
                )
        except TorCheckApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except TorCheckApiClientCommunicationError:
            _LOGGER.debug("Communication error: Can't connect to TOR network.")
        except TorCheckApiClientError as exception:
            raise UpdateFailed(exception) from exception

        try:
            if data[KEY_MY_IP] is None:
                data[KEY_MY_IP] = self._cache_set(
                    KEY_MY_IP,
                    await self.client.async_get_my_ip(),
                )
        except TorCheckApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except TorCheckApiClientError as exception:
            raise UpdateFailed(exception) from exception

        data[KEY_TOR_CONNECTED] = data.get(KEY_MY_TOR_IP) in data.get(
            KEY_TOR_EXIT_NODES
        )

        return data
