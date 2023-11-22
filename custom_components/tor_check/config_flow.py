"""Adds config flow for TOR Check custom component."""
from __future__ import annotations

from typing import Final, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from . import async_create_proxy_clientsession
from .api import (
    TorCheckApiClient,
    TorCheckApiClientAuthenticationError,
    TorCheckApiClientCommunicationError,
    TorCheckApiClientError,
)
from .const import (
    CONF_TOR_HOST,
    CONF_TOR_PORT,
    DEFAULT_CONFIG,
    DOMAIN,
    LOGGER,
    ConfigType,
)

PORT_SELECTOR = vol.All(
    NumberSelector(NumberSelectorConfig(mode=NumberSelectorMode.BOX, min=1, max=65535)),
    vol.Coerce(int),
)


class TorCheckFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TOR Check custom component."""

    VERSION = 1
    CONNECTION_CLASS: Final = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(
        self, platform_config: ConfigType
    ) -> config_entries.FlowResult:
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        for entry in self._async_current_entries():
            if entry.source == config_entries.SOURCE_IMPORT:
                self.hass.config_entries.async_update_entry(entry, data=platform_config)
                return self.async_abort(reason="")

        return self.async_create_entry(title="configuration.yaml", data=platform_config)

    async def async_step_user(
        self, user_input: Optional[ConfigType] = None
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        if user_input is not None:
            try:
                await self._test_credentials(
                    tor_host=user_input[CONF_TOR_HOST],
                    tor_port=user_input[CONF_TOR_PORT],
                )
            except TorCheckApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except TorCheckApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except TorCheckApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_TOR_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TOR_HOST,
                        default=(user_input or DEFAULT_CONFIG).get(CONF_TOR_HOST),
                    ): TextSelector(),
                    vol.Optional(
                        CONF_TOR_PORT,
                        default=(user_input or DEFAULT_CONFIG).get(CONF_TOR_PORT),
                    ): PORT_SELECTOR,
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, tor_host: str, tor_port: int) -> None:
        """Validate credentials."""
        proxy_url = f"socks5://{tor_host}:{tor_port}"
        client = TorCheckApiClient(
            session=async_create_clientsession(self.hass),
            tor_session=async_create_proxy_clientsession(self.hass, proxy_url),
        )
        await client.async_get_my_tor_ip()
