# Domain Pitfalls

**Domain:** ESPHome Alarm Clock auf LilyGo T-RGB (ESP32-S3, rundes Display, Piezo Audio, HA-Integration)
**Researched:** 2026-03-17 (Stack-Research Update)
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: T-RGB hat KEINE freien GPIOs -- Audio/Speaker-Anschluss blockiert

**What goes wrong:**
Die T-RGB hat laut Hersteller "no free GPIO and cannot be expanded". Alle ESP32-S3 Pins sind fuer Display (16 RGB-Daten + Steuerpins), I2C-Bus (GPIO 8/48), und interne Funktionen belegt. I2S-Lautsprecher (3 Pins) ist physisch unmoeglich.

**Why it happens:**
Das Board ist als reines Display-Modul konzipiert. Der ESP32-S3R8 hat 45 GPIOs, aber das 16-Bit-Parallel-RGB-Interface allein verbraucht ~20 Pins. Ein XL9535 I/O-Expander wird genutzt, um die restlichen Steuersignale zu bedienen.

**Consequences:**
Kein I2S-Audio moeglich. Ohne Buzzer ist das Geraet kein Wecker. Projekt-Blocker.

**Prevention:**
1. **VOR Hardware-Bestellung:** Schaltplan der T-RGB analysieren und freien GPIO identifizieren
2. GPIO0 (Boot-Button) nach dem Booten als normalen GPIO nutzen -- moeglicherweise fuer Buzzer
3. Ungenutzte XL9535-Pins pruefen (0-7, 10-17) -- XL9535 kann KEIN PWM, aber moeglicherweise Ein/Aus-Buzzer
4. Passiver Piezo-Buzzer an einem einzigen LEDC-GPIO (braucht echten ESP32-GPIO, kein XL9535)
5. **Fallback:** LilyGo T-Circle-S3 (hat eingebauten Speaker) als Alternative evaluieren

**Detection:** Tritt sofort bei Hardwareplanung auf. VOR Bestellung klaeren.

---

### Pitfall 2: Falsches Framework (Arduino statt ESP-IDF)

**What goes wrong:**
Projekt kompiliert, aber Display bleibt schwarz oder zeigt Artefakte.

**Why it happens:**
`mipi_rgb`-Treiber erfordert ESP-IDF. Arduino hat keinen nativen Support fuer 16-Bit-Parallel-RGB.

**Consequences:**
Komplett-Umbau der YAML-Konfiguration.

**Prevention:**
Ab Tag 1 `framework: type: esp-idf` setzen. Niemals Arduino fuer T-RGB.

**Detection:** Display bleibt schwarz beim ersten Boot.

---

### Pitfall 3: PSRAM nicht korrekt konfiguriert

**What goes wrong:**
Crashes beim LVGL-Init, partielles Bild, Watchdog-Resets.

**Why it happens:**
480x480 Display braucht ~450KB Framebuffer. Ohne PSRAM hat ESP32-S3 nur 512KB SRAM.

**Consequences:**
Random Crashes, Watchdog-Resets, Netzwerkprobleme.

**Prevention:**
```yaml
psram:
  mode: octal
  speed: 80MHz
esphome:
  platformio_options:
    board_build.flash_mode: dio  # Pflicht fuer T-RGB
```

**Detection:** Reboot-Loops, Guru Meditation Errors.

---

### Pitfall 4: RTTTL spielt mit Speaker-Component nur einmal ab

**What goes wrong:**
Erster Alarm funktioniert, alle weiteren bleiben stumm.

