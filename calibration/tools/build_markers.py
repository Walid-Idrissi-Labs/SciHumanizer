#!/usr/bin/env python3
"""Build the calibrated marker-word lists of a language (scripts/data/markers_<lang>.json).

  build_markers.py CONFIG.json [--write]
  CONFIG: {"lang": "en", "registers": {"scientific": {"human": ["calib/human/scientific"], "ai": ["calib/ai/scientific", ...]}, ...},
           "exclude": ["topic", "words"]}

Method
  1. Per register, the log-odds ratio of every lemma between AI and human texts, with an informative
     Dirichlet prior (Monroe, Colaresi & Quinn 2008): z > 0 = over-used by AI, z < 0 = under-used.
  2. A word enters a list only if it replicates: |z| >= Z_MIN in at least two registers with the same
     sign, no register pointing the other way (|z| >= 2), and it occurs in a minimum share of the texts
     of the side it marks. Registers differ in topic (medicine and social science, physics and computer
     science, news and essays), so replication removes topic words.
  3. Glue words: among the ten most frequent grammatical words of the human texts, those that AI text
     under-uses in at least two registers.
  4. Honest evaluation by cross-fitting: lists are built on one half of the documents and their rates
     are tested (AUC) on the other half, then the halves are swapped. The shipped lists use all documents.
"""
import bisect, collections, glob, json, math, os, random, statistics, sys

from paths import DATA, REPO, WS
import sci_metrics as S  # noqa: E402
import textcore as T  # noqa: E402

Z_MIN, PRIOR_MASS = 3.0, 1000.0
NAMES = ("glue", "human_function", "ai_function", "ai_content", "human_content")
MAX = {"ai_function": 22, "ai_content": 60, "human_content": 45, "human_function": 20, "glue": 6}


def auc(h, a):
    hs = sorted(h)
    tot = 0.0
    for x in a:
        lo, hi = bisect.bisect_left(hs, x), bisect.bisect_right(hs, x)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(a) * len(h))


def load(dirs, lang):
    docs = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(WS, d, "*.txt"))):
            doc = T.Doc(open(f, encoding="utf-8", errors="ignore").read(), lang)
            c = collections.Counter()
            for s in doc.all_sentences:
                for t, l, g in zip(s["toks"], s["lemmas"], s["tags"]):
                    if g in ("NUM", "PROPN", "ACRO") or not l or not l[0].isalpha():
                        continue
                    c[(l.lower(), "F" if (g in S.FUNCTION_TAGS or t in doc.lp.STOPWORDS) else "C")] += 1
            if sum(c.values()) >= 120:
                docs.append(c)
    return docs


def zscores(H, A):
    h, a, dh, da = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for d in H:
        h.update(d)
        dh.update(d.keys())
    for d in A:
        a.update(d)
        da.update(d.keys())
    NH, NA = sum(h.values()), sum(a.values())
    out = {}
    for w in set(h) | set(a):
        p = PRIOR_MASS * (h[w] + a[w]) / (NH + NA)
        delta = math.log((a[w] + p) / (NA + PRIOR_MASS - a[w] - p)) - math.log((h[w] + p) / (NH + PRIOR_MASS - h[w] - p))
        out[w] = (delta / math.sqrt(1 / (a[w] + p) + 1 / (h[w] + p)), dh[w] / len(H), da[w] / len(A), 1e3 * h[w] / NH, 1e3 * a[w] / NA)
    return out


def select(data, exclude=()):
    """data: {register: (human docs, AI docs)} -> lists"""
    Z = {r: zscores(H, A) for r, (H, A) in data.items()}
    dfmin = {r: (0.2 if statistics.median(sum(d.values()) for d in H) >= 400 else 0.12) for r, (H, A) in data.items()}
    words = set().union(*[set(z) for z in Z.values()])
    cand = {"ai_function": [], "ai_content": [], "human_content": [], "human_function": []}
    for w in words:
        if w[0] in exclude or len(w[0]) < 2:
            continue
        zs = {r: Z[r][w] for r in Z if w in Z[r]}
        up = [r for r, v in zs.items() if v[0] >= Z_MIN and v[2] >= dfmin[r]]
        dn = [r for r, v in zs.items() if v[0] <= -Z_MIN and v[1] >= dfmin[r]]
        if len(up) >= 2 and not any(v[0] <= -2 for v in zs.values()):
            cand["ai_function" if w[1] == "F" else "ai_content"].append((sum(zs[r][0] for r in up), w[0]))
        if len(dn) >= 2 and not any(v[0] >= 2 for v in zs.values()):
            cand["human_function" if w[1] == "F" else "human_content"].append((-sum(zs[r][0] for r in dn), w[0]))
    lists = {k: [w for _, w in sorted(v, reverse=True)][:MAX.get(k, 40)] for k, v in cand.items()}
    # glue: the most frequent grammatical lemmas of human text that AI under-uses
    freq = collections.Counter()
    for H, _ in data.values():
        for d in H:
            for (l, cls), k in d.items():
                if cls == "F":
                    freq[l] += k
    top10 = [w for w, _ in freq.most_common(10)]
    lists["glue"] = [w for w in top10 if w in lists["human_function"]][:MAX["glue"]]
    lists["human_function"] = [w for w in lists["human_function"] if w not in lists["glue"]][:MAX["human_function"]]
    detail = {k: {w: {r: round(Z[r][(w, "F" if "function" in k or k == "glue" else "C")][0], 1) for r in Z
                      if (w, "F" if "function" in k or k == "glue" else "C") in Z[r]} for w in v} for k, v in lists.items()}
    return lists, detail


