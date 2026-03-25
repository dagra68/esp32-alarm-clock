# Phase 2: Alarm-Kernfunktion - Research

**Researched:** 2026-03-25
**Domain:** ESPHome Alarm-Logik, I2S Audio (MAX98357A), RTTTL Speaker, LVGL Alarm-Pages, Wochentag-Filter via HA-Switch
**Confidence:** HIGH (Logik und LVGL), MEDIUM (I2S-Pin-Nummern des T-RGB)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Audio-Output:**
- MAX98357A I2S-Verstaerker-Modul (externer Lautsprecher, Mono, 3W)
- Anschluss an die dedizierten I2S-Pins des LilyGo T-RGB Boards (bereits herausgefuehrt)
- ESPHome `i2s_audio`-Komponente mit `dac_type: external`
- RTTTL-Komponente nutzt den I2S-Output (ersetzt bestehenden `ledc`-Output auf GPIO38)
- Bestehender `output: platform: ledc, pin: GPIO38` wird entfernt

**Snooze und Alarm-Stopp:**
- Ausschliesslich per Touch auf der `alarm_ringing_page`
- Zwei Buttons: "Snooze 5min" und "Stopp"
- Keine physische Taste -- bestehender GPIO0 `binary_sensor` (snooze_button) wird entfernt

**Wochentag-Filter (Mo-Fr):**
- Neuer HA-Switch: "Nur Mo-Fr" (`weekday_only`, bool, `restore_value: yes`)
- EIN: Alarm klingelt nur Montag-Freitag
- AUS: Alarm klingelt jeden Tag
- `on_time`-Lambda prueft: `bool day_ok = !id(weekday_only) || (now.day_of_week >= 2 && now.day_of_week <= 6);`
- Aktuell ist Mo-Fr hardcodiert in der `on_time`-Lambda -- das wird durch den Switch ersetzt

**Alarm-Logik (bestehend, bleibt erhalten):**
- `on_time` Trigger: jede Minute, prueft alarm_enabled + day_ok + Stunde/Minute
- `alarm_timeout_script`: Auto-Aus nach 5 min
- `snooze_action`: RTTTL stopp -> 5 min warten -> Alarm erneut ausloesen -> alarm_ringing_page zeigen
- `alarm_stop_action`: RTTTL stopp -> alarm_ringing = false -> alarm_enabled = false -> zurueck zur Uhr
- Globals: `alarm_hour`, `alarm_minute`, `alarm_enabled`, `alarm_ringing`, `alarm_melody_name` -- alle mit `restore_value`

**Alarm-UI (bestehend, bleibt erhalten):**
- `alarm_ringing_page`: wird automatisch bei Alarm-Trigger gezeigt, Snooze + Stopp Buttons
- `alarm_settings_page`: +/- Buttons fuer Stunde/Minute, Zugang via Long-Press auf Alarm-Button
- Alarm-Button auf `analog_clock_page`: Short-Click = Toggle Ein/Aus, Long-Press = Settings

**Was entfernt wird:**
- `output: platform: ledc, pin: GPIO38` -> durch `i2s_audio`-Output ersetzt
- `binary_sensor: platform: gpio, pin: GPIO0` (snooze_button) -> komplett entfernt
- Hardcodierte Wochentag-Bedingung in `on_time` -> durch `weekday_only` Global + Switch ersetzt

**Melodien (bestehend, bleibt erhalten):**
- 3 RTTTL-Melodien: Reveille (Standard), Entertainer, Frere Jacques
- Auswahl ueber `alarm_melody_select` HA-Select-Entity
- Melodie-Wiederholung via `on_finished_playback` mit 15s Pause

### Claude's Discretion

Keine explizit als Discretion markierten Bereiche in der CONTEXT.md.

### Deferred Ideas (OUT OF SCOPE)

