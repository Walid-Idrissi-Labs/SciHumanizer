#!/usr/bin/env python3
"""Lexical statistics with known mathematical properties (standard library only).

Why these estimators: the raw type-token ratio falls as a text gets longer (Heaps' law), so
texts of different lengths cannot be compared with it. Every measure here is defined at a
*fixed sample size* and is therefore comparable across lengths.

  rarefied_types(freqs, n)   E[number of distinct words in a random n-token subsample]   (exact)
  rarefied_hapax(freqs, n)   E[number of words occurring once in that subsample]         (exact)
  mattr(tokens, w)           mean type-token ratio over every contiguous window of w tokens
  mtld_wrap(tokens)          mean run length that keeps TTR above 0.72, from every start, wrapping
  dispersion(tokens, w)      mattr / (rarefied_types/w): local vs chance-level repetition
  yule_k(freqs)              10^4 * (sum f^2 - N) / N^2: repeat rate, length-independent

Rarefaction is the hypergeometric expectation used in ecology and behind HD-D (McCarthy &
Jarvis 2007): for a word with frequency f in a text of N tokens, the probability that a random
subsample of n tokens (without replacement) misses it is C(N-f, n) / C(N, n). Therefore

    E[V_n]  = sum_i [ 1 - C(N - f_i, n) / C(N, n) ]
    E[V1_n] = sum_i   f_i * C(N - f_i, n - 1) / C(N, n)

Both are order-independent and exact (no simulation, no window artifacts). MATTR (Covington &
McFall 2010) and MTLD (McCarthy & Jarvis 2010; wrap-around variant after Vidal & Jarvis 2020)
are order-dependent: they also see *where* repetitions fall. The dispersion index compares the
two: below 1, repeated words cluster (a writer staying with a term); above 1, repeats are spread
out more evenly than chance (a writer avoiding a word just used).

Run `python3 lexstats.py` to self-test the formulas against Monte Carlo simulation.
"""
import collections
import math
import random


def _log_choose(a, b):
    if b < 0 or b > a:
        return float("-inf")
    return math.lgamma(a + 1) - math.lgamma(b + 1) - math.lgamma(a - b + 1)


def spectrum(tokens):
    """Frequency spectrum: {frequency: number of types with that frequency}."""
    return collections.Counter(collections.Counter(tokens).values())


def rarefied_types(spec, n_total, n):
    """Expected number of distinct types in a random subsample of n tokens. None if n > N."""
    if n > n_total or n <= 0:
        return None
    denom = _log_choose(n_total, n)
    out = 0.0
    for f, v in spec.items():
        miss = _log_choose(n_total - f, n) - denom        # log P(type absent from subsample)
        out += v * (1.0 - (math.exp(miss) if miss > float("-inf") else 0.0))
    return out


def rarefied_hapax(spec, n_total, n):
    """Expected number of types occurring exactly once in a random subsample of n tokens."""
    if n > n_total or n <= 0:
        return None
    denom = _log_choose(n_total, n)
    out = 0.0
    for f, v in spec.items():
        lp = math.log(f) + _log_choose(n_total - f, n - 1) - denom   # log P(exactly one of the f drawn)
        if lp > float("-inf"):
            out += v * math.exp(lp)
    return out


def mattr(tokens, w=50):
    """Moving-average type-token ratio. None when the text is shorter than the window."""
    n = len(tokens)
    if n < w or w <= 0:
        return None
    window = collections.Counter(tokens[:w])
    total = len(window)
    for i in range(w, n):
        o = tokens[i - w]
        window[o] -= 1
        if not window[o]:
            del window[o]
        window[tokens[i]] += 1
        total += len(window)
    return total / ((n - w + 1) * w)


def mtld_wrap(tokens, threshold=0.72, min_tokens=50):
    """MTLD, moving-average wrap-around: from every start position, the number of tokens read
    (wrapping to the beginning) until the running TTR first falls to the threshold or below; the
    mean of those run lengths. No partial factors, every token starts one run. Runs that never
    reach the threshold are censored at N. None for texts under min_tokens."""
    n = len(tokens)
    if n < min_tokens:
        return None
    total = 0
    for start in range(n):
        seen = set()
        length = n
        for k in range(1, n + 1):
            seen.add(tokens[(start + k - 1) % n])
            if len(seen) / k <= threshold:
                length = k
                break
        total += length
    return total / n


def yule_k(spec, n_total):
    if n_total < 2:
        return None
    m2 = sum(f * f * v for f, v in spec.items())
    return 1e4 * (m2 - n_total) / (n_total * n_total)


def dispersion(tokens, w=50):
    """Observed local diversity (MATTR) over the diversity expected if the same words were
    shuffled (rarefied types at the window size). < 1: repeats cluster; > 1: repeats avoid each other."""
    m = mattr(tokens, w)
    if m is None:
        return None
    exp = rarefied_types(spectrum(tokens), len(tokens), w)
    return m / (exp / w) if exp else None


