---
phase: 01-board-und-digitale-uhr
plan: 01
subsystem: infra
tags: [esphome, esp32s3, lilygo-t-rgb, lvgl, mipi_rgb, ft5x06, xl9535, sntp, esp-idf, psram]

# Dependency graph
requires: []
provides:
  - ESPHome-Konfiguration fuer LilyGo T-RGB 2.1" Half Circle (compilierbar, hardware-verifiziert)
  - secrets.yaml mit WiFi- und API-Credentials-Platzhaltern
  - LVGL digitale Uhr: HH:MM (montserrat_48) + Datum/Wochentag (montserrat_14)
  - NTP-Zeitsynchronisation mit Zeitzone Europe/Berlin
  - Display-Backlight als steuerbare Home-Assistant-Entity
affects: [02-alarm-logic, 03-ha-integration, 04-physical-controls]

# Tech tracking
tech-stack:
  added:
    - ESPHome (YAML-basiertes Firmware-Framework)
    - ESP-IDF Framework (NICHT Arduino -- Pflicht fuer mipi_rgb)
    - LVGL (Embedded-GUI-Library, buffer_size 25%)
    - mipi_rgb Display-Treiber mit Board-Modell T-RGB-2.1
    - ft5x06 Touchscreen-Treiber (FT3267 IC auf T-RGB 2.1 Half Circle)
    - XL9535 I/O-Expander (Display-Reset/Enable, SPI CLK/MOSI fuer LCD-Init)
    - LEDC PWM Output fuer Backlight (GPIO46)
    - SNTP Zeitkomponente
  patterns:
    - XL9535-Block MUSS vor Display-Block in YAML stehen (Initialisierungsreihenfolge)
    - auto_clear_enabled: false + update_interval: never bei LVGL-Displays Pflicht
    - PSRAM octal 80MHz fuer Display-Framebuffer benoetigt
    - flash_mode: dio (nicht qio) fuer dieses Board
    - SPI CLK/MOSI fuer ST7701S LCD-Init laufen ueber XL9535 IO5/IO4 (nicht direkte GPIOs)
    - ft5x06 reset_pin wird NICHT konfiguriert (Treiber unterstuetzt es nicht)

key-files:
  created:
    - alarm-clock.yaml
    - secrets.yaml
  modified: []

key-decisions:
  - "Touchscreen-Platform ft5x06 (nicht cst816): T-RGB 2.1 Half Circle hat FT3267 IC, nicht CST816"
  - "SPI-Bus fuer LCD-Initialisierung: CLK/MOSI auf XL9535 IO5/IO4 (nicht GPIO48/GPIO47 direkt)"
  - "LVGL buffer_size 25%: stabiler als 100% fuer initiale Board-Validierung"
  - "ft5x06 reset_pin weglassen: Treiber wirft Fehler bei konfiguriertem reset_pin"
  - "allow_other_uses nicht noetig: SPI und I2C teilen sich GPIO48 nicht mehr"

patterns-established:
  - "Secrets-Pattern: alle Credentials via !secret Direktiven, secrets.yaml nie committen"
  - "Einzel-Datei-Pattern fuer Phase 1: alles in alarm-clock.yaml (Package-Aufteilung ab Phase 2)"

requirements-completed: ["TIME-01", "DISP-01", "DISP-03"]

# Metrics
duration: ~60min (zwei Sessions + Hardware-Debug)
completed: 2026-03-24
---

# Phase 1 Plan 01: Board-Setup und Digitale Uhr Summary

**ESPHome-Konfiguration fuer LilyGo T-RGB 2.1" Half Circle: LVGL-Uhrzeitanzeige (HH:MM, montserrat_48) und Datum/Wochentag via NTP-Sync Europe/Berlin -- hardware-verifiziert, Display zeigt korrekte Uhrzeit**

## Performance

- **Duration:** ~60 min (zwei Sessions + Hardware-Debug)
- **Started:** 2026-03-17
- **Completed:** 2026-03-24 (alle 3 Tasks abgeschlossen, Hardware-Verifikation erfolgreich)
- **Tasks:** 3/3 abgeschlossen
- **Files modified:** 2

## Accomplishments

- secrets.yaml mit allen 5 erforderlichen Keys (wifi_ssid, wifi_password, api_key, ota_password, fallback_password) und generiertem API-Key
- alarm-clock.yaml mit vollstaendiger Board-Konfiguration: ESP-IDF Framework, PSRAM octal 80MHz, DIO Flash-Mode, XL9535 I/O-Expander, mipi_rgb Display (T-RGB-2.1), ft5x06 Touchscreen, LEDC Backlight GPIO46, SNTP Europe/Berlin
- LVGL-UI mit time_label (HH:MM, montserrat_48, CENTER) und date_label (Wochentag + Datum, montserrat_14, y+40)
- Hardware-Verifikation erfolgreich: Board zeigt helles Display mit weisser Uhrzeit (HH:MM) zentriert, darunter dunkelgrauer Wochentag und Datum

## Task Commits

Jede Task wurde atomar committed:

1. **Task 1: secrets.yaml mit Platzhaltern** - `f0daf74` (feat)
2. **Task 2: alarm-clock.yaml Board-Setup + LVGL-Uhr** - `886ebc5` + `4b961aa` (feat)
3. **Task 3: Board-Flash und visuelle Pruefung** - `65f62aa` (fix) -- Hardware-Debug-Fixes nach Flash

