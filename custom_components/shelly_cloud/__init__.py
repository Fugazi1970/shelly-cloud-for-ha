"""Shelly Cloud Integration für Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShellyCloudApi, ShellyCloudApiError, ShellyCloudAuthError
from .const import CONF_AUTH_KEY, CONF_SERVER_URL, DOMAIN, PLATFORMS
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

    coordinator = ShellyCloudCoordinator(hass, api)

    try:
        await coordinator.async_setup()
    except ShellyCloudAuthError as exc:
        raise ConfigEntryAuthFailed from exc
    except ShellyCloudApiError as exc:
        raise ConfigEntryNotReady from exc

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ShellyCloudConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
