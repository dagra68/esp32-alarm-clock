# Phase 2: Alarm-Kernfunktion - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Die Alarm-Kernfunktion wird vollständig über Touch-Display und Home Assistant bedient. Audio-Ausgabe erfolgt über I2S (MAX98357A-Modul an den dedizierten I2S-Pins des T-RGB Boards). Snooze und Alarm-Stopp sind ausschließlich per Touch auf der Alarm-Aktiv-Seite möglich — keine physische Taste. Der Wochentag-Filter (Mo–Fr) ist per HA-Switch umschaltbar, nicht hardcodiert.

Viel Code ist bereits in `alarm-clock.yaml` vorhanden (aus früheren Implementierungen), muss aber angepasst werden: LEDC-Buzzer auf GPIO38 → I2S-Output, GPIO0-Binary-Sensor entfernen, Mo–Fr-Hardcodierung durch HA-Switch ersetzen.

</domain>

<decisions>
## Implementation Decisions

### Audio-Output
- **MAX98357A** I2S-Verstärker-Modul (externer Lautsprecher, Mono, 3W)
- Anschluss an die **dedizierten I2S-Pins** des LilyGo T-RGB Boards (bereits herausgeführt)
- ESPHome `i2s_audio`-Komponente mit `dac_type: external`
- RTTTL-Komponente nutzt den I2S-Output (ersetzt bestehenden `ledc`-Output auf GPIO38)
- Bestehender `output: platform: ledc, pin: GPIO38` wird **entfernt**

### Snooze und Alarm-Stopp
- **Ausschließlich per Touch** auf der `alarm_ringing_page`
- Zwei Buttons: "Snooze 5min" und "Stopp"
- **Keine physische Taste** — bestehender GPIO0 `binary_sensor` (snooze_button) wird **entfernt**

### Wochentag-Filter (Mo–Fr)
- Neuer HA-Switch: "Nur Mo–Fr" (`weekday_only`, bool, `restore_value: yes`)
- **EIN:** Alarm klingelt nur Montag–Freitag
- **AUS:** Alarm klingelt jeden Tag
- `on_time`-Lambda prüft: `bool day_ok = !id(weekday_only) || (now.day_of_week >= 2 && now.day_of_week <= 6);`
- Aktuell ist Mo–Fr **hardcodiert** in der `on_time`-Lambda — das wird durch den Switch ersetzt

### Alarm-Logik (bestehend, bleibt erhalten)
- `on_time` Trigger: jede Minute, prüft alarm_enabled + day_ok + Stunde/Minute
- `alarm_timeout_script`: Auto-Aus nach 5 min (Alarm klingelt nicht ewig)
- `snooze_action`: RTTTL stopp → 5 min warten → Alarm erneut auslösen → alarm_ringing_page zeigen
- `alarm_stop_action`: RTTTL stopp → alarm_ringing = false → alarm_enabled = false → zurück zur Uhr
- Globals: `alarm_hour`, `alarm_minute`, `alarm_enabled`, `alarm_ringing`, `alarm_melody_name` — alle mit `restore_value`

### Alarm-UI (bestehend, bleibt erhalten)
- `alarm_ringing_page`: wird automatisch bei Alarm-Trigger gezeigt, Snooze + Stopp Buttons
- `alarm_settings_page`: +/– Buttons für Stunde/Minute, Zugang via Long-Press auf Alarm-Button
- Alarm-Button auf `analog_clock_page`: Short-Click = Toggle Ein/Aus, Long-Press = Settings

### Was entfernt wird
- `output: platform: ledc, pin: GPIO38` → durch `i2s_audio`-Output ersetzt
- `binary_sensor: platform: gpio, pin: GPIO0` (snooze_button) → komplett entfernt
- Hardcodierte Wochentag-Bedingung in `on_time` → durch `weekday_only` Global + Switch ersetzt

### Melodien (bestehend, bleibt erhalten)
- 3 RTTTL-Melodien: Reveille (Standard), Entertainer, Frere Jacques
- Auswahl über `alarm_melody_select` HA-Select-Entity
- Melodie-Wiederholung via `on_finished_playback` mit 15s Pause

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bestehende Implementierung
- `alarm-clock.yaml` — Vollständige aktuelle ESPHome-Config. Enthält bereits große Teile der Alarm-Logik. Änderungen sind chirurgisch: I2S statt LEDC, GPIO0-Sensor entfernen, weekday_only Switch ergänzen.

### Hardware
- **LilyGo T-RGB ESP32-S3** — I2S-Pins sind dediziert herausgeführt (genaue Pin-Nummern aus Schaltplan/Pinout ermitteln vor Implementierung)
- **MAX98357A** — I2S Mono-Verstärker, externer Lautsprecher (4Ω oder 8Ω, 1–3W)
- GPIO0 ist der Boot-Button — wird **nicht** für Snooze verwendet

### Anforderungen
- `.planning/REQUIREMENTS.md` — ALRM-01 bis ALRM-06, DISP-04, DISP-05

### Bekannte Entscheidungen aus STATE.md
- ESP-IDF Framework ist Pflicht (kein Arduino) — `i2s_audio` ist ESP-IDF-kompatibel
- PSRAM 8MB octal aktiv
- ft5x06 Touchscreen auf Adresse 0x38

</canonical_refs>
