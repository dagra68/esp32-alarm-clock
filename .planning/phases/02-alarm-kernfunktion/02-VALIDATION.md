---
phase: 2
slug: alarm-kernfunktion
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-25
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | ESPHome compile + OTA flash + visuelle/auditive Pruefung |
| **Config file** | alarm-clock.yaml |
| **Quick run command** | `esphome compile alarm-clock.yaml` |
| **Full suite command** | `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml` |
| **Estimated runtime** | ~120 seconds (compile) |

---

## Sampling Rate

- **After every task commit:** Run `esphome compile alarm-clock.yaml`
- **After every plan wave:** Run `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml` + Funktionstest am Board
- **Before `/gsd:verify-work`:** Compile + Upload + Alarm-Funktionstest must be green
- **Max feedback latency:** 120 seconds (compile)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 0 | ALRM-03 | manual | `esphome compile alarm-clock.yaml` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 1 | ALRM-03 | compile | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |
| 2-01-03 | 01 | 1 | ALRM-03 | compile + manual (auditiv) | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |
| 2-02-01 | 02 | 1 | ALRM-01 | compile | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |
| 2-02-02 | 02 | 1 | ALRM-04, ALRM-05 | compile | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |
| 2-03-01 | 03 | 2 | ALRM-02, DISP-04, DISP-05 | compile + manual (visuell) | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |
| 2-03-02 | 03 | 2 | ALRM-06 | compile + manual (visuell) | `esphome compile alarm-clock.yaml` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] I2S-Pin-Nummern aus T-RGB-Schaltplan ermitteln (BCLK, LRCLK, DOUT) — Blocker fuer I2S-Konfiguration
- [ ] MAX98357A physisch anschliessen und korrekte GPIO-Nummern in alarm-clock.yaml eintragen

*Hinweis: `alarm-clock.yaml` existiert bereits als funktionstuechtiger Ausgangszustand.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| RTTTL-Melodie hoerbar ueber I2S-Lautsprecher | ALRM-03 | Audio-Output nur physisch pruefbar | Alarm-Zeit auf naechste Minute setzen, warten bis Melodie spielt, Lautstaerke und Klangqualitaet pruefen |
| Alarm klingelt Mo-Fr aber nicht Sa/So | ALRM-01 | Wochentag-Logik erfordert Zeitwarten oder RTC-Mock | weekday_only Switch einschalten, Alarm-Zeit auf naechste Minute, Wochentag beachten |
| Snooze pausiert 5 Minuten und klingelt erneut | ALRM-05 | Zeitabhaengig, 5 Minuten warten | Waehrend klingendem Alarm Snooze-Button druecken, nach 5min auf erneutes Klingeln warten |
| Alarm-Status auf Display sichtbar | DISP-05 | Display-Darstellung visuell pruefbar | Alarm aktivieren/deaktivieren, Display-Anzeige auf Uebereinstimmung pruefen |
| Naechste Alarmzeit auf Display | DISP-04 | Display-Darstellung visuell pruefbar | Alarmzeit aendern, pruefen ob Display-Anzeige aktualisiert wird |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
