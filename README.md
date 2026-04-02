# ESP32 Alarm Clock

ESPHome configuration for an analog alarm clock based on the **LilyGo T-RGB 2.1"** (round display, ESP32-S3). Fully integrated with Home Assistant.

## Hardware

| Component | Details |
|---|---|
| Board | LilyGo T-RGB 2.1" |
| MCU | ESP32-S3 (16 MB Flash, PSRAM Octal 80 MHz) |
| Display | MIPI-RGB, 480×480, round |
| Touch | FT5x06 (I2C) |
| Buzzer | Passive, GPIO38 (LEDC, formerly SD card pin) |
| Backlight | GPIO46 (LEDC, dimmable) |
| IO Expander | XL9535 (display reset, SPI) |

## Features

- **Analog clock** — LVGL meter with hour and minute hands
- **Alarm** — weekdays only or daily, time configurable via touch or Home Assistant
- **RTTTL melodies** — Reveille, Entertainer, Frere Jacques (selectable)
- **Snooze** — 5 minutes, repeatable
- **Auto-stop** — alarm stops automatically after 5 minutes
- **Display sleep** — backlight turns off after 2 minutes of inactivity, returns to main page
- **Wake-on-touch** — first touch only wakes the display (no accidental button tap)
- **5 hand styles** — Classic, White, Red, Gold, Neon (via HA select)
- **4 background colors** — Pink, White, Black, Dark Blue

## Home Assistant Entities

| Type | Name | Description |
|---|---|---|
| `switch` | Alarm aktiv | Enable/disable alarm |
| `switch` | Nur Mo-Fr | Weekday filter |
| `datetime` | Alarmzeit | Set alarm time |
| `select` | Alarm Melodie | Choose melody |
| `select` | Zeiger Design | Choose hand style |
| `select` | Hintergrundfarbe | Choose dial color |
| `light` | Display Backlight | Control brightness |

## Pages (LVGL)

```
analog_clock_page     → Main page: analog clock
alarm_settings_page   → Set alarm time + weekday filter (access: tap gear icon)
alarm_ringing_page    → Alarm ringing: Snooze / Stop
```

## Touch Controls

| Gesture | Action |
|---|---|
| Tap alarm label | Toggle alarm on/off |
| Tap gear icon | Open settings page |
| Tap Mo-Fr toggle | Toggle weekday filter on/off |
| Tap "OK" | Confirm settings, return to clock |
| Tap "Snooze 5min" | Snooze alarm for 5 minutes |
| Tap "Stopp" | Stop alarm |
| Any touch (display sleeping) | Wake display only (no button action) |

## Installation

1. Create `secrets.yaml`:

```yaml
api_key: "your_api_key"
ota_password: "your_ota_password"
wifi_ssid: "your_wifi"
wifi_password: "your_wifi_password"
fallback_password: "fallback_password"
```

2. Flash firmware:

```bash
esphome run alarm-clock.yaml --device COMx
```

## Project Structure

```
alarm-clock.yaml   # ESPHome configuration
secrets.yaml       # Credentials (not in repo)
.planning/         # GSD planning documents
```
