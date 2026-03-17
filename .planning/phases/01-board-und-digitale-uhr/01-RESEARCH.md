# Phase 1: Board und Digitale Uhr - Research

**Researched:** 2026-03-17
**Domain:** ESPHome Board-Konfiguration, MIPI-RGB Display, LVGL Zeitanzeige, NTP-Synchronisation
**Confidence:** HIGH

## Summary

Phase 1 bringt das LilyGo T-RGB Board mit ESPHome zum Laufen und zeigt Uhrzeit, Datum und Wochentag auf dem runden 480x480 Display. Der Stack ist gut ausgereift: ESPHome bietet mit `mipi_rgb` ein vorkonfiguriertes Board-Modell (`T-RGB-2.1`), das alle Pin-Definitionen automatisch setzt. LVGL ist nativ integriert und bietet `time_format`-Labels, die sich automatisch aktualisieren -- kein manuelles Lambda-Polling noetig.

Die Hauptrisiken dieser Phase sind Hardware-Konfigurationsfehler: falsches Framework (muss ESP-IDF sein), fehlende PSRAM-Konfiguration (Pflicht fuer 480x480 Framebuffer), fehlender XL9535 I/O-Expander (ohne den das Display dunkel bleibt), und falscher Flash-Mode (muss DIO sein). Alle diese Fehler fuehren zu schwarzem Display oder Boot-Loops und sind durch korrekte YAML-Konfiguration von Anfang an vermeidbar.

**Primary recommendation:** Eine einzelne ESPHome YAML-Datei erstellen, die Board-Konfiguration (ESP-IDF, PSRAM, XL9535), Display (mipi_rgb T-RGB-2.1), LVGL (Label-Widgets mit time_format), NTP (SNTP mit Europe/Berlin), und Backlight (LEDC auf GPIO46) konfiguriert. Inkrementell vorgehen: erst Board booten lassen, dann Display aktivieren, dann LVGL-Labels hinzufuegen.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TIME-01 | Uhrzeit wird automatisch per NTP ueber WLAN synchronisiert (Zeitzone Europe/Berlin) | SNTP-Component mit `timezone: "Europe/Berlin"`, deutsche NTP-Server (0.de.pool.ntp.org), `is_valid()` Check vor Anzeige |
| DISP-01 | Nutzer sieht digitale Uhrzeit auf dem runden Display (LVGL Label) | LVGL Label-Widget mit `time_format: "%H:%M"` und expliziter Time-Source, automatisches Update |
| DISP-03 | Nutzer sieht Datum und Wochentag auf dem Display | Zweites LVGL Label mit `time_format: "%A, %d. %B %Y"` (strftime fuer Wochentag + Datum) |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ESPHome | 2026.2.x | Firmware-Framework | Native HA-Integration, deklarative YAML-Konfiguration, LVGL + mipi_rgb nativ integriert |
| ESP-IDF | 5.x (via ESPHome) | Build-Framework | Zwingend fuer mipi_rgb Display-Treiber, kein Arduino moeglich |
| LVGL | 8.x (via ESPHome) | UI-Rendering | Label-Widget mit time_format fuer Zeitanzeige, Montserrat-Fonts eingebaut |
| mipi_rgb | ESPHome built-in | ST7701S Display-Treiber | Vorkonfiguriertes Board-Modell T-RGB-2.1, ersetzt deprecated st7701s |
| SNTP | ESPHome built-in | NTP-Zeitsynchronisation | Automatische Zeitsync, TZ-Datenbank-Name Support |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| XL9535 | ESPHome built-in | I/O-Expander | Pflicht fuer T-RGB: LCD Reset, LCD Enable, Touch Reset |
| LEDC Output | ESPHome built-in | PWM fuer Backlight | GPIO46 Backlight-Steuerung |
| Monochromatic Light | ESPHome built-in | Backlight-Abstrahierung | Helligkeit 0-100% mit Transition |
| CST816 | ESPHome built-in | Touchscreen-Treiber | T-RGB 2.1" Full Circle (CST820 kompatibel) |
| WiFi | ESPHome built-in | WLAN-Verbindung | Pflicht fuer NTP und spaetere HA-Integration |
| API | ESPHome built-in | HA Native API | Vorbereitung fuer spaetere HA-Integration |
| OTA | ESPHome built-in | Over-the-Air Updates | Firmware-Updates ohne USB |
| Logger | ESPHome built-in | Serial/WiFi Logging | Debugging |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| mipi_rgb (T-RGB-2.1) | st7701s (deprecated) | st7701s funktioniert noch, wird aber in zukuenftigen ESPHome-Versionen entfernt |
| LVGL Labels | Custom display lambda | Kein Touch-Support, kein Widget-System, manuelles Rendering |
| SNTP | HA Time | HA-Abhaengigkeit fuer Grundfunktion, SNTP ist autark |

