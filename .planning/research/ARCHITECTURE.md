# Architecture Patterns

**Domain:** ESPHome-basierter Smart Alarm Clock auf LilyGo T-RGB (ESP32-S3)
**Researched:** 2026-03-17 (Stack-Research Update)

## Recommended Architecture

Das System folgt einer komponentenbasierten Architektur, die durch ESPHomes YAML-Konfiguration mit Packages strukturiert wird. Jede logische Einheit (Display, Audio, Alarm-Logik, HA-Integration) lebt in einer separaten YAML-Datei.

### High-Level Systemdiagramm

```
+------------------+     +------------------+     +------------------+
|   Home Assistant |<--->|  ESPHome Native  |<--->|   ESP32-S3       |
|   (Feiertag-     |     |  API Component   |     |   (LilyGo T-RGB) |
|    Automation)   |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                                        |
                   +-----------------------------------+-----------------------------------+
                   |                   |                   |                   |
           +-------v------+   +-------v------+   +-------v------+   +-------v------+
           |   Display    |   |    Audio     |   |  Alarm Logic |   |    Input      |
           |  (LVGL +     |   | (LEDC PWM + |   |  (Time +     |   |  (CST816/820 +|
           |   MIPI RGB)  |   |   RTTTL)    |   |   Globals)   |   |   Taste)     |
           +--------------+   +--------------+   +--------------+   +--------------+
```

**WICHTIG: Audio ist LEDC PWM + Passiver Buzzer, NICHT I2S-Speaker.** Die T-RGB hat keine freien GPIOs fuer I2S (braucht 3 Pins). RTTTL mit LEDC-Output braucht nur 1 GPIO.

### YAML Package-Struktur

```
alarm-clock/
  alarm-clock.yaml          # Hauptdatei: Board, WiFi, API, Packages
  packages/
    board.yaml               # ESP32-S3, PSRAM, XL9535, I2C
    display.yaml             # MIPI RGB + LVGL Konfiguration
    audio.yaml               # LEDC Output + RTTTL
    alarm.yaml               # Alarm-Logik, Globals, Template Datetime/Switch
    input.yaml               # Touchscreen + physische Taste
    common.yaml              # WiFi, OTA, Logger, API
```

**Rationale:** ESPHome's Package-System merged YAML-Dateien intelligent (Dictionaries per Key, Listen per ID). Jedes Package kann isoliert getestet werden.

### Component Boundaries

| Component | Responsibility | Communicates With | ESPHome Components |
|-----------|---------------|-------------------|--------------------|
| **Board** | I2C-Bus, XL9535 Expander, PSRAM, Backlight | Alle (Hardware-Basis) | `i2c`, `xl9535`, `psram`, `output` (ledc) |
| **Display** | Uhr-Rendering (analog/digital), Alarm-Overlay, UI-Feedback | Alarm Logic, Input | `mipi_rgb` (model: T-RGB-2.1), `lvgl`, `font` |
| **Audio** | RTTTL-Melodie abspielen ueber Piezo-Buzzer | Alarm Logic | `output` (ledc), `rtttl` |
| **Alarm Logic** | Alarm-Zeitpunkt pruefen, Snooze verwalten, Alarm-Status | Audio, Display, HA | `time` (SNTP/HA), `template datetime`, `globals`, `switch`, `script` |
| **Input** | Touch-Events auf LVGL-Widgets, physische Taste (Snooze) | Alarm Logic, Display | `cst816`/`gt911` (Touch), `binary_sensor` (GPIO) |
| **HA Integration** | Alarm Switch exponieren, Feiertag-Signal empfangen | Alarm Logic | `api`, `switch`, `homeassistant` (Sensor) |

### Data Flow

