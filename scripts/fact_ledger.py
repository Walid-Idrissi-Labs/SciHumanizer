#!/usr/bin/env python3
"""Fact ledger: prove a rewrite kept every hard fact and invented none. English and French.

  fact_ledger.py SOURCE DRAFT [--facts FACTS] [--write] [--protect "term a,term b"] [--lang en|fr] [--json]

  --write: WRITE mode (SOURCE is the user's brief). Only additions fail: a brief's numbers need not
           all be used, and instructions such as "about 700 words" are not facts.

  --facts: extra facts the user supplied beyond SOURCE (an abstract, notes). Values found there may
           appear in DRAFT without counting as "added", but they are not required (an introduction
           need not repeat the abstract's results). Everything in SOURCE must still survive.

Extracts from both texts and compares:
  numbers        11%, 95% CI, 1.9 million, 2008-2018, p < 0.05, n = 45 (French: 3,5 %, 1 200, 1,9 million);
                 values are normalised, so 1,200 = 1200 and 3,5 % = 3.5%
  citations      [12], [3-5], (Smith et al., 2020), Smith and Jones (2019): compared as references
                 (first author + year, or number), so moving a citation into the sentence is not a change
  entities       capitalised names and acronyms that are not just sentence-initial words
  protected      user-supplied technical terms that must survive verbatim
  certainty      hedges / boosters / negations per 1,000 words (a shift means a claim changed strength)

Exit code 1 when a distinct number or citation is missing or added, or a protected term is lost
(repeating a sourced number is not an addition); 0 otherwise. A number that is absent from the source
but equals simple arithmetic on two source numbers standing in the same paragraph of the draft (a
total, a ratio, a percentage, a relative change, a complement) is listed with the formula found
instead of failing. Entity and certainty differences are warnings to review by hand.
"""
import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textcore as T  # noqa: E402

SP = "   "
_NAME = r"[%s][%s'’\-]+" % (T.UPPER, T.LETTERS)
_YEAR = r"(?:1[6-9]|20)\d\d[a-z]?"
_PAREN_YEAR = re.compile(r"\(([^()]*\b%s\b[^()]*)\)" % _YEAR)
_IN_PAREN = re.compile(r"(%s)(?:\s+(?:et al\.?|et coll\.?)|\s+(?:and|et|&)\s+%s)?,?\s+(%s)" % (_NAME, _NAME, _YEAR))
_NARRATIVE = re.compile(r"(%s)(?:\s+(?:et al\.?|et coll\.?)|\s+(?:and|et|&)\s+%s)?\s+\((%s)[^()]{0,20}\)" % (_NAME, _NAME, _YEAR))
_BRACKET = re.compile(r"\[\s*(\d+(?:\s*[-–,;]\s*\d+)*)\s*\]")


def _value(raw, lp):
    """Digits as written -> float, following the language's separators."""
    t = raw
    if lp.DECIMAL_COMMA:
        t = re.sub(r"(?<=\d)[%s](?=\d{3}(?!\d))" % SP, "", t)             # 1 200 -> 1200
        if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", t):                    # 1.200,5 -> 1200.5
            t = t.replace(".", "")
        t = t.replace(",", ".")
    elif re.match(r"^\d{1,3}(,\d{3})+(\.\d+)?$", t):                      # 1,200.5 -> 1200.5
        t = t.replace(",", "")
    try:
        return float(t.rstrip("."))
    except ValueError:
        return None