**Installation:**
```bash
pip install esphome
esphome compile alarm-clock.yaml
esphome upload alarm-clock.yaml
```

## Architecture Patterns

### Recommended Project Structure (Phase 1)
```
alarm-clock/
  alarm-clock.yaml          # Hauptdatei: alles in einer Datei fuer Phase 1
```

**Rationale:** In Phase 1 ist die Konfiguration noch ueberschaubar (~100 Zeilen). Package-Aufteilung erfolgt ab Phase 2 wenn Alarm-Logik und Audio hinzukommen.

### Pattern 1: LVGL Label mit time_format (automatisches Update)
**What:** LVGL Labels koennen direkt eine `time_format`-Property nutzen, die strftime-Formate akzeptiert und sich automatisch aktualisiert.
**When to use:** Immer wenn Zeit oder Datum angezeigt werden soll.
**Example:**
```yaml
# Source: https://esphome.io/components/lvgl/widgets/
lvgl:
  displays:
    - my_display
  touchscreens:
    - my_touchscreen
  buffer_size: 25%
  pages:
    - id: digital_clock_page
      widgets:
        # Uhrzeit gross in der Mitte
        - label:
            id: time_label
            align: CENTER
            text_font: montserrat_48
            text_color: 0xFFFFFF
            text:
              time_format: "%H:%M"
              time: sntp_time
        # Datum und Wochentag darunter
        - label:
            id: date_label
            align: CENTER
            y: 50
            text_font: montserrat_14
            text_color: 0xCCCCCC
            text:
              time_format: "%A, %d.%m.%Y"
              time: sntp_time
```

### Pattern 2: Board-Konfiguration mit Pflicht-Einstellungen
**What:** ESP32-S3 + ESP-IDF + PSRAM + DIO Flash-Mode als unveraenderliche Basis.
**When to use:** Immer fuer T-RGB Board.
**Example:**
```yaml
# Source: https://esphome.io/components/display/mipi_rgb/
esphome:
  name: alarm-clock
  friendly_name: "Wecker"
  platformio_options:
    board_build.flash_mode: dio  # Pflicht fuer T-RGB

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  flash_size: 16MB
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz
```

### Pattern 3: XL9535 vor Display deklarieren
**What:** Der I/O-Expander muss in der YAML vor dem Display konfiguriert sein, da Display-Reset und Display-Enable ueber XL9535-Pins laufen.
**When to use:** Immer fuer T-RGB.
**Example:**
```yaml
# Source: https://esphome.io/components/xl9535/
i2c:
  sda: GPIO8
  scl: GPIO48

xl9535:
  - id: xl9535_hub
    address: 0x20
```

### Pattern 4: SNTP mit Validitaetspruefung
**What:** NTP-Sync mit is_valid()-Check vor Nutzung der Zeit.
**When to use:** Immer bei zeitkritischen Funktionen.
**Example:**
```yaml
# Source: https://esphome.io/components/time/sntp/
time:
  - platform: sntp
    id: sntp_time
    timezone: "Europe/Berlin"
    servers:
      - 0.de.pool.ntp.org
      - 1.de.pool.ntp.org
      - 2.de.pool.ntp.org
    on_time_sync:
      then:
        - logger.log: "NTP-Zeit synchronisiert"
```

### Pattern 5: Display mit LVGL-Optimierungen
**What:** mipi_rgb mit auto_clear und update_interval fuer LVGL konfigurieren.
**Example:**
```yaml
# Source: https://esphome.io/components/display/mipi_rgb/
display:
  - platform: mipi_rgb
    model: T-RGB-2.1
    id: my_display
    auto_clear_enabled: false
    update_interval: never
    reset_pin:
      xl9535: xl9535_hub
      number: 6
      inverted: true
    enable_pin:
      xl9535: xl9535_hub
      number: 2
      inverted: true
```

### Anti-Patterns to Avoid

