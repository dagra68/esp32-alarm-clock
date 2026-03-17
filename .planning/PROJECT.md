# ESP32 Smart Alarm Clock

## What This Is

Ein ESPHome-basierter Wecker auf dem LilyGo T-RGB (ESP32-S3, rundes Touch-Display 2.1"/2.8"), der Wochentag-Alarme mit RTTTL-Melodien abspielt und sich vollständig in Home Assistant integriert. Der Nutzer kann den Alarm per Touch und physischer Taste bedienen, während Home Assistant den Alarm automatisch an Feiertagen deaktivieren kann.

## Core Value

Der Wecker weckt zuverlässig an Wochentagen und lässt sich über Home Assistant automatisch an Feiertagen stumm schalten — ohne manuellen Eingriff.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Uhrzeit wird per NTP über WLAN synchronisiert
- [ ] Rundes Display zeigt analoge Uhr (Zeiger) und digitale Uhr (Zahlen)
- [ ] Nutzer kann per Touch zwischen analogem und digitalem Zifferblatt wechseln
- [ ] Wochentag-Alarm (Mo–Fr) konfigurierbar über Touch-Interface
- [ ] Alarm-Ein/Aus-Status wird als Switch in Home Assistant exponiert (ESPHome)
- [ ] Home Assistant kann den Alarm per Automatisierung deaktivieren (z. B. Feiertage)
- [ ] Alarm tönt als RTTTL-Melodie über I2S-Lautsprecher
- [ ] Physische Taste löst Snooze (5 Minuten) aus
- [ ] Snooze-Funktion verzögert Alarm um 5 Minuten
- [ ] Alarm kann per Touch dauerhaft ausgeschaltet werden

### Out of Scope

- Wochenend-Alarm — explizit nicht gewünscht, nur Mo–Fr
- MP3/WAV-Wiedergabe — RTTTL ist ausreichend und einfacher
- Web-Interface zur Konfiguration — HA + Touch ersetzt das
- RTC-Modul (DS3231) — NTP genügt, kein Batterie-Backup nötig

## Context

- **Hardware:** LilyGo T-RGB ESP32-S3, rundes Touch-Display (GC9A01 oder ST77916), I2S-Lautsprecher, 1 physische Taste
- **Firmware:** ESPHome (YAML + Lambda für Display-Rendering)
- **Integration:** Home Assistant via ESPHome native API
- **Display-Bibliothek:** ESPHome LVGL-Komponente oder custom Lambda mit LVGL/TFT_eSPI
- **Zeitzone:** Muss in ESPHome konfiguriert werden (z. B. Europe/Berlin)
- Das runde Display erfordert Polar-Koordinaten für analoge Uhrzeiger-Darstellung

## Constraints

- **Hardware:** LilyGo T-RGB — pinout und Display-Treiber sind spezifisch für dieses Board
- **Firmware:** Ausschließlich ESPHome — kein PlatformIO/Arduino-Code außerhalb von Lambdas
- **Audio:** I2S-Lautsprecher — kein externer DAC sofern ESP32-S3 internen I2S nutzt
- **HA-Kompatibilität:** Alarm-Switch muss als `switch` Entity in ESPHome definiert sein

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ESPHome als Basis | Native HA-Integration, kein Custom-Protokoll nötig | — Pending |
| RTTTL statt MP3 | Einfacher, kein Dateisystem nötig, ESPHome-nativ | — Pending |
| NTP statt RTC | Ausreichend wenn WLAN verfügbar, weniger Hardware | — Pending |
| Snooze per Taste | Klassisches Wecker-UX, Touch für alles andere | — Pending |

---
*Last updated: 2026-03-17 after initialization*
