#!/usr/bin/env python3
"""Which vocabulary estimators deserve a place in the gate?
For each candidate: separation (AUC human vs AI at matched length), reliability (correlation between the
odd-sentence half and the even-sentence half of the same human text), and length drift (150 vs 600 words of
the same human text, in units of the between-text SD). Also: what drives the AI-human gap in all-word variety."""
import bisect, collections, glob, math, os, statistics, sys
from paths import WS
import lexstats as X, textcore as T, sci_metrics as S

def auc(h, a):
    hs = sorted(h); tot = 0.0
    for x in a:
        lo, hi = bisect.bisect_left(hs, x), bisect.bisect_right(hs, x); tot += lo + 0.5 * (hi - lo)
    return tot / (len(a) * len(h))

def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")

def mtld_v1(tokens, thr=0.72):
    def one(tk):
        factors, types, count = 0.0, set(), 0
        for t in tk:
            count += 1; types.add(t)
            if len(types) / count <= thr:
                factors += 1; types, count = set(), 0
        if count:
            factors += (1 - len(types) / count) / (1 - thr)
        return len(tk) / factors if factors else float(len(tk))
    return (one(tokens) + one(tokens[::-1])) / 2

def hapax_window(tokens, w=100):
    hw = []
    for i in range(0, len(tokens) - w + 1, w):
        c = collections.Counter(tokens[i:i + w]); hw.append(sum(1 for v in c.values() if v == 1) / w)
    return statistics.mean(hw) if hw else None

def seqs(doc):
    """(word forms, lemmas, content lemmas, function lemmas)"""
    forms, lem, cont, fw = [], [], [], []
    for s in doc.all_sentences:
        for t, l, g in zip(s["toks"], s["lemmas"], s["tags"]):
            if g == "NUM" or not l or not l[0].isalpha():
                continue
            forms.append(t); lem.append(l.lower())
            if g in S.CONTENT_TAGS: cont.append(l.lower())
            elif g in S.FUNCTION_TAGS: fw.append(l.lower())
    return forms, lem, cont, fw

def rt(seq, n):
    return X.rarefied_types(X.spectrum(seq), len(seq), n) / n if len(seq) >= n else None

def rh(seq, n):
    return X.rarefied_hapax(X.spectrum(seq), len(seq), n) / n if len(seq) >= n else None

def estimators(doc):
    forms, lem, cont, fw = seqs(doc)
    n = len(lem)
    top = collections.Counter(fw).most_common(5)
    e = {
        "raw TTR (lemmas)": len(set(lem)) / n if n else None,
        "types@100 forms (rarefied)": rt(forms, 100), "types@100 lemmas (rarefied)": rt(lem, 100),
        "hapax@100 lemmas (rarefied)": rh(lem, 100), "hapax per 100-window forms (v1)": hapax_window(forms),
        "MATTR-50 forms (v1)": X.mattr(forms, 50), "MATTR-50 lemmas": X.mattr(lem, 50),
        "MATTR-100 lemmas": X.mattr(lem, 100),
        "MTLD two-pass forms (v1)": mtld_v1(forms) if n >= 50 else None, "MTLD wrap lemmas": X.mtld_wrap(lem) if n >= 50 else None,
        "Yule K lemmas (negated)": -X.yule_k(X.spectrum(lem), n) if n > 1 else None,
        "dispersion-50 lemmas": X.dispersion(lem, 50),
        "content types@50": rt(cont, 50), "content types@100": rt(cont, 100), "content MATTR-25": X.mattr(cont, 25),
        "function types@50": rt(fw, 50), "function types@100": rt(fw, 100),
        "lexical density": len(cont) / n if n else None,
        "top-5 function-word share of tokens": sum(v for _, v in top) / n if n else None,
    }
    return e

def load(folder, lang="en"):
    return [T.Doc(open(f, encoding="utf-8", errors="ignore").read(), lang)
            for d in folder.split(",") if d for f in sorted(glob.glob(d + "/*.txt"))]

def halves(doc):
    a = T.Doc("\n\n".join(s["text"] for s in doc.sentences[0::2]), doc.lang)
    b = T.Doc("\n\n".join(s["text"] for s in doc.sentences[1::2]), doc.lang)
    return a, b

