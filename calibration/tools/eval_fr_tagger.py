#!/usr/bin/env python3
"""Evaluate the French lexicon tagger on UD_French-GSD test (held out from lexicon building)."""
import collections, os, re, sys
from paths import WS
import textcore as T

def norm(f):
    return re.sub(r"^-(?:t-)?", "", f.lower().replace("’", "'"))

def sentences(path):
    text, toks, skip = None, [], set()
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# text ="):
            text = line[8:].strip()
        elif not line.strip():
            if text and toks:
                yield text, toks
            text, toks, skip = None, [], set()
        elif not line.startswith("#"):
            c = line.split("\t")
            if "." in c[0]:
                continue
            if "-" in c[0]:                      # multiword token: keep surface form, tag = first part
                a, b = c[0].split("-")
                skip = set(range(int(a), int(b) + 1))
                toks.append([c[1], None, int(a)])
                continue
            i = int(c[0])
            if i in skip:
                for t in toks:
                    if t[1] is None and t[2] == min(skip):
                        t[1] = c[3]
                continue
            toks.append([c[1], c[3], i])

def main():
    tg = T.tagger("fr")
    ok = tot = aligned = gold_n = 0
    conf = collections.Counter()
    lem_ok = lem_tot = 0
    oov = collections.Counter()
    for text, gold in sentences(os.path.join(WS, "fr", "lex", "fr_gsd-ud-test.conllu")):
        gold = [(norm(f), u) for f, u, _ in gold if u not in ("PUNCT", "SYM", "X", "INTJ", None) and re.search(r"[a-zà-ÿ0-9]", f.lower())]
        toks, tags, lemmas, origs = tg.analyse(text)
        gold_n += len(gold)
        i = j = 0
        while i < len(gold) and j < len(toks):
            g, u = gold[i]
            t = toks[j]
            if g == t or g.rstrip("'") == t.rstrip("'"):
                p = {"ACRO": "PROPN"}.get(tags[j], tags[j])
                tot += 1; aligned += 1
                good = (p == u) or (u == "PART" and p == "ADV")
                ok += good
                if not good:
                    conf[(u, p)] += 1
                if t not in tg.lex and not t[0].isdigit() and tags[j] not in ("PROPN", "ACRO") and t not in tg.lp.CLITIC_TAGS:
                    oov[t] += 1
                i += 1; j += 1
            elif i + 1 < len(gold) and gold[i + 1][0] == t:
                i += 1
            elif j + 1 < len(toks) and toks[j + 1] == g:
                j += 1
            else:
                i += 1; j += 1
    print("gold tokens %d | aligned %d (%.1f%%) | tag accuracy %.4f" % (gold_n, aligned, 100.0 * aligned / gold_n, ok / tot))
    print("top confusions (gold -> predicted):", conf.most_common(10))
    print("OOV tokens (not proper nouns): %d = %.2f%% of aligned; examples: %s" % (sum(oov.values()), 100.0 * sum(oov.values()) / aligned, [w for w, _ in oov.most_common(15)]))

if __name__ == "__main__":
    main()
