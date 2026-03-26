# Requirements: ESP32 Smart Alarm Clock

**Defined:** 2026-03-17
**Core Value:** Der Wecker weckt zuverlaessig an Wochentagen und laesst sich ueber Home Assistant automatisch an Feiertagen stumm schalten.

## v1 Requirements

### Zeit & Display

- [x] **TIME-01**: Uhrzeit wird automatisch per NTP ueber WLAN synchronisiert (Zeitzone Europe/Berlin)
- [x] **DISP-01**: Nutzer sieht digitale Uhrzeit auf dem runden Display (LVGL Label)
- [x] **DISP-02**: Nutzer sieht analoge Uhr mit Stunden- und Minutenzeiger (LVGL Meter-Widget) -- kein Sekundenzeiger per User-Entscheidung
- [x] **DISP-03**: Nutzer sieht Datum und Wochentag auf dem Display
- [x] **DISP-04**: Nutzer sieht wann der naechste Alarm ausgeloest wird
- [x] **DISP-05**: Nutzer sieht auf dem Display ob der Alarm aktiviert oder deaktiviert ist
- [x] **DISP-06**: Nutzer kann per HA-Select zwischen analogem und digitalem Zifferblatt wechseln -- per User-Entscheidung HA-Select statt Touch

### Alarm

- [x] **ALRM-01**: Nutzer kann eine Alarmzeit (Stunde + Minute) fuer Mo-Fr konfigurieren
- [x] **ALRM-02**: Nutzer kann die Alarmzeit direkt am Touch-Display einstellen
- [x] **ALRM-03**: Alarm loest Mo-Fr zur konfigurierten Zeit eine RTTTL-Melodie aus (Piezo-Buzzer via LEDC PWM)
- [x] **ALRM-04**: Nutzer kann den Alarm per Touch-Button dauerhaft ausschalten
- [x] **ALRM-05**: Nutzer kann per physischer Taste 5 Minuten Snooze ausloesen
- [x] **ALRM-06**: Nutzer kann den Alarm per Toggle aktivieren und deaktivieren

### Home Assistant Integration

- [ ] **HA-01**: Alarm Ein/Aus-Status ist als Switch-Entity in Home Assistant verfuegbar
- [ ] **HA-02**: Home Assistant kann den Alarm automatisch deaktivieren (z. B. via Feiertags-Automatisierung)
- [ ] **HA-03**: Alarmzeit (Stunde + Minute) ist ueber Number-Entities in HA einstellbar
- [ ] **HA-04**: Melodie-Auswahl ist als Select-Entity in HA verfuegbar (mind. 3 RTTTL-Melodien)
- [ ] **HA-05**: Display-Helligkeit ist als Slider in HA steuerbar

### Bedienung & Display

- [ ] **CTRL-01**: Nutzer kann Display-Helligkeit manuell dimmen (per Touch oder HA)

## v2 Requirements

### Erweiterte Funktionen

- **UX-01**: Zeitbasierter Nachtmodus (automatisches Dimmen z. B. 22:00-06:00)
- **UX-02**: Mehrere RTTTL-Melodien ueber Touch waehlbar (nicht nur per HA)
- **DISP-07**: Animierter Sekundenzeiger mit glattem Sweep (statt 1s-Sprung)

## Out of Scope

| Feature | Grund |
|---------|-------|
| Wochenend-Alarm | Explizit nicht gewuenscht -- nur Mo-Fr |
| Mehrere Alarme | Erhoehte UI-Komplexitaet auf kleinem Display |
| I2S-Lautsprecher / MP3 | T-RGB hat keine freien GPIOs -- Piezo-Buzzer ist die einzige Option |
| RTC-Modul (DS3231) | NTP genuegt, kein Batterie-Backup noetig, kein freier GPIO |
| Web-Interface | HA + Touch ersetzt das vollstaendig |
| Swipe-Gesten | ESPHome Swipe-Erkennung nicht robust (Feature-Request #3059 offen) |
| Wetter-Anzeige | Scope-Creep -- reiner Wecker |
| Arduino/PlatformIO | Ausschliesslich ESPHome -- ESP-IDF ist Pflicht fuer mipi_rgb |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TIME-01 | Phase 1 | Complete |
| DISP-01 | Phase 1 | Complete |
| DISP-02 | Phase 4 | Complete |
| DISP-03 | Phase 1 | Complete |
| DISP-04 | Phase 2 | Complete |
| DISP-05 | Phase 2 | Complete |
| DISP-06 | Phase 4 | Complete |
| ALRM-01 | Phase 2 | Complete |
| ALRM-02 | Phase 2 | Complete |
| ALRM-03 | Phase 2 | Complete |
| ALRM-04 | Phase 2 | Complete |
| ALRM-05 | Phase 2 | Complete |
| ALRM-06 | Phase 2 | Complete |
| HA-01 | Phase 3 | Pending |
| HA-02 | Phase 3 | Pending |
| HA-03 | Phase 3 | Pending |
| HA-04 | Phase 3 | Pending |
| HA-05 | Phase 3 | Pending |
| CTRL-01 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-03-17*
*Last updated: 2026-03-17 after roadmap creation*
