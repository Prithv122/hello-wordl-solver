# 4-letter Hello Wordl - full report

Words in list: **10,521** · everyday words: **1,256** · guessable pool: **2,381**

## Best first guesses (exact search over every word)

| # | word | exp. guesses* | info (bits) | avg answers left | worst case |
|---|---|---|---|---|---|
| 1 | **SALE** | 4.655 | 4.564 | 753 | 2080 |
| 2 | **TALE** | 4.674 | 4.509 | 867 | 2484 |
| 3 | **LARE** | 4.670 | 4.525 | 827 | 2434 |
| 4 | **SEAL** | 4.690 | 4.465 | 809 | 2080 |
| 5 | **RASE** | 4.682 | 4.491 | 765 | 2018 |
| 6 | **SATE** | 4.694 | 4.455 | 820 | 2124 |
| 7 | **LATE** | 4.698 | 4.442 | 880 | 2484 |
| 8 | **RATE** | 4.700 | 4.437 | 883 | 2444 |
| 9 | **RALE** | 4.670 | 4.522 | 826 | 2434 |
| 10 | **SEAT** | 4.702 | 4.432 | 873 | 2124 |
| 11 | **REAL** | 4.702 | 4.431 | 883 | 2434 |
| 12 | **LEAS** | 4.691 | 4.465 | 806 | 2080 |
| 13 | **SANE** | 4.710 | 4.410 | 816 | 2096 |
| 14 | **TEAL** | 4.713 | 4.401 | 932 | 2484 |
| 15 | **TAEL** | 4.694 | 4.454 | 892 | 2484 |

\* model estimate of total guesses; real averages are in the benchmark below.

## Best everyday-word openers

| # | word | info (bits) | avg answers left |
|---|---|---|---|
| 1 | **SALE** | 4.564 | 753 |
| 2 | **TALE** | 4.509 | 867 |
| 3 | **SEAL** | 4.465 | 809 |
| 4 | **SATE** | 4.455 | 820 |
| 5 | **LATE** | 4.442 | 880 |
| 6 | **RATE** | 4.437 | 883 |
| 7 | **SEAT** | 4.432 | 873 |
| 8 | **REAL** | 4.431 | 883 |
| 9 | **SANE** | 4.410 | 816 |
| 10 | **TEAL** | 4.401 | 932 |

## Best fixed two-word starts (play both, whatever the colours)

| first | second | combined info (bits) |
|---|---|---|
| SALE | TORN | 7.77 |
| LARE | TONS | 7.75 |
| SALE | DIRT | 7.72 |
| SALE | RIOT | 7.72 |
| SALE | PORT | 7.69 |
| SEAL | TORN | 7.68 |
| SATE | ROIL | 7.67 |
| SATE | LORD | 7.65 |
| LARE | DOTS | 7.65 |
| SEAL | RIOT | 7.64 |

## Letter probabilities

P(letter appears in the answer): **E** 38%, **A** 37%, **O** 26%, **L** 24%, **R** 24%, **S** 24%, **I** 22%, **T** 22%, **N** 18%, **D** 15%, **U** 14%, **M** 13%

Most likely letter in each position:

| position | top letters |
|---|---|
| 1 | S 9%, B 7%, P 7%, C 6%, L 6% |
| 2 | A 20%, O 18%, E 14%, I 13%, U 9% |
| 3 | A 10%, R 10%, L 9%, E 9%, N 8% |
| 4 | E 17%, T 11%, S 9%, L 7%, D 7% |

- P(answer has a repeated letter): **19%**
- Number of vowels (A E I O U): 0: 1%, 1: 51%, 2: 46%, 3: 1%
- Common endings: -EAR 0.7%, -ILL 0.7%, -AIL 0.6%, -ARE 0.6%, -ATE 0.6%, -ENT 0.6%, -OLD 0.6%, -ALL 0.6%
- Common beginnings: CO- 1.9%, BA- 1.7%, CA- 1.7%, BO- 1.6%, MA- 1.6%, HA- 1.6%, PA- 1.6%, LA- 1.6%

## What your first feedback means (after SALE)

| greens | yellows | how often | avg answers still possible |
|---|---|---|---|
| 0 | 0 | 17.6% | 2080 |
| 0 | 1 | 23.7% | 868 |
| 0 | 2 | 11.7% | 246 |
| 0 | 3 | 1.7% | 49 |
| 1 | 0 | 22.7% | 644 |
| 1 | 1 | 11.2% | 124 |
| 1 | 2 | 1.2% | 14 |
| 2 | 0 | 7.7% | 100 |
| 2 | 1 | 1.2% | 9 |
| 3 | 0 | 1.0% | 12 |

## Trap families (56% of everyday words sit in a family of 4+)

Words that differ in only one letter. If you land in one, don't guess them one by one - play a word that tests several of the differing letters at once.

- `_EAR` (11): BEAR, DEAR, FEAR, GEAR, HEAR, NEAR, PEAR, REAR, TEAR, WEAR, YEAR
- `_ALE` (10): BALE, DALE, GALE, HALE, KALE, MALE, PALE, SALE, TALE, WALE
- `_AIL` (10): BAIL, FAIL, HAIL, JAIL, MAIL, NAIL, RAIL, SAIL, TAIL, WAIL
- `_AKE` (9): BAKE, CAKE, HAKE, LAKE, MAKE, RAKE, SAKE, TAKE, WAKE
- `_ARE` (9): BARE, CARE, DARE, FARE, HARE, MARE, PARE, RARE, WARE
- `_ILL` (9): BILL, FILL, GILL, HILL, KILL, MILL, PILL, TILL, WILL
- `_ATE` (9): DATE, FATE, GATE, HATE, LATE, MATE, PATE, RATE, SATE
- `_ORE` (8): BORE, CORE, FORE, GORE, LORE, MORE, SORE, WORE
- `_EAL` (8): DEAL, HEAL, MEAL, REAL, SEAL, TEAL, WEAL, ZEAL
- `_ELL` (8): BELL, CELL, FELL, HELL, SELL, TELL, WELL, YELL
- `_ICK` (8): KICK, LICK, NICK, PICK, RICK, SICK, TICK, WICK
- `_ACK` (8): BACK, HACK, JACK, LACK, PACK, RACK, SACK, TACK

## Solver benchmark (held-out real answers, 6 tries)

| mode | games | avg guesses | win rate | distribution |
|---|---|---|---|---|
| normal | 652 | 4.419 | 97.4% | 2: 9 · 3: 114 · 4: 258 · 5: 165 · 6: 89 · 7: 7 · 8: 9 · 9: 1 |
| hard | 652 | 4.828 | 85.4% | 2: 26 · 3: 129 · 4: 201 · 5: 117 · 6: 84 · 7: 31 · 8: 23 · 9: 20 · 10: 7 · 11: 8 · 12: 2 · 13: 3 · 14: 1 |

Missed (normal mode): JAZZ, HAST, BADE, JUNK, MART, COLA, POLO, CHEZ, LULL, MORT, QUIZ, BUNK, GAOL, NANA, MORN, PAIL, DILL

Opening book: 52 first-feedback patterns precomputed (99.6% of games). Average live step: 4 ms.
