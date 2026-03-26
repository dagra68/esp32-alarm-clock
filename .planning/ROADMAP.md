# Roadmap: ESP32 Smart Alarm Clock

## Overview

Vom blanken LilyGo T-RGB Board zum vollstaendigen ESPHome-Wecker in 4 Phasen: Zuerst laeuft das Display mit Uhrzeit (Board-Validierung inklusive), dann kommt die Alarm-Kernfunktion mit Buzzer und Snooze, danach die Home-Assistant-Integration fuer Fernsteuerung und Feiertags-Automatisierung, und zuletzt die analoge Uhren-Darstellung mit Seitenwechsel.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Board und Digitale Uhr** - ESPHome-Grundkonfiguration, Display-Treiber, NTP-Sync, digitale Zeitanzeige (completed 2026-03-24)
- [x] **Phase 2: Alarm-Kernfunktion** - Alarm-Logik, RTTTL-Buzzer, Snooze, Touch-Bedienung am Display (completed 2026-03-26)
- [x] **Phase 3: Home Assistant Integration** - HA-Entities, Automatisierung, Helligkeit, Melodie-Auswahl (completed 2026-03-26)
- [x] **Phase 4: Analoge Uhr und Seitenwechsel** - LVGL Meter-Widget, HA-gesteuerter Seitenwechsel (completed 2026-03-25)

## Phase Details

### Phase 1: Board und Digitale Uhr
**Goal**: Nutzer sieht die aktuelle Uhrzeit und das Datum auf dem runden Display -- Board laeuft stabil mit ESPHome
**Depends on**: Nothing (first phase)
**Requirements**: TIME-01, DISP-01, DISP-03
**Success Criteria** (what must be TRUE):
  1. ESP32-S3 bootet mit ESPHome (ESP-IDF Framework, PSRAM aktiv) und verbindet sich mit WLAN
  2. Nutzer sieht die aktuelle Uhrzeit (NTP-synchronisiert, Zeitzone Europe/Berlin) auf dem runden Display
  3. Nutzer sieht Datum und Wochentag auf dem Display
  4. Display-Backlight ist eingeschaltet und das Display zeigt LVGL-Inhalte korrekt an
**Plans**: 1 plan

Plans:
- [x] 01-01-PLAN.md -- Board-Setup, Display, NTP, LVGL digitale Uhr mit Datum

### Phase 2: Alarm-Kernfunktion
**Goal**: Nutzer wird Mo-Fr zur eingestellten Zeit durch RTTTL-Melodie geweckt und kann per Touch reagieren
**Depends on**: Phase 1
**Requirements**: ALRM-01, ALRM-02, ALRM-03, ALRM-04, ALRM-05, ALRM-06, DISP-04, DISP-05
**Success Criteria** (what must be TRUE):
  1. Nutzer kann eine Alarmzeit (Stunde + Minute) direkt am Touch-Display einstellen
  2. Alarm loest Mo-Fr (oder jeden Tag per HA-Switch) zur konfigurierten Zeit eine RTTTL-Melodie ueber I2S-Lautsprecher aus
  3. Nutzer kann per Touch-Button 5 Minuten Snooze ausloesen (Alarm pausiert und klingelt erneut)
  4. Nutzer kann den aktiven Alarm per Touch dauerhaft ausschalten
  5. Display zeigt Alarm-Status (ein/aus) und naechste Alarmzeit an
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md -- I2S-Audio-Migration (LEDC->I2S) und GPIO0-Sensor entfernen
- [x] 02-02-PLAN.md -- weekday_only Switch ergaenzen und on_time Lambda refactoren
- [x] 02-03-PLAN.md -- OTA-Flash und Board-Verifikation (3 Gaps: Snooze/Stopp-Buttons, weekday_only-Display)

### Phase 3: Home Assistant Integration
**Goal**: Nutzer kann den Wecker vollstaendig ueber Home Assistant fernsteuern und automatisieren
**Depends on**: Phase 2
**Requirements**: HA-01, HA-02, HA-03, HA-04, HA-05, CTRL-01
**Success Criteria** (what must be TRUE):
  1. Alarm Ein/Aus ist als Switch-Entity in Home Assistant sichtbar und steuerbar
  2. Alarmzeit kann ueber datetime Time-Entity in HA eingestellt werden
  3. Home Assistant kann den Alarm per Automatisierung deaktivieren (z.B. Feiertags-Kalender)
  4. Melodie-Auswahl ist als Select-Entity in HA verfuegbar (mind. 3 RTTTL-Melodien)
  5. Display-Helligkeit ist ueber HA-Slider (light entity) steuerbar
**Status**: Complete (2026-03-26) -- alle Entities bereits in alarm-clock.yaml umgesetzt

Implemented entities:
- switch: "Alarm aktiv" (alarm_enabled_switch)
- switch: "Nur Mo-Fr" (weekday_only_switch)
- datetime type:time "Alarmzeit" (alarm_time)
- select: "Alarm Melodie" (alarm_melody_select) -- Entertainer, Frere Jacques, Reveille
- select: "Hintergrundfarbe" (bg_color_select)
- light: "Display Backlight" (backlight)
- time: platform homeassistant (sntp_time) -- Zeit via HA-API

### Phase 4: Analoge Uhr und Seitenwechsel
**Goal**: Nutzer kann zwischen digitalem und analogem Zifferblatt per HA-Select wechseln
**Depends on**: Phase 1
**Requirements**: DISP-02, DISP-06
**Success Criteria** (what must be TRUE):
  1. Nutzer sieht eine analoge Uhr mit Stunden- und Minutenzeiger (LVGL Meter-Widget)
  2. Nutzer kann per HA-Select zwischen analogem und digitalem Zifferblatt wechseln
  3. Beide Zifferblaetter zeigen die korrekte Uhrzeit (NTP-synchronisiert)
**Plans**: 1 plan

Plans:
- [x] 04-01-PLAN.md -- Analog-Uhr-Seite mit Meter-Widget, Select-Entities fuer Seitenwechsel und Farbauswahl

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Board und Digitale Uhr | 1/1 | Complete   | 2026-03-24 |
| 2. Alarm-Kernfunktion | 4/4 | Complete | 2026-03-26 |
| 3. Home Assistant Integration | -- | Complete (in Phase 2/4 umgesetzt) | 2026-03-26 |
| 4. Analoge Uhr und Seitenwechsel | 1/1 | Complete    | 2026-03-25 |
