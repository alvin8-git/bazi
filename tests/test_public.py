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
    # domains are bilingual triples [zh, en, score] for the roster card
    assert len(p["domains"]) == 6
    assert all(len(d) == 3 and isinstance(d[2], int) for d in p["domains"])
    assert any("Career" in d[1] for d in p["domains"])


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
    # P1 room briefs: one per traced room, old colors key still present
    assert set(d["room_briefs"]) == {"master", "living"}
    assert d["room_briefs"]["master"]["colours_use"] and "severity" in d["room_briefs"]["master"]
    assert d["room_briefs"]["master"]["palace"] == d["main"]["rooms"]["master"]
    # P2: placements/afflictions joined to every traced room, bed rows on assigned rooms
    assert set(d["room_placements"]) == {"master", "living"}
    for rid in ("master", "living"):
        assert "placements" in d["room_briefs"][rid] and "afflictions" in d["room_briefs"][rid]
        assert d["room_briefs"][rid]["afflictions"]["year"] == d["year"]
    # trace checks are always present; a balcony is excluded from the centre and reported
    assert isinstance(d["trace_checks"], list) and d["include_outdoor"] is False
    balc = {"id": "balc", "label": "Balcony", "sleeping": False, "capacity": 0, "rtype": "Balcony 阳台",
            "poly": [[50, 400], [500, 400], [500, 520], [50, 520]]}
    r2 = client.post(f"/api/pub/w/{tok}/analyze", json=dict(req, rooms=ROOMS + [balc]))
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    assert d2["main"]["rooms"]["master"] == d["main"]["rooms"]["master"]
    assert any(c["code"] == "outdoor-excluded" and c["rooms"] == ["Balcony"] for c in d2["trace_checks"])
    assert "balc" in d2["main"]["rooms"]
    r3 = client.post(f"/api/pub/w/{tok}/analyze", json=dict(req, rooms=ROOMS + [balc], include_outdoor=True))
    assert any(c["code"] == "outdoor-included" for c in r3.json()["trace_checks"])
    r = client.post(f"/api/pub/w/{tok}/analyze", json=req); d = r.json()      # restore the fixture state
    # selection-driven report: roles, two assignment options, rows for every pair, palettes for all
    assert all(p["role"] in ("parent", "adult", "child") and "age" in p for p in d["people"])
    assert d["suggestion"]["default"]["assignment"] and d["suggestion"]["optimal"]["assignment"]
    assert d["suggestion"]["assignment"] == d["suggestion"]["default"]["assignment"]
    assert len(d["placement"]["rows"]) == len(d["people"]) * 1      # one sleeping room in this fixture
    for b in d["room_briefs"].values():
        if b.get("palace") != "中":
            assert set(b["occupant_options"]) == {p["name"] for p in d["people"]}
    # P3: lighting on every brief, F2 + timing on afflicted rooms, two gate candidates
    assert all("fixed_k" in b["lighting"] for b in d["room_briefs"].values())
    assert len(d["chengmen"]) == 2 and all("guarded" in g for g in d["chengmen"])
    for row in d["works_timing"]["rooms"]:
        b = d["room_briefs"][row["id"]]
        assert any(r["code"] == "F2" for r in b["timing_rules"])
        assert b["timing"]["structure_ok"] == (not row["now"])
    mb = d["room_briefs"]["master"]["beds"]
    assert len(mb) == 2 and all("site_checks" in r and r["site_checks"] for r in mb)
    for r in mb:
        if r["desk"]:
            assert r["desk"]["door_side"] in ("behind-left", "behind-right", "square-behind", "side", "front", "none")
    assert d["room_briefs"]["master"]["occupants"] and d["colors"]
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
    # four palaces 宮位: pillars arc + spouse/children/vault deep lines
    P = d["palaces"]
    assert [p["key"] for p in P["pillars"]] == ["year", "month", "day", "hour"]
    assert all(p["gz"] and p["line"] for p in P["pillars"])
    assert P["spouse"]["branch"] and P["spouse"]["state"]
    assert "output_share" in P["children"]
    assert P["vault"]["state"] and isinstance(P["vault"]["present"], bool)
    # structure check: 用神 alignment, rooting, classical pair patterns
    ti = d["tengod_insights"]
    assert 1 <= len(ti["favor"]) <= 3
    assert all(f["status"] in ("favourable", "unfavourable", "neutral")
               for f in ti["favor"])
    assert all(r["state"] in ("rooted", "floating") for r in ti["rooted"])
    assert isinstance(ti["patterns"], list)
    # 生剋 interaction layer: DM flows + findings for the §1 wheel
    er = d["element_relations"]
    assert er["dm"] in "木火土金水" and len(er["flows"]) == 5
    assert set(er["flows"]) == {"resource", "output", "wealth", "pressure", "peer"}
    assert er["findings"] and abs(sum(er["share"].values()) - 100) < 1
    # every calculated section carries its own narrative paragraph
    import re
    secs = {int(m.group(1)) for p in d["interpretation"]["paragraphs"]
            for m in [re.match(r"\[§(\d+)", p)] if m}
    assert {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13} <= secs
    # strategy advice distributed per section (s2..s13)
    assert {"s2", "s5", "s8", "s10", "s11", "s12", "s13"} <= set(d["strategy"])
    assert d["strategy"]["s12"]["advice"] and d["strategy"]["s13"]["wealth_pattern"]
    assert client.get(f"/w/{tok}/person/0/reading").status_code == 200
    assert client.get(f"/w/{tok}/person/5/reading").status_code == 404


