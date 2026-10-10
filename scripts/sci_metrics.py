#!/usr/bin/env python3
"""SciHumanizer metrics: measure the statistical fingerprints of AI-typical prose.

Pure standard library (Python 3.8+). English and French.

  analyze   FILE [--register R] [--lang en|fr] [--target-words N | --min-words N | --max-words N]
            [--source FILE] [--waive D1,D2] [--protect "term a,term b"] [--sentences] [--all] [--json]
            Measure a text and score it against human bands for its register AND its length.
  compare   FILE --ref REF [--lang en|fr] [--json]
            Test whether FILE deviates from a human reference text (the writer's own prose).
  count     FILE [--target-words N] [--min-words N] [--max-words N]
            The one word count used by every script and every rule in the skill.
  growth    OLD NEW [--register R] [--source FILE]
            After lengthening a draft: did the added words bring new content, or only words?
  calibrate --human DIR --ai DIR --register NAME [--lang en|fr] [--out calibration.json]
            Build bands for a new register from your own folders of human and AI texts.
  selftest  Check the vocabulary formulas against simulation and the analyzer's invariants.

Registers shipped: scientific, abstract, general, for each calibrated language.
Exit code: 0 = passed (or report only), 1 = style gate, length check or growth check failed, 2 = usage error.
"""
import argparse
import bisect
import collections
import glob
import json
import math
import os
import re
import statistics
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lexstats  # noqa: E402
import textcore as T  # noqa: E402

CALIBRATION_PATH = os.path.join(T.DATA, "calibration.json")
MIN_WORDS_FOR_GATE = 150      # shortest calibrated length; below it the report is informational
LONG_DOC_FACTOR = 1.35        # beyond this multiple of the longest calibrated length, score in windows
RAREFY_N = 100                # sample size of the rarefied vocabulary measures (lemmas)
QS = (("p025", .025), ("p05", .05), ("p10", .10), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .90),
      ("p95", .95), ("p975", .975))
CONTENT_TAGS = {"NOUN", "PROPN", "ACRO", "VERB", "ADJ", "ADJC", "ADJS", "ADV", "ADVC"}
FUNCTION_TAGS = {"DET", "ADP", "PRON", "CCONJ", "SCONJ", "MODAL", "AUX", "TO", "PRT"}
LIST_CLASS = {"NOUN": "N", "PROPN": "N", "ACRO": "N", "NUM": "N", "ADJ": "A", "ADJC": "A", "ADJS": "A",
              "VERB": "V", "ADV": "R", "ADVC": "R"}
CLOSERS = "\"')”’»] "


# ------------------------------------------------------------------------------- helpers
def per_k(count, n, k=1000.0):
    return round(count * k / n, 3) if n else 0.0


def mean(xs):
    return statistics.mean(xs) if xs else 0.0


