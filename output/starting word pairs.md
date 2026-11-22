# Wordle starting word pairs

**Best pair of everyday words: SLATE then MINOR.** After both, about 16 possible answers are left on average.

From the solver's analysis of 5-letter words:

| First | Second | Avg answers left after both |
|---|---|---|
| LARES | TONIC | **14.4** (best overall, but LARES is an obscure word) |
| LARES | POINT | 15.0 |
| **SLATE** | **MINOR** | **16.4** (best with everyday words) |
| SLATE | DORIC | 16.6 |
| SLATE | ROUND | 17.8 |
| TEARS | COULD | 18.2 |
| RAISE | COUNT | 21.6 (popular, but noticeably weaker) |

The pair works because the second word covers five completely new common letters, so between them you test S L A T E M I N O R.

## Best third word after SLATE + MINOR

**Play PUDGY** (or DUCHY). It tests five more brand-new letters (P U D G Y), so after three words you've covered 15 letters.

After SLATE + MINOR, about **16.4** answers are left on average and only 10% of answers are pinned down exactly. A fixed third word cuts that a lot:

| Third word | Avg answers left after all three | Answers pinned down exactly |
|---|---|---|
| **DUCHY** | **3.75** | 38% |
| **PUDGY** | **3.76** | 38% |
| DUCKY | 3.85 | 36% |
| CUBED | 3.95 | 37% |
| CUPID | 4.05 | 36% |
| HYPED | 4.18 | 35% |
| DUCKS | 4.29 | 34% (best of the most common words) |
| DUTCH | 4.39 | 36% |
| DOUGH | 4.62 | 34% |
| POUCH | 4.71 | 37% |

The best third words share the same idea: D, U, C/P, H/G and Y are the most useful letters still untested after SLATE + MINOR.

**Only use a fixed third word if the first two gave you little.** If SLATE + MINOR already lit up 4 or more letters, you usually know enough to start guessing real answers. Spending turn 3 on PUDGY then costs you a guess you didn't need.

## When to skip the second word

If SLATE already shows 3 or more coloured letters, start guessing real answers instead.

In the tests on real answers:

- Always playing both words won 99.0% of games but took 3.85 guesses on average.
- Skipping the second word after a strong first result was slightly faster but won a bit less often.
- The full solver averaged 3.56 guesses and won 100%.

So a fixed pair is a good, safe habit, but not the fastest route.

## Caveat

These numbers are for Hello Wordl's 5-letter answers. The New York Times Wordle uses its own hand-picked answer list. The rankings should be very similar, since both favour common words, but they haven't been tested against the NYT list specifically.
