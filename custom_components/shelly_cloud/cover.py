"""Shelly Cloud Cover-Plattform (Rollladen, Jalousie)."""
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
from .const import COVER_CODES
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities = [
        ShellyCloudCover(coordinator, device_id)
        for device_id, meta in coordinator.device_info.items()
        if (meta.get("code") or meta.get("type", "")) in COVER_CODES
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
        covers = status.get("covers") or status.get("rollers") or [{}]
        return covers[0] if covers else {}

    @property
    def current_cover_position(self) -> int | None:
        pos = self._roller_status().get("current_pos") or self._roller_status().get("current_position")
        return pos

    @property
    def is_closed(self) -> bool | None:
        pos = self.current_cover_position
        if pos is None:
            return None
        return pos == 0

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
        position = kwargs[ATTR_POSITION]
        await self.coordinator.api.set_cover(self._device_id, position)
        await self.coordinator.async_request_refresh()
