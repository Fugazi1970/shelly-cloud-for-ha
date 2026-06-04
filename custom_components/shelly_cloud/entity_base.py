"""Basis-Entität für Shelly Cloud."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ShellyCloudCoordinator


class ShellyCloudEntity(CoordinatorEntity[ShellyCloudCoordinator]):
    """Gemeinsame Basis für alle Shelly Cloud Entitäten."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ShellyCloudCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id

        # Gerätename aus der manuellen Konfiguration
        display_name = coordinator.device_name(device_id)

        # Modell/Typ aus dem API-Response (wird beim ersten Poll befüllt)
        dev_data = coordinator.data.get(device_id, {})
        model = dev_data.get("code") or dev_data.get("type") or "Shelly"
        gen = dev_data.get("gen")
        if gen:
            model = f"{model} (Gen{gen})"

        self._attr_unique_id = device_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=display_name,
            manufacturer="Shelly",
            model=model,
        )

    @property
    def _device_data(self) -> dict[str, Any]:
        return self.coordinator.data.get(self._device_id, {})

    @property
    def available(self) -> bool:
        return bool(self._device_data.get("online"))
