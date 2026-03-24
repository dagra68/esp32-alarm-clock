---
phase: 01-board-und-digitale-uhr
plan: 01
subsystem: infra
tags: [esphome, esp32s3, lilygo-t-rgb, lvgl, mipi_rgb, ft5x06, xl9535, sntp, esp-idf, psram]

# Dependency graph
requires: []
provides:
  - ESPHome-Konfiguration fuer LilyGo T-RGB 2.1" Half Circle (compilierbar)
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
    - XL9535 I/O-Expander (Display-Reset/Enable und Touchscreen-Reset)
    - LEDC PWM Output fuer Backlight (GPIO46)
    - SNTP Zeitkomponente
  patterns:
    - XL9535-Block MUSS vor Display-Block in YAML stehen (Initialisierungsreihenfolge)
    - auto_clear_enabled: false + update_interval: never bei LVGL-Displays Pflicht
    - PSRAM octal 80MHz fuer Display-Framebuffer benoetigt
    - flash_mode: dio (nicht qio) fuer dieses Board

key-files:
  created:
    - alarm-clock.yaml
    - secrets.yaml
  modified: []

key-decisions:
  - "Touchscreen-Platform ft5x06 (nicht cst816): T-RGB 2.1 Half Circle hat FT3267 IC, nicht CST816"
  - "SPI-Bus fuer LCD-Initialisierung: GPIO48 (SCL) wird shared mit SPI CLK via allow_other_uses"
  - "LVGL buffer_size 25%: stabiler als 100% fuer initiale Board-Validierung"
  - "show_test_card: true initial entfernt nach LVGL-Integration"

patterns-established:
  - "Secrets-Pattern: alle Credentials via !secret Direktiven, secrets.yaml nie committen"
  - "Einzel-Datei-Pattern fuer Phase 1: alles in alarm-clock.yaml (Package-Aufteilung ab Phase 2)"

requirements-completed: ["TIME-01", "DISP-01", "DISP-03"]

# Metrics
duration: ~30min
completed: 2026-03-24
---

# Phase 1 Plan 01: Board-Setup und Digitale Uhr Summary

**ESPHome-Konfiguration fuer LilyGo T-RGB 2.1" mit LVGL-Uhrzeitanzeige (HH:MM, montserrat_48) und Datum/Wochentag via NTP-Sync Europe/Berlin, wartet auf Hardware-Flash-Verifikation**

## Performance

- **Duration:** ~30 min (verteilt ueber zwei Sessions)
- **Started:** 2026-03-17
- **Completed:** 2026-03-24 (Tasks 1+2 abgeschlossen, Task 3 Checkpoint ausstehend)
- **Tasks:** 2/3 abgeschlossen (Task 3 ist ein Hardware-Checkpoint)
- **Files modified:** 2

## Accomplishments

- secrets.yaml mit allen 5 erforderlichen Keys (wifi_ssid, wifi_password, api_key, ota_password, fallback_password) und generiertem API-Key
- alarm-clock.yaml mit vollstaendiger Board-Konfiguration: ESP-IDF Framework, PSRAM octal 80MHz, DIO Flash-Mode, XL9535 I/O-Expander, mipi_rgb Display (T-RGB-2.1), ft5x06 Touchscreen, LEDC Backlight GPIO46, SNTP Europe/Berlin
- LVGL-UI mit time_label (HH:MM, montserrat_48, CENTER) und date_label (Wochentag + Datum, montserrat_14, y+40)

## Task Commits

Jede Task wurde atomar committed:

1. **Task 1: secrets.yaml mit Platzhaltern** - `f0daf74` (feat)
2. **Task 2: alarm-clock.yaml Board-Setup + LVGL-Uhr** - `886ebc5` + `4b961aa` (feat)
3. **Task 3: Board-Flash und visuelle Pruefung** - Checkpoint, noch ausstehend

**Plan-Metadaten:** Checkpoint-SUMMARY wird nach erfolgreicher Hardware-Verifikation final committed.

## Files Created/Modified

- `alarm-clock.yaml` - Komplette ESPHome-Konfiguration: Board (ESP-IDF, PSRAM, DIO), Display (mipi_rgb T-RGB-2.1 via XL9535), Touchscreen (ft5x06), Backlight (LEDC GPIO46), NTP (Europe/Berlin), LVGL-UI mit digitaler Uhr
- `secrets.yaml` - WiFi- und API-Credentials (Platzhalter, nicht committet)