def numbers(text, lang="en"):
    """Return (counts, contexts, digit_keys). Keys are normalised values ('1200', '3.5%'); digit_keys
    holds the values written with digits somewhere, which are the hard facts."""
    lp = T.pack(lang)
    t = re.sub(r"(\d)[%s]*%s(?![\w])" % (SP, lp.PERCENT_WORDS), r"\1%", text, flags=re.I)
    t = re.sub(r"(\d)[%s]+%%" % SP, r"\1%", t)
    scale = "|".join(sorted(lp.SCALE, key=len, reverse=True))
    if lp.DECIMAL_COMMA:
        num = r"\d{1,3}(?:[%s]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)*" % SP
    else:
        num = r"\d+(?:[.,]\d+)*"
    out, ctx, digit_keys = collections.Counter(), {}, set()
    for m in re.finditer(r"(?<![\w.,])(%s)(%%)?(?:[%s]*(%s)(?![\w]))?" % (num, SP, scale), t, flags=re.I):
        v = _value(m.group(1), lp)
        if v is None:
            continue
        if m.group(3):
            v *= lp.SCALE[m.group(3).lower()]
        key = ("%.10g" % v) + ("%" if m.group(2) else "")
        out[key] += 1
        digit_keys.add(key)
        ctx.setdefault(key, t[max(0, m.start() - 35): m.end() + 25].replace("\n", " "))
    words = "|".join(sorted(lp.NUMWORDS, key=len, reverse=True))
    for m in re.finditer(r"(?<![\w'’-])(%s)(?:[\s-]+(%s))?(?![\w'’])" % (words, scale), t, flags=re.I):
        v = lp.NUMWORDS[m.group(1).lower()] * (lp.SCALE[m.group(2).lower()] if m.group(2) else 1)
        key = "%.10g" % v
        out[key] += 1
        ctx.setdefault(key, t[max(0, m.start() - 35): m.end() + 25].replace("\n", " "))
    return out, ctx, digit_keys


def citations(text, lang="en"):
    """References as keys: '[12]' for numbered styles, 'smith 2020' (first author + year) otherwise."""
    lp = T.pack(lang)
    keys = collections.Counter()
    for m in _BRACKET.finditer(text):
        for part in re.split(r"\s*[,;]\s*", m.group(1)):
            r = re.split(r"\s*[-–]\s*", part)
            if len(r) == 2 and r[0].isdigit() and r[1].isdigit() and 0 < int(r[1]) - int(r[0]) <= 30:
                for k in range(int(r[0]), int(r[1]) + 1):
                    keys["[%d]" % k] += 1
            else:
                keys["[%s]" % part] += 1
    seen = set()
    for m in _PAREN_YEAR.finditer(text):
        for c in _IN_PAREN.finditer(m.group(1)):
            if c.group(1).lower() not in lp.NOT_AUTHORS:
                keys["%s %s" % (c.group(1).lower(), c.group(2))] += 1
                seen.add(m.start(1) + c.start())
    for c in _NARRATIVE.finditer(text):
        if c.group(1).lower() not in lp.NOT_AUTHORS and c.start() not in seen:
            keys["%s %s" % (c.group(1).lower(), c.group(2))] += 1
    return keys


def entities(text, lang="en"):
    lp = T.pack(lang)
    ents = collections.Counter()
    for sent in re.split(r"(?<=[.!?…])\s+", text):
        toks = re.findall(r"[%s][%s0-9'’\-]*" % (T.LETTERS, T.LETTERS), sent)
        for i, w in enumerate(toks):
            w = re.sub(r"^(?:[LlDdJjNnSsCcMmTt]|[Qq]u)['’]", "", w) if lang == "fr" else w
            if not w:
                continue
            if re.match(r"^[%s][%s0-9\-]{1,}s?$" % (T.UPPER, T.UPPER), w):          # acronym
                ents[w] += 1
            elif i > 0 and w[0].isupper() and w.lower() not in lp.STOPWORDS:
                ents[w] += 1
    return ents


def rate(text, terms):
    low = T.norm(text)
    n = 0
    for t in terms:
        right = r"(?![\w'])" if t[-1].isalnum() else ""
        n += len(re.findall(r"(?<!\w)" + re.escape(t) + right, low))
    return n


_REQUEST = re.compile(r"\b(?:please|draft|write|rewrite|humani[sz]e|make it|rédige[zr]?|écris|écrivez|peux-tu|pouvez-vous|"
                      r"merci de|reformule[zr]?)\b", re.I)


