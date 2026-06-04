"""Config Flow für Shelly Cloud Integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShellyCloudApi, ShellyCloudApiError, ShellyCloudAuthError
from .const import CONF_AUTH_KEY, CONF_SERVER_URL, DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVER_URL, description={"suggested_value": "https://shelly-X-eu.shelly.cloud"}): str,
        vol.Required(CONF_AUTH_KEY): str,
    }
)


class ShellyCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow Handler."""

    VERSION = 1

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
                await self.async_set_unique_id(auth_key[:16])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Shelly Cloud",
                    data={
                        CONF_SERVER_URL: server_url,
                        CONF_AUTH_KEY: auth_key,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