def sd(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def pct(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    pos = (len(xs) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _lookup(lp, name):
    obj = lp
    for part in name.split("."):
        obj = obj[part] if isinstance(obj, dict) else getattr(obj, part)
    return obj


_RX = {}


def phrase_rx(lp, name):
    """One alternation per phrase list, longest phrase first, so overlapping entries ("the fact that"
    inside "due to the fact that") are counted once. A phrase ending in an eliding word also matches
    its elided form (afin de -> afin d')."""
    key = (lp.__name__, name)
    if key not in _RX:
        fin = set(getattr(lp, "ELIDING_FINALS", ()))
        canon = set()
        for ph in _lookup(lp, name):
            ph = ph.strip().lower()
            if ph.endswith("'") and (ph[:-1] + "e").split()[-1] in fin:
                ph = ph[:-1] + "e"
            canon.add(ph)
        order = sorted(canon, key=lambda p: (-len(p), p))
        alts = []
        for ph in order:
            if ph.split()[-1] in fin:
                alts.append("(%s(?:e(?![\\w'])|'))" % re.escape(ph[:-1]))
            elif ph[-1].isalnum():
                alts.append("(%s(?![\\w']))" % re.escape(ph))
            else:
                alts.append("(%s)" % re.escape(ph))
        _RX[key] = (re.compile(r"(?<!\w)(?:%s)" % "|".join(alts)) if alts else None, order)
    return _RX[key]


def phrase_count(doc, name):
    rx, order = phrase_rx(doc.lp, name)
    c = collections.Counter()
    if rx:
        for m in rx.finditer(doc.norm_text):
            c[order[m.lastindex - 1]] += 1
    return c


_SETS = {}


def lemma_count(doc, name, tags=None):
    """Occurrences of the listed dictionary forms, matched on lemmas (studies = study). With `tags`,
    only tokens tagged as one of these classes count ('a need' but not 'it needs')."""
    lp = doc.lp
    key = (lp.__name__, name)
    if key not in _SETS:
        _SETS[key] = frozenset(w.lower() for w in _lookup(lp, name))
    want = _SETS[key]
    c = collections.Counter()
    for s in doc.all_sentences:
        for k, (tok, lem) in enumerate(zip(s["toks"], s["lemmas"])):
            if tags is not None and s["tags"][k] not in tags:
                continue
            hit = next((x for x in lp.lemma_candidates(tok, lem.lower()) if x in want), None)
            if hit is None:
                continue
            if hit in lp.CASE_SENSITIVE_WORDS and s["origs"][k][:1].isupper() and k > 0:
                continue        # "May 2019", "Will Smith"
            c[hit] += 1
    return c


def list_count(doc, name):
    """A {lemmas, phrases} list."""
    c = lemma_count(doc, name + ".lemmas")
    c.update(phrase_count(doc, name + ".phrases"))
    return c


def _stock_rx(lp):
    if not hasattr(lp, "_STOCK_RX"):
        lp._STOCK_RX = [(re.compile(p), label, src) for p, label, src in lp.STOCK_PATTERNS]
        lp._ECHO_RX = re.compile(lp.SIGNIFICANCE_ECHO)
        lp._PART_RX = re.compile(lp.PARTICIPIAL_CLAUSE)
        lp._EXPL_RX = re.compile(lp.EXPLETIVE_OPENER)
        lp._EXTRA_RX = re.compile(lp.EXTRAPOSITION)
        lp._DH_RX = [re.compile(p) for p in lp.DOUBLE_HEDGES]
        lp._OPENER_RX = [re.compile(p) for p in lp.STOCK_OPENERS]
        lp._ENDING_RX = re.compile(lp.FORMULAIC_ENDING)
        lp._CONN_INDEX = sorted(((ph, cls) for cls, phs in lp.CONNECTIVES.items() for ph in phs), key=lambda x: -len(x[0]))
    return lp


def starts_with(low, phrase):
    if not low.startswith(phrase):
        return False
    rest = low[len(phrase):]
    return not rest or not phrase[-1].isalnum() or not (rest[0].isalnum() or rest[0] == "'")


# ------------------------------------------------------------------------------- metric groups
def m_rhythm(doc):
    lens = [s["n"] for s in doc.sentences]
    n = len(lens)
    out = {"sentences": n}
    if n == 0:
        return out
    mu, sg = mean(lens), sd(lens)
    out.update({
        "sent_len_mean": round(mu, 2), "sent_len_sd": round(sg, 2),
        "sent_len_cv": round(sg / mu, 3) if mu else 0.0,
        "sent_len_median": pct(lens, 0.5), "sent_len_min": min(lens), "sent_len_max": max(lens),
        "short_share": round(sum(l <= 10 for l in lens) / n, 3),
        "long_share": round(sum(l >= 30 for l in lens) / n, 3),
        "masd_norm": round(mean([abs(a - b) for a, b in zip(lens, lens[1:])]) / mu, 3) if n > 1 and mu else None,
    })
    tol = max(4, round(0.25 * mu))
    best, best_at = 1, 0
    for i in range(n):
        lo = hi = lens[i]
        j = i
        while j + 1 < n and max(hi, lens[j + 1]) - min(lo, lens[j + 1]) <= tol:
            j += 1
            lo, hi = min(lo, lens[j]), max(hi, lens[j])
        if j - i + 1 > best:
            best, best_at = j - i + 1, i
    out["uniform_run_max"] = best
    out["uniform_run_share"] = round(best / n, 3)
    out["uniform_run_at"] = [best_at + 1, best_at + best] if best > 1 else None
    out["uniform_run_tolerance"] = tol
    return out


def m_paragraphs(doc):
    wl = [sum(s["n"] for s in p) for p in doc.paragraphs]
    sl = [len(p) for p in doc.paragraphs]
    out = {"paragraphs": len(wl)}
    if len(wl) >= 3:
        out.update({
            "para_words_mean": round(mean(wl), 1), "para_words_cv": round(sd(wl) / mean(wl), 3),
            "para_sents_mean": round(mean(sl), 2), "para_sents_cv": round(sd(sl) / mean(sl), 3) if mean(sl) else 0.0,
            "single_sentence_para_share": round(sum(x == 1 for x in sl) / len(sl), 3),
        })
    return out


def _rare(seq, n):
    r = lexstats.rarefied_types(lexstats.spectrum(seq), len(seq), n) if len(seq) >= n else None
    return round(r / n, 4) if r else None


def m_lexical(doc, protect=()):
    """Vocabulary, measured on lemmas at fixed sample sizes (mathematics in lexstats.py)."""
    lp = doc.lp
    lem = doc.lex_lemmas()
    n = len(lem)
    out = {"lemma_tokens": n}
    if n == 0:
        return out
    prof = lexstats.profile(lem, n=RAREFY_N, w=50)
    out.update({
        "types_at_100": prof["types_at_%d" % RAREFY_N], "hapax_at_100": prof["hapax_at_%d" % RAREFY_N],
        "mattr50": prof["mattr50"], "mtld_wrap": prof["mtld_wrap"], "dispersion50": prof["dispersion50"],
        "yule_k": prof["yule_k"], "ttr_raw": round(prof["types"] / n, 3),
    })
    pairs = [(l.lower(), t, g) for s in doc.all_sentences for l, t, g in zip(s["lemmas"], s["toks"], s["tags"])
             if l and l[0].isalpha() and g != "NUM"]
    # function-word variety is lower in AI text even where overall variety is higher (survey: Zindela; Andre)
    out["fw_types_at_50"] = _rare([l for l, t, g in pairs if g in FUNCTION_TAGS], 50)
    cw = [l for l, t, g in pairs if g in CONTENT_TAGS]
    out["content_types_at_50"] = _rare(cw, 50)
    cm = lexstats.mattr(cw, 25)
    out["content_mattr25"] = round(cm, 4) if cm is not None else None
    # grammatical glue: the handful of most frequent grammatical words (the / of / in / be ...)
    glue = set(lp.GLUE_LEMMAS)
    out["glue_per100"] = round(100.0 * sum(1 for l, t, g in pairs if l in glue) / len(pairs), 2) if pairs else 0.0
    gc = collections.Counter(l for l, t, g in pairs if l in glue)
    out["glue_counts"] = {w: gc[w] for w in lp.GLUE_LEMMAS}
    out["glue_base"] = len(pairs)
    # words outside the general lexicon: technical and field-specific vocabulary (names are counted
    # under specificity). Same idea as MAGE's corpus-level rarity feature, with a fixed reference list.
    known = T.tagger(doc.lang).known
    low = [(t, g) for l, t, g in pairs if g not in ("PROPN", "ACRO") and t not in lp.CLITIC_TAGS]
    out["rare_word_pct"] = round(100.0 * sum(1 for t, g in low if t not in known) / len(low), 2) if low else 0.0
    chars = [len(t) for l, t, g in pairs if t not in lp.CLITIC_TAGS]
    out["word_len_mean"] = round(mean(chars), 3) if chars else 0.0
    out["long_word_pct"] = round(100.0 * sum(c >= 9 for c in chars) / len(chars), 2) if chars else 0.0
    raw = doc.all_text.encode("utf-8")
    out["compress_ratio"] = round(len(zlib.compress(raw, 9)) / len(raw), 4) if len(raw) > 400 else None
    # repetition (terminology the writer protects is ignored)
    prot = {p.lower() for p in protect}
    content = [l for l in cw if l not in lp.STOPWORDS and len(l) > 3 and l not in prot]
    out["top_content_words"] = [[k, v] for k, v in collections.Counter(content).most_common(10)]
    for nn in (3, 4):
        g = collections.Counter()
        for s in doc.all_sentences:
            lw = s["toks"]
            for i in range(len(lw) - nn + 1):
                gram = tuple(lw[i:i + nn])
                if all(x in lp.STOPWORDS for x in gram) or any(x[0].isdigit() for x in gram):
                    continue
                j = " ".join(gram)
                if any(j in p or p in j for p in prot):
                    continue
                g[gram] += 1
        rep = {k: v for k, v in g.items() if v >= 2}
        out["repeated_%dgram_per1k" % nn] = per_k(sum(v - 1 for v in rep.values()), doc.n_words)
        if nn == 3:
            out["top_repeated_3grams"] = [[" ".join(k), v] for k, v in sorted(rep.items(), key=lambda x: -x[1])[:8]]
    frames = collections.Counter(" ".join(s["toks"][:2]) for s in doc.sentences if len(s["toks"]) >= 3)
    rf = {k: v for k, v in frames.items() if v >= 2 and not all(x in lp.STOPWORDS for x in k.split())}
    out["repeated_frames"] = [[k, v] for k, v in sorted(rf.items(), key=lambda x: -x[1])[:6]]
    out["repeated_frame_share"] = round(sum(rf.values()) / len(doc.sentences), 3) if doc.sentences else 0.0
    return out


def m_pos(doc):
    """Part-of-speech shares are percentages of linguistic tokens; per-1k rates are per 1,000 words."""
    lp = doc.lp
    nt = doc.n_tokens or 1
    n = doc.n_words or 1
    c = collections.Counter(doc.tags)
    rate = lambda *ks: round(100.0 * sum(c[k] for k in ks) / nt, 2)  # noqa: E731
    toks = doc.toks
    modal = c["MODAL"] + sum(1 for l in doc.lemmas if l in lp.MODAL_LEMMAS)
    deriv = sum(1 for t, g in zip(toks, doc.tags) if lp.is_derived_adverb(t, g))
    verbs = c["VERB"]
    return {
        "noun_pct": rate("NOUN"), "propn_pct": rate("PROPN"), "acronym_pct": rate("ACRO"),
        "verb_pct": rate("VERB"), "aux_pct": rate("AUX"), "modal_pct": round(100.0 * modal / nt, 2),
        "adj_pct": rate("ADJ", "ADJC", "ADJS"), "adv_pct": rate("ADV", "ADVC"),
        "deriv_adv_pct": round(100.0 * deriv / nt, 2),
        "pron_pct": rate("PRON"), "det_pct": rate("DET"), "adp_pct": rate("ADP"),
        "cconj_pct": rate("CCONJ"), "sconj_pct": rate("SCONJ"), "num_pct": rate("NUM"),
        "noun_verb_ratio": round(c["NOUN"] / verbs, 3) if verbs else None,
        "nominal_verbal_ratio": round((c["NOUN"] + c["ADJ"] + c["ADP"] + c["DET"]) /
                                      max(1, c["VERB"] + c["ADV"] + c["PRON"] + c["AUX"] + c["MODAL"]), 3),
        "lexical_density": round(sum(c[k] for k in CONTENT_TAGS) / nt, 3),
        "comparative_per1k": per_k(c["ADJC"] + c["ADJS"] + c["ADVC"] + sum(1 for t in toks if t in lp.DEGREE_WORDS), n),
        "specificity_pct": rate("PROPN", "ACRO", "NUM"),
        "first_person_per1k": per_k(sum(1 for w in toks if w in lp.FIRST_PERSON), n),
        "second_person_per1k": per_k(sum(1 for w in toks if w in lp.SECOND_PERSON), n),
        "pronoun_per1k": per_k(sum(1 for w in toks if w in lp.FIRST_PERSON | lp.SECOND_PERSON | lp.THIRD_PERSON), n),
        "of_per100": round(100.0 * toks.count(lp.OF_WORD) / n, 2),
    }


def _nominals(s, lp):
    return [t for t, l, g in zip(s["toks"], s["lemmas"], s["tags"]) if lp.is_nominalization(t, l, g)]


def m_nominal(doc):
    lp = doc.lp
    total, per_sent = 0, []
    for s in doc.all_sentences:
        k = _nominals(s, lp)
        total += len(k)
        if len(k) >= 3 and "i" in s:
            per_sent.append([s["i"], len(k), k[:6]])
    return {"nominalization_per1k": per_k(total, doc.n_words),
            "nominal_heavy_sentences": per_sent[:12],
            "nominal_heavy_share": round(len(per_sent) / len(doc.sentences), 3) if doc.sentences else 0.0}


def m_function_words(doc):
    lp = doc.lp
    c = collections.Counter(doc.toks)
    n = doc.n_words or 1
    ai = sum(c[w] for w in lp.AI_FAVORED_FW)
    hu = sum(c[w] for w in lp.HUMAN_FAVORED_FW)
    return {"ai_fw_per1k": per_k(ai, n), "human_fw_per1k": per_k(hu, n),
            "fw_ratio": round(hu / ai, 3) if ai else None,
            "ai_fw_detail": {w: per_k(c[w], n) for w in lp.AI_FAVORED_FW},
            "human_fw_detail": {w: per_k(c[w], n) for w in lp.HUMAN_FAVORED_FW if c[w]}}


def initial_connective(s, lp):
    """Sentence-initial conjunctive adverb or linking phrase (Furthermore / De plus / In conclusion).
    Subordinators and coordinators are not counted here: they open clauses and count as varied openers."""
    low = s["norm"].lstrip("\"'“«(-–— ")
    for ph, cls in _stock_rx(lp)._CONN_INDEX:
        if ph in lp.NOT_ADVERBIAL:
            continue
        if starts_with(low, ph):
            if ph in lp.NEED_COMMA and not low.startswith(ph + ","):
                continue
            return ph, cls
    return None, None


def m_connectives(doc):
    lp = doc.lp
    init, cls_init, listing = collections.Counter(), collections.Counter(), []
    for s in doc.sentences:
        ph, cls = initial_connective(s, lp)
        if ph:
            init[ph] += 1
            cls_init[cls] += 1
            if cls in lp.FORMULAIC_CONNECTIVE_CLASSES:
                listing.append([s["i"], ph])
    n = len(doc.sentences) or 1
    by_cls = collections.Counter()
    for ph, k in phrase_count(doc, "UNAMBIGUOUS_CONNECTIVES").items():
        for cls, phs in lp.CONNECTIVES.items():
            if ph in phs:
                by_cls[cls] += k
                break
    tot = sum(by_cls.values())
    return {
        "connective_initial_share": round(sum(init.values()) / n, 3),
        "formulaic_initial_share": round(sum(cls_init[c] for c in lp.FORMULAIC_CONNECTIVE_CLASSES) / n, 3),
        "logical_connective_share": round(sum(by_cls[c] for c in lp.LOGICAL_CONNECTIVE_CLASSES) / tot, 3) if tot else None,
        "connective_type_diversity": round(len(init) / sum(init.values()), 3) if init else None,
        "connectives_per1k": per_k(tot, doc.n_words),
        "initial_connectives": dict(init.most_common()),
        "formulaic_initial_sentences": listing[:15],
    }


def m_stance(doc):
    lp = doc.lp
    n = doc.n_words or 1
    h, b, a = list_count(doc, "HEDGES"), list_count(doc, "BOOSTERS"), list_count(doc, "ATTITUDE")
    self_m = sum(1 for w in doc.toks if w in lp.FIRST_PERSON)
    questions = sum(1 for s in doc.sentences if s["text"].rstrip(CLOSERS).endswith("?"))
    return {
        "hedges_per1k": per_k(sum(h.values()), n), "boosters_per1k": per_k(sum(b.values()), n),
        "attitude_per1k": per_k(sum(a.values()), n), "self_mention_per1k": per_k(self_m, n),
        "stance_per1k": per_k(sum(h.values()) + sum(b.values()) + sum(a.values()) + self_m, n),
        "question_share": round(questions / len(doc.sentences), 3) if doc.sentences else 0.0,
        "top_hedges": dict(h.most_common(6)), "top_attitude": dict(a.most_common(6)),
    }


def m_sentiment(doc):
    crit, promo = lemma_count(doc, "CRITICAL_LEMMAS"), lemma_count(doc, "PROMO_LEMMAS")
    c, p = sum(crit.values()), sum(promo.values())
    return {"critical_per1k": per_k(c, doc.n_words), "promo_per1k": per_k(p, doc.n_words),
            "positivity_skew": round(p / (p + c), 3) if (p + c) else None,
            "top_promo": [[w, k] for w, k in promo.most_common(8)]}


def _marks(t, sentences):
    return {
        "comma": t.count(","), "period": sum(1 for s in sentences if s["text"].rstrip(CLOSERS).endswith(".")),
        "semicolon": t.count(";"), "colon": len(re.findall(r":(?!\d)", t)), "question": t.count("?"),
        "exclamation": t.count("!"), "parenthesis": t.count("("),
        "quote": (t.count('"') + t.count("“") + t.count("”")) // 2 + t.count("«"),
        "dash": t.count("—") + len(re.findall(r"\s--\s|\s–\s", t)),
    }


def m_punctuation(doc):
    t = doc.all_text
    n = doc.n_words or 1
    marks = _marks(t, doc.all_sentences)
    nodash = {k: v for k, v in marks.items() if k != "dash"}
    tot = sum(nodash.values()) or 1
    ent = -sum((v / tot) * math.log2(v / tot) for v in nodash.values() if v)
    return {
        "per1k": {k: per_k(v, n) for k, v in marks.items()},
        "punct_entropy_nodash": round(ent / math.log2(len(nodash)), 3),
        "nonbasic_share_nodash": round((tot - nodash["comma"] - nodash["period"]) / tot, 3),
        "em_dash_per1k": per_k(marks["dash"], n),
        "contraction_per1k": per_k(len(re.findall(r"[A-Za-z](?:n['’]t|['’](?:re|ve|ll|d|m))\b", t)), n) if doc.lang == "en" else 0.0,
        "comma_per_sentence": round(marks["comma"] / max(1, len(doc.all_sentences)), 2),
    }


_LIST_RE = re.compile(r"(?:^|[\s(«“\"])((?:[\w'’-]+ ){0,3}[\w'’-]+), ((?:[\w'’-]+ ){0,3}[\w'’-]+)"
                      r"(?:, (?:[\w'’-]+ ){0,3}[\w'’-]+)*,? (?:and|or|et|ou) ((?:[\w'’-]+ ){0,3}[\w'’-]+)")
_PAIR_RE = re.compile(r"(?<![,;] )(?<![\w'’-])([^\W\d_]{4,}) (and|or|et|ou) ([^\W\d_]{4,})(?![\w'’-])")


def _klass(word, tg):
    tags = tg.analyse(word)[1]
    return LIST_CLASS.get(tags[-1]) if tags else None


def count_lists(s, tg):
    """Coordinated lists of >= 3 parallel items, with or without the serial comma."""
    k = 0
    for m in _LIST_RE.finditer(s["text"]):
        c1, c2 = _klass(m.group(1).split()[-1], tg), _klass(m.group(2).split()[-1], tg)
        if not c1 or c1 != c2:
            continue
        if any(_klass(w, tg) == c1 for w in m.group(3).split()):
            k += 1
    return k


def m_stock(doc):
    lp = _stock_rx(doc.lp)
    tg = T.tagger(doc.lang)
    hits, where, by_src = collections.Counter(), [], collections.Counter()
    for rx, label, src in lp._STOCK_RX:
        for s in doc.all_sentences:
            k = len(rx.findall(s["norm"]))
            if k:
                hits[label] += k
                by_src[src] += k
                if len(where) < 25:
                    where.append([s.get("i"), label])
    vocab = lemma_count(doc, "AI_VOCAB_LEMMAS")
    echo = [s["i"] for s in doc.sentences if lp._ECHO_RX.search(s["norm"])]
    n = doc.n_words or 1
    return {
        "ai_vocab_per1k": per_k(sum(vocab.values()), n), "ai_vocab_hits": dict(vocab.most_common(12)),
        "stock_per1k": per_k(sum(hits.values()), n),
        "stock_research_per1k": per_k(by_src["R"], n), "stock_practitioner_per1k": per_k(by_src["P"], n),
        "stock_hits": dict(hits.most_common()), "stock_where": where,
        "significance_echo_sentences": echo, "significance_echo_per1k": per_k(len(echo), n),
        "extraposition_per1k": per_k(len(lp._EXTRA_RX.findall(doc.norm_text)), n),
        "triad_lists_per1k": per_k(sum(count_lists(s, tg) for s in doc.all_sentences), n),
    }


def m_markers(doc):
    """Calibrated marker words (data/markers_<lang>.json): what current models over-use and what they
    avoid, measured against human text on the same topics. Empty lists give zero rates."""
    lp = doc.lp
    n = doc.n_words or 1
    fw, hf = set(lp.MARKER_AI_FUNCTION), set(lp.MARKER_HUMAN_FUNCTION)
    fwc = collections.Counter(l.lower() for l in doc.lemmas if l.lower() in fw)
    hfc = sum(1 for l in doc.lemmas if l.lower() in hf)
    aic = lemma_count(doc, "MARKER_AI_CONTENT")
    huc = lemma_count(doc, "MARKER_HUMAN_CONTENT")
    return {"ai_function_per1k": per_k(sum(fwc.values()), n), "ai_content_per1k": per_k(sum(aic.values()), n),
            "human_function_per1k": per_k(hfc, n), "plain_per1k": per_k(sum(huc.values()), n),
            "ai_function_hits": dict(fwc.most_common(12)), "ai_content_hits": dict(aic.most_common(14))}


def content_types(doc):
    return {l.lower() for l, g in zip(doc.lemmas, doc.tags) if g in CONTENT_TAGS and l and l[0].isalpha()}


def fact_types(doc):
    """Distinct numbers, names and acronyms: the verifiable specifics of a text."""
    return {(t if g == "NUM" else l.lower()) for t, l, g in zip(doc.toks, doc.lemmas, doc.tags) if g in ("NUM", "PROPN", "ACRO")}


def _content_set(s, lp):
    return {l.lower() for l, t in zip(s["lemmas"], s["tags"])
            if t in ("NOUN", "PROPN", "ACRO", "VERB", "ADJ", "NUM") and l.lower() not in lp.STOPWORDS and len(l) > 2}


def m_padding(doc):
    """Words that add length without adding information. What a word list can find is counted here;
    padding that paraphrases needs the deletion test in SKILL.md, and this returns its candidates."""
    lp = _stock_rx(doc.lp)
    tg = T.tagger(doc.lang)
    n = doc.n_words or 1
    ns = len(doc.sentences) or 1
    wordy, meta = phrase_count(doc, "WORDY"), phrase_count(doc, "METADISCOURSE")
    shell = lemma_count(doc, "SHELL_NOUNS", tags=("NOUN",))
    dh = sum(len(rx.findall(doc.norm_text)) for rx in lp._DH_RX)
    # doublets: two words of one class joined by and/or outside a longer list ("robust and reliable")
    bino = []
    for s in doc.all_sentences:
        toks, tags = s["toks"], s["tags"]
        for m in _PAIR_RE.finditer(s["norm"]):
            a, cj, b = m.group(1), m.group(2), m.group(3)
            if a in lp.STOPWORDS or b in lp.STOPWORDS:
                continue
            # word classes as tagged in the sentence; out of context only if the pair cannot be located
            at = next((i for i in range(len(toks) - 2) if toks[i] == a and toks[i + 1] == cj and toks[i + 2] == b), None)
            ca, cb = (LIST_CLASS.get(tags[at]), LIST_CLASS.get(tags[at + 2])) if at is not None else (_klass(a, tg), _klass(b, tg))
            if ca and ca == cb:
                bino.append("%s %s %s" % (a, cj, b))
    # comment clause tacked on after a comma with a present participle
    part = []
    for s in doc.all_sentences:
        for m in lp._PART_RX.finditer(s["norm"]):
            w = m.group(1)
            if w not in lp.PARTICIPIAL_EXCLUDE and (tg.lex.get(w) or [("VERB", None)])[0][0] == "VERB":
                part.append([s.get("i"), w])
    expl = sum(1 for s in doc.sentences if lp._EXPL_RX.search(s["norm"].lstrip("\"'“«( ")))
    # restatement: most content words of a sentence already stood together in one earlier sentence
    sets = [_content_set(s, lp) for s in doc.sentences]
    restate = []
    for j in range(1, len(sets)):
        cj = sets[j]
        if len(cj) < 5:
            continue
        if any(len(sets[i]) >= 5 and len(cj & sets[i]) >= 0.6 * len(cj) for i in range(j)):
            restate.append(doc.sentences[j]["i"])
    over = None
    if len(doc.paragraphs) >= 4:
        first = set().union(*[_content_set(s, lp) for s in doc.paragraphs[0]])
        last = set().union(*[_content_set(s, lp) for s in doc.paragraphs[-1]])
        over = round(len(first & last) / len(last), 3) if last else None
    return {
        "wordy_per1k": per_k(sum(wordy.values()), n), "metadiscourse_per1k": per_k(sum(meta.values()), n),
        "shell_noun_per1k": per_k(sum(shell.values()), n), "double_hedge_per1k": per_k(dh, n),
        "binomial_per1k": per_k(len(bino), n), "participial_clause_per1k": per_k(len(part), n),
        "expletive_opener_share": round(expl / ns, 3), "restatement_share": round(len(restate) / ns, 3),
        "intro_outro_overlap": over,
        "wordy_hits": dict(wordy.most_common(10)), "metadiscourse_hits": dict(meta.most_common(8)),
        "shell_hits": dict(shell.most_common(10)), "binomial_examples": bino[:8],
        "participial_clauses": part[:12], "restating_sentences": restate[:12],
    }


def _opener_class(s, lp):
    ph, _ = initial_connective(s, lp)
    if ph:
        return "connective"
    lw, tags = s["toks"], s["tags"]
    if not lw:
        return "other"
    low = s["norm"].lstrip("\"'“«(-–— ")
    w0, t0 = lw[0], tags[0]
    hint = lp.opener_hint(low, lw, tags)
    if hint:
        return hint
    if w0 in lp.COORDINATORS:
        return "coordinator"
    if w0 in lp.SUBORDINATORS or t0 == "SCONJ" or any(starts_with(low, p) for p in lp.SUBORD_PHRASES):
        return "subordinate"
    if w0 in lp.PREPOSITIONS or t0 in ("ADP", "TO"):
        return "prepositional"
    if t0 in ("ADV", "ADVC"):
        return "adverbial"
    if t0 == "VERB" and re.search(lp.PARTICIPLE_FORM, w0):
        return "participial"
    if t0 == "VERB":
        return "verb-initial"
    return "subject"


def m_structure(doc):
    lp = doc.lp
    n = len(doc.sentences) or 1
    classes = collections.Counter(_opener_class(s, lp) for s in doc.sentences)
    first = collections.Counter(s["toks"][0] for s in doc.sentences if s["toks"])
    skel = collections.Counter()
    for s in doc.sentences:
        ph, _ = initial_connective(s, lp)
        skel[" ".join((["CONN"] if ph else []) + s["tags"][len(ph.split()) if ph else 0:][:3])] += 1
    ent = -sum((v / n) * math.log2(v / n) for v in skel.values()) if doc.sentences else 0.0
    passive = [s["i"] for s in doc.sentences if lp.passive(s["toks"], s["tags"])]
    return {
        "opener_classes": {k: round(v / n, 3) for k, v in classes.most_common()},
        "subject_initial_share": round(classes["subject"] / n, 3),
        "varied_opener_share": round((classes["subordinate"] + classes["prepositional"] + classes["adverbial"] +
                                      classes["participial"] + classes["coordinator"]) / n, 3),
        "top_first_words": [[k, v] for k, v in first.most_common(5)],
        "top_first_word_share": round(first.most_common(1)[0][1] / n, 3) if first else 0.0,
        "skeleton_entropy": round(ent / math.log2(n), 3) if n > 1 else None,
        "passive_sentence_share": round(len(passive) / n, 3),
        "passive_sentences": passive[:20],
    }


def m_document(doc):
    lp = _stock_rx(doc.lp)
    out = {}
    if not doc.sentences:
        return out
    first = doc.sentences[0]["norm"].lstrip("\"'“«( ")
    out["stock_opener"] = any(rx.search(first) for rx in lp._OPENER_RX)
    last_par = " ".join(s["norm"] for s in doc.paragraphs[-1])
    _, cls = initial_connective(doc.paragraphs[-1][0], lp)
    out["formulaic_ending"] = bool(lp._ENDING_RX.search(last_par)) or cls == "summarizing"
    wraps = 0
    for par in doc.paragraphs:
        if len(par) < 3:
            continue
        _, c2 = initial_connective(par[-1], lp)
        if c2 == "summarizing" or lp._ECHO_RX.search(par[-1]["norm"]):
            wraps += 1
    multi = sum(1 for p in doc.paragraphs if len(p) >= 3)
    out["paragraph_wrapup_share"] = round(wraps / multi, 3) if multi else 0.0
    return out


def m_format(doc):
    n = doc.n_words or 1
    f = doc.fmt
    typo = []
    for pat, label in getattr(doc.lp, "TYPOGRAPHY", ()):
        k = len(re.findall(pat, doc.all_text))
        if k:
            typo.append([label, k])
    return {"bold_per1k": per_k(f["bold"], n), "headings": f["headings"],
            "title_case_headings": f["title_case_headings"], "list_items": f["list_items"],
            "bold_lead_items": f["bold_lead_items"], "emoji": f["emoji"],
            "list_word_share": round(sum(s["n"] for s in doc.list_sentences) / n, 3), "typography": typo}


def m_pointers(doc):
    """Sentence- and word-level pointers for revision (not scored)."""
    lp = doc.lp
    longs = sorted(((s["n"], s["text"].count(","), s["i"]) for s in doc.sentences
                    if s["n"] >= 35 or s["text"].count(",") >= 4), reverse=True)[:8]
    adv = collections.Counter(t for s in doc.all_sentences for t, g in zip(s["toks"], s["tags"]) if lp.is_derived_adverb(t, g))
    adj = collections.Counter(l.lower() for s in doc.all_sentences for l, g in zip(s["lemmas"], s["tags"])
                              if g in ("ADJ", "ADJC", "ADJS") and len(l) > 3)
    tags = collections.Counter(doc.tags)
    mk = _marks(doc.all_text, doc.all_sentences)
    # compressed sentences: long enough to judge, with fewer than half the usual share of glue words
    glue = set(lp.GLUE_LEMMAS)
    tight = []
    for s in doc.sentences:
        nt = len(s["toks"])
        k = sum(1 for l in s["lemmas"] if l.lower() in glue)
        if nt >= 14 and 100.0 * k / nt < 0.5 * lp.GLUE_REFERENCE:
            tight.append([100.0 * k / nt, s["i"], k, nt])
    return {"long_sentences": [[i, w, c] for w, c, i in longs],
            "compressed_sentences": [[i, k, nt] for _, i, k, nt in sorted(tight)[:8]],
            "top_derived_adverbs": [[k, v] for k, v in adv.most_common(10)],
            "top_adjectives": [[k, v] for k, v in adj.most_common(10)],
            "counts": {"proper_nouns": tags["PROPN"], "acronyms": tags["ACRO"], "numbers": tags["NUM"],
                       "parentheses": mk["parenthesis"], "semicolons": mk["semicolon"], "colons": mk["colon"],
                       "questions": mk["question"], "dashes": mk["dash"]}}


def metrics_of(doc, protect=()):
    return {"lang": doc.lang, "words": doc.n_words, "tokens": doc.n_tokens, "count": doc.count,
            "rhythm": m_rhythm(doc), "paragraphs": m_paragraphs(doc),
            "lexical": m_lexical(doc, protect), "pos": m_pos(doc), "nominal": m_nominal(doc),
            "function_words": m_function_words(doc), "connectives": m_connectives(doc),
            "stance": m_stance(doc), "sentiment": m_sentiment(doc), "punctuation": m_punctuation(doc),
            "stock": m_stock(doc), "markers": m_markers(doc), "padding": m_padding(doc), "structure": m_structure(doc),
            "document": m_document(doc), "format": m_format(doc), "pointers": m_pointers(doc)}


def analyze_text(text, protect=(), lang=None):
    doc = T.Doc(text, lang)
    return doc, metrics_of(doc, protect)


def getpath(m, path):
    if path in m:                      # flat rows (calibration)
        return m[path]
    cur = m
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


# ------------------------------------------------------------------------------- scoring
def load_calibration(path=CALIBRATION_PATH):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            calib = json.load(fh)
        if calib.get("version") == 3:
            return calib
        sys.stderr.write("calibration file %s has an older format (version %s); it is ignored\n" % (path, calib.get("version")))
    return None


def register_key(calib, register, lang):
    regs = (calib or {}).get("registers", {})
    for k in ("%s.%s" % (lang, register), register):
        if k in regs:
            return k
    return None


def interp(table, n_words):
    """Calibration values are stored per text length. Interpolate linearly between the two nearest
    calibrated lengths; outside the calibrated range use the nearest one."""
    ls = sorted(int(k) for k in table)
    if n_words <= ls[0]:
        return table[str(ls[0])]
    if n_words >= ls[-1]:
        return table[str(ls[-1])]
    hi = bisect.bisect_right(ls, n_words)
    lo, hi = ls[hi - 1], ls[hi]
    t = (n_words - lo) / float(hi - lo)
    a, b = table[str(lo)], table[str(hi)]
    if isinstance(a, dict):
        return {k: a[k] + t * (b[k] - a[k]) for k in a if k in b and is_num(a[k]) and is_num(b[k])}
    return a + t * (b - a)


def side_scale(h, side, min_scale):
    """Spread of the human values on one side of their median, as a standard-deviation equivalent.
    Uses the first quantile on that side that differs from the median (count metrics are zero for
    most human texts, so the quartile is often degenerate)."""
    pairs = (("p75", 0.6745), ("p90", 1.2816), ("p975", 1.9600)) if side > 0 else \
            (("p25", 0.6745), ("p10", 1.2816), ("p025", 1.9600))
    for q, z in pairs:
        sc = abs(h[q] - h["p50"]) / z
        if sc > 0:
            return max(sc, min_scale)
    return max(min_scale, 1e-9)


def metric_z(x, h, d, min_scale):
    """Distance from the human median toward the AI side, in human standard deviations, clipped to
    [0, 4]. d = +1: AI runs higher; -1: lower; 0: different models err on different sides, so both count."""
    dev = x - h["p50"]
    side = (1 if dev >= 0 else -1) if d == 0 else d
    if dev * side <= 0:
        return 0.0
    return min(abs(dev) / side_scale(h, side, min_scale), 4.0)


def profile_weights(human_z, ai_z):
    """Weights of one AI profile: for each dimension, how far that model's texts sit above human
    texts on the dimension score, divided by the score's variance (a diagonal linear discriminant).
    human_z, ai_z: {dimension: [scores]}. Dimensions on which the model does not deviate get 0."""
    w = {}
    for g, hv in human_z.items():
        av = ai_z.get(g) or []
        if len(hv) < 2 or len(av) < 2:
            continue
        shift = mean(av) - mean(hv)
        var = (statistics.pvariance(hv) + statistics.pvariance(av)) / 2.0
        w[g] = max(0.0, shift) / max(var, 0.05)
    tot = sum(w.values())
    return {g: round(x / tot, 4) for g, x in w.items() if x > 0} if tot > 0 else {}


def composite_of(gz, reg):
    """Composite of the dimension scores gz = {dimension: z}. With AI profiles in the calibration:
    for each profile, the weighted mean of the dimension scores; the largest one counts (how far the
    text leans toward the nearest known AI profile). Without profiles: root-mean-square."""
    profiles = reg.get("profiles")
    if not gz:
        return 0.0, None, {}
    if not profiles:
        return math.sqrt(sum(z * z for z in gz.values()) / len(gz)), None, {}
    best = None
    for tier, w in profiles.items():
        sw = sum(w.get(g, 0.0) for g in gz)
        if sw <= 0:
            continue
        val = sum(w.get(g, 0.0) * z for g, z in gz.items()) / sw
        if best is None or val > best[0]:
            best = (val, tier, {g: w.get(g, 0.0) * z / sw for g, z in gz.items()})
    return best if best else (0.0, None, {})


def evaluate(m, calib, register, waive=(), n_words=None, lang=None):
    """Score one text against the human bands of a register at the text's own length.

    Per metric   one-sided z = d * (x - p50) / scale, clipped to [0, 4]; p50 and scale come from HUMAN
                 texts cut to the same length; d = +1 when AI text runs higher, -1 when lower.
    Dimension    mean z of its metrics; PASS / WARN / FAIL against the distribution of that same score
                 in human texts (<= p75 / <= p90 / above): one calibrated verdict per dimension.
    Gate 1       composite <= the human 90th percentile. The composite is, for each calibrated AI
                 profile, the weighted mean of the dimension scores (weights: how strongly that
                 model deviates from human text on each dimension); the largest profile value counts.
    Gate 2       classic guards: research-documented tells beyond the extreme human range (p97.5 or
                 p2.5); at most `max_classic_violations` of them.
    Gate 3       over-correction: the same dimension scores measured on the far side of the human
                 median (root-mean-square over dimensions) must stay within the 99th percentile of
                 human texts, so a text cannot pass by overshooting human writing. Metrics whose far
                 side is harmless (less filler, fewer stock phrases, more names and numbers) carry
                 "far_side": false in the calibration and are left out.
    The z-scores only rank texts; the error rates of the gate are measured on held-out texts, not
    derived from a normality assumption (references/calibration.md)."""
    lang = lang or m.get("lang") or "en"
    key = register_key(calib, register, lang)
    if key is None:
        return None
    reg = calib["registers"][key]
    n = n_words if n_words is not None else m.get("words", 0)
    waive = set(waive or ())
    rows, groups, viol, rgroups = [], collections.defaultdict(list), [], collections.defaultdict(list)
    for mkey, spec in reg["metrics"].items():
        x = getpath(m, mkey)
        if not is_num(x):
            continue
        h = interp(spec["bands"], n)
        d = spec["ai_direction"]
        if spec.get("classic"):
            hi = max(h["p975"], spec.get("min_violation", 0.0))
            if spec.get("guard") == "ceiling" and x > hi and (hi > h["p50"] or spec.get("min_violation")):
                viol.append(mkey)
            elif spec.get("guard") == "floor" and x < h["p025"] and h["p025"] < h["p50"]:
                viol.append(mkey)
        if not spec.get("gate"):
            continue
        z = metric_z(x, h, d, spec.get("min_scale", 1e-6))
        g = spec.get("group", mkey)
        far = spec.get("far_side", True)
        if g not in waive:
            groups[g].append(z)
            if d != 0 and far:               # distance on the far side of the human median
                rgroups[g].append(metric_z(x, h, -d, spec.get("min_scale", 1e-6)))
        if d < 0:
            status = "PASS" if x >= h["p25"] else ("WARN" if x >= h["p10"] else "FAIL")
            if far and x > h["p975"] > h["p50"]:
                status = "OVER"
        elif d > 0:
            status = "PASS" if x <= h["p75"] else ("WARN" if x <= h["p90"] else "FAIL")
            if far and x < h["p025"] < h["p50"]:
                status = "OVER"
        else:
            status = "PASS" if h["p10"] <= x <= h["p90"] else ("WARN" if h["p025"] <= x <= h["p975"] else "FAIL")
        ai = {k: round(interp(v, n), 4) for k, v in (spec.get("ai_p50") or {}).items() if v}
        rows.append({"metric": mkey, "value": x, "status": status, "z": round(z, 2), "group": g,
                     "direction": {1: "AI higher", -1: "AI lower", 0: "AI off on both sides"}[d],
                     "human_p10_p50_p90": [round(h["p10"], 4), round(h["p50"], 4), round(h["p90"], 4)],
                     "ai_p50": ai, "label": spec.get("label", mkey), "fix": spec.get("fix", "")})
    gz = {g: sum(v) / len(v) for g, v in groups.items() if v}
    comp, lean, contrib = composite_of(gz, reg)
    rz = {g: sum(v) / len(v) for g, v in rgroups.items() if v}
    over = math.sqrt(sum(z * z for z in rz.values()) / len(rz)) if rz else 0.0
    cspec = reg.get("composite", {})
    thr = interp(cspec["threshold"], n) if cspec.get("threshold") else None
    over_thr = interp(cspec["over_threshold"], n) if cspec.get("over_threshold") else None
    dims = []
    for g, z in sorted(gz.items(), key=lambda kv: (-contrib.get(kv[0], 0.0), -kv[1])):
        gb = reg.get("groups", {}).get(g)
        b = interp(gb, n) if gb else {"p75": 0.7, "p90": 1.5}
        dims.append({"dimension": g, "z": round(z, 2),
                     "status": "PASS" if z <= b["p75"] + 1e-9 else ("WARN" if z <= b["p90"] + 1e-9 else "FAIL"),
                     "human_p75_p90": [round(b["p75"], 2), round(b["p90"], 2)],
                     "share": round(contrib[g] / comp, 3) if contrib and comp > 0 else None})
    ls = sorted(int(k) for k in cspec["threshold"]) if thr is not None else []
    power = interp(reg["power"], n) if reg.get("power") else None
    maxv = reg.get("max_classic_violations", 1)
    return {"register": key, "mode": "whole", "n_words": n, "rows": rows, "composite": round(comp, 3), "leans_toward": lean,
            "composite_threshold": round(thr, 3) if thr is not None else None,
            "calibrated_range": [ls[0], ls[-1]] if ls else None, "waived": sorted(waive),
            "dimensions": dims, "classic_violations": viol, "max_classic_violations": maxv,
            "overcorrection": round(over, 3), "overcorrection_limit": round(over_thr, 3) if over_thr is not None else None,
            "overcorrected": sorted(((g, round(z, 2)) for g, z in rz.items() if z >= 1.5), key=lambda kv: -kv[1]),
            "gate_pass": (thr is None or comp <= thr) and len(viol) <= maxv and (over_thr is None or over <= over_thr),
            "power": {k: round(v, 3) for k, v in power.items()} if power else None,
            "calibration_note": reg.get("note", "")}


def windows(doc, size):
    """Consecutive windows of whole sentences, equal in length and as close to `size` words as possible."""
    k = max(2, int(round(doc.n_words / float(size))))
    target = int(math.ceil(doc.n_words / float(k)))
    out, start = [], 0
    for w in range(k):
        text, n, nxt = doc.window_text(target if w < k - 1 else doc.n_words, start)
        if n:
            out.append((T.Doc(text, doc.lang), [doc.sentences[start]["i"], doc.sentences[nxt - 1]["i"]]))
        start = nxt
        if start >= len(doc.sentences):
            break
    return out


def score(doc, m, calib, register, waive=(), protect=()):
    """Gate decision for a document of any length. Up to LONG_DOC_FACTOR times the longest calibrated
    length the text is scored whole. Longer documents are cut into equal windows of calibrated length,
    every window is scored against the bands for its length, and the document passes when the mean
    window composite is within the threshold and no window exceeds the classic-guard allowance."""
    key = register_key(calib, register, doc.lang)
    if key is None or m["words"] < MIN_WORDS_FOR_GATE:
        return None
    reg = calib["registers"][key]
    top = max(int(k) for k in reg["composite"]["threshold"])
    if m["words"] <= top * LONG_DOC_FACTOR:
        return evaluate(m, calib, register, waive, lang=doc.lang)
    parts = []
    for wd, span in windows(doc, top):
        ev = evaluate(metrics_of(wd, protect), calib, register, waive, lang=doc.lang)
        ev["sentences"] = span
        parts.append(ev)
    comp = mean([p["composite"] for p in parts])
    thr = mean([p["composite_threshold"] for p in parts])
    zs, sh = collections.defaultdict(list), collections.defaultdict(list)
    for p in parts:
        for d in p["dimensions"]:
            zs[d["dimension"]].append(d["z"])
            sh[d["dimension"]].append(d.get("share") or 0.0)
    gb = reg.get("groups", {})
    dims = []
    for g, v in sorted(zs.items(), key=lambda kv: (-mean(sh[kv[0]]), -mean(kv[1]))):
        z = mean(v)
        b = interp(gb[g], parts[0]["n_words"]) if g in gb else {"p75": 0.7, "p90": 1.5}
        dims.append({"dimension": g, "z": round(z, 2),
                     "status": "PASS" if z <= b["p75"] else ("WARN" if z <= b["p90"] else "FAIL"),
                     "human_p75_p90": [round(b["p75"], 2), round(b["p90"], 2)], "share": round(mean(sh[g]), 3)})
    worst = max(parts, key=lambda p: len(p["classic_violations"]))
    maxv = parts[0]["max_classic_violations"]
    over = mean([p["overcorrection"] for p in parts])
    over_thr = parts[0]["overcorrection_limit"]
    oc = collections.defaultdict(list)
    for p in parts:
        for g, z in p["overcorrected"]:
            oc[g].append(z)
    return {"register": key, "mode": "windows", "n_words": m["words"], "composite": round(comp, 3),
            "leans_toward": max(parts, key=lambda p: p["composite"]).get("leans_toward"),
            "composite_threshold": round(thr, 3), "calibrated_range": parts[0]["calibrated_range"],
            "waived": sorted(set(waive or ())), "dimensions": dims, "windows": parts,
            "rows": [dict(r, window=i + 1) for i, p in enumerate(parts) for r in p["rows"]],
            "classic_violations": sorted({v for p in parts for v in p["classic_violations"]}),
            "max_classic_violations": maxv, "overcorrection": round(over, 3), "overcorrection_limit": over_thr,
            "overcorrected": sorted(((g, round(max(v), 2)) for g, v in oc.items()), key=lambda kv: -kv[1]),
            "gate_pass": comp <= thr and len(worst["classic_violations"]) <= maxv and (over_thr is None or over <= over_thr),
            "power": parts[0].get("power"), "calibration_note": reg.get("note", "")}


# ------------------------------------------------------------------------------- length
UNSUPPORTED_BELOW = 0.40      # share of a sentence's content words found in the anchor texts
UNSUPPORTED_THIN, UNSUPPORTED_PADDING = 0.25, 0.40       # share of the judged words in such sentences
ANCHOR_MIN_SOURCE_WORDS = 60  # a one-line brief anchors nothing


def loose_sentences(doc, anchors, old_sets=()):
    """Sentences of `doc` that carry no number, name or acronym and share less than UNSUPPORTED_BELOW of
    their content lemmas with the anchor texts (the source, the notes, an earlier version): general
    statements about the topic, the usual seat of padding and of claims the source does not make.
    Sentences with fewer than three content lemmas are not judged; sentences that `old_sets` already
    hold (70% of their content lemmas in one old sentence) are skipped.
    Returns (words judged, [[sentence number, words, share anchored, text], ...])."""
    lp = doc.lp
    base = set()
    for d in anchors:
        for s in d.all_sentences:
            base |= _content_set(s, lp)
    judged, loose = 0, []
    for s in doc.sentences:
        c = _content_set(s, lp)
        if len(c) < 3 or any(len(c & o) >= 0.7 * len(c) for o in old_sets):
            continue
        judged += s["n"]
        support = len(c & base) / float(len(c))
        if support < UNSUPPORTED_BELOW and not any(g in ("NUM", "PROPN", "ACRO") for g in s["tags"]):
            loose.append([s["i"], s["n"], round(support, 2), s["text"]])
    return judged, sorted(loose, key=lambda x: x[2])


def length_report(doc, target=None, tolerance=0.10, min_words=None, max_words=None, source_text=None):
    """Word count against the requested length. If a source or brief is given, list what it contains
    that the draft has not used (substance to add instead of padding) and which sentences of the
    draft are not anchored in it (candidates for padding or for claims the source does not make)."""
    n = doc.count["total"]
    out = {"words": n, "count": doc.count, "target": target, "min_words": min_words, "max_words": max_words,
           "tolerance": tolerance, "status": None}
    lo = max(x for x in (min_words, int(math.ceil(target * (1 - tolerance))) if target else None, 0) if x is not None)
    his = [x for x in (max_words, int(math.floor(target * (1 + tolerance))) if target else None) if x is not None]
    hi = min(his) if his else None
    if target or min_words or max_words:
        out["allowed"] = [lo, hi]
        out["status"] = "UNDER" if n < lo else ("OVER" if hi is not None and n > hi else "ON TARGET")
        out["words_missing"] = max(0, lo - n)
        out["words_excess"] = max(0, n - hi) if hi is not None else 0
    if source_text:
        import fact_ledger
        out["unused"] = fact_ledger.unused(source_text, doc.raw, doc.lang)
        src = T.Doc(source_text, doc.lang)
        out["source_words"] = src.count["total"]
        if out["source_words"] >= ANCHOR_MIN_SOURCE_WORDS:
            judged, loose = loose_sentences(doc, [src])
            out["unanchored_share"] = round(sum(x[1] for x in loose) / float(judged), 3) if judged else 0.0
            out["unanchored_sentences"] = loose[:10]
    return out


PADDING_KEYS = (("padding.restatement_share", "sentences repeating an earlier one (share)"),
                ("padding.metadiscourse_per1k", "announcements per 1k"), ("padding.wordy_per1k", "wordy phrases per 1k"),
                ("padding.participial_clause_per1k", "comment clauses per 1k"), ("padding.shell_noun_per1k", "abstract framing nouns per 1k"),
                ("padding.double_hedge_per1k", "stacked hedges per 1k"), ("padding.binomial_per1k", "doublets per 1k"),
                ("stock.significance_echo_per1k", "significance-echo sentences per 1k"), ("stock.stock_per1k", "stock phrases per 1k"))


def growth_report(old_doc, new_doc, calib=None, register="general", source_doc=None):
    """Did a longer version add information or only words? Counts what the added words bring that the
    shorter version did not have: new content words (lemmas) and new specifics (numbers, names,
    acronyms), per 100 added words, against what human texts of this register add when they grow by the
    same amount (calibration table 'growth'). Also compares the padding rates of the two versions, and
    lists the added sentences that carry no number or name and share little vocabulary with the old
    version or the source: general statements about the topic, the usual material of padding."""
    wo, wn = old_doc.n_words, new_doc.n_words
    added = wn - wo
    out = {"words_old": old_doc.count["total"], "words_new": new_doc.count["total"], "words_added": added}
    if added < 20:
        out["status"] = "NOT LONGER"
        return out
    new_c = content_types(new_doc) - content_types(old_doc)
    new_f = fact_types(new_doc) - fact_types(old_doc)
    out["new_content_words"] = len(new_c)
    out["new_specifics"] = sorted(new_f)[:40]
    out["content_per100"] = round(100.0 * len(new_c) / added, 1)
    out["specifics_per100"] = round(100.0 * len(new_f) / added, 1)
    ref = None
    key = register_key(calib, register, new_doc.lang)
    if key and calib["registers"][key].get("growth"):
        ref = interp(calib["registers"][key]["growth"], wo)
    ref = ref or {"content_p10": 20.0, "content_p25": 24.0, "content_p50": 30.0, "specifics_p25": 0.5, "specifics_p50": 2.0}
    out["human"] = {k: round(v, 1) for k, v in ref.items() if k != "n"}
    mo, mn = metrics_of(old_doc), metrics_of(new_doc)
    specs = calib["registers"][key]["metrics"] if key else {}
    worse = []
    for path, label in PADDING_KEYS:
        a, b = getpath(mo, path) or 0.0, getpath(mn, path) or 0.0
        unit = len(new_doc.sentences) if path.endswith("share") else wn / 1000.0
        human = interp(specs[path]["bands"], wn)["p50"] if path in specs else 0.0
        # A rate "went up" when the new version has at least two occurrences more than the old rate
        # predicts for its length, the rate rose by 30% or more, and it is now above the rate of the
        # median human text of this length (one more framing noun in 600 words is not padding).
        if (b - a) * unit >= 1.5 and b > 1.3 * a and b > human:
            worse.append([label, a, b])
    out["padding_up"] = worse
    # added sentences, and how much of each is anchored in the old version or the source
    old_sets = [c for c in (_content_set(s, new_doc.lp) for s in old_doc.all_sentences) if c]
    added_words, loose = loose_sentences(new_doc, [d for d in (old_doc, source_doc) if d is not None], old_sets)
    share = sum(x[1] for x in loose) / float(added_words) if added_words else 0.0
    out["unsupported_share"] = round(share, 3)
    out["unsupported_sentences"] = loose[:10]
    out["source_given"] = source_doc is not None
    low_content = out["content_per100"] < ref["content_p25"]
    no_specifics = not new_f and ref["specifics_p50"] > 0
    out["status"] = ("PADDING" if out["content_per100"] < ref["content_p10"] or len(worse) >= 2 or share >= UNSUPPORTED_PADDING else
                     "THIN" if worse or no_specifics or share >= UNSUPPORTED_THIN or
                     (low_content and out["specifics_per100"] < ref["specifics_p50"]) else
                     "SUBSTANCE")
    out["reasons"] = [r for r, c in (("few new content words: the added text mostly repeats", out["content_per100"] < ref["content_p10"]),
                                     ("several padding rates went up", len(worse) >= 2),
                                     ("a padding rate went up", len(worse) == 1),
                                     ("%.0f%% of the added words stand in sentences with no number or name and little "
                                      "vocabulary from the %s" % (100 * share, "source or the old version" if source_doc is not None else "old version"),
                                      share >= UNSUPPORTED_THIN),
                                     ("no new number, name or acronym in the added text", no_specifics),
                                     ("fewer new content words than three quarters of human texts", low_content and out["content_per100"] >= ref["content_p10"])) if c]
    return out


def render_growth(g):
    if g.get("status") == "NOT LONGER":
        return "# Growth check\nThe new version is not longer than the old one (%d -> %d words): nothing to check." % (g["words_old"], g["words_new"])
    h = g["human"]
    out = ["# Growth check: %d -> %d words (+%d analysed words)  ->  %s" % (g["words_old"], g["words_new"], g["words_added"], g["status"]),
           "- new content words per 100 added words: %.1f  (human texts growing from this length: p10 %.1f, p25 %.1f, median %.1f)" % (
               g["content_per100"], h["content_p10"], h["content_p25"], h["content_p50"]),
           "- new numbers, names and acronyms per 100 added words: %.1f  (human: p25 %.1f, median %.1f)%s" % (
               g["specifics_per100"], h["specifics_p25"], h["specifics_p50"],
               "  [" + ", ".join(g["new_specifics"][:20]) + "]" if g["new_specifics"] else "")]
    for label, a, b in g["padding_up"]:
        out.append("- padding went up: %s %s -> %s" % (label, fmt_num(a), fmt_num(b)))
    if g.get("unsupported_sentences"):
        out.append("- added sentences with no number or name and little vocabulary from the %s (%.0f%% of the added words). "
                   "For each: is it a fact of the source, a calculation, or a condition, limit or consequence that follows "
                   "from its facts? A general statement about the topic is padding, or a claim the source does not make." % (
                       "source or the old version" if g.get("source_given") else "old version (give --source to count the notes or the brief)",
                       100 * g["unsupported_share"]))
        for i, n, sup, text in g["unsupported_sentences"]:
            out.append("    s%d (%dw, %.0f%% anchored): %s" % (i, n, 100 * sup, text if len(text) <= 150 else text[:147] + "..."))
    if g["reasons"]:
        out.append("- why: " + "; ".join(g["reasons"]))
    if g["status"] == "PADDING":
        out.append("The added words restate or decorate. Remove them; lengthen only with facts, steps of reasoning, conditions, "
                   "limits or consequences that the source supports. Every new specific must pass fact_ledger.py.")
    elif g["status"] == "THIN":
        out.append("Apply the deletion test (SKILL.md) to every added sentence, the listed ones first: a sentence the text "
                   "does not need, or that states something the source does not, is cut.")
    else:
        out.append("The added words bring new content at the rate human texts do. Run fact_ledger.py: every new specific must come from the source.")
    return "\n".join(out)


# ------------------------------------------------------------------------------- compare mode
def two_prop_z(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0:
        return 0.0
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) if 0 < p < 1 else 0
    return (k1 / n1 - k2 / n2) / se if se else 0.0


def ks_2samp(a, b):
    a, b = sorted(a), sorted(b)
    n, m = len(a), len(b)
    if not n or not m:
        return 0.0, 1.0
    i = j = 0
    d = 0.0
    while i < n and j < m:
        x = min(a[i], b[j])
        while i < n and a[i] <= x:
            i += 1
        while j < m and b[j] <= x:
            j += 1
        d = max(d, abs(i / n - j / m))
    en = math.sqrt(n * m / (n + m))
    lam = (en + 0.12 + 0.11 / en) * d
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 101))
    return round(d, 3), round(min(max(p, 0.0), 1.0), 4)


def compare_docs(doc_a, ma, doc_b, mb):
    lp = doc_a.lp
    mm = {id(doc_a): ma, id(doc_b): mb}
    back = lambda d, path: round((getpath(mm[id(d)], path) or 0) * d.n_words / 1000.0)  # noqa: E731
    ct = lambda d, pred: sum(1 for w in d.toks if pred(w))  # noqa: E731
    word_feats = [
        ("nominalizations", lambda d: back(d, "nominal.nominalization_per1k")),
        ("first-person pronouns", lambda d: ct(d, lambda w: w in lp.FIRST_PERSON)),
        ("all pronouns", lambda d: ct(d, lambda w: w in lp.FIRST_PERSON | lp.SECOND_PERSON | lp.THIRD_PERSON)),
        ("AI-favoured function words", lambda d: ct(d, lambda w: w in lp.AI_FAVORED_FW)),
        ("human-favoured function words", lambda d: ct(d, lambda w: w in lp.HUMAN_FAVORED_FW)),
        ("derived adverbs (-ly / -ment)", lambda d: sum(1 for t, g in zip(d.toks, d.tags) if lp.is_derived_adverb(t, g))),
        ("nouns (tagged)", lambda d: d.tags.count("NOUN")),
        ("verbs (tagged)", lambda d: d.tags.count("VERB")),
        ("adjectives (tagged)", lambda d: sum(d.tags.count(t) for t in ("ADJ", "ADJC", "ADJS"))),
        ("names + acronyms + numbers", lambda d: sum(d.tags.count(t) for t in ("PROPN", "ACRO", "NUM"))),
        ("commas", lambda d: d.all_text.count(",")),
        ("semicolons + colons + parentheses", lambda d: d.all_text.count(";") + d.all_text.count(":") + d.all_text.count("(")),
        ("dashes", lambda d: _marks(d.all_text, [])["dash"]),
        ("wordy phrases", lambda d: back(d, "padding.wordy_per1k")),
        ("abstract framing nouns", lambda d: back(d, "padding.shell_noun_per1k")),
        ("participial tail clauses", lambda d: back(d, "padding.participial_clause_per1k")),
        ("stance markers", lambda d: back(d, "stance.stance_per1k")),
    ]
    rows = []
    for name, f in word_feats:
        ka, kb = f(doc_a), f(doc_b)
        rows.append({"feature": name, "draft_per1k": per_k(ka, doc_a.n_words), "ref_per1k": per_k(kb, doc_b.n_words),
                     "z": round(two_prop_z(ka, doc_a.n_words, kb, doc_b.n_words), 2)})
    sa, sb = len(doc_a.sentences), len(doc_b.sentences)
    for name, path in (("sentence-initial connectives", "connectives.connective_initial_share"),
                       ("formulaic sentence openers", "connectives.formulaic_initial_share"),
                       ("passive sentences", "structure.passive_sentence_share"),
                       ("questions", "stance.question_share"),
                       ("subject-first sentences", "structure.subject_initial_share")):
        ka, kb = round((getpath(ma, path) or 0) * sa), round((getpath(mb, path) or 0) * sb)
        rows.append({"feature": name + " (per sentence)", "draft_per1k": per_k(ka, sa), "ref_per1k": per_k(kb, sb),
                     "z": round(two_prop_z(ka, sa, kb, sb), 2)})
    d, p = ks_2samp([s["n"] for s in doc_a.sentences], [s["n"] for s in doc_b.sentences])
    # vocabulary: both texts measured at the same sample size, so their lengths may differ
    nmin = min(ma["lexical"].get("lemma_tokens", 0), mb["lexical"].get("lemma_tokens", 0))
    scalar = {k: (getpath(ma, path), getpath(mb, path)) for k, path in (
        ("sentence length mean", "rhythm.sent_len_mean"), ("sentence length CV", "rhythm.sent_len_cv"),
        ("distinct lemmas per 100 (rarefied)", "lexical.types_at_100"), ("MATTR-50 (lemmas)", "lexical.mattr50"),
        ("repeat dispersion", "lexical.dispersion50"), ("paragraph length (words)", "paragraphs.para_words_mean"),
        ("stock phrases per 1k", "stock.stock_per1k"))}
    return {"rate_tests": rows, "sentence_length_ks": {"D": d, "p": p}, "scalar": scalar,
            "significant": sorted([r for r in rows if abs(r["z"]) >= 1.96], key=lambda r: -abs(r["z"])),
            "note": "z = two-proportion z-test (draft vs reference); |z|>=1.96 ~ p<.05, |z|>=2.58 ~ p<.01. "
                    "Low power under ~300 words per side: treat as hints. Vocabulary measures use fixed sample "
                    "sizes, so texts of different lengths are comparable (shorter side: %d lemma tokens)." % nmin}


# ------------------------------------------------------------------------------- reports
def fmt_num(x):
    if isinstance(x, float):
        return ("%.3f" % x).rstrip("0").rstrip(".")
    return str(x)


def sig(x):
    """Three significant digits, for report lines."""
    if not is_num(x):
        return str(x)
    if x == 0 or abs(x) >= 100:
        return "%.0f" % x
    return ("%.3g" % x)


def render_length(length):
    out = []
    c = length["count"]
    line = "## Length: %d words" % length["words"]
    if length["status"]:
        lo, hi = length["allowed"]
        line += "  (allowed %s)  ->  %s" % ("%d-%d" % (lo, hi) if hi is not None else ">= %d" % lo, length["status"])
    out.append(line)
    out.append("counted: body %d + list items %d + headings %d%s" % (
        c["body"], c["list_items"], c["headings"],
        "; not counted: %d table lines, %d code lines" % (c["table_lines_excluded"], c["code_lines_excluded"])
        if c["table_lines_excluded"] or c["code_lines_excluded"] else ""))
    if length["status"] == "UNDER":
        out.append("- %d words short. Add substance, never filler: a fact the source has and the draft lacks, a step of "
                   "reasoning, a condition or limit, a consequence, a comparison with its basis. If nothing true is left "
                   "to add, stop and say so (SKILL.md, 'Length without padding')." % length["words_missing"])
    if length["status"] == "OVER":
        out.append("- %d words over. Cut what the padding section lists first: restatements, announcements, wordy "
                   "phrases, doublets, comment clauses." % length["words_excess"])
    u = length.get("unused")
    if u:
        out.append("- In the source, not in the draft: numbers %s | names and terms %s" % (
            ", ".join(u["numbers"][:25]) or "none", ", ".join(u["names"][:25]) or "none"))
        if length["status"] == "UNDER" and len(u["numbers"]) <= 2:
            out.append("- The draft already uses the source's numbers. What can still be added: a calculation on them, or a "
                       "condition, limit or consequence that follows from the source's facts. General statements about the "
                       "topic are padding. If nothing of that kind is left, STOP: deliver the text at %d words and tell the "
                       "user what material would be needed for more." % length["words"])
    if length.get("unanchored_share") is not None:
        sh = length["unanchored_share"]
        out.append("- The source has %d words, this text %d. Not anchored in the source: %.0f%% of the words (sentences with "
                   "no number or name and little of the source's vocabulary, listed under 'Where to look')." % (
                       length["source_words"], length["words"], 100 * sh))
        if sh >= UNSUPPORTED_THIN and length["status"] in ("ON TARGET", "OVER"):
            out.append("- CHECK THE LENGTH. In a text that reports (a summary, results, a description), sentences that are "
                       "not anchored in the source are padding: a count reached with them was not reached. In a text that "
                       "interprets (a discussion, an argument), they are the reasoning, and each must follow from the "
                       "source's facts. Keep a listed sentence only if it is a fact of the source, a calculation, or a "
                       "condition, limit or consequence of its facts. If the text then falls short of the target, deliver "
                       "it short and tell the user what material is missing.")
    return out


def render(doc, m, ev, show_sentences=False, length=None, show_all=False):
    r = m["rhythm"]
    out = ["# SciHumanizer metrics report (%s)" % doc.lp.NAME,
           "words=%d (analysed: %d; citation markers and headings are not analysed)  sentences=%d  paragraphs=%d" % (
               m["count"]["total"], m["words"], r.get("sentences", 0), m["paragraphs"]["paragraphs"])]
    if length:
        out.append("")
        out.extend(render_length(length))
    if m["words"] < MIN_WORDS_FOR_GATE:
        out.append("")
        out.append("NOTE: under %d words there is too little text for stable statistics, so no gate is applied "
                   "(power by length: references/calibration.md). Use the pointers below and the semantic checklist." % MIN_WORDS_FOR_GATE)
    if ev:
        out.append("")
        out.append("## Style gate (%s, bands for %s)  composite=%s  threshold=%s  ->  %s" % (
            ev["register"],
            "%d-word texts" % ev["n_words"] if ev["mode"] == "whole" else "%d windows of about %d words" % (
                len(ev["windows"]), ev["windows"][0]["n_words"]),
            ev["composite"], ev["composite_threshold"], "PASS" if ev["gate_pass"] else "FAIL"))
        rng = ev.get("calibrated_range")
        if ev["mode"] == "whole" and rng and ev["n_words"] > rng[1]:
            out.append("(longer than the calibrated %d-%d words: the bands for %d words are used)" % (rng[0], rng[1], rng[1]))
        if ev.get("power"):
            out.append("at this length the gate passes %.0f%% of held-out human texts and %.0f%% of unedited AI texts" % (
                100 * ev["power"]["human_pass"], 100 * ev["power"]["ai_pass"]))
        if ev.get("waived"):
            out.append("waived dimensions (excluded from the composite; say so in the verification block): " + ", ".join(ev["waived"]))
        if ev["mode"] == "windows":
            for i, w in enumerate(ev["windows"], 1):
                out.append("- window %d (sentences %d-%d, %d words): composite %s vs %s -> %s; highest: %s" % (
                    i, w["sentences"][0], w["sentences"][1], w["n_words"], w["composite"], w["composite_threshold"],
                    "PASS" if w["gate_pass"] else "FAIL",
                    ", ".join("%s %.1f" % (d["dimension"], d["z"]) for d in w["dimensions"][:3])))
        if ev.get("leans_toward"):
            out.append("closest AI profile: %s. Dimensions are listed by how much of the composite they explain: fix from the top." % ev["leans_toward"])
        if ev["classic_violations"]:
            out.append("classic tells beyond the human range (max allowed %d%s): %s" % (
                ev["max_classic_violations"], " per window" if ev["mode"] == "windows" else "", ", ".join(ev["classic_violations"])))
        if ev.get("overcorrection_limit") is not None:
            bad = ev["overcorrection"] > ev["overcorrection_limit"]
            if bad or ev["overcorrected"]:
                out.append("over-correction %s (limit %s)%s%s" % (
                    ev["overcorrection"], ev["overcorrection_limit"], " -> TOO FAR: the text now overshoots human writing" if bad else "",
                    "; beyond the human median on the far side: " + ", ".join("%s %.1f" % kv for kv in ev["overcorrected"]) if ev["overcorrected"] else ""))
        out.append("### Dimensions: one verdict each, against human texts of this length")
        by_dim = collections.defaultdict(list)
        for row in ev["rows"]:
            by_dim[row["group"]].append(row)
        passed = []
        for d in ev["dimensions"]:
            rows = sorted(by_dim.get(d["dimension"], []), key=lambda x: (x.get("window", 0), -x["z"]))
            over = [x for x in rows if x["status"] == "OVER"]
            if d["status"] == "PASS" and not over and not show_all:
                passed.append("%s %.2f" % (d["dimension"], d["z"]))
                continue
            out.append("- [%s] %s: z=%.2f (human p75 %.2f, p90 %.2f)%s" % (
                d["status"], d["dimension"], d["z"], d["human_p75_p90"][0], d["human_p75_p90"][1],
                ", %.0f%% of the composite" % (100 * d["share"]) if d.get("share") else ""))
            fixes = []
            for row in rows:
                if row["status"] == "PASS" and not show_all:
                    continue
                h = row["human_p10_p50_p90"]
                out.append("    [%s] %s%s = %s  (human p10 / p50 / p90: %s / %s / %s; AI: %s; %s)" % (
                    row["status"], "w%d " % row["window"] if "window" in row else "", row["label"], sig(row["value"]),
                    sig(h[0]), sig(h[1]), sig(h[2]),
                    ", ".join("%s %s" % (sig(v), k) for k, v in row["ai_p50"].items()) or "?", row["direction"]))
                if row["status"] == "OVER":
                    fx = "over-corrected: this is now beyond the human range on the far side. Move back toward the human median (%s)." % sig(h[1])
                    if not any(f.startswith("over-corrected") for f in fixes):
                        fixes.append(fx)
                elif row["fix"] and not row["fix"].startswith("Same as") and row["fix"] not in fixes:
                    fixes.append(row["fix"])
            for fx in fixes[:3]:
                out.append("    fix: " + fx)
        if passed:
            out.append("- [PASS] " + ", ".join(passed))
    out.append("")
    out.append("## Where to look")
    if r.get("uniform_run_at"):
        a, b = r["uniform_run_at"]
        out.append("- Uniform-length run: sentences %d-%d, lengths %s (tolerance +/-%d words)" % (
            a, b, [s["n"] for s in doc.sentences[a - 1:b]], r["uniform_run_tolerance"]))
    pt = m["pointers"]
    if length and length.get("unanchored_sentences"):
        out.append("- Not anchored in the source (no number or name, little of its vocabulary): for each, is it a fact of "
                   "the source, a calculation, or a consequence of its facts? If not, it is padding or invention.")
        for i, n, sup, text in length["unanchored_sentences"]:
            out.append("    s%d (%dw, %.0f%% anchored): %s" % (i, n, 100 * sup, text if len(text) <= 130 else text[:127] + "..."))
    lx0 = m["lexical"]
    grow = next((x for x in ev["rows"] if x["metric"] == "lexical.glue_per100"), None) if ev else None
    if grow and lx0.get("glue_counts"):
        p10, p50, p90 = grow["human_p10_p50_p90"]
        base = lx0["glue_base"] / 100.0
        out.append("- Glue words: %d in this text (%s). Human texts of this length have about %d (most between %d and %d)." % (
            sum(lx0["glue_counts"].values()), ", ".join("%s %d" % kv for kv in lx0["glue_counts"].items()),
            round(p50 * base), round(p10 * base), round(p90 * base)))
    if pt["long_sentences"]:
        out.append("- Long / comma-chained sentences: " + ", ".join("s%d (%dw, %d commas)" % (i, w, k) for i, w, k in pt["long_sentences"]))
    if pt["compressed_sentences"]:
        out.append("- Compressed sentences (few glue words: %s): " % "/".join(doc.lp.GLUE_LEMMAS) +
                   ", ".join("s%d (%d in %d tokens)" % (i, k, nt) for i, k, nt in pt["compressed_sentences"]))
    if pt["top_derived_adverbs"]:
        out.append("- Most used derived adverbs: " + ", ".join("%s(%d)" % (w, k) for w, k in pt["top_derived_adverbs"][:8]))
    if pt["top_adjectives"]:
        out.append("- Most used adjectives: " + ", ".join("%s(%d)" % (w, k) for w, k in pt["top_adjectives"][:8]))
    cn = pt["counts"]
    out.append("- Specifics: %d proper nouns, %d acronyms, %d numbers | punctuation: %d parentheses, %d semicolons, "
               "%d colons, %d questions, %d dashes" % (cn["proper_nouns"], cn["acronyms"], cn["numbers"], cn["parentheses"],
                                                      cn["semicolons"], cn["colons"], cn["questions"], cn["dashes"]))
    c = m["connectives"]
    if c["formulaic_initial_sentences"]:
        out.append("- Formulaic sentence openers: " + ", ".join("s%d '%s'" % (i, p) for i, p in c["formulaic_initial_sentences"]))
    st = m["stock"]
    if st["stock_where"]:
        out.append("- Stock phrases: " + ", ".join("s%s %s" % (i if i else "(list)", lab) for i, lab in st["stock_where"]))
    if st.get("ai_vocab_hits"):
        out.append("- LLM-typical vocabulary (practitioner list; legitimate in some fields, check context): " +
                   ", ".join("%s(%d)" % (w, k) for w, k in st["ai_vocab_hits"].items()))
    if st["significance_echo_sentences"]:
        out.append("- Significance-echo sentences (restate importance, add nothing): " + ", ".join("s%d" % i for i in st["significance_echo_sentences"]))
    mk = m["markers"]
    if mk["ai_function_hits"] or mk["ai_content_hits"]:
        out.append("- Words current models over-use (calibrated list): " + ", ".join(
            "%s(%d)" % (w, k) for w, k in list(mk["ai_function_hits"].items()) + list(mk["ai_content_hits"].items())))
    pd = m["padding"]
    pad = []
    if pd["restating_sentences"]:
        pad.append("sentences that mostly repeat an earlier one: " + ", ".join("s%d" % i for i in pd["restating_sentences"]))
    if pd["metadiscourse_hits"]:
        pad.append("announcing instead of saying: " + ", ".join("'%s' x%d" % (w, k) for w, k in pd["metadiscourse_hits"].items()))
    if pd["wordy_hits"]:
        pad.append("wordy phrases: " + ", ".join("'%s' x%d" % (w, k) for w, k in pd["wordy_hits"].items()))
    if pd["participial_clauses"]:
        pad.append("comment clauses after a comma: " + ", ".join("s%s ', %s ...'" % (i if i else "(list)", w) for i, w in pd["participial_clauses"]))
    if pd["binomial_examples"]:
        pad.append("doublets: " + ", ".join(pd["binomial_examples"]))
    if pd["shell_hits"]:
        pad.append("abstract framing nouns: " + ", ".join("%s(%d)" % (w, k) for w, k in pd["shell_hits"].items()))
    for line in pad:
        out.append("- Padding candidates, " + line)
    nm = m["nominal"]
    if nm["nominal_heavy_sentences"]:
        out.append("- Nominalization clusters (>=3 per sentence): " + "; ".join("s%d %s" % (i, "/".join(ws)) for i, k, ws in nm["nominal_heavy_sentences"]))
    lx = m["lexical"]
    if lx.get("top_repeated_3grams"):
        out.append("- Repeated 3-grams: " + ", ".join("'%s' x%d" % (g, k) for g, k in lx["top_repeated_3grams"]))
    if lx.get("repeated_frames"):
        out.append("- Repeated sentence frames: " + ", ".join("'%s' x%d" % (g, k) for g, k in lx["repeated_frames"]))
    if lx.get("top_content_words"):
        out.append("- Most repeated content words: " + ", ".join("%s(%d)" % (w, k) for w, k in lx["top_content_words"][:8]))
    d = m["document"]
    if d.get("stock_opener"):
        out.append("- Opening sentence uses a stock opener.")
    if d.get("formulaic_ending"):
        out.append("- Final paragraph is a formulaic wrap-up (summary connective / future-outlook boilerplate).")
    if d.get("paragraph_wrapup_share", 0) >= 0.3:
        out.append("- %.0f%% of paragraphs end with a summary/significance sentence." % (100 * d["paragraph_wrapup_share"]))
    if pd.get("intro_outro_overlap") is not None and pd["intro_outro_overlap"] >= 0.5:
        out.append("- %.0f%% of the last paragraph's content words already stand in the first paragraph: the ending "
                   "repeats the opening." % (100 * pd["intro_outro_overlap"]))
    p = m["punctuation"]
    if p["em_dash_per1k"] > 3:
        out.append("- Dashes: %.1f per 1k words (keep rare unless the writer uses them)." % p["em_dash_per1k"])
    f = m["format"]
    if f["bold_lead_items"] or f["emoji"] or f["title_case_headings"]:
        out.append("- Formatting artifacts: bold-lead bullets=%d, emoji=%d, title-case headings=%d" % (
            f["bold_lead_items"], f["emoji"], f["title_case_headings"]))
    for label, k in f.get("typography", []):
        out.append("- Typography: %s (x%d)" % (label, k))
    out.append("")
    out.append("## Profile")
    for grp in ("rhythm", "paragraphs", "lexical", "pos", "nominal", "function_words", "connectives", "stance",
                "sentiment", "punctuation", "markers", "padding", "structure", "stock", "document"):
        vals = {k: v for k, v in m[grp].items() if not isinstance(v, (list, dict)) or k in ("opener_classes", "per1k", "initial_connectives")}
        out.append("- %s: %s" % (grp, ", ".join("%s=%s" % (k, fmt_num(v) if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False)) for k, v in vals.items())))
    if show_sentences:
        out.append("")
        out.append("## Sentences")
        for s in doc.sentences:
            flags = []
            ph, _ = initial_connective(s, doc.lp)
            if ph:
                flags.append("conn:" + ph)
            k = len(_nominals(s, doc.lp))
            if k >= 2:
                flags.append("nom:%d" % k)
            if doc.lp.passive(s["toks"], s["tags"]):
                flags.append("passive")
            out.append("s%d [%dw]%s %s" % (s["i"], s["n"], (" {" + ", ".join(flags) + "}") if flags else "", s["text"]))
    return "\n".join(out)


