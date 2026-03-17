# Research Summary: ESP32 Smart Alarm Clock

**Domain:** ESPHome-basierter Wecker auf LilyGo T-RGB (ESP32-S3, rundes Touch-Display)
**Researched:** 2026-03-17
**Overall confidence:** MEDIUM

## Executive Summary

Der ESPHome-Stack fuer die LilyGo T-RGB ist 2026 gut ausgereift. Die aktuelle ESPHome-Version 2026.2.x bietet native Unterstuetzung fuer das Board ueber den `mipi_rgb`-Display-Treiber mit dem vorkonfigurierten Modell `T-RGB-2.1`. LVGL ist als UI-Framework nativ integriert und bietet ein Meter-Widget, das ideal fuer eine analoge Uhren-Darstellung auf dem runden Display geeignet ist. Die RTTTL-Komponente ermoeglicht Melodie-Wiedergabe ohne externes Dateisystem.

Die groesste technische Herausforderung ist der **extreme GPIO-Mangel** der T-RGB. Das Board nutzt praktisch alle verfuegbaren ESP32-S3 Pins fuer das 16-Bit-Parallel-RGB-Display, den XL9535 I/O-Expander und den I2C-Bus. Der Hersteller gibt an: "T-RGB has no free GPIO and cannot be expanded." Dies macht den Anschluss eines I2S-Lautsprechers (3 Pins) unmoeglich. Die einzig realistische Audio-Loesung ist ein passiver Piezo-Buzzer an einem einzelnen GPIO-Pin (z.B. GPIO0 nach Boot oder ein ungenutzter XL9535-Pin).

Die Home-Assistant-Integration ist unkompliziert: ESPHome Native API bietet automatische Entity-Erkennung. Ein Template-Switch fuer den Alarm-Status erlaubt HA-Automatisierungen (Feiertag-Deaktivierung). Die Alarm-Zeit kann ueber Number-Entities in HA konfiguriert werden, waehrend die Logik komplett auf dem ESP32 laeuft.

Das ESP-IDF Framework ist **zwingend erforderlich** -- Arduino unterstuetzt den MIPI-RGB-Treiber nicht. PSRAM (8MB octal) ist ebenfalls Pflicht fuer den Display-Framebuffer. Diese Entscheidungen sind nicht optional und muessen von Anfang an richtig gesetzt werden.

## Key Findings

**Stack:** ESPHome 2026.2.x + ESP-IDF + LVGL + mipi_rgb (T-RGB-2.1) + RTTTL mit LEDC-Output
**Architecture:** LVGL Pages (analog/digital), Script-basierte Alarm-Logik, Template-Switch fuer HA
**Critical Pitfall:** T-RGB hat keine freien GPIOs -- I2S-Audio unmoeglich, Buzzer-GPIO muss aus Schaltplan identifiziert werden

## Implications for Roadmap

Basierend auf der Recherche, empfohlene Phasenstruktur:

1. **Phase 0: Hardware-Validierung** - GPIO-Analyse und Buzzer-Machbarkeit
   - Adressiert: Kritischen GPIO-Mangel (Pitfall #1)
   - Vermeidet: Hardware-Bestellung ohne GPIO-Klaerung
   - Aufgaben: Schaltplan analysieren, freien GPIO identifizieren, Buzzer testen

2. **Phase 1: Board-Grundkonfiguration** - ESP-IDF, Display, Backlight
   - Adressiert: Display-Treiber (mipi_rgb), PSRAM, XL9535 Expander
   - Vermeidet: Framework-Fehler (Pitfall #2), PSRAM-Crashes (Pitfall #3)
   - Aufgaben: ESPHome YAML Grundgeruest, Display laeuft, Backlight steuerbar

3. **Phase 2: LVGL UI - Digitale Uhr** - Einfachste Uhranzeige
   - Adressiert: Kernfunktion Zeitanzeige, Touch-Grundlagen
   - Vermeidet: Komplexitaet der analogen Uhr zu frueh
   - Aufgaben: LVGL-Init, Label-Widget fuer Uhrzeit, NTP-Sync

4. **Phase 3: Alarm-Logik und Audio** - Wecker-Kernfunktion
   - Adressiert: RTTTL-Buzzer, Template-Switch, Mo-Fr Trigger
   - Vermeidet: RTTTL Speaker-Bug (Pitfall #4) durch LEDC-Output
   - Aufgaben: Alarm Ein/Aus, Zeitkonfiguration, Melodie-Wiedergabe, Snooze

5. **Phase 4: LVGL UI - Analoge Uhr** - Meter-Widget mit Zeigern
   - Adressiert: Analoge Uhren-Darstellung, Page-Navigation
   - Aufgaben: Meter-Widget mit 3 Skalen, Zeiger-Update-Script, Seitenwechsel

6. **Phase 5: HA-Integration und Polish** - Automatisierung, Nachtmodus
   - Adressiert: Feiertag-Deaktivierung, Dimming, Feinschliff
   - Aufgaben: HA-Automatisierung, Nachtmodus, Melodie-Auswahl

**Phase ordering rationale:**
- Phase 0 zuerst: Ohne geklaerten GPIO fuer Buzzer ist das Projekt blockiert
- Display vor Audio: Visuelles Feedback erleichtert Debugging
- Digital vor Analog: Proof-of-Concept mit niedrigerer Komplexitaet
- Alarm-Logik vor Analog-UI: Kernfunktion hat Prioritaet ueber aesthetische Features
- HA zuletzt: Funktioniert auch standalone, HA ist Enhancement

**Research flags for phases:**
- Phase 0: MUSS tiefer recherchiert werden (Schaltplan-Analyse, GPIO-Mapping)
- Phase 1: Standard-Patterns, Community-Beispiele vorhanden
- Phase 2: Standard LVGL, gut dokumentiert
- Phase 3: RTTTL Output-Modus gut dokumentiert, Alarm-Logik braucht Lambda
- Phase 4: LVGL Meter gut dokumentiert, Cookbook hat Analog-Clock-Beispiel
- Phase 5: Standard HA-Integration

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack (ESPHome/ESP-IDF) | HIGH | Offizielle Docs, vorkonfiguriertes Board-Modell T-RGB-2.1 |
| Display (mipi_rgb) | HIGH | Offiziell unterstuetzt, Community-validiert |
| LVGL UI | HIGH | Offizielle Docs, Cookbook mit Analog-Clock-Beispiel |
| Audio (RTTTL/Buzzer) | MEDIUM | RTTTL gut dokumentiert, aber GPIO-Verfuegbarkeit unklar |
| GPIO-Situation | LOW | Hersteller sagt "no free GPIO", Schaltplan nicht analysiert |
| Touch (cst816) | HIGH | Offiziell unterstuetzt, Board-Version bestimmt Treiber |
| HA-Integration | HIGH | Standard ESPHome Native API |

## Gaps to Address

- **GPIO-Analyse (kritisch):** Schaltplan der T-RGB muss vor Projektstart analysiert werden. Welcher GPIO ist fuer Buzzer nutzbar? Ist GPIO0 (Boot) nach dem Booten verfuegbar? Hat der XL9535 ungenutzte Pins?
- **Physische Taste:** Welcher GPIO? Wie mit Snooze-Funktion verbinden?
- **LVGL Analog Clock:** Das Cookbook-Beispiel sollte vor Phase 4 im Detail studiert werden.
- **RTTTL Endlosschleife:** Script-basierte Wiederholung muss getestet werden (play -> wait -> play).
- **Alternative Hardware:** Falls GPIO-Situation aussichtslos: LilyGo T-Circle-S3 (hat eingebauten Speaker) als Backup evaluieren.
