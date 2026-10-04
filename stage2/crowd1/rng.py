"""Reproducible, stream-separated PRNG for the CROWD-1 Stage 1 engine.

Specification v0.6 CLOCKS: "Clocks, recipient draws and acceptance coins are
mutually independent."  We therefore carry three *independent* generator states
inside the engine, one per role, each seeded from the run's master seed by a
distinct stream id.  Two further streams are used in Python (not in the kernel)
for the cohort draw and the initial-law draw, so that changing the replicate
count of one role never shifts another role's numbers.

Generator: xoshiro256++ (Blackman & Vigna), seeded by splitmix64.  Both are
implemented here rather than taken from numpy so that the *same* bit stream is
reproducible from inside an njit kernel and from plain Python.

Stream ids (fixed for all time; never reassign):
    0 = clocks            (broadcast / reset / reconsideration waiting times)
    1 = recipient draws   (uniform choice of the receiving agent)
    2 = acceptance coins  (the accept/reject coin of the message transition)
    3 = cohort draw       (u_i ~ Bernoulli(f)), used in Python
    4 = initial law       (I1 / I2 / I3 draws), used in Python
    5 = prescribed exogenous message process (T3), used in Python
"""

import numpy as np
from numba import njit

STREAM_CLOCKS = 0
STREAM_RECIPIENT = 1
STREAM_COIN = 2
STREAM_COHORT = 3
STREAM_INITIAL = 4
STREAM_EXOGENOUS = 5

STREAM_NAMES = {
    0: "clocks",
    1: "recipient",
    2: "coin",
    3: "cohort",
    4: "initial_law",
    5: "exogenous",
}

_M64 = np.uint64(0xFFFFFFFFFFFFFFFF)


@njit(cache=True, inline="always")
def _splitmix64(state):
    """One splitmix64 step.  Returns (new_state, output)."""
    state = np.uint64(state + np.uint64(0x9E3779B97F4A7C15))
    z = state
    z = np.uint64(z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    z = np.uint64(z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    z = np.uint64(z ^ (z >> np.uint64(31)))
    return state, z


@njit(cache=True)
def seed_streams(master_seed, n_streams):
    """Build an (n_streams, 4) uint64 xoshiro256++ state table.

    Stream k is seeded from splitmix64 applied to (master_seed XOR golden*k),
    so distinct stream ids give provably distinct, well-separated states.
    """
    out = np.empty((n_streams, 4), dtype=np.uint64)
    for k in range(n_streams):
        st = np.uint64(np.uint64(master_seed) ^ (np.uint64(0x9E3779B97F4A7C15) * np.uint64(k + 1)))
        for j in range(4):
            st, z = _splitmix64(st)
            # xoshiro must not be seeded all-zero
            if z == np.uint64(0):
                z = np.uint64(0x853C49E6748FEA9B)
            out[k, j] = z
    return out


@njit(cache=True, inline="always")
def _rotl(x, k):
    return np.uint64((x << np.uint64(k)) | (x >> np.uint64(64 - k)))


@njit(cache=True, inline="always")
def next_u64(s, k):
    """xoshiro256++ next() for stream row k of state table s (modified in place)."""
    s0 = s[k, 0]
    s1 = s[k, 1]
    s2 = s[k, 2]
    s3 = s[k, 3]
    result = np.uint64(_rotl(np.uint64(s0 + s3), 23) + s0)
    t = np.uint64(s1 << np.uint64(17))
    s2 = np.uint64(s2 ^ s0)
    s3 = np.uint64(s3 ^ s1)
    s1 = np.uint64(s1 ^ s2)
    s0 = np.uint64(s0 ^ s3)
    s2 = np.uint64(s2 ^ t)
    s3 = _rotl(s3, 45)
    s[k, 0] = s0
    s[k, 1] = s1
    s[k, 2] = s2
    s[k, 3] = s3
    return result


@njit(cache=True, inline="always")
def next_double(s, k):
    """Uniform in [0, 1) with 53-bit resolution."""
    return np.float64(next_u64(s, k) >> np.uint64(11)) * (1.0 / 9007199254740992.0)


@njit(cache=True, inline="always")
def next_exp(s, k, rate):
    """Exponential(rate).  Uses 1 - U so the argument of log is in (0, 1]."""
    u = next_double(s, k)
    return -np.log(1.0 - u) / rate


@njit(cache=True, inline="always")
def next_below(s, k, n):
    """Uniform integer in [0, n) by Lemire-style rejection (unbiased)."""
    n64 = np.uint64(n)
    # threshold = 2**64 mod n
    thresh = np.uint64(np.uint64(0) - n64) % n64
    while True:
        r = next_u64(s, k)
        if r >= thresh:
            return np.int64(r % n64)


_MASK = (1 << 64) - 1
_GOLDEN = 0x9E3779B97F4A7C15


def _splitmix64_py(state):
    """Pure-Python splitmix64 (explicit 64-bit masking; no numpy overflow warnings)."""
    state = (state + _GOLDEN) & _MASK
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    z = z ^ (z >> 31)
    return state, z


def python_generator(master_seed, stream_id):
    """numpy Generator for the Python-side streams (cohort, initial law, exogenous).

    Seeded from the same splitmix64 derivation as the kernel streams, so the
    master seed alone reproduces every number in a run.
    """
    st = (int(master_seed) ^ ((_GOLDEN * (int(stream_id) + 1)) & _MASK)) & _MASK
    words = []
    for _ in range(4):
        st, z = _splitmix64_py(st)
        words.append(int(z))
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(words)))


def derive_run_seed(master_seed, *labels):
    """Deterministic per-run seed from a master seed and integer labels."""
    st = int(master_seed) & _MASK
    for lab in labels:
        st = (st ^ ((_GOLDEN * (int(lab) + 1)) & _MASK)) & _MASK
        st, z = _splitmix64_py(st)
        st = z
    return int(st)
