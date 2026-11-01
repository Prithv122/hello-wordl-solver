"""Tune CANDIDATE_MARGIN on the TRAIN half of real answers.
How much worse (in expected guesses) may a possible answer be than the best
probe word and still be preferred?   python scripts/tune_margin.py 4 5 6
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tune import train_answers  # noqa: E402
from wordl.analysis import best_openers  # noqa: E402
from wordl.book import build_book  # noqa: E402
from wordl.simulate import simulate  # noqa: E402
from wordl.solver import Solver  # noqa: E402


def run(args):
    L, m = args
    s = Solver(L, use_book=False, candidate_margin=m)
    known = set(s.words)
    ans = [w for w in train_answers(L) if w in known]
    op = best_openers(s, 1)[0]["word"]
    book = build_book(L, op, candidate_margin=m)
    r = simulate(L, 10 ** 6, opener=op, book=book, answers=ans, candidate_margin=m)
    return L, m, r["avg_guesses"], r["win_rate"], r["games"]


if __name__ == "__main__":
    lengths = [int(x) for x in sys.argv[1:]] or [4, 5]
    grid = [(L, m) for L in lengths for m in (0.0, 0.1, 0.2, 0.35, 0.5)]
    with ProcessPoolExecutor(4) as ex:
        for L, m, avg, win, n in ex.map(run, grid):
            print(f"len {L} margin {m:4.2f}  avg {avg:.3f}  win {win:.4f}  ({n} games)", flush=True)
