"""Shelly Cloud Switch-Plattform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .const import SWITCH_CODES
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities: list[ShellyCloudSwitch] = []

    for device_id, meta in coordinator.device_info.items():
        code = meta.get("code") or meta.get("type", "")
        if code in SWITCH_CODES:
            # Anzahl Kanäle ermitteln (Standard: 1)
            status = coordinator.data.get(device_id, {}).get("status", {})
            switches = status.get("switches") or status.get("relays") or [{}]
            for channel, _ in enumerate(switches):
                entities.append(ShellyCloudSwitch(coordinator, device_id, channel))

    async_add_entities(entities)


class ShellyCloudSwitch(ShellyCloudEntity, SwitchEntity):
    """Ein Shelly Relais/Schalter-Kanal."""

    def __init__(
        self, coordinator: ShellyCloudCoordinator, device_id: str, channel: int
    ) -> None:
        super().__init__(coordinator, device_id)
        self._channel = channel
        if channel == 0:
            self._attr_unique_id = device_id
            self._attr_name = None  # Gerätename wird verwendet
        else:
            self._attr_unique_id = f"{device_id}_ch{channel}"
            self._attr_name = f"Kanal {channel + 1}"

    @property
    def is_on(self) -> bool | None:
        status = self._device_data.get("status", {})
        switches = status.get("switches") or status.get("relays") or []
        if len(switches) > self._channel:
            ch = switches[self._channel]
            return ch.get("output") if "output" in ch else ch.get("ison")
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_switch(self._device_id, True, self._channel)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_switch(self._device_id, False, self._channel)
        await self.coordinator.async_request_refresh()
