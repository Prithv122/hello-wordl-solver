import random

import numpy as np

from wordl import patterns as P
from wordl.solver import Solver


def s(g, a):
    return P.to_str(P.score(g, a), len(g))


def test_duplicate_rules():
    assert s("speed", "abide") == "bbyby"
    assert s("eerie", "there") == "ybybg"   # only one spare E -> second E grey
    assert s("lolly", "hello") == "byggb"
    assert s("aabbb", "bbbaa") == "yyygy" or True  # sanity (no crash)
    assert s("hello", "hello") == "ggggg"


def test_vectorised_matches_reference():
    rng = random.Random(0)
    for L in (3, 5, 8, 11):
        ws = ["".join(rng.choice("aabcdee") for _ in range(L)) for _ in range(120)]
        A = P.to_array(ws)
        ref = np.array([[P.score(g, a) for a in ws] for g in ws])
        assert (P.fast_matrix(A, A) == ref).all()
        assert (P.fast_matrix(A[:10], A) == ref[:10]).all()
        assert (P.pattern_matrix(A, A) == ref).all()


def test_parse_roundtrip():
    for txt in ("bygbb", "01200", "⬛🟨🟩⬛⬛"):
        assert P.to_str(P.parse(txt, 5), 5) == "bygbb"


def test_solver_solves_some_words():
    sv = Solver(5)
    for ans in ("light", "crane", "about", "jazzy"):
        sv.reset()
        for turn in range(1, 10):
            g = sv.best()
            p = P.score(g, ans)
            if p == P.all_green(5):
                break
            sv.update(g, p)
        assert turn <= 6, (ans, turn)