- **Arduino Framework verwenden:** mipi_rgb braucht ESP-IDF. Arduino = schwarzes Display.
- **PSRAM vergessen:** 480x480 Display braucht ~450KB Framebuffer. Ohne PSRAM: Crashes und Watchdog-Resets.
- **XL9535 vergessen:** Ohne Expander-Config bleiben LCD-Reset und LCD-Enable inaktiv = schwarzes Display.
- **Flash-Mode QIO statt DIO:** T-RGB braucht DIO. QIO = sporadische Crashes oder Boot-Fehler.
- **st7701s statt mipi_rgb:** Deprecated, wird in Zukunft entfernt.
- **buffer_size: 100% ohne Test:** Kann zu Instabilitaet fuehren, 25% ist sicherer Start.
- **display lambda statt LVGL:** Kein Touch-Support, kein Widget-System, unnoetig komplex.
- **NTP-Zeit ohne is_valid() nutzen:** Vor Sync zeigt die Uhr 01:00:00 (UTC+1 auf Epoch 1970).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Zeitanzeige auf Display | Custom lambda mit it.print() | LVGL Label mit time_format | Automatisches Update, Touch-kompatibel, Widget-basiert |
| Zeitsynchronisation | Manueller NTP-Client | ESPHome SNTP Component | Automatische Sync, Timezone-Support, is_valid() API |
| Display-Initialisierung | Manuelle ST7701S Init-Sequenz | mipi_rgb model: T-RGB-2.1 | Alle Pins und Init-Commands vorkonfiguriert |
| GPIO-Erweiterung | Manuelle I2C-Kommunikation | xl9535 Component | Native ESPHome-Integration, Pin-Referenzen in anderen Components |
| Backlight-Steuerung | Manuelles GPIO-Toggle | LEDC + Monochromatic Light | Dimming, Transitions, HA-Entity automatisch |

## Common Pitfalls

### Pitfall 1: Display bleibt schwarz (Framework falsch)
**What goes wrong:** Projekt kompiliert, aber Display zeigt nichts.
**Why it happens:** Arduino-Framework statt ESP-IDF. mipi_rgb braucht ESP-IDF.
**How to avoid:** `framework: type: esp-idf` ab Zeile 1 setzen.
**Warning signs:** Kompilierung erfolgreich, aber Display dunkel nach Flash.

### Pitfall 2: Boot-Loop / Guru Meditation (PSRAM fehlt)
**What goes wrong:** ESP32 startet immer wieder neu mit Watchdog-Reset.
**Why it happens:** 480x480x2 Bytes = ~450KB Framebuffer passt nicht in 512KB SRAM.
**How to avoid:** PSRAM mit `mode: octal` und `speed: 80MHz` konfigurieren. Flash-Mode `dio`.
**Warning signs:** Reboot-Loops in Serial-Log, "Guru Meditation Error".

### Pitfall 3: Display schwarz trotz korrekter Pins (XL9535 fehlt)
**What goes wrong:** Alle Display-Pins stimmen, aber nichts passiert.
**Why it happens:** LCD-Reset (XL9535 Pin 6, invertiert) und LCD-Enable (XL9535 Pin 2, invertiert) werden nie geschaltet.
**How to avoid:** XL9535 Component konfigurieren, Reset/Enable-Pins als xl9535-Pins referenzieren.
**Warning signs:** I2C-Scan findet Device an 0x20, aber Display bleibt dunkel.

### Pitfall 4: Uhr zeigt 01:00:00 (NTP noch nicht synchronisiert)
**What goes wrong:** Nach dem Boot zeigt die Uhr die falsche Zeit (Epoch + Timezone-Offset).
**Why it happens:** NTP-Sync braucht WLAN-Verbindung + DNS + NTP-Server-Antwort.
**How to avoid:** `on_time_sync` Trigger nutzen, vorher "Synchronisiere..." anzeigen oder leere Anzeige.
**Warning signs:** Uhr springt nach einigen Sekunden von 01:00 auf die korrekte Zeit.

### Pitfall 5: Timezone falsch / Sommerzeit stimmt nicht
**What goes wrong:** Uhrzeit stimmt im Winter, aber nicht im Sommer (oder umgekehrt).
**Why it happens:** POSIX-Timezone-String statt TZ-Datenbank-Name verwendet.
**How to avoid:** `timezone: "Europe/Berlin"` (TZ-Datenbank-Name, NICHT POSIX-String wie "CET-1CEST,M3.5.0,M10.5.0/3").
**Warning signs:** Uhrzeit 1 Stunde falsch nach Zeitumstellung.

### Pitfall 6: OTA schlaegt fehl (Partition zu klein)
**What goes wrong:** LVGL + WiFi sprengen die Standard-Partition.
**Why it happens:** Standard ESP32-Partition ist ~1.3MB, LVGL-Firmware kann groesser sein.
**How to avoid:** T-RGB hat 16MB Flash. Bei Bedarf Custom Partition Table oder `default_16MB.csv`.
**Warning signs:** Kompilierung zeigt "Firmware too large" oder OTA-Upload schlaegt fehl.