Keine explizit markierten Deferred Ideas.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ALRM-01 | Nutzer kann eine Alarmzeit (Stunde + Minute) fuer Mo-Fr konfigurieren | `datetime: platform: template` mit `alarm_hour`/`alarm_minute` Globals + `weekday_only` Switch -- beides bereits im YAML vorhanden, Switch ist neu |
| ALRM-02 | Nutzer kann die Alarmzeit direkt am Touch-Display einstellen | `alarm_settings_page` mit +/- Buttons bereits implementiert; Long-Press auf Alarm-Button oeffnet Settings |
| ALRM-03 | Alarm loest Mo-Fr zur konfigurierten Zeit eine RTTTL-Melodie aus | `on_time`-Lambda prueft Wochentag-Bedingung; RTTTL via `speaker` (I2S statt LEDC); `on_finished_playback`-Loop |
| ALRM-04 | Nutzer kann den Alarm per Touch-Button dauerhaft ausschalten | `alarm_stop_action` Script: rtttl.stop + alarm_ringing=false + alarm_enabled=false + Page zurueck |
| ALRM-05 | Nutzer kann 5 Minuten Snooze ausloesen (per CONTEXT.md: Touch statt physischer Taste) | `snooze_action` Script + Snooze-Button auf `alarm_ringing_page`; GPIO0 binary_sensor wird entfernt |
| ALRM-06 | Nutzer kann den Alarm per Toggle aktivieren und deaktivieren | Short-Click auf Alarm-Button toggelt `alarm_enabled`; Farbaenderung des Labels als visuelles Feedback |
| DISP-04 | Nutzer sieht wann der naechste Alarm ausgeloest wird | Alarm-Label auf `analog_clock_page` zeigt Glocken-Symbol + Zeit (LV_SYMBOL_BELL + HH:MM) |
| DISP-05 | Nutzer sieht ob der Alarm aktiviert oder deaktiviert ist | Label-Farbe: 0xFFAA00 (aktiv) vs 0x666666 (inaktiv) auf Alarm-Button |
</phase_requirements>

---

## Summary

Phase 2 ist primativ eine **chirurgische Aenderung** an der bestehenden `alarm-clock.yaml`, die bereits grosse Teile der Alarm-Logik enthaelt. Die drei Kerneingriffe sind: (1) LEDC-Buzzer-Output auf GPIO38 durch I2S-Audio mit MAX98357A ersetzen, (2) GPIO0 Binary-Sensor (Snooze-Button) entfernen, (3) hardcodierte Mo-Fr-Bedingung durch einen neuen `weekday_only` HA-Switch ersetzen.

Der groesste technische Unsicherheitsfaktor ist die Ermittlung der korrekten I2S-Pin-Nummern des T-RGB Boards. Die offizielle `utilities.h` des Boards listet GPIO38 als SD-Karte DAT (erklaert warum der bisherige LEDC-Buzzer funktioniert hat, solange keine SD-Karte steckt). Die eigentlichen I2S-Pins (BCLK, LRCLK/WS, DOUT) muessen aus dem Board-Schaltplan ermittelt werden -- sie sind nicht in der offiziellen Dokumentation veroeffntlicht.

Ein weiterer wichtiger Fund: ESPHome hatte bis Version 2025.7 einen Bug bei RTTTL + Speaker (spielte nur einmal, dann haengt der State). Dieser wurde mit PR #10381 am 28. August 2025 gefixt. Mit ESPHome >= 2026.x (aktuelle Version) ist kein Workaround noetig.

