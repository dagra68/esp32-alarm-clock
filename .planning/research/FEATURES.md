# Feature Landscape

**Domain:** ESPHome-basierter Wecker auf LilyGo T-RGB
**Researched:** 2026-03-17 (Stack-Research Update)

## Table Stakes

Features, die Nutzer erwarten. Fehlen = Produkt fuehlt sich unfertig an.

| Feature | Warum erwartet | Komplexitaet | Notizen |
|---------|----------------|--------------|---------|
| Uhrzeitanzeige (digital) | Grundfunktion eines Weckers | Niedrig | LVGL Label-Widget, SNTP-Sync |
| Uhrzeitanzeige (analog) | Rundes Display schreit nach analoger Uhr | Mittel | LVGL Meter-Widget mit 3 Skalen (Stunden, Minuten, Stunden-Fein 0-720); ESPHome Cookbook hat fertiges Beispiel |
| NTP-Zeitsynchronisation | Kein manuelles Stellen noetig | Niedrig | SNTP-Component + HA-Time als Fallback, Europe/Berlin Timezone |
| Wochentag-Alarm (Mo-Fr) | Kernfunktion Wecker | Mittel | `time.on_time` mit Lambda-Check oder Template Datetime `on_time` |
| Alarm-Melodie (RTTTL) | Akustisches Wecksignal | Niedrig | RTTTL-Component mit LEDC PWM Output (NICHT Speaker -- siehe Pitfalls) |
| Snooze-Taste (physisch) | Klassisches Wecker-UX | Niedrig | GPIO Binary Sensor + 5min Script-Delay |
| Alarm aus per Touch | Touchscreen muss nutzbar sein | Niedrig | LVGL Button-Widget auf Top-Layer |
| HA-Integration (Switch) | Fernsteuerung / Automatisierung | Niedrig | Template Switch + ESPHome Native API |
| Display-Hintergrundbeleuchtung | Sichtbarkeit, Nachtmodus | Niedrig | LEDC-Monochromatic-Light an GPIO46 |
| Alarm Ein/Aus Switch | Ohne Ein/Aus-Schalter kein Wecker | Niedrig | Template Switch, restore_mode: RESTORE_DEFAULT_ON |

## Differentiators

Features, die das Produkt besonders machen. Nicht erwartet, aber geschaetzt.

| Feature | Wertversprechen | Komplexitaet | Notizen |
|---------|-----------------|--------------|---------|
| Feiertag-Auto-Stummschaltung | Kein manuelles Deaktivieren an Feiertagen | Niedrig (HA-Seite) | HA-Automatisierung deaktiviert Switch. Kalender-Integration in HA. |
| Wechsel analog/digital per Touch | Nutzerfreiheit, schoene Interaktion | Mittel | LVGL Page-Navigation; page_wrap fuer zyklisches Blaettern |
| Nachtmodus (dimmen/aus) | Kein Licht im Schlafzimmer | Niedrig | Zeitbasiertes Dimmen der Hintergrundbeleuchtung ueber LEDC |
| Naechster-Alarm-Anzeige | Nutzer sieht, wann der naechste Alarm ist | Mittel | Label-Widget zeigt berechnete Zeit |
| Melodie-Auswahl in HA | Verschiedene Weck-Melodien | Mittel | Select-Entity in HA, RTTTL-Strings als Optionen |
| Animierter Sekundenzeiger | Visuell ansprechend | Niedrig | LVGL Meter Indicator-Line, Update per 1s Interval |
| Datums-/Wochentag-Anzeige | Nuetzliche Zusatzinfo | Niedrig | LVGL Label mit strftime Format |
| Status-Anzeige (Alarm an/aus) | Nutzer sieht Alarm-Status auf einen Blick | Niedrig | LVGL Label oder Icon |

## Anti-Features

Features, die explizit NICHT gebaut werden.

