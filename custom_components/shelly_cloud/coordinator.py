"""DataUpdateCoordinator für Shelly Cloud."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ShellyCloudApi, ShellyCloudApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ShellyCloudCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Koordiniert das Polling aller Shelly Cloud Geräte."""

    def __init__(self, hass: HomeAssistant, api: ShellyCloudApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self._device_ids: list[str] = []
        # Gerätemetadaten aus der Geräteliste (id, type, code, name, ...)
        self.device_info: dict[str, dict[str, Any]] = {}

    async def async_setup(self) -> None:
        """Geräteliste laden und device_ids befüllen."""
        devices = await self.api.list_devices()
        self.device_info = {}
        for dev in devices:
            dev_id = dev.get("id") or dev.get("_id")
            if dev_id:
                self.device_info[dev_id] = dev
        self._device_ids = list(self.device_info.keys())
        _LOGGER.debug("Shelly Cloud: %d Geräte gefunden", len(self._device_ids))

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        if not self._device_ids:
            return {}
        try:
            raw = await self.api.get_devices_status(self._device_ids)
        except ShellyCloudApiError as exc:
            raise UpdateFailed(f"Fehler beim Abruf der Gerätedaten: {exc}") from exc

        result: dict[str, dict[str, Any]] = {}
        for dev in raw:
            dev_id = dev.get("id") or dev.get("_id")
            if dev_id:
                result[dev_id] = dev
        return result