def render_compare(res):
    out = ["# Draft vs reference", "sentence-length distribution: KS D=%s p=%s %s" % (
        res["sentence_length_ks"]["D"], res["sentence_length_ks"]["p"],
        "(different rhythm)" if res["sentence_length_ks"]["p"] < 0.05 else "(compatible)")]
    for k, (a, b) in res["scalar"].items():
        out.append("- %s: draft %s | ref %s" % (k, fmt_num(a) if a is not None else "-", fmt_num(b) if b is not None else "-"))
    out.append("")
    out.append("## Significant deviations (|z| >= 1.96)")
    if not res["significant"]:
        out.append("none")
    for r in res["significant"]:
        out.append("- %s: draft %s vs ref %s per 1k  (z=%s, draft %s)" % (
            r["feature"], r["draft_per1k"], r["ref_per1k"], r["z"], "higher" if r["z"] > 0 else "lower"))
    out.append("")
    out.append(res["note"])
    return "\n".join(out)


# ------------------------------------------------------------------------------- user calibration
def auc(h, a):
    """P(AI value > human value), ties count half (Mann-Whitney)."""
    hs = sorted(h)
    tot = 0.0
    for x in a:
        lo, hi = bisect.bisect_left(hs, x), bisect.bisect_right(hs, x)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(a) * len(h))