## Files Created/Modified

- `alarm-clock.yaml` - Komplette ESPHome-Konfiguration: Board (ESP-IDF, PSRAM, DIO), Display (mipi_rgb T-RGB-2.1 via XL9535), Touchscreen (ft5x06), Backlight (LEDC GPIO46), NTP (Europe/Berlin), LVGL-UI mit digitaler Uhr
- `secrets.yaml` - WiFi- und API-Credentials (Platzhalter, nicht committet)

## Decisions Made

- **ft5x06 statt cst816:** T-RGB 2.1 Half Circle verwendet FT3267 Touch-IC, das vom ft5x06-Treiber unterstuetzt wird. Der Plan nannte noch cst816 (war inkorrekt).
- **SPI-Pins auf XL9535:** Der ST7701S-LCD-Initialisierungs-SPI lauft ueber XL9535 IO5 (CLK) und IO4 (MOSI), nicht ueber direkte GPIOs. Dies ist die korrekte Hardware-Verdrahtung des T-RGB Half Circle Boards.
- **ft5x06 ohne reset_pin:** Der ft5x06-Treiber in ESPHome wirft Fehler wenn reset_pin konfiguriert ist -- weglassen ist korrekt.
- **LVGL buffer_size 25%:** Stabile Wahl fuer initiale Board-Validierung, vermeidet Speicherprobleme beim ersten Flash.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Touchscreen-Platform korrigiert: ft5x06 statt cst816**
- **Found during:** Task 2 Fertigstellung
- **Issue:** Plan spezifizierte `platform: cst816`, aber das T-RGB 2.1 Half Circle Board hat einen FT3267 Touch-IC, der vom ft5x06-Treiber unterstuetzt wird
- **Fix:** Touchscreen-Platform auf `ft5x06` geaendert
- **Files modified:** alarm-clock.yaml
- **Committed in:** 4b961aa

**2. [Rule 2 - Missing] LVGL touchscreens-Referenz ergaenzt**
- **Found during:** Task 2 Vervollstaendigung
- **Issue:** LVGL-Block hatte keinen `touchscreens:` Eintrag -- Toucheingaben waeren nicht an LVGL weitergeleitet worden
- **Fix:** `touchscreens: - my_touchscreen` in LVGL-Block eingefuegt
- **Files modified:** alarm-clock.yaml
- **Committed in:** 4b961aa

**3. [Rule 1 - Bug] LVGL time_format Labels statt statischem "TEST"-String**
- **Found during:** Task 2 Vervollstaendigung
- **Issue:** LVGL-Label hatte `text: "TEST"` statt der time_format-Direktive; Datum-Label fehlte vollstaendig
- **Fix:** time_label auf `time_format: "%H:%M"` umgestellt, date_label (`%A, %d.%m.%Y`) ergaenzt
- **Files modified:** alarm-clock.yaml
- **Committed in:** 4b961aa

**4. [Rule 1 - Bug] ft5x06 reset_pin entfernt (Hardware-Debug nach Flash)**
- **Found during:** Task 3 Hardware-Verifikation
- **Issue:** ft5x06-Treiber in ESPHome wirft Fehler bei konfiguriertem reset_pin -- Treiber unterstuetzt diese Option nicht
- **Fix:** reset_pin-Block aus touchscreen-Konfiguration entfernt
- **Files modified:** alarm-clock.yaml
- **Committed in:** 65f62aa

**5. [Rule 1 - Bug] SPI-Bus auf XL9535-Pins korrigiert (Hardware-Debug nach Flash)**
- **Found during:** Task 3 Hardware-Verifikation
- **Issue:** Urspruengliche SPI-Konfiguration nutzte GPIO47/GPIO48 direkt -- falsche Pins fuer dieses Board. Der ST7701S-LCD-Init-SPI laeuft beim T-RGB Half Circle ueber XL9535 IO-Expander
- **Fix:** SPI CLK auf XL9535 IO5, MOSI auf XL9535 IO4; allow_other_uses komplett entfernt
- **Files modified:** alarm-clock.yaml
- **Committed in:** 65f62aa

---

**Total deviations:** 5 auto-fixed (3 vor Flash, 2 beim Hardware-Debug)
**Impact on plan:** Alle Auto-Fixes waren notwendig fuer korrekten Betrieb. Kein Scope-Creep.

## Hardware-Verifikation (Task 3 Ergebnis)

- Board erfolgreich geflasht via USB
- Display zeigt: heller grauer Hintergrund, weisse Uhrzeit (HH:MM) zentriert, dunkelgrauer Wochentag und Datum darunter
- NTP-Sync: Zeitzone Europe/Berlin korrekt
- Display-Backlight leuchtet

## Next Phase Readiness

- alarm-clock.yaml ist compilierbar, hardware-verifiziert und vollstaendig konfiguriert
- Phase 1 Plan 1 ist vollstaendig abgeschlossen
- Phase 2 (Alarm-Logik) kann beginnen
- Offener Punkt: GPIO fuer Piezo-Buzzer und physische Taste muss aus T-RGB-Schaltplan identifiziert werden (Confidence: LOW, relevant ab Phase 2/4)

---
*Phase: 01-board-und-digitale-uhr*
*Completed: 2026-03-24*