**Primary recommendation:** Erst I2S-Pin-Nummern aus T-RGB-Schaltplan ermitteln (erster Task), dann LEDC->I2S migrieren und GPIO0-Sensor entfernen (zweiter Task), dann `weekday_only`-Switch ergaenzen (dritter Task). Jeder Task endet mit `esphome compile`.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ESPHome | 2026.x | Firmware-Framework | Bereits im Projekt, alle Komponenten nativ |
| i2s_audio | ESPHome built-in | I2S Bus-Konfiguration | Einzige offizielle I2S-Implementierung in ESPHome |
| speaker (i2s_audio) | ESPHome built-in | Audio-Output fuer RTTTL | Einzige Moeglichkeit RTTTL ueber I2S auszugeben |
| rtttl | ESPHome built-in | RTTTL-Melodie-Wiedergabe | Bereits im YAML; jetzt `speaker:` statt `output:` |
| globals | ESPHome built-in | Persistente State-Variablen | Alarm-Zustand ueber Reboots hinweg erhalten |
| switch (template) | ESPHome built-in | `weekday_only` HA-Switch | Neuer Switch fuer Mo-Fr-Filter |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| datetime (template) | ESPHome built-in | Alarmzeit als HA-Entity | Bereits vorhanden; ermoeglicht HA-Steuerung der Alarmzeit |
| script | ESPHome built-in | Alarm-Aktionen | snooze_action, alarm_stop_action, alarm_timeout_script |
| lvgl | ESPHome built-in | UI-Pages und Widgets | alarm_ringing_page, alarm_settings_page bereits vorhanden |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| i2s_audio speaker | ledc output (LEDC PWM) | LEDC auf GPIO38 ist SD-Karte DAT; I2S = echter Lautsprecher mit Verstaerker |
| weekday_only Global+Switch | Hardcodierte Bedingung | Switch macht Mo-Fr per HA umschaltbar; flexibler |
| Touch-only Snooze | GPIO0 physical button | GPIO0 ist Boot-Strapping-Pin, nicht zuverlaessig als Input; Touch ist robuster |

**Installation:**
```bash
# Kein neues npm/pip install noetig -- ESPHome bereits installiert
esphome compile alarm-clock.yaml
esphome upload alarm-clock.yaml
```

---

## Architecture Patterns

### Recommended Project Structure (Phase 2)

```
alarm-clock/
  alarm-clock.yaml          # Einzeldatei -- alle Aenderungen hier
                            # Package-Split erst ab Phase 3 wenn HA-Integration komplex wird
```

**Rationale:** Die Aenderungen sind chirurgisch (3 konkrete Eingriffe). Eine einzige Datei bleibt ueberschaubar. Die YAML ist bereits ~670 Zeilen -- Package-Aufteilung kann in Phase 3 erfolgen.

### Pattern 1: I2S Audio + RTTTL Speaker (Kernmuster Phase 2)

**What:** `i2s_audio`-Bus definieren, `speaker: platform: i2s_audio` mit externem DAC, `rtttl: speaker: my_speaker`
**When to use:** Immer wenn RTTTL ueber MAX98357A ausgegeben werden soll

```yaml
# Source: https://esphome.io/components/i2s_audio/
# Source: https://esphome.io/components/speaker/i2s_audio/
# Source: https://esphome.io/components/rtttl/
i2s_audio:
  i2s_lrclk_pin: GPIO_XX  # T-RGB I2S WS/LRCLK Pin -- aus Schaltplan ermitteln
  i2s_bclk_pin: GPIO_XX   # T-RGB I2S BCLK Pin -- aus Schaltplan ermitteln

speaker:
  - platform: i2s_audio
    id: alarm_speaker
    dac_type: external
    i2s_dout_pin: GPIO_XX  # T-RGB I2S DOUT Pin -- aus Schaltplan ermitteln
    channel: mono
    sample_rate: 16000
    bits_per_sample: 16bit

rtttl:
  speaker: alarm_speaker   # Ersetzt: output: buzzer_output
  id: alarm_buzzer
  gain: 0.8
  on_finished_playback:
    - if:
        condition:
          lambda: 'return id(alarm_ringing);'
        then:
          - delay: 15s
          - rtttl.play: !lambda |-
              # ... Melodie-Auswahl Lambda (unveraendert)
```

### Pattern 2: weekday_only Global + Switch

**What:** Neuer bool-Global mit `restore_value: yes` + Template-Switch der ihn steuert
**When to use:** Wochentag-Filter per HA steuerbar machen

