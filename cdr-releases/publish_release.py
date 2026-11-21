"""Publish a new version:  python publish_release.py 1.0.1 CDR_Converter.exe "Fixed Jazz dates" [--mandatory]
Needs env vars: API_URL (Render url), ADMIN_TOKEN, and either --url or GitHub CLI (gh) + RELEASES_REPO (e.g. nisar/cdr-releases).
"""
import argparse, hashlib, json, os, subprocess, sys, urllib.request
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("version"); p.add_argument("exe"); p.add_argument("notes", nargs="?", default="")
p.add_argument("--mandatory", action="store_true")
p.add_argument("--url", help="direct download link, if you already uploaded the exe yourself")
a = p.parse_args()

exe = Path(a.exe)
sha = hashlib.sha256(exe.read_bytes()).hexdigest()
url = a.url
if not url:
    repo = os.environ["RELEASES_REPO"]
    subprocess.run(["gh", "release", "create", f"v{a.version}", str(exe), "--repo", repo,
                    "--title", f"v{a.version}", "--notes", a.notes or f"Version {a.version}"], check=True)
    url = f"https://github.com/{repo}/releases/download/v{a.version}/{exe.name}"

req = urllib.request.Request(os.environ["API_URL"].rstrip("/") + "/admin/version", method="POST",
    data=json.dumps({"version": a.version, "download_url": url, "sha256": sha, "notes": a.notes, "mandatory": a.mandatory}).encode(),
    headers={"Content-Type": "application/json", "X-Admin-Token": os.environ["ADMIN_TOKEN"]})
print(urllib.request.urlopen(req, timeout=60).read().decode(), "\n", url, "\n", sha)
