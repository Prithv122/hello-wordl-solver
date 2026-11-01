"""Why not just "the most frequent letters"? Compare three ways of choosing
the first word.  python scripts/compare_openers.py 5
"""
import os
import sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wordl.solver import Solver
from wordl import patterns as P
L=int(sys.argv[1])
s=Solver(L,use_book=False)
p=s.w/s.w.sum(); C=P.letter_counts(s.A)
pres=p@(C>0)                                  # P(letter in answer)
pos=np.zeros((L,26))
for j in range(L): np.add.at(pos[j], s.A[:,j], p)
pool=np.nonzero(s.is_guess & s.is_common)[0]
G=s.A[pool]; Gc=C[pool]
distinct=(Gc.max(1)==1)
f_score=np.where(distinct,(Gc>0)@pres,-1)                         # "most common letters"
pos_score=np.where(distinct,sum(pos[j,G[:,j]] for j in range(L)),-1) # "most common letters in their usual spots"
picks={'most frequent letters':pool[np.argmax(f_score)],
       'frequent letters in usual positions':pool[np.argmax(pos_score)]}
best=s.rank(1,pool=pool,exact=True)[0]
picks['information (solver)']=s.index[best['word']]
res=s.score_pool(np.array(list(picks.values())), p)
print(f"--- {L} letters: {len(s.words)} words")
for k,(name,i) in enumerate(picks.items()):
    print(f"{name:38s} {s.words[i].upper():12s} info {res['H'][k]:.2f} bits | avg answers left {res['avg_left'][k]:7.1f} | worst case {res['worst'][k]:5d} | {res['groups'][k]} patterns")
print("top letters by P(in answer):", " ".join(f"{c.upper()}{v*100:.0f}" for c,v in sorted(zip('abcdefghijklmnopqrstuvwxyz',pres), key=lambda x:-x[1])[:10]))
