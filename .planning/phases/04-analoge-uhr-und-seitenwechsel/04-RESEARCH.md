# Phase 4: Analoge Uhr und Seitenwechsel - Research

**Researched:** 2026-03-24
**Domain:** ESPHome LVGL Meter-Widget, Seitenwechsel, Home Assistant Select-Entity
**Confidence:** HIGH

## Summary

Phase 4 fuegt eine analoge Uhren-Seite via LVGL Meter-Widget hinzu und ermoeglicht den Wechsel zwischen Digital- und Analog-Zifferblatt ueber eine Home Assistant Select-Entity. Die Implementierung basiert auf dem offiziellen ESPHome-Cookbook-Beispiel fuer analoge Uhren, das drei Meter-Scales verwendet: Minuten-Ticks (0-60), Stunden-Labels (1-12), und eine hochaufloesende Stunden-Skala (0-720) fuer praezise Zeiger-Positionierung.

Das bestehende Projekt hat bereits alle notwendigen Patterns etabliert: `lvgl.page.show:` fuer Seitenwechsel, `select:` Template-Entities fuer HA-Steuerung (Melodie-Select als Vorlage), und minuetliche Time-Trigger fuer Updates. Die Analog-Uhr erfordert keinen Sekundenzeiger (laut CONTEXT.md), was den Update-Takt auf einmal pro Minute vereinfacht -- identisch zum bestehenden `on_time` Trigger.

**Primary recommendation:** Das offizielle ESPHome-Cookbook Analog-Clock-Beispiel 1:1 uebernehmen, Sekundenzeiger weglassen, Farben an Pink-Theme anpassen, und via Select-Entity `set_action` mit `lvgl.page.show:` zwischen Seiten wechseln.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- LVGL Meter-Widget (`lv_meter`) -- kein Custom-Lambda/Canvas
- Nur Stunden- und Minutenzeiger -- kein Sekundenzeiger
- Update-Takt: minutenweise (kein eigener 1s-Interval noetig)
- Zeiger-Farbe: Schwarz (`0x000000`)
- 12 Zahlen (1-12) auf dem Zifferblatt via Polar-Koordinaten-Lambda
- Seitenwechsel ausschliesslich ueber Home Assistant Select-Entity
- Select-Entity mit Optionen: "Digital", "Analog" -- erweiterbar
- Kein Touch-Trigger fuer Seitenwechsel
- ESPHome-Seite wechselt via `lvgl.page.show:` im `set_action` der Select-Entity
- Hintergrundfarbe Standard: Pink `0xFF69B4`
- Farb-Select mit vordefinierten Optionen (mind. 4: Pink, Weiss, Schwarz, Dunkelblau)
- Farb-Select setzt globale Variable, Lambda aktualisiert `bg_color`

### Claude's Discretion
- Exakte Radius-Werte fuer Zahlen-Positionierung auf dem runden Display
- Meter-Widget arc-Konfiguration (Winkelbereich, Skalierung)
- Anzahl der Farboptionen im Farb-Select (mindestens 4)
- Name und Icon der neuen HA-Entities

### Deferred Ideas (OUT OF SCOPE)
- Weitere Zifferblatt-Designs (z.B. Minimal, Dark) -- ueber Select-Entity spaeter erweiterbar
- Animierter Sekundenzeiger mit Sweep -- v2 Requirement UX-02 / DISP-07
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DISP-02 | Nutzer sieht analoge Uhr mit Stunden- und Minutenzeiger (LVGL Meter-Widget) | Offizielles ESPHome-Cookbook liefert vollstaendiges Meter-Widget-Beispiel mit 3 Scales; Sekundenzeiger wird weggelassen per CONTEXT.md |
| DISP-06 | Nutzer kann per Touch/HA zwischen analogem und digitalem Zifferblatt wechseln | Select-Entity mit `set_action` + `lvgl.page.show:` -- bestehendes Pattern im Projekt; Touch ist Out-of-Scope per CONTEXT.md |
</phase_requirements>

