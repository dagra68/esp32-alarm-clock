# ESP32 Alarm Clock

ESPHome-Konfiguration für einen analogen Wecker auf Basis des **LilyGo T-RGB 2.1"** (rundes Display, ESP32-S3). Vollständig in Home Assistant integriert.

## Hardware

| Komponente | Details |
|---|---|
| Board | LilyGo T-RGB 2.1" |
| MCU | ESP32-S3 (16 MB Flash, PSRAM Octal 80 MHz) |
| Display | MIPI-RGB, 480×480, rund |
| Touch | FT5x06 (I2C) |
| Buzzer | Passiv, GPIO4 (LEDC) |
| Backlight | GPIO46 (LEDC, dimmbar) |
| IO-Expander | XL9535 (Display-Reset, SPI) |

## Features

- **Analoge Uhr** — LVGL-Meter mit Stunden- und Minutenzeiger
- **Alarm** — Mo–Fr oder täglich, einstellbare Uhrzeit per Home Assistant
- **RTTTL-Melodien** — Reveille, Entertainer, Frere Jacques (auswählbar)
- **Snooze** — 5 Minuten, beliebig oft
- **Auto-Stop** — Alarm stoppt nach 5 Minuten automatisch
- **Display-Timeout** — Backlight schaltet nach 3 Minuten Inaktivität ab
- **Wake-on-Touch** — Beliebiger Touch weckt das Display wieder auf
- **5 Zeiger-Designs** — Klassisch, Weiss, Rot, Gold, Neon (per HA-Select)
- **4 Hintergrundfarben** — Pink, Weiss, Schwarz, Dunkelblau

## Home Assistant Entities

| Typ | Name | Beschreibung |
|---|---|---|
| `switch` | Alarm aktiv | Alarm ein/aus |
| `switch` | Nur Mo-Fr | Wochentag-Filter |
| `datetime` | Alarmzeit | Weckzeit einstellen |
| `select` | Alarm Melodie | Melodie wählen |
| `select` | Zeiger Design | Zeiger-Stil wählen |
| `select` | Hintergrundfarbe | Zifferblatt-Farbe |
| `light` | Display Backlight | Helligkeit steuern |

## Seiten (LVGL)

```
analog_clock_page     → Hauptseite: analoge Uhr
alarm_settings_page   → Alarmzeit einstellen (Zugang: Long-Press auf Alarm-Label)
alarm_ringing_page    → Alarm klingelt: Snooze / Stopp
```

## Touch-Bedienung

| Geste | Aktion |
|---|---|
| Tap auf Alarm-Label | Alarm ein/aus |
| Long-Press auf Alarm-Label | Alarmzeit einstellen |
| Tap auf "Snooze 5min" | Alarm 5 Minuten pausieren |
| Tap auf "Stopp" | Alarm beenden |
| Beliebiger Touch | Display aufwecken |

## Installation

1. `secrets.yaml` anlegen:

```yaml
api_key: "dein_api_key"
ota_password: "dein_ota_passwort"
wifi_ssid: "dein_wlan"
wifi_password: "dein_wlan_passwort"
fallback_password: "fallback_passwort"
```

2. Firmware flashen:

```bash
esphome run alarm-clock.yaml --device COMx
```

## Projektstruktur

```
alarm-clock.yaml   # ESPHome-Konfiguration
secrets.yaml       # Zugangsdaten (nicht im Repo)
.planning/         # GSD Planungsdokumente
```