def quantiles(xs):
    return {k: round(pct(xs, q), 5) for k, q in QS}


def calibrate(human_dir, ai_dir, register, out_path, lang=None, base="scientific", min_gap=0.15):
    """Rebuild one register from your own folders. Every text is cut to one common length (the 25th
    percentile of the human lengths, so three quarters of them qualify) and the bands hold for texts
    around that length. Metric definitions, research guards and dimensions come from a base register.
    The shipped registers are built by a longer pipeline with several lengths and cross-validation."""
    def read(d):
        fps = sorted(glob.glob(os.path.join(d, "**", "*.txt"), recursive=True) +
                     glob.glob(os.path.join(d, "**", "*.md"), recursive=True))
        return [T.Doc(T.read_text(fp), lang) for fp in fps]
    Hd, Ad = read(human_dir), read(ai_dir)
    Hd = [d for d in Hd if d.n_words >= MIN_WORDS_FOR_GATE]
    if len(Hd) < 10 or len(Ad) < 5:
        sys.exit("need >= 10 human and >= 5 AI texts of >= %d words" % MIN_WORDS_FOR_GATE)
    lang = lang or Hd[0].lang
    L = max(MIN_WORDS_FOR_GATE, int(pct([d.n_words for d in Hd], 0.25)) // 50 * 50)
    H = [metrics_of(d.truncated(L)) for d in Hd if d.n_words >= L]
    A = [metrics_of(d.truncated(L)) for d in Ad if d.n_words >= L]
    if len(H) < 10 or len(A) < 5:
        sys.exit("after cutting to %d words only %d human and %d AI texts remain; need 10 and 5" % (L, len(H), len(A)))
    calib = load_calibration(out_path) or load_calibration() or {"version": 3, "registers": {}}
    bkey = register_key(calib, base, lang) or next(iter(calib["registers"]))
    Ls = str(L)
    metrics = {}
    for key, spec in calib["registers"][bkey]["metrics"].items():
        hv = [x for x in (getpath(m, key) for m in H) if is_num(x)]
        av = [x for x in (getpath(m, key) for m in A) if is_num(x)]
        if len(hv) < 10 or len(av) < 5:
            continue
        u = auc(hv, av)
        edir = 1 if u > 0.5 else -1
        guard = spec.get("guard")
        strong = abs(u - 0.5) >= min_gap
        conflict = ((guard == "ceiling" and edir < 0) or (guard == "floor" and edir > 0)) and strong
        hq = quantiles(hv)
        ns = {k: v for k, v in spec.items() if k not in ("bands", "ai_p50", "auc")}
        ns.update({"bands": {Ls: hq}, "ai_p50": {"your AI set": {Ls: round(pct(av, .5), 5)}}, "auc": {"your AI set": round(u, 3)},
                   "gate": strong and not conflict,
                   "ai_direction": (1 if guard == "ceiling" else -1) if (guard and (conflict or not strong)) else edir,
                   "min_scale": round(max(1e-6, 0.05 * (abs(hq["p50"]) or 1)), 6)})
        metrics[key] = ns
    name = "%s.%s" % (lang, register)
    reg = {"lang": lang, "metrics": metrics, "max_classic_violations": 1, "n_human": len(H), "n_ai": len(A),
           "composite": {"threshold": {Ls: 99.0}}}
    wrap = {"registers": {name: reg}}
    evs = [evaluate(m, wrap, register, lang=lang) for m in H]
    reg["composite"]["threshold"] = {Ls: round(pct([e["composite"] for e in evs], 0.90), 3)}
    gz = collections.defaultdict(list)
    for e in evs:
        for d in e["dimensions"]:
            gz[d["dimension"]].append(d["z"])
    reg["groups"] = {g: {Ls: {"p50": round(pct(v, .5), 4), "p75": round(pct(v, .75), 4), "p90": round(pct(v, .90), 4)}}
                     for g, v in gz.items()}
    az = collections.defaultdict(list)
    for m in A:
        for d in evaluate(m, wrap, register, lang=lang)["dimensions"]:
            az[d["dimension"]].append(d["z"])
    reg["profiles"] = {"your AI set": profile_weights(gz, az)}
    reg["composite"]["threshold"] = {Ls: round(pct([evaluate(m, wrap, register, lang=lang)["composite"] for m in H], 0.90), 3)}
    hp = sum(evaluate(m, wrap, register, lang=lang)["gate_pass"] for m in H) / len(H)
    ap = sum(evaluate(m, wrap, register, lang=lang)["gate_pass"] for m in A) / len(A)
    reg["power"] = {Ls: {"human_pass": round(hp, 3), "ai_pass": round(ap, 3)}}
    reg["note"] = "user calibration: %s (n=%d) vs %s (n=%d), texts cut to %d words; in-sample human pass %.0f%%, AI pass %.0f%%" % (
        human_dir, len(H), ai_dir, len(A), L, 100 * hp, 100 * ap)
    calib["registers"][name] = reg
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(calib, fh, indent=1, ensure_ascii=False)
    print("wrote %s: register '%s' at %d words (%d human, %d AI); threshold %.3f; human pass %.0f%%, AI pass %.0f%% (in-sample)" % (
        out_path, name, L, len(H), len(A), reg["composite"]["threshold"][Ls], 100 * hp, 100 * ap))


# ------------------------------------------------------------------------------- self-test
def selftest():
    ok = lexstats.selftest()

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))

    en = ("The model was trained on 1,200 scans from three hospitals (Lyon, Turin and Graz). It didn't generalise: "
          "accuracy fell from 91% to 78% on the external set. We suspect the scanners, because two sites used older "
          "detectors. Due to the fact that labels were noisy, we re-read 150 cases.\n\n## Methods\n\n- First item here\n")
    d = T.Doc(en, "en")
    check("word count: 49 body + 3 list + 1 heading words (1,200 / 91% / didn't / re-read are one word each)",
          (d.count["total"], d.count["body"], d.count["list_items"], d.count["headings"]) == (53, 49, 3, 1), str(d.count))
    check("count splits into body + list items + headings", d.count["total"] == d.count["body"] + d.count["list_items"] + d.count["headings"])
    check("sentence lengths sum to the analysed word count", sum(s["n"] for s in d.all_sentences) == d.n_words)
    check("contraction is one word but two tokens", d.n_tokens > d.n_words and "n't" in d.toks)
    check("lemma count unites inflected forms", lemma_count(T.Doc("It delves and delved, fostering what fosters.", "en"), "AI_VOCAB_LEMMAS")
          == collections.Counter({"delve": 2, "foster": 2}))
    check("overlapping phrases are counted once", sum(phrase_count(d, "WORDY").values()) == 1, str(dict(phrase_count(d, "WORDY"))))
    fr = T.Doc("L'étude montre qu'au sein de l'équipe, afin d'éviter les biais, 3,5 % des cas ont été relus. "
               "N'a-t-on pas oublié l'essentiel ?", "fr")
    check("French: elided phrase forms are matched", phrase_count(fr, "WORDY") == collections.Counter({"au sein de": 1}),
          str(dict(phrase_count(fr, "WORDY"))))
    check("French: l'étude / qu'au / N'a-t-on are one word each; a lone % or ? is not a word",
          fr.count["total"] == 20 and fr.n_tokens == 27 and "l'" in fr.toks, "(%d words, %d tokens)" % (fr.count["total"], fr.n_tokens))
    check("French: two sentences, question mark after a space", len(fr.sentences) == 2)
    table = {"200": {"p50": 1.0}, "400": {"p50": 2.0}}
    check("bands interpolate linearly in length and clamp outside", abs(interp(table, 300)["p50"] - 1.5) < 1e-12 and
          interp(table, 50)["p50"] == 1.0 and interp(table, 900)["p50"] == 2.0)
    h = {"p025": 0, "p10": 0, "p25": 0, "p50": 0, "p75": 0, "p90": 1.2816, "p975": 5}      # one unit = one SD upward
    check("scale falls back to a wider quantile for count metrics", abs(side_scale(h, 1, 1e-6) - 1.0) < 1e-9)
    check("one-sided z ignores the non-AI side; two-sided z counts both",
          metric_z(-3, h, 1, 0.5) == 0.0 and metric_z(-1, h, 0, 0.5) == 2.0 and abs(metric_z(2.5632, h, 1, 0.5) - 2.5632) < 1e-9)
    old = T.Doc("The trial compared two irrigation schedules in one vineyard block during a dry season.", "en")
    src = T.Doc("Plot B received 1,210 m3/ha of water. Two tensiometers failed in July and were replaced.", "en")
    new = T.Doc("The trial compared two irrigation schedules in one vineyard block during a dry season. "
                "Plot B received 1,210 m3/ha of water, and two tensiometers failed in July and were replaced. "
                "Water management is an increasingly important issue for sustainable agriculture worldwide. "
                "Careful planning remains essential for successful adoption across diverse farming contexts.", "en")
    g = growth_report(old, new, None, "general", src)
    check("growth: generic added sentences are listed as unanchored, sourced ones are not",
          [x[0] for x in sorted(g["unsupported_sentences"])] == [3, 4] and g["unsupported_share"] > 0.5 and g["status"] == "PADDING",
          str((g["unsupported_share"], [x[0] for x in g["unsupported_sentences"]], g["status"])))
    print("\nselftest: %s" % ("all checks passed" if ok else "FAILURES"))
    return ok


