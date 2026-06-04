# Shelly Cloud for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant Integration zur Steuerung von Shelly-Geräten über die **Shelly Cloud API v2** (kein lokaler Zugriff erforderlich).

## Features

- Schalter / Steckdosen (mehrere Kanäle)
- Rollladen / Jalousien (inkl. Positionssteuerung)
- Leuchtmittel (RGB, Farbtemperatur, Helligkeit, Effekte)
- Automatische Geräteerkennung über die Shelly Cloud
- Polling-Intervall: 30 Sekunden

## Installation via HACS

1. HACS öffnen → **Integrationen**
2. Rechts oben auf die drei Punkte → **Benutzerdefinierte Repositories**
3. URL: `https://github.com/Fugazi1970/shelly-cloud-for-ha` — Kategorie: **Integration**
4. **Shelly Cloud** in HACS suchen und installieren
5. Home Assistant neu starten

## Einrichtung

1. **Einstellungen → Integrationen → + Hinzufügen → Shelly Cloud**
2. **Server URL** und **Authorization Key** eingeben
   - Beides in der Shelly Cloud App unter *Benutzereinstellungen → Authorization cloud key*

## API-Dokumentation

[Shelly Cloud Control API v2](https://shelly-api-docs.shelly.cloud/cloud-control-api/communication-v2)
