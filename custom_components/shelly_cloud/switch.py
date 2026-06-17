"""Shelly Cloud Switch-Plattform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)


def _rpc_switch_channels(status: dict[str, Any]) -> list[int]:
    """Return Gen2/RPC switch channel ids from status keys like switch:0."""
    channels: list[int] = []
    for key, value in status.items():
        if not key.startswith("switch:") or not isinstance(value, dict):
            continue
        try:
            channels.append(int(key.split(":", 1)[1]))
        except (IndexError, ValueError):
            continue
    return sorted(channels)


def _switch_channels(dev_data: dict[str, Any]) -> list[int]:
    """Return all relay/switch channel ids for block and RPC status formats."""
    status = dev_data.get("status", {})
    block_channels = status.get("switches") or status.get("relays")
    if block_channels:
        return list(range(len(block_channels)))
    return _rpc_switch_channels(status)



def _switch_channel_status(status: dict[str, Any], channel: int) -> dict[str, Any]:
    """Return the status dict for a switch channel in block or RPC format."""
    channels = status.get("switches") or status.get("relays") or []
    if len(channels) > channel:
        return channels[channel]
    return status.get(f"switch:{channel}", {})


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities: list[ShellyCloudSwitch] = []

    for device_id in coordinator.device_ids:
        dev_data = coordinator.data.get(device_id, {})
        for channel in _switch_channels(dev_data):
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
            self._attr_name = None
        else:
            self._attr_unique_id = f"{device_id}_ch{channel}"
            self._attr_name = f"Kanal {channel + 1}"

    @property
    def is_on(self) -> bool | None:
        status = self._device_data.get("status", {})
        ch = _switch_channel_status(status, self._channel)
        return ch.get("output") if "output" in ch else ch.get("ison")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_switch(self._device_id, True, self._channel)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_switch(self._device_id, False, self._channel)
        await self.coordinator.async_request_refresh()
