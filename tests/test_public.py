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
    assert len(tok) == 8          # short enough to share, 64^8 against guessing
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


def test_rename_person():
    tok = _new_ws(P1)
    r = client.patch(f"/api/pub/w/{tok}/person/0", json={"name": "改名"})
    assert r.status_code == 200 and r.json()["people"][0]["name"] == "改名"
    assert client.patch(f"/api/pub/w/{tok}/person/9",
                        json={"name": "x"}).status_code == 404
    assert client.patch(f"/api/pub/w/{tok}/person/0",
                        json={"name": ""}).status_code == 422


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
    assert client.get("/api/pub/w/short").status_code == 404   # <8 chars rejected
    assert client.get("/api/pub/w/../../etc/passwd").status_code == 404


def test_redis_store_roundtrip(monkeypatch):
    """When the Upstash env is present, workspaces go through Redis with TTL."""
    import public
    fake: dict[str, str] = {}

    def fake_cmd(*cmd):
        if cmd[0] == "SET":
            assert cmd[3:] == ("EX", str(public.TTL_SECONDS))
            fake[cmd[1]] = cmd[2]
            return "OK"
        return fake.get(cmd[1])                     # GET

    monkeypatch.setattr(public, "_REDIS_URL", "https://fake.upstash.io")
    monkeypatch.setattr(public, "_redis_cmd", fake_cmd)
    tok = client.post("/api/pub/workspace", json=P1).json()["token"]
    assert f"ws:{tok}" in fake
    assert client.post(f"/api/pub/w/{tok}/person", json=P2).status_code == 200
    d = client.get(f"/api/pub/w/{tok}").json()
    assert len(d["people"]) == 2 and d["harmony"]
    assert client.get("/api/pub/w/aaaabbbb").status_code == 404


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
    # geomancer's read: structure meaning + wealth spots (+ door if marked)
    assert d["main"]["notes"] and d["main"]["structure"] in d["main"]["notes"][0]
    assert any("財位" in n for n in d["main"]["notes"])
    assert d["main"]["rooms"]["master"] in ("坎", "艮", "震", "巽", "離", "坤", "兌", "乾", "中")
    assert len(d["scores"]["scores"]) == 2
    assert all(s["breakdown"] for s in d["scores"]["scores"])
    # per-person deliverable: house match, directions, room ranking, suggestion
    assert d["house"]["sitting_gua"] and "四" in d["house"]["group"]
    assert len(d["people"]) == 2
    for p in d["people"]:
        assert isinstance(p["match"], bool)
        assert len(p["dirs_good"]) == 4 and len(p["dirs_bad"]) == 4
        assert p["rooms"] and p["rooms"][0]["label"] == "Master"
        assert {"t", "v"} <= set(p["rooms"][0]["why"][0])
    assert d["suggestion"]["assignment"]["Master"]
    assert isinstance(d["suggestion"]["household_total"], float)
    # aspect scores ride along on every analysis
    assert len(d["aspects"]["测试一"]) == 6
    assert {a["aspect"] for a in d["aspects"]["测试一"]} == {
        "health", "career", "study", "wealth", "relationship", "luck"}
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


def test_homes_and_battlecard():
    tok = _new_ws(P1, P2)
    h1 = client.post(f"/api/pub/w/{tok}/homes", json={"name": "TowerB"}).json()["id"]
    h2 = client.post(f"/api/pub/w/{tok}/homes", json={"name": "TowerC"}).json()["id"]
    # homes are renameable
    r = client.patch(f"/api/pub/w/{tok}/homes/{h1}", json={"name": "TowerB #02-19"})
    assert r.status_code == 200
    assert any(h["name"] == "TowerB #02-19" for h in r.json()["homes"])
    req = {"facing_deg": 135, "period": 8, "rooms": ROOMS,
           "assignment": {"master": ["测试一", "测试二"]}, "entrance": [0.5, 0.9]}
    assert client.post(f"/api/pub/w/{tok}/homes/{h1}/analyze",
                       json=req).status_code == 200
    d2 = client.post(f"/api/pub/w/{tok}/homes/{h2}/analyze",
                     json={**req, "facing_deg": 270}).json()
    assert len(d2["aspects"]["测试一"]) == 6
    # config + analysis saved per home, restorable
    saved = client.get(f"/api/pub/w/{tok}/homes/{h1}").json()
    assert saved["entrance"] == [0.5, 0.9]
    assert saved["rooms"][0]["label"] == "Master"
    assert saved["analysis"]["house"] and saved["analysis"]["people"]
    lst = client.get(f"/api/pub/w/{tok}/homes").json()["homes"]
    assert [h["analyzed"] for h in lst] == [True, True]
    # battlecard across the two homes
    bc = client.get(f"/api/pub/w/{tok}/battlecard").json()
    assert len(bc["homes"]) == 2 and len(bc["people"]) == 2
    p = bc["people"][0]
    assert p["edge"] in (h1, h2) and set(p["homes"]) == {h1, h2}
    assert len(p["homes"][h1]["aspects"]) == 6
    assert p["homes"][h1]["aspects"]["health"]["band"] in (
        "strong", "good", "fair", "weak", "poor")
    assert client.delete(f"/api/pub/w/{tok}/homes/{h2}").status_code == 200
    assert client.get(f"/api/pub/w/{tok}/battlecard").status_code == 400


