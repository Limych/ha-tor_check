"""Sample API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout
import python_socks

TOR_CHECK_URL = "https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=1.1.1.1"
IPIFY_API_URL = "https://api.ipify.org"


class TorCheckApiClientError(Exception):
    """Exception to indicate a general API error."""


class TorCheckApiClientCommunicationError(TorCheckApiClientError):
    """Exception to indicate a communication error."""


class TorCheckApiClientAuthenticationError(TorCheckApiClientError):
    """Exception to indicate an authentication error."""


async def _async_get_data(session: aiohttp.ClientSession, url: str) -> any:
    """Fetch data from remote server."""
    try:
        async with async_timeout.timeout(10):
            response = await session.request(
                method="GET",
                url=url,
            )
            if response.status in (401, 403):
                raise TorCheckApiClientAuthenticationError("Invalid credentials")
            response.raise_for_status()
            return await response.text()

    except asyncio.TimeoutError as exception:
        raise TorCheckApiClientCommunicationError(
            "Timeout error fetching information",
        ) from exception
    except (
        aiohttp.ClientError,
        socket.gaierror,
        python_socks.ProxyConnectionError,
    ) as exception:
        raise TorCheckApiClientCommunicationError(
            "Error fetching information",
        ) from exception
    except Exception as exception:  # pylint: disable=broad-except
        raise TorCheckApiClientError("Something really wrong happened!") from exception


class TorCheckApiClient:
    """TOR API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        tor_session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._session = session
        self._tor_session = tor_session

    async def async_get_tor_exit_nodes(self) -> list[str]:
        """Get list of exit nodes from the TOR."""
        return (await _async_get_data(self._session, TOR_CHECK_URL)).split()

    async def async_get_my_tor_ip(self) -> str:
        """Get my current IP from the TOR."""
        return await _async_get_data(self._tor_session, IPIFY_API_URL)

    async def async_get_my_ip(self) -> str:
        """Get my current real IP."""
        return await _async_get_data(self._session, IPIFY_API_URL)
