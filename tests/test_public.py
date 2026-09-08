"""bazifor.me public surfaces — workspace, reports, fengshui analyzer, baby."""
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)

P1 = {"name": "测试一", "sex": "M", "dob": "1985-03-15", "birth_time": "08:30"}
P2 = {"name": "测试二", "sex": "F", "dob": "1988-07-20", "birth_time": "14:10"}


def _new_ws(*people):
    r = client.post("/api/pub/workspace", json=people[0])
    assert r.status_code == 200, r.text
    tok = r.json()["token"]
    for p in people[1:]:
        assert client.post(f"/api/pub/w/{tok}/person", json=p).status_code == 200
    return tok


def test_workspace_create_and_summary():
    tok = _new_ws(P1)
    d = client.get(f"/api/pub/w/{tok}").json()
    assert len(d["people"]) == 1 and d["harmony"] is None
    p = d["people"][0]
    assert p["day_master"] and len(p["pillars"]) == 4
    assert p["favourable"] and p["top_careers"]
    assert set(p["domains"]) >= {"career", "wealth", "health"}


def test_workspace_harmony_and_cap():
    tok = _new_ws(P1, P2)
    d = client.get(f"/api/pub/w/{tok}").json()
    assert d["harmony"] and len(d["harmony"]["pairs"]) == 1
    assert 0 <= d["harmony"]["pairs"][0]["score"] <= 100
    for i in range(6):
        r = client.post(f"/api/pub/w/{tok}/person",
                        json={**P1, "name": f"p{i}"})
        assert r.status_code == 200
    assert client.post(f"/api/pub/w/{tok}/person",
                       json={**P1, "name": "p9"}).status_code == 400
    # remove then re-add works
    assert client.delete(f"/api/pub/w/{tok}/person/7").status_code == 200
    assert client.post(f"/api/pub/w/{tok}/person",
                       json={**P1, "name": "p9"}).status_code == 200


def test_person_report_html():
    tok = _new_ws(P1, P2)
    r = client.get(f"/w/{tok}/person/0/report")
    assert r.status_code == 200
    assert "BaZi strategy report" in r.text
    assert "Q1" in r.text and "Windows" not in r.headers  # full report body
    assert "测试二" in r.text or "family" in r.text.lower()  # family section present
    assert client.get(f"/w/{tok}/person/9/report").status_code == 404


def test_bad_inputs():
    assert client.post("/api/pub/workspace",
                       json={**P1, "dob": "1985-13-40"}).status_code in (400, 422)
    assert client.post("/api/pub/workspace",
                       json={**P1, "sex": "X"}).status_code == 422
    assert client.get("/api/pub/w/nosuchtoken12345678").status_code == 404
    assert client.get("/api/pub/w/../../etc/passwd").status_code == 404


ROOMS = [
    {"id": "master", "label": "Master", "sleeping": True, "capacity": 2,
     "poly": [[50, 50], [250, 50], [250, 200], [50, 200]]},
    {"id": "living", "label": "Living", "sleeping": False, "capacity": 0,
     "poly": [[300, 50], [500, 50], [500, 300], [300, 300]]},
]


def test_analyze_fengshui():
    tok = _new_ws(P1, P2)
    req = {"facing_deg": 135, "period": 8, "rooms": ROOMS,
           "assignment": {"master": ["测试一", "测试二"]}}
    r = client.post(f"/api/pub/w/{tok}/analyze", json=req)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["main"]["structure"]
    assert d["main"]["rooms"]["master"] in ("坎", "艮", "震", "巽", "離", "坤", "兌", "乾", "中")
    assert len(d["scores"]["scores"]) == 2
    assert all(s["breakdown"] for s in d["scores"]["scores"])
    # 騎線 facing → alternate chart with its own scores
    r2 = client.post(f"/api/pub/w/{tok}/analyze", json={**req, "facing_deg": 307})
    d2 = r2.json()
    assert d2.get("alternate") and d2.get("alternate_scores")
    assert d2["boundary"]["zone"] == "騎線"
    # bad room / person names rejected
    assert client.post(f"/api/pub/w/{tok}/analyze",
                       json={**req, "assignment": {"nope": ["测试一"]}}).status_code == 400
    assert client.post(f"/api/pub/w/{tok}/analyze",
                       json={**req, "assignment": {"master": ["ghost"]}}).status_code == 400


def test_baby_page():
    r = client.post("/api/pub/baby", data={"sex": "M", "dob": "2026-01-15",
                                           "birth_time": "09:30", "surname": "王"})
    assert r.status_code == 200
    assert "四柱" in r.text and "起名方向" in r.text and "用神" in r.text
    assert client.post("/api/pub/baby",
                       data={"sex": "M", "dob": "bad"}).status_code == 400


def test_pages_served():
    for path in ("/start", "/fengshui", "/baby"):
        assert client.get(path).status_code == 200