# ------------------------------------------------------------------------------- CLI
def _length_args(p):
    p.add_argument("--target-words", type=int, default=None, help="requested length; passes within +/- tolerance")
    p.add_argument("--min-words", type=int, default=None)
    p.add_argument("--max-words", type=int, default=None, help="hard limit, e.g. a journal's abstract limit")
    p.add_argument("--tolerance", type=float, default=0.10, help="allowed deviation from --target-words (default 0.10)")


def main(argv=None):
    T.utf8_output()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("analyze")
    a.add_argument("file")
    a.add_argument("--register", default="general")
    a.add_argument("--lang", choices=["en", "fr"], default=None, help="default: detected from the text")
    a.add_argument("--json", action="store_true")
    a.add_argument("--sentences", action="store_true")
    a.add_argument("--all", action="store_true", help="list every scored metric, not only those behind a weak dimension")
    a.add_argument("--protect", default="", help="comma-separated technical terms to exclude from repetition checks")
    a.add_argument("--calibration", default=CALIBRATION_PATH)
    a.add_argument("--waive", default="", help="comma-separated dimensions to leave out of the composite "
                   "(e.g. 'specificity' when the source has no names or numbers); reported in the output")
    a.add_argument("--source", default=None, help="source text or brief: lists its numbers and names the draft has not used")
    _length_args(a)
    c = sub.add_parser("compare")
    c.add_argument("file")
    c.add_argument("--ref", required=True)
    c.add_argument("--lang", choices=["en", "fr"], default=None)
    c.add_argument("--json", action="store_true")
    n = sub.add_parser("count")
    n.add_argument("file")
    _length_args(n)
    g = sub.add_parser("growth", help="did a longer version add information, or only words?")
    g.add_argument("old")
    g.add_argument("new")
    g.add_argument("--register", default="general")
    g.add_argument("--lang", choices=["en", "fr"], default=None)
    g.add_argument("--source", default=None, help="notes, brief or source text: sentences anchored in it count as supported")
    g.add_argument("--calibration", default=CALIBRATION_PATH)
    g.add_argument("--json", action="store_true")
    k = sub.add_parser("calibrate")
    k.add_argument("--human", required=True)
    k.add_argument("--ai", required=True)
    k.add_argument("--register", required=True)
    k.add_argument("--lang", choices=["en", "fr"], default=None)
    k.add_argument("--out", default=CALIBRATION_PATH)
    k.add_argument("--base", default="scientific", help="register whose metric definitions and guards to reuse")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    if args.cmd == "analyze":
        text = T.read_text(args.file)
        protect = [t.strip() for t in args.protect.split(",") if t.strip()]
        doc, m = analyze_text(text, protect, args.lang)
        calib = load_calibration(args.calibration)
        waive = [w.strip() for w in args.waive.split(",") if w.strip()]
        ev = score(doc, m, calib, args.register, waive, protect) if calib else None
        length = None
        if args.target_words or args.min_words or args.max_words or args.source:
            src = T.read_text(args.source) if args.source else None
            length = length_report(doc, args.target_words, args.tolerance, args.min_words, args.max_words, src)
        if args.json:
            print(json.dumps({"metrics": m, "evaluation": ev, "length": length}, indent=1, ensure_ascii=False))
        else:
            print(render(doc, m, ev, args.sentences, length, args.all))
        length_ok = not length or length["status"] in (None, "ON TARGET")
        return 0 if (ev is None or ev["gate_pass"]) and length_ok else 1
    if args.cmd == "compare":
        da, ma = analyze_text(T.read_text(args.file), lang=args.lang)
        db, mb = analyze_text(T.read_text(args.ref), lang=da.lang)
        res = compare_docs(da, ma, db, mb)
        print(json.dumps(res, indent=1, ensure_ascii=False) if args.json else render_compare(res))
        return 0
    if args.cmd == "count":
        doc = T.Doc(T.read_text(args.file))
        length = length_report(doc, args.target_words, args.tolerance, args.min_words, args.max_words)
        print("\n".join(render_length(length)).replace("## Length: ", ""))
        return 0 if length["status"] in (None, "ON TARGET") else 1
    if args.cmd == "growth":
        do = T.Doc(T.read_text(args.old), args.lang)
        dn = T.Doc(T.read_text(args.new), do.lang)
        ds = T.Doc(T.read_text(args.source), do.lang) if args.source else None
        res = growth_report(do, dn, load_calibration(args.calibration), args.register, ds)
        print(json.dumps(res, indent=1, ensure_ascii=False) if args.json else render_growth(res))
        return 1 if res["status"] == "PADDING" else 0
    if args.cmd == "calibrate":
        calibrate(args.human, args.ai, args.register, args.out, lang=args.lang, base=args.base)
        return 0
    if args.cmd == "selftest":
        return 0 if selftest() else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
