"""Build and load the word lexicon.

Two sources are combined:

* ``data/raw/words.csv``      – ~466k raw English tokens (one per line). Huge
  coverage (plurals, inflections, rare words) but also a lot of noise.
* ``data/raw/dictionary.csv`` – Webster's dictionary: headword, part of speech,
  definition. ~32k distinct headwords. The number of definitions a headword
  has is a good proxy for how *common* the word is ("run" has 72, "zoanthus" 1).

Every word gets a *class* and a *prior weight* = how likely it is to be the
hidden answer (Hello Wordl answers are everyday words):

    A1..A4  in Webster with 2-3 / 4-7 / 8-15 / 16+ definitions
              (each class is further split -f0..-f4 by how often the word is
              USED inside the definitions text = a word-frequency signal)
    B       in Webster with exactly 1 definition (mostly rare words)
    C       plural / -ed / -ing / -er ... of a Webster word ("cats", "baked")
    D       any other word in words.csv

If data/external/dictionary.json (Hello Wordl's accepted-word list, fetched by
scripts/fetch_game_lists.py) is present, only words the game accepts are
kept: names (JAMEL, PATEL), abbreviations and junk are dropped. Every
remaining word still comes from the two files above.

Case is ignored everywhere (the game has no case): "Time", "TIME" and
"time" are the same word. Words are stored lowercase internally and shown
in CAPITALS.

The weight of each class is CALIBRATED (scripts/calibrate.py): the fraction
of words of that class and length that are real Hello Wordl answers, fitted
on half of the game's public answer list (the other half is the benchmark).
Classes A-C form the *guess pool* (words the game accepts as guesses);
every class is a possible answer.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_WORDS = os.path.join(ROOT, "data", "raw", "words.csv")
RAW_DICT = os.path.join(ROOT, "data", "raw", "dictionary.csv")
LEX_DIR = os.path.join(ROOT, "data", "lexicon")

GUESS_TIERS = {"A", "B", "C"}
COMMON_WEIGHT = 0.15   # classes the game (almost) always accepts as guesses


def _clean(w: str) -> str | None:
    w = w.strip()
    if w.isascii() and w.isalpha():
        return w
    return None


def _inflection_stem(w: str, base: set[str]) -> str | None:
    """Return the Webster stem if ``w`` is a simple inflection of it."""
    cands = []
    if w.endswith("ies"):
        cands.append(w[:-3] + "y")
    if w.endswith("es"):
        cands.append(w[:-2])
    if w.endswith("s") and not w.endswith("ss"):
        cands.append(w[:-1])
    if w.endswith("ied"):
        cands.append(w[:-3] + "y")
    if w.endswith("ed"):
        cands += [w[:-2], w[:-1]]
        if len(w) > 4 and w[-3] == w[-4]:
            cands.append(w[:-3])  # stopped -> stop
    if w.endswith("ing"):
        cands += [w[:-3], w[:-3] + "e"]
        if len(w) > 5 and w[-4] == w[-5]:
            cands.append(w[:-4])  # running -> run
    for suf in ("er", "est"):
        if w.endswith(suf):
            cands += [w[: -len(suf)], w[: -len(suf)] + "e"]
    if w.endswith("ly"):
        cands.append(w[:-2])
    for c in cands:
        if len(c) >= 2 and c in base:
            return c
    return None


def build(words_path: str = RAW_WORDS, dict_path: str = RAW_DICT):
    """Return {length: [(word, tier, weight, n_defs), ...]} sorted by weight."""
    defs: Counter[str] = Counter()
    usage: Counter[str] = Counter()      # how often a word is USED inside definitions
    with open(dict_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f):
            if row and (w := _clean(row[0])):
                defs[w.lower()] += 1
            if len(row) >= 3:
                usage.update(_TOKEN.findall(row[2].lower()))

    seen: set[str] = set()
    with open(words_path, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.reader(f):
            if row and (w := _clean(row[0])):
                seen.add(w.lower())          # case-insensitive

    base = set(defs)
    universe = base | seen
    valid = load_game_dictionary()
    if valid:  # names, abbreviations and junk are never valid Hello Wordl words
        universe &= valid
    calib = load_calibration()
    by_len = defaultdict(list)
    for w in universe:
        n = defs.get(w, 0)
        cls = word_class(w, n, base) + "-f" + str(freq_bucket(usage.get(w, 0)))
        wt = class_weight(calib, len(w), cls)
        by_len[len(w)].append((w, cls, wt, n))
    for L in by_len:
        by_len[L].sort(key=lambda t: (-t[2], -t[3], t[0]))
    return dict(by_len)


_TOKEN = re.compile(r"[a-z]+")


def freq_bucket(n: int) -> int:
    """0: never used in a definition, 1: 1-2x, 2: 3-9x, 3: 10-49x, 4: 50x+"""
    return 0 if n == 0 else 1 if n < 3 else 2 if n < 10 else 3 if n < 50 else 4


def word_class(w: str, n_defs: int, base: set[str]) -> str:
    if n_defs >= 2:
        return "A" + str(min(int(math.log2(n_defs)), 4))   # A1 (2-3 defs) .. A4 (16+)
    if n_defs == 1:
        return "B"
    if _inflection_stem(w, base):
        return "C"
    return "D"


CALIB_FILE = os.path.join(ROOT, "data", "prior_calibration.json")
GAME_DICT = os.path.join(ROOT, "data", "external", "dictionary.json")


def load_game_dictionary() -> set[str] | None:
    """Hello Wordl's accepted-word list (scripts/fetch_game_lists.py), if present."""
    if os.path.exists(GAME_DICT):
        with open(GAME_DICT) as f:
            return {w.lower() for w in json.load(f)}
    return None
