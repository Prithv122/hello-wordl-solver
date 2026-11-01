"""Export word lists + openers + opening books for the web app (docs/).

    python scripts/export_web.py

Each length becomes docs/data/len_XX.js (a plain <script>, so the page also
works when opened straight from disk with file://).
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wordl.lexicon import ROOT, load  # noqa: E402
from wordl.solver import JUNK_TAX, TIER_TAX, load_openers  # noqa: E402

OUT = os.path.join(ROOT, "docs", "data")


def main():
    os.makedirs(OUT, exist_ok=True)
    openers = load_openers()
    for L in range(4, 12):
        lx = load(L)
        groups = defaultdict(list)
        cls_info = {}
        for i, (w, c) in enumerate(zip(lx.words, lx.classes)):
            groups[c].append(w)
            if c not in cls_info:
                g = lx.is_guess(i)
                tax = 0.0 if lx.is_common(i) else TIER_TAX[lx.tiers[i]]
                if not g:
                    tax = JUNK_TAX
                cls_info[c] = {"w": lx.weights[i], "g": int(g), "t": tax}
        book_path = os.path.join(ROOT, "output", "opening_book", f"len_{L:02d}.json")
        book = json.load(open(book_path)) if os.path.exists(book_path) else None
        if book:  # slim it down: top 3 per pattern
            book = {"opener": book["opener"],
                    "p": {k: [[b["word"], b["expected_guesses"], b["entropy_bits"], b["p_win"]]
                              for b in v["best"][:3]] for k, v in book["patterns"].items()}}
        op = [[o["word"], o["expected_guesses"], o["entropy_bits"], o["p_win"]]
              for o in openers.get(str(L), {}).get("normal", [])[:10]]
        data = {"L": L, "classes": cls_info, "groups": {c: "".join(ws) for c, ws in groups.items()},
                "openers": op, "book": book}
        with open(os.path.join(OUT, f"len_{L:02d}.js"), "w") as f:
            f.write(f"window.WORDL_DATA=window.WORDL_DATA||{{}};WORDL_DATA[{L}]=")
            json.dump(data, f, separators=(",", ":"))
            f.write(";\n")
        print(L, len(lx.words), os.path.getsize(os.path.join(OUT, f"len_{L:02d}.js")) // 1024, "KB")


if __name__ == "__main__":
    main()