def rates(doc, lists):
    n = sum(doc.values()) or 1
    lem = collections.Counter()
    for (l, cls), k in doc.items():
        lem[(l, cls)] += k
    out = {}
    for name, cls in (("ai_function", "F"), ("ai_content", "C"), ("human_content", "C"), ("human_function", "F"), ("glue", "F")):
        out[name] = 1000.0 * sum(lem[(w, cls)] for w in lists[name]) / n
    return out


def main():
    cfg = json.load(open(sys.argv[1]))
    lang = cfg["lang"]
    data = {r: (load(v["human"], lang), load(v["ai"], lang)) for r, v in cfg["registers"].items()}
    for r, (H, A) in data.items():
        print("%-12s human %d texts, AI %d texts" % (r, len(H), len(A)))
    lists, detail = select(data, set(cfg.get("exclude", [])))
    # cross-fitting
    rng = random.Random(5)
    held = collections.defaultdict(list)
    for rep in range(4):
        halves = {}
        for r, (H, A) in data.items():
            H2, A2 = H[:], A[:]
            rng.shuffle(H2)
            rng.shuffle(A2)
            halves[r] = ((H2[::2], A2[::2]), (H2[1::2], A2[1::2]))
        for a, b in ((0, 1), (1, 0)):
            l2, _ = select({r: halves[r][a] for r in data}, set(cfg.get("exclude", [])))
            for r in data:
                Ht, At = halves[r][b]
                for name in NAMES:
                    if l2[name]:
                        held[(r, name)].append(auc([rates(d, l2)[name] for d in Ht], [rates(d, l2)[name] for d in At]))
    print("\nAUC = P(AI rate > human rate); held-out = lists built on the other half of the documents")
    print("%-12s %-15s %9s %9s" % ("register", "list", "in-sample", "held-out"))
    heldout = {}
    for r, (H, A) in data.items():
        for name in NAMES:
            ins = auc([rates(d, lists)[name] for d in H], [rates(d, lists)[name] for d in A]) if lists[name] else float("nan")
            ho = statistics.mean(held[(r, name)]) if held[(r, name)] else float("nan")
            heldout.setdefault(r, {})[name] = {"in_sample": round(ins, 3), "held_out": round(ho, 3)}
            print("%-12s %-15s %9.3f %9.3f" % (r, name, ins, ho))
    for name in ("glue", "ai_function", "ai_content", "human_content", "human_function"):
        print("\n%s (%d): %s" % (name, len(lists[name]), ", ".join("%s %s" % (w, "/".join("%+.0f" % z for z in detail[name][w].values())) for w in lists[name])))
    if "--write" in sys.argv:
        glue_rates = [rates(d, lists)["glue"] / 10.0 for H, _ in data.values() for d in H]
        out = {"lang": lang, "glue": lists["glue"], "glue_reference": round(statistics.median(glue_rates), 1),
               "human_function": lists["human_function"],
               "ai_function": lists["ai_function"], "ai_content": lists["ai_content"], "human_content": lists["human_content"],
               "provenance": {"method": "log-odds with informative Dirichlet prior; |z| >= %.0f in >= 2 registers, same sign, no register opposite; see references/calibration.md" % Z_MIN,
                              "registers": {r: {"human_texts": len(H), "ai_texts": len(A)} for r, (H, A) in data.items()},
                              "auc": heldout, "z_by_register": detail}}
        path = os.path.join(DATA, "markers_%s.json" % lang)
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("\nwrote", os.path.relpath(path, REPO).replace(os.sep, "/"))


if __name__ == "__main__":
    main()
