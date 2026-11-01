"""Calibrate the answer prior against Hello Wordl's public answer list.

    python scripts/calibrate.py            # downloads the list from GitHub

Hello Wordl (MIT, github.com/lynn/hello-wordl) picks answers from
src/targets.json - a frequency-ordered list - keeping words "no rarer than
'murky'". We split those answers in two halves (even / odd positions):

  * TRAIN half -> P(answer | word class, length) = the class weights
                  -> data/prior_calibration.json
  * TEST  half -> data/benchmark_answers.json, used ONLY to measure the solver

Only aggregate rates are stored (a few dozen numbers); the game's lists are
not redistributed. Classes are coarse (8 per length) so overfitting is nil.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.fetch_game_lists import fetch as fetch_list  # noqa: E402
from wordl import lexicon  # noqa: E402


def fetch():
    fetch_list("dictionary.json")
    t = json.load(open(fetch_list("targets.json")))
    t = t[: t.index("murky") + 1]
    return [w for w in t if w.isalpha() and 4 <= len(w) <= 11]


def main():
    targets = fetch()
    train = set(targets[0::2])
    test = targets[1::2]
    # classes without calibration (weights irrelevant here)
    if os.path.exists(lexicon.CALIB_FILE):
        os.remove(lexicon.CALIB_FILE)
    by_len = lexicon.build()
    calib, report = {}, {}
    # pooled over lengths first, then each length shrunk toward the pool
    # (empirical-Bayes: rate = (hits + K * pooled) / (count + K))
    K = 40
    ptot, phit = Counter(), Counter()
    for L in range(4, 12):
        for w, c, _, _ in by_len[L]:
            ptot[c] += 1
            phit[c] += w in train
    g = sum(phit.values()) / sum(ptot.values())
    pooled = {c: (phit[c] + K * g) / (ptot[c] + K) for c in ptot}
    calib["all"] = {c: round(v, 6) for c, v in sorted(pooled.items())}
    for L in range(4, 12):
        rows = by_len[L]
        tot = Counter(c for _, c, _, _ in rows)
        hit = Counter(c for w, c, _, _ in rows if w in train)
        calib[str(L)] = {c: round((hit[c] + K * pooled[c]) / (tot[c] + K), 6) for c in sorted(tot)}
        n_test = [w for w in test if len(w) == L]
        known = {w for w, _, _, _ in rows}
        report[L] = {"train_answers": sum(1 for w in train if len(w) == L),
                     "test_answers": len(n_test),
                     "test_coverage": round(sum(w in known for w in n_test) / max(len(n_test), 1), 4),
                     "rates": calib[str(L)]}
        print(L, {k: v for k, v in report[L].items() if k != "rates"}, flush=True)
    print("pooled P(answer | class):")
    for c, v in sorted(pooled.items()):
        print(f"   {c:7s} n={ptot[c]:7d}  {v:.4f}")
    with open(lexicon.CALIB_FILE, "w") as f:
        json.dump(calib, f, indent=1)
    with open(os.path.join(lexicon.ROOT, "data", "benchmark_answers.json"), "w") as f:
        json.dump({str(L): [w for w in test if len(w) == L] for L in range(4, 12)}, f)
    with open(os.path.join(lexicon.ROOT, "output", "calibration_report.json"), "w") as f:
        json.dump(report, f, indent=1)
    lexicon.save(lexicon.build())


if __name__ == "__main__":
    main()
