#!/usr/bin/env python3
"""Evaluate the English lexicon tagger on the Brown sentences held out from lexicon building
(brown_test.json: [[word, coarse tag], ...] per sentence). Prints accuracy and the top confusions."""
import collections, json, os, re, sys
from paths import WS
import textcore as T


def main():
    tg = T.tagger("en")
    sents = json.load(open(os.path.join(WS, "brown_test.json"), encoding="utf-8"))
    ok = tot = gold_n = 0
    conf = collections.Counter()
    nv = collections.Counter()
    for sent in sents:
        gold = [(w.lower().replace("’", "'"), t) for w, t in sent if t not in ("PUNCT", "X") and re.search(r"[A-Za-z0-9]", w)]
        text = " ".join(w for w, _ in sent)
        toks, tags, lemmas, origs = tg.analyse(text)
        gold_n += len(gold)
        j = 0
        for g, u in gold:
            if j >= len(toks):
                break
            # the tagger may split a gold word (didn't -> did + n't; Britain's -> britain + 's)
            if toks[j] == g:
                k = j + 1
            else:
                acc, k = toks[j], j + 1
                while k < len(toks) and len(acc) < len(g) and g.startswith(acc + toks[k]):
                    acc += toks[k]
                    k += 1
                if acc != g:
                    # resynchronise on the next exact match within a short window
                    nxt = next((x for x in range(j, min(j + 4, len(toks))) if toks[x] == g), None)
                    if nxt is None:
                        continue
                    j, k = nxt, nxt + 1
            p = {"ACRO": "PROPN"}.get(tags[j], tags[j])
            tot += 1
            good = p == u
            ok += good
            if not good:
                conf[(u, p)] += 1
            if u in ("NOUN", "VERB") and p in ("NOUN", "VERB"):
                nv[(u, p)] += 1
            j = k
    print("gold tokens %d | aligned %d (%.1f%%) | tag accuracy %.4f" % (gold_n, tot, 100.0 * tot / gold_n, ok / tot))
    print("top confusions (gold -> predicted):", conf.most_common(12))
    print("noun/verb: " + ", ".join("%s->%s %d" % (a, b, n) for (a, b), n in sorted(nv.items())))


if __name__ == "__main__":
    main()
