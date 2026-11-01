# 5-letter Hello Wordl - full report

Words in list: **22,223** · everyday words: **1,579** · guessable pool: **4,363**

## Best first guesses (exact search over every word)

| # | word | exp. guesses* | info (bits) | avg answers left | worst case |
|---|---|---|---|---|---|
| 1 | **TEARS** | 4.259 | 6.146 | 560 | 2156 |
| 2 | **SLATE** | 4.270 | 6.115 | 599 | 2260 |
| 3 | **LARES** | 4.265 | 6.130 | 470 | 1404 |
| 4 | **STARE** | 4.289 | 6.061 | 576 | 2156 |
| 5 | **RATES** | 4.274 | 6.105 | 517 | 1545 |
| 6 | **TALES** | 4.282 | 6.083 | 545 | 1602 |
| 7 | **RAISE** | 4.299 | 6.034 | 500 | 1198 |
| 8 | **AIRES** | 4.284 | 6.077 | 481 | 1891 |
| 9 | **RALES** | 4.287 | 6.069 | 486 | 1404 |
| 10 | **SATLE** | 4.275 | 6.101 | 559 | 1602 |
| 11 | **SANER** | 4.290 | 6.058 | 497 | 1358 |
| 12 | **SNARE** | 4.306 | 6.013 | 552 | 1758 |
| 13 | **LEARS** | 4.295 | 6.047 | 530 | 1844 |
| 14 | **TRIES** | 4.310 | 6.002 | 648 | 2472 |
| 15 | **REALS** | 4.295 | 6.046 | 529 | 1844 |

\* model estimate of total guesses; real averages are in the benchmark below.

## Best everyday-word openers

| # | word | info (bits) | avg answers left |
|---|---|---|---|
| 1 | **TEARS** | 6.146 | 560 |
| 2 | **SLATE** | 6.115 | 599 |
| 3 | **STARE** | 6.061 | 576 |
| 4 | **RAISE** | 6.034 | 500 |
| 5 | **SNARE** | 6.013 | 552 |
| 6 | **TRIES** | 6.002 | 648 |
| 7 | **STALE** | 5.990 | 625 |
| 8 | **ARISE** | 5.973 | 554 |
| 9 | **LEAST** | 5.946 | 652 |
| 10 | **ALOES** | 5.934 | 587 |

## Best fixed two-word starts (play both, whatever the colours)

| first | second | combined info (bits) |
|---|---|---|
| LARES | TONIC | 9.87 |
| LARES | POINT | 9.87 |
| LARES | COUNT | 9.81 |
| SLATE | MINOR | 9.78 |
| SLATE | DORIC | 9.78 |
| SLATE | GROIN | 9.73 |
| SLATE | ROUND | 9.72 |
| SLATE | ROBIN | 9.72 |
| TEARS | COULD | 9.69 |
| LARES | MOUNT | 9.69 |

## Letter probabilities

P(letter appears in the answer): **E** 47%, **A** 42%, **S** 37%, **R** 35%, **O** 29%, **T** 29%, **I** 28%, **L** 28%, **N** 24%, **C** 18%, **U** 18%, **D** 17%

Most likely letter in each position:

| position | top letters |
|---|---|
| 1 | S 15%, C 8%, B 7%, T 7%, A 7% |
| 2 | A 15%, O 14%, E 11%, R 10%, I 9% |
| 3 | A 14%, I 10%, O 10%, R 9%, E 8% |
| 4 | E 16%, N 7%, A 7%, L 7%, I 7% |
| 5 | E 17%, S 16%, T 9%, Y 9%, R 8% |

- P(answer has a repeated letter): **32%**
- Number of vowels (A E I O U): 1: 30%, 2: 60%, 3: 10%
- Common endings: -TCH 0.9%, -TER 0.7%, -ING 0.7%, -VER 0.6%, -LLY 0.6%, -NES 0.6%, -AIN 0.5%, -IDE 0.5%
- Common beginnings: ST- 2.7%, SH- 2.0%, GR- 1.6%, SP- 1.6%, CH- 1.6%, CA- 1.5%, SC- 1.5%, CO- 1.5%

## What your first feedback means (after TEARS)

| greens | yellows | how often | avg answers still possible |
|---|---|---|---|
| 0 | 0 | 6.3% | 1545 |
| 0 | 1 | 19.0% | 1432 |
| 0 | 2 | 22.6% | 620 |
| 0 | 3 | 8.1% | 213 |
| 0 | 4 | 1.6% | 42 |
| 1 | 0 | 8.2% | 570 |
| 1 | 1 | 14.6% | 264 |
| 1 | 2 | 8.4% | 80 |
| 1 | 3 | 1.5% | 19 |
| 2 | 0 | 4.0% | 130 |
| 2 | 1 | 3.1% | 33 |
| 2 | 2 | 0.8% | 7 |
| 3 | 0 | 0.9% | 21 |
| 3 | 1 | 0.5% | 5 |

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
| normal | 712 | 3.603 | 99.6% | 2: 20 · 3: 364 · 4: 229 · 5: 80 · 6: 16 · 7: 3 |
| hard | 712 | 3.713 | 97.9% | 2: 42 · 3: 323 · 4: 214 · 5: 92 · 6: 26 · 7: 6 · 8: 6 · 9: 1 · 10: 2 |

Missed (normal mode): LASER, BATCH, BOXER

Opening book: 147 first-feedback patterns precomputed (99.5% of games). Average live step: 6 ms.