## Standard Stack

### Core
| Komponente | Version | Zweck | Warum Standard |
|------------|---------|-------|----------------|
| ESPHome LVGL `meter` Widget | ESPHome 2024.x+ | Analoge Uhren-Darstellung mit Skalen und Zeigern | Offizielles Cookbook-Beispiel, nativ in ESPHome integriert |
| ESPHome `select` Template | ESPHome 2024.x+ | HA-Entity fuer Seitenwechsel und Farbauswahl | Bereits im Projekt fuer Melodie-Select verwendet |
| `lvgl.page.show:` Action | ESPHome 2024.x+ | Seitenwechsel zwischen Pages | Bereits im Projekt fuer Alarm-Navigation verwendet |
| `lvgl.indicator.update:` Action | ESPHome 2024.x+ | Zeiger-Positionen aktualisieren | Offizielle API fuer Meter-Indicator-Updates |

### Supporting
| Komponente | Zweck | Wann nutzen |
|------------|-------|-------------|
| `globals` (int/string) | Farb-Zustand speichern | Fuer Hintergrundfarb-Persistenz |
| `lvgl.label.update:` | Stunden-Zahlen und Datum | Fuer die 12 Label-Widgets auf dem Zifferblatt |
| `sntp_time` | NTP-synchronisierte Zeit | Bereits vorhanden -- Zeiger-Update-Quelle |