| Anti-Feature | Warum vermeiden | Was stattdessen tun |
|--------------|-----------------|---------------------|
| Wochenend-Alarm | Explizit nicht gewuenscht laut Anforderung | Mo-Fr Alarm genuegt |
| MP3/WAV-Wiedergabe | Braucht Dateisystem, SD-Karte, mehr Speicher. T-RGB hat keine freien GPIOs fuer I2S-Lautsprecher (3 Pins noetig, max 1-2 frei). | RTTTL-Melodien mit Piezo-Buzzer |
| I2S-Lautsprecher | T-RGB hat "no free GPIO" laut Hersteller. I2S braucht 3 GPIOs (BCLK, LRCLK, DOUT). Zusaetzlich: bekannter RTTTL+Speaker Bug (nur einmal abspielen). | Passiver Piezo-Buzzer mit LEDC PWM an 1 GPIO |
| Web-Interface | Unnoetige Komplexitaet, HA + Touch ersetzt das | ESPHome Native API + HA Dashboard |
| RTC-Modul (DS3231) | Kein Batterie-Backup noetig, kein freier GPIO/I2C | NTP ueber WLAN + HA-Time Fallback |
| Komplexe Touch-Gesten | Swipe-Erkennung in ESPHome ist noch nicht robust (Feature-Request #3059) | Einfache Taps und Buttons |
| Wetter-Anzeige | Scope-Creep | Reiner Wecker |
| Mehrere Alarme | Erhoehte UI-Komplexitaet auf kleinem Display | 1 Alarm Mo-Fr genuegt |

## Feature-Abhaengigkeiten

```
NTP-Zeitsync -> Uhrzeitanzeige (analog + digital)
NTP-Zeitsync -> Wochentag-Alarm
Display-Treiber (mipi_rgb) -> LVGL UI -> Uhrzeitanzeige
Display-Treiber (mipi_rgb) -> LVGL UI -> Touch-Bedienung
Touch-Treiber (cst816/gt911) -> LVGL UI -> Touch-Bedienung
LEDC-Output -> RTTTL-Buzzer -> Alarm-Melodie
Template-Switch -> HA-Integration -> Feiertag-Automatisierung
Wochentag-Alarm -> Snooze-Funktion
XL9535 Expander -> Display-Treiber (Reset/Enable)
XL9535 Expander -> Touch-Treiber (Reset)
I2C Bus -> XL9535 Expander
I2C Bus -> Touch-Controller
```

## MVP-Empfehlung

Priorisieren:
1. **Display + LVGL (digital)** -- Ohne Display kein Wecker. Digitale Uhr zuerst (einfacher).
2. **NTP-Zeitsync** -- Grundlage fuer alles Zeitbasierte.
3. **RTTTL-Alarm mit Mo-Fr Trigger** -- Kernfunktion. Passiver Buzzer mit LEDC.
4. **HA-Switch** -- Fernsteuerung und Feiertag-Automatisierung.
5. **Touch: Alarm aus** -- Mindest-Interaktion.
6. **Snooze (physische Taste)** -- Essentielles Wecker-UX.

Aufschieben:
- **Analoge Uhr:** Komplexer (Meter-Widget, 3 Skalen). Digital zuerst als Proof-of-Concept.
- **Analog/Digital-Wechsel:** Erst wenn beide Zifferblaetter funktionieren.
- **Melodie-Auswahl:** Nice-to-have, eine Melodie genuegt fuer MVP.
- **Nachtmodus:** Einfach nachzuruesten, aber nicht MVP-kritisch.
- **Alarmzeit per Touch einstellen:** Anfangs ueber HA konfigurieren.

## Quellen

- ESPHome LVGL Meter (Analog Clock): https://esphome.io/cookbook/lvgl/
- ESPHome RTTTL: https://esphome.io/components/rtttl/
- LilyGo T-RGB "no free GPIO": https://github.com/Xinyuan-LilyGO/LilyGo-T-RGB
- RTTTL Speaker Bug: https://github.com/esphome/esphome/issues/10312
- Swipe-Gesten Feature Request: https://github.com/esphome/feature-requests/issues/3059
- Projektanforderungen: C:/Users/Daniel/.planning/PROJECT.md
