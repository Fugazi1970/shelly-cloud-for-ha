# Shelly Cloud for Home Assistant

🇬🇧 English | [🇩🇪 Deutsch](README.de.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/badge/version-1.0.0--alpha.3-blue.svg)
![status](https://img.shields.io/badge/status-alpha-orange.svg)

Home Assistant integration to control Shelly devices through the **Shelly Cloud API v2** — i.e. via the cloud, **without local network access**.

> ⚠️ **Alpha release.** Working, but still being tested. Feedback and issues are very welcome.

## What is this for?

This integration is for **remote Shellys** that aren't reachable on your local network (e.g. at a holiday home, at relatives' houses, or behind another router). Devices are added **individually and on purpose** by their Device ID.

For Shellys on your own network, the [official Shelly integration](https://www.home-assistant.io/integrations/shelly/) is the better choice — both can run side by side without conflict.

## Features

- Control via the Shelly Cloud (no local network access required)
- Devices are added and removed **individually** by Device ID
- Device type is detected automatically from the cloud data
- Configurable polling interval: 1–60 seconds (cloud limit: 1 request/second)

### Supported device classes

| Platform | Devices | Functions |
|----------|---------|-----------|
| **switch** | Relays, plugs (e.g. Plus Plug, Pro 1/2) | On/off, multiple channels |
| **cover** | Roller shutters, blinds | Open/close/stop, position |
| **light** | Dimmers, RGBW, bulbs | On/off, brightness, color, color temperature, effects |
| **sensor** | Energy meters & sensors | see below |

**Sensors in detail:**
- **Shelly Pro 3EM / 3EM Pro** — all 3 phases (voltage, current, active/apparent power, power factor, frequency), neutral, totals and energy (consumed/returned)
- **Shelly EM / 1EM** (Gen1) — power, voltage, current, energy per channel
- **Shelly Plus/Pro 1PM / 2PM** — power, voltage, current, energy, internal temperature
- **Temperature / humidity / battery sensors** (e.g. Plus H&T)

## Installation via HACS

1. Open HACS → **Integrations**
2. Top-right three dots → **Custom repositories**
3. URL: `https://github.com/Fugazi1970/shelly-cloud-for-ha` — Category: **Integration**
4. Search for **Shelly Cloud** in HACS and download it
5. Restart Home Assistant

> 💡 Since this is an alpha release: enable **"show beta versions"** on the integration in HACS so alpha versions are offered.

## Setup

### Step 1 — Connect to the cloud

**Settings → Devices & Services → Add Integration → Shelly Cloud**

Enter:
- **Server URL** — e.g. `https://shelly-11-eu.shelly.cloud`
- **Authorization Key**

Both are found in the **Shelly Cloud app** / at [control.shelly.cloud](https://control.shelly.cloud):
*User Settings → Access and Permissions → Cloud Authorization Key*

### Step 2 — Add your first device

Right after, you can add the first device by its **Device ID** (or skip this step).

The **Device ID** is shown in the Shelly app under:
*Device → Settings → Device Information → Device ID*

### Managing devices

Via the **gear icon (Configure)** on the integration you can at any time:
- add more devices by Device ID
- remove existing devices
- change the update interval (1–60 seconds)

The integration reloads automatically after each change.

## Known limitations

- No real-time updates — values are polled at the configured interval
- Some device types may return different fields and still need small tweaks
- No automated tests yet

## API documentation

[Shelly Cloud Control API v2](https://shelly-api-docs.shelly.cloud/cloud-control-api/communication-v2)

---

Built with the help of [Claude](https://claude.com/claude-code).