## Code Examples

### Komplette Phase-1 YAML-Konfiguration (Vorlage)

```yaml
# Source: Zusammengestellt aus offiziellen ESPHome-Docs
# https://esphome.io/components/display/mipi_rgb/
# https://esphome.io/components/lvgl/
# https://esphome.io/components/time/sntp/

esphome:
  name: alarm-clock
  friendly_name: "Wecker"
  platformio_options:
    board_build.flash_mode: dio

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  flash_size: 16MB
  framework:
    type: esp-idf

psram:
  mode: octal
  speed: 80MHz

logger:

api:
  encryption:
    key: !secret api_key

ota:
  - platform: esphome
    password: !secret ota_password

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "Wecker-Fallback"
    password: !secret fallback_password

i2c:
  sda: GPIO8
  scl: GPIO48

xl9535:
  - id: xl9535_hub
    address: 0x20

display:
  - platform: mipi_rgb
    model: T-RGB-2.1
    id: my_display
    auto_clear_enabled: false
    update_interval: never
    reset_pin:
      xl9535: xl9535_hub
      number: 6
      inverted: true
    enable_pin:
      xl9535: xl9535_hub
      number: 2
      inverted: true

touchscreen:
  - platform: cst816
    id: my_touchscreen
    interrupt_pin: GPIO1
    reset_pin:
      xl9535: xl9535_hub
      number: 1

output:
  - platform: ledc
    id: backlight_output
    pin: GPIO46
    frequency: 1000Hz

light:
  - platform: monochromatic
    output: backlight_output
    name: "Display Backlight"
    id: backlight
    default_transition_length: 0.5s
    restore_mode: ALWAYS_ON

time:
  - platform: sntp
    id: sntp_time
    timezone: "Europe/Berlin"
    servers:
      - 0.de.pool.ntp.org
      - 1.de.pool.ntp.org
      - 2.de.pool.ntp.org
    on_time_sync:
      then:
        - logger.log: "NTP-Zeit synchronisiert"

lvgl:
  displays:
    - my_display
  touchscreens:
    - my_touchscreen
  buffer_size: 25%
  pages:
    - id: digital_clock_page
      widgets:
        - label:
            id: time_label
            align: CENTER
            text_font: montserrat_48
            text_color: 0xFFFFFF
            text:
              time_format: "%H:%M"
              time: sntp_time
        - label:
            id: date_label
            align: CENTER
            y: 40
            text_font: montserrat_14
            text_color: 0xCCCCCC
            text:
              time_format: "%A, %d.%m.%Y"
              time: sntp_time
```

### strftime Format-Referenz fuer Uhr/Datum

```
%H   Stunde (24h, 00-23)
%M   Minute (00-59)
%S   Sekunde (00-59)
%d   Tag des Monats (01-31)
%m   Monat (01-12)
%Y   Jahr (4-stellig)
%A   Wochentag ausgeschrieben (Monday, Tuesday, ...)
%a   Wochentag abgekuerzt (Mon, Tue, ...)
%B   Monatsname ausgeschrieben (January, ...)
%b   Monatsname abgekuerzt (Jan, ...)
```

**Hinweis:** Wochentag- und Monatsnamen sind auf dem ESP32 standardmaessig englisch. Deutsche Lokalisierung ist auf dem ESP32 nicht trivial. Alternative: Wochentag per Lambda manuell uebersetzen oder abgekuerztes Format nutzen.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| st7701s Display-Treiber | mipi_rgb mit Board-Modellen | ESPHome 2024.x | Einfachere Config, vorkonfigurierte Pin-Mappings |
| display lambda fuer UI | LVGL nativ in ESPHome | ESPHome 2024.x | Widget-System, Touch-Support, Pages, time_format |
| Manuelle NTP-Konfiguration | SNTP mit TZ-Datenbank | Stabil seit ESPHome 2023 | Automatische DST-Umstellung |

**Deprecated/outdated:**
- `st7701s` Display-Treiber: Durch `mipi_rgb` ersetzt, wird in zukuenftigen Versionen entfernt
- `display: lambda:` fuer UI: Durch LVGL ersetzt, nur noch fuer einfachste Displays sinnvoll

## Open Questions

1. **Deutsche Wochentag-/Monatsnamen**
   - What we know: strftime auf ESP32 liefert englische Namen (Monday, January...)
   - What's unclear: Ob ESPHome/ESP-IDF Locale-Einstellungen unterstuetzt
   - Recommendation: Fuer Phase 1 englische Namen akzeptieren oder per Lambda-Mapping uebersetzen (z.B. "Mon" -> "Mo"). Kein Blocker.

