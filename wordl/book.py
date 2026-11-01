"""Opening book: precomputed best SECOND guess for every likely feedback to
the best opener -> answers are instant on turns 1 and 2."""
from __future__ import annotations

import json
import os

import numpy as np

from . import patterns as P
from .solver import BOOK_DIR, Solver


def build_book(L: int, opener: str, mass: float = 0.995, max_patterns: int = 600,
               top: int = 5, **solver_kw) -> dict:
    s = Solver(L, use_book=False, **solver_kw)
    g = P.to_array([opener])[0]
    pats = P.patterns_one(g, s.A, P.letter_counts(s.A))
    wc = s.w / s.w.sum()
    pm = np.bincount(pats, weights=wc, minlength=3 ** L)
    order = np.argsort(-pm)
    book, covered = {}, 0.0
    for p in order[:max_patterns]:
        if pm[p] <= 0 or covered >= mass:
            break
        covered += pm[p]
        if p == P.all_green(L):
            continue
        s.reset()
        s.update(opener, int(p))
        book[P.to_str(int(p), L)] = {
            "prob": round(float(pm[p]), 5),
            "left": int(len(s.cand)),
            "best": s.rank(top),
        }
    return {"length": L, "opener": opener, "coverage": round(covered, 4), "patterns": book}


def save_book(book: dict):
    os.makedirs(BOOK_DIR, exist_ok=True)
    with open(os.path.join(BOOK_DIR, f"len_{book['length']:02d}.json"), "w") as f:
        json.dump(book, f, separators=(",", ":"))


_cache: dict = {}


def lookup(L: int, opener: str, pattern: int):
    if L not in _cache:
        path = os.path.join(BOOK_DIR, f"len_{L:02d}.json")
        _cache[L] = json.load(open(path)) if os.path.exists(path) else None
    b = _cache[L]
    if not b or b["opener"] != opener:
        return None
    e = b["patterns"].get(P.to_str(pattern, L))
    return e["best"] if e else None
