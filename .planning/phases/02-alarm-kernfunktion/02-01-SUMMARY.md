---
phase: 02-alarm-kernfunktion
plan: 01
subsystem: audio
tags: [esphome, ledc, pwm, rtttl, piezo, gpio]

# Dependency graph
requires:
  - phase: 01-board-und-digitale-uhr
    provides: alarm-clock.yaml Grundkonfiguration mit LEDC buzzer_output auf GPIO38
provides:
  - LEDC buzzer_output auf GPIO4 (Piezo-Buzzer) statt GPIO38
  - GPIO0 binary_sensor (Boot-Strapping-Pin) vollstaendig entfernt
  - alarm-clock.yaml kompiliert fehlerfrei mit Piezo-Konfiguration
affects:
  - 02-alarm-kernfunktion
  - 03-ha-integration

# Tech tracking
tech-stack:
  added: []
  patterns:
    - LEDC PWM fuer Piezo-Buzzer (GPIO4) mit RTTTL output-Referenz

key-files:
  created: []
  modified:
    - alarm-clock.yaml

key-decisions:
  - "Scope Change: I2S MAX98357A verworfen -- LEDC Piezo-Buzzer auf GPIO4 statt GPIO38 (kein freier I2S-faehiger GPIO am T-RGB Board verfuegbar)"
  - "GPIO0 (Boot-Strapping-Pin) als binary_sensor entfernt -- Snooze nur noch per Touch-Button auf alarm_ringing_page"
  - "RTTTL bleibt auf output: buzzer_output (kein speaker:) -- kein Umbau der Audio-Architektur noetig"

patterns-established:
  - "Scope Changes durch Checkpoint-Entscheidung: Urspruenglich I2S geplant, nach Board-Analyse auf LEDC umgestellt"

requirements-completed: [ALRM-03, ALRM-05]

# Metrics
duration: ~15min
completed: 2026-03-25
---

# Phase 02 Plan 01: Audio-Pin-Migration Summary

**LEDC buzzer_output Pin von GPIO38 auf GPIO4 migriert (Piezo-Buzzer), GPIO0 Boot-Strapping-Pin als Input entfernt -- Kompilierung erfolgreich**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-25T18:55:00Z
- **Completed:** 2026-03-25T19:09:00Z
- **Tasks:** 2 (Task 1 war Checkpoint, durch Scope Change aufgeloest)
- **Files modified:** 1

## Accomplishments

- buzzer_output LEDC Output von GPIO38 auf GPIO4 umgestellt (Piezo-Buzzer an GPIO4)
- RTTTL-Konfiguration unveraendert (bleibt auf `output: buzzer_output`)
- GPIO0 binary_sensor (snooze_button) vollstaendig entfernt -- Boot-Strapping-Pin wird nicht mehr als Input genutzt
- Snooze-Funktion weiterhin per Touch-Button (snooze_btn) auf alarm_ringing_page verfuegbar
- alarm-clock.yaml kompiliert fehlerfrei mit Exit 0

## Task Commits

Jeder Task wurde atomar committed:

1. **Task 2: LEDC buzzer_output GPIO38 -> GPIO4** - `9557d81` (feat)
2. **Task 3: GPIO0 binary_sensor entfernt** - `70464a9` (feat)

**Plan metadata:** (folgt mit diesem Commit)

## Files Created/Modified

- `C:/Users/Daniel/dev/esp32-alarm-clock/alarm-clock.yaml` - LEDC Pin GPIO38->GPIO4, binary_sensor entfernt (19 Zeilen geloescht, 1 Zeile geaendert)

## Decisions Made

- Scope Change: I2S MAX98357A wurde verworfen. Kein freier I2S-faehiger GPIO am T-RGB Board (GPIO19/GPIO20 sind die einzigen Kandidaten, aber zu wenig fuer stabile I2S-Kommunikation). Stattdessen: Piezo-Buzzer bleibt per LEDC PWM, Pin von GPIO38 auf GPIO4 geaendert (GPIO38 ist laut Schaltplan SD_DAT-Pin, GPIO4 ist Batterie-Spannungs-Pin der NICHT im Firmware-Code als ADC genutzt wird).
- GPIO0 als binary_sensor ist eine schlechte Praxis (Boot-Strapping-Pin, kann zu Boot-Fehlern fuehren). Snooze-Funktion per Touch-Button auf der UI reicht aus.

## Deviations from Plan

### Scope Change (kein Auto-Fix -- durch Benutzer-Entscheidung)

**Checkpoint-Entscheidung: I2S -> LEDC Piezo auf GPIO4**
- **Geplant:** I2S + MAX98357A Lautsprecher, LEDC buzzer_output entfernen, neuer i2s_audio Block
- **Entschieden:** Kein I2S, LEDC bleibt -- nur Pin-Wechsel von GPIO38 auf GPIO4
- **Grund:** T-RGB Board hat keine freien GPIOs fuer I2S ohne Konflikte mit Display, Touch, SD-Karte
- **Auswirkung:** Piezo-Buzzer statt Lautsprecher -- funktioniert fuer Weckfunktion

---

**Total deviations:** 1 Scope Change (durch Benutzer-Checkpoint-Entscheidung)
**Impact on plan:** Scope Change reduziert Komplexitaet erheblich. RTTTL-Architektur unveraendert, kein Umbau noetig.

## Issues Encountered

- Erster Kompilierungsversuch nach Task 3 schlug fehl (ESP-IDF Build-Cache Fehler: `esp_sha1.c.o: No such file or directory`) -- fluechtiger Fehler, zweiter Versuch erfolgreich.

## User Setup Required

None - keine externe Service-Konfiguration erforderlich.

## Next Phase Readiness

- alarm-clock.yaml konfiguriert und kompilierend: Piezo-Buzzer auf GPIO4, kein GPIO0-Sensor
- Naechste Schritte in Phase 2: Weitere Alarm-Kernfunktion-Plans (falls vorhanden) oder Phase 3: HA-Integration
- Hardware-Verifikation steht aus: Piezo-Buzzer an GPIO4 anschliessen und RTTTL-Melodie testen

---
*Phase: 02-alarm-kernfunktion*
*Completed: 2026-03-25*
