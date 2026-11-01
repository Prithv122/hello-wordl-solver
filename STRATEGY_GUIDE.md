# How to win Hello Wordl at any length - a probability guide

Everything here is computed from the two word files in `data/raw/` (466k-word list + Webster's dictionary), weighted by how likely each word is to be the answer, and checked against real Hello Wordl answers the model never saw. Words are shown in CAPITALS; case never matters.

## 1. The rules that matter

- 4 to 11 letters, **6 tries at every length**.
- 🟩 green = right letter, right spot · 🟨 yellow = in the word, wrong spot · ⬛ grey = not in the word.
- **Duplicates:** greens are given out first, then yellows from left to right only while the answer still has unused copies. So if you guess two E's and get one 🟨 and one ⬛, the answer has **exactly one E**.
  Example: guess `EERIE`, answer `THERE` → 🟨⬛🟨⬛🟩.
- A word the game rejects ("not in word list") does **not** cost a try.

## 2. The one idea: every guess should split the possible answers as evenly as possible

Think of every guess as a question. A question whose answer you could have predicted teaches you nothing. A colour pattern that could come out hundreds of different ways teaches you a lot. That is measured in **bits**: each bit halves the number of possible answers.

| letters | possible answers* | bits needed | best opener gives |
|---|---|---|---|
| 4 | ~1,256 everyday words | ~10.3 | 4.6 bits |
| 5 | ~1,579 everyday words | ~10.6 | 6.1 bits |
| 6 | ~2,220 everyday words | ~11.1 | 7.6 bits |
| 7 | ~2,226 everyday words | ~11.1 | 9.0 bits |
| 8 | ~1,933 everyday words | ~10.9 | 10.1 bits |
| 9 | ~1,616 everyday words | ~10.7 | 11.1 bits |
| 10 | ~1,147 everyday words | ~10.2 | 11.5 bits |
| 11 | ~649 everyday words | ~9.3 | 11.8 bits |

\* everyday words, i.e. the likely answers. Longer words have more letters to test but **fewer** similar words, so they are actually *easier*: one good guess often leaves a handful.

## 3. Is the best first word just "the most common letters"? No

That's the usual human rule, and it's a decent start, but it is beaten at most lengths. Here are three ways to pick a first word ("left" = average possible answers remaining after it):

| letters | most frequent letters | frequent letters in usual spots | **information (solver)** |
|---|---|---|---|
| 4 | ALOE · 4.27 bits · 863 left | SALE · 4.56 bits · 753 left | **SALE · 4.56 bits · 753 left** |
| 5 | TEARS · 6.15 bits · 560 left | CANES · 5.79 bits · 650 left | **TEARS · 6.15 bits · 560 left** |
| 6 | SATIRE · 7.56 bits · 342 left | SALTED · 7.30 bits · 416 left | **SATIRE · 7.56 bits · 342 left** |
| 7 | ARSENIC · 8.06 bits · 324 left | PARTIES · 8.85 bits · 182 left | **PARTIES · 8.85 bits · 182 left** |
| 8 | ENTRAILS · 9.78 bits · 98 left | COUNTIES · 9.79 bits · 106 left | **CURTAINS · 9.92 bits · 97 left** |
| 9 | DOCTRINES · 10.76 bits · 56 left | COMPANIES · 10.58 bits · 62 left | **CENTURIES · 10.89 bits · 43 left** |
| 10 | TOURMALINE · 11.34 bits · 25 left | DECORATING · 11.23 bits · 28 left | **MERCANTILE · 11.43 bits · 23 left** |
| 11 | PERSONALITY · 11.64 bits · 15 left | PERSONALITY · 11.64 bits · 15 left | **PERSECUTION · 11.67 bits · 13 left** |

Why frequency alone isn't enough:

1. **A letter is most useful when it's in about half the words.** In 8+ letter words E is in ~66% of answers, so learning "yes, there's an E" is less informative than a letter present in ~50%.
2. **Common letters overlap.** A, O and E tend to appear in the *same* words, so testing all three is partly redundant (ALOE loses to SALE for 4 letters).
3. **Position matters.** S is the most common first letter and E/S/Y are common last letters: a letter in its usual spot often lands a green, which eliminates far more than a yellow.
4. **After turn 1, frequency stops working at all.** The best 2nd/3rd guess often uses letters you already know are wrong, purely to split the remaining candidates.

## 4. Best starting words

| letters | best overall | best everyday word | best fixed pair (play both) | avg answers left after the opener |
|---|---|---|---|---|
| 4 | **SALE** | SALE | SALE + TORN | 753 |
| 5 | **TEARS** | TEARS | LARES + TONIC | 560 |
| 6 | **SATIRE** | SATIRE | SALTER + CONIUM | 342 |
| 7 | **SALTIRE** | PARTIES | PARTIES + COLUMNS | 156 |
| 8 | **NOTARIES** | CURTAINS | CURTAINS + EMPLOYED | 76 |
| 9 | **SARCOLINE** | CENTURIES | CENTURIES + GALLOPADE | 39 |
| 10 | **AEROLITICS** | MERCANTILE | MERCANTILE + INDIGENOUS | 21 |
| 11 | **UNREALITIES** | PERSECUTION | UNREALITIES + BRACHIOPODA | 11 |

Runners-up (any of these is within a hair of the best):

- **4:** TALE, LARE, SEAL, RASE, SATE, LATE, RATE
- **5:** SLATE, LARES, STARE, RATES, TALES, RAISE, AIRES
- **6:** SANTER, RAINES, SALTER, SALINE, SAILER, SALITE, SERIAL
- **7:** SALTIER, PARTIES, SARDINE, RETAINS, RETAILS, RATLINS, LATRINE
- **8:** CURTAINS, GANTRIES, LATRINES, RATLINES, REALTIES, RETINALS, ARTICLES
- **9:** NECTARIES, CENTURIES, COUNTRIES, LARCENIES, REACTIONS, PENALTIES, RELATIONS
- **10:** MERCANTILE, LACUSTRINE, LAURESTINE, TOURMALINE, NORMALCIES, RECUSATION, CALEDONITE
- **11:** PERSECUTION, ULCERATIONS, AERONAUTICS, CUSTOMARILY, PERSONALITY, DECORATIONS, LACERATIONS

If the game rejects a word (it happens with rarer ones), just use the next one in the list.

## 5. Letter probabilities to memorise

![letter presence](output/charts/letter_presence.png)

| letters | top letters (P in answer) | P(repeated letter) | most likely last letter |
|---|---|---|---|
| 4 | E38 A37 O26 L24 R24 S24 I22 T22 | 19% | E 17%, T 11%, S 9% |
| 5 | E47 A42 S37 R35 O29 T29 I28 L28 | 32% | E 17%, S 16%, T 9% |
| 6 | E62 A45 R44 I36 S36 N33 T33 L32 | 52% | E 16%, S 14%, R 10% |
| 7 | E64 A49 I49 R47 N43 S41 T37 L35 | 66% | E 17%, S 16%, D 11% |
| 8 | E66 I57 A53 R51 N49 S45 T44 O40 | 79% | S 18%, E 16%, D 12% |
| 9 | E73 I63 A56 R56 N55 T51 S49 O45 | 89% | E 19%, S 19%, D 11% |
| 10 | E75 I70 N62 A59 T59 R57 O53 S50 | 95% | E 18%, S 18%, N 10% |
| 11 | I76 E75 N68 T66 A65 R63 O59 S52 | 98% | S 18%, E 17%, N 13% |

![letter positions](output/charts/letter_positions.png)

Patterns worth knowing:

- **Repeated letters are common** and get more common with length (see the table). If you're stuck with few letters found, suspect a double.
- **Endings carry a lot of probability in long words:** 7: -ING, -TED, -ERS, -ISH; 8: -ING, -ESS, -TED, -ATE; 9: -ING, -ION, -ATE, -ESS; 10: -ING, -ION, -OUS, -ENT; 11: -ION, -ING, -OUS, -ENT
- **4-5 letters** are the hardest: many near-identical words (see traps below) and only 6 tries.

## 6. Signs to watch for

### After your first guess

Using the best 5-letter opener **TEARS** as the example (every length has its own table in `output/reports/`):

| greens | yellows | how often | avg answers still possible |
|---|---|---|---|
| 0 | 0 | 6% | 1545 |
| 0 | 1 | 19% | 1432 |
| 0 | 2 | 23% | 620 |
| 0 | 3 | 8% | 213 |
| 0 | 4 | 2% | 42 |
| 1 | 0 | 8% | 570 |
| 1 | 1 | 15% | 264 |
| 1 | 2 | 8% | 80 |
| 1 | 3 | 2% | 19 |
| 2 | 0 | 4% | 130 |
| 2 | 1 | 3% | 33 |

- **All grey is not bad news**: it happens often and still removes most words. Play a second word with five *new* common letters.
- **One green is worth about two yellows.** Greens pin a position; yellows only rule one out.
- **Many yellows** (3+) means the letters are right but scrambled: few words fit, so start guessing real candidates.

### Trap families - the #1 way to lose

A trap is a set of words that differ in a single position. Guessing them one by one can take more tries than you have.

- **4 letters** (56% of everyday words are in a family of 4+): `_EAR` → BEAR DEAR FEAR GEAR HEAR NEAR PEAR REAR; `_ALE` → BALE DALE GALE HALE KALE MALE PALE SALE; `_AIL` → BAIL FAIL HAIL JAIL MAIL NAIL RAIL SAIL
- **5 letters** (10% of everyday words are in a family of 4+): `_IGHT` → EIGHT FIGHT HIGHT LIGHT MIGHT NIGHT RIGHT SIGHT; `_OUND` → BOUND FOUND HOUND MOUND POUND ROUND SOUND WOUND; `_ATCH` → CATCH HATCH LATCH MATCH PATCH WATCH
- **6 letters** (3% of everyday words are in a family of 4+): `_ALLOW` → FALLOW MALLOW SALLOW TALLOW WALLOW; `_UMBLE` → FUMBLE HUMBLE JUMBLE RUMBLE TUMBLE; `_ATHER` → FATHER GATHER LATHER RATHER
- **7 letters** (3% of everyday words are in a family of 4+): `_EARING` → BEARING GEARING HEARING TEARING WEARING; `HEA_ING` → HEADING HEALING HEARING HEATING HEAVING; `_ETTING` → BETTING GETTING LETTING NETTING SETTING

**What to do:** if the possible answers outnumber your remaining tries and they differ in one spot, spend a guess on a word (even an impossible one) containing as many of the competing letters as you can. Example: `_IGHT` with F, L, M, N, R, S, T, W possible → a word like FLOWN or NYMPH tests several at once.

### Other signs

- **Yellow + grey of the same letter** → exactly that many copies, no more.
- **A yellow letter must move.** Never put it back in the same spot; in hard mode the game forces you to reuse it.
- **Few vowels found by turn 2** → check Y, and words with one vowel repeated.
- **Long words (8+)**: after the first guess, look at the end of the word: -ING, -ED, -ER, -TION, -NESS, -ABLE and plural -S decide a big chunk of the answer.
- **Two candidates left** → guess the more common word. **Three+ left with turns to spare** → a splitting word beats guessing a candidate.

## 7. A simple human recipe

1. Turn 1: play the opener for your length (table above).
2. Turn 2: if you got ≤1 hit, play the fixed partner word (new letters). Otherwise pick a word that keeps your greens, moves your yellows and adds new common letters.
3. Turn 3+: count the words that still fit. If ≤ remaining tries, guess the most common one. If more, play a splitting word first (see traps).
4. Use the solver (`python -m wordl play -n 7` or the web page) to check yourself; it shows the best word *and why* (expected guesses, bits, chance to win now).

## 8. How good is the algorithm?

Tested on real Hello Wordl answers it **never saw during tuning** (held-out half), 6 tries:

| letters | games | avg guesses | win rate | hard-mode avg | hard-mode win |
|---|---|---|---|---|---|
| 4 | 652 | **4.42** | **97.4%** | 4.83 | 85.4% |
| 5 | 712 | **3.60** | **99.6%** | 3.71 | 97.9% |
| 6 | 1012 | **3.31** | **99.9%** | 3.40 | 98.8% |
| 7 | 1057 | **3.06** | **100.0%** | 3.12 | 99.4% |
| 8 | 980 | **2.84** | **100.0%** | 2.88 | 99.9% |
| 9 | 903 | **2.63** | **100.0%** | 2.67 | 100.0% |
| 10 | 724 | **2.52** | **100.0%** | 2.53 | 100.0% |
| 11 | 472 | **2.44** | **100.0%** | 2.46 | 100.0% |

![benchmark](output/charts/benchmark.png)

Speed: turns 1-2 are instant lookups (precomputed opening book); later turns are computed live in milliseconds (Python ≈ 8 ms worst average; the browser version is similar).

## 9. How the algorithm works

1. **Prior** - every word gets P(answer). Class = Webster definitions count × how often the word is *used* inside the 54k definitions (a word-frequency signal), plus plurals/inflections. Class weights are calibrated on half of Hello Wordl's public answer list (`scripts/calibrate.py`).
2. **Feedback** - exact Hello Wordl colouring including duplicates, vectorised with NumPy.
3. **Score every guess** - group all candidates by the pattern they'd produce, then compute information (entropy), P(win now) and an *expected number of guesses* E = 1 + Σ P(pattern) × F(bits left in that group).
4. **Endgame search** - with ≤80 candidates it searches the game tree 1-2 moves deep, solving the last two turns exactly and adding a heavy penalty for running out of tries, so it sacrifices a guess to escape traps.
5. **Opening book** - best first word and the best reply to every likely first feedback are precomputed.
6. **Tuning** - prior strength, fail penalty and search width were tuned on the training half only.
