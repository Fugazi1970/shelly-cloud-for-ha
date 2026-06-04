"""Shelly Cloud Sensor-Plattform (Energiezähler, Temperatur, etc.)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ShellySensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any] = lambda _: None


# ──────────────────────────────────────────────────────────────────
# Shelly Pro 3EM: Gen2  →  status enthält "em:0" und "emdata:0"
# ──────────────────────────────────────────────────────────────────

def _em(status: dict, field: str) -> Any:
    return status.get("em:0", {}).get(field)

def _emdata(status: dict, field: str) -> Any:
    return status.get("emdata:0", {}).get(field)


EM_SENSORS: list[ShellySensorDescription] = [
    # ── Phase A ──────────────────────────────────────────────────
    ShellySensorDescription(
        key="a_voltage", name="Phase A Spannung",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "a_voltage"),
    ),
    ShellySensorDescription(
        key="a_current", name="Phase A Strom",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "a_current"),
    ),
    ShellySensorDescription(
        key="a_act_power", name="Phase A Wirkleistung",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "a_act_power"),
    ),
    ShellySensorDescription(
        key="a_aprt_power", name="Phase A Scheinleistung",
        native_unit_of_measurement="VA",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda s: _em(s, "a_aprt_power"),
    ),
    ShellySensorDescription(
        key="a_pf", name="Phase A Leistungsfaktor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "a_pf"),
    ),
    ShellySensorDescription(
        key="a_freq", name="Phase A Frequenz",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "a_freq"),
    ),
    ShellySensorDescription(
        key="a_total_act_energy", name="Phase A Energie (bezogen)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "a_total_act_energy"),
    ),
    ShellySensorDescription(
        key="a_total_act_ret_energy", name="Phase A Energie (eingespeist)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "a_total_act_ret_energy"),
    ),
    # ── Phase B ──────────────────────────────────────────────────
    ShellySensorDescription(
        key="b_voltage", name="Phase B Spannung",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "b_voltage"),
    ),
    ShellySensorDescription(
        key="b_current", name="Phase B Strom",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "b_current"),
    ),
    ShellySensorDescription(
        key="b_act_power", name="Phase B Wirkleistung",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "b_act_power"),
    ),
    ShellySensorDescription(
        key="b_aprt_power", name="Phase B Scheinleistung",
        native_unit_of_measurement="VA",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda s: _em(s, "b_aprt_power"),
    ),
    ShellySensorDescription(
        key="b_pf", name="Phase B Leistungsfaktor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "b_pf"),
    ),
    ShellySensorDescription(
        key="b_total_act_energy", name="Phase B Energie (bezogen)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "b_total_act_energy"),
    ),
    ShellySensorDescription(
        key="b_total_act_ret_energy", name="Phase B Energie (eingespeist)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "b_total_act_ret_energy"),
    ),
    # ── Phase C ──────────────────────────────────────────────────
    ShellySensorDescription(
        key="c_voltage", name="Phase C Spannung",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "c_voltage"),
    ),
    ShellySensorDescription(
        key="c_current", name="Phase C Strom",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "c_current"),
    ),
    ShellySensorDescription(
        key="c_act_power", name="Phase C Wirkleistung",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "c_act_power"),
    ),
    ShellySensorDescription(
        key="c_aprt_power", name="Phase C Scheinleistung",
        native_unit_of_measurement="VA",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda s: _em(s, "c_aprt_power"),
    ),
    ShellySensorDescription(
        key="c_pf", name="Phase C Leistungsfaktor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "c_pf"),
    ),
    ShellySensorDescription(
        key="c_total_act_energy", name="Phase C Energie (bezogen)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "c_total_act_energy"),
    ),
    ShellySensorDescription(
        key="c_total_act_ret_energy", name="Phase C Energie (eingespeist)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "c_total_act_ret_energy"),
    ),
    # ── Gesamt ───────────────────────────────────────────────────
    ShellySensorDescription(
        key="total_act_power", name="Gesamte Wirkleistung",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "total_act_power"),
    ),
    ShellySensorDescription(
        key="total_current", name="Gesamtstrom",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _em(s, "total_current"),
    ),
    ShellySensorDescription(
        key="total_act_energy", name="Gesamtenergie (bezogen)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "total_act"),
    ),
    ShellySensorDescription(
        key="total_act_ret_energy", name="Gesamtenergie (eingespeist)",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _emdata(s, "total_act_ret"),
    ),
]

# ──────────────────────────────────────────────────────────────────
# Shelly 1PM / 2PM / Plus 1PM: Gen1/2 → status enthält "emeters"
# ──────────────────────────────────────────────────────────────────

def _emeter(status: dict, idx: int, field: str) -> Any:
    emeters = status.get("emeters", [])
    if len(emeters) > idx:
        return emeters[idx].get(field)
    return None


def _emeter_sensors(idx: int, label: str) -> list[ShellySensorDescription]:
    return [
        ShellySensorDescription(
            key=f"emeter{idx}_power", name=f"{label} Leistung",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _emeter(s, i, "power"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_voltage", name=f"{label} Spannung",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _emeter(s, i, "voltage"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_current", name=f"{label} Strom",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _emeter(s, i, "current"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_pf", name=f"{label} Leistungsfaktor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _emeter(s, i, "pf"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_total", name=f"{label} Energie (bezogen)",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda s, i=idx: _emeter(s, i, "total"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_total_returned", name=f"{label} Energie (eingespeist)",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda s, i=idx: _emeter(s, i, "total_returned"),
        ),
    ]


# ──────────────────────────────────────────────────────────────────
# Temperatur (ShellyPlusHT, ShellyBLU etc.)
# ──────────────────────────────────────────────────────────────────

TEMPERATURE_SENSORS: list[ShellySensorDescription] = [
    ShellySensorDescription(
        key="temperature", name="Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            s.get("temperature:0", {}).get("tC")
            or s.get("tmp", {}).get("value")
        ),
    ),
    ShellySensorDescription(
        key="humidity", name="Luftfeuchtigkeit",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            s.get("humidity:0", {}).get("rh")
            or s.get("hum", {}).get("value")
        ),
    ),
    ShellySensorDescription(
        key="battery", name="Batterie",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            s.get("devicepower:0", {}).get("battery", {}).get("percent")
            or s.get("bat", {}).get("value")
        ),
    ),
]


def _build_sensors_for_device(
    coordinator: ShellyCloudCoordinator, device_id: str
) -> list["ShellyCloudSensor"]:
    dev_data = coordinator.data.get(device_id, {})
    status = dev_data.get("status", {})
    entities: list[ShellyCloudSensor] = []

    # Gen2 3-Phasen-Zähler
    if "em:0" in status or "emdata:0" in status:
        for desc in EM_SENSORS:
            if desc.value_fn(status) is not None:
                entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    # Gen1 Energiezähler (emeters-Array)
    emeters = status.get("emeters", [])
    phase_labels = ["Phase A", "Phase B", "Phase C"]
    for idx, _ in enumerate(emeters):
        label = phase_labels[idx] if idx < len(phase_labels) else f"Kanal {idx+1}"
        for desc in _emeter_sensors(idx, label):
            if desc.value_fn(status) is not None:
                entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    # Temperatur / Feuchte / Batterie
    for desc in TEMPERATURE_SENSORS:
        if desc.value_fn(status) is not None:
            entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyCloudConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ShellyCloudCoordinator = entry.runtime_data
    entities: list[ShellyCloudSensor] = []
    for device_id in coordinator.device_ids:
        entities.extend(_build_sensors_for_device(coordinator, device_id))
    async_add_entities(entities)


class ShellyCloudSensor(ShellyCloudEntity, SensorEntity):
    """Ein einzelner Messwert eines Shelly-Geräts."""

    entity_description: ShellySensorDescription

    def __init__(
        self,
        coordinator: ShellyCloudCoordinator,
        device_id: str,
        description: ShellySensorDescription,
    ) -> None:
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        status = self._device_data.get("status", {})
        return self.entity_description.value_fn(status)