### Alternatives Considered
| Statt | Koennte man | Tradeoff |
|-------|-------------|----------|
| Meter-Widget | Canvas/Custom-Lambda | Mehr Kontrolle, aber enormer Aufwand -- Meter ist die offizielle Loesung |
| Select-Entity | Touch-Swipe | Touch-Swipe in ESPHome nicht robust (Issue #3059); Select ist zuverlaessiger |
| 12 separate Labels | Meter `label_gap` | Meter-Labels sind automatisch, aber Positionierung auf rundem Display ist ungenau; Polar-Koordinaten-Labels geben volle Kontrolle |

## Architecture Patterns

### Empfohlene Struktur in alarm-clock.yaml

```
alarm-clock.yaml Erweiterungen:
  globals:          + bg_color_hex (int, restore_value)
  select:           + Zifferblatt-Select (Digital/Analog)
                    + Hintergrundfarbe-Select (Pink/Weiss/Schwarz/Dunkelblau)
  lvgl: pages:      + analog_clock_page (neue Seite)
  script:           + analog_time_update (Zeiger-Aktualisierung)
  time: on_time:    Erweiterung: analog_time_update aufrufen
```

### Pattern 1: Meter-Widget mit 3 Skalen (Offizielles Cookbook-Pattern)

**Was:** Drei ueberlagerte Skalen auf einem Meter-Widget -- Minuten, Stunden-Labels, Stunden-Zeiger
**Wann:** Immer bei analogen Uhren mit LVGL Meter
**Beispiel:**
```yaml
# Quelle: https://github.com/esphome/esphome-docs (cookbook/lvgl.mdx)
- meter:
    height: 220
    width: 220
    align: CENTER
    bg_opa: TRANSP
    border_width: 0
    text_color: 0x000000
    scales:
      - range_from: 0        # Minuten-Skala
        range_to: 60
        angle_range: 360
        rotation: 270
        ticks:
          width: 1
          count: 61
          length: 10
          color: 0x000000
        indicators:
          - line:
              id: minute_hand
              width: 3
              color: 0x000000    # Schwarz (User-Entscheidung)
              r_mod: -4
              value: 0
      - range_from: 1        # Stunden-Labels
        range_to: 12
        angle_range: 330
        rotation: 300
        ticks:
          width: 1
          count: 12
          length: 1
          major:
            stride: 1
            width: 4
            length: 10
            color: 0x000000
            label_gap: 12
      - range_from: 0        # Stunden-Zeiger (0-720 fuer praezise Position)
        range_to: 720
        angle_range: 360
        rotation: 270
        ticks:
          count: 0
        indicators:
          - line:
              id: hour_hand
              width: 5
              color: 0x000000    # Schwarz (User-Entscheidung)
              r_mod: -30
              value: 0
```

### Pattern 2: Select-Entity fuer Seitenwechsel

**Was:** Template-Select steuert welche LVGL-Page angezeigt wird
**Wann:** HA-gesteuerter Seitenwechsel ohne Touch
**Beispiel:**
```yaml
select:
  - platform: template
    name: "Zifferblatt"
    id: clock_face_select
    icon: mdi:clock-outline
    options:
      - "Digital"
      - "Analog"
    initial_option: "Digital"
    optimistic: true
    set_action:
      - if:
          condition:
            lambda: 'return x == "Analog";'
          then:
            - script.execute: analog_time_update
            - lvgl.page.show: analog_clock_page
          else:
            - lvgl.page.show: digital_clock_page
```

### Pattern 3: Hintergrundfarb-Select mit Global

**Was:** Globale Variable speichert Farbwert, Select-Entity aendert sie
**Wann:** Dynamische Farbwechsel ueber HA
**Beispiel:**
```yaml
globals:
  - id: bg_color_hex
    type: int
    restore_value: yes
    initial_value: '0xFF69B4'    # Pink Standard

select:
  - platform: template
    name: "Hintergrundfarbe"
    id: bg_color_select
    icon: mdi:palette
    options:
      - "Pink"
      - "Weiss"
      - "Schwarz"
      - "Dunkelblau"
    initial_option: "Pink"
    optimistic: true
    set_action:
      - lambda: |-
          if (x == "Pink") id(bg_color_hex) = 0xFF69B4;
          else if (x == "Weiss") id(bg_color_hex) = 0xFFFFFF;
          else if (x == "Schwarz") id(bg_color_hex) = 0x000000;
          else if (x == "Dunkelblau") id(bg_color_hex) = 0x1A1A2E;
      - lvgl.widget.update:
          id: analog_clock_bg
          bg_color: !lambda 'return lv_color_hex(id(bg_color_hex));'
```

### Pattern 4: Zeiger-Update per Minuten-Script

**Was:** Script wird jede Minute aufgerufen und aktualisiert Zeiger-Positionen
**Wann:** Immer bei Analog-Uhr ohne Sekundenzeiger
**Beispiel:**
```yaml
# Quelle: https://github.com/esphome/esphome-docs (cookbook/lvgl.mdx)
script:
  - id: analog_time_update
    then:
      - lvgl.indicator.update:
          id: minute_hand
          value: !lambda 'return id(sntp_time).now().minute;'
      - lvgl.indicator.update:
          id: hour_hand
          value: !lambda |-
            auto now = id(sntp_time).now();
            return std::fmod(now.hour, 12) * 60 + now.minute;

time:
  - platform: sntp
    ...
    on_time:
      - seconds: 0
        minutes: /1
        then:
          # Bestehende Logik bleibt, ergaenzt um:
          - if:
              condition:
                lvgl.page.is_showing: analog_clock_page
              then:
                - script.execute: analog_time_update
```

### Anti-Patterns zu vermeiden
- **Sekundenzeiger hinzufuegen:** Explizit vom User ausgeschlossen, wuerde unnoetige 1s-Updates erzwingen
- **Touch-Seitenwechsel:** Laut CONTEXT.md nicht gewuenscht -- nur HA-Select
- **Feste Farb-Werte statt Global:** Macht Farbwechsel unmoeglich; immer Global + Lambda nutzen
- **Meter-Updates ohne Page-Check:** Unnoetige Updates wenn Digital-Seite aktiv -- `lvgl.page.is_showing` pruefen

## Don't Hand-Roll

| Problem | Nicht bauen | Stattdessen nutzen | Warum |
|---------|-------------|---------------------|-------|
| Zeiger-Zeichnung | Custom Canvas Lambda | LVGL Meter `line` Indicator | Meter berechnet Winkel automatisch aus Wert |
| Skalen-Ticks | Manuelle Linien-Widgets | Meter `ticks` Konfiguration | 60/12 Ticks automatisch verteilt |
| Stunden-Zahlen | 12 einzelne Labels mit sin/cos | Meter `major.label_gap` | LVGL positioniert Labels automatisch an Major-Ticks |
| Seitenwechsel-Logik | Custom State-Machine | `lvgl.page.show:` Action | Native LVGL-Page-Navigation |
| Farbauswahl-UI | Touch-basierter Colorpicker | HA Select-Entity | Einfacher, zuverlaessiger, vom User gewuenscht |

**Key Insight:** Das LVGL Meter-Widget uebernimmt die gesamte Trigonometrie (Winkelberechnung, Zeiger-Rotation, Tick-Verteilung). Man gibt nur Werte (0-60 fuer Minuten, 0-720 fuer Stunden) und LVGL zeichnet alles.

**Hinweis zu Stunden-Labels:** Der User moechte "12 Zahlen via Polar-Koordinaten-Lambda". Das Meter-Widget bietet jedoch eine eingebaute `major.label_gap` Option, die Labels automatisch an den Major-Ticks positioniert. Dies sollte zuerst getestet werden -- nur falls die automatische Positionierung auf dem runden 480px Display nicht passt, sind manuelle Labels mit sin/cos noetig.

## Common Pitfalls

### Pitfall 1: Stunden-Skala Bereich und Rotation
**Was passiert:** Zeiger zeigt falsche Uhrzeit wenn `range_to` oder `rotation` falsch konfiguriert
**Warum:** Die Stunden-Skala nutzt 0-720 (12 Stunden * 60 Minuten) statt 0-12, damit der Stundenzeiger zwischen den Stunden-Markierungen stehen kann
**Vermeidung:** Exakt das Cookbook-Pattern uebernehmen: `range_to: 720`, `rotation: 270`, Wert = `fmod(hour, 12) * 60 + minute`
**Warnsignale:** Stundenzeiger springt nur auf volle Stunden oder zeigt 180 Grad versetzt

### Pitfall 2: Stunden-Labels Offset (angle_range/rotation)
**Was passiert:** Stunden-Zahlen stehen an falschen Positionen (z.B. "12" nicht oben)
**Warum:** Die Labels-Skala hat `angle_range: 330` und `rotation: 300` (nicht 360/270) -- das ist ein bewusstes Offset damit die Labels korrekt bei den Ticks stehen
**Vermeidung:** Exakt die Cookbook-Werte verwenden: `range_from: 1`, `range_to: 12`, `angle_range: 330`, `rotation: 300`
**Warnsignale:** "12" steht nicht an der 12-Uhr-Position

### Pitfall 3: Meter-Updates auf inaktiver Seite
**Was passiert:** Unnoetige CPU-Last oder visuelle Glitches
**Warum:** `lvgl.indicator.update` auf einem nicht-sichtbaren Widget kann zu Problemen fuehren
**Vermeidung:** Update-Script nur ausfuehren wenn `lvgl.page.is_showing: analog_clock_page` true ist
**Warnsignale:** Logger zeigt haeufige LVGL-Warnings

### Pitfall 4: Select-Entity Initialisierung beim Boot
**Was passiert:** Beim Boot zeigt ESP die falsche Seite oder Select-Entity hat falschen Zustand
**Warum:** `initial_option` und `restore_value` koennen konflikten
**Vermeidung:** `optimistic: true` verwenden (wie bestehendes Melodie-Select), `initial_option: "Digital"` setzen
**Warnsignale:** Nach Neustart zeigt Analog-Seite obwohl Digital erwartet

### Pitfall 5: Hintergrundfarbe mit lv_color_hex
**Was passiert:** Compiler-Fehler oder falsche Farben
**Warum:** `lv_color_hex()` erwartet einen `uint32_t`, nicht einen String
**Vermeidung:** Global als `int` definieren, Werte als Hex-Literale (`0xFF69B4`), in Lambda mit `lv_color_hex(id(bg_color_hex))` konvertieren
**Warnsignale:** Compile-Error bei `bg_color` Lambda

## Code Examples

### Vollstaendige Analog-Clock-Seite (angepasst ans Projekt)
```yaml
# Basiert auf: ESPHome Cookbook Analog Clock
# Angepasst: Kein Sekundenzeiger, schwarze Zeiger, Pink-Hintergrund
- id: analog_clock_page
  widgets:
    - obj:
        id: analog_clock_bg
        width: 480
        height: 480
        align: CENTER
        bg_color: 0xFF69B4
        border_width: 0
        pad_all: 0
        widgets:
          - meter:
              id: analog_meter
              height: 400
              width: 400
              align: CENTER
              bg_opa: TRANSP
              border_width: 0
              text_color: 0x000000
              scales:
                - range_from: 0
                  range_to: 60
                  angle_range: 360
                  rotation: 270
                  ticks:
                    width: 1
                    count: 61
                    length: 10
                    color: 0x000000
                  indicators:
                    - line:
                        id: minute_hand
                        width: 3
                        color: 0x000000
                        r_mod: -4
                        value: 0
                - range_from: 1
                  range_to: 12
                  angle_range: 330
                  rotation: 300
                  ticks:
                    width: 1
                    count: 12
                    length: 1
                    major:
                      stride: 1
                      width: 4
                      length: 10
                      color: 0x000000
                      label_gap: 14
                - range_from: 0
                  range_to: 720
                  angle_range: 360
                  rotation: 270
                  ticks:
                    count: 0
                  indicators:
                    - line:
                        id: hour_hand
                        width: 5
                        color: 0x000000
                        r_mod: -50
                        value: 0
```

### Zeiger-Update Script
```yaml
# Quelle: ESPHome Cookbook Analog Clock (modifiziert)
script:
  - id: analog_time_update
    then:
      - lvgl.indicator.update:
          id: minute_hand
          value: !lambda 'return id(sntp_time).now().minute;'
      - lvgl.indicator.update:
          id: hour_hand
          value: !lambda |-
            auto now = id(sntp_time).now();
            return std::fmod(now.hour, 12) * 60 + now.minute;
```

### Select-Entity fuer Zifferblatt-Wechsel
```yaml
select:
  - platform: template
    name: "Zifferblatt"
    id: clock_face_select
    icon: mdi:clock-outline
    options:
      - "Digital"
      - "Analog"
    initial_option: "Digital"
    optimistic: true
    set_action:
      - if:
          condition:
            lambda: 'return x == "Analog";'
          then:
            - script.execute: analog_time_update
            - lvgl.page.show: analog_clock_page
          else:
            - lvgl.page.show: digital_clock_page
```

## State of the Art

| Alter Ansatz | Aktueller Ansatz | Seit wann | Auswirkung |
|--------------|------------------|-----------|------------|
| Canvas-Lambda fuer Uhren | LVGL Meter-Widget | ESPHome 2024.2+ | Kein manuelles Zeichnen noetig, deklarative YAML-Konfiguration |
| Display `show_page` | `lvgl.page.show:` | ESPHome LVGL-Integration | Native LVGL-Seitenverwaltung statt Display-Component |
| Hardcoded Farben | HA Select + Globals | Schon immer moeglich | Dynamische Konfiguration ueber HA |

**Deprecated/veraltet:**
- `display.show_page:` -- ersetzt durch `lvgl.page.show:` bei LVGL-basierten Displays
- Manuelles Canvas-Rendering fuer Uhren -- LVGL Meter-Widget ist die offizielle Loesung

## Open Questions

1. **Display-Groesse fuer Meter-Widget**
   - Was wir wissen: T-RGB 2.1 hat 480x480 Pixel rundes Display
   - Was unklar ist: Optimale Meter-Groesse (400px? 420px?) fuer gute Lesbarkeit der Stunden-Labels
   - Empfehlung: Mit 400px starten, visuell pruefen, ggf. anpassen

2. **Stunden-Labels: Meter auto-labels vs. manuelle Polar-Labels**
   - Was wir wissen: CONTEXT.md sagt "Polar-Koordinaten-Lambda", aber Meter-Widget bietet auto-Labels via `major.label_gap`
   - Was unklar ist: Ob die auto-Labels auf dem runden 480px Display gut aussehen
   - Empfehlung: Zuerst `major.label_gap` testen (einfacher); falls Positionierung nicht passt, 12 separate Labels mit sin/cos hinzufuegen

3. **Hintergrundfarb-Aenderung: Analog- und Digital-Seite**
   - Was wir wissen: CONTEXT.md spricht von "bg_color der Analog-Seite"
   - Was unklar ist: Ob die Farbe auch die Digital-Seite aendern soll
   - Empfehlung: Farb-Select aendert nur die Analog-Seite (CONTEXT.md Fokus); Digital bleibt bei Pink

## Validation Architecture

### Test Framework
| Eigenschaft | Wert |
|-------------|------|
| Framework | ESPHome Compile-Check + OTA-Flash |
| Config file | `alarm-clock.yaml` |
| Quick run command | `esphome compile alarm-clock.yaml` |
| Full suite command | `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml --device <IP>` |

### Phase Requirements -> Test Map
| Req ID | Verhalten | Test-Typ | Automatisierter Befehl | Datei existiert? |
|--------|-----------|----------|------------------------|-----------------|
| DISP-02 | Analoge Uhr mit Zeigern sichtbar | manual-only | Visuell auf Display pruefen | N/A -- Hardware-Verifikation |
| DISP-06 | Seitenwechsel via HA Select | manual-only | HA Select umschalten, Display pruefen | N/A -- HA + Display |

### Sampling Rate
- **Per task commit:** `esphome compile alarm-clock.yaml`
- **Per wave merge:** Compile + OTA-Flash + visuelle Verifikation
- **Phase gate:** Beide Zifferblaetter zeigen korrekte Zeit, Select wechselt zuverlaessig

### Wave 0 Gaps
Keine -- bestehende Infrastruktur (ESPHome compile, OTA) deckt alle Phase-Requirements ab. Tests sind hardware-basiert (visuell + HA-Interaktion), keine Software-Unit-Tests moeglich.

## Sources

### Primary (HIGH confidence)
- [ESPHome Cookbook LVGL - Analog Clock](https://github.com/esphome/esphome-docs/blob/current/src/content/docs/cookbook/lvgl.mdx) - Vollstaendiges Meter-Widget Beispiel mit 3 Skalen, Zeigern, Update-Script
- [ESPHome LVGL Documentation](https://esphome.io/components/lvgl/) - `lvgl.page.show:`, `lvgl.page.is_showing`, `lvgl.indicator.update:` Actions
- [ESPHome LVGL Widgets](https://esphome.io/components/lvgl/widgets/) - Meter-Widget Konfigurationsoptionen

### Secondary (MEDIUM confidence)
- [HA Community: ESPHome Elegant LVGL Clock](https://community.home-assistant.io/t/esphome-elegant-lvgl-clock/772365) - Praxis-Beispiel mit rundem Display, bestaetigt Meter-Pattern
- [clowrey/esphome-esp32-2424s012-lvgl-powermeter](https://github.com/clowrey/esphome-esp32-2424s012-lvgl-powermeter) - Analog-Clock auf rundem ESP32 Display

### Tertiary (LOW confidence)
- Keine -- alle Kernerkenntnisse sind durch offizielle Quellen abgedeckt

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH - Offizielles ESPHome-Cookbook liefert exaktes Beispiel
- Architecture: HIGH - Patterns (Select, page.show, Globals) bereits im Projekt etabliert
- Pitfalls: HIGH - Aus offizieller Dokumentation und bestehendem Projekt-Kontext abgeleitet

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stabile ESPHome LVGL API, aendert sich selten)