```yaml
# Source: https://esphome.io/components/globals/
# Source: https://esphome.io/components/switch/template/
globals:
  # Bestehende Globals unveraendert, NEU hinzufuegen:
  - id: weekday_only
    type: bool
    restore_value: yes
    initial_value: 'true'  # Standard: nur Mo-Fr

switch:
  # Bestehender alarm_enabled_switch unveraendert
  # NEU hinzufuegen:
  - platform: template
    name: "Nur Mo-Fr"
    id: weekday_only_switch
    icon: mdi:calendar-week
    restore_mode: RESTORE_DEFAULT_ON  # Standard: nur Mo-Fr aktiv
    lambda: |-
      return id(weekday_only);
    turn_on_action:
      - globals.set:
          id: weekday_only
          value: 'true'
    turn_off_action:
      - globals.set:
          id: weekday_only
          value: 'false'
```

### Pattern 3: on_time Lambda mit weekday_only-Check

**What:** Bestehende hardcodierte Mo-Fr-Bedingung durch dynamischen Global-Check ersetzen
**When to use:** In der `on_time` Automation der SNTP-Komponente

```yaml
# Bestehende hardcodierte Bedingung (wird ersetzt):
# bool is_weekday = (now.day_of_week >= 2 && now.day_of_week <= 6);
# if (id(alarm_enabled) && is_weekday && ...)

# Neue Bedingung mit weekday_only Switch:
on_time:
  - seconds: 0
    minutes: /1
    then:
      - lambda: |-
          if (id(alarm_ringing)) return;
          auto now = id(sntp_time).now();
          if (!now.is_valid()) return;
          // day_of_week: 1=Sonntag, 2=Montag, ..., 6=Freitag, 7=Samstag
          bool day_ok = !id(weekday_only) || (now.day_of_week >= 2 && now.day_of_week <= 6);
          if (id(alarm_enabled) && day_ok &&
              now.hour == id(alarm_hour) && now.minute == id(alarm_minute)) {
            id(alarm_ringing) = true;
            id(alarm_timeout_script).execute();
          }
      # Rest der on_time Automation unveraendert
```

**Hinweis:** `day_of_week` in ESPHome: 1=Sonntag, 2=Montag, 3=Dienstag, 4=Mittwoch, 5=Donnerstag, 6=Freitag, 7=Samstag. Der bestehende Code `>= 2 && <= 6` deckt korrekt Mo-Fr ab.

### Anti-Patterns to Avoid

- **GPIO38 fuer Buzzer beibehalten (LEDC):** GPIO38 ist laut `utilities.h` als SD-Karte DAT definiert. Solange keine SD-Karte steckt funktioniert LEDC, aber es ist eine unbeabsichtigte Pin-Verwendung. I2S ist die korrekte Loesung.
- **GPIO0 als physische Snooze-Taste nutzen:** GPIO0 ist Boot-Strapping-Pin. Laut CONTEXT.md-Entscheidung: komplett entfernen.
- **rtttl `output:` statt `speaker:` verwenden:** Mit I2S-Verstaerker muss `speaker:` genutzt werden. `output:` funktioniert nur mit LEDC PWM.
- **ESPHome < 2025.8 + RTTTL Speaker:** Bug: RTTTL spielte nur einmal (State-Machine-Fehler). Gefixt in PR #10381 (August 2025). Mit ESPHome 2026.x kein Workaround noetig.
- **I2S-Pins schätzen statt aus Schaltplan lesen:** Die ESP32-S3-GPIO-Matrix erlaubt zwar beliebige I2S-Pin-Zuweisungen, aber das MAX98357A-Modul muss physisch verdrahtet sein -- die tatsaechlichen Pins haengen von der Hardware-Verkabelung ab.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RTTTL-Wiedergabe | Eigene Notenfrequenz-Berechnung | ESPHome `rtttl`-Komponente | RTTTL-Parser, Timing-Logik, Speaker-Anbindung bereits geloest |
| Audio-Timeout | Eigener Counter/Timer | `script: mode: restart` + `delay: 5min` | Script-Restart-Mechanismus verhindert doppeltes Ausfuehren |
| Alarm-State-Persistenz | NVS-Schreibcode | `globals: restore_value: yes` | ESPHome handled NVS-Lesen/-Schreiben automatisch |
| Touch-Button-Logik | Manuelles Touch-Koordinaten-Mapping | LVGL `button: on_short_click` | LVGL handhabt Hit-Testing und Debouncing |

