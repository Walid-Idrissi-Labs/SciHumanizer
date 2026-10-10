#!/usr/bin/env python3
"""Build the French lemma + POS lexicon for the analyzer.

Sources (both CC BY-SA 4.0, so the derived file is CC BY-SA 4.0 as well):
  Lexique 3.83 (New, Pallier, Brysbaert & Ferrand 2004; lexique.org): form, lemma, category, frequency
  UD_French-GSD train+dev (Universal Dependencies): which reading a form takes in running text

Output TSV: form <tab> TAG:lemma:weight[,TAG:lemma:weight]   (top two readings, lowercase form)
Tags: NOUN PROPN VERB AUX ADJ ADV PRON DET ADP CCONJ SCONJ NUM X
"""
import collections, csv, os, re, sys

from paths import WS
LEX = os.path.join(WS, "fr", "lex")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WS, "fr", "fr_lexicon.tsv")
MIN_FREQ = 0.30     # per million, Lexique (books or films)

CCONJ = {"et", "ou", "mais", "donc", "or", "ni", "car", "soit", "puis", "voire"}
CGRAM = {"NOM": "NOUN", "VER": "VERB", "AUX": "AUX", "ADJ": "ADJ", "ADV": "ADV", "PRE": "ADP", "ONO": "X", "LIA": "X",
         "ADJ:num": "NUM", "ADJ:ind": "DET", "ADJ:pos": "DET", "ADJ:dem": "DET", "ADJ:int": "DET",
         "ART:def": "DET", "ART:ind": "DET", "PRO:per": "PRON", "PRO:ind": "PRON", "PRO:pos": "PRON",
         "PRO:int": "PRON", "PRO:rel": "PRON", "PRO:dem": "PRON"}


def fnum(x):
    try:
        return float(x)
    except ValueError:
        return 0.0


def main():
    lexi = collections.defaultdict(dict)      # form -> {tag: (lemma, freq)}
    with open(os.path.join(LEX, "Lexique383.tsv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            form, lemma, cg = r["ortho"].lower(), r["lemme"].lower(), r["cgram"]
            if not form or " " in form:
                continue
            tag = "CCONJ" if cg == "CON" and form in CCONJ else ("SCONJ" if cg == "CON" else CGRAM.get(cg))
            if tag is None:
                continue
            f = max(fnum(r["freqlivres"]), fnum(r["freqfilms2"]))
            old = lexi[form].get(tag)
            if old is None or f > old[1]:
                lexi[form][tag] = (lemma, f)
    ud = collections.defaultdict(collections.Counter)      # form -> tag counts in running text
    ud_lemma = {}
    for part in ("train", "dev"):
        for line in open(os.path.join(LEX, "fr_gsd-ud-%s.conllu" % part), encoding="utf-8"):
            if not line.strip() or line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            form, lemma, upos = c[1].lower(), c[2].lower(), c[3]
            if upos in ("PUNCT", "SYM", "X", "INTJ", "PART") or not re.match(r"^[a-zà-öø-ÿœæ]", form):
                continue
            form = form.replace("’", "'")
            ud[form][upos] += 1
            ud_lemma.setdefault((form, upos), collections.Counter())[lemma] += 1
    forms = set(f for f, rd in lexi.items() if max(v[1] for v in rd.values()) >= MIN_FREQ or
                any(t in ("DET", "PRON", "ADP", "CCONJ", "SCONJ", "AUX") for t in rd))
    forms |= set(f for f, c in ud.items() if sum(c.values()) >= 2 and "PROPN" not in c)
    n = 0
    with open(OUT, "w", encoding="utf-8") as out:
        out.write("# French lemma + POS lexicon derived from Lexique 3.83 (lexique.org) and UD_French-GSD. Licence: CC BY-SA 4.0.\n")
        out.write("# form\tTAG:lemma:weight[,TAG:lemma:weight]  (weight = occurrences per million; two most likely readings)\n")
        for form in sorted(forms):
            if not re.match(r"^[a-zà-öø-ÿœæ][a-zà-öø-ÿœæ'\-]*$", form):
                continue
            cand = {}
            utot = sum(ud[form].values()) if form in ud else 0
            if utot >= 5:                                # usage in running text decides the ranking
                for tag, k in ud[form].items():
                    if tag == "PROPN":
                        continue
                    lem = lexi.get(form, {}).get(tag, (None, 0))[0] or ud_lemma[(form, tag)].most_common(1)[0][0]
                    cand[tag] = (lem, 1e6 * k / 400000.0)
                for tag, (lem, f) in lexi.get(form, {}).items():   # keep rarer dictionary readings as fallbacks
                    cand.setdefault(tag, (lem, min(f, 0.5)))
            else:
                for tag, (lem, f) in lexi.get(form, {}).items():
                    cand[tag] = (lem, f)
                for tag, k in (ud[form].items() if form in ud else []):
                    if tag != "PROPN" and tag not in cand:
                        cand[tag] = (ud_lemma[(form, tag)].most_common(1)[0][0], 1e6 * k / 400000.0)
            if not cand:
                continue
            top = sorted(cand.items(), key=lambda kv: -kv[1][1])[:2]
            out.write(form + "\t" + ",".join("%s:%s:%.2f" % (t, l.replace(":", "").replace(",", ""), w) for t, (l, w) in top) + "\n")
            n += 1
    print("entries:", n, "->", OUT, "| bytes:", os.path.getsize(OUT))


if __name__ == "__main__":
    main()
