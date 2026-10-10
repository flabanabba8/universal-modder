#!/usr/bin/env python3
"""CC0 PBR material finder/downloader (ambientCG API v3, Poly Haven public API). Stdlib only.

  cc0_materials.py ambientcg search "<words>" [--limit 10]
  cc0_materials.py ambientcg get <AssetId> [--res 2K] [--fmt JPG|PNG] [--out DIR]
  cc0_materials.py polyhaven search "<words>" [--limit 10]
  cc0_materials.py polyhaven get <asset_id> [--res 2k] [--maps Diffuse,nor_gl,arm,Displacement] [--fmt jpg|png] [--out DIR]

Rules: one request at a time with a 2 s pause; Poly Haven requires a unique User-Agent naming the software (used below); both sites'
assets are CC0 (no credit needed); building on the LIVE Poly Haven API needs a "Powered by Poly Haven" credit in the product, not in the game assets.
Searching only reads metadata. `get` downloads files, so run it only when a material is actually needed.
"""
import argparse, json, pathlib, sys, time, urllib.parse, urllib.request
UA = "universal-modder-wiki-cc0-fetch/1.0 (local game-modding tool)"
def get(url, raw=False):
    time.sleep(2)
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120)
    return r.read() if raw else json.load(r)
def save(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists(): print("exists", dest); return
    dest.write_bytes(get(url, raw=True)); print("saved", dest, dest.stat().st_size)
def amb_search(a):
    d = get("https://ambientCG.com/api/v3/assets?" + urllib.parse.urlencode({"type": "material", "q": a.q, "limit": a.limit, "sort": "popular"}))
    print(d.get("totalResults"), "results")
    for x in d["assets"]: print(x["id"])
def amb_get(a):
    d = get("https://ambientCG.com/api/v3/assets?" + urllib.parse.urlencode({"id": a.id, "include": "downloads"}))
    want = f"{a.res}-{a.fmt}".upper()
    for dl in d["assets"][0]["downloads"]:
        if dl["attributes"].upper() == want:
            save(dl["url"], pathlib.Path(a.out) / f"{a.id}_{want}.zip"); return
    sys.exit("no such variant; have: " + ", ".join(x["attributes"] for x in d["assets"][0]["downloads"]))
def ph_search(a):
    d = get("https://api.polyhaven.com/assets?t=textures")
    q = a.q.lower().split()
    hits = [(k, v) for k, v in d.items() if all(w in (k + " " + v["name"] + " " + " ".join(v["tags"] + v["categories"])).lower() for w in q)]
    print(len(hits), "of", len(d), "textures")
    for k, v in hits[:a.limit]: print(k, "|", v["name"], "|", ",".join(v["categories"]), "| max", v["max_resolution"])
def ph_get(a):
    files = get(f"https://api.polyhaven.com/files/{a.id}")
    for m in a.maps.split(","):
        try: f = files[m][a.res][a.fmt]
        except KeyError: print("missing", m, a.res, a.fmt, "have", list(files)); continue
        save(f["url"], pathlib.Path(a.out) / a.id / pathlib.Path(f["url"]).name)
p = argparse.ArgumentParser(); s = p.add_subparsers(dest="site", required=True)
for site, sf, gf in (("ambientcg", amb_search, amb_get), ("polyhaven", ph_search, ph_get)):
    sp = s.add_parser(site).add_subparsers(dest="cmd", required=True)
    q = sp.add_parser("search"); q.add_argument("q"); q.add_argument("--limit", type=int, default=10); q.set_defaults(f=sf)
    g = sp.add_parser("get"); g.add_argument("id"); g.add_argument("--out", default="assets/materials"); g.set_defaults(f=gf)
    if site == "ambientcg": g.add_argument("--res", default="2K"); g.add_argument("--fmt", default="JPG")
    else: g.add_argument("--res", default="2k"); g.add_argument("--fmt", default="jpg"); g.add_argument("--maps", default="Diffuse,nor_gl,arm,Displacement")
a = p.parse_args(); a.f(a)