**Key insight:** Die gesamte Alarm-Logik ist bereits implementiert. Phase 2 ist Refactoring, kein Neuaufbau.

---

## Common Pitfalls

### Pitfall 1: I2S-Pin-Nummern unbekannt -- T-RGB-Schaltplan pflicht

**What goes wrong:** Kompilierung schlaegt fehl oder kein Ton, weil falsche GPIO-Nummern fuer BCLK/LRCLK/DOUT eingetragen sind.
**Why it happens:** LilyGo dokumentiert die I2S-Pins des T-RGB nicht prominent in der README. Die `utilities.h` zeigt nur Display/SD/I2C-Pins.
**How to avoid:** Schaltplan aus GitHub herunterladen (`/schematic/T-RGB.pdf`) und I2S-Pins identifizieren. Alternativ: physische Verdrahtung des MAX98357A-Moduls an beliebige freie ESP32-S3-GPIOs und entsprechend in YAML eintragen.
**Warning signs:** Compile-Fehler "Invalid pin" oder kein Ton trotz korrekter YAML-Syntax.

**Bekannte GPIO-Belegung (aus utilities.h):**

| GPIO | Funktion |
|------|---------|
| 1 | Touch IRQ |
| 2-18, 21, 43-45 | RGB Display Datenpins |
| 39 | SD Card CLK |
| 40 | SD Card CMD |
| 38 | SD Card DAT |
| 42 | Display PCLK |
| 46 | Backlight |
| 47 | Display HSYNC |
| 48 | I2C SCL |
| 8 | I2C SDA |
| 4 | ADC/SPI MOSI (XL9535) |
| 5 | SPI CLK (XL9535) |
| 41 | Display VSYNC |

**Potenziell freie GPIOs** (nicht in utilities.h als belegt gelistet): GPIO0 (Boot-Button, nicht fuer Snooze), GPIO19, GPIO20 -- aber Verifikation am Schaltplan ist Pflicht.

### Pitfall 2: RTTTL-Bug bei Speaker (ESPHome < 2025.8)

