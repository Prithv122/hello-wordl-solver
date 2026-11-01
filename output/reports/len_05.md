# 5-letter Hello Wordl - full report

Words in list: **10,443** · everyday words: **1,542** · guessable pool: **3,668**

## Best first guesses (exact search over every word)

| # | word | exp. guesses* | info (bits) | avg answers left | worst case |
|---|---|---|---|---|---|
| 1 | **TEARS** | 4.172 | 6.168 | 246 | 718 |
| 2 | **SLATE** | 4.187 | 6.126 | 262 | 723 |
| 3 | **LARES** | 4.191 | 6.115 | 215 | 685 |
| 4 | **STARE** | 4.204 | 6.078 | 253 | 718 |
| 5 | **RATES** | 4.192 | 6.114 | 226 | 718 |
| 6 | **TALES** | 4.200 | 6.089 | 239 | 723 |
| 7 | **TRIES** | 4.217 | 6.039 | 271 | 955 |
| 8 | **RALES** | 4.211 | 6.058 | 220 | 685 |
| 9 | **SNARE** | 4.228 | 6.008 | 258 | 689 |
| 10 | **RAISE** | 4.229 | 6.005 | 245 | 638 |
| 11 | **STALE** | 4.230 | 6.002 | 275 | 723 |
| 12 | **LEARS** | 4.216 | 6.044 | 241 | 685 |
| 13 | **REALS** | 4.217 | 6.042 | 239 | 685 |
| 14 | **SANER** | 4.218 | 6.038 | 234 | 689 |
| 15 | **TAELS** | 4.220 | 6.033 | 274 | 919 |

\* model estimate of total guesses; real averages are in the benchmark below.

## Best everyday-word openers

| # | word | info (bits) | avg answers left |
|---|---|---|---|
| 1 | **TEARS** | 6.168 | 246 |
| 2 | **SLATE** | 6.126 | 262 |
| 3 | **STARE** | 6.078 | 253 |
| 4 | **TRIES** | 6.039 | 271 |
| 5 | **SNARE** | 6.008 | 258 |
| 6 | **RAISE** | 6.005 | 245 |
| 7 | **STALE** | 6.002 | 275 |
| 8 | **ARISE** | 5.945 | 268 |
| 9 | **ALOES** | 5.943 | 246 |
| 10 | **LEAST** | 5.937 | 298 |

## Best fixed two-word starts (play both, whatever the colours)

| first | second | combined info (bits) |
|---|---|---|
| LARES | POINT | 9.82 |
| LARES | TONIC | 9.80 |
| LARES | COUNT | 9.76 |
| SLATE | DORIC | 9.73 |
| SLATE | MINOR | 9.73 |
| SLATE | ROUND | 9.68 |
| TEARS | COULD | 9.68 |
| SLATE | GROIN | 9.67 |
| SLATE | ROBIN | 9.65 |
| TRIES | BLAND | 9.65 |

## Letter probabilities

P(letter appears in the answer): **E** 48%, **A** 40%, **S** 39%, **R** 35%, **O** 30%, **T** 29%, **I** 27%, **L** 27%, **N** 23%, **C** 18%, **D** 18%, **U** 17%

Most likely letter in each position:

| position | top letters |
|---|---|
| 1 | S 16%, C 8%, B 7%, T 7%, P 6% |
| 2 | O 14%, A 14%, E 11%, R 10%, I 10% |
| 3 | A 14%, I 11%, O 10%, R 8%, E 8% |
| 4 | E 17%, N 7%, L 7%, A 7%, T 7% |
| 5 | S 17%, E 17%, Y 10%, T 9%, R 8% |

- P(answer has a repeated letter): **31%**
- Number of vowels (A E I O U): 1: 31%, 2: 60%, 3: 9%
- Common endings: -TCH 0.9%, -TER 0.7%, -ING 0.7%, -NES 0.6%, -LLY 0.6%, -VER 0.6%, -AIN 0.5%, -IDE 0.5%
- Common beginnings: ST- 2.8%, SH- 2.1%, SP- 1.7%, CH- 1.6%, GR- 1.6%, CO- 1.6%, BR- 1.5%, SC- 1.5%

## What your first feedback means (after TEARS)

| greens | yellows | how often | avg answers still possible |
|---|---|---|---|
| 0 | 0 | 6.4% | 718 |
| 0 | 1 | 18.6% | 506 |
| 0 | 2 | 21.7% | 242 |
| 0 | 3 | 8.1% | 97 |
| 0 | 4 | 1.6% | 25 |
| 1 | 0 | 8.4% | 370 |
| 1 | 1 | 14.8% | 175 |
| 1 | 2 | 8.6% | 58 |
| 1 | 3 | 1.6% | 15 |
| 2 | 0 | 4.3% | 99 |
| 2 | 1 | 3.3% | 28 |
| 2 | 2 | 0.9% | 6 |
| 3 | 0 | 1.0% | 20 |
| 3 | 1 | 0.5% | 4 |

## Trap families (10% of everyday words sit in a family of 4+)

Words that differ in only one letter. If you land in one, don't guess them one by one - play a word that tests several of the differing letters at once.

- `_IGHT` (9): EIGHT, FIGHT, HIGHT, LIGHT, MIGHT, NIGHT, RIGHT, SIGHT, TIGHT
- `_OUND` (8): BOUND, FOUND, HOUND, MOUND, POUND, ROUND, SOUND, WOUND
- `_ATCH` (6): CATCH, HATCH, LATCH, MATCH, PATCH, WATCH
- `GRA_E` (6): GRACE, GRADE, GRAPE, GRATE, GRAVE, GRAZE
- `SHA_E` (6): SHADE, SHAKE, SHALE, SHAME, SHAPE, SHARE
- `STA_E` (6): STAGE, STAKE, STALE, STARE, STATE, STAVE
- `BEA_S` (6): BEADS, BEAKS, BEAMS, BEANS, BEARS, BEATS
- `_ABLE` (5): CABLE, FABLE, GABLE, SABLE, TABLE
- `_ASTE` (5): CASTE, HASTE, PASTE, TASTE, WASTE
- `_INES` (5): LINES, MINES, SINES, VINES, WINES
- `_OWER` (5): BOWER, DOWER, LOWER, POWER, TOWER
- `_AUNT` (5): DAUNT, HAUNT, JAUNT, TAUNT, VAUNT

## Solver benchmark (held-out real answers, 6 tries)

| mode | games | avg guesses | win rate | distribution |
|---|---|---|---|---|
| normal | 712 | 3.560 | 100.0% | 2: 23 · 3: 362 · 4: 249 · 5: 61 · 6: 17 |
| hard | 712 | 3.657 | 98.6% | 2: 47 · 3: 308 · 4: 247 · 5: 82 · 6: 18 · 7: 4 · 8: 3 · 9: 2 · 10: 1 |

Opening book: 147 first-feedback patterns precomputed (99.5% of games). Average live step: 6 ms.
