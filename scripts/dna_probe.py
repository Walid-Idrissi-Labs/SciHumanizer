#!/usr/bin/env python3
"""Continuation probe (after DNA-GPT's divergent n-gram analysis, Yang et al. 2023).

Idea from the research: truncate a text and let a model regenerate the rest. Model-written
text is regenerated with high n-gram overlap (the model "converges" on it); human text diverges.
Here the question is practical: which paragraphs of a draft are so predictable that a fresh
model writes nearly the same thing when given only their first half?

  dna_probe.py split DRAFT [--out probe.json] [--lang en|fr]  -> prefixes to give a FRESH model (subagent)
  dna_probe.py score probe.json continuations.json    -> overlap per paragraph

continuations.json: {"p1": "continuation text", "p2": "...", ...}  (or {"p1": ["run 1", "run 2"]})

How to read it (see references/calibration.md section 9):
  The decisive check is semantic. `score` prints each real second half next to the fresh model's
  continuation. Rate every pair: 2 = same points in the same order, 1 = partly overlapping,
  0 = different points. In a blind calibration on 24 scientific paragraphs, 42% of AI-written
  paragraphs were rated 2 versus 8% of human ones. If more than about 1 in 5 of your paragraphs
  rate 2, rework those paragraphs: add what only this text can say (the specific result, the
  caveat, the disagreement) or cut the predictable second half.
  The n-gram overlap score is only a rough ranking aid: exact-overlap separation was weak
  (AUC 0.63) with one continuation per paragraph.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textcore as T  # noqa: E402

WEIGHTS = {n: n * math.log(n) for n in (2, 3, 4)}


def grams(text, n):
    w = [x.lower() for x in T.raw_tokens(text)]
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def overlap(cont, suffix):
    per = {}
    for n in WEIGHTS:
        gs = grams(suffix, n)
        gc = grams(cont, n)
        per[n] = len(gs & gc) / len(gs) if gs else 0.0
    score = sum(WEIGHTS[n] * per[n] for n in WEIGHTS) / sum(WEIGHTS.values())
    return score, per


def cmd_split(a):
    doc = T.Doc(T.read_text(a.draft), a.lang)
    items = []
    for i, par in enumerate(doc.paragraphs):
        if len(par) < a.min_sents:
            continue
        k = math.ceil(len(par) / 2)
        prefix = " ".join(s["text"] for s in par[:k])
        suffix = " ".join(s["text"] for s in par[k:])
        items.append({"id": "p%d" % (i + 1), "prefix": prefix, "suffix": suffix,
                      "suffix_words": len(T.words(suffix))})
    if not items and doc.sentences:  # short text: split the whole document
        k = math.ceil(len(doc.sentences) / 2)
        items.append({"id": "doc", "prefix": " ".join(s["text"] for s in doc.sentences[:k]),
                      "suffix": " ".join(s["text"] for s in doc.sentences[k:]),
                      "suffix_words": sum(s["n"] for s in doc.sentences[k:])})
    out = a.out or os.path.splitext(a.draft)[0] + ".probe.json"
    json.dump(items, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("wrote %d probe items to %s\n" % (len(items), out))
    print("---- prompt for a FRESH subagent (it must not have seen the draft) ----")
    print("Continue each passage below the way it would most naturally go on%s. Write about the given number "
          "of words for each, in the same style, and nothing else. Return JSON: {\"<id>\": \"<continuation>\"}.\n"
          % (", in French" if doc.lang == "fr" else ""))
    for it in items:
        print("[%s] (~%d words)\n%s\n" % (it["id"], it["suffix_words"], it["prefix"]))
    return 0


def cmd_score(a):
    items = {it["id"]: it for it in json.load(open(a.probe, encoding="utf-8"))}
    conts = json.load(open(a.continuations, encoding="utf-8"))
    rows = []
    for pid, it in items.items():
        c = conts.get(pid)
        if c is None:
            continue
        runs = c if isinstance(c, list) else [c]
        sc = [overlap(r, it["suffix"]) for r in runs]
        mean_score = sum(x[0] for x in sc) / len(sc)
        per = {n: round(sum(x[1][n] for x in sc) / len(sc), 3) for n in WEIGHTS}
        rows.append((pid, round(mean_score, 4), per))
    if not rows:
        print("no matching ids")
        return 2
    rows.sort(key=lambda r: -r[1])
    avg = sum(r[1] for r in rows) / len(rows)
    print("# Continuation probe  (mean weighted n-gram overlap = %.4f over %d passages; ranking aid only)" % (avg, len(rows)))
    for pid, sc_, per in rows:
        print("- %s: overlap=%.4f  2g=%.3f 3g=%.3f 4g=%.3f" % (pid, sc_, per[2], per[3], per[4]))
    print("\n# Rate each pair: 2 = same points in the same order, 1 = partly overlapping, 0 = different points.")
    print("# Rework any paragraph rated 2; aim for at most ~1 in 5 rated 2 (human baseline 8%, AI baseline 42%).")
    for pid, _, _ in rows:
        c = conts[pid]
        c = c[0] if isinstance(c, list) else c
        print("\n=== %s\nREAL: %s\nFRESH MODEL: %s" % (pid, items[pid]["suffix"], c))
    return 0


def main():
    T.utf8_output()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sp = sub.add_parser("split")
    sp.add_argument("draft")
    sp.add_argument("--out")
    sp.add_argument("--min-sents", type=int, default=4)
    sp.add_argument("--lang", choices=["en", "fr"], default=None)
    sc = sub.add_parser("score")
    sc.add_argument("probe")
    sc.add_argument("continuations")
    a = ap.parse_args()
    if a.cmd == "split":
        return cmd_split(a)
    if a.cmd == "score":
        return cmd_score(a)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
