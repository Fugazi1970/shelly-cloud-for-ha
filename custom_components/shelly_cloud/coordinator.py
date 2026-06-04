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
    """Koordiniert das Polling der manuell konfigurierten Shelly-Geräte."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: ShellyCloudApi,
        devices: list[dict[str, str]],
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        # devices: [{"device_id": "abc", "device_name": "Wohnzimmer"}, ...]
        self.devices = devices

    @property
    def device_ids(self) -> list[str]:
        from .const import CONF_DEVICE_ID
        return [d[CONF_DEVICE_ID] for d in self.devices]

    def device_name(self, device_id: str) -> str:
        from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME
        for d in self.devices:
            if d[CONF_DEVICE_ID] == device_id:
                return d.get(CONF_DEVICE_NAME, device_id)
        return device_id

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        if not self.device_ids:
            return {}
        try:
            raw = await self.api.get_devices_status(self.device_ids)
        except ShellyCloudApiError as exc:
            raise UpdateFailed(f"Fehler beim Abruf der Gerätedaten: {exc}") from exc

        result: dict[str, dict[str, Any]] = {}
        for dev in raw:
            dev_id = dev.get("id") or dev.get("_id")
            if dev_id:
                result[dev_id] = dev
        return result
