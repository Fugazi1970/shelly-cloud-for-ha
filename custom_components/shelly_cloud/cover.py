"""Shelly Cloud Cover-Plattform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)


def _is_cover(dev_data: dict[str, Any]) -> bool:
    status = dev_data.get("status", {})
    return bool(status.get("covers") or status.get("rollers"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities = [
        ShellyCloudCover(coordinator, device_id)
        for device_id in coordinator.device_ids
        if _is_cover(coordinator.data.get(device_id, {}))
    ]
    async_add_entities(entities)


class ShellyCloudCover(ShellyCloudEntity, CoverEntity):
    """Ein Shelly Rollladen/Jalousie."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )
    _attr_name = None

    def _roller_status(self) -> dict[str, Any]:
        status = self._device_data.get("status", {})
        entries = status.get("covers") or status.get("rollers") or [{}]
        return entries[0] if entries else {}

    @property
    def current_cover_position(self) -> int | None:
        s = self._roller_status()
        return s.get("current_pos") or s.get("current_position")

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        return None if pos is None else pos == 0

    @property
    def is_opening(self) -> bool:
        return self._roller_status().get("state") in ("opening", "open")

    @property
    def is_closing(self) -> bool:
        return self._roller_status().get("state") in ("closing", "close")

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_cover(self._device_id, "open")
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_cover(self._device_id, "close")
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_cover(self._device_id, "stop")
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_cover(self._device_id, kwargs[ATTR_POSITION])
        await self.coordinator.async_request_refresh()
