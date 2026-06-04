"""Shelly Cloud Sensor-Plattform.

Unterstützt:
  - Shelly Pro 3EM / 3EM Pro  (Gen2, RPC) — em:0 + emdata:0
  - Shelly EM / 1EM            (Gen1, Block) — emeters[]
  - Shelly Plus/Pro 1PM/2PM    (Gen2, RPC) — switch:N mit apower/aenergy
  - Shelly 1PM                 (Gen1, Block) — emeters[]
  - Temperatur-/Feuchte-/Batterie-Sensoren
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ShellyCloudConfigEntry
from .coordinator import ShellyCloudCoordinator
from .entity_base import ShellyCloudEntity

_LOGGER = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen
# ──────────────────────────────────────────────────────────────────────────────

def _rpc(status: dict, component: str, sub_key: str) -> Any:
    """Wert aus RPC-Status lesen: status[component][sub_key]."""
    comp = status.get(component) or status.get(component.split(":")[0] + ":0", {})
    if isinstance(comp, dict):
        return comp.get(sub_key)
    return None


def _rpc_nested(status: dict, component: str, sub_key: str, inner: str) -> Any:
    """Wert aus verschachteltem RPC-Status: status[component][sub_key][inner]."""
    val = _rpc(status, component, sub_key)
    if isinstance(val, dict):
        return val.get(inner)
    return None


def _block(status: dict, idx: int, field_name: str) -> Any:
    """Wert aus Block-Status lesen: status[emeters][idx][field]."""
    emeters = status.get("emeters", [])
    if len(emeters) > idx:
        return emeters[idx].get(field_name)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Sensor-Beschreibung
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ShellySensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any] = field(default=lambda _: None)
    # Wenn True: Sensor wird nur angelegt wenn value_fn nicht None zurückgibt
    optional: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Pro 3EM / 3EM Pro  →  em:0  +  emdata:0
# ──────────────────────────────────────────────────────────────────────────────

EM3_SENSORS: list[ShellySensorDescription] = []

_EM3_PHASE_FIELDS = [
    ("a_voltage",       "Phase A Spannung",           UnitOfElectricPotential.VOLT,  SensorDeviceClass.VOLTAGE,       SensorStateClass.MEASUREMENT),
    ("a_current",       "Phase A Strom",              UnitOfElectricCurrent.AMPERE,  SensorDeviceClass.CURRENT,       SensorStateClass.MEASUREMENT),
    ("a_act_power",     "Phase A Wirkleistung",       UnitOfPower.WATT,              SensorDeviceClass.POWER,         SensorStateClass.MEASUREMENT),
    ("a_aprt_power",    "Phase A Scheinleistung",     "VA",                          None,                            SensorStateClass.MEASUREMENT),
    ("a_pf",            "Phase A Leistungsfaktor",    None,                          SensorDeviceClass.POWER_FACTOR,  SensorStateClass.MEASUREMENT),
    ("a_freq",          "Phase A Frequenz",           UnitOfFrequency.HERTZ,         SensorDeviceClass.FREQUENCY,     SensorStateClass.MEASUREMENT),
    ("b_voltage",       "Phase B Spannung",           UnitOfElectricPotential.VOLT,  SensorDeviceClass.VOLTAGE,       SensorStateClass.MEASUREMENT),
    ("b_current",       "Phase B Strom",              UnitOfElectricCurrent.AMPERE,  SensorDeviceClass.CURRENT,       SensorStateClass.MEASUREMENT),
    ("b_act_power",     "Phase B Wirkleistung",       UnitOfPower.WATT,              SensorDeviceClass.POWER,         SensorStateClass.MEASUREMENT),
    ("b_aprt_power",    "Phase B Scheinleistung",     "VA",                          None,                            SensorStateClass.MEASUREMENT),
    ("b_pf",            "Phase B Leistungsfaktor",    None,                          SensorDeviceClass.POWER_FACTOR,  SensorStateClass.MEASUREMENT),
    ("b_freq",          "Phase B Frequenz",           UnitOfFrequency.HERTZ,         SensorDeviceClass.FREQUENCY,     SensorStateClass.MEASUREMENT),
    ("c_voltage",       "Phase C Spannung",           UnitOfElectricPotential.VOLT,  SensorDeviceClass.VOLTAGE,       SensorStateClass.MEASUREMENT),
    ("c_current",       "Phase C Strom",              UnitOfElectricCurrent.AMPERE,  SensorDeviceClass.CURRENT,       SensorStateClass.MEASUREMENT),
    ("c_act_power",     "Phase C Wirkleistung",       UnitOfPower.WATT,              SensorDeviceClass.POWER,         SensorStateClass.MEASUREMENT),
    ("c_aprt_power",    "Phase C Scheinleistung",     "VA",                          None,                            SensorStateClass.MEASUREMENT),
    ("c_pf",            "Phase C Leistungsfaktor",    None,                          SensorDeviceClass.POWER_FACTOR,  SensorStateClass.MEASUREMENT),
    ("c_freq",          "Phase C Frequenz",           UnitOfFrequency.HERTZ,         SensorDeviceClass.FREQUENCY,     SensorStateClass.MEASUREMENT),
    ("n_current",       "Neutralleiter Strom",        UnitOfElectricCurrent.AMPERE,  SensorDeviceClass.CURRENT,       SensorStateClass.MEASUREMENT),
    ("total_act_power", "Gesamte Wirkleistung",       UnitOfPower.WATT,              SensorDeviceClass.POWER,         SensorStateClass.MEASUREMENT),
    ("total_aprt_power","Gesamte Scheinleistung",     "VA",                          None,                            SensorStateClass.MEASUREMENT),
    ("total_current",   "Gesamtstrom",                UnitOfElectricCurrent.AMPERE,  SensorDeviceClass.CURRENT,       SensorStateClass.MEASUREMENT),
]

for _sk, _name, _unit, _dc, _sc in _EM3_PHASE_FIELDS:
    EM3_SENSORS.append(ShellySensorDescription(
        key=f"em_{_sk}",
        name=_name,
        native_unit_of_measurement=_unit,
        device_class=_dc,
        state_class=_sc,
        value_fn=(lambda s, sub=_sk: _rpc(s, "em:0", sub)),
    ))

# Energiedaten aus emdata:0
_EM3_ENERGY_FIELDS = [
    ("a_total_act_energy",      "Phase A Energie (bezogen)"),
    ("a_total_act_ret_energy",  "Phase A Energie (eingespeist)"),
    ("b_total_act_energy",      "Phase B Energie (bezogen)"),
    ("b_total_act_ret_energy",  "Phase B Energie (eingespeist)"),
    ("c_total_act_energy",      "Phase C Energie (bezogen)"),
    ("c_total_act_ret_energy",  "Phase C Energie (eingespeist)"),
    ("total_act",               "Gesamtenergie (bezogen)"),
    ("total_act_ret",           "Gesamtenergie (eingespeist)"),
]

for _sk, _name in _EM3_ENERGY_FIELDS:
    EM3_SENSORS.append(ShellySensorDescription(
        key=f"emdata_{_sk}",
        name=_name,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=(lambda s, sub=_sk: _rpc(s, "emdata:0", sub)),
    ))


# ──────────────────────────────────────────────────────────────────────────────
# Switch-Leistungsmessung (Plus 1PM, Pro 1PM, Pro 2PM …)
# Key: switch:N  —  Felder: apower, voltage, current, aenergy{total}
# ──────────────────────────────────────────────────────────────────────────────

def _switch_sensors(ch: int) -> list[ShellySensorDescription]:
    comp = f"switch:{ch}"
    label = f"Kanal {ch + 1} " if ch > 0 else ""
    return [
        ShellySensorDescription(
            key=f"switch{ch}_power",
            name=f"{label}Leistung",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, c=comp: _rpc(s, c, "apower"),
        ),
        ShellySensorDescription(
            key=f"switch{ch}_voltage",
            name=f"{label}Spannung",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, c=comp: _rpc(s, c, "voltage"),
        ),
        ShellySensorDescription(
            key=f"switch{ch}_current",
            name=f"{label}Strom",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, c=comp: _rpc(s, c, "current"),
        ),
        ShellySensorDescription(
            key=f"switch{ch}_energy",
            name=f"{label}Energie",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            # aenergy ist ein Dict: {"total": ..., "by_minute": [...]}
            value_fn=lambda s, c=comp: _rpc_nested(s, c, "aenergy", "total"),
        ),
        ShellySensorDescription(
            key=f"switch{ch}_temperature",
            name=f"{label}Temperatur (intern)",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, c=comp: _rpc_nested(s, c, "temperature", "tC"),
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Gen1 Block-Energiezähler  →  emeters[]
# ──────────────────────────────────────────────────────────────────────────────

def _block_emeter_sensors(idx: int) -> list[ShellySensorDescription]:
    labels = ["Phase A", "Phase B", "Phase C"]
    label = labels[idx] if idx < len(labels) else f"Kanal {idx + 1}"
    return [
        ShellySensorDescription(
            key=f"emeter{idx}_power",
            name=f"{label} Leistung",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _block(s, i, "power"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_voltage",
            name=f"{label} Spannung",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _block(s, i, "voltage"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_current",
            name=f"{label} Strom",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _block(s, i, "current"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_pf",
            name=f"{label} Leistungsfaktor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda s, i=idx: _block(s, i, "pf"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_total",
            name=f"{label} Energie (bezogen)",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda s, i=idx: _block(s, i, "total"),
        ),
        ShellySensorDescription(
            key=f"emeter{idx}_total_returned",
            name=f"{label} Energie (eingespeist)",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_fn=lambda s, i=idx: _block(s, i, "total_returned"),
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Allgemeine Sensoren: Temperatur, Feuchte, Batterie
# ──────────────────────────────────────────────────────────────────────────────

GENERAL_SENSORS: list[ShellySensorDescription] = [
    ShellySensorDescription(
        key="temperature",
        name="Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            _rpc_nested(s, "temperature:0", None, "tC")
            or _rpc(s, "temperature:0", "tC")
            or (s.get("tmp") or {}).get("value")
        ),
    ),
    ShellySensorDescription(
        key="humidity",
        name="Luftfeuchtigkeit",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            _rpc(s, "humidity:0", "rh")
            or (s.get("hum") or {}).get("value")
        ),
    ),
    ShellySensorDescription(
        key="battery",
        name="Batterie",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: (
            _rpc_nested(s, "devicepower:0", "battery", "percent")
            or (s.get("bat") or {}).get("value")
        ),
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Sensor-Erkennung pro Gerät
# ──────────────────────────────────────────────────────────────────────────────

def _build_sensors_for_device(
    coordinator: ShellyCloudCoordinator, device_id: str
) -> list["ShellyCloudSensor"]:
    dev_data = coordinator.data.get(device_id, {})
    status = dev_data.get("status", {})
    entities: list[ShellyCloudSensor] = []

    # Pro 3EM (Gen2 RPC): em:0 oder emdata:0 vorhanden
    if "em:0" in status or "emdata:0" in status:
        for desc in EM3_SENSORS:
            if desc.value_fn(status) is not None:
                entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    # Gen1 Block-Energiezähler: emeters-Array
    for idx, _ in enumerate(status.get("emeters", [])):
        for desc in _block_emeter_sensors(idx):
            if desc.value_fn(status) is not None:
                entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    # Switch-Leistungsmessung (Gen2): switch:N mit apower-Feld
    for ch in range(4):  # max. 4 Kanäle
        comp_key = f"switch:{ch}"
        comp = status.get(comp_key, {})
        if isinstance(comp, dict) and "apower" in comp:
            for desc in _switch_sensors(ch):
                if desc.value_fn(status) is not None:
                    entities.append(ShellyCloudSensor(coordinator, device_id, desc))

    # Allgemeine Sensoren: Temperatur, Feuchte, Batterie
    for desc in GENERAL_SENSORS:
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