**Alarm-Ausloesung:**
```
SNTP on_time (jede Minute, Sekunde 0)
  -> Lambda: Stunde/Minute == Alarm-Zeit?
  -> Lambda: Wochentag Mo-Fr (day_of_week 2-6)?
  -> Lambda: alarm_enabled Switch ON?
  -> Lambda: time.now().is_valid()?
  -> JA: script.execute: alarm_ring
  -> LVGL: Top-Layer Overlay "ALARM" anzeigen
```

**Snooze:**
```
Physische Taste gedrueckt (binary_sensor on_press)
  -> script.stop: alarm_ring
  -> rtttl.stop
  -> LVGL: "Snooze 5 Min" anzeigen
  -> delay 5 Minuten (Script)
  -> script.execute: alarm_ring (erneut)
```

**Alarm aus per Touch:**
```
LVGL Button "Alarm Aus" getippt (on_click)
  -> script.stop: alarm_ring
  -> rtttl.stop
  -> globals: alarm_ringing = false
  -> LVGL: Overlay entfernen
```

**Feiertag-Deaktivierung:**
```
HA-Automatisierung erkennt Feiertag (Kalender/Workday-Sensor)
  -> Schaltet alarm_enabled Switch auf OFF
  -> Am naechsten Werktag: Switch wieder auf ON (separate HA-Automation)
```

## Patterns to Follow

### Pattern 1: Package-basierte Modularitaet
**Was:** Jede logische Einheit in separater YAML-Datei
**Wann:** Immer bei Projekten mit mehr als 3 Komponenten-Typen
**Warum:** Isoliertes Testen, uebersichtliche Struktur

### Pattern 2: LVGL Page-basierte Navigation
**Was:** Jedes Zifferblatt ist eine eigene LVGL-Page.
**Wann:** Mehrere Ansichten auf einem Display.
```yaml
lvgl:
  page_wrap: true
  pages:
    - id: analog_page
      widgets:
        - meter:
            align: CENTER
            width: 240
            height: 240
            scales:
              # Skala 1: Minuten (0-60)
              - range_from: 0
                range_to: 60
                angle_range: 360
                rotation: 270
                ticks:
                  count: 61
                  width: 1
                  length: 10
                  major:
                    stride: 5
                    width: 2
                    length: 15
                indicators:
                  - line:
                      id: minute_hand
                      width: 3
                      color: 0xFFFFFF
                      r_mod: -5
                      value: 0
              # Skala 2: Stunden-Fein (0-720, fuer natuerliche Position zwischen Stunden)
              - range_from: 0
                range_to: 720
                angle_range: 360
                rotation: 270
                indicators:
                  - line:
                      id: hour_hand
                      width: 5
                      color: 0xFFFFFF
                      r_mod: -30
                      value: 0
    - id: digital_page
      widgets:
        - label:
            id: time_label
            align: CENTER
            text_font: montserrat_48
            text: "00:00"
```

### Pattern 3: Template Switch mit Restore
**Was:** Alarm-Switch, der seinen Zustand ueber Neustarts behaelt.
```yaml
switch:
  - platform: template
    name: "Wecker Alarm"
    id: alarm_enabled
    optimistic: true
    restore_mode: RESTORE_DEFAULT_ON
```

### Pattern 4: Script-basierte Alarm-Logik
**Was:** ESPHome Scripts fuer Alarm und Snooze.
```yaml
script:
  - id: alarm_ring
    mode: restart
    then:
      - globals.set:
          id: alarm_ringing
          value: 'true'
      - while:
          condition:
            lambda: 'return id(alarm_ringing);'
          then:
            - rtttl.play:
                rtttl: alarm_buzzer
                value: "Alarm:d=4,o=5,b=160:c,e,g,c6,e6,g6"
            - wait_until:
                not:
                  rtttl.is_playing: alarm_buzzer
            - delay: 2s

  - id: snooze_script
    mode: restart
    then:
      - script.stop: alarm_ring
      - rtttl.stop: alarm_buzzer
      - globals.set:
          id: alarm_ringing
          value: 'false'
      - delay: 5min
      - script.execute: alarm_ring
```

