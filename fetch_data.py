#!/usr/bin/env python3
"""Deterministic data fetcher — download + md5-verify the public inputs into data_sources/.

Idempotent: a file already present with the correct md5 is skipped. Files are resolved through the figshare
API by (article id, version, filename) — the *versioned* endpoint, so a future figshare version cannot
silently change what we download — then verified against a hard-pinned md5 before being moved into place.
Every source is pinned; a file that fails verification is never left at its canonical path.

Run on a machine with network access:  python fetch_data.py [--data DIR] [--only KEY ...]
This is a download utility; it is not exercised in CI.
"""
import argparse, hashlib, os, sys
import urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import default_data_dir, safe_stdout
safe_stdout()

FIGSHARE_API = "https://api.figshare.com/v2"
# figshare serves file bodies from its downloader host; refuse anything else (see _checked_url).
ALLOWED_DOWNLOAD_HOSTS = {"ndownloader.figshare.com", "ndownloader.figsh.com"}

# (article_id, version) pins the figshare record; filename picks the file; md5+size are the hard guard.
# All three md5s were verified against the versioned figshare records on 2026-08-11.
SOURCES = {
    "prism_19q4": dict(
        article_id=9393293, version=4,           # PRISM Repurposing 19Q4 (doi:10.6084/m9.figshare.9393293.v4)
        filename="secondary-screen-dose-response-curve-parameters.csv",
        md5="e629b9d505ad3d6bf65fde96f1c54bee", size=264340589, required=True),
    "depmap_24q2_mutations": dict(
        article_id=25880521, version=1,          # DepMap 24Q2 Public (doi:10.25452/figshare.plus.25880521.v1)
        filename="OmicsSomaticMutationsMatrixDamaging.csv",
        md5="02f3568b71af0ca3e8d10e681eefac86", size=135585447, required=True),
    "demeter2_rnai": dict(
        article_id=6025238, version=6,           # DEMETER2 data v6 (doi:10.6084/m9.figshare.6025238.v6)
        filename="D2_combined_gene_dep_scores.csv",
        md5="e82566a48993753c20ea5f480f1867ec", size=160616970, required=False),
}

def md5sum(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def _checked_url(url):
    """The download URL comes out of the API response — constrain it before we fetch it."""
    p = urllib.parse.urlparse(url)
    if p.scheme != "https":
        raise RuntimeError(f"refusing non-https download URL: {url}")
    host = p.netloc.lower().rsplit("@", 1)[-1].split(":")[0]
    if host not in ALLOWED_DOWNLOAD_HOSTS and not host.endswith(".figshare.com"):
        raise RuntimeError(f"refusing download from unexpected host {host!r}: {url}")
    return url

def resolve_and_download(s, dest):
    """Download to dest.part, verify md5+size there, and only then move it into place."""
    import requests
    aid, ver, filename = s["article_id"], s["version"], s["filename"]
    r = requests.get(f"{FIGSHARE_API}/articles/{aid}/versions/{ver}", timeout=60)
    r.raise_for_status()
    files = r.json().get("files", [])
    match = next((f for f in files if f.get("name") == filename), None)
    if not match:
        raise RuntimeError(f"'{filename}' not found in figshare article {aid} v{ver}. "
                           f"Available: {[f.get('name') for f in files][:8]} ... — "
                           f"download manually per DOWNLOAD_CHECKLIST.md")
    url = _checked_url(match["download_url"])
    print(f"    downloading {filename} ({match.get('size', '?')} bytes) ...")
    tmp = dest + ".part"
    h = hashlib.md5(); n = 0
    with requests.get(url, stream=True, timeout=600) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as out:
            for chunk in resp.iter_content(1 << 20):
                out.write(chunk); h.update(chunk); n += len(chunk)
    got = h.hexdigest()
    if got != s["md5"] or (s.get("size") and n != s["size"]):
        os.replace(tmp, dest + ".bad")
        raise RuntimeError(f"verification FAILED (got md5 {got}, {n} bytes; expected {s['md5']}, "
                           f"{s.get('size')} bytes). Quarantined at {dest}.bad — {dest} not written.")
    os.replace(tmp, dest)
    return got

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", default=default_data_dir(here))
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
            if got == s["md5"]:
                print("    present, md5 OK — skip"); continue
            print(f"    present but md5 {got} != expected {s['md5']} — re-downloading")
        try:
            got = resolve_and_download(s, dest)
        except Exception as e:
            print(f"    ERROR: {e}")
            rc = max(rc, 2 if s["required"] else 1)
            continue
        print(f"    OK  md5={got}")
    print("\nDone." if rc == 0 else f"\nDone with errors (exit {rc}).")
    sys.exit(rc)

if __name__ == "__main__":
    main()
