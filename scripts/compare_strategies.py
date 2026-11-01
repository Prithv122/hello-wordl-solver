"""Compare simple human strategies with the solver on held-out real answers.

    python scripts/compare_strategies.py            # lengths 4-11

Human strategy "frequency pair, then guess":
  turn 1  the word whose (distinct) letters are most common
  turn 2  if turn 1 revealed >= THRESHOLD letters (green or yellow) start
          guessing; otherwise play the second word: the most common NEW letters
  after   always guess the most common word that still fits

Tested with THRESHOLD = 2 and 3, plus "always play both words" and
"guess from turn 2". Writes output/strategy_comparison.json / .md
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wordl import patterns as P  # noqa: E402
from wordl.lexicon import ROOT  # noqa: E402
from wordl.simulate import benchmark_answers  # noqa: E402
from wordl.solver import Solver  # noqa: E402


def frequency_pair(s: Solver) -> tuple[str, str]:
    p = s.w / s.w.sum()
    C = P.letter_counts(s.A) > 0
    pres = p @ C                                   # P(letter in answer)
    pool = np.nonzero(s.is_common & s.is_guess)[0]
    distinct = P.letter_counts(s.A[pool]).max(1) == 1
    pool = pool[distinct] if distinct.any() else pool
    sc1 = C[pool] @ pres
    w1 = pool[int(np.argmax(sc1))]
    used = C[w1]
    sc2 = C[pool] @ (pres * ~used) - 2 * (C[pool] @ (pres * used))   # new letters only
    w2 = pool[int(np.argmax(sc2))]
    return s.words[w1], s.words[w2]


def hits(pattern: int, L: int) -> int:
    return sum(d > 0 for d in P.decode(pattern, L))


def common_letters_candidate(s: Solver) -> str:
    """A word that still fits every clue (keeps greens, moves yellows) and
    whose UNTESTED letters are the most common among the remaining words."""
    cand = s.cand
    wc = s.w[cand] / s.w[cand].sum()
    C = P.letter_counts(s.A[cand]) > 0
    f = wc @ C                                       # P(letter in answer | clues)
    tested = np.zeros(26, bool)
    for g, _ in s.history:
        tested[[ord(ch) - 97 for ch in g]] = True
    score = C @ (f * ~tested)                        # common NEW letters
    best = np.lexsort((-wc, -np.round(score, 6)))[0]  # tie -> more common word
    return s.words[cand[best]]


def play_human(s: Solver, answer: str, w1: str, w2: str, threshold: int | None,
               mode: str = "common_word") -> int:
    """threshold None = always play both words; 0 = start guessing at turn 2.
    mode: common_word = guess the most common fitting word;
          common_letters = guess the fitting word with the most common new letters."""
    s.reset()
    win = P.all_green(s.L)
    for turn in range(1, 30):
        if turn == 1:
            g = w1
        elif turn == 2 and threshold is None:
            g = w2
        elif turn == 2 and threshold and hits(s.history[0][1], s.L) < threshold:
            g = w2
        elif mode == "common_letters" and len(s.cand) > 2:
            g = common_letters_candidate(s)
        else:
            g = s.candidates(1)[0][0]               # most common word that fits
        p = P.score(g, answer)
        if p == win:
            return turn
        s.update(g, p)
    return 99


def run(L: int) -> dict:
    s = Solver(L, use_book=False)
    answers, source = benchmark_answers(L, s)
    w1, w2 = frequency_pair(s)
    out = {"length": L, "games": len(answers), "first": w1, "second": w2, "strategies": {}}
    for name, th, mode in (
            ("pair, guess if 2+ revealed", 2, "common_word"),
            ("pair, guess if 3+ revealed", 3, "common_word"),
            ("always play both words", None, "common_word"),
            ("one word, then guess", 0, "common_word"),
            ("pair if <2 revealed, then keep-hits + common letters", 2, "common_letters"),
            ("one word, then keep-hits + common letters", 0, "common_letters")):
        dist = Counter(play_human(s, a, w1, w2, th, mode) for a in answers)
        n = sum(dist.values())
        out["strategies"][name] = {
            "avg_guesses": round(sum(k * v for k, v in dist.items()) / n, 3),
            "win_rate": round(sum(v for k, v in dist.items() if k <= 6) / n, 4),
            "distribution": {int(k): v for k, v in sorted(dist.items())},
        }
    return out


def main():
    lengths = [int(x) for x in sys.argv[1:]] or list(range(4, 12))
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(run, lengths))
    bench_path = os.path.join(ROOT, "output", "benchmark.json")
    bench = json.load(open(bench_path)) if os.path.exists(bench_path) else {}
    for r in res:
        b = bench.get(str(r["length"]), {}).get("common_answers")
        if b:
            r["strategies"]["SOLVER (information)"] = {k: b[k] for k in ("avg_guesses", "win_rate", "distribution")}
    with open(os.path.join(ROOT, "output", "strategy_comparison.json"), "w") as f:
        json.dump(res, f, indent=1)
    names = list(res[0]["strategies"])
    lines = ["| letters | frequency pair | " + " | ".join(names) + " |",
             "|---|---|" + "---|" * len(names)]
    for r in res:
        cells = []
        for n in names:
            x = r["strategies"].get(n)
            cells.append(f"{x['avg_guesses']:.2f} · {x['win_rate'] * 100:.1f}%" if x else "-")
        lines.append(f"| {r['length']} | {r['first'].upper()} + {r['second'].upper()} | " + " | ".join(cells) + " |")
    md = "\n".join(lines)
    with open(os.path.join(ROOT, "output", "strategy_comparison.md"), "w") as f:
        f.write("Average guesses · win rate (6 tries), held-out real Hello Wordl answers\n\n" + md + "\n")
    print(md)


if __name__ == "__main__":
    main()
