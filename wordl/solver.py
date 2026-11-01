"""Probability / information-theory solver for Hello Wordl (any word length).

How a guess is scored
---------------------
Every remaining candidate answer has a prior weight (see lexicon.py). For a
guess ``g`` we compute the colour pattern it would produce against every
candidate and group the candidates by pattern. With q_p = probability mass of
pattern p:

* entropy   H(g) = -sum q_p log2 q_p      (bits of information expected)
* p_win(g)       = mass of the all-green pattern (g itself is the answer)
* E(g) = 1 + sum_{p != win} q_p * F(h_p)
  the *expected number of guesses* including this one, where h_p is the
  uncertainty (bits) left inside group p and F(h) is the expected number of
  guesses needed to finish from h bits (F(0)=1, F(1)=1.5, ~0.35/bit after).

The solver plays the guess with the lowest E (plus a tiny "obscure word"
tax so it prefers words the game will accept). This automatically balances
"learn as much as possible" (high H) against "this could win now" (p_win).
"""
from __future__ import annotations

import json
import os

import numpy as np

from . import patterns as P
from .lexicon import ROOT, Lexicon, load

OPENERS_FILE = os.path.join(ROOT, "output", "openers.json")
BOOK_DIR = os.path.join(ROOT, "output", "opening_book")
PAIR_BUDGET = 4_000_000        # guess x candidate pairs evaluated exactly per live step
LOOKAHEAD_K = 80               # exact tree search when <= this many candidates remain
LOOKAHEAD_WIDTH = 10           # guesses explored per node in that search
FAIL_PENALTY = 20.0            # cost of running out of tries, in "guesses" (tuned)
CANDIDATE_MARGIN = 0.0         # tuned in scripts/tune.py
PRIOR_POWER = 1.0              # tuned in scripts/tune.py
JUNK_TAX = 0.15
TIER_TAX = {"A": 0.01, "B": 0.03, "C": 0.015, "D": 0.05}


def finish_cost(h: np.ndarray) -> np.ndarray:
    """F(h): expected guesses to finish a group holding h bits of uncertainty."""
    return np.where(h <= 1.0, 1.0 + 0.5 * h, 1.5 + 0.35 * (h - 1.0))


