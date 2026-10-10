#!/usr/bin/env python3
"""Shared text handling for the SciHumanizer scripts (standard library only, Python 3.8+).

One definition of each unit, used by every script and both languages (English, French):

  word      a typographic word: a whitespace-delimited chunk containing a letter or digit.
            This is what a word processor counts and what "about 700 words" means. Sentence,
            paragraph and document lengths and every per-1,000-word rate use it.
  token     a linguistic token: words with clitics and elisions split (don't -> do + n't,
            l'eau -> l' + eau), numbers kept whole. Used for word lists and part-of-speech rates.
  lemma     the dictionary form of a token (studies -> study, étaient -> être). Used for
            vocabulary measures, so inflection is not mistaken for vocabulary variety.
  sentence  split on . ! ? … followed by a capital, digit or opening quote, with abbreviation
            and initial handling per language.
"""
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def utf8_output():
    """Keep printing when the console is not UTF-8. A Windows code page or a C locale would
    otherwise fail on the first character it cannot encode, and the text under analysis can hold
    any character. Piped output is written as UTF-8; on a terminal only the error mode changes."""
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def read_text(path):
    """Read a text file as UTF-8 (with or without a byte-order mark). A file that is not valid
    UTF-8 is read as Windows-1252, the usual encoding of older French and English documents, with
    a note on stderr; "-" reads standard input."""
    if path == "-":
        return sys.stdin.read()
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        sys.stderr.write("note: %s is not UTF-8; read as Windows-1252\n" % path)
        return raw.decode("cp1252", errors="replace")

LETTERS = "A-Za-zÀ-ÖØ-öø-ÿŒœÆæ"
UPPER = "A-ZÀ-ÖØ-ÞŒÆ"
WORD_CHAR_RE = re.compile(r"[0-9%s]" % LETTERS)
TOKEN_RE = re.compile(
    r"\d+(?:[.,]\d+)*\s?%%|\d+(?:[.,]\d+)*"
    r"|[%(L)s]+(?:['’][%(L)s]+)*(?:-[%(L)s0-9]+(?:['’][%(L)s]+)?)*" % {"L": LETTERS})
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F000-\U0001F2FF☀-⛿]")

_EN_HINT = set("the of and to in is that for it as with was on be by are this which from at or an not have has were".split())
_FR_HINT = set("le la les de des du et à un une est que qui dans pour pas sur au aux par ce cette ces il elle nous vous "
               "ils elles ne se sont été plus avec comme mais ou où dont leur leurs d l qu n s c".split())

_PACKS = {}


def load_markers(lang):
    """Calibrated marker words for a language (data/markers_<lang>.json, built by the calibration
    pipeline from human and AI corpora; see references/calibration.md). Empty lists if absent."""
    import json
    path = os.path.join(DATA, "markers_%s.json" % lang)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {"ai_function": [], "ai_content": [], "human_function": [], "human_content": [], "glue": []}


def pack(lang):
    """Language pack module (word lists, patterns, language-specific rules)."""
    if lang not in _PACKS:
        if HERE not in os.sys.path:
            os.sys.path.insert(0, HERE)
        _PACKS[lang] = importlib.import_module("lang_" + lang)
    return _PACKS[lang]


def detect_lang(text):
    toks = re.findall(r"[%s]+" % LETTERS, text.lower())[:4000]
    en = sum(t in _EN_HINT for t in toks)
    fr = sum(t in _FR_HINT for t in toks)
    return "fr" if fr > en * 1.15 else "en"


# ------------------------------------------------------------------------------- markdown
_APOS = re.compile("(?<=[%s])[\u2019\u02bc\u00b4\u0060\u2018](?=[%s])" % (LETTERS, LETTERS))


def _clean_inline(s, fmt):
    s = _APOS.sub("'", s)                      # typographic, acute-accent and backtick apostrophes -> '
    fmt["bold"] += len(re.findall(r"\*\*[^*]+\*\*|__[^_]+__", s))
    fmt["emoji"] += len(EMOJI_RE.findall(s))
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"(\*\*|__)(.+?)\1", r"\2", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)\*(?!\w)", r"\1", s)
    s = re.sub(r"(?<![\w_])_(?!\s)([^_]+?)_(?!\w)", r"\1", s)
    return EMOJI_RE.sub("", s)


