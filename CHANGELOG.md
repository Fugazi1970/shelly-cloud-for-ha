# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier dokumentiert.

Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionierung folgt [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0-alpha.3] – 2026-06-17

### Behoben
- Shelly Gen2/Plus-Geräte (z. B. Shelly Plus 1 Mini) wurden nicht als `switch`-Entität erkannt,
  wenn ihr Status via RPC-Keys (`switch:0`, `switch:1` …) gemeldet wird statt über das
  Legacy-Array `switches`/`relays`. Dank Beitrag von [@TomTomNavigator](https://github.com/TomTomNavigator).

## [1.0.0-alpha.2] – 2026-06-04

### Hinzugefügt
- Update-Intervall ist jetzt einstellbar (1–60 Sekunden) über den
  Optionen-Dialog der Integration. Standard bleibt 30 Sekunden.

## [1.0.0-alpha.1] – 2026-06-04

Erste Alpha-Version. Funktionsfähig, aber noch in Erprobung.

### Hinzugefügt
- Anbindung an die Shelly Cloud Control API v2 (kein lokaler Zugriff nötig)
- Einrichtung über die Oberfläche: Server-URL + Authorization Key
- Manuelles Hinzufügen einzelner Geräte per Device ID (Options-Dialog)
- Entfernen von Geräten über den Options-Dialog
- Plattform **switch** – Relais und Steckdosen (mehrere Kanäle)
- Plattform **cover** – Rollläden und Jalousien inkl. Positionssteuerung
- Plattform **light** – RGB, Farbtemperatur, Helligkeit, Effekte
- Plattform **sensor**:
  - Shelly Pro 3EM / 3EM Pro (alle 3 Phasen, Neutralleiter, Gesamtwerte, Energie)
  - Shelly EM / 1EM (Gen1)
  - Shelly Plus/Pro 1PM / 2PM (Leistung, Spannung, Strom, Energie, interne Temperatur)
  - Temperatur-, Feuchte- und Batterie-Sensoren (z. B. Plus H&T)
- Automatische Erkennung des Gerätetyps anhand des API-Responses
- Polling alle 30 Sekunden (Rate-Limit: 1 Anfrage/Sekunde)

### Bekannte Einschränkungen
- Keine Echtzeit-Updates (nur Polling über die Cloud)
- Gerätetypen müssen ggf. noch ergänzt werden, wenn Felder abweichen
- Noch keine automatisierten Tests
