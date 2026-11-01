"""Write STRATEGY_GUIDE.md and output/reports/len_XX.md from the analysis data.

    python scripts/make_guide.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "output", "analysis")
LENGTHS = [L for L in range(4, 12) if os.path.exists(os.path.join(AN, f"len_{L:02d}.json"))]
U = str.upper


def load(L):
    return json.load(open(os.path.join(AN, f"len_{L:02d}.json")))


def pct(x, d=0):
    return f"{x * 100:.{d}f}%"


def opener_methods():
    p = os.path.join(ROOT, "output", "opener_methods.txt")
    if not os.path.exists(p):
        return ""
    rows, L = [], None
    for line in open(p):
        m = re.match(r"--- (\d+) letters", line)
        if m:
            L = int(m.group(1)); cur = {"L": L}; rows.append(cur); continue
        m = re.match(r"(.+?)\s{2,}(\S+)\s+info ([\d.]+) bits \| avg answers left\s+([\d.]+)", line)
        if m and L:
            key = {"most frequent letters": "freq", "frequent letters in usual positions": "pos",
                   "information (solver)": "info"}[m.group(1).strip()]
            cur[key] = (m.group(2), float(m.group(3)), float(m.group(4)))
    out = ["| letters | most frequent letters | frequent letters in usual spots | **information (solver)** |",
           "|---|---|---|---|"]
    for r in rows:
        if all(k in r for k in ("freq", "pos", "info")):
            cell = lambda t: f"{t[0]} · {t[1]:.2f} bits · {t[2]:.0f} left"  # noqa: E731
            out.append(f"| {r['L']} | {cell(r['freq'])} | {cell(r['pos'])} | **{cell(r['info'])}** |")
    return "\n".join(out)


def report(L, r):
    """Detailed per-length report."""
    lt = r["letters"]
    b, bh = r["benchmark"], r["benchmark_hard"]
    o = [f"# {L}-letter Hello Wordl - full report", ""]
    o += [f"Words in list: **{r['n_words']:,}** · everyday words: **{r['n_common']:,}** · "
          f"guessable pool: **{r['n_guess_pool']:,}**", ""]
    o += ["## Best first guesses (exact search over every word)", "",
          "| # | word | exp. guesses* | info (bits) | avg answers left | worst case |", "|---|---|---|---|---|---|"]
    for i, x in enumerate(r["openers"][:15], 1):
        o.append(f"| {i} | **{U(x['word'])}** | {x['expected_guesses']:.3f} | {x['entropy_bits']:.3f} | "
                 f"{x['avg_left']:.0f} | {x['worst_case_left']} |")
    o += ["", "\\* model estimate of total guesses; real averages are in the benchmark below.", "",
          "## Best everyday-word openers", "", "| # | word | info (bits) | avg answers left |", "|---|---|---|---|"]
    for i, x in enumerate(r["common_openers"][:10], 1):
        o.append(f"| {i} | **{U(x['word'])}** | {x['entropy_bits']:.3f} | {x['avg_left']:.0f} |")
    o += ["", "## Best fixed two-word starts (play both, whatever the colours)", "",
          "| first | second | combined info (bits) |", "|---|---|---|"]
    for x in r["pairs"][:10]:
        o.append(f"| {U(x['first'])} | {U(x['second'])} | {x['joint_bits']:.2f} |")
    o += ["", "## Letter probabilities", "",
          "P(letter appears in the answer): " + ", ".join(f"**{U(k)}** {pct(v)}" for k, v in list(lt["presence"].items())[:12]),
          "", "Most likely letter in each position:", "", "| position | top letters |", "|---|---|"]
    for k, v in lt["positional"].items():
        o.append(f"| {k[3:]} | " + ", ".join(f"{U(a)} {pct(p)}" for a, p in list(v.items())[:5]) + " |")
    o += ["", f"- P(answer has a repeated letter): **{pct(lt['p_double_letter'])}**",
          "- Number of vowels (A E I O U): " + ", ".join(f"{k}: {pct(v)}" for k, v in lt["vowel_count"].items() if v >= 0.005),
          "- Common endings: " + ", ".join(f"-{U(k)} {pct(v, 1)}" for k, v in lt["top_endings_3"][:8]),
          "- Common beginnings: " + ", ".join(f"{U(k)}- {pct(v, 1)}" for k, v in lt["top_starts_2"][:8]), ""]
    o += [f"## What your first feedback means (after {U(r['openers'][0]['word'])})", "",
          "| greens | yellows | how often | avg answers still possible |", "|---|---|---|---|"]
    for x in r["first_feedback"]:
        if x["probability"] >= 0.002:
            o.append(f"| {x['greens']} | {x['yellows']} | {pct(x['probability'], 1)} | {x['avg_candidates_left']:.0f} |")
    o += ["", f"## Trap families ({pct(r['trap_share'])} of everyday words sit in a family of 4+)", "",
          "Words that differ in only one letter. If you land in one, don't guess them one by one - "
          "play a word that tests several of the differing letters at once.", ""]
    for t in r["traps"][:12]:
        o.append(f"- `{U(t['pattern'])}` ({t['size']}): " + ", ".join(U(w) for w in t["words"]))
    o += ["", "## Solver benchmark (held-out real answers, 6 tries)", "",
          "| mode | games | avg guesses | win rate | distribution |", "|---|---|---|---|---|"]
    for name, x in (("normal", b), ("hard", bh)):
        o.append(f"| {name} | {x['games']} | {x['avg_guesses']:.3f} | {pct(x['win_rate'], 1)} | "
                 + " · ".join(f"{k}: {v}" for k, v in x["distribution"].items()) + " |")
    if b["failed_words"]:
        o += ["", "Missed (normal mode): " + ", ".join(U(w) for w in b["failed_words"])]
    o += ["", f"Opening book: {r['book_patterns']} first-feedback patterns precomputed "
              f"({pct(r['book_coverage'], 1)} of games). Average live step: {b['avg_live_step_seconds'] * 1000:.0f} ms.", ""]
    return "\n".join(o)


def guide(data):
    D = data
    o = []
    o += ["# How to win Hello Wordl at any length - a probability guide", "",
          "Everything here is computed from the two word files in `data/raw/` (466k-word list + Webster's "
          "dictionary), weighted by how likely each word is to be the answer, and checked against real "
          "Hello Wordl answers the model never saw. Words are shown in CAPITALS; case never matters.", ""]
    o += ["## 1. The rules that matter", "",
          "- 4 to 11 letters, **6 tries at every length**.",
          "- 🟩 green = right letter, right spot · 🟨 yellow = in the word, wrong spot · ⬛ grey = not in the word.",
          "- **Duplicates:** greens are given out first, then yellows from left to right only while the answer still has "
          "unused copies. So if you guess two E's and get one 🟨 and one ⬛, the answer has **exactly one E**.",
          "  Example: guess `EERIE`, answer `THERE` → 🟨⬛🟨⬛🟩.",
          "- A word the game rejects (\"not in word list\") does **not** cost a try.", ""]
    o += ["## 2. The one idea: every guess should split the possible answers as evenly as possible", "",
          "Think of every guess as a question. A question whose answer you could have predicted teaches you nothing. "
          "A colour pattern that could come out hundreds of different ways teaches you a lot. That is measured in "
          "**bits**: each bit halves the number of possible answers.", "",
          "| letters | possible answers* | bits needed | best opener gives |", "|---|---|---|---|"]
    for L in LENGTHS:
        r = D[L]
        import math
        need = math.log2(max(r["n_common"], 2))
        o.append(f"| {L} | ~{r['n_common']:,} everyday words | ~{need:.1f} | {r['openers'][0]['entropy_bits']:.1f} bits |")
    o += ["", "\\* everyday words, i.e. the likely answers. Longer words have more letters to test but **fewer** "
          "similar words, so they are actually *easier*: one good guess often leaves a handful.", ""]
    o += ["## 3. Is the best first word just \"the most common letters\"? No", "",
          "That's the usual human rule, and it's a decent start, but it is beaten at most lengths. Here are three ways "
          "to pick a first word (\"left\" = average possible answers remaining after it):", "", opener_methods(), "",
          "Why frequency alone isn't enough:", "",
          "1. **A letter is most useful when it's in about half the words.** In 8+ letter words E is in ~66% of answers, "
          "so learning \"yes, there's an E\" is less informative than a letter present in ~50%.",
          "2. **Common letters overlap.** A, O and E tend to appear in the *same* words, so testing all three "
          "is partly redundant (ALOE loses to SALE for 4 letters).",
          "3. **Position matters.** S is the most common first letter and E/S/Y are common last letters: "
          "a letter in its usual spot often lands a green, which eliminates far more than a yellow.",
          "4. **After turn 1, frequency stops working at all.** The best 2nd/3rd guess often uses letters you "
          "already know are wrong, purely to split the remaining candidates.", ""]
    o += ["## 4. Best starting words", "",
          "| letters | best overall | best everyday word | best fixed pair (play both) | avg answers left after the opener |",
          "|---|---|---|---|---|"]
    for L in LENGTHS:
        r = D[L]
        best = r["openers"][0]
        com = r["common_openers"][0]
        pr = r["pairs"][0]
        o.append(f"| {L} | **{U(best['word'])}** | {U(com['word'])} | {U(pr['first'])} + {U(pr['second'])} "
                 f"| {best['avg_left']:.0f} |")
    o += ["", "Runners-up (any of these is within a hair of the best):", ""]
    for L in LENGTHS:
        o.append(f"- **{L}:** " + ", ".join(U(x["word"]) for x in D[L]["openers"][1:8]))
    o += ["", "If the game rejects a word (it happens with rarer ones), just use the next one in the list.", ""]
    o += ["## 5. Letter probabilities to memorise", "",
          "![letter presence](output/charts/letter_presence.png)", "",
          "| letters | top letters (P in answer) | P(repeated letter) | most likely last letter |",
          "|---|---|---|---|"]
    for L in LENGTHS:
        lt = D[L]["letters"]
        last = list(lt["positional"][f"pos{L}"].items())[:3]
        o.append(f"| {L} | " + " ".join(f"{U(k)}{v * 100:.0f}" for k, v in list(lt["presence"].items())[:8])
                 + f" | {pct(lt['p_double_letter'])} | " + ", ".join(f"{U(k)} {pct(v)}" for k, v in last) + " |")
    o += ["", "![letter positions](output/charts/letter_positions.png)", "",
          "Patterns worth knowing:", "",
          "- **Repeated letters are common** and get more common with length (see the table). "
          "If you're stuck with few letters found, suspect a double.",
          "- **Endings carry a lot of probability in long words:** " + "; ".join(
              f"{L}: " + ", ".join(f"-{U(k)}" for k, _ in D[L]["letters"]["top_endings_3"][:4]) for L in LENGTHS if L >= 7),
          "- **4-5 letters** are the hardest: many near-identical words (see traps below) and only 6 tries.", ""]
    o += ["## 6. Signs to watch for", "",
          "### After your first guess", "",
          f"Using the best 5-letter opener **{U(D[5]['openers'][0]['word'])}** as the example "
          "(every length has its own table in `output/reports/`):", "",
          "| greens | yellows | how often | avg answers still possible |", "|---|---|---|---|"] if 5 in D else []
    if 5 in D:
        for x in D[5]["first_feedback"]:
            if x["probability"] >= 0.01:
                o.append(f"| {x['greens']} | {x['yellows']} | {pct(x['probability'])} | {x['avg_candidates_left']:.0f} |")
        o += ["", "- **All grey is not bad news**: it happens often and still removes most words. "
              "Play a second word with five *new* common letters.",
              "- **One green is worth about two yellows.** Greens pin a position; yellows only rule one out.",
              "- **Many yellows** (3+) means the letters are right but scrambled: few words fit, so start guessing real candidates.", ""]
    o += ["### Trap families - the #1 way to lose", "",
          "A trap is a set of words that differ in a single position. Guessing them one by one can take more tries "
          "than you have.", ""]
    for L in LENGTHS:
        if D[L]["traps"]:
            t = D[L]["traps"][:3]
            o.append(f"- **{L} letters** ({pct(D[L]['trap_share'])} of everyday words are in a family of 4+): "
                     + "; ".join(f"`{U(x['pattern'])}` → " + " ".join(U(w) for w in x["words"][:8]) for x in t))
    o += ["", "**What to do:** if the possible answers outnumber your remaining tries and they differ in one spot, "
          "spend a guess on a word (even an impossible one) containing as many of the competing letters as you can. "
          "Example: `_IGHT` with F, L, M, N, R, S, T, W possible → a word like FLOWN or NYMPH tests several at once.", "",
          "### Other signs", "",
          "- **Yellow + grey of the same letter** → exactly that many copies, no more.",
          "- **A yellow letter must move.** Never put it back in the same spot; in hard mode the game forces "
          "you to reuse it.",
          "- **Few vowels found by turn 2** → check Y, and words with one vowel repeated.",
          "- **Long words (8+)**: after the first guess, look at the end of the word: -ING, -ED, -ER, -TION, -NESS, "
          "-ABLE and plural -S decide a big chunk of the answer.",
          "- **Two candidates left** → guess the more common word. **Three+ left with turns to spare** → a splitting "
          "word beats guessing a candidate.", ""]
    sc_path = os.path.join(ROOT, "output", "strategy_comparison.json")
    if os.path.exists(sc_path):
        sc = json.load(open(sc_path))
        names = list(sc[0]["strategies"])
        o += ["## 7. Human strategies, tested", "",
              "Each strategy below was played on every held-out real answer. Cells show "
              "**average guesses · win rate** (6 tries). The \"frequency pair\" is the two words made of the most "
              "common letters (second word = the most common *new* letters).", "",
              "| letters | frequency pair | " + " | ".join(names) + " |",
              "|---|---|" + "---|" * len(names)]
        for r in sc:
            cells = []
            for n in names:
                x = r["strategies"].get(n)
                cells.append(f"{x['avg_guesses']:.2f} · {x['win_rate'] * 100:.1f}%" if x else "-")
            o.append(f"| {r['length']} | {U(r['first'])} + {U(r['second'])} | " + " | ".join(cells) + " |")
        o += ["", "What this shows:", "",
              "- **Short words (4-5 letters): simple rules lose games.** Many near-identical words "
              "means guessing \"the most common word that fits\" walks you into traps; the solver's probe words "
              "are what keep the win rate near 100%.",
              "- **Long words (8+): almost any sensible start works.** One frequency word usually leaves a handful "
              "of words, so starting to guess immediately is close to optimal.",
              "- **Don't burn a second fixed word on long words** - it costs about half a guess.", ""]
    o += ["## 8. A simple human recipe", "",
          "1. Turn 1: play the opener for your length (table above).",
          "2. Turn 2: if you got ≤1 hit, play the fixed partner word (new letters). Otherwise pick a word that keeps your "
          "greens, moves your yellows and adds new common letters.",
          "3. Turn 3+: count the words that still fit. If ≤ remaining tries, guess the most common one. If more, "
          "play a splitting word first (see traps).",
          "4. Use the solver (`python -m wordl play -n 7` or the web page) to check yourself; it shows the best word "
          "*and why* (expected guesses, bits, chance to win now).", ""]
    o += ["## 9. How good is the algorithm?", "",
          "Tested on real Hello Wordl answers it **never saw during tuning** (held-out half), 6 tries:", "",
          "| letters | games | avg guesses | win rate | hard-mode avg | hard-mode win |", "|---|---|---|---|---|---|"]
    for L in LENGTHS:
        b, h = D[L]["benchmark"], D[L]["benchmark_hard"]
        o.append(f"| {L} | {b['games']} | **{b['avg_guesses']:.2f}** | **{pct(b['win_rate'], 1)}** | "
                 f"{h['avg_guesses']:.2f} | {pct(h['win_rate'], 1)} |")
    o += ["", "![benchmark](output/charts/benchmark.png)", "",
          "Speed: turns 1-2 are instant lookups (precomputed opening book); later turns are computed live in "
          "milliseconds (Python ≈ " + f"{max(D[L]['benchmark']['avg_live_step_seconds'] for L in LENGTHS) * 1000:.0f}"
          " ms worst average; the browser version is similar).", ""]
    o += ["## 10. How the algorithm works", "",
          "1. **Prior** - every word gets P(answer). Class = Webster definitions count × how often the word is *used* "
          "inside the 54k definitions (a word-frequency signal), plus plurals/inflections. Class weights are "
          "calibrated on half of Hello Wordl's public answer list (`scripts/calibrate.py`). Only words the game "
          "accepts are kept, so names (JAMEL, PATEL) and abbreviations never count as possible answers.",
          "2. **Feedback** - exact Hello Wordl colouring including duplicates, vectorised with NumPy.",
          "3. **Score every guess** - group all candidates by the pattern they'd produce, then compute information "
          "(entropy), P(win now) and an *expected number of guesses* "
          "E = 1 + Σ P(pattern) × F(bits left in that group).",
          "4. **Endgame search** - with ≤80 candidates it searches the game tree 1-2 moves deep, solving the last two "
          "turns exactly and adding a heavy penalty for running out of tries, so it sacrifices a guess to escape traps.",
          "5. **Opening book** - best first word and the best reply to every likely first feedback are precomputed.",
          "6. **Tuning** - prior strength, fail penalty and search width were tuned on the training half only.", ""]
    return "\n".join(o)


def main():
    data = {L: load(L) for L in LENGTHS}
    os.makedirs(os.path.join(ROOT, "output", "reports"), exist_ok=True)
    for L, r in data.items():
        with open(os.path.join(ROOT, "output", "reports", f"len_{L:02d}.md"), "w") as f:
            f.write(report(L, r))
    with open(os.path.join(ROOT, "STRATEGY_GUIDE.md"), "w") as f:
        f.write(guide(data))
    print("wrote STRATEGY_GUIDE.md and", len(data), "reports")


if __name__ == "__main__":
    main()