def test_put_person_edits_birth_and_name():
    r = client.post("/api/pub/workspace", json={"name": "Edit A", "sex": "M", "dob": "1988-03-15", "birth_time": "09:30"})
    assert r.status_code == 200
    tok = r.json()["token"]
    before = client.get(f"/api/pub/w/{tok}/person/0/chart").json()["pillars"]["day"]
    r = client.put(f"/api/pub/w/{tok}/person/0", json={"name": "Edit B", "sex": "F", "dob": "1990-11-02", "birth_time": "14:20"})
    assert r.status_code == 200
    ws = r.json()
    assert ws["people"][0]["name"] == "Edit B" and ws["people"][0]["sex"] == "F" and ws["people"][0]["dob"] == "1990-11-02"
    after = client.get(f"/api/pub/w/{tok}/person/0/chart").json()["pillars"]["day"]
    assert after != before
    assert client.put(f"/api/pub/w/{tok}/person/7", json={"name": "x", "sex": "M", "dob": "1990-01-01"}).status_code == 404


# ---- name builder API ---------------------------------------------------------
NAME_Q = "sex=F&dob=2026-03-15&birth_time=09:30"


def test_name_chart_and_candidates():
    r = client.get(f"/api/pub/name/chart?{NAME_Q}&surname=王")
    assert r.status_code == 200
    d = r.json()
    assert len(d["pillars"]) == 4 and all(p["sel"] and p["bel"] for p in d["pillars"])
    assert d["surname_ks"] == [4] and d["fav"] and sum(d["weights"].values()) in range(98, 103)
    r = client.get(f"/api/pub/name/chars?surname=王&{NAME_Q}&given=__&slot=0")
    c = r.json()
    assert r.status_code == 200 and len(c["tiles"]) == 48 and len(c["chips"]) == 6
    assert all(t["el"] in d["fav"] for t in c["tiles"])
    r = client.get(f"/api/pub/name/chars?surname=王&{NAME_Q}&given=禄_&slot=1&py=ting&el=all")
    assert "婷" in [t["ch"] for t in r.json()["tiles"]]
    assert client.get(f"/api/pub/name/chars?surname=王&sex=X&dob=2026-03-15").status_code == 400
    assert client.get(f"/api/pub/name/chart?{NAME_Q}&surname=王王王").status_code == 400


