"""Regenerate every output file:

    python scripts/build_all.py              # lengths 4-11 (Hello Wordl's range)
    python scripts/build_all.py 5 6          # just some lengths
    python scripts/build_all.py --games 500  # bigger benchmark

Writes:
    data/lexicon/len_XX.tsv          word lists with tier + prior weight
    output/openers.json              ranked best first guesses per length
    output/opening_book/len_XX.json  best 2nd guess for each first feedback
    output/analysis/len_XX.json      all statistics used by the guide
    output/benchmark.json            simulated performance
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wordl import analysis as An  # noqa: E402
from wordl import lexicon  # noqa: E402
from wordl.book import build_book, save_book  # noqa: E402
from wordl.simulate import simulate  # noqa: E402
from wordl.solver import OPENERS_FILE, Solver  # noqa: E402

OUT = os.path.join(lexicon.ROOT, "output")


def work(L: int, games: int) -> dict:
    t0 = time.time()
    s = Solver(L, use_book=False)
    log = lambda m: print(f"[len {L:2d} {time.time() - t0:6.1f}s] {m}", flush=True)  # noqa: E731
    res = {"length": L, "n_words": len(s.words),
           "tiers": {t: s.lex.tiers.count(t) for t in "ABCD"},
           "n_common": int(s.is_common.sum()),
           "n_guess_pool": int(s.is_guess.sum())}
    res["letters"] = An.letter_stats(s); log("letter stats")
    res["openers"] = An.best_openers(s, 25); log(f"openers -> {res['openers'][0]['word']}")
    res["common_openers"] = An.common_openers(s, 10); log("common openers")
    best = res["openers"][0]["word"]
    firsts = [o["word"] for o in res["openers"][:4]] + [o["word"] for o in res["common_openers"][:4]]
    res["pairs"] = An.best_pairs(s, list(dict.fromkeys(firsts))); log("pairs")
    res["traps"], res["trap_share"] = An.trap_families(s); log("traps")
    res["first_feedback"] = An.first_feedback_signals(s, best); log("signals")
    book = build_book(L, best); save_book(book)
    res["book_patterns"] = len(book["patterns"]); res["book_coverage"] = book["coverage"]
    log(f"book: {len(book['patterns'])} patterns, coverage {book['coverage']}")
    res["benchmark"] = simulate(L, games, opener=best, book=book)
    res["benchmark_hard"] = simulate(L, games, opener=best, hard=True)
    log(f"benchmark avg {res['benchmark']['avg_guesses']} "
        f"(hard mode {res['benchmark_hard']['avg_guesses']})")
    res["seconds"] = round(time.time() - t0, 1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lengths", nargs="*", type=int, default=list(range(4, 12)))
    ap.add_argument("--games", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()

    lexicon.save(lexicon.build())
    os.makedirs(os.path.join(OUT, "analysis"), exist_ok=True)
    order = sorted(a.lengths, key=lambda L: -abs(L - 8.5))  # slow lengths first
    with ProcessPoolExecutor(a.jobs) as ex:
        results = list(ex.map(work, order, [a.games] * len(order)))

    openers = json.load(open(OPENERS_FILE)) if os.path.exists(OPENERS_FILE) else {}
    bench = json.load(open(os.path.join(OUT, "benchmark.json"))) \
        if os.path.exists(os.path.join(OUT, "benchmark.json")) else {}
    for r in sorted(results, key=lambda r: r["length"]):
        L = r["length"]
        openers[str(L)] = {"normal": r["openers"], "hard": r["openers"]}
        bench[str(L)] = {"common_answers": r["benchmark"], "hard_mode": r["benchmark_hard"]}
        with open(os.path.join(OUT, "analysis", f"len_{L:02d}.json"), "w") as f:
            json.dump(r, f, indent=1)
    with open(OPENERS_FILE, "w") as f:
        json.dump(dict(sorted(openers.items(), key=lambda kv: int(kv[0]))), f, indent=1)
    with open(os.path.join(OUT, "benchmark.json"), "w") as f:
        json.dump(dict(sorted(bench.items(), key=lambda kv: int(kv[0]))), f, indent=1)
    print("done")


if __name__ == "__main__":
    main()