def test_blob_floorplan(monkeypatch):
    """With BLOB_READ_WRITE_TOKEN set, plans go to Vercel Blob; GET redirects."""
    import public
    deleted = []
    monkeypatch.setattr(public, "_BLOB_TOKEN", "fake")
    monkeypatch.setattr(public, "_blob_put",
                        lambda p, d, c: f"https://blob.test/{p}-rnd")
    monkeypatch.setattr(public, "_blob_delete", deleted.append)
    tok = _new_ws(P1)
    hid = client.post(f"/api/pub/w/{tok}/homes", json={"name": "B"}).json()["id"]
    files = {"file": ("p.png", b"\x89PNG-fake", "image/png")}
    assert client.post(f"/api/pub/w/{tok}/homes/{hid}/floorplan",
                       files=files).status_code == 200
    r = client.get(f"/api/pub/w/{tok}/homes/{hid}/floorplan",
                   follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"].startswith("https://blob.test/plans/")
    # re-upload replaces (old blob deleted), delete-home cleans up too
    assert client.post(f"/api/pub/w/{tok}/homes/{hid}/floorplan",
                       files=files).status_code == 200
    assert len(deleted) == 1
    assert client.delete(f"/api/pub/w/{tok}/homes/{hid}").status_code == 200
    assert len(deleted) == 2


def test_legacy_analyze_creates_default_home():
    tok = _new_ws(P1)
    req = {"facing_deg": 135, "period": 8, "rooms": ROOMS, "assignment": {}}
    assert client.post(f"/api/pub/w/{tok}/analyze", json=req).status_code == 200
    lst = client.get(f"/api/pub/w/{tok}/homes").json()["homes"]
    assert len(lst) == 1 and lst[0]["name"] == "My home" and lst[0]["analyzed"]


def test_baby_page():
    r = client.post("/api/pub/baby", data={"sex": "M", "dob": "2026-01-15",
                                           "birth_time": "09:30", "surname": "王"})
    assert r.status_code == 200
    assert "四柱" in r.text and "起名方向" in r.text and "用神" in r.text
    assert client.post("/api/pub/baby",
                       data={"sex": "M", "dob": "bad"}).status_code == 400


def test_certificate():
    r = client.get("/api/pub/certificate", params={
        "surname": "王", "given": "涛冰", "sex": "M",
        "dob": "2026-03-01", "birth_time": "10:00"})
    assert r.status_code == 200
    t = r.text
    assert "命名證書" in t and "王涛冰" in t
    assert "三 才 五 格" in t and "八 字 四 柱" in t
    assert "康熙" in t and "喜用神" in t
    # bad inputs
    assert client.get("/api/pub/certificate", params={
        "surname": "王", "given": "涛冰", "sex": "X",
        "dob": "2026-03-01"}).status_code == 400
    assert client.get("/api/pub/certificate", params={
        "surname": "𰻝", "given": "涛", "sex": "M",
        "dob": "2026-03-01"}).status_code == 400
    assert client.get("/api/pub/certificate", params={
        "surname": "王", "given": "涛冰乐", "sex": "M",
        "dob": "2026-03-01"}).status_code == 400


def test_baby_certificate_links():
    r = client.post("/api/pub/baby", data={"sex": "M", "dob": "2026-01-15",
                                           "birth_time": "09:30",
                                           "surname": "王"})
    assert r.status_code == 200
    assert "/api/pub/certificate?" in r.text and "命名證書" in r.text


def test_pages_served():
    for path in ("/start", "/fengshui", "/baby", "/app"):
        assert client.get(path).status_code == 200
    assert "Sitemap:" in client.get("/robots.txt").text
    assert "<urlset" in client.get("/sitemap.xml").text
    v = client.get("/api/pub/version").json()
    assert v["version"] and v["env"] in ("prod", "local")
    landing = client.get("/")
    assert landing.status_code == 200
    for word in ("Personal", "House", "Name"):
        assert word in landing.text


def test_person_reading_13_sections():
    tok = _new_ws(P1)
    d = client.get(f"/api/pub/w/{tok}/person/0/chart").json()
    # the same 13-section payload the family Reading tab consumes
    assert {"pillars", "strength", "tengods_pct", "domains", "dayun_detail",
            "youxing", "shensha", "personality", "health", "industries",
            "careers", "windows", "life_palaces", "interpretation",
            "citations"} <= set(d)
    assert d["name"] == "测试一" and len(d["windows"]["years"]) == 10
    # strategy advice distributed per section (s2..s13)
    assert {"s2", "s5", "s8", "s10", "s11", "s12", "s13"} <= set(d["strategy"])
    assert d["strategy"]["s12"]["advice"] and d["strategy"]["s13"]["wealth_pattern"]
    assert client.get(f"/w/{tok}/person/0/reading").status_code == 200
    assert client.get(f"/w/{tok}/person/5/reading").status_code == 404
