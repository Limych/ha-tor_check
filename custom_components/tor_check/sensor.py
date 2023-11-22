"""Sensor platform for TOR Check custom component."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import ATTR_REAL_IP, ATTR_TOR_CONNECTED, DOMAIN
from .coordinator import (
    KEY_MY_IP,
    KEY_MY_TOR_IP,
    KEY_TOR_CONNECTED,
    TorCheckDataUpdateCoordinator,
)
from .entity import TorCheckEntity

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="tor_ip",
        name="TOR IP",
        icon="mdi:ip",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TorCheckSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class TorCheckSensor(TorCheckEntity, SensorEntity):
    """TOR Check Sensor class."""

    def __init__(
        self,
        coordinator: TorCheckDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(KEY_MY_TOR_IP)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        attrs = {
            ATTR_REAL_IP: self.coordinator.data.get(KEY_MY_IP),
            ATTR_TOR_CONNECTED: self.coordinator.data.get(KEY_TOR_CONNECTED),
        }
        attrs.update(super().extra_state_attributes or {})
        return attrs
