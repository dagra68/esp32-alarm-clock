# Technology Stack

**Project:** ESP32 Smart Alarm Clock
**Researched:** 2026-03-17

## Recommended Stack

### Core Platform

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| ESPHome | 2026.2.x | Firmware-Framework | Native Home Assistant Integration, deklarative YAML-Konfiguration, LVGL-Support, RTTTL-Support. Aktuellste stabile Version mit Performance-Verbesserungen (36% schnellere Builds, 50% weniger RAM). | HIGH |
| ESP-IDF | 5.x (via ESPHome) | Build-Framework | Zwingend erforderlich fuer den ST7701S/MIPI-RGB Display-Treiber und PSRAM-Support. Arduino-Framework ist NICHT kompatibel mit dem RGB-Parallel-Display. | HIGH |
| Home Assistant | 2026.x | Smart Home Hub | Alarm-Automatisierung (Feiertag-Erkennung), Switch-Steuerung, Dashboard. Kommunikation ueber ESPHome Native API. | HIGH |

### Display

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| `mipi_rgb` Display-Treiber | ESPHome built-in | ST7701S Ansteuerung | Offizieller Nachfolger des deprecated `st7701s`-Treibers. Unterstuetzt T-RGB-2.1 und T-RGB-2.8 als vorkonfigurierte Board-Modelle. 16-Bit RGB565 Parallel-Interface. | HIGH |
| LVGL | ESPHome built-in (LVGL 8.x) | UI-Rendering | Meter-Widget fuer analoge Uhr (Zeiger als needle indicators), Label-Widget fuer digitale Uhr, Page-System fuer Umschaltung analog/digital. Nativ in ESPHome integriert seit 2024. | HIGH |
| XL9535 I/O Expander | ESPHome built-in | GPIO-Erweiterung | Die T-RGB nutzt den XL9535 (I2C, Adresse 0x20) fuer Display-Reset, LCD-Enable und Touchscreen-Reset. Ohne diesen Expander funktioniert das Board nicht. | HIGH |

### Touchscreen

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| `cst816` Touchscreen-Treiber | ESPHome built-in | Touch-Eingabe | T-RGB 2.1" Full Circle nutzt CST820 (kompatibel mit cst816-Treiber). T-RGB 2.8" nutzt GT911 (separater Treiber `gt911`). Board-Version bestimmt den Treiber. | HIGH |

### Audio

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| LEDC PWM Output | ESPHome built-in | Passiver Buzzer | **KRITISCH:** Die T-RGB hat keine freien GPIOs fuer I2S (braucht 3 Pins: BCLK, LRCLK, DOUT). Es gibt nur 2 freie GPIOs. Ein passiver Piezo-Buzzer braucht nur 1 GPIO-Pin mit LEDC PWM. | HIGH |
| RTTTL Buzzer | ESPHome built-in | Melodie-Wiedergabe | Spielt monophone Melodien im RTTTL-Format. Nutzt den LEDC-Output als `output`-Parameter (NICHT `speaker`). Kein Dateisystem noetig. | HIGH |

### Zeitsteuerung

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| SNTP Time | ESPHome built-in | NTP-Zeitsynchronisation | Automatische Zeitsync ueber WLAN. Timezone als TZ-Datenbank-Name (z.B. `Europe/Berlin`). Update-Intervall 15min default. | HIGH |
| `time` Component | ESPHome built-in | Zeitbasierte Automationen | `on_time`-Trigger fuer Alarm-Ausloesung zu konfigurierten Zeiten. Unterstuetzt Cron-Syntax. | HIGH |

### Home Assistant Integration

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| ESPHome Native API | ESPHome built-in | HA-Kommunikation | Direkte Integration ohne MQTT. Verschluesselung mit API-Key. Automatische Entity-Erkennung in HA. | HIGH |
| `switch` Component | ESPHome built-in | Alarm Ein/Aus | Exponiert Alarm-Status als Switch-Entity in HA. HA-Automatisierungen koennen den Switch steuern (Feiertage). | HIGH |
| `number` Component | ESPHome built-in | Alarm-Uhrzeit | Stunden und Minuten als Number-Entities in HA steuerbar. Alternative: `time` Entity (falls verfuegbar). | MEDIUM |

## Kritische Hardware-Einschraenkung: GPIO-Mangel

**Die T-RGB hat KEINE freien GPIOs im Standardzustand.**

Alle ESP32-S3 Pins werden vom Display (16 RGB-Datenpins + Steuerpins), I2C-Bus (GPIO 8 SDA, GPIO 48 SCL), und internen Funktionen belegt. Der XL9535 I/O-Expander steuert Display-Reset, LCD-Enable und Touch-Reset.

