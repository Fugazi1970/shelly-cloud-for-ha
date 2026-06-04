"""Shelly Cloud API v2 Client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 10
MAX_DEVICES_PER_REQUEST = 10


class ShellyCloudApiError(Exception):
    pass


class ShellyCloudAuthError(ShellyCloudApiError):
    pass


class ShellyCloudApi:
    """Client für die Shelly Cloud API v2."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        auth_key: str,
        server_url: str,
    ) -> None:
        self._session = session
        self._auth_key = auth_key
        # Trailing-Slash entfernen
        self._server_url = server_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self._server_url}{path}"

    async def _post(self, path: str, body: dict[str, Any]) -> Any:
        url = self._url(path)
        params = {"auth_key": self._auth_key}
        try:
            async with self._session.post(
                url, params=params, json=body, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            ) as resp:
                if resp.status == 401:
                    raise ShellyCloudAuthError("Ungültiger Auth Key")
                if resp.status != 200:
                    text = await resp.text()
                    raise ShellyCloudApiError(f"HTTP {resp.status}: {text}")
                # Manche Endpoints liefern leere Antwort bei Erfolg
                if resp.content_length == 0 or resp.content_type != "application/json":
                    return {}
                data = await resp.json()
                if isinstance(data, dict) and "error" in data:
                    raise ShellyCloudApiError(data["error"])
                return data
        except asyncio.TimeoutError as exc:
            raise ShellyCloudApiError("Timeout bei API-Anfrage") from exc
        except aiohttp.ClientError as exc:
            raise ShellyCloudApiError(f"Verbindungsfehler: {exc}") from exc

    async def get_devices_status(self, device_ids: list[str]) -> list[dict[str, Any]]:
        """Status von bis zu 10 Geräten gleichzeitig abrufen."""
        results: list[dict[str, Any]] = []
        # In Batches von MAX_DEVICES_PER_REQUEST aufteilen
        for i in range(0, len(device_ids), MAX_DEVICES_PER_REQUEST):
            batch = device_ids[i : i + MAX_DEVICES_PER_REQUEST]
            data = await self._post(
                "/v2/devices/api/get",
                {"ids": batch, "select": ["status", "settings"]},
            )
            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                results.append(data)
            # Rate Limit: 1 req/s
            if i + MAX_DEVICES_PER_REQUEST < len(device_ids):
                await asyncio.sleep(1)
        return results

    async def list_devices(self) -> list[dict[str, Any]]:
        """Alle Geräte des Accounts abrufen (v1 Endpoint)."""
        url = self._url("/interface/device/list")
        params = {"auth_key": self._auth_key}
        try:
            async with self._session.post(
                url,
                params=params,
                json={},
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                if resp.status == 401:
                    raise ShellyCloudAuthError("Ungültiger Auth Key")
                if resp.status != 200:
                    text = await resp.text()
                    raise ShellyCloudApiError(f"HTTP {resp.status}: {text}")
                data = await resp.json()
        except asyncio.TimeoutError as exc:
            raise ShellyCloudApiError("Timeout bei API-Anfrage") from exc
        except aiohttp.ClientError as exc:
            raise ShellyCloudApiError(f"Verbindungsfehler: {exc}") from exc

        if isinstance(data, dict):
            if data.get("isok") is False:
                raise ShellyCloudApiError(data.get("errors", "Unbekannter Fehler"))
            devices = data.get("data", {}).get("devices", {})
            return list(devices.values()) if isinstance(devices, dict) else devices
        return []

    async def set_switch(
        self, device_id: str, on: bool, channel: int = 0, toggle_after: int | None = None
    ) -> None:
        body: dict[str, Any] = {"id": device_id, "channel": channel, "on": on}
        if toggle_after is not None:
            body["toggle_after"] = toggle_after
        await self._post("/v2/devices/api/set/switch", body)

    async def set_cover(
        self,
        device_id: str,
        position: str | int,
        duration: int | None = None,
    ) -> None:
        body: dict[str, Any] = {"id": device_id, "position": position}
        if duration is not None:
            body["duration"] = duration
        await self._post("/v2/devices/api/set/cover", body)

    async def set_light(
        self,
        device_id: str,
        on: bool | None = None,
        brightness: int | None = None,
        temperature: int | None = None,
        red: int | None = None,
        green: int | None = None,
        blue: int | None = None,
        mode: str | None = None,
        effect: int | None = None,
    ) -> None:
        body: dict[str, Any] = {"id": device_id}
        if on is not None:
            body["on"] = on
        if brightness is not None:
            body["brightness"] = brightness
        if temperature is not None:
            body["temperature"] = temperature
        if red is not None:
            body["red"] = red
        if green is not None:
            body["green"] = green
        if blue is not None:
            body["blue"] = blue
        if mode is not None:
            body["mode"] = mode
        if effect is not None:
            body["effect"] = effect
        await self._post("/v2/devices/api/set/light", body)

    async def validate_credentials(self) -> bool:
        """Credentials testen, indem die Geräteliste abgerufen wird."""
        await self.list_devices()
        return True
