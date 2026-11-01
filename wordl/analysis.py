"""Statistics that drive the strategy guide: letter probabilities, best
openers, best fixed opening pairs, "trap" families, and what the first
feedback tells you."""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np

from . import patterns as P
from .solver import Solver

VOWELS = set("aeiou")


def prior(s: Solver):
    return s.w / s.w.sum()


def letter_stats(s: Solver) -> dict:
    p = prior(s)
    pres = p @ (P.letter_counts(s.A) > 0)
    pos = np.zeros((s.L, 26))
    for j in range(s.L):
        np.add.at(pos[j], s.A[:, j], p)
    letters = "abcdefghijklmnopqrstuvwxyz"
    doubles = float(p @ (P.letter_counts(s.A).max(1) >= 2))
    vowel_n = Counter()
    for w, pw in zip(s.words, p):
        vowel_n[sum(ch in VOWELS for ch in w)] += pw
    ends2, ends3, starts2 = Counter(), Counter(), Counter()
    for w, pw in zip(s.words, p):
        ends2[w[-2:]] += pw
        ends3[w[-3:]] += pw
        starts2[w[:2]] += pw
    return {
        "presence": {letters[i]: float(pres[i]) for i in np.argsort(-pres)},
        "positional": {f"pos{j + 1}": {letters[i]: float(pos[j, i]) for i in np.argsort(-pos[j])[:6]}
                       for j in range(s.L)},
        "positional_matrix": pos.tolist(),
        "p_double_letter": doubles,
        "vowel_count": {int(k): float(v) for k, v in sorted(vowel_n.items())},
        "top_endings_2": [(k, float(v)) for k, v in ends2.most_common(10)],
        "top_endings_3": [(k, float(v)) for k, v in ends3.most_common(10)],
        "top_starts_2": [(k, float(v)) for k, v in starts2.most_common(10)],
    }


def best_openers(s: Solver, top: int = 25) -> list[dict]:
    """Exact ranking over the whole guess pool against every word."""
    pool = np.nonzero(s.is_guess)[0]
    return s.rank(top, pool=pool, exact=True)


def common_openers(s: Solver, top: int = 10) -> list[dict]:
    """Best openers restricted to everyday words."""
    pool = np.nonzero(s.is_common & s.is_guess)[0]
    return s.rank(top, pool=pool, exact=True)


def _joint_entropy(p1, p2, wc, L):
    key = p1.astype(np.int64) * (3 ** L) + p2
    _, inv = np.unique(key, return_inverse=True)
    q = np.bincount(inv, weights=wc)
    q = q[q > 0]
    return float(-(q * np.log2(q)).sum())


def best_pairs(s: Solver, openers: list[str], n_first: int = 8, n_second: int = 150,
               top: int = 10) -> list[dict]:
    """Best FIXED two-word openings (play both regardless of feedback) -
    great for humans. Scored by joint entropy."""
    wc = prior(s)
    C = P.letter_counts(s.A)
    pres = wc @ (C > 0)
    guess_idx = np.nonzero(s.is_common & s.is_guess)[0]  # everyday words only
    Gc = C[guess_idx] > 0
    out = []
    for w1 in openers[:n_first]:
        g1 = P.to_array([w1])[0]
        p1 = P.patterns_one(g1, s.A, C)
        used = np.zeros(26, bool)
        used[g1] = True
        score = Gc @ (pres * ~used) - 0.5 * (Gc @ (pres * used))
        shortlist = guess_idx[np.argsort(-score)[:n_second]]
        for j in shortlist:
            p2 = P.patterns_one(s.A[j], s.A, C)
            out.append({"first": w1, "second": s.words[j], "joint_bits": _joint_entropy(p1, p2, wc, s.L)})
    out.sort(key=lambda d: -d["joint_bits"])
    seen, res = set(), []
    for d in out:
        k = frozenset((d["first"], d["second"]))
        if k not in seen:
            seen.add(k)
            d["joint_bits"] = round(d["joint_bits"], 3)
            res.append(d)
        if len(res) >= top:
            break
    return res


def trap_families(s: Solver, top: int = 12, min_size: int = 4) -> list[dict]:
    """Groups of realistic answers that differ in only ONE position, e.g.
    _ight -> fight light might night right sight tight. These are where
    players run out of guesses."""
    realistic = [w for w, c in zip(s.words, s.is_common) if c]
    fams = defaultdict(list)
    for w in realistic:
        for j in range(s.L):
            fams[w[:j] + "_" + w[j + 1:]].append(w)
    big = sorted(((k, v) for k, v in fams.items() if len(v) >= min_size), key=lambda kv: -len(kv[1]))
    res, used = [], set()
    for k, v in big:
        if frozenset(v) in used:
            continue
        used.add(frozenset(v))
        res.append({"pattern": k, "size": len(v), "words": sorted(v)})
        if len(res) >= top:
            break
    n_in_trap = len({w for k, v in fams.items() if len(v) >= min_size for w in v})
    return res, n_in_trap / max(len(realistic), 1)


def first_feedback_signals(s: Solver, opener: str) -> list[dict]:
    """For the best opener: given how many greens/yellows you get, how likely
    is that and how many candidates remain on average?"""
    wc = prior(s)
    g = P.to_array([opener])[0]
    pats = P.patterns_one(g, s.A, P.letter_counts(s.A))
    table = defaultdict(lambda: [0.0, Counter()])
    for p in np.unique(pats):
        d = P.decode(int(p), s.L)
        key = (d.count(2), d.count(1))
        m = pats == p
        table[key][0] += wc[m].sum()
        table[key][1][int(p)] = int(m.sum())
    rows = []
    for (gr, ye), (prob, pc) in sorted(table.items()):
        # avg candidates left (weighted by how often each exact pattern happens)
        tot = sum(pc.values())
        avg_left = sum(c * c for c in pc.values()) / tot
        rows.append({"greens": gr, "yellows": ye, "probability": round(float(prob), 4),
                     "avg_candidates_left": round(avg_left, 1), "distinct_patterns": len(pc)})
    return rows
