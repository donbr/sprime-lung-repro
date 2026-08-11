#!/usr/bin/env python3
"""Deterministic data fetcher — download + md5-verify the public inputs into data_sources/.

Idempotent: a file already present with the correct md5 is skipped. Files are resolved through the figshare
API by article id + filename (so we do not hard-code fragile CDN URLs), then verified against a pinned md5
(PRISM, DepMap 24Q2) or against figshare's own computed_md5 (DEMETER2, whose md5 is not pre-pinned here).

Run on a machine with network access:  python fetch_data.py [--data DIR] [--only KEY ...]
This is a download utility; it is not exercised in CI.
"""
import argparse, hashlib, os, sys

FIGSHARE_API = "https://api.figshare.com/v2"

# article_id resolves the figshare record; filename picks the file; md5 (if set) is the hard guard.
SOURCES = {
    "prism_19q4": dict(
        article_id=11384241,                     # DepMap 19Q4 Public (doi:10.6084/m9.figshare.11384241.v2)
        filename="secondary-screen-dose-response-curve-parameters.csv",
        md5="e629b9d505ad3d6bf65fde96f1c54bee", required=True),
    "depmap_24q2_mutations": dict(
        article_id=25880521,                     # DepMap Public 24Q2 (doi:10.25452/figshare.plus.25880521.v1)
        filename="OmicsSomaticMutationsMatrixDamaging.csv",
        md5="02f3568b71af0ca3e8d10e681eefac86", required=True),
    "demeter2_rnai": dict(
        article_id=9201770,                      # DEMETER2 Data v6 (doi:10.6084/m9.figshare.9201770)
        filename="D2_combined_gene_dep_scores.csv",
        md5=None, required=False),               # md5 not pre-pinned; verified vs figshare computed_md5, then printed to pin
}

def md5sum(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def resolve_and_download(article_id, filename, dest):
    import requests
    r = requests.get(f"{FIGSHARE_API}/articles/{article_id}/files", timeout=60)
    r.raise_for_status()
    files = r.json()
    match = next((f for f in files if f.get("name") == filename), None)
    if not match:
        raise RuntimeError(f"'{filename}' not found in figshare article {article_id}. "
                           f"Available: {[f.get('name') for f in files][:8]} ... — "
                           f"download manually per DOWNLOAD_CHECKLIST.md")
    url = match["download_url"]; api_md5 = match.get("computed_md5")
    print(f"    downloading {filename} ({match.get('size', '?')} bytes) ...")
    with requests.get(url, stream=True, timeout=600) as resp:
        resp.raise_for_status()
        tmp = dest + ".part"
        with open(tmp, "wb") as out:
            for chunk in resp.iter_content(1 << 20):
                out.write(chunk)
        os.replace(tmp, dest)
    return api_md5

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", default=os.path.join(here, "data_sources"))
    ap.add_argument("--only", nargs="*", choices=list(SOURCES), help="fetch only these keys")
    a = ap.parse_args()
    os.makedirs(a.data, exist_ok=True)
    keys = a.only or list(SOURCES)
    rc = 0
    for k in keys:
        s = SOURCES[k]; dest = os.path.join(a.data, s["filename"])
        print(f"[{k}] -> {dest}")
        if os.path.exists(dest):
            got = md5sum(dest)
            if s["md5"] and got == s["md5"]:
                print("    present, md5 OK — skip"); continue
            if s["md5"] is None:
                print(f"    present (md5 {got}) — skip (no pinned md5)"); continue
            print(f"    present but md5 {got} != expected {s['md5']} — re-downloading")
        try:
            api_md5 = resolve_and_download(s["article_id"], s["filename"], dest)
        except Exception as e:
            print(f"    ERROR: {e}")
            if s["required"]: rc = 2
            continue
        got = md5sum(dest)
        if s["md5"] and got != s["md5"]:
            print(f"    md5 MISMATCH: got {got}, expected {s['md5']} — WRONG FILE/RELEASE"); rc = 3
        elif api_md5 and got != api_md5:
            print(f"    md5 mismatch vs figshare ({got} != {api_md5}) — download may be corrupt"); rc = 3
        else:
            print(f"    OK  md5={got}" + ("  <-- pin this in SOURCES/DOWNLOAD_CHECKLIST" if s["md5"] is None else ""))
    print("\nDone." if rc == 0 else f"\nDone with errors (exit {rc}).")
    sys.exit(rc)

if __name__ == "__main__":
    main()
