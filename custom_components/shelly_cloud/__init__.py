"""Shelly Cloud Integration für Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShellyCloudApi, ShellyCloudApiError, ShellyCloudAuthError
from .config_flow import ShellyCloudOptionsFlow
from .const import (
    CONF_AUTH_KEY,
    CONF_DEVICES,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import ShellyCloudCoordinator

_LOGGER = logging.getLogger(__name__)

type ShellyCloudConfigEntry = ConfigEntry[ShellyCloudCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ShellyCloudConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = ShellyCloudApi(
        session,
        entry.data[CONF_AUTH_KEY],
        entry.data[CONF_SERVER_URL],
    )

    devices = entry.options.get(CONF_DEVICES, [])
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = ShellyCloudCoordinator(hass, api, devices, scan_interval)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryAuthFailed:
        raise
    except Exception as exc:
        raise ConfigEntryNotReady from exc

    entry.runtime_data = coordinator

    # Bei Änderungen der Options (Gerät hinzugefügt/entfernt) neu laden
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: ShellyCloudConfigEntry
) -> None:
    """Wird aufgerufen wenn Options (Geräteliste) geändert wurden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ShellyCloudConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