### Pattern 5: Dynamische Alarm-Zeit per Lambda
**Was:** Jede Minute pruefen ob Alarm-Zeit erreicht (statt feste Cron-Expression).
```yaml
time:
  - platform: sntp
    id: sntp_time
    timezone: "Europe/Berlin"
    on_time:
      - seconds: 0
        then:
          - if:
              condition:
                and:
                  - switch.is_on: alarm_enabled
                  - lambda: |-
                      auto now = id(sntp_time).now();
                      if (!now.is_valid()) return false;
                      return now.day_of_week >= 2 && now.day_of_week <= 6
                        && now.hour == (int)id(alarm_hour).state
                        && now.minute == (int)id(alarm_minute).state;
              then:
                - script.execute: alarm_ring
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Custom Lambda fuer Display-Rendering
**Was:** `display: lambda: |-` mit manuellem `it.line()`, `it.circle()`.
**Warum schlecht:** Kein Touch-Support, kein Widget-System, muehsame Trigonometrie.
**Stattdessen:** LVGL `meter` Widget fuer analoge Uhr, LVGL `label` fuer digitale Uhr.

### Anti-Pattern 2: Arduino Framework mit T-RGB
**Was:** Arduino-Framework statt ESP-IDF.
**Warum schlecht:** `mipi_rgb`-Treiber erfordert ESP-IDF. Arduino hat keinen nativen Support fuer 16-Bit-Parallel-RGB.
**Stattdessen:** Immer `framework: type: esp-idf`.

### Anti-Pattern 3: I2S-Speaker auf T-RGB
**Was:** Versuch, einen I2S-Lautsprecher anzuschliessen.
**Warum schlecht:** T-RGB hat KEINE 3 freien GPIOs fuer I2S. Zusaetzlich: RTTTL+Speaker Bug (spielt nur einmal, Issue #10312).
**Stattdessen:** Passiver Piezo-Buzzer mit LEDC PWM Output an einem einzelnen GPIO.

### Anti-Pattern 4: Feste Alarm-Zeit im Code
**Was:** `on_time: cron: '0 30 6 * * MON-FRI'`
**Warum schlecht:** Jede Aenderung erfordert Firmware-Update.
**Stattdessen:** Number-Entities fuer Stunde/Minute, dynamische Lambda-Pruefung.

### Anti-Pattern 5: Interner DAC auf ESP32-S3
**Was:** `dac_type: internal` in Speaker-Konfiguration.
**Warum schlecht:** ESP32-S3 hat keinen internen DAC. Irrelevant da kein I2S genutzt wird.
**Stattdessen:** LEDC PWM + passiver Buzzer.

### Anti-Pattern 6: Polling-Loop fuer Alarm-Check
**Was:** `interval: 1s` mit Lambda.
**Warum schlecht:** Unnoetige CPU-Last.
**Stattdessen:** `on_time` Trigger mit `seconds: 0` (einmal pro Minute).

## Build Order (Abhaengigkeiten)

```
Phase 0: Hardware-Validierung
  |- Schaltplan analysieren: freien GPIO fuer Buzzer identifizieren
  |- Piezo-Buzzer Machbarkeit pruefen
  \- Keine Software-Abhaengigkeiten

Phase 1: Board + Grundkonfiguration
  |- WiFi, OTA, Logger, API
  |- I2C Bus (GPIO8 SDA, GPIO48 SCL)
  |- XL9535 Expander (Adresse 0x20)
  |- SNTP Time Component
  |- Backlight (GPIO46, LEDC)
  \- Abhaengig von: Phase 0 (GPIO geklaert)

Phase 2: Display + Digitale Uhr
  |- MIPI RGB Display-Treiber (model: T-RGB-2.1)
  |- LVGL Grundkonfiguration (buffer_size, pages)
  |- Digitale Uhr (Label-Widget, NTP-Sync)
  \- Abhaengig von: Phase 1 (I2C, XL9535, Time)

