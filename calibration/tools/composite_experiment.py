#!/usr/bin/env python3
"""Which way of combining dimension scores separates best at a fixed human pass rate?
Out of fold (5 folds by document): metrics, bands and weights come from the training folds only.
  a  unweighted root-mean-square of the dimension scores (first version of the gate)
  b  weighted RMS, weight = how far AI texts sit above human texts on that dimension (mean over tiers)
  c  weighted mean (linear), same weights
  d  the larger of the per-tier weighted means (each tier has its own weights)
  e  the larger of the per-tier weighted RMS
  f  as d, with weights divided by the variance of the dimension score (diagonal discriminant): adopted
"""
import collections, json, math, os, random, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrate as CAL
S = CAL.S

def dims(row, reg, L):
    e = S.evaluate(row, {"registers": {"x.calib": reg}}, "calib", n_words=L, lang="x")
    return {d["dimension"]: d["z"] for d in e["dimensions"]}, len(e["classic_violations"])

def run(name, cfg, data, K=5, seed=3):
    rng = random.Random(seed)
    lang = name.split(".")[0]
    all_ai = [s for t in cfg["ai"].values() for s in t]
    lengths = [L for L in sorted({L for (s, L) in data.by if L > 0})
               if data.n_docs(cfg["human"], L) >= CAL.MIN_H and data.n_docs(all_ai, L) >= CAL.MIN_A]
    tiers = list(cfg["ai"])
    hdocs = data.files(cfg["human"], lengths[0]); rng.shuffle(hdocs)
    hfold = {f: i % K for i, f in enumerate(hdocs)}
    afold = {}
    for t in tiers:
        d = data.files(cfg["ai"][t], lengths[0]); rng.shuffle(d)
        afold.update({f: i % K for i, f in enumerate(d)})
    variants = "adf"
    H = {v: {L: [] for L in lengths} for v in variants}
    A = {v: {t: {L: [] for L in lengths} for t in tiers} for v in variants}
    for k in range(K):
        htr = {f for f in hdocs if hfold[f] != k}; atr = {f for f, i in afold.items() if i != k}
        reg = {"lang": lang, "metrics": CAL.build(data, cfg, lang, lengths, htr, atr), "max_classic_violations": 1,
               "composite": {"threshold": {str(L): 99.0 for L in lengths}}}
        # weights from the training documents
        zh, za = collections.defaultdict(list), {t: collections.defaultdict(list) for t in tiers}
        for L in lengths:
            for r in data.rows(cfg["human"], L, htr):
                for g, z in dims(r, reg, L)[0].items(): zh[g].append(z)
            for t in tiers:
                for r in data.rows(cfg["ai"][t], L, atr):
                    for g, z in dims(r, reg, L)[0].items(): za[t][g].append(z)
        wt = {t: {g: max(0.0, statistics.mean(za[t][g]) - statistics.mean(zh[g])) for g in zh if za[t][g]} for t in tiers}
        # diagonal discriminant weights: mean shift / pooled within-class variance of the dimension score
        wl = {t: {g: max(0.0, statistics.mean(za[t][g]) - statistics.mean(zh[g])) /
                     max(0.05, (statistics.pvariance(zh[g]) + statistics.pvariance(za[t][g])) / 2.0)
                  for g in zh if len(za[t][g]) > 1} for t in tiers}
        w = {g: statistics.mean(wt[t].get(g, 0.0) for t in tiers) for g in zh}
        def comps(dz):
            gs = list(dz)
            out = {"a": math.sqrt(sum(dz[g] ** 2 for g in gs) / len(gs)) if gs else 0.0}
            sw = sum(w.get(g, 0) for g in gs) or 1e-9
            out["b"] = math.sqrt(sum(w.get(g, 0) * dz[g] ** 2 for g in gs) / sw)
            out["c"] = sum(w.get(g, 0) * dz[g] for g in gs) / sw
            lin, rms = [], []
            for t in tiers:
                st = sum(wt[t].get(g, 0) for g in gs) or 1e-9
                lin.append(sum(wt[t].get(g, 0) * dz[g] for g in gs) / st)
                rms.append(math.sqrt(sum(wt[t].get(g, 0) * dz[g] ** 2 for g in gs) / st))
            out["d"], out["e"] = max(lin), max(rms)
            lda = []
            for t in tiers:
                st = sum(wl[t].get(g, 0) for g in gs) or 1e-9
                lda.append(sum(wl[t].get(g, 0) * dz[g] for g in gs) / st)
            out["f"] = max(lda)
            return out
        for L in lengths:
            for r in data.rows(cfg["human"], L):
                if hfold.get(r["_file"]) == k:
                    dz, viol = dims(r, reg, L); c = comps(dz)
                    for v in variants: H[v][L].append((r["_file"], c[v], viol, {}, 0.0))
            for t in tiers:
                for r in data.rows(cfg["ai"][t], L):
                    if afold.get(r["_file"]) == k:
                        dz, viol = dims(r, reg, L); c = comps(dz)
                        for v in variants: A[v][t][L].append((r["_file"], c[v], viol, {}, 0.0))
    print("\n== %s  (AI pass rate at the threshold that passes 90%% of out-of-fold human composites; per tier)" % name)
    print("words   " + "   ".join("%-22s" % ("%s: %s" % (v, " / ".join(t.split()[0] for t in tiers))) for v in variants))
    for L in lengths:
        cells = []
        for v in variants:
            thr = S.pct([sc[1] for sc in H[v][L]], 0.90)
            cells.append("%-22s" % " / ".join("%3.0f%%" % (100 * CAL.doc_pass(A[v][t][L], thr)) if A[v][t][L] else "  - " for t in tiers))
        print("%5d   %s" % (L, "   ".join(cells)))
    last = sorted(w.items(), key=lambda kv: -kv[1])
    print("weights (last fold): " + ", ".join("%s %.2f" % (g, x) for g, x in last if x > 0.05))

cfg = json.load(open(sys.argv[1]))
rows = [json.loads(l) for l in open(os.path.join(CAL.WS, cfg["run"]), encoding="utf-8")]
data = CAL.Data(rows)
for name, rc in cfg["registers"].items():
    run(name, rc, data)