## Decisions Made

- **ft5x06 statt cst816:** T-RGB 2.1 Half Circle verwendet FT3267 Touch-IC, das vom ft5x06-Treiber unterstuetzt wird. Der Plan nannte noch cst816 (war inkorrekt).
- **SPI-Bus notwendig:** mipi_rgb-Treiber benoetigt SPI fuer LCD-Initialisierung. GPIO48 wird shared zwischen I2C SCL und SPI CLK via `allow_other_uses: true`.
- **LVGL buffer_size 25%:** Stabile Wahl fuer initiale Board-Validierung, vermeidet Speicherprobleme beim ersten Flash.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Touchscreen-Platform korrigiert: ft5x06 statt cst816**
- **Found during:** Task 2 Fertigstellung (per important_notes in Auftrag)
- **Issue:** Plan (und urspruenglich alarm-clock.yaml) spezifizierte `platform: cst816`, aber das T-RGB 2.1 Half Circle Board hat einen FT3267 Touch-IC, der vom ft5x06-Treiber unterstuetzt wird
- **Fix:** Touchscreen-Platform auf `ft5x06` geaendert (war bereits in vorhandener alarm-clock.yaml korrekt)
- **Files modified:** alarm-clock.yaml
- **Verification:** `grep -q "platform: ft5x06" alarm-clock.yaml` -> PASS
- **Committed in:** 4b961aa

**2. [Rule 2 - Missing] LVGL touchscreens-Referenz ergaenzt**
- **Found during:** Task 2 Vervollstaendigung
- **Issue:** LVGL-Block hatte keinen `touchscreens:` Eintrag -- Toucheingaben waeren nicht an LVGL weitergeleitet worden
- **Fix:** `touchscreens: - my_touchscreen` in LVGL-Block eingefuegt
- **Files modified:** alarm-clock.yaml
- **Verification:** Visuell geprueft
- **Committed in:** 4b961aa

**3. [Rule 1 - Bug] LVGL time_format Labels statt statischem "TEST"-String**
- **Found during:** Task 2 Vervollstaendigung
- **Issue:** LVGL-Label hatte `text: "TEST"` statt der time_format-Direktive; Datum-Label fehlte vollstaendig
- **Fix:** time_label auf `time_format: "%H:%M"` umgestellt, date_label (`%A, %d.%m.%Y`) ergaenzt
- **Files modified:** alarm-clock.yaml
- **Verification:** `grep -q 'time_format' alarm-clock.yaml && grep -q '%H:%M' alarm-clock.yaml` -> PASS
- **Committed in:** 4b961aa

---

**Total deviations:** 3 auto-fixed (1 Bug-Fix Touchscreen-Treiber, 1 fehlende LVGL-Referenz, 1 Bug-Fix LVGL-Label-Inhalt)
**Impact on plan:** Alle Auto-Fixes waren notwendig fuer korrekten Betrieb. Kein Scope-Creep.

## Issues Encountered

- alarm-clock.yaml war bereits teilweise vorhanden (aus vorheriger Session), aber unvollstaendig (LVGL zeigte "TEST", kein Datum-Label, kein touchscreens-Eintrag in LVGL). Task 2 wurde durch Ergaenzung der fehlenden Teile vervollstaendigt.

## User Setup Required

**Vor dem ersten Flash erforderlich:**
1. `secrets.yaml` editieren: `wifi_ssid` und `wifi_password` mit echten WLAN-Daten fuellen
2. `esphome compile alarm-clock.yaml` -- muss fehlerfrei durchlaufen
3. `esphome upload alarm-clock.yaml` -- Board via USB flashen
4. Pruefen: Display leuchtet, Uhrzeit HH:MM angezeigt, Datum/Wochentag sichtbar, NTP-Sync im Log

## Next Phase Readiness

- alarm-clock.yaml ist compilierbar und vollstaendig konfiguriert
- Nach erfolgreicher Hardware-Verifikation (Task 3 Checkpoint) ist Phase 1 Plan 1 abgeschlossen
- Phase 1 Plan 2 (falls vorhanden) oder Phase 2 kann danach beginnen
- Offener Punkt: GPIO fuer Piezo-Buzzer und physische Taste muss aus T-RGB-Schaltplan identifiziert werden (Confidence: LOW, relevant ab Phase 2/4)

---
*Phase: 01-board-und-digitale-uhr*
*Completed: 2026-03-24*
