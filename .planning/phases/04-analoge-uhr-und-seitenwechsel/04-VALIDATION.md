---
phase: 4
slug: analoge-uhr-und-seitenwechsel
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | ESPHome compile + OTA flash (kein Unit-Test-Framework) |
| **Config file** | `esp32-alarm-clock.yaml` |
| **Quick run command** | `esphome compile esp32-alarm-clock.yaml` |
| **Full suite command** | `esphome compile esp32-alarm-clock.yaml && esphome upload esp32-alarm-clock.yaml` |
| **Estimated runtime** | ~60 seconds (compile), ~120 seconds (compile + flash) |

---

## Sampling Rate

- **Nach jedem Task-Commit:** `esphome compile esp32-alarm-clock.yaml`
- **Nach jeder Plan-Wave:** Compile + OTA Flash + manuelle Sichtprüfung
- **Vor `/gsd:verify-work`:** Vollständiger Compile + Flash + alle manuellen Tests grün
- **Max feedback latency:** 60 seconds (compile)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | DISP-02 | compile | `esphome compile esp32-alarm-clock.yaml` | ✅ | ⬜ pending |
| 4-01-02 | 01 | 1 | DISP-02 | compile | `esphome compile esp32-alarm-clock.yaml` | ✅ | ⬜ pending |
| 4-01-03 | 01 | 2 | DISP-06 | compile | `esphome compile esp32-alarm-clock.yaml` | ✅ | ⬜ pending |
| 4-01-04 | 01 | 2 | DISP-06 | manual | OTA flash + HA Select prüfen | ❌ manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* ESPHome compile validiert YAML-Syntax und LVGL-Konfiguration automatisch. Kein separates Test-Setup nötig.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Analoge Uhr zeigt korrekte Uhrzeit | DISP-02 | Visuell — LVGL-Rendering nur auf Hardware prüfbar | OTA flash, Analog-Seite aufrufen, Uhrzeit mit Referenz vergleichen |
| Zeiger-Farbe schwarz auf Pink-Hintergrund | DISP-02 | Visuell | Analog-Seite aufrufen, Zeiger-Farbe prüfen |
| Seitenwechsel Digital ↔ Analog per HA-Select | DISP-06 | Hardware + HA-Integration | In HA "Zifferblatt" auf "Analog" setzen → ESP wechselt; zurück auf "Digital" → ESP wechselt |
| 12 Zahlen korrekt positioniert | DISP-02 | Visuell | Analog-Seite aufrufen, alle 12 Zahlen sichtbar und korrekt positioniert |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
