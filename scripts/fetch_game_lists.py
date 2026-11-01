"""Download Hello Wordl's public word lists (MIT, github.com/lynn/hello-wordl)
into data/external/ (git-ignored, not redistributed):

  dictionary.json  every word the game accepts. Used as a FILTER: words from
                   our own files that the game would never accept (names like
                   JAMEL / PATEL, abbreviations, junk) are removed.
  targets.json     the answer pool, used only by scripts/calibrate.py.

    python scripts/fetch_game_lists.py
"""
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "data", "external")
BASE = "https://raw.githubusercontent.com/lynn/hello-wordl/main/src/"


def fetch(name: str) -> str:
    os.makedirs(EXT, exist_ok=True)
    path = os.path.join(EXT, name)
    if not os.path.exists(path):
        with urllib.request.urlopen(BASE + name, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


if __name__ == "__main__":
    for n in ("dictionary.json", "targets.json"):
        print(fetch(n))
