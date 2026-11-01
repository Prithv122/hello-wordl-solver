# 4-letter Hello Wordl - full report

Words in list: **3,947** · everyday words: **1,512** · guessable pool: **1,875**

## Best first guesses (exact search over every word)

| # | word | exp. guesses* | info (bits) | avg answers left | worst case |
|---|---|---|---|---|---|
| 1 | **SALE** | 4.509 | 4.567 | 264 | 689 |
| 2 | **TALE** | 4.533 | 4.498 | 323 | 921 |
| 3 | **SATE** | 4.543 | 4.473 | 285 | 722 |
| 4 | **SEAL** | 4.543 | 4.471 | 280 | 689 |
| 5 | **SEAT** | 4.546 | 4.461 | 298 | 722 |
| 6 | **LEAS** | 4.537 | 4.490 | 275 | 689 |
| 7 | **RASE** | 4.546 | 4.464 | 279 | 689 |
| 8 | **LATE** | 4.559 | 4.426 | 329 | 921 |
| 9 | **SANE** | 4.566 | 4.407 | 294 | 719 |
| 10 | **RATE** | 4.569 | 4.398 | 341 | 935 |
| 11 | **TEAL** | 4.571 | 4.391 | 343 | 921 |
| 12 | **RALE** | 4.545 | 4.467 | 320 | 918 |
| 13 | **REAL** | 4.575 | 4.379 | 338 | 918 |
| 14 | **SOLE** | 4.578 | 4.370 | 310 | 783 |
| 15 | **TAEL** | 4.552 | 4.446 | 331 | 921 |

\* model estimate of total guesses; real averages are in the benchmark below.

## Best everyday-word openers

| # | word | info (bits) | avg answers left |
|---|---|---|---|
| 1 | **SALE** | 4.567 | 264 |
| 2 | **TALE** | 4.498 | 323 |
| 3 | **SATE** | 4.473 | 285 |
| 4 | **SEAL** | 4.471 | 280 |
| 5 | **SEAT** | 4.461 | 298 |
| 6 | **LATE** | 4.426 | 329 |
| 7 | **SANE** | 4.407 | 294 |
| 8 | **RATE** | 4.398 | 341 |
| 9 | **TEAL** | 4.391 | 343 |
| 10 | **REAL** | 4.379 | 338 |

## Best fixed two-word starts (play both, whatever the colours)

| first | second | combined info (bits) |
|---|---|---|
| SALE | TORN | 7.73 |
| SALE | PORT | 7.69 |
| SALE | DIRT | 7.68 |
| SALE | RIOT | 7.66 |
| SEAL | TORN | 7.65 |
| SATE | LORD | 7.64 |
| TALE | PROS | 7.61 |
| SEAL | PORT | 7.60 |
| SATE | ROIL | 7.60 |
| SEAL | DIRT | 7.59 |

## Letter probabilities

P(letter appears in the answer): **E** 39%, **A** 36%, **O** 27%, **S** 25%, **L** 24%, **R** 23%, **T** 22%, **I** 22%, **N** 18%, **D** 16%, **U** 14%, **P** 13%

Most likely letter in each position:

| position | top letters |
|---|---|
| 1 | S 10%, B 7%, P 7%, C 7%, T 6% |
| 2 | A 20%, O 19%, E 14%, I 13%, U 9% |
| 3 | A 10%, R 10%, L 10%, E 9%, N 8% |
| 4 | E 17%, T 11%, S 11%, D 7%, L 7% |

- P(answer has a repeated letter): **19%**
- Number of vowels (A E I O U): 1: 54%, 2: 45%, 3: 1%
- Common endings: -EAR 0.7%, -ILL 0.7%, -AIL 0.6%, -ATE 0.6%, -ENT 0.6%, -ARE 0.6%, -INE 0.6%, -ALL 0.6%
- Common beginnings: CO- 2.1%, BA- 1.8%, CA- 1.7%, BO- 1.7%, LO- 1.7%, MA- 1.6%, PA- 1.6%, WA- 1.6%

## What your first feedback means (after SALE)

| greens | yellows | how often | avg answers still possible |
|---|---|---|---|
| 0 | 0 | 17.5% | 689 |
| 0 | 1 | 23.7% | 303 |
| 0 | 2 | 11.5% | 109 |
| 0 | 3 | 1.8% | 20 |
| 1 | 0 | 22.6% | 228 |
| 1 | 1 | 11.5% | 82 |
| 1 | 2 | 1.2% | 8 |
| 2 | 0 | 7.8% | 55 |
| 2 | 1 | 1.1% | 5 |
| 3 | 0 | 1.0% | 9 |

## Trap families (62% of everyday words sit in a family of 4+)

Words that differ in only one letter. If you land in one, don't guess them one by one - play a word that tests several of the differing letters at once.

- `_INE` (11): DINE, FINE, KINE, LINE, MINE, NINE, PINE, SINE, TINE, VINE, WINE
- `_EAR` (11): BEAR, DEAR, FEAR, GEAR, HEAR, NEAR, PEAR, REAR, TEAR, WEAR, YEAR
- `_ARE` (10): BARE, CARE, DARE, FARE, HARE, MARE, PARE, RARE, TARE, WARE
- `_ILL` (10): BILL, FILL, GILL, HILL, KILL, MILL, PILL, SILL, TILL, WILL
- `_ENT` (10): BENT, CENT, DENT, KENT, LENT, PENT, RENT, SENT, TENT, VENT
- `_ALE` (10): BALE, DALE, GALE, HALE, KALE, MALE, PALE, SALE, TALE, WALE
- `_ATE` (10): BATE, DATE, FATE, GATE, HATE, LATE, MATE, PATE, RATE, SATE
- `_AIL` (10): BAIL, FAIL, HAIL, JAIL, MAIL, NAIL, RAIL, SAIL, TAIL, WAIL
- `_AKE` (9): BAKE, CAKE, HAKE, LAKE, MAKE, RAKE, SAKE, TAKE, WAKE
- `_ORE` (9): BORE, CORE, FORE, GORE, LORE, MORE, PORE, SORE, WORE
- `_ASH` (9): CASH, DASH, GASH, HASH, LASH, MASH, RASH, SASH, WASH
- `_OLD` (9): BOLD, COLD, FOLD, GOLD, HOLD, MOLD, SOLD, TOLD, WOLD

## Solver benchmark (held-out real answers, 6 tries)

| mode | games | avg guesses | win rate | distribution |
|---|---|---|---|---|
| normal | 652 | 4.245 | 98.6% | 2: 7 · 3: 144 · 4: 275 · 5: 147 · 6: 70 · 7: 5 · 8: 4 |
| hard | 652 | 4.597 | 89.4% | 2: 25 · 3: 132 · 4: 215 · 5: 132 · 6: 79 · 7: 34 · 8: 15 · 9: 9 · 10: 6 · 11: 3 · 12: 1 · 13: 1 |

Missed (normal mode): BADE, POLO, BABA, JEEP, BUNK, DUFF, PAIL, DILL, MIME

Opening book: 52 first-feedback patterns precomputed (99.5% of games). Average live step: 3 ms.