class Solver:
    def __init__(self, length: int, lex: Lexicon | None = None, hard: bool = False,
                 max_guesses: int | None = None, use_book: bool = True,
                 pair_budget: int = PAIR_BUDGET, lookahead: bool = True,
                 lookahead_k: int = LOOKAHEAD_K, lookahead_width: int = LOOKAHEAD_WIDTH,
                 prior_power: float = PRIOR_POWER, fail_penalty: float = FAIL_PENALTY,
                 candidate_margin: float = CANDIDATE_MARGIN):
        self.L = length
        self.lex = lex or load(length)
        if len(self.lex) == 0:
            raise ValueError(f"no {length}-letter words in lexicon")
        self.words = self.lex.words
        self.index = {w: i for i, w in enumerate(self.words)}
        self.A = P.to_array(self.words)
        # prior_power < 1 flattens the prior = hedge more against "rare" answers
        self.w = np.asarray(self.lex.weights, dtype=np.float64) ** prior_power
        self.fail_penalty = fail_penalty
        self.candidate_margin = candidate_margin
        n = len(self.words)
        self.is_guess = np.array([self.lex.is_guess(i) for i in range(n)])
        self.is_common = np.array([self.lex.is_common(i) for i in range(n)])
        # small "obscure word" tax: the game may reject rare words
        self.tax = np.where(self.is_common, 0.0,
                            np.array([TIER_TAX[t] for t in self.lex.tiers]))
        self.tax[~self.is_guess] = JUNK_TAX   # probably not even accepted by the game
        self.hard = hard
        self.max_guesses = max_guesses or 6  # Hello Wordl: 6 tries at every length
        self.use_book = use_book
        self.pair_budget = pair_budget
        self.lookahead = lookahead
        self.lookahead_k = lookahead_k
        self.lookahead_width = lookahead_width
        self.reset()

    # ------------------------------------------------------------------ state
    def reset(self):
        self.cand = np.arange(len(self.words))
        self.history: list[tuple[str, int]] = []
        self.rejected: set[int] = set()

    def reject(self, word: str):
        """The game refused this word - never suggest it again."""
        i = self.index.get(word.lower())
        if i is not None:
            self.rejected.add(i)
            self.cand = self.cand[self.cand != i]

    def update(self, guess: str, pattern: int | str) -> int:
        """Apply the feedback for a played guess; returns #candidates left."""
        guess = guess.lower().strip()
        if len(guess) != self.L or not guess.isalpha():
            raise ValueError(f"guess must be {self.L} letters")
        if isinstance(pattern, str):
            pattern = P.parse(pattern, self.L)
        g = P.to_array([guess])[0]
        Ac = self.A[self.cand]
        pats = P.patterns_one(g, Ac, P.letter_counts(Ac))
        self.cand = self.cand[pats == pattern]
        self.history.append((guess, pattern))
        return len(self.cand)

    @property
    def solved(self) -> bool:
        return bool(self.history) and self.history[-1][1] == P.all_green(self.L)

    def candidates(self, top: int | None = None):
        """Remaining possible answers, most likely first: (word, prob, tier)."""
        order = np.argsort(-self.w[self.cand], kind="stable")
        idx = self.cand[order]
        tot = self.w[self.cand].sum()
        return [(self.words[i], float(self.w[i] / tot), self.lex.tiers[i]) for i in idx[:top]]

    # --------------------------------------------------------------- ranking
    def _pool(self) -> np.ndarray:
        if self.hard:
            pool = self.cand[self.is_guess[self.cand]]
            if len(pool) == 0:
                pool = self.cand
        else:
            pool = np.union1d(np.nonzero(self.is_guess)[0], self.cand)
        if self.rejected:
            pool = np.setdiff1d(pool, np.fromiter(self.rejected, int))
        return pool

    def _prefilter(self, pool: np.ndarray, keep: int) -> np.ndarray:
        """Cheap shortlist when the exact search would be big: reward letters
        whose presence is close to 50/50 among the candidates (max info) and
        likely-green positions. Always keeps the most likely candidates."""
        Ac = self.A[self.cand]
        wc = self.w[self.cand] / self.w[self.cand].sum()
        f = wc @ (P.letter_counts(Ac) > 0)          # P(letter in answer)
        pres = f * (1 - f)
        pos = np.zeros((self.L, 26))
        for j in range(self.L):
            np.add.at(pos[j], Ac[:, j], wc)
        G = self.A[pool]
        s = (P.letter_counts(G) > 0) @ pres
        for j in range(self.L):
            pj = pos[j, G[:, j]]
            s += 0.5 * pj * (1 - pj)
        top = pool[np.argsort(-s)[:keep]]
        likely = self.cand[np.argsort(-wc)[:100]]
        if self.hard:
            likely = likely[self.is_guess[likely]] if self.is_guess[likely].any() else likely
        return np.union1d(top, likely)

    def rank(self, top: int = 10, pool: np.ndarray | None = None, exact: bool = False):
        """Return the ``top`` best guesses (dicts), best first."""
        K = len(self.cand)
        if K == 0:
            raise RuntimeError("no candidates left - the answer is not in the word list "
                               "(or a feedback was mistyped)")
        if not self.history and self.use_book and pool is None and not self.rejected:
            cached = load_openers().get(str(self.L), {}).get("hard" if self.hard else "normal")
            if cached:
                return cached[:top]
        if (len(self.history) == 1 and self.use_book and pool is None and not self.rejected
                and not self.hard):
            from .book import lookup
            hit = lookup(self.L, *self.history[0])
            if hit:
                return hit[:top]
        wc = self.w[self.cand] / self.w[self.cand].sum()
        if K <= 2:
            return [self._single(i, p) for p, i in sorted(zip(-wc, self.cand))][:top]
        if pool is None:
            pool = self._pool()
            if not exact and len(pool) * K > self.pair_budget:
                pool = self._prefilter(pool, max(250, self.pair_budget // K))
        res = self.score_pool(pool, wc)
        E = res["E"] + self.tax[pool]
        order = np.lexsort((-res["p_win"], E))
        turns_left = self.max_guesses - len(self.history)
        if self.lookahead and (K <= self.lookahead_k or (turns_left <= 3 and K <= 4 * self.lookahead_k)):
            depth = 2 if K <= self.lookahead_k // 2 or turns_left <= 3 else 1
            refined = self._lookahead(pool[order], depth=depth, width=self.lookahead_width)
            searched = np.zeros(len(pool), bool)
            for o in order[:self.lookahead_width]:
                if int(pool[o]) in refined:
                    res["E"][o] = refined[int(pool[o])] - self.tax[pool[o]]
                    searched[o] = True
            E = res["E"] + self.tax[pool]
            # searched guesses (honest cost) first, then the rest by heuristic
            order = np.lexsort((-res["p_win"], E, ~searched))
        # Prefer a guess that could WIN NOW when it is nearly as good as the
        # best probe word (a probe can never be the answer).
        if self.candidate_margin > 0 and res["p_win"][order[0]] == 0:
            Ef = res["E"] + self.tax[pool]
            cands = order[res["p_win"][order] > 0]
            if len(cands) and Ef[cands[0]] - Ef[order[0]] <= self.candidate_margin:
                order = np.concatenate(([cands[0]], order[order != cands[0]]))
        order = order[:top]
        return [{
            "word": self.words[pool[o]],
            "expected_guesses": round(float(res["E"][o]), 4),
            "entropy_bits": round(float(res["H"][o]), 4),
            "p_win": round(float(res["p_win"][o]), 4),
            "groups": int(res["groups"][o]),
            "worst_case_left": int(res["worst"][o]),
            "avg_left": round(float(res["avg_left"][o]), 2),
        } for o in order]

    def best(self) -> str:
        return self.rank(1)[0]["word"]

    def _single(self, i, negp):
        p = float(-negp)
        return {"word": self.words[i], "expected_guesses": round(2 - p, 4),
                "entropy_bits": round(float(-(p * np.log2(p) + (1 - p) * np.log2(max(1 - p, 1e-300)))), 4)
                if p < 1 else 0.0,
                "p_win": round(p, 4), "groups": len(self.cand), "worst_case_left": 1,
                "avg_left": 1.0}

    def score_pool(self, pool: np.ndarray, wc: np.ndarray) -> dict:
        """Score every guess in ``pool`` against current candidates (weights wc)."""
        Ac = self.A[self.cand]
        K = len(self.cand)
        G = self.A[pool]
        n = len(pool)
        if n * K <= 25_000_000:
            return stats_from_matrix(P.fast_matrix(G, Ac), wc, P.all_green(self.L))
        # huge candidate set (first guess): one guess at a time with bincount
        win = P.all_green(self.L)
        wlogw = wc * np.log2(np.maximum(wc, 1e-300))
        acc = _new_acc(n)
        Cc = P.letter_counts(Ac)
        nb = 3 ** self.L
        for r in range(n):
            p = P.patterns_one(G[r], Ac, Cc)
            ws = np.bincount(p, weights=wc, minlength=nb)
            nz = np.nonzero(ws)[0]
            wl = np.bincount(p, weights=wlogw, minlength=nb)[nz]
            cnt = np.bincount(p, minlength=nb)[nz]
            _accumulate(np.full(len(nz), r), nz, ws[nz], wl, cnt, win, acc, n)
        acc["E"] += 1.0
        return acc

    # ------------------------------------------------------- endgame search
    def _lookahead(self, ranked: np.ndarray, depth: int, width: int) -> dict[int, float]:
        """Search the game tree below the top ``width`` root guesses.

        Each node costs  E + self.fail_penalty * P(fail)  where E = expected guesses
        and P(fail) = chance of NOT finishing within the remaining tries.
        The last two turns are solved exactly; deeper leaves use the
        heuristic E. Returns {pool word index: cost}."""
        cand = self.cand
        win = P.all_green(self.L)
        sub_pool = cand if self.hard else np.union1d(ranked[:max(width * 5, 60)], cand)
        Mfull = P.fast_matrix(self.A[sub_pool], self.A[cand]).astype(np.int64)
        tax = self.tax[sub_pool]
        w = self.w[cand]
        memo: dict = {}
        turns0 = self.max_guesses - len(self.history)

        def node(sub: np.ndarray, d: int, t: int) -> float:
            """Best cost with candidates ``sub`` and ``t`` tries left."""
            K = len(sub)
            if t <= 0:
                return self.fail_penalty + 1.0
            q = w[sub] / w[sub].sum()
            if K == 1:
                return 1.0
            if t == 1:                                    # must guess the likeliest
                pm = float(q.max())
                return 1.0 + self.fail_penalty * (1 - pm)
            if K == 2:
                return 1.0 + float(q.min())
            key = (sub.tobytes(), d, min(t, 4))
            if key in memo:
                return memo[key]
            M = Mfull[:, sub]
            st = stats_from_matrix(M, q, win)
            E = st["E"] + tax
            if t == 2:                                    # exact: win now or next turn
                pwin2 = st["p_win"] + _group_max_sum(M, q, win)
                cost = st["E"] + self.fail_penalty * (1 - pwin2) + tax
                best = float(cost.min())
            elif d == 0:
                best = float(E.min())
            else:
                best = np.inf
                for g in np.argsort(E)[:width]:
                    best = min(best, branch(M[g], sub, q, d, t) + tax[g])
            memo[key] = best
            return best

        def branch(row, sub, q, d, t) -> float:
            cost = 1.0
            order = np.argsort(row, kind="stable")
            cuts = np.nonzero(np.diff(row[order]))[0] + 1
            for grp in np.split(order, cuts):
                if row[grp[0]] == win:
                    continue
                cost += float(q[grp].sum()) * node(sub[grp], d - 1, t - 1)
            return cost

        allpos = np.arange(len(cand))
        q0 = w / w.sum()
        pos_of = {int(v): i for i, v in enumerate(sub_pool)}
        out = {}
        for gi in ranked[:width]:
            if int(gi) in pos_of:
                out[int(gi)] = branch(Mfull[pos_of[int(gi)]], allpos, q0, depth, turns0)
        return out


def _group_max_sum(M: np.ndarray, q: np.ndarray, win: int) -> np.ndarray:
    """Per guess: sum over non-winning feedback groups of the likeliest
    candidate's probability = P(win on the NEXT turn)."""
    n, K = M.shape
    order = np.argsort(M, axis=1, kind="stable")
    Ms = np.take_along_axis(M, order, axis=1).ravel()
    Q = q[order].ravel()
    start = np.ones(n * K, bool)
    start[1:] = Ms[1:] != Ms[:-1]
    start[::K] = True
    s_idx = np.nonzero(start)[0]
    gmax = np.maximum.reduceat(Q, s_idx)
    gmax[Ms[s_idx] == win] = 0.0
    return np.bincount(s_idx // K, weights=gmax, minlength=n)


def _new_acc(n):
    acc = {k: np.zeros(n) for k in ("H", "E", "p_win", "avg_left")}
    acc["groups"] = np.zeros(n, int)
    acc["worst"] = np.zeros(n, int)
    return acc


def stats_from_matrix(M: np.ndarray, wc: np.ndarray, win: int) -> dict:
    """Per-row (guess) statistics of a pattern matrix M (n guesses x K cands)."""
    n, K = M.shape
    acc = _new_acc(n)
    wlogw = wc * np.log2(np.maximum(wc, 1e-300))
    order = np.argsort(M, axis=1, kind="stable")
    Ms = np.take_along_axis(M, order, axis=1).ravel()
    W = wc[order].ravel()
    WL = wlogw[order].ravel()
    start = np.ones(n * K, bool)
    start[1:] = Ms[1:] != Ms[:-1]
    start[::K] = True                                 # each row starts a new group
    s_idx = np.nonzero(start)[0]
    ws = np.add.reduceat(W, s_idx)
    wl = np.add.reduceat(WL, s_idx)
    cnt = np.diff(np.append(s_idx, n * K))
    _accumulate(s_idx // K, Ms[s_idx].astype(np.int64), ws, wl, cnt, win, acc, n)
    acc["E"] += 1.0                                   # this guess itself
    return acc


def _accumulate(row, pat, ws, wl, cnt, win, acc, n):
    safe = np.maximum(ws, 1e-300)
    h = np.maximum(np.log2(safe) - wl / safe, 0.0)    # bits left inside group
    is_win = pat == win
    acc["H"] += np.bincount(row, weights=-ws * np.log2(safe), minlength=n)
    acc["p_win"] += np.bincount(row, weights=np.where(is_win, ws, 0.0), minlength=n)
    acc["E"] += np.bincount(row, weights=np.where(is_win, 0.0, ws * finish_cost(h)), minlength=n)
    acc["groups"] += np.bincount(row, minlength=n)
    np.maximum.at(acc["worst"], row, cnt)
    acc["avg_left"] += np.bincount(row, weights=ws * cnt, minlength=n)


_openers_cache = None


def load_openers() -> dict:
    global _openers_cache
    if _openers_cache is None:
        _openers_cache = {}
        if os.path.exists(OPENERS_FILE):
            with open(OPENERS_FILE) as f:
                _openers_cache = json.load(f)
    return _openers_cache