def preprocess(text):
    """Markdown-aware split into paragraphs. Returns (paragraphs, format counts, heading texts).
    Headings, tables and code are not prose; each list item is its own paragraph flagged `list`."""
    import collections
    fmt = collections.Counter()
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                lines = lines[j + 1:]
                break
    paras, cur, in_code, headings = [], [], False, []
    prev_blank, prev_list = True, False

    def flush():
        if cur:
            text = " ".join(cur)
            ws = words(text)
            # a short line standing alone without end punctuation is a plain-text title or subheading
            if len(cur) == 1 and 0 < len(ws) <= 14 and not re.search(r"[.!?…;,»\"”)]\s*$", text):
                fmt["headings"] += 1
                fmt["plain_headings"] += 1
                headings.append(text)
            else:
                paras.append({"text": text, "list": False})
            cur.clear()

    for line in lines:
        st = line.strip()
        if st.startswith("```") or st.startswith("~~~"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            fmt["code_lines"] += 1
            continue
        if not st:
            flush()
            prev_blank, prev_list = True, False
            continue
        if re.match(r"^#{1,6}\s", st):
            flush()
            fmt["headings"] += 1
            h = re.sub(r"^#{1,6}\s+", "", st)
            headings.append(h)
            ws = [w for w in re.findall(r"[%s][%s'’-]*" % (LETTERS, LETTERS), h) if len(w) > 3]
            if len(ws) >= 2 and sum(w[0].isupper() for w in ws) / len(ws) >= 0.8:
                fmt["title_case_headings"] += 1
            prev_blank, prev_list = True, False
            continue
        if "|" in st and (st.startswith("|") or re.match(r"^[:\-| ]+$", st)):
            flush()
            fmt["table_lines"] += 1
            continue
        m = re.match(r"^([-*+•]|\d{1,2}[.)])\s+(.*)$", st)
        if m and (prev_blank or prev_list or not m.group(1)[0].isdigit() or m.group(1)[:-1] == "1"):
            prev_blank, prev_list = False, True
            flush()
            fmt["list_items"] += 1
            if re.match(r"^(\*\*|__)[^*_]{1,60}?(?:[:—–-](\*\*|__)|(\*\*|__)\s*[:—–-])", m.group(2)):
                fmt["bold_lead_items"] += 1
            paras.append({"text": _clean_inline(m.group(2), fmt), "list": True})
            continue
        if st.startswith(">"):
            st = st.lstrip("> ").strip()
        prev_blank, prev_list = False, False
        cur.append(_clean_inline(st, fmt))
    flush()
    return paras, fmt, headings


# ------------------------------------------------------------------------------- citations
_YEAR = r"(?:1[6-9]|20)\d\d[a-z]?"
_LOC = r"(?:\s*[:,]\s*(?:pp?\.?\s*)?\d+(?:\s*[-–]\s*\d+)?)?"
_NAME = r"[%s][%s'’\-]+" % (UPPER, LETTERS)
_AUTH = _NAME + r"(?:\s+(?:et al\.?|et coll\.?|and|et|&)\s*(?:%s)?)?" % _NAME
_CITE_PATTERNS = [
    re.compile(r"\s?\[\s*\d+(?:\s*[-–,;]\s*\d+)*\s*\]"),
    re.compile(r"\s?\((?:e\.g\.,?\s*|see\s+|cf\.\s*|voir\s+|p\. ex\.,?\s*)?%s,?\s+%s%s(?:\s*[;,]\s*%s,?\s+%s%s)*\)" % (
        _AUTH, _YEAR, _LOC, _AUTH, _YEAR, _LOC)),
    re.compile(r"(?<=et al\.)\s?\(%s%s\)|(?<=[%s][a-zà-ÿ])\s\(%s%s\)" % (_YEAR, _LOC, UPPER, _YEAR, _LOC)),
]


def strip_citations(text):
    """Remove citation markers: they are forced choices, not style. The fact ledger keeps them."""
    for rx in _CITE_PATTERNS:
        text = rx.sub("", text)
    return text


# ------------------------------------------------------------------------------- units
def words(s):
    """Typographic words (the unit of every length and every per-1,000 rate)."""
    return [t for t in s.split() if WORD_CHAR_RE.search(t)]


def count_breakdown(text):
    """The one word count used for every length statement in the skill: body paragraphs, list
    items and headings, counted as typographic words (what a word processor reports). Markdown
    syntax is not counted; code blocks and tables are left out and reported separately."""
    paras, fmt, headings = preprocess(text)
    body = sum(len(words(p["text"])) for p in paras if not p["list"])
    lists = sum(len(words(p["text"])) for p in paras if p["list"])
    heads = sum(len(words(h)) for h in headings)
    return {"total": body + lists + heads, "body": body, "list_items": lists, "headings": heads,
            "table_lines_excluded": fmt["table_lines"], "code_lines_excluded": fmt["code_lines"]}


def count_words(text):
    return count_breakdown(text)["total"]


def norm(s):
    """Lowercase, straight apostrophes, plain spaces: the form every phrase pattern is matched on."""
    return re.sub(r"\s+", " ", s.lower().replace("’", "'").replace("\u00a0", " ").replace("\u202f", " ")).strip()


_SENT_END = re.compile(r"(?:\.|\s?[!?…])+(?:\s?[\"'”’»)\]])*(?=\s+(?:[\"'“‘«(\[]\s?|[-–—]\s)?[%s0-9])" % UPPER)


def split_sentences(par, lang="en"):
    lp = pack(lang)
    par = re.sub(r"\s+", " ", par).strip()
    if not par:
        return []
    out, start = [], 0
    for m in _SENT_END.finditer(par):
        end = m.end()
        if m.group(0).lstrip().startswith("."):
            before = par[start:m.start()]
            last = re.search(r"([%s][%s.\-]*)$" % (LETTERS, LETTERS), before)
            if last:
                w = last.group(1).lower().rstrip(".")
                if w in lp.ABBREVIATIONS or (len(last.group(1)) == 1 and last.group(1).isupper()):
                    nxt = re.match(r"\s+[\"'“‘«(\[]?\s?([%s]+)" % LETTERS, par[end:])
                    nxt_w = nxt.group(1).lower() if nxt else ""
                    if not (w in lp.SENTENCE_FINAL_ABBREV and nxt_w in lp.SENTENCE_STARTERS):
                        continue
        out.append(par[start:end].strip())
        start = end
    tail = par[start:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if re.search(r"[%s]" % LETTERS, s)]


def raw_tokens(s):
    """Linguistic tokens before clitic splitting, apostrophes normalised."""
    return [t.replace("’", "'").replace(" ", "") for t in TOKEN_RE.findall(s)]


# ------------------------------------------------------------------------------- tagging
class Tagger:
    """Lexicon tagger: most likely reading per form (corpus-derived), suffix guesses for unknown
    words, a few context rules. Reliable for document-level rates, not for single words.
    Accuracy on held-out treebank text is recorded in references/metrics.md."""
    FUNCTION_TAGS = {"DET", "ADP", "PRON", "CCONJ", "SCONJ", "MODAL", "AUX", "TO"}

    def __init__(self, lang):
        self.lang = lang
        self.lp = pack(lang)
        self.lex = {}
        path = os.path.join(DATA, "%s_lexicon.tsv" % lang)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("#") or "\t" not in line:
                        continue
                    w, readings = line.rstrip("\n").split("\t")
                    rd = []
                    for item in readings.split(","):
                        p = item.split(":")
                        rd.append((p[0], p[1] if len(p) == 3 else None))
                    self.lex[w] = rd
        self.known = set(self.lex)

    def analyse(self, sentence):
        """sentence text -> (tokens_lower, tags, lemmas, originals). Clitics and elisions become own tokens."""
        lp = self.lp
        toks, origs = [], []
        for t in raw_tokens(sentence):
            for part in lp.split_token(t):
                toks.append(part.lower())
                origs.append(part)
        tags, lemmas = [], []
        for i, (lw, orig) in enumerate(zip(toks, origs)):
            first = (i == 0)
            fixed = lp.CLITIC_TAGS.get(lw)
            if fixed:
                tags.append(fixed[0])
                lemmas.append(fixed[1])
                continue
            if lw[0].isdigit():
                tags.append("NUM")
                lemmas.append("#")
                continue
            cands = self.lex.get(lw)
            top = cands[0][0] if cands else None
            if len(orig) >= 2 and re.match(r"^[%s][%s0-9\-]+s?$" % (UPPER, UPPER), orig) and top not in self.FUNCTION_TAGS:
                tag, lem = "ACRO", orig
            elif orig[:1].isupper() and not first and top not in self.FUNCTION_TAGS and not lp.lower_ok_capital(lw, cands):
                tag, lem = "PROPN", orig
            elif cands is None:
                tag = lp.guess_tag(orig, first, self.known)
                lem = None
            else:
                tag, lem = cands[0]
                if len(cands) > 1:
                    alt = lp.disambiguate(lw, cands, toks, tags, i, self.lex)
                    if alt is not None:
                        tag, lem = alt
            if lem is None:
                lem = lp.lemma(lw, tag, self.known)
            lem = lp.LEMMA_OVERRIDES.get(lem, lem)
            tags.append(tag)
            lemmas.append(lem)
        return toks, tags, lemmas, origs


_TAGGERS = {}


def tagger(lang):
    if lang not in _TAGGERS:
        _TAGGERS[lang] = Tagger(lang)
    return _TAGGERS[lang]


class Doc:
    """A parsed document. Sentences carry: text, words (typographic), toks (linguistic, lower),
    tags, lemmas, paragraph index, list flag, and i (1-based index among prose sentences)."""

    def __init__(self, text, lang=None):
        self.raw = text
        self.lang = lang or detect_lang(text)
        self.lp = pack(self.lang)
        self.paras_raw, self.fmt, self.headings = preprocess(text)
        tg = tagger(self.lang)
        self.paragraphs, self.list_sentences, self.sentences = [], [], []
        for pi, p in enumerate(self.paras_raw):
            sents = []
            for s in split_sentences(strip_citations(p["text"]), self.lang):
                ws = words(s)
                if not ws:
                    continue
                toks, tags, lemmas, origs = tg.analyse(s)
                sents.append({"text": s, "norm": norm(s), "words": ws, "n": len(ws), "toks": toks, "tags": tags,
                              "lemmas": lemmas, "origs": origs, "para": pi, "list": p["list"]})
            if not sents:
                continue
            if p["list"]:
                self.list_sentences.extend(sents)
            else:
                self.paragraphs.append(sents)
        for s in (s for par in self.paragraphs for s in par):
            s["i"] = len(self.sentences) + 1
            self.sentences.append(s)
        self.all_sentences = self.sentences + self.list_sentences
        self.toks = [t for s in self.all_sentences for t in s["toks"]]
        self.tags = [t for s in self.all_sentences for t in s["tags"]]
        self.lemmas = [t for s in self.all_sentences for t in s["lemmas"]]
        self.prose_text = "\n\n".join(" ".join(s["text"] for s in par) for par in self.paragraphs)
        self.all_text = self.prose_text + ("\n" + "\n".join(s["text"] for s in self.list_sentences) if self.list_sentences else "")
        self.norm_text = " ".join(s["norm"] for s in self.all_sentences)
        self.n_words = sum(s["n"] for s in self.all_sentences)   # analysed text: body + list items, citation markers removed
        self.n_tokens = len(self.toks)
        self.count = count_breakdown(text)                       # the document word count (see count_breakdown)

    def lex_lemmas(self):
        """Lemmas of alphabetic tokens (numbers and clitic markers dropped): the vocabulary sequence."""
        return [l.lower() for l, t in zip(self.lemmas, self.tags) if t != "NUM" and l and l[0].isalpha()]

    def window_text(self, max_words, start_sentence=0):
        """Text of whole sentences from prose sentence `start_sentence` on, as close to max_words words
        as whole sentences allow (within half a sentence), paragraph breaks kept.
        Returns (text, words, index of the next sentence)."""
        out, cur, n, para, k = [], [], 0, None, start_sentence
        while k < len(self.sentences):
            s = self.sentences[k]
            if n > 0 and n + s["n"] / 2.0 > max_words:      # stopping here is closer to the target than going on
                break
            if para is not None and s["para"] != para and cur:
                out.append(" ".join(cur))
                cur = []
            para = s["para"]
            cur.append(s["text"])
            n += s["n"]
            k += 1
        if cur:
            out.append(" ".join(cur))
        return "\n\n".join(out), n, k

    def truncated(self, max_words, start_sentence=0):
        """A new Doc of at most max_words words (whole sentences) starting at a given sentence."""
        return Doc(self.window_text(max_words, start_sentence)[0], self.lang)
