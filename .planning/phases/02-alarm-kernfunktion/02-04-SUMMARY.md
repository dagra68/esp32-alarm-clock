---
phase: 02-alarm-kernfunktion
plan: 04
subsystem: alarm-yaml
tags: [gap-fix, lvgl, i2s, ha-mirror, weekday-only, touch]
dependency_graph:
  requires: [02-01, 02-02, 02-03]
  provides: [alarm_ringing_page-touch-fix, i2s-migration, ha-alarm-mirror, weekday-display]
  affects: [alarm-clock.yaml, Phase-3-HA-Integration]
tech_stack:
  added: [i2s_audio, speaker-i2s, rtttl-speaker]
  patterns: [lvgl-bg-widget-touch-fix, component-update-ha-mirror, weekday-label-suffix]
key_files:
  modified: [alarm-clock.yaml]
decisions:
  - "alarm_ringing_page bg-Widget: clickable:false obj als erster Widget-Eintrag (Touch-Event-Routing)"
  - "I2S-Pins: GPIO38 (BCLK), GPIO39 (LRCLK), GPIO40 (DOUT) -- GPIO5/6/7 durch mipi_rgb Display blockiert"
  - "settings_back_btn ebenfalls auf weekday_only-Format aktualisiert (Konsistenz, nicht im Plan aber notwendig)"
metrics:
  duration: 33min
  completed_date: "2026-03-25"
  tasks_completed: 3
  tasks_total: 4
  files_modified: 1
---

# Phase 02 Plan 04: Gap-Fix -- Touch, I2S, HA-Mirror, weekday_only Display Summary

**One-liner:** Alle 4 Phase-2-Gaps geschlossen: alarm_ringing_page Touch-Fix via bg-Widget, I2S-Migration mit GPIO38-40, HA-Spiegel via component.update, weekday_only "Mo-Fr" Display-Suffix.

## Objective

Gap-Fix-Plan fuer alle 4 offenen Gaps aus der Phase-2-Verifikation (02-VERIFICATION.md). Ziel: Phase 2 in vollstaendig funktionierenden Zustand bringen, damit Phase 3 (HA-Integration) auf stabilem Fundament aufbaut.

## Tasks Completed

| Task | Name | Commit | Status |
|------|------|--------|--------|
| 1 | alarm_ringing_page Touch-Fix (bg-Widget) | f3afc6b | DONE |
| 2 | I2S-Migration abschliessen | f8c723c | DONE |
| 3 | HA-Spiegel + weekday_only Display-Feedback | 32c9b08 | DONE |
| 4 | OTA-Flash und Board-Verifikation | -- | AWAITING CHECKPOINT |

## What Was Built

### Task 1: alarm_ringing_page Touch-Fix

**Problem:** Snooze/Stopp-Buttons auf alarm_ringing_page reagierten nicht am Board. LVGL routet Touch-Events nur an Seiten mit registrierbarer Flaeche.

**Fix:** `obj` Widget `alarm_ringing_bg` (480x480, align: CENTER, bg_color: 0x1A1A2E, clickable: false) als erstes Widget in alarm_ringing_page eingefuegt. LVGL registriert die gesamte Seitenflaeche als valide Touch-Flaeche und routet Events korrekt zu snooze_btn und stopp_btn.

snooze_btn und stopp_btn-Handler unveraendert (script.execute: snooze_action / alarm_stop_action).

### Task 2: I2S-Migration

**Problem:** I2S-Migration aus 02-01-PLAN war nie umgesetzt worden -- buzzer_output (LEDC, GPIO4) noch aktiv, kein i2s_audio-Block.

**Fix (3 Aenderungen):**
1. buzzer_output LEDC-Block (Zeilen 84-87) entfernt
2. i2s_audio-Block + speaker alarm_speaker eingefuegt
3. rtttl von `output: buzzer_output` auf `speaker: alarm_speaker`, gain von `70%` auf `0.8`

**Deviation:** GPIO5/6/7 (laut Plan-Empfehlung) sind vom mipi_rgb Display-Treiber intern belegt -- Compile scheiterte mit "Pin X is used in multiple places". Alternative Pins GPIO38 (BCLK), GPIO39 (LRCLK), GPIO40 (DOUT) verwendet. Compile erfolgreich.

### Task 3: HA-Spiegel + weekday_only Display-Feedback

**Aenderungen:**
- 4x `component.update: alarm_time` nach hour_plus/minus/minute_plus/minus Buttons ergaenzt
- weekday_only_switch turn_on_action: lvgl.label.update analog_alarm_label mit "Mo-Fr" Suffix
- weekday_only_switch turn_off_action: lvgl.label.update analog_alarm_label ohne Suffix
- analog_alarm_label initial text: weekday_only-Pruefung (Mo-Fr oder nur HH:MM)
- alarm_time set_action: analog_alarm_label auf neues weekday_only-Format
- settings_back_btn: ebenfalls auf weekday_only-Format aktualisiert (Konsistenz)
- Alle snprintf-Aufrufe mit Mo-Fr-Suffix verwenden buf[24]

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] I2S-Pins GPIO5/6/7 durch mipi_rgb Display blockiert**
- **Found during:** Task 2 (I2S-Migration)
- **Issue:** Plan empfahl GPIO5/6/7 als Standard-I2S-Pins. Compile-Fehler: "Pin 5/6/7 is used in multiple places" -- mipi_rgb Display-Treiber des T-RGB 2.1 belegt diese intern.
- **Fix:** GPIO38 (BCLK), GPIO39 (LRCLK), GPIO40 (DOUT) verwendet -- keine Konflikte, Compile erfolgreich.
- **Files modified:** alarm-clock.yaml
- **Commit:** f8c723c

**2. [Rule 2 - Missing functionality] settings_back_btn nicht im Plan enthalten**
- **Found during:** Task 3
- **Issue:** settings_back_btn aktualisiert analog_alarm_label -- noch auf altem buf[16]-Format ohne weekday_only. Waere nach Rueckkehr inkonsistent.
- **Fix:** settings_back_btn ebenfalls auf weekday_only-Format + buf[24] umgestellt.
- **Files modified:** alarm-clock.yaml
- **Commit:** 32c9b08

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| buzzer_output count | 0 | 0 | PASS |
| i2s_audio: (Zeile) | 1 Treffer | Zeile 85 | PASS |
| speaker: alarm_speaker in rtttl | 1 Treffer | Zeile 272 | PASS |
| id: alarm_ringing_bg | 1 Treffer | Zeile 563 | PASS |
| component.update: alarm_time count | 4 | 4 | PASS |
| Mo-Fr count | >= 3 | 5 | PASS |
| esphome compile | SUCCESS | SUCCESS (48s) | PASS |

## Open Items

- **Task 4 (OTA-Flash):** Awaiting human verification checkpoint -- OTA-Flash + Board-Verifikation aller 4 Gap-Fixes am echten Board
- **I2S Audio Hardware:** MAX98357A Modul noch nicht physisch am Board angeschlossen -- kein Ton erwartet bis Verdrahtung durch Nutzer

## Self-Check

**SUMMARY.md created:** .planning/phases/02-alarm-kernfunktion/02-04-SUMMARY.md
**Commits verified:**
- f3afc6b: feat(02-04): alarm_ringing_page bg-Widget fuer Touch-Event-Fix
- f8c723c: feat(02-04): I2S-Migration abschliessen -- LEDC entfernt, i2s_audio + speaker eingefuegt
- 32c9b08: feat(02-04): HA-Spiegel + weekday_only Display-Feedback
</content>
</invoke>