**Grove-Port:** GPIO 8 (SDA) und GPIO 48 (SCL) -- geteilt mit Touch-Controller. Kann fuer I2C-Geraete genutzt werden, aber NICHT fuer I2S oder PWM.

**Konsequenz fuer Audio:**
- I2S-Lautsprecher (3 Pins) ist NICHT moeglich ohne Hardware-Modifikation
- Ein passiver Piezo-Buzzer an 1 GPIO ist die einzig realistische Option
- GPIO muss durch Analyse des Schaltplans identifiziert werden (moeglicherweise GPIO 0 oder ein Pin der Boot-Taste)
- **Fallback:** I2C-basierter Audio-Chip ueber Grove-Port (z.B. I2C-Buzzer-Modul)

## Board-Konfiguration: LilyGo T-RGB 2.1" Full Circle

```yaml
esphome:
  name: alarm-clock
  friendly_name: "Wecker"
  platformio_options:
    board_build.flash_mode: dio  # Kritisch fuer T-RGB!

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  flash_size: 16MB
  framework:
    type: esp-idf  # Pflicht fuer mipi_rgb Display-Treiber

psram:
  mode: octal
  speed: 80MHz  # PSRAM ist Pflicht fuer Display-Buffer
```

### I2C und XL9535 Expander

```yaml
i2c:
  sda: GPIO8
  scl: GPIO48

xl9535:
  - id: xl9535_hub
    address: 0x20
```

### Display (MIPI RGB mit ST7701S)

```yaml
display:
  - platform: mipi_rgb
    model: T-RGB-2.1  # Vorkonfiguriertes Board-Modell!
    id: my_display
    auto_clear_enabled: false  # Pflicht fuer LVGL
    update_interval: never     # LVGL uebernimmt Rendering
    reset_pin:
      xl9535: xl9535_hub
      number: 6
      inverted: true
    enable_pin:
      xl9535: xl9535_hub
      number: 2
      inverted: true
```

### Backlight

```yaml
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
```

### Touchscreen (CST820 via cst816-Treiber)

```yaml
touchscreen:
  - platform: cst816
    id: my_touchscreen
    interrupt_pin: GPIO1
    reset_pin:
      xl9535: xl9535_hub
      number: 1
```

### LVGL Grundkonfiguration

```yaml
lvgl:
  displays:
    - my_display
  touchscreens:
    - my_touchscreen
  buffer_size: 25%  # Ohne PSRAM waere weniger noetig, mit PSRAM kann 100%
  pages:
    - id: analog_clock_page
      widgets:
        - meter:
            # Analoge Uhr mit 3 Skalen (Minuten, Stunden, Stunden-Fein)
            # Siehe ARCHITECTURE.md fuer Details
    - id: digital_clock_page
      widgets:
        - label:
            # Digitale Uhrzeitanzeige
```

### NTP-Zeit

```yaml
time:
  - platform: sntp
    id: sntp_time
    timezone: "Europe/Berlin"
    servers:
      - 0.de.pool.ntp.org
      - 1.de.pool.ntp.org
      - 2.de.pool.ntp.org
```

### Audio (Passiver Buzzer)

```yaml
output:
  - platform: ledc
    id: buzzer_output
    pin: GPIOXX  # Muss aus Schaltplan ermittelt werden!

rtttl:
  output: buzzer_output
  id: alarm_buzzer
  gain: 80%
  on_finished_playback:
    - logger.log: "Melodie beendet"
```

### Home Assistant Switch

```yaml
switch:
  - platform: template
    name: "Wecker Alarm"
    id: alarm_enabled
    optimistic: true
    restore_mode: RESTORE_DEFAULT_ON
```

## Alternativen (bewertet und verworfen)