def profile(tokens, n=100, w=50):
    """All measures for one token sequence (use lemmas for a vocabulary measure)."""
    spec = spectrum(tokens)
    n_total = len(tokens)
    rt = rarefied_types(spec, n_total, n)
    rh = rarefied_hapax(spec, n_total, n)
    return {
        "tokens": n_total, "types": sum(spec.values()),
        "types_at_%d" % n: round(rt / n, 4) if rt is not None else None,
        "hapax_at_%d" % n: round(rh / n, 4) if rh is not None else None,
        "mattr%d" % w: round(mattr(tokens, w), 4) if n_total >= w else None,
        "mtld_wrap": round(mtld_wrap(tokens), 1) if n_total >= 50 else None,
        "dispersion%d" % w: round(dispersion(tokens, w), 4) if n_total >= w else None,
        "yule_k": round(yule_k(spec, n_total), 1) if n_total > 1 else None,
    }


# ------------------------------------------------------------------------------- self-test
def _zipf_text(n_tokens, vocab=3000, s=1.05, seed=0):
    rng = random.Random(seed)
    weights = [1.0 / (r ** s) for r in range(1, vocab + 1)]
    return rng.choices(range(vocab), weights=weights, k=n_tokens)


def selftest(verbose=True):
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and cond
        if verbose:
            print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))

    rng = random.Random(1)
    text = _zipf_text(1200, seed=3)
    spec, n_total = spectrum(text), len(text)

    # 1. rarefaction equals Monte Carlo subsampling (types and hapax)
    for n in (42, 100, 300):
        sims_v, sims_h = [], []
        for _ in range(3000):
            sub = collections.Counter(rng.sample(text, n))
            sims_v.append(len(sub))
            sims_h.append(sum(1 for c in sub.values() if c == 1))
        ev, eh = rarefied_types(spec, n_total, n), rarefied_hapax(spec, n_total, n)
        mv, mh = sum(sims_v) / len(sims_v), sum(sims_h) / len(sims_h)
        check("rarefied types  n=%d matches simulation" % n, abs(ev - mv) < 0.25, "(exact %.3f, simulated %.3f)" % (ev, mv))
        check("rarefied hapax  n=%d matches simulation" % n, abs(eh - mh) < 0.25, "(exact %.3f, simulated %.3f)" % (eh, mh))

    # 2. boundary identities
    check("rarefied types at n=N equals V", abs(rarefied_types(spec, n_total, n_total) - sum(spec.values())) < 1e-6)
    check("rarefied hapax at n=N equals V1", abs(rarefied_hapax(spec, n_total, n_total) - spec[1]) < 1e-6)
    check("rarefied types at n=1 equals 1", abs(rarefied_types(spec, n_total, 1) - 1.0) < 1e-9)
    check("no repetition -> every measure maximal", abs(mattr(list(range(200)), 50) - 1.0) < 1e-12 and
          abs(rarefied_types(spectrum(range(200)), 200, 100) - 100) < 1e-9)
    check("one repeated word -> minimal", abs(mattr([7] * 200, 50) - 1 / 50) < 1e-12 and mtld_wrap([7] * 200) == 2.0)

    # 3. length invariance on text from one source: 300 vs 2400 tokens of the same Zipf process
    short = [profile(_zipf_text(300, seed=s)) for s in range(40)]
    long_ = [profile(_zipf_text(2400, seed=s + 100)) for s in range(40)]
    for key, tol in (("types_at_100", 0.02), ("hapax_at_100", 0.03), ("mattr50", 0.02)):
        a = sum(p[key] for p in short) / len(short)
        b = sum(p[key] for p in long_) / len(long_)
        check("%s is length-invariant (300 vs 2400 tokens)" % key, abs(a - b) < tol, "(%.4f vs %.4f)" % (a, b))
    ttr_s = sum(p["types"] / p["tokens"] for p in short) / len(short)
    ttr_l = sum(p["types"] / p["tokens"] for p in long_) / len(long_)
    check("raw TTR is NOT length-invariant (the reason it is not used)", ttr_s - ttr_l > 0.1, "(%.3f vs %.3f)" % (ttr_s, ttr_l))

    # 4. dispersion: shuffled text ~ 1, clustered text < 1, round-robin text > 1
    shuffled = text[:]
    rng.shuffle(shuffled)
    clustered = sorted(text)                         # every repeat adjacent
    cyc = [i % 60 for i in range(1200)]              # a word never returns before 59 others
    check("dispersion of shuffled text is about 1", abs(dispersion(shuffled) - 1.0) < 0.02, "(%.3f)" % dispersion(shuffled))
    check("dispersion of clustered text is below 1", dispersion(clustered) < 0.8, "(%.3f)" % dispersion(clustered))
    check("dispersion of evenly spread repeats is above 1", dispersion(cyc) > 1.05, "(%.3f)" % dispersion(cyc))

    # 5. order (in)dependence
    check("rarefaction ignores word order",
          abs(rarefied_types(spectrum(shuffled), n_total, 100) - rarefied_types(spec, n_total, 100)) < 1e-9)
    check("MATTR sees word order", abs(mattr(clustered, 50) - mattr(shuffled, 50)) > 0.1)
    if verbose:
        print("\nlexstats self-test: %s" % ("all checks passed" if ok else "FAILURES"))
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
