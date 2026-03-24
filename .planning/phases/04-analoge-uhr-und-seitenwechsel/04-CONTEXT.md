# Phase 4: Analoge Uhr und Seitenwechsel - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Eine neue LVGL-Seite mit analogem Zifferblatt (Stunden- und Minutenzeiger via LVGL Meter-Widget) wird hinzugefügt. Der Wechsel zwischen digitalem und analogem Zifferblatt wird ausschließlich über eine Home Assistant Select-Entity gesteuert. Beide Zifferblätter zeigen NTP-synchronisierte Zeit. Touch-Navigation zwischen Seiten ist explizit Out-of-Scope.

</domain>

<decisions>
## Implementation Decisions

### Analoguhr-Rendering
- LVGL Meter-Widget (`lv_meter`) — kein Custom-Lambda/Canvas
- Nur Stunden- und Minutenzeiger — kein Sekundenzeiger
- Update-Takt: minutenweise (kein eigener 1s-Interval nötig)
- Zeiger-Farbe: Schwarz (`0x000000`)

### Stundenmarkierungen
- 12 Zahlen (1–12) auf dem Zifferblatt
- Positionierung via Polar-Koordinaten-Lambda (sin/cos um Mittelpunkt des runden Displays)

### Seitenwechsel
- Ausschließlich über Home Assistant — eine `select` Entity mit Optionen: "Digital", "Analog"
- Erweiterbar für zukünftige Designs (z.B. "Minimal", "Dark")
- Kein Touch-Trigger für Seitenwechsel
- ESPHome-Seite wechselt via `lvgl.page.show:` im `set_action` der Select-Entity

### Hintergrundfarbe
- Standard: Pink `0xFF69B4` — konsistent mit bestehenden Seiten
- Farbwechsel über HA `select` Entity mit vordefinierten Optionen (z.B. Pink, Weiß, Schwarz, Dunkelblau)
- Farb-Select setzt globale Variable, Lambda aktualisiert `bg_color` der Analog-Seite

### Claude's Discretion
- Exakte Radius-Werte für Zahlen-Positionierung auf dem runden Display
- Meter-Widget arc-Konfiguration (Winkelbereich, Skalierung)
- Anzahl der Farboptionen im Farb-Select (mindestens 4)
- Name und Icon der neuen HA-Entities

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bestehende Implementierung
- `alarm-clock.yaml` — Vollständige aktuelle ESPHome-Config. Enthält alle LVGL-Pages, Touch-Setup, Globals, Scripts. Neue Analog-Seite wird hier ergänzt.

### Anforderungen
- `.planning/REQUIREMENTS.md` — DISP-02 (Analoguhr mit Meter-Widget), DISP-06 (Seitenwechsel)

### Bekannte Hardware-Entscheidungen
- `.planning/STATE.md` — ft5x06 `marked FAILED` beim Boot (kein Problem für Phase 4 da Touch nicht für Navigation genutzt wird), ESP-IDF Framework Pflicht, PSRAM 8MB octal aktiv

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `digital_clock_page`: Bestehendes Muster für LVGL-Page mit Hintergrundfarbe und Widgets — Analog-Seite folgt gleichem Aufbau
- `lvgl.page.show:` Action: Bereits für Navigation zwischen allen Seiten genutzt — gleiches Pattern für Select-Entity `set_action`
- `sntp_time`: Bestehende NTP-Zeit-Quelle — Meter-Widget liest daraus via Lambda (gleich wie `time_label`)
- Globals (`alarm_hour`, `alarm_minute`, etc.): Pattern für restore_value und Lambda-Zugriff bereits etabliert

### Established Patterns
- Hintergrundfarbe: `bg_color: 0xFF69B4` auf allen Haupt-Seiten
- Fonts: `montserrat_14/24/36/48` verfügbar
- Touch: `on_short_click` / `on_long_press` auf Buttons — nicht für globale Navigation
- HA-Entities: `switch`, `datetime`, `select` bereits vorhanden — neue `select` Entities folgen gleichem Muster

### Integration Points
- `lvgl: pages:` Block — neue `analog_clock_page` wird als weiterer Eintrag hinzugefügt
- `select:` Block — zwei neue Template-Selects: Zifferblatt-Auswahl + Hintergrundfarbe
- Bestehende `digital_clock_page` bleibt unverändert

</code_context>

<specifics>
## Specific Ideas

- Select-Entity "Zifferblatt" mit Optionen "Digital" / "Analog" — erweiterbar für künftige Designs
- Farb-Select mit mindestens: Pink (Standard), Weiß, Schwarz, Dunkelblau — gleiche Farben wie bestehende Button-Farben (`0x1A1A2E` bereits im Code)

</specifics>

<deferred>
## Deferred Ideas

- Weitere Zifferblatt-Designs (z.B. Minimal, Dark) — über Select-Entity later erweiterbar, aber nicht in Phase 4
- Animierter Sekundenzeiger mit Sweep — bereits als v2 Requirement UX-02 / DISP-07 erfasst

</deferred>

---

*Phase: 04-analoge-uhr-und-seitenwechsel*
*Context gathered: 2026-03-24*