def unused(source_text, draft_text, lang="en"):
    """What the source holds that the draft does not use yet: material for lengthening without padding.
    Sentences of a brief that are requests ("Please draft the Discussion, about 700 words") are not facts."""
    source_text = " ".join(s for s in re.split(r"(?<=[.!?:])\s+", source_text) if not _REQUEST.search(s))
    ns, cs, ds = numbers(source_text, lang)
    nd, _, _ = numbers(draft_text, lang)
    es, low = entities(source_text, lang), draft_text.lower()
    return {"numbers": [k for k in ns if k in ds and k not in nd],
            "names": [k for k, _ in es.most_common() if k.lower() not in low],
            "contexts": {k: cs[k].strip() for k in ns if k in ds and k not in nd}}


def derivation(key, source_keys):
    """If a number that is absent from the source equals simple arithmetic on two source numbers, rounded
    as written (38 x 45 = 1710; 60 / 38 = 1.6; 100 x 9 / 38 = 24%; 2000 x (100 - 89%) = 220; a relative
    change, 100 x (1840 - 1210) / 1840 = 34%), return the formulas found (at most three: coincidences
    happen, the writer confirms which one is meant). Percentages come only from percentage arithmetic;
    bare integers under 10 are never accepted."""
    pct = key.endswith("%")
    try:
        x = float(key.rstrip("%"))
    except ValueError:
        return []
    dec = len(key.rstrip("%").split(".")[1]) if "." in key else 0
    if x < 10 and dec == 0 and not pct:
        return []
    tol = 0.5 * 10 ** (-dec) + 1e-9
    vals = []
    for k in source_keys:
        try:
            vals.append((float(k.rstrip("%")), k.endswith("%"), k))
        except ValueError:
            pass
    found = []
    for a, ap, ka in vals:
        if pct and ap and abs(100 - a - x) <= tol:
            found.append("100 - %s" % ka)
        for b, bp, kb in vals:
            if ka == kb:
                continue
            if pct:
                cands = [("100 x %s / %s", 100.0 * a / b)] if (not ap and not bp and b) else []
                if ap and bp:
                    cands += [("%s + %s", a + b), ("%s - %s", a - b)]
            elif not ap and not bp:
                cands = [("%s + %s", a + b), ("%s - %s", a - b), ("%s x %s", a * b)] + ([("%s / %s", a / b)] if b else [])
            elif not ap and bp:
                cands = [("%s x %s", a * b / 100.0), ("%s x (100 - %s)", a * (100 - b) / 100.0)]
            else:
                cands = []
            for fmt, c in cands:
                pair = tuple(sorted((ka, kb))) if fmt in ("%s + %s", "%s x %s") else (ka, kb)
                if abs(c - x) <= tol and (fmt % pair) not in found:
                    found.append(fmt % pair)
            # relative change: b is x% less (or more) than a
            if pct and not ap and not bp and a > 0 and b > 0 and abs(100.0 * abs(a - b) / a - x) <= tol:
                hi, lo = (ka, kb) if a > b else (kb, ka)
                rel = "100 x (%s - %s) / %s" % (hi, lo, ka)
                if rel not in found:
                    found.append(rel)
    # relative changes first, then products and ratios, then sums and differences
    found.sort(key=lambda f: (0 if f.startswith("100 x (") else 2 if ("+" in f or " - " in f) else 1, len(f)))
    return found[:3]


