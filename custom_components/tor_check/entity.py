"""TOR Check custom component entity class."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import TorCheckDataUpdateCoordinator


class TorCheckEntity(CoordinatorEntity):
    """TOR Check custom component entity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: TorCheckDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
