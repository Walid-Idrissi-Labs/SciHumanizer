#!/usr/bin/env python3
"""Brown corpus -> (1) plain text per genre, (2) compact POS lexicon for the analyzer.

Lexicon format (TSV): word <tab> TAG:count[,TAG:count]  (top-2 coarse tags, lowercase word)
Coarse tags: NOUN PROPN VERB AUX MODAL ADJ ADJC ADJS ADV ADVC PRT PRON DET ADP CCONJ SCONJ NUM TO X
"""
import collections, json, os, random, re, sys

from paths import WS
SRC = os.path.join(WS, "corpora", "brown")
OUT_TXT = os.path.join(WS, "corpora", "brown_txt")
LEX_OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WS, "en_lexicon.tsv")


def coarse(tag):
    t = tag.lower()
    t = re.sub(r"-(hl|tl|nc)$", "", t)
    t = re.sub(r"-(hl|tl|nc)$", "", t)
    if t.startswith("fw-"):
        return "X"
    t = t.split("+")[0]
    t = t.rstrip("*")
    if t in ("np", "nps", "np$", "nps$"):
        return "PROPN"
    if t.startswith("nn") or t.startswith("nr"):
        return "NOUN"
    if t.startswith("vb"):
        return "VERB"
    if t.startswith("be") or t.startswith("hv") or t.startswith("do"):
        return "AUX"
    if t == "md":
        return "MODAL"
    if t == "jjr":
        return "ADJC"
    if t in ("jjs", "jjt"):
        return "ADJS"
    if t.startswith("jj"):
        return "ADJ"
    if t == "rbr":
        return "ADVC"
    if t in ("rb", "rbt", "rn", "ql", "qlp", "wrb", "rb$"):
        return "ADV"
    if t == "rp":
        return "PRT"
    if t in ("at", "ap", "abn", "abx", "dt", "dti", "dts", "dtx", "wdt", "abl", "ap$", "dt$"):
        return "DET"
    if t.startswith("pp") or t.startswith("wp") or t in ("ex", "prp"):
        return "PRON"
    if t == "in":
        return "ADP"
    if t == "to":
        return "TO"
    if t == "cc":
        return "CCONJ"
    if t == "cs":
        return "SCONJ"
    if t in ("cd", "od", "cd$"):
        return "NUM"
    if t in (".", ",", ":", "(", ")", "''", "``", "'", "--", "nil", ""):
        return "PUNCT"
    return "X"


def read_file(path):
    paras, cur = [], []
    for line in open(path, encoding="latin-1"):
        if not line.strip():
            if cur:
                paras.append(cur)
                cur = []
            continue
        toks = []
        for tt in line.split():
            if "/" not in tt:
                continue
            w, tag = tt.rsplit("/", 1)
            toks.append((w, tag))
        if toks:
            cur.append(toks)
    if cur:
        paras.append(cur)
    return paras  # list of paragraphs -> list of sentences -> list of (w, tag)


def detok(sent):
    out = ""
    quote_open = False
    for w, tag in sent:
        if w == "``":
            out += (" " if out else "") + '"'
            quote_open = True
            continue
        if w == "''":
            out += '"'
            quote_open = False
            continue
        if out.endswith('"') and quote_open and out[-2:-1] in (" ", ""):
            out += w
            continue
        if w in (",", ".", ";", ":", "!", "?", ")", "'s", "n't", "'re", "'ve", "'ll", "'d", "'m", "%") or out.endswith("("):
            out += w
        elif w == "--":
            out += " -- "
        else:
            out += (" " if out and not out.endswith(" ") else "") + w
    out = re.sub(r"\s+", " ", out).replace(" -- ", " -- ")
    return out.strip()


def main():
    cats = {}
    for line in open(os.path.join(SRC, "cats.txt")):
        f, c = line.split()
        cats[f] = c
    files = sorted(cats)
    random.seed(7)
    held = set(random.sample(files, 50))
    lex = collections.defaultdict(collections.Counter)
    test = []
    for f in files:
        paras = read_file(os.path.join(SRC, f))
        # plain text
        d = os.path.join(OUT_TXT, cats[f])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f + ".txt"), "w") as fh:
            fh.write("\n\n".join(" ".join(detok(s) for s in p) for p in paras) + "\n")
        for p in paras:
            for s in p:
                if f in held:
                    test.append(s)
                    continue
                for w, tag in s:
                    c = coarse(tag)
                    if c == "PUNCT":
                        continue
                    lex[w.lower()][c] += 1
    # write lexicon (words seen >= 2 times, or closed-class)
    n = 0
    with open(LEX_OUT, "w") as fh:
        fh.write("# Coarse POS lexicon derived from the tagged Brown Corpus (Francis & Kucera 1961/1979, NLTK distribution).\n")
        fh.write("# word\ttop tags with counts. Used by sci_metrics.py for approximate POS ratios.\n")
        for w, cnt in sorted(lex.items()):
            tot = sum(cnt.values())
            if tot < 2 and not any(k in ("DET", "PRON", "ADP", "CCONJ", "SCONJ", "MODAL", "AUX") for k in cnt):
                continue
            if not re.match(r"^[a-z][a-z'\-]*$", w):
                continue
            top = cnt.most_common(2)
            fh.write(w + "\t" + ",".join(f"{t}:{c}" for t, c in top) + "\n")
            n += 1
    print("lexicon entries:", n, "->", LEX_OUT)
    json.dump({"held_out": sorted(held)}, open(os.path.join(WS, "brown_heldout.json"), "w"))
    json.dump([[(w, coarse(t)) for w, t in s] for s in test], open(os.path.join(WS, "brown_test.json"), "w"))
    print("held-out sentences:", len(test))


if __name__ == "__main__":
    main()
