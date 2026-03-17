---
phase: 1
slug: board-und-digitale-uhr
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | ESPHome compile + manual hardware verification |
| **Config file** | `alarm-clock.yaml` |
| **Quick run command** | `esphome compile alarm-clock.yaml` |
| **Full suite command** | `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml` |
| **Estimated runtime** | ~120 seconds (compile) |

---

## Sampling Rate

- **After every task commit:** Run `esphome compile alarm-clock.yaml`
- **After every plan wave:** Run `esphome compile alarm-clock.yaml && esphome upload alarm-clock.yaml`
- **Before `/gsd:verify-work`:** Full suite must be green + hardware check
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | DISP-01 | compile | `esphome compile alarm-clock.yaml` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | DISP-01 | compile | `esphome compile alarm-clock.yaml` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 2 | TIME-01 | compile+manual | `esphome compile alarm-clock.yaml` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 2 | DISP-03 | manual | Manual: Datum sichtbar auf Display | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `alarm-clock.yaml` — ESPHome Basis-Konfiguration (erstellt in Wave 1)
- [ ] ESPHome CLI installiert und erreichbar

*Wave 0 = Grundstruktur der YAML-Datei anlegen, damit Compile-Tests laufen können.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Uhrzeit sichtbar auf rundem Display | DISP-01 | Embedded hardware, kein Simulator | Board verbinden, `esphome upload`, Display prüfen |
| NTP-Sync (Zeit korrekt nach WLAN-Verbindung) | TIME-01 | Netzwerkabhängig, nur auf Hardware testbar | Board starten, nach 30s Uhrzeit prüfen |
| Datum + Wochentag sichtbar | DISP-03 | Embedded display | Display nach Upload prüfen |
| Display-Backlight eingeschaltet | DISP-01 | Hardware | Sichtprüfung nach Upload |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