**Why it happens:**
Bekannter Bug (GitHub Issue #10312): RTTTL erreicht nie STATE_STOPPED bei Verwendung mit Speaker-Component. Fix in PR #10381 (merged August 2025), aber nur in ESPHome >= 2025.9.0.

**Consequences:**
Wecker funktioniert nur am ersten Tag.

**Prevention:**
RTTTL mit `output` (LEDC PWM) statt `speaker` verwenden. Output-Modus hat diesen Bug nicht. Zusaetzlich: Ist ohnehin die einzige Option auf T-RGB (kein I2S moeglich).

**Detection:** Funktioniert einmal, dann nie wieder (erst nach Reboot).

---

### Pitfall 5: XL9535 Expander-Konfiguration fehlt oder falsch

**What goes wrong:**
Display bleibt dunkel trotz korrekter Display-Pin-Konfiguration.

**Why it happens:**
T-RGB routet LCD Reset (Pin 6, invertiert), LCD Enable (Pin 2, invertiert), Touch Reset (Pin 1) ueber den XL9535. Ohne Expander-Config werden diese Pins nie geschaltet.

**Prevention:**
XL9535 MUSS vor Display in der YAML stehen:
```yaml
i2c:
  sda: GPIO8
  scl: GPIO48

xl9535:
  - id: xl9535_hub
    address: 0x20
```
Pin-Nummern: 0-7 und 10-17 (8-9 existieren nicht bei XL9535).

**Detection:** Display komplett schwarz nach Flash. I2C-Scan findet 0x20.

## Moderate Pitfalls

### Pitfall 6: Deprecated ST7701S-Treiber verwenden

**What goes wrong:** Config funktioniert heute, bricht bei ESPHome-Update.
**Prevention:** `mipi_rgb` mit `model: T-RGB-2.1` verwenden. ST7701S-Treiber wird in Zukunft entfernt.

### Pitfall 7: Touch-Controller falsch identifiziert

**What goes wrong:** Touchscreen reagiert nicht.
**Prevention:** Board-Version pruefen:
- 2.1" Half Circle = FT3267 -> `ft5x06`
- 2.1" Full Circle = CST820 -> `cst816`
- 2.8" Full Circle = GT911 -> `gt911`

### Pitfall 8: NTP-Sync schlaegt nach Boot fehl (Uhr zeigt 1970)

**What goes wrong:** Uhr zeigt 01:00:00 (UTC+1 auf Epoch). Alarme werden verpasst.
**Prevention:**
1. HA-Time als primaere Quelle, SNTP als Fallback
2. `time.now().is_valid()` Check in Alarm-Lambda
3. DNS-Server konfigurieren bei statischer IP
4. Display zeigt "Synchronisiere..." bis gueltige Zeit

### Pitfall 9: Alarm-Zustand geht bei Reboot verloren

**What goes wrong:** Nach Stromausfall ist Alarm deaktiviert.
**Prevention:** `restore_mode: RESTORE_DEFAULT_ON` beim Template-Switch.

### Pitfall 10: LVGL Buffer zu gross / Performance-Probleme

**What goes wrong:** Flackern, traege Touch-Reaktion, hohe Loop-Zeiten.
**Prevention:**
- `buffer_size: 25%` (nicht 100% trotz PSRAM)
- PSRAM auf octal/80MHz konfigurieren
- Nur geaenderte Bereiche invalidieren (LVGL macht das automatisch bei Widgets)

## Minor Pitfalls

### Pitfall 11: Backlight immer an

**What goes wrong:** Display leuchtet nachts, stoert beim Schlafen.
**Prevention:** LEDC-Output auf GPIO46, zeitbasiertes Dimmen.

### Pitfall 12: Flash-Mode falsch (QIO statt DIO)

**What goes wrong:** Board bootet nicht oder crasht sporadisch.
**Prevention:** `board_build.flash_mode: dio` ist Pflicht.

### Pitfall 13: RTTTL-Melodie zu leise

**What goes wrong:** Nutzer verschlaeft.
**Prevention:** Endlosschleife per Script. Gain auf 100%. Ggf. NPN-Transistor als Verstaerker.

### Pitfall 14: OTA schlaegt fehl (Partition zu klein)

**What goes wrong:** LVGL + WiFi + Audio sprengen Standard-Partition (1.3MB).
**Prevention:** Custom Partition Table oder `default_16MB.csv` nutzen (T-RGB hat 16MB Flash).

### Pitfall 15: Timezone / Sommerzeit falsch

**What goes wrong:** Uhrzeit stimmt im Winter, aber nicht im Sommer.
**Prevention:** `timezone: "Europe/Berlin"` als TZ-Datenbank-Name, NICHT als POSIX-String.

## Phase-spezifische Warnungen

| Phase-Thema | Wahrscheinlicher Pitfall | Mitigation |
|-------------|--------------------------|------------|
| Hardware-Validierung | Kein freier GPIO fuer Buzzer (#1) | Schaltplan analysieren, GPIO0 pruefen, XL9535 Pins pruefen |
| Board-Setup | Framework falsch (#2), PSRAM (#3), Flash-Mode (#12) | ESP-IDF, octal/80MHz, DIO |
| Display | XL9535 fehlt (#5), ST7701S deprecated (#6) | mipi_rgb mit T-RGB-2.1, XL9535 vor Display |
| Touch | Falscher Treiber (#7) | Board-Version verifizieren |
| Audio | RTTTL Speaker-Bug (#4), Buzzer leise (#13) | LEDC Output-Modus, Gain 100%, Script-Loop |
| Alarm-Logik | NTP-Sync (#8), Switch-Restore (#9), DST (#15) | is_valid() Check, RESTORE_DEFAULT_ON, TZ-Name |
| UI/Display | Buffer Performance (#10), Backlight (#11) | buffer_size 25%, LEDC Dimming |
| Deployment | OTA Partition (#14) | 16MB Flash, default_16MB.csv |

## "Looks Done But Isn't" Checklist

- [ ] NTP-Sync: `is_valid()` wird geprueft, nicht nur Zeit angezeigt
- [ ] Alarm-Wiederholung: 3x hintereinander ausloesen, jedes Mal hoerbar
- [ ] Switch Restore: ESP neustarten, Alarm-Switch hat korrekten State in HA
- [ ] Feiertags-Logik: HA schaltet aus UND wieder ein am naechsten Werktag
- [ ] Snooze-Repeat: Nach 5min Snooze klingelt es tatsaechlich wieder
- [ ] OTA-Update: Funktioniert nach vollstaendiger Firmware (LVGL + Audio + WiFi)
- [ ] DST: Sommerzeit-Umstellung korrekt (timezone als TZ-Name, nicht POSIX)
- [ ] Nachtmodus: Backlight geht tatsaechlich aus/dimmt, nicht nur Display-Content

## Sources

- LilyGo T-RGB "no free GPIO": https://github.com/Xinyuan-LilyGO/LilyGo-T-RGB
- RTTTL Speaker Bug: https://github.com/esphome/esphome/issues/10312
- HA Community T-RGB Thread: https://community.home-assistant.io/t/lilygo-t-rgb-esp32-s3-2-1/948076
- ESPHome XL9535: https://esphome.io/components/xl9535/
- ESPHome CST816: https://esphome.io/components/touchscreen/cst816/
- ESPHome MIPI RGB: https://esphome.io/components/display/mipi_rgb/
- ESPHome SNTP: https://esphome.io/components/time/sntp/
- ESPHome Switch restore_mode: https://esphome.io/components/switch/