def run(name, hdir, adirs, L, lang="en"):
    H = [d for d in load(hdir, lang) if d.n_words >= L]
    A = {k: [d for d in load(v, lang) if d.n_words >= L] for k, v in adirs.items()}
    eh = [estimators(d.truncated(L)) for d in H]
    ea = {k: [estimators(d.truncated(L)) for d in v] for k, v in A.items()}
    hh = [(estimators(a), estimators(b)) for a, b in (halves(d.truncated(L)) for d in H)]
    Hs = [d for d in H if d.n_words >= 600]
    short = [estimators(d.truncated(150)) for d in Hs]; long_ = [estimators(d.truncated(600)) for d in Hs]
    print("\n## %s at %d words: human n=%d, AI %s" % (name, L, len(H), ", ".join("%s n=%d" % (k, len(v)) for k, v in A.items())))
    print("%-36s %s  %8s %8s  %s" % ("estimator", " ".join("AUC %-7s" % k for k in A), "split-r", "drift", "human median -> AI medians"))
    for key in eh[0]:
        hv = [e[key] for e in eh if e[key] is not None]
        if len(hv) < 20:
            continue
        aucs, meds = [], []
        for k in A:
            av = [e[key] for e in ea[k] if e[key] is not None]
            aucs.append("%.2f       " % auc(hv, av) if len(av) >= 8 else "  -        ")
            meds.append("%.3g" % statistics.median(av) if av else "-")
        pairs = [(a[key], b[key]) for a, b in hh if a[key] is not None and b[key] is not None]
        r = pearson([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 20 else float("nan")
        dr = [(s[key], l[key]) for s, l in zip(short, long_) if s[key] is not None and l[key] is not None]
        drift = (statistics.mean(l for _, l in dr) - statistics.mean(s for s, _ in dr)) / (statistics.pstdev([l for _, l in dr]) or 1) if len(dr) >= 15 else float("nan")
        print("%-36s %s %8.2f %+8.2f  %.3g -> %s" % (key, " ".join(aucs), r, drift, statistics.median(hv), " / ".join(meds)))
    # what drives the gap in all-word variety? remove the part of MATTR predicted by density (fit on humans)
    for target in ("MATTR-50 lemmas", "types@100 lemmas (rarefied)"):
        for pred in ("lexical density", "top-5 function-word share of tokens", "content types@50"):
            xs = [e[pred] for e in eh if e[pred] is not None and e[target] is not None]
            ys = [e[target] for e in eh if e[pred] is not None and e[target] is not None]
            mx, my = statistics.mean(xs), statistics.mean(ys)
            b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
            res_h = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
            line = []
            for k in A:
                res_a = [e[target] - (my + b * (e[pred] - mx)) for e in ea[k] if e[pred] is not None and e[target] is not None]
                raw_a = [e[target] for e in ea[k] if e[target] is not None]
                line.append("%s %.2f -> %.2f" % (k, auc(ys, raw_a), auc(res_h, res_a)))
            print("  %s AUC before -> after removing what '%s' predicts (r=%.2f in humans): %s" % (target, pred, pearson(xs, ys), "; ".join(line)))

C = os.path.join(WS, "calib")
if len(sys.argv) > 1 and sys.argv[1] == "fr":
    run("fr.scientific", C + "/fr/human/scientific", {"sonnet": C + "/fr/ai_sonnet/scientific", "haiku": C + "/fr/ai_haiku/scientific"}, 450, "fr")
    run("fr.general", C + "/fr/human/general", {"sonnet": C + "/fr/ai_sonnet/general", "haiku": C + "/fr/ai_haiku/general"}, 450, "fr")
    run("fr.abstract", C + "/fr/human/abstract", {"sonnet": C + "/fr/ai_sonnet/abstract", "haiku": C + "/fr/ai_haiku/abstract"}, 200, "fr")
else:
    run("en.scientific", C + "/human/scientific", {"sonnet": C + "/ai/scientific", "haiku": C + "/ai_haiku/scientific"}, 450)
    run("en.general (modern human texts)", C + "/human/general_modern", {"sonnet": C + "/ai/general," + C + "/ai/general_modern", "haiku": C + "/ai_haiku/general," + C + "/ai_haiku/general_modern"}, 450)
    run("en.abstract", C + "/human/abstract", {"sonnet": C + "/ai/abstract", "haiku": C + "/ai_haiku/abstract"}, 200)
