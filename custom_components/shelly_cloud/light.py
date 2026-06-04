"""Shelly Cloud Light-Plattform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)

EFFECTS = ["None", "Meteor Shower", "Gradual Change", "Flash", "Breath", "On/Off Gradual", "Red/Green Change"]
MIN_COLOR_TEMP_K = 2700
MAX_COLOR_TEMP_K = 7000


def _is_light(dev_data: dict[str, Any]) -> bool:
    status = dev_data.get("status", {})
    return bool(status.get("lights")) or "brightness" in status or "gain" in status


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities = [
        ShellyCloudLight(coordinator, device_id)
        for device_id in coordinator.device_ids
        if _is_light(coordinator.data.get(device_id, {}))
    ]
    async_add_entities(entities)


class ShellyCloudLight(ShellyCloudEntity, LightEntity):
    """Ein Shelly Leuchtmittel."""

    _attr_name = None
    _attr_min_color_temp_kelvin = MIN_COLOR_TEMP_K
    _attr_max_color_temp_kelvin = MAX_COLOR_TEMP_K
    _attr_effect_list = EFFECTS

    def _light_status(self) -> dict[str, Any]:
        status = self._device_data.get("status", {})
        lights = status.get("lights")
        return lights[0] if lights else status

    @property
    def color_mode(self) -> ColorMode:
        s = self._light_status()
        if s.get("mode") == "color" or "red" in s:
            return ColorMode.RGB
        if "color_temp" in s or "temp" in s:
            return ColorMode.COLOR_TEMP
        return ColorMode.BRIGHTNESS

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        s = self._light_status()
        modes: set[ColorMode] = set()
        if "red" in s:
            modes.add(ColorMode.RGB)
        if "color_temp" in s or "temp" in s:
            modes.add(ColorMode.COLOR_TEMP)
        return modes or {ColorMode.BRIGHTNESS}

    @property
    def supported_features(self) -> LightEntityFeature:
        return LightEntityFeature.EFFECT

    @property
    def is_on(self) -> bool | None:
        s = self._light_status()
        return s.get("output") if "output" in s else s.get("ison")

    @property
    def brightness(self) -> int | None:
        s = self._light_status()
        gain = s.get("brightness") or s.get("gain")
        return round(gain / 100 * 255) if gain is not None else None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        s = self._light_status()
        return (s["red"], s["green"], s["blue"]) if "red" in s else None

    @property
    def color_temp_kelvin(self) -> int | None:
        s = self._light_status()
        return s.get("temp") or s.get("color_temp")

    @property
    def effect(self) -> str | None:
        idx = self._light_status().get("effect")
        return EFFECTS[idx] if idx is not None and 0 <= idx < len(EFFECTS) else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        rgb = kwargs.get(ATTR_RGB_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        effect_name = kwargs.get(ATTR_EFFECT)
        effect_idx = EFFECTS.index(effect_name) if effect_name in (EFFECTS or []) else None

        await self.coordinator.api.set_light(
            self._device_id,
            on=True,
            brightness=round(brightness / 255 * 100) if brightness is not None else None,
            red=rgb[0] if rgb else None,
            green=rgb[1] if rgb else None,
            blue=rgb[2] if rgb else None,
            temperature=color_temp,
            mode="color" if rgb else ("white" if color_temp else None),
            effect=effect_idx,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_light(self._device_id, on=False)
        await self.coordinator.async_request_refresh()