DEFAULT_WEIGHT = {"A4": 1.0, "A3": 0.9, "A2": 0.6, "A1": 0.25, "B": 0.05, "C": 0.005,
                  "D": 0.06}


def load_calibration() -> dict:
    if os.path.exists(CALIB_FILE):
        with open(CALIB_FILE) as f:
            return json.load(f)
    return {}


def class_weight(calib: dict, L: int, cls: str) -> float:
    rates = calib.get(str(L), {})
    if cls in rates:
        return max(rates[cls], 1e-4)
    if cls in calib.get("all", {}):
        return max(calib["all"][cls], 1e-4)
    base = DEFAULT_WEIGHT[cls.split("-")[0]]
    f = int(cls[-1]) if "-f" in cls else 0
    return round(base * (0.3, 1, 2, 4, 6)[f], 5)


def save(by_len, out_dir: str = LEX_DIR, lengths=range(2, 16)):
    os.makedirs(out_dir, exist_ok=True)
    for L in lengths:
        rows = by_len.get(L, [])
        with open(os.path.join(out_dir, f"len_{L:02d}.tsv"), "w") as f:
            f.write("word\tclass\tweight\tdefinitions\n")
            for w, t, wt, n in rows:
                f.write(f"{w}\t{t}\t{wt}\t{n}\n")


@dataclass
class Lexicon:
    length: int
    words: list[str]
    tiers: list[str]          # A/B/C/D/E
    weights: list[float]
    defs: list[int]
    classes: list[str]        # A1..A4/B/C/D/E

    def freq(self, i: int) -> int:
        return int(self.classes[i][-1]) if "-f" in self.classes[i] else 0

    def is_guess(self, i: int) -> bool:
        """Will the game accept it? Webster words + inflections, or any word
        that is genuinely used in English text (definition usage >= 3)."""
        return self.tiers[i] in GUESS_TIERS or self.freq(i) >= 2

    def is_common(self, i: int) -> bool:
        """Everyday word: calibrated P(answer) high enough to teach with."""
        return self.weights[i] >= COMMON_WEIGHT

    def __len__(self):
        return len(self.words)


def load(length: int, lex_dir: str = LEX_DIR, extra_words_file: str | None = None) -> Lexicon:
    path = os.path.join(lex_dir, f"len_{length:02d}.tsv")
    if not os.path.exists(path):
        save(build())
    words, tiers, weights, defs, classes = [], [], [], [], []
    with open(path) as f:
        next(f)
        for line in f:
            w, t, wt, n = line.rstrip("\n").split("\t")
            words.append(w)
            tiers.append(t[0])
            classes.append(t)
            weights.append(float(wt))
            defs.append(int(n))
    if extra_words_file:
        known = set(words)
        with open(extra_words_file) as f:
            for line in f:
                w = line.strip().lower()
                if len(w) == length and w.isalpha() and w not in known:
                    words.append(w)
                    tiers.append("A")
                    classes.append("A4")
                    weights.append(1.0)
                    defs.append(0)
    return Lexicon(length, words, tiers, weights, defs, classes)


if __name__ == "__main__":
    bl = build()
    save(bl)
    for L in range(3, 13):
        c = Counter(t for _, t, _, _ in bl.get(L, []))
        print(L, len(bl.get(L, [])), dict(sorted(c.items())), flush=True)