def test_name_score_trad_switch_and_certificate():
    a = client.get(f"/api/pub/name/score?surname=王&given=禄云&{NAME_Q}").json()
    b = client.get(f"/api/pub/name/score?surname=王&given=禄云&trad=云:云&{NAME_Q}").json()
    assert a["trad"] == "王祿雲" and b["trad"] == "王祿云" and a["strokes"] != b["strokes"]
    assert [g["grid"] for g in a["grids"]] == ["天格", "人格", "地格", "外格", "總格"]
    assert client.get(f"/api/pub/name/score?surname=王&given=禄云&trad=云:雨&{NAME_Q}").status_code == 400
    r = client.get(f"/api/pub/certificate?surname=王&given=优云&{NAME_Q}")
    assert r.status_code == 200 and "繁體 王優雲" in r.text and "color:#" in r.text
    r = client.get(f"/api/pub/certificate?surname=王&given=优云&trad=云:云&{NAME_Q}")
    assert "繁體 王優云" in r.text


def test_name_optimise_endpoint():
    r = client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=禄_")
    d = r.json()
    assert r.status_code == 200 and d["mode"] == "fill" and d["results"]
    assert all(x["given"][0] == "禄" and 0 <= x["score"]["total"] <= 100 for x in d["results"])
    d2 = client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=禄云").json()
    assert d2["mode"] == "improve" and d2["baseline"]["given"] == "禄云"
    s = client.get(f"/api/pub/name/score?surname=王&given=禄云&{NAME_Q}").json()
    assert s["score"]["total"] == d2["baseline"]["score"]["total"]
    assert client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=___").status_code in (200, 400)
    assert client.get(f"/api/pub/name/optimise?surname=王王王&{NAME_Q}&given=__").status_code == 400


def test_name_api_carries_meaning_and_confidence_fields():
    r = client.get(f"/api/pub/name/chars?surname=王&{NAME_Q}&given=__&slot=0&py=yun&el=all").json()
    t = {x["ch"]: x for x in r["tiles"]}
    assert t["晕"]["blocked"] is True and t["晕"]["why"]
    s = client.get(f"/api/pub/name/score?surname=王&given=禄晕&{NAME_Q}").json()
    assert s["warnings"] and s["warnings"][0]["ch"] == "晕"
    assert all("conf" in c for c in s["chars"])
    d = client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=_婷").json()
    assert "晕" not in "".join(x["given"] for x in d["results"])


def test_name_api_meaning_and_five_part_score():
    ch = client.get(f"/api/pub/name/chart?{NAME_Q}&surname=王").json()
    assert len(ch["categories"]) == 16
    r = client.get(f"/api/pub/name/chars?surname=王&{NAME_Q}&given=__&slot=0&mean=zhi").json()
    assert r["tiles"] and all("zhi" in t["tags"] for t in r["tiles"]) and r["meaning"] == "zhi"
    assert client.get(f"/api/pub/name/chars?surname=王&{NAME_Q}&given=__&slot=0&mean=nope").status_code == 400
    o = client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=__&mean=zhi,mei").json()
    assert o["results"] and all("zhi" in x["chars"][0]["tags"] and "mei" in x["chars"][1]["tags"] for x in o["results"])
    assert client.get(f"/api/pub/name/optimise?surname=王&{NAME_Q}&given=__&mean=nope,_").status_code == 400
    s = client.get(f"/api/pub/name/score?surname=王&given=禄婷&{NAME_Q}").json()
    assert set(s["score"]["parts"]) == {"yongshen", "wuge", "sancai", "meaning", "sound", "gender", "confidence"}
    assert s["score"]["notes"]["sound"] == "tones 2-4-2, no clashes" and s["sound"]["score"] == 1.0
    assert s["interpretation"]["zh"] and s["score"]["grade"]["en"] and s["score"]["notes"]["gender"] == "both suit a girl"
    boy = NAME_Q.replace("sex=F", "sex=M")
    b = client.get(f"/api/pub/name/chars?surname=王&{boy}&given=__&slot=0").json()
    assert b["tiles"] and not any(t["gender"] == "F" for t in b["tiles"])
    assert client.get(f"/api/pub/name/score?surname=王&given=禄婷&{boy}").json()["score"]["parts"]["gender"] == 2.5
    cert = client.get(f"/api/pub/certificate?surname=王&given=禄婷&{NAME_Q}").text
    assert "既福禄双全，又亭亭玉立" in cert
    assert s["sancai"]["detail"][0]["text"] and s["chars"][1]["gloss"]