| Kategorie | Empfohlen | Alternative | Warum nicht |
|-----------|-----------|-------------|-------------|
| Framework | ESP-IDF | Arduino | Arduino unterstuetzt kein MIPI-RGB-Display auf ESP32-S3. Nicht optional. |
| Display-Treiber | `mipi_rgb` (T-RGB-2.1) | `st7701s` (deprecated) | Deprecated, wird in zukuenftigen ESPHome-Versionen entfernt. `mipi_rgb` ist der offizielle Nachfolger. |
| Audio | LEDC PWM + passiver Buzzer | I2S + Lautsprecher | T-RGB hat nicht genug freie GPIOs (braucht 3, hat max 2). Zudem bekannter Bug: RTTTL spielt mit Speaker nur einmal ab (Issue #10312). |
| Audio | LEDC PWM + passiver Buzzer | I2C Audio-Modul | Zusaetzliche Hardware, komplexer, langsamer. Buzzer ist fuer RTTTL-Melodien voellig ausreichend. |
| UI-Framework | LVGL (ESPHome-nativ) | Custom Lambda mit TFT_eSPI | TFT_eSPI unterstuetzt ST7701S nicht nativ. LVGL hat Meter-Widget fuer analoge Uhr. Kein Grund fuer Custom-Code. |
| UI-Framework | LVGL (ESPHome-nativ) | Custom Lambda mit LovyanGFX | Unnoetige Komplexitaet. ESPHome LVGL deckt alle Anforderungen ab (Uhr, Touch, Pages). |
| Zeitsync | SNTP (NTP) | RTC-Modul (DS3231) | Explizit Out-of-Scope. NTP genuegt bei stabiler WLAN-Verbindung. Kein Batterie-Backup noetig. |
| HA-Protokoll | Native API | MQTT | Native API ist einfacher, schneller, automatische Entity-Erkennung. MQTT nur bei Nicht-HA-Systemen noetig. |
| Touch-Treiber (2.1") | `cst816` | `ft5x06` | CST820 ist der verbaute Chip (2.1" Full Circle). FT3267 nur bei Half-Circle-Version. |

## Board-Versionen und Touch-Controller

| T-RGB Version | Display | Touch-Controller | ESPHome Touch-Treiber |
|---------------|---------|------------------|-----------------------|
| 2.1" Half Circle | ST7701S | FT3267 | `ft5x06` |
| 2.1" Full Circle | ST7701S | CST820 | `cst816` |
| 2.8" Full Circle | ST7701S | GT911 | `gt911` |

**Empfehlung:** Die 2.1" Full Circle Version waehlen. CST820/cst816-Treiber ist gut unterstuetzt und stabil.

## Installation

```bash
# ESPHome installieren (falls noch nicht vorhanden)
pip install esphome

# Projekt kompilieren und flashen
esphome compile alarm-clock.yaml
esphome upload alarm-clock.yaml

# Alternativ ueber Home Assistant ESPHome Add-on
# Dashboard -> + -> Neues Geraet -> YAML einfuegen
```

## Offene Fragen (muessen vor Phase 1 geklaert werden)

1. **GPIO fuer Buzzer:** Welcher Pin ist tatsaechlich frei? Schaltplan muss analysiert werden. Moeglicherweise ist die physische Taste an einem GPIO, der dual genutzt werden kann, oder es gibt einen ungenutzten Pin am XL9535.
2. **Physische Taste:** Welcher GPIO? Boot-Button (GPIO0) koennte genutzt werden, aber Vorsicht bei Flash-Modus.
3. **LVGL Buffer-Groesse:** Mit 8MB PSRAM sollte 100% moeglich sein, aber Stabilitaet muss getestet werden.
4. **RTTTL Lautstaerke:** Passiver Buzzer ist leise. Ggf. NPN-Transistor als Verstaerker noetig (Hardware-Modifikation).

## Quellen

- ESPHome MIPI RGB Display: https://esphome.io/components/display/mipi_rgb/
- ESPHome ST7701S (deprecated): https://esphome.io/components/display/st7701s/
- ESPHome LVGL: https://esphome.io/components/lvgl/
- ESPHome LVGL Widgets: https://esphome.io/components/lvgl/widgets/
- ESPHome LVGL Cookbook: https://esphome.io/cookbook/lvgl/
- ESPHome RTTTL: https://esphome.io/components/rtttl/
- ESPHome I2S Speaker: https://esphome.io/components/speaker/i2s_audio/
- ESPHome CST816: https://esphome.io/components/touchscreen/cst816/
- ESPHome SNTP: https://esphome.io/components/time/sntp/
- ESPHome XL9535: https://www.esphome.io/components/xl9535/
- ESPHome LEDC Output: https://esphome.io/components/output/ledc/
- ESPHome Changelog 2026.2.0: https://esphome.io/changelog/2026.2.0/
- LilyGo T-RGB GitHub: https://github.com/Xinyuan-LilyGO/LilyGo-T-RGB
- LilyGo T-RGB Produkt: https://lilygo.cc/products/t-rgb
- HA Community T-RGB Thread: https://community.home-assistant.io/t/lilygo-t-rgb-esp32-s3-2-1/948076
- RTTTL Bug mit Speaker: https://github.com/esphome/esphome/issues/10312