def ledger(src, dft, facts="", lang=None, write=False, protect=()):
    lang = lang or T.detect_lang(src)
    lp = T.pack(lang)
    ns, cs, ds = numbers(src, lang)
    nd, cd, dd = numbers(dft, lang)
    nf, _, _ = numbers(facts, lang)
    allowed = set(ns) | set(nf)
    # Distinct values decide the verdict: repeating a sourced number for emphasis is not fabrication,
    # and mentioning a sourced number fewer times is not a loss. Count changes are reported as info.
    # Values written only as words ("two trends", "an eleven-year period") are review items: they are
    # often counting words or ranges rephrased, not data. Values written with digits are hard facts.
    num_missing = {k: v for k, v in ns.items() if k not in nd and k in ds}
    num_added = {k: v for k, v in nd.items() if k not in allowed and k in dd}
    # A number absent from the source counts as derived only when it is arithmetic on source numbers that
    # stand in the same paragraph of the draft, where the reader can check it. A source with thirty
    # numbers has some pair matching almost any value by coincidence, so a match with operands that are
    # not nearby proves nothing: it is reported, and the number still counts as added.
    near, beside = collections.defaultdict(set), collections.defaultdict(set)
    for para in re.split(r"\n\s*\n", dft):
        pn = set(numbers(para, lang)[0])
        for k in pn:
            near[k] |= pn - {k}
        for sent in re.split(r"(?<=[.!?…])\s+(?=[%s\d«\"(\[])" % T.UPPER, para):
            sn = set(numbers(sent, lang)[0])
            for k in sn:
                beside[k] |= sn - {k}
    derived, pending, progress = {}, dict(num_added), True
    while progress:                 # a derived number can be the operand of the next (630, then 34%)
        progress = False
        for k in list(pending):
            # operands in the same sentence explain the number best; then the rest of the paragraph
            f = (derivation(k, [x for x in beside[k] if x in allowed or x in derived]) or
                 derivation(k, [x for x in near[k] if x in allowed or x in derived]))
            if f:
                derived[k] = " or ".join(f)
                del pending[k]
                progress = True
    far = {k: " or ".join(f) for k, f in ((k, derivation(k, list(allowed))) for k in pending) if f}
    num_added = pending
    word_missing = {k: v for k, v in ns.items() if k not in nd and k not in ds}
    word_added = {k: v for k, v in nd.items() if k not in allowed and k not in dd}
    num_recount = {k: [ns[k], nd[k]] for k in ns if k in nd and ns[k] != nd[k]}
    cis, cid, cif = citations(src, lang), citations(dft, lang), citations(facts, lang)
    cit_missing = sorted(k for k in cis if k not in cid)
    cit_added = sorted(k for k in cid if k not in cis and k not in cif)
    es, ed = entities(src, lang), entities(dft, lang)
    ent_missing = sorted(k for k in es if k not in ed and k.lower() not in dft.lower())
    ent_added = sorted(k for k in ed if k not in es and k.lower() not in (src + " " + facts).lower())
    prot_lost = [t for t in protect if t.lower() in src.lower() and t.lower() not in dft.lower()]
    ws, wd = max(1, T.count_words(src)), max(1, T.count_words(dft))
    cert = {}
    for name, terms in (("hedges", lp.LEDGER_HEDGES), ("boosters", lp.LEDGER_BOOSTERS), ("negations", lp.NEGATIONS)):
        s_n, d_n = rate(src, terms), rate(dft, terms)
        cert[name] = {"source": s_n, "draft": d_n, "source_per1k": round(1000 * s_n / ws, 2),
                      "draft_per1k": round(1000 * d_n / wd, 2)}
    warnings = []
    h = cert["hedges"]
    if write:
        pass          # a brief is not prose: its hedge and negation counts say nothing about the draft
    elif h["source"] >= 1 and h["draft"] < h["source"] and h["draft_per1k"] < 0.7 * h["source_per1k"]:
        warnings.append("Hedges dropped (%d -> %d): check that no tentative claim became a flat assertion." % (h["source"], h["draft"]))
    b = cert["boosters"]
    if not write and b["draft"] >= 2 and b["draft_per1k"] > 1.5 * max(b["source_per1k"], 1):
        warnings.append("Boosters increased: check for overclaiming (e.g. 'shows' -> 'proves', 'may' -> 'will').")
    ng = cert["negations"]
    if not write and ng["source"] != ng["draft"]:
        warnings.append("Negation count changed (%d -> %d): verify that no negation was lost or added." % (ng["source"], ng["draft"]))
    hard = bool(num_added or cit_added) if write else bool(num_missing or num_added or cit_missing or cit_added or prot_lost)
    return {"lang": lang, "words": {"source": ws, "draft": wd},
            "numbers_missing": {k: [v, cs.get(k, "")] for k, v in num_missing.items()},
            "numbers_added": {k: [v, cd.get(k, "")] for k, v in num_added.items()},
            "numbers_derived": {k: [f, cd.get(k, "")] for k, f in derived.items()},
            "numbers_added_far_match": far,
            "citations_missing": cit_missing, "citations_added": cit_added,
            "entities_missing": ent_missing, "entities_added": ent_added,
            "protected_lost": prot_lost, "certainty": cert, "warnings": warnings,
            "number_mentions_changed": num_recount,
            "number_words_missing": {k: [v, cs.get(k, "")] for k, v in word_missing.items()},
            "number_words_added": {k: [v, cd.get(k, "")] for k, v in word_added.items()},
            "hard_fail": hard}


