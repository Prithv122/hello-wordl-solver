"""Play the solver against many hidden answers and measure performance."""
from __future__ import annotations

import json
import os
import random
import time
from collections import Counter

from . import patterns as P
from .lexicon import ROOT
from .solver import Solver


BENCH_FILE = os.path.join(ROOT, "data", "benchmark_answers.json")


def benchmark_answers(L: int, s: Solver) -> tuple[list[str], str]:
    """Held-out real Hello Wordl answers if available, else common words."""
    if os.path.exists(BENCH_FILE):
        ans = json.load(open(BENCH_FILE)).get(str(L), [])
        known = set(s.words)
        return [w for w in ans if w in known], "held-out Hello Wordl answers"
    return [w for w, c in zip(s.words, s.is_common) if c], "common words (no calibration file)"


def simulate(L: int, n_games: int = 300, opener: str | None = None, book: dict | None = None,
             seed: int = 0, hard: bool = False, answers: list[str] | None = None,
             **solver_kw) -> dict:
    s = Solver(L, use_book=False, hard=hard, **solver_kw)
    source = "given list"
    if answers is None:
        answers, source = benchmark_answers(L, s)
    rng = random.Random(seed)
    if len(answers) > n_games:
        answers = rng.sample(answers, n_games)
    memo: dict[tuple, str] = {}
    dist = Counter()
    fails, step_times, solved_words = [], [], []
    max_g = s.max_guesses
    for ans in answers:
        s.reset()
        n = 0
        while True:
            key = tuple(s.history)
            if key in memo:
                g = memo[key]
            else:
                t0 = time.time()
                if not s.history and opener:
                    g = opener
                elif (len(s.history) == 1 and book and opener
                      and (e := book["patterns"].get(P.to_str(s.history[0][1], L)))):
                    g = e["best"][0]["word"]
                else:
                    g = s.best()
                step_times.append(time.time() - t0)
                memo[key] = g
            n += 1
            p = P.score(g, ans)
            if p == P.all_green(L):
                break
            s.update(g, p)
            if n > 3 * max_g:  # safety
                break
        dist[n] += 1
        if n > max_g:
            fails.append(ans)
    total = sum(dist.values())
    return {
        "length": L,
        "games": total,
        "answers": source,
        "opener": opener,
        "avg_guesses": round(sum(k * v for k, v in dist.items()) / total, 3),
        "distribution": {int(k): v for k, v in sorted(dist.items())},
        "max_guesses_allowed": max_g,
        "win_rate": round(1 - len(fails) / total, 4),
        "failed_words": fails[:20],
        "avg_live_step_seconds": round(sum(step_times) / max(len(step_times), 1), 4),
        "max_live_step_seconds": round(max(step_times, default=0), 3),
    }
