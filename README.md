# FengShui Family Compass

BaZi 八字 × 玄空飛星 home optimizer for one household — a personal, local-only
tool. Design doc: `docs/designs/fengshui-family-compass.md` (eng-reviewed,
ENG CLEARED 2026-08-31).

## Status

- **All four milestones shipped (61 pytest tests green).**
  M1 engine core (golden-fixture-validated incl. `baziValidation.docx`, the
  published 八運乾山巽向 旺山旺向 chart, and a 20/20-pillar cross-validation of
  all 5 members against the independent `@openfate/bazi-mcp` engine, 2026-08-31) · M2 web UI + floorplan overlay ·
  M3 constrained room optimizer + live what-if scoring · M4 流年流月 forecasts,
  擇日 date ratings, 姓名學 (康熙 stroke validation + 三才五格), and the
  coarse-mode candidate-unit evaluator.
- Server: `.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8808` →
  http://192.168.1.168:8808 on the home LAN (8 tabs).

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install sxtwl openpyxl pydantic pytest
.venv/bin/python -m pytest tests/ -q          # 32 tests
.venv/bin/python -m engine.import_family Names.xlsx data/family.json
.venv/bin/python -m engine.report --year 2026 # → data/out/m1_report.json + summary
```

## Inputs

- `Names.xlsx` — family members (name 繁體, sex, DOB, birth time). Imported and
  validated into `data/family.json`; bad cells fail loudly with the cell named.
- `data/house.json` — facing degrees + period(s). **PROVISIONAL** until the
  compass cross-check procedure is done (see design doc "The Assignment").
  Both Period 8 and 9 charts are emitted until the renovation date is confirmed.
- `floorplan.jpeg` — used from Milestone 2 (room polygon tracing).

## Engine map

| Module | Owns |
|---|---|
| `engine/wuxing.py` | ALL 干支/五行 constant tables (single source, reference-tested) |
| `engine/calendar.py` | sxtwl wrapper, 節氣, SG timezone history (UTC+7:30 pre-1982), true-solar correction |
| `engine/bazi.py` | `Chart` contract: pillars, 十神, element weights, 4-step strength, 大運 |
| `engine/yongshen.py` | 用神 (扶抑 + 調候 implemented; 病藥/通關 advisory until M4) |
| `engine/bazhai.py` | 命卦, East/West groups, 遊年八星 (derived, tested vs published rows) |
| `engine/xuankong.py` | flying stars: natal 山/向, annual; period is a runtime parameter |
| `engine/join.py` | 3-layer `ScoreBreakdown` per person × sector (premise-5 labeling) |
| `engine/import_family.py` | validated xlsx → json import |
| `engine/report.py` | M1 CLI report |

Every score decomposes into cited rules — `breakdown[].source_ref` — so any
number can be traced to the classical rule (or labeled modern synthesis) that
produced it.


## Public release note

This repository ships with a FICTIONAL sample family and home (`data/*.json`, `floorplan.jpeg`). Replace them with your own birth data and traced floorplan to use the app — personal data stays on your machine and is never part of this repo. The family-specific golden test suite is excluded for the same reason; the included tests cover the calculation engines (玄空/八宅/五行/sectors).