def main():
    T.utf8_output()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("draft")
    ap.add_argument("--facts", default=None, help="file with extra user-supplied facts (allowed, not required)")
    ap.add_argument("--write", action="store_true", help="WRITE mode: fail only on additions")
    ap.add_argument("--protect", default="")
    ap.add_argument("--lang", choices=["en", "fr"], default=None, help="default: detected from SOURCE")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = T.read_text(a.source)
    dft = T.read_text(a.draft)
    facts = T.read_text(a.facts) if a.facts else ""
    res = ledger(src, dft, facts, a.lang, a.write, [t.strip() for t in a.protect.split(",") if t.strip()])
    if a.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return 1 if res["hard_fail"] else 0
    print("# Fact ledger: %s -> %s  (%d -> %d words)" % (os.path.basename(a.source), os.path.basename(a.draft),
                                                         res["words"]["source"], res["words"]["draft"]))
    print("verdict: %s" % ("FAIL (hard facts changed)" if res["hard_fail"] else "OK (no hard-fact changes)"))
    for k, lab in ((("numbers_missing", "brief numbers not used (fine in WRITE mode)") if a.write else
                    ("numbers_missing", "numbers MISSING from draft")), ("numbers_added", "numbers ADDED in draft")):
        if res[k]:
            print("- %s:" % lab)
            for num, (cnt, c) in res[k].items():
                print("    %s (x%d)  ...%s..." % (num, cnt, c.strip()))
                if k == "numbers_added" and num in res["numbers_added_far_match"]:
                    print("        (equals %s, but those numbers do not stand in the same paragraph: if it is a "
                          "calculation, state it where the reader can check it; otherwise remove the number)"
                          % res["numbers_added_far_match"][num])
    if res["numbers_derived"]:
        print("- numbers not in the source that are arithmetic on source numbers of the same paragraph "
              "(confirm each, and show it in the verification block):")
        for num, (formula, c) in res["numbers_derived"].items():
            print("    %s = %s  ...%s..." % (num, formula, c.strip()))
    for k, lab in (("citations_missing", "citations MISSING"), ("citations_added", "citations ADDED"),
                   ("protected_lost", "protected terms LOST"), ("entities_missing", "names/acronyms missing (review)"),
                   ("entities_added", "names/acronyms added (review: invented?)")):
        if res[k]:
            print("- %s: %s" % (lab, ", ".join(res[k][:40])))
    for k, lab in (("number_words_missing", "spelled-out numbers missing (review: rephrased range, or a lost fact?)"),
                   ("number_words_added", "spelled-out numbers added (review: counting word, or an invented fact?)")):
        if res[k]:
            print("- %s: %s" % (lab, "; ".join("%s ...%s..." % (n, c.strip()) for n, (_, c) in list(res[k].items())[:8])))
    if res["number_mentions_changed"]:
        print("- (info) sourced numbers mentioned a different number of times: " +
              ", ".join("%s %d->%d" % (k, a_, b_) for k, (a_, b_) in list(res["number_mentions_changed"].items())[:12]))
    print("- certainty: " + "; ".join("%s %s->%s per1k" % (k, v["source_per1k"], v["draft_per1k"]) for k, v in res["certainty"].items()))
    for w in res["warnings"]:
        print("  WARNING: " + w)
    return 1 if res["hard_fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
