"""Binary sensor platform for TOR Check custom component."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import ATTR_REAL_IP, ATTR_TOR_IP, DOMAIN
from .coordinator import (
    KEY_MY_IP,
    KEY_MY_TOR_IP,
    KEY_TOR_CONNECTED,
    TorCheckDataUpdateCoordinator,
)
from .entity import TorCheckEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="tor_check",
        name="TOR",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        TorCheckBinarySensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class TorCheckBinarySensor(TorCheckEntity, BinarySensorEntity):
    """TOR Check binary sensor class."""

    def __init__(
        self,
        coordinator: TorCheckDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get(KEY_TOR_CONNECTED)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return entity specific state attributes."""
        attrs = {
            ATTR_REAL_IP: self.coordinator.data.get(KEY_MY_IP),
            ATTR_TOR_IP: self.coordinator.data.get(KEY_MY_TOR_IP),
        }
        attrs.update(super().extra_state_attributes or {})
        return attrs
