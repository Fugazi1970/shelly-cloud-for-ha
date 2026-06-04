"""Config Flow und Options Flow für Shelly Cloud."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import ShellyCloudApi, ShellyCloudApiError, ShellyCloudAuthError
from .const import (
    CONF_AUTH_KEY,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DEVICES,
    CONF_SERVER_URL,
    DOMAIN,
)


class ShellyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    @staticmethod
    def async_get_options_flow(config_entry):
        return ShellyCloudOptionsFlow()


    """Schritt 1: Server + Auth Key. Schritt 2: erstes Gerät hinzufügen."""

    VERSION = 1

    def __init__(self) -> None:
        self._server_url: str = ""
        self._auth_key: str = ""

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            server_url = user_input[CONF_SERVER_URL].rstrip("/")
            auth_key = user_input[CONF_AUTH_KEY]

            session = async_get_clientsession(self.hass)
            api = ShellyCloudApi(session, auth_key, server_url)
            try:
                await api.validate_credentials()
            except ShellyCloudAuthError:
                errors["base"] = "invalid_auth"
            except ShellyCloudApiError:
                errors["base"] = "cannot_connect"
            else:
                self._server_url = server_url
                self._auth_key = auth_key
                return await self.async_step_add_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SERVER_URL): str,
                vol.Required(CONF_AUTH_KEY): str,
            }),
            errors=errors,
        )

    async def async_step_add_device(self, user_input=None):
        """Erstes Gerät hinzufügen (oder überspringen)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input.get(CONF_DEVICE_ID, "").strip()
            device_name = user_input.get(CONF_DEVICE_NAME, "").strip()

            if device_id:
                # Gerät kurz prüfen
                session = async_get_clientsession(self.hass)
                api = ShellyCloudApi(session, self._auth_key, self._server_url)
                try:
                    result = await api.get_devices_status([device_id])
                    if not result:
                        errors[CONF_DEVICE_ID] = "device_not_found"
                except ShellyCloudApiError:
                    errors[CONF_DEVICE_ID] = "device_not_found"

            if not errors:
                devices = []
                if device_id:
                    devices.append({
                        CONF_DEVICE_ID: device_id,
                        CONF_DEVICE_NAME: device_name or device_id,
                    })

                await self.async_set_unique_id(self._auth_key[:16])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Shelly Cloud",
                    data={
                        CONF_SERVER_URL: self._server_url,
                        CONF_AUTH_KEY: self._auth_key,
                    },
                    options={CONF_DEVICES: devices},
                )

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Optional(CONF_DEVICE_ID): str,
                vol.Optional(CONF_DEVICE_NAME): str,
            }),
            description_placeholders={
                "hint": "Device ID in der Shelly App unter Gerät → Einstellungen → Geräteinformation"
            },
            errors=errors,
            last_step=True,
        )


class ShellyCloudOptionsFlow(config_entries.OptionsFlow):
    """Geräte hinzufügen oder entfernen."""

    def __init__(self) -> None:
        self._action: str = ""
        self._remove_id: str = ""

    async def async_step_init(self, user_input=None):
        devices: list[dict] = self.config_entry.options.get(CONF_DEVICES, [])

        if not devices:
            # Keine Geräte vorhanden → direkt zum Hinzufügen
            return await self.async_step_add_device()

        options = {
            "add": "Gerät hinzufügen",
            **{d[CONF_DEVICE_ID]: f"Entfernen: {d.get(CONF_DEVICE_NAME, d[CONF_DEVICE_ID])}"
               for d in devices},
        }

        if user_input is not None:
            action = user_input["action"]
            if action == "add":
                return await self.async_step_add_device()
            else:
                self._remove_id = action
                return await self.async_step_remove_device()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action"): vol.In(options),
            }),
            description_placeholders={
                "devices": "\n".join(
                    f"• {d.get(CONF_DEVICE_NAME, d[CONF_DEVICE_ID])} ({d[CONF_DEVICE_ID]})"
                    for d in devices
                ) or "–"
            },
        )

    async def async_step_add_device(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input.get(CONF_DEVICE_ID, "").strip()
            device_name = user_input.get(CONF_DEVICE_NAME, "").strip()

            if not device_id:
                errors[CONF_DEVICE_ID] = "device_id_required"
            else:
                session = async_get_clientsession(self.hass)
                api = ShellyCloudApi(
                    session,
                    self.config_entry.data[CONF_AUTH_KEY],
                    self.config_entry.data[CONF_SERVER_URL],
                )
                try:
                    result = await api.get_devices_status([device_id])
                    if not result:
                        errors[CONF_DEVICE_ID] = "device_not_found"
                except ShellyCloudApiError:
                    errors[CONF_DEVICE_ID] = "device_not_found"

            if not errors:
                devices: list[dict] = list(
                    self.config_entry.options.get(CONF_DEVICES, [])
                )
                # Doppelte IDs verhindern
                if any(d[CONF_DEVICE_ID] == device_id for d in devices):
                    errors[CONF_DEVICE_ID] = "already_configured"

            if not errors:
                devices.append({
                    CONF_DEVICE_ID: device_id,
                    CONF_DEVICE_NAME: device_name or device_id,
                })
                return self.async_create_entry(
                    data={**self.config_entry.options, CONF_DEVICES: devices}
                )

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_ID): str,
                vol.Optional(CONF_DEVICE_NAME): str,
            }),
            description_placeholders={
                "hint": "Device ID in der Shelly App unter Gerät → Einstellungen → Geräteinformation"
            },
            errors=errors,
        )

    async def async_step_remove_device(self, user_input=None):
        if user_input is not None:
            if user_input.get("confirm"):
                devices = [
                    d for d in self.config_entry.options.get(CONF_DEVICES, [])
                    if d[CONF_DEVICE_ID] != self._remove_id
                ]
                return self.async_create_entry(
                    data={**self.config_entry.options, CONF_DEVICES: devices}
                )
            return await self.async_step_init()

        device = next(
            (d for d in self.config_entry.options.get(CONF_DEVICES, [])
             if d[CONF_DEVICE_ID] == self._remove_id),
            {CONF_DEVICE_NAME: self._remove_id},
        )
        name = device.get(CONF_DEVICE_NAME, self._remove_id)

        return self.async_show_form(
            step_id="remove_device",
            data_schema=vol.Schema({vol.Required("confirm", default=False): bool}),
            description_placeholders={"device_name": name, "device_id": self._remove_id},
        )