2. **LVGL time_format automatisches Update-Intervall**
   - What we know: time_format-Labels aktualisieren sich automatisch basierend auf der Time-Source
   - What's unclear: Exaktes Update-Intervall (sekuendlich oder minuetlich?)
   - Recommendation: Testen. Falls nur minuetlich: Fuer "%H:%M" (ohne Sekunden) ist das ausreichend.

3. **Touch-Reset-Pin Invertierung**
   - What we know: LCD-Reset und LCD-Enable sind invertiert
   - What's unclear: Ob Touch-Reset-Pin (XL9535 Pin 1) auch invertiert sein muss
   - Recommendation: Erst ohne `inverted`, bei Problemen mit `inverted: true` testen.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | ESPHome compile + flash (keine Unit-Tests fuer YAML) |
| Config file | alarm-clock.yaml |
| Quick run command | `esphome compile alarm-clock.yaml` |
| Full suite command | `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TIME-01 | NTP-Sync und korrekte Zeitzone | manual + compile | `esphome compile alarm-clock.yaml` | Wave 0 |
| DISP-01 | Digitale Uhrzeit auf Display sichtbar | manual (visuell) | `esphome compile alarm-clock.yaml` | Wave 0 |
| DISP-03 | Datum und Wochentag auf Display sichtbar | manual (visuell) | `esphome compile alarm-clock.yaml` | Wave 0 |

### Sampling Rate
- **Per task commit:** `esphome compile alarm-clock.yaml`
- **Per wave merge:** Compile + Upload + visuelle Pruefung auf dem Board
- **Phase gate:** Board zeigt korrekte Uhrzeit, Datum, Wochentag; NTP-Sync im Log bestaetigt

### Wave 0 Gaps
- [ ] `alarm-clock.yaml` -- Hauptkonfigurationsdatei, existiert noch nicht
- [ ] `secrets.yaml` -- WiFi-Credentials und API-Keys
- [ ] ESPHome installiert und funktionsfaehig auf dem Entwicklungsrechner

**Hinweis:** ESPHome-Projekte werden durch `esphome compile` validiert (YAML-Syntax + Component-Kompatibilitaet). Echte Funktionstests erfordern Hardware (Flash + visuelle Pruefung). Unit-Tests sind in diesem Kontext nicht anwendbar.

## Sources

### Primary (HIGH confidence)
- [ESPHome MIPI RGB Display](https://esphome.io/components/display/mipi_rgb/) -- Board-Modell T-RGB-2.1, Pin-Konfiguration, ESP-IDF Requirement
- [ESPHome LVGL Graphics](https://esphome.io/components/lvgl/) -- Buffer-Size, Pages, Display/Touchscreen-Konfiguration
- [ESPHome LVGL Widgets](https://esphome.io/components/lvgl/widgets/) -- Label Widget, time_format Property, text/format Alternativen
- [ESPHome SNTP Time](https://esphome.io/components/time/sntp/) -- Server-Konfiguration, TZ-Datenbank-Name
- [ESPHome Time Component](https://esphome.io/components/time/) -- on_time Trigger, strftime, is_valid(), Lambda-API
- [ESPHome XL9535](https://esphome.io/components/xl9535/) -- Pin-Nummern (0-7, 10-17), I2C-Adresse, Konfiguration
- [ESPHome CST816](https://esphome.io/components/touchscreen/cst816/) -- Touch-Treiber fuer T-RGB 2.1" Full Circle

### Secondary (MEDIUM confidence)
- [ESPHome LVGL Cookbook](https://esphome.io/cookbook/lvgl/) -- Analog Clock Beispiel (fuer spaetere Phasen)
- [LilyGo T-RGB GitHub](https://github.com/Xinyuan-LilyGO/LilyGo-T-RGB) -- Hardware-Specs, GPIO-Belegung

### Tertiary (LOW confidence)
- [HA Community T-RGB Thread](https://community.home-assistant.io/t/lilygo-t-rgb-esp32-s3-2-1/948076) -- Community-Erfahrungen, nicht offiziell verifiziert

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Alle Components offiziell dokumentiert, vorkonfiguriertes Board-Modell
- Architecture: HIGH -- Standard ESPHome YAML-Pattern, LVGL time_format offiziell dokumentiert
- Pitfalls: HIGH -- Alle Pitfalls aus offizieller Doku und bekannten Hardware-Einschraenkungen abgeleitet
- Validation: MEDIUM -- Compile-Validierung moeglich, aber echte Tests erfordern Hardware

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stabiler Stack, keine schnellen Aenderungen erwartet)
