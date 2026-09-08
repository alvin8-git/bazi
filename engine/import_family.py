"""One-time validated import: Names.xlsx → data/family.json (eng review 4A).

Bad cells fail loudly with the exact cell named — the engine reads only the
validated JSON, never the spreadsheet.

Usage: .venv/bin/python -m engine.import_family [xlsx_path] [json_path]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

import openpyxl
from pydantic import BaseModel, field_validator

EXCEL_EPOCH = date(1899, 12, 30)
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", re.I)


class Member(BaseModel):
    name: str
    sex: str
    dob: date
    birth_time: time

    @field_validator("name")
    @classmethod
    def name_is_cjk(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("empty name")
        if not all("一" <= c <= "鿿" for c in v):
            raise ValueError(f"name {v!r} contains non-CJK characters")
        # ponytail: full 康熙 fan-ti stroke validation lands with 姓名學 (M4);
        # M1 guarantees CJK-only names so the stroke DB has valid input.
        return v

    @field_validator("sex")
    @classmethod
    def sex_mf(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in ("M", "F"):
            raise ValueError(f"sex must be M or F, got {v!r}")
        return v

    @property
    def birth_dt(self) -> datetime:
        return datetime.combine(self.dob, self.birth_time)


def _parse_dob(value, cell: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, (int, float)):
        return EXCEL_EPOCH + timedelta(days=int(value))
    raise ValueError(f"cell {cell}: unparseable DOB {value!r} (retyped as text?)")


def _parse_time(value, cell: str) -> time:
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, str):
        m = TIME_RE.match(value.strip())
        if m:
            h, mnt, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
            if not (1 <= h <= 12 and 0 <= mnt <= 59):
                raise ValueError(f"cell {cell}: time out of range {value!r}")
            h = h % 12 + (12 if ap == "PM" else 0)
            return time(h, mnt)
    raise ValueError(f"cell {cell}: unparseable time {value!r} (expected e.g. 4:09AM)")


def import_family(xlsx_path: str | Path, json_path: str | Path) -> list[Member]:
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.worksheets[0]
    members: list[Member] = []
    errors: list[str] = []
    for row in ws.iter_rows(min_row=2):
        name_c, sex_c, dob_c, time_c = row[0], row[1], row[2], row[3]
        if name_c.value is None:
            continue
        try:
            members.append(Member(
                name=str(name_c.value),
                sex=str(sex_c.value or ""),
                dob=_parse_dob(dob_c.value, dob_c.coordinate),
                birth_time=_parse_time(time_c.value, time_c.coordinate),
            ))
        except (ValueError, Exception) as e:  # pydantic ValidationError included
            errors.append(f"row {name_c.row}: {e}")
    if errors:
        raise SystemExit("family import FAILED:\n  " + "\n  ".join(errors))
    if not members:
        raise SystemExit("family import FAILED: no data rows found")

    out = [{"name": m.name, "sex": m.sex, "dob": m.dob.isoformat(),
            "birth_time": m.birth_time.strftime("%H:%M")} for m in members]
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), "utf8")
    return members


def load_family(json_path: str | Path) -> list[Member]:
    data = json.loads(Path(json_path).read_text("utf8"))
    return [Member(name=d["name"], sex=d["sex"], dob=date.fromisoformat(d["dob"]),
                   birth_time=time.fromisoformat(d["birth_time"])) for d in data]


if __name__ == "__main__":
    xlsx = sys.argv[1] if len(sys.argv) > 1 else "data/Names.xlsx"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/family.json"
    ms = import_family(xlsx, out)
    print(f"imported {len(ms)} members → {out}")
