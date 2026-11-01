"""Feedback (colour pattern) computation - scalar and vectorised.

A pattern is encoded as an integer in base 3, position i contributing
digit * 3**i with digit 0 = grey/absent, 1 = yellow/misplaced, 2 = green.

Duplicate-letter rule (same as Wordle / Hello Wordl): greens are assigned
first; then, left to right, a non-green letter is yellow only while the
answer still has unused copies of that letter; otherwise it is grey.
"""
from __future__ import annotations

import numpy as np

GREY, YELLOW, GREEN = 0, 1, 2
_SYMBOLS = {
    "b": 0, "x": 0, "-": 0, ".": 0, "0": 0, "g0": 0, "⬛": 0, "⬜": 0,
    "y": 1, "1": 1, "?": 1, "🟨": 1,
    "g": 2, "2": 2, "!": 2, "🟩": 2,
}


def score(guess: str, answer: str) -> int:
    """Scalar reference implementation."""
    L = len(guess)
    res = [0] * L
    left: dict[str, int] = {}
    for i in range(L):
        if guess[i] == answer[i]:
            res[i] = 2
        else:
            left[answer[i]] = left.get(answer[i], 0) + 1
    for i in range(L):
        if res[i] == 0 and left.get(guess[i], 0) > 0:
            res[i] = 1
            left[guess[i]] -= 1
    return encode(res)


def encode(digits) -> int:
    v = 0
    for i, d in enumerate(digits):
        v += d * 3 ** i
    return v


def decode(p: int, L: int) -> list[int]:
    out = []
    for _ in range(L):
        out.append(p % 3)
        p //= 3
    return out


def to_str(p: int, L: int, style: str = "letters") -> str:
    d = decode(p, L)
    if style == "emoji":
        return "".join("⬛🟨🟩"[x] for x in d)
    return "".join("byg"[x] for x in d)


def parse(s: str, L: int) -> int:
    """Parse 'bygbb', '01200', '⬛🟨🟩⬛⬛' etc. (b=grey, y=yellow, g=green)."""
    s = s.strip().lower()
    digits = []
    for ch in s:
        if ch in " ,️":
            continue
        if ch not in _SYMBOLS:
            raise ValueError(f"bad feedback symbol {ch!r}; use b/y/g (grey/yellow/green)")
        digits.append(_SYMBOLS[ch])
    if len(digits) != L:
        raise ValueError(f"feedback has {len(digits)} symbols, expected {L}")
    return encode(digits)


def all_green(L: int) -> int:
    return 3 ** L - 1


def dtype_for(L: int):
    return np.uint16 if 3 ** L <= 65535 else np.uint32


def to_array(words: list[str]) -> np.ndarray:
    """(N, L) uint8 array of letter codes 0..25."""
    if not words:
        return np.zeros((0, 0), dtype=np.uint8)
    b = np.frombuffer("".join(words).encode("ascii"), dtype=np.uint8)
    return (b.reshape(len(words), -1) - ord("a")).astype(np.uint8)


def letter_counts(A: np.ndarray) -> np.ndarray:
    """(N, 26) count of each letter in each word."""
    C = np.zeros((A.shape[0], 26), dtype=np.int8)
    for j in range(A.shape[1]):
        np.add.at(C, (np.arange(A.shape[0]), A[:, j]), 1)
    return C


_POW3 = None


def patterns_one(g: np.ndarray, A: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Patterns of ONE guess ``g`` (L,) against MANY answers ``A`` (M, L).

    ``C`` is letter_counts(A). Cost ~3L vector ops of size M - fast for big M.
    """
    M, L = A.shape
    green = A == g  # (M, L)
    out = np.zeros(M, dtype=np.int64)
    pw = 1
    pows = [3 ** i for i in range(L)]
    for i in range(L):
        out += green[:, i] * (2 * pows[i])
    for c in np.unique(g):
        pos = np.nonzero(g == c)[0]
        avail = C[:, c].astype(np.int16) - green[:, pos].sum(axis=1)
        for i in pos:
            y = (~green[:, i]) & (avail > 0)
            out += y * pows[i]
            avail -= y
    return out.astype(dtype_for(L))


def patterns_block(G: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Patterns of MANY guesses ``G`` (B, L) vs MANY answers ``A`` (M, L).

    Fully vectorised via a (B, M, L, L) equality tensor - use when B*M*L*L is
    moderate (the solver chunks automatically).
    """
    B, L = G.shape
    M = A.shape[0]
    pows = (3 ** np.arange(L)).astype(np.int64)
    green = G[:, None, :] == A[None, :, :]  # (B, M, L)
    # E[b,m,i,j] : guess letter i equals answer letter j
    E = G[:, None, :, None] == A[None, :, None, :]
    # copies of guess-letter i in the answer at NON-green answer positions
    avail = (E & ~green[:, :, None, :]).sum(-1)  # (B, M, L)
    # earlier non-green copies of the same letter in the guess (they take
    # yellows first)
    same = (G[:, :, None] == G[:, None, :]) & np.tri(L, k=-1, dtype=bool)[None]  # (B, i, k) k<i
    rank = np.einsum("bik,bmk->bmi", same.astype(np.int16), (~green).astype(np.int16))
    yellow = ~green & (avail > rank)
    pat = (green * 2 + yellow) @ pows
    return pat.astype(dtype_for(L))


def pattern_matrix(G: np.ndarray, A: np.ndarray, budget: int = 40_000_000) -> np.ndarray:
    """(len(G), len(A)) pattern matrix, automatically chunked."""
    B, L = G.shape
    M = A.shape[0]
    out = np.empty((B, M), dtype=dtype_for(L))
    if B == 0 or M == 0:
        return out
    per_row = M * L * L
    if per_row > budget:  # huge answer set - go guess by guess
        C = letter_counts(A)
        for b in range(B):
            out[b] = patterns_one(G[b], A, C)
        return out
    step = max(1, budget // per_row)
    for s in range(0, B, step):
        out[s:s + step] = patterns_block(G[s:s + step], A)
    return out


def patterns_vs_answer(G: np.ndarray, a: np.ndarray, ca: np.ndarray) -> np.ndarray:
    """Patterns of MANY guesses ``G`` (B, L) against ONE answer ``a`` (L,).

    ``ca`` = letter counts of ``a`` (26,). Cost ~L^2 vector ops of size B.
    """
    B, L = G.shape
    green = G == a  # (B, L)
    out = (green * 2) @ (3 ** np.arange(L)).astype(np.int64)
    used = [None] * L
    for i in range(L):
        c = G[:, i]
        avail = ca[c].astype(np.int16)
        for j in range(L):
            avail = avail - (green[:, j] & (G[:, j] == c))
        for k in range(i):
            avail = avail - (used[k] & (G[:, k] == c))
        y = ~green[:, i] & (avail > 0)
        used[i] = y
        out += y * 3 ** i
    return out


def fast_matrix(G: np.ndarray, A: np.ndarray) -> np.ndarray:
    """(len(G), len(A)) pattern matrix, looping over the smaller side."""
    B, L = G.shape
    M = A.shape[0]
    out = np.empty((B, M), dtype=dtype_for(L))
    if B == 0 or M == 0:
        return out
    if M <= B:
        CA = letter_counts(A)
        for m in range(M):
            out[:, m] = patterns_vs_answer(G, A[m], CA[m])
    else:
        CA = letter_counts(A)
        for b in range(B):
            out[b] = patterns_one(G[b], A, CA)
    return out