Phase 3: Touch + Audio
  |- CST816/GT911 Touchscreen (je nach Board-Version)
  |- LVGL Touch-Routing
  |- LEDC Output fuer Buzzer
  |- RTTTL Component (output-Modus, NICHT speaker)
  |- Test: Melodie 3x hintereinander abspielen
  \- Abhaengig von: Phase 1 (I2C, GPIO)

Phase 4: Alarm-Logik
  |- Template Switch (alarm_enabled, restore_mode)
  |- Number Entities (alarm_hour, alarm_minute)
  |- on_time Lambda (Mo-Fr Check, is_valid() Check)
  |- Script: alarm_ring (While-Loop mit RTTTL)
  |- Script: snooze (5min Delay + Re-Ring)
  |- Physische Taste -> Snooze
  |- Touch "Alarm Aus" Button
  \- Abhaengig von: Phase 2 (Display), Phase 3 (Touch, Audio)

Phase 5: Analoge Uhr + UI Polish
  |- LVGL Meter-Widget (3 Skalen, Zeiger)
  |- Page-Navigation (analog <-> digital)
  |- Alarm-Status Overlay (Top-Layer)
  |- Nachtmodus (Dimming)
  \- Abhaengig von: Phase 2 (LVGL), Phase 4 (Alarm)

Phase 6: HA-Integration
  |- Switch Entity in HA
  |- Feiertag-Sensor empfangen (binary_sensor.workday_sensor)
  |- HA-Automatisierung erstellen (Feiertag -> Switch OFF)
  \- Abhaengig von: Phase 4 (Alarm-Logik)
```

**Hinweis:** Phase 3 (Touch + Audio) kann teilweise parallel zu Phase 2 (Display) entwickelt werden.

## Hardware-spezifische Architektur-Hinweise (LilyGo T-RGB)

### XL9535 I/O Expander
- Adresse: 0x20
- Pin 6: LCD Reset (invertiert)
- Pin 2: LCD Enable (invertiert)
- Pin 1: Touch Reset
- Pin 5: SPI CLK fuer Display-Init
- Pin 4: SPI MOSI fuer Display-Init
- Gueltige Pins: 0-7 und 10-17 (8-9 existieren nicht)

### PSRAM Pflicht
```yaml
psram:
  mode: octal
  speed: 80MHz
```

### Flash-Modus
```yaml
esphome:
  platformio_options:
    board_build.flash_mode: dio  # PFLICHT fuer T-RGB, QIO funktioniert nicht
```

### Board-Versionen und Touch-Controller
| Version | Touch-Controller | ESPHome-Treiber |
|---------|-----------------|-----------------|
| 2.1" Half Circle | FT3267 | `ft5x06` |
| 2.1" Full Circle | CST820 | `cst816` |
| 2.8" Full Circle | GT911 | `gt911` |

## Sources

- ESPHome LVGL: https://esphome.io/components/lvgl/ - HIGH
- ESPHome MIPI RGB: https://esphome.io/components/display/mipi_rgb/ - HIGH
- ESPHome RTTTL: https://esphome.io/components/rtttl/ - HIGH
- ESPHome LEDC Output: https://esphome.io/components/output/ledc/ - HIGH
- ESPHome Time: https://esphome.io/components/time/ - HIGH
- ESPHome CST816: https://esphome.io/components/touchscreen/cst816/ - HIGH
- ESPHome Packages: https://esphome.io/components/packages/ - HIGH
- LilyGo T-RGB GitHub: https://github.com/Xinyuan-LilyGO/LilyGo-T-RGB - HIGH
- LilyGo T-RGB Community: https://community.home-assistant.io/t/lilygo-t-rgb-esp32-s3-2-1/948076 - MEDIUM
- RTTTL Speaker Bug: https://github.com/esphome/esphome/issues/10312 - HIGH
