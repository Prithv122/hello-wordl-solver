"""Tune prior_power and fail_penalty on the TRAIN half of real answers
(the test half in data/benchmark_answers.json is never used here).

    python scripts/tune.py 4 5
"""
import itertools
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wordl.analysis import best_openers  # noqa: E402
from wordl.book import build_book  # noqa: E402
from wordl.simulate import simulate  # noqa: E402
from wordl.solver import Solver  # noqa: E402

TARGETS = "/tmp/hello_wordl_targets.json"


def train_answers(L):
    t = json.load(open(TARGETS))
    t = t[: t.index("murky") + 1]
    return [w for w in t[0::2] if len(w) == L and w.isalpha()]


def run(args):
    L, power, pen, n = args
    s = Solver(L, use_book=False, prior_power=power, fail_penalty=pen)
    known = set(s.words)
    ans = [w for w in train_answers(L) if w in known][:n]
    op = best_openers(s, 1)[0]["word"]
    book = build_book(L, op, prior_power=power, fail_penalty=pen)
    r = simulate(L, opener=op, book=book, answers=ans, prior_power=power, fail_penalty=pen)
    return L, power, pen, op, r["avg_guesses"], r["win_rate"]


if __name__ == "__main__":
    lengths = [int(x) for x in sys.argv[1:]] or [4, 5]
    grid = [(L, p, f, 400) for L in lengths for p, f in itertools.product((1.0, 0.75, 0.5), (6.0, 20.0))]
    with ProcessPoolExecutor(4) as ex:
        for L, p, f, op, avg, win in ex.map(run, grid):
            print(f"len {L} power {p:4.2f} penalty {f:4.1f} opener {op.upper():8s} avg {avg:.3f} win {win:.4f}",
                  flush=True)
