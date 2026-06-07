# Shelly Cloud für Home Assistant

[🇬🇧 English](README.md) | 🇩🇪 Deutsch

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/badge/version-1.0.0--alpha.2-blue.svg)
![status](https://img.shields.io/badge/status-alpha-orange.svg)

Home Assistant Integration zur Steuerung von Shelly-Geräten über die **Shelly Cloud API v2** – also über die Cloud, **ohne lokalen Zugriff** auf die Geräte.

> ⚠️ **Alpha-Version.** Funktionsfähig, aber noch in Erprobung. Über Rückmeldungen und Issues freue ich mich.

## Wofür ist das gedacht?

Diese Integration ist für **entfernte Shellys**, die nicht im lokalen Netz erreichbar sind (z. B. in einem Ferienhaus, bei Verwandten oder hinter einem anderen Router). Geräte werden **einzeln und gezielt** per Device ID hinzugefügt.

Für Shellys im eigenen Netzwerk ist die [offizielle Shelly-Integration](https://www.home-assistant.io/integrations/shelly/) die bessere Wahl – beide lassen sich problemlos parallel betreiben.

## Features

- Steuerung über die Shelly Cloud (kein lokaler Netzwerkzugriff nötig)
- Geräte werden **gezielt einzeln** per Device ID hinzugefügt und entfernt
- Automatische Erkennung des Gerätetyps anhand der Cloud-Daten
- Einstellbares Polling-Intervall: 1–60 Sekunden (Cloud-Limit: 1 Anfrage/Sekunde)

### Unterstützte Geräteklassen

| Plattform | Geräte | Funktionen |
|-----------|--------|-----------|
| **switch** | Relais, Steckdosen (z. B. Plus Plug, Pro 1/2) | Ein/Aus, mehrere Kanäle |
| **cover** | Rollladen, Jalousien | Öffnen/Schließen/Stop, Position |
| **light** | Dimmer, RGBW, Bulbs | An/Aus, Helligkeit, Farbe, Farbtemperatur, Effekte |
| **sensor** | Energiezähler & Sensoren | siehe unten |

**Sensoren im Detail:**
- **Shelly Pro 3EM / 3EM Pro** – alle 3 Phasen (Spannung, Strom, Wirk-/Scheinleistung, Leistungsfaktor, Frequenz), Neutralleiter, Gesamtwerte und Energie (bezogen/eingespeist)
- **Shelly EM / 1EM** (Gen1) – Leistung, Spannung, Strom, Energie pro Kanal
- **Shelly Plus/Pro 1PM / 2PM** – Leistung, Spannung, Strom, Energie, interne Temperatur
- **Temperatur-/Feuchte-/Batterie-Sensoren** (z. B. Plus H&T)

## Installation via HACS

1. HACS öffnen → **Integrationen**
2. Rechts oben auf die drei Punkte → **Benutzerdefinierte Repositories**
3. URL: `https://github.com/Fugazi1970/shelly-cloud-for-ha` — Kategorie: **Integration**
4. **Shelly Cloud** in HACS suchen und herunterladen
5. Home Assistant neu starten

> 💡 Da dies eine Alpha-Version ist: In HACS bei der Integration **„Pre-Releases anzeigen"** aktivieren, damit Alpha-Versionen angeboten werden.

## Einrichtung

### Schritt 1 – Mit der Cloud verbinden

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Shelly Cloud**

Dort eingeben:
- **Server URL** – z. B. `https://shelly-11-eu.shelly.cloud`
- **Authorization Key**

Beides findest du in der **Shelly Cloud App** bzw. unter [control.shelly.cloud](https://control.shelly.cloud):
*Benutzereinstellungen → Zugang und Berechtigungen → Cloud-Autorisierungs-Schlüssel*

### Schritt 2 – Erstes Gerät hinzufügen

Im Anschluss kannst du direkt das erste Gerät per **Device ID** hinzufügen (oder den Schritt überspringen).

Die **Device ID** steht in der Shelly App unter:
*Gerät → Einstellungen → Geräteinformation → Device ID*

### Geräte verwalten

Über das **Zahnrad-Symbol (Konfigurieren)** bei der Integration kannst du jederzeit:
- weitere Geräte per Device ID hinzufügen
- vorhandene Geräte entfernen
- das Update-Intervall ändern (1–60 Sekunden)

Nach jeder Änderung lädt die Integration automatisch neu.

## Bekannte Einschränkungen

- Keine Echtzeit-Updates – Werte werden im eingestellten Intervall abgerufen
- Einzelne Gerätetypen liefern ggf. abweichende Felder und müssen noch ergänzt werden
- Noch keine automatisierten Tests

## API-Dokumentation

[Shelly Cloud Control API v2](https://shelly-api-docs.shelly.cloud/cloud-control-api/communication-v2)

---

Erstellt mit Hilfe von [Claude](https://claude.com/claude-code).