**What goes wrong:** Alarm klingelt beim ersten Ausloesen, aber beim zweiten Alarm (nach Snooze oder am naechsten Tag) kommt kein Ton.
**Why it happens:** Bug in RTTTL + Speaker State-Machine: nach dem ersten Play bleibt State in STATE_STOPPING haengen. Loop wird deaktiviert.
**How to avoid:** ESPHome 2026.x nutzen (Bug seit PR #10381 gefixt). Bei aelteren Versionen Workaround: nach `rtttl.play` ein `lambda: id(alarm_buzzer).enable_loop();` ausfuehren.
**Warning signs:** Erster Alarm funktioniert, zweiter ist lautlos.

### Pitfall 3: `alarm_enabled_switch` restore_mode DISABLED -- Switch-State geht verloren

**What goes wrong:** Nach Reboot ist der Alarm-Switch im HA immer AUS, obwohl er vorher EIN war.
**Why it happens:** `restore_mode: DISABLED` im bestehenden `alarm_enabled_switch`. Der globale `alarm_enabled` bool hat `restore_value: yes`, aber der Switch-State wird nicht aus NVS wiederhergestellt.
**How to avoid:** Der Switch-State wird via Lambda aus dem Global gelesen -- das ist korrekt. Der Global persitiert. Kein Aenderungsbedarf, aber beim neuen `weekday_only_switch` auf `RESTORE_DEFAULT_ON` setzen (nicht DISABLED).
**Warning signs:** Nach Reboot zeigt HA-Switch falschen Zustand, aber Alarm klingelt trotzdem korrekt (weil Global den echten Zustand haelt).

### Pitfall 4: on_finished_playback vs. Loop -- Melodie endet nie

**What goes wrong:** `on_finished_playback` wird nicht ausgeloest, Melodie-Loop laeuft nicht.
**Why it happens:** Bei LEDC-Output lief die Melodie einmal und `on_finished_playback` wurde ausgeloest. Bei Speaker ist das Timing anders.
**How to avoid:** Mit `speaker` und ESPHome 2026.x wird `on_finished_playback` korrekt ausgeloest. Testen mit kurzem RTTTL-String.
**Warning signs:** Melodie spielt einmal und stoppt, kein Wiederholungs-Delay.

### Pitfall 5: `alarm_ringing` State nach Reboot

**What goes wrong:** Nach ungeplantem Reboot waehrend eines Alarms ist `alarm_ringing = false` (kein `restore_value`), aber der RTTTL-Player laeuft weiter.
**Why it happens:** `alarm_ringing` hat bewusst `restore_value: no` -- das ist korrekt, ein Alarm soll nach Reboot nicht wieder anfangen.
**How to avoid:** Kein Aenderungsbedarf -- das Verhalten ist intentional.

---

## Code Examples

### I2S Audio + RTTTL Speaker Vollkonfiguration (Template)

```yaml
# Source: https://esphome.io/components/i2s_audio/
# Source: https://esphome.io/components/speaker/i2s_audio/
# Source: https://esphome.io/components/rtttl/

# I2S Bus (Pin-Nummern aus T-RGB Schaltplan ermitteln!)
i2s_audio:
  i2s_lrclk_pin: GPIOX   # WS-Pin des MAX98357A -- aus Schaltplan
  i2s_bclk_pin:  GPIOX   # BCLK-Pin des MAX98357A -- aus Schaltplan

speaker:
  - platform: i2s_audio
    id: alarm_speaker
    dac_type: external
    i2s_dout_pin: GPIOX   # DIN-Pin des MAX98357A -- aus Schaltplan
    channel: mono
    sample_rate: 16000
    bits_per_sample: 16bit

# RTTTL: output: buzzer_output ENTFERNEN, speaker: alarm_speaker HINZUFUEGEN
rtttl:
  speaker: alarm_speaker
  id: alarm_buzzer
  gain: 0.8
  on_finished_playback:
    - if:
        condition:
          lambda: 'return id(alarm_ringing);'
        then:
          - delay: 15s
          - rtttl.play: !lambda |-
              if (id(alarm_melody_name) == "Entertainer")
                return std::string("Entertainer:d=4,o=5,b=140:8d,8d#,8e,c,8e,c,8e,2b.,8c6,8c6,8c6,2a.,8b.,8a,8g,8a,8b,a,8a.,8g,8f#,8e,8d,2g,p");
              if (id(alarm_melody_name) == "Frere Jacques")
                return std::string("FrereJacques:d=4,o=5,b=126:c,d,e,c,c,d,e,c,e,f,2g,e,f,2g");
              return std::string("Reveille:d=4,o=5,b=120:8g,8g,8g,8c,8e,8g,2c6,8e,8g,2c6,8e,8g,8c6,8e6,8d6,8c6,8d6,8e6,8c6,8g,8e,2c");
```

### Entfernte Abschnitte

```yaml
# ENTFERNEN -- output buzzer_output (LEDC GPIO38):
# output:
#   - platform: ledc
#     id: buzzer_output
#     pin: GPIO38
#     frequency: 1000Hz

# ENTFERNEN -- snooze_button binary_sensor (GPIO0):
# binary_sensor:
#   - platform: gpio
#     pin:
#       number: GPIO0
#       mode: { input: true, pullup: true }
#       inverted: true
#       ignore_strapping_warning: true
#     id: snooze_button
#     ...
```

### ESPTime day_of_week Referenz

```
# Source: https://esphome.io/components/time/index.html
# day_of_week Werte in ESPHome:
# 1 = Sonntag
# 2 = Montag
# 3 = Dienstag
# 4 = Mittwoch
# 5 = Donnerstag
# 6 = Freitag
# 7 = Samstag
# Mo-Fr: now.day_of_week >= 2 && now.day_of_week <= 6  (bereits korrekt im YAML)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LEDC PWM auf GPIO38 fuer Buzzer | I2S Speaker mit MAX98357A | CONTEXT.md-Entscheidung Phase 2 | Echter Lautsprecher statt Piezo, besserer Klang |
| Physische Snooze-Taste (GPIO0) | Touch-only Snooze | CONTEXT.md-Entscheidung Phase 2 | Weniger Hardware-Komplexitaet |
| `rtttl: output: buzzer_output` | `rtttl: speaker: alarm_speaker` | ESPHome seit 2024.x | RTTTL kann I2S-Speaker verwenden |
| Hardcodiertes Mo-Fr in Lambda | `weekday_only` Global + HA-Switch | Phase 2 | Per HA umschaltbar |
| RTTTL-Speaker-Bug (nur 1x spielen) | Gefixt in ESPHome >= 2025.8 | PR #10381, Aug 2025 | Kein Workaround mehr noetig |

**Deprecated/outdated:**
- `output: platform: ledc` fuer Alarm-Ton: Wird durch `speaker: platform: i2s_audio` ersetzt
- `binary_sensor: platform: gpio, pin: GPIO0`: Wird komplett entfernt

---

## Open Questions

1. **I2S-Pin-Nummern des T-RGB Boards**
   - What we know: GPIO38=SD DAT, GPIO39=SD CLK, GPIO40=SD CMD -- diese sind belegt. Alle RGB-Display-Datenpins (2-18, 21, 43-45) sind belegt.
   - What's unclear: Welche GPIOs das Board physisch als I2S-Pins herausfuehrt (Connector/Loetstellen). Die CONTEXT.md nennt "dedizierte I2S-Pins ... bereits herausgefuehrt" -- das impliziert, dass Pins vorhanden sind.
   - Recommendation: **Erster Task in Phase 2**: T-RGB-Schaltplan (`/schematic/T-RGB.pdf` aus LilyGo GitHub) herunterladen und I2S-Pins identifizieren. Alternativ: physische Pins am Board messen/dokumentieren. Potenziell freie Kandidaten: GPIO19, GPIO20 (nicht in utilities.h als belegt gelistet).

2. **MAX98357A Versorgungsspannung**
   - What we know: Community-Berichte empfehlen 5V statt 3.3V fuer MAX98357A um statisches Rauschen zu reduzieren (ESPHome Issue #6653 Diskussion Nov 2024).
   - What's unclear: Ob T-RGB 5V ueber den Connector herausfuehrt.
   - Recommendation: Beim Hardware-Aufbau mit 5V versuchen, falls verfuegbar.

3. **I2S-Bus Konflikt mit Display**
   - What we know: Das T-RGB nutzt MIPI-RGB (parallel RGB Interface), nicht I2S. Der I2S-Bus ist im ESP32-S3 ein separates Peripheral.
   - What's unclear: Ob der ESP32-S3 beide I2S-Instanzen (I2S0, I2S1) frei hat.
   - Recommendation: LOW Risiko -- Display nutzt kein I2S. Kein erwarteter Konflikt.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | ESPHome compile + OTA flash + visuelle/auditive Pruefung |
| Config file | alarm-clock.yaml |
| Quick run command | `esphome compile alarm-clock.yaml` |
| Full suite command | `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ALRM-01 | Alarmzeit konfigurierbar (Stunde + Minute), Wochentag-Filter per Switch | compile + manual | `esphome compile alarm-clock.yaml` | besteht (Aenderung) |
| ALRM-02 | Alarmzeit per Touch einstellen | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (unveraendert) |
| ALRM-03 | Alarm loest RTTTL-Melodie aus | compile + manual (auditiv) | `esphome compile alarm-clock.yaml` | besteht (Aenderung: I2S) |
| ALRM-04 | Alarm per Touch stoppen | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (unveraendert) |
| ALRM-05 | 5 Minuten Snooze per Touch | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (Aenderung: GPIO0 entfernt) |
| ALRM-06 | Alarm per Toggle aktivieren/deaktivieren | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (unveraendert) |
| DISP-04 | Naechste Alarmzeit auf Display sichtbar | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (unveraendert) |
| DISP-05 | Alarm-Status (ein/aus) auf Display sichtbar | manual (visuell) | `esphome compile alarm-clock.yaml` | besteht (unveraendert) |

### Sampling Rate

- **Per task commit:** `esphome compile alarm-clock.yaml`
- **Per wave merge:** Compile + OTA Upload + Funktionstest am Board
- **Phase gate:** Alarm klingelt zur eingestellten Zeit (Mo-Fr), Snooze/Stopp per Touch, Melodie hoerbar ueber Lautsprecher

### Wave 0 Gaps

- [ ] I2S-Pin-Nummern aus T-RGB-Schaltplan ermitteln (Blocker fuer I2S-Konfiguration)
- [ ] MAX98357A physisch anschliessen und korrekte GPIO-Nummern in YAML eintragen

*(Hinweis: `alarm-clock.yaml` existiert bereits und ist funktionstuechtiger Ausgangszustand)*

---

## Sources

### Primary (HIGH confidence)

- [ESPHome I2S Audio Component](https://esphome.io/components/i2s_audio/) -- i2s_lrclk_pin, i2s_bclk_pin Konfiguration
- [ESPHome I2S Audio Speaker](https://esphome.io/components/speaker/i2s_audio/) -- dac_type: external, i2s_dout_pin, channel, sample_rate
- [ESPHome RTTTL Buzzer](https://esphome.io/components/rtttl/) -- speaker: statt output:, on_finished_playback
- [ESPHome Time Component](https://esphome.io/components/time/index.html) -- day_of_week Werte (1=So, 7=Sa), ESPTime struct
- [ESPHome Global Variables](https://esphome.io/components/globals/) -- restore_value, max_restore_data_length
- [ESPHome Template Switch](https://esphome.io/components/switch/template/) -- lambda, turn_on/off_action, restore_mode
- LilyGo T-RGB utilities.h (via GitHub) -- GPIO-Belegungstabelle (Display, SD, I2C, Backlight)

### Secondary (MEDIUM confidence)

- [ESPHome RTTTL Speaker Bug PR #10381](https://github.com/esphome/esphome/issues/10312) -- Bug-Fix bestaetigt fuer ESPHome >= 2025.8
- [ESPHome Community: MAX98357A mit ESP32](https://community.home-assistant.io/t/i2s-esp32-stereo-output-two-max98357a/573741) -- Praxiserfahrungen, 5V-Empfehlung

### Tertiary (LOW confidence)

- LilyGo T-RGB Schaltplan (`/schematic/T-RGB.pdf`) -- I2S-Pin-Nummern **noch nicht verifiziert** (PDF nicht direkt lesbar via WebFetch)

---

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH -- Alle ESPHome-Komponenten offiziell dokumentiert; Einsatz von i2s_audio + speaker + rtttl ist etabliertes Muster
- Architecture: HIGH -- Bestehende alarm-clock.yaml ist vollstaendiger Ausgangszustand; Aenderungen sind klar umrissen
- Alarm-Logik (on_time, scripts, globals): HIGH -- Alles bereits im YAML implementiert und verifiziert
- I2S-Pin-Nummern T-RGB: LOW -- Nicht in offizieller Doku; Schaltplan-Analyse vor Implementierung erforderlich
- Pitfalls: HIGH -- RTTTL-Bug verifiziert und gefixt; GPIO-Belegung aus utilities.h direkt gelesen

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stabiler ESPHome-Stack; I2S-Pins aendern sich nicht)
