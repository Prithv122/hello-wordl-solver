"""Command line interface.

    python -m wordl play -n 5            interactive helper (step by step)
    python -m wordl suggest -n 5 rales:bybbg night:bbgbb
    python -m wordl openers -n 7         best first words for 7 letters
    python -m wordl candidates -n 5 rales:bybbg

Feedback is typed as one symbol per letter:
    g = green (right letter, right spot)
    y = yellow (in the word, wrong spot)
    b = grey/black (not in the word - or no more copies of it)
Digits 2/1/0 and the emoji squares also work.
"""
from __future__ import annotations

import argparse
import sys
import time

from . import patterns as P
from .solver import Solver


def _table(rows, cands_left):
    print(f"   {'guess':<14}{'exp.guesses':>12}{'info(bits)':>11}{'P(win now)':>11}{'worst left':>11}")
    for i, r in enumerate(rows):
        star = "*" if i == 0 else " "
        print(f" {star} {r['word'].upper():<14}{r['expected_guesses']:>12.2f}{r['entropy_bits']:>11.2f}"
              f"{r['p_win'] * 100:>10.1f}%{r['worst_case_left']:>11}")


def _show_cands(s: Solver, n=15):
    c = s.candidates(n)
    more = len(s.cand) - len(c)
    txt = ", ".join(f"{w.upper()} {p * 100:.0f}%" if p >= 0.01 else w.upper() for w, p, _ in c)
    print(f"   possible answers ({len(s.cand)}): {txt}{' ...+' + str(more) if more > 0 else ''}")


def _apply(s: Solver, items):
    for it in items:
        w, p = it.split(":")
        s.update(w, p)


def cmd_suggest(a):
    s = Solver(a.length, hard=a.hard)
    _apply(s, a.history)
    t = time.time()
    if len(s.cand) == 0:
        print("No word in the list matches that feedback - check for a typo."); return 1
    rows = s.rank(a.top)
    _table(rows, len(s.cand))
    _show_cands(s)
    print(f"   ({time.time() - t:.2f}s)")


def cmd_candidates(a):
    s = Solver(a.length)
    _apply(s, a.history)
    for w, p, t in s.candidates(a.top):
        print(f"{w}\t{p:.4f}\ttier {t}")


def cmd_openers(a):
    s = Solver(a.length, hard=a.hard)
    _table(s.rank(a.top), len(s.cand))


def cmd_play(a):
    s = Solver(a.length, hard=a.hard)
    L = a.length
    print(f"\nHello Wordl helper - {L} letters, {s.max_guesses} tries"
          f"{' (hard mode)' if a.hard else ''}. {len(s.words)} words in list.")
    print("After each guess type the colours: g=green y=yellow b=grey   e.g. " + "bygbb"[:L].ljust(L, "b"))
    print("Played a different word? type  WORD COLOURS.  Commands: ! = game rejected the word, "
          "? = list answers, u = undo, n = new game, q = quit\n")
    while True:
        if len(s.cand) == 0:
            print("No candidates left - a feedback was probably mistyped. Undoing last step.")
            hist = s.history[:-1]; s.reset(); [s.update(w, p) for w, p in hist]
        t = time.time()
        rows = s.rank(a.top)
        turn = len(s.history) + 1
        print(f"Turn {turn}/{s.max_guesses}  ({len(s.cand)} possible, {time.time() - t:.2f}s)")
        _table(rows, len(s.cand))
        if len(s.cand) <= 15:
            _show_cands(s)
        sug = rows[0]["word"]
        try:
            line = input(f"\n  play {sug.upper()} -> feedback: ").strip().lower()
        except EOFError:
            return
        if not line:
            continue
        if line == "q":
            return
        if line == "n":
            s.reset(); print("\nNew game.\n"); continue
        if line == "?":
            _show_cands(s, 200); continue
        if line == "u":
            hist = s.history[:-1]; s.reset(); [s.update(w, p) for w, p in hist]; continue
        if line.startswith("!"):
            s.reject(line[1:].strip() or sug); print("  ok, won't suggest it again"); continue
        parts = line.split()
        word, fb = (sug, parts[0]) if len(parts) == 1 else (parts[0], parts[1])
        try:
            pat = P.parse(fb, L)
        except ValueError as e:
            print("  ", e); continue
        if pat == P.all_green(L):
            print(f"\n  Solved in {turn}!  New game started.\n"); s.reset(); continue
        left = s.update(word, pat)
        print(f"  {word.upper()} {P.to_str(pat, L, 'emoji')} -> {left} possible\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wordl", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("play", cmd_play), ("suggest", cmd_suggest),
                     ("openers", cmd_openers), ("candidates", cmd_candidates)]:
        p = sub.add_parser(name)
        p.add_argument("-n", "--length", type=int, default=5)
        p.add_argument("--hard", action="store_true", help="hard mode: only guess possible answers")
        p.add_argument("--top", type=int, default=8)
        if name in ("suggest", "candidates"):
            p.add_argument("history", nargs="*", help="guess:feedback pairs, e.g. rales:bybbg")
        p.set_defaults(fn=fn)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
