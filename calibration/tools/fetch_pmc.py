#!/usr/bin/env python3
"""Fetch pre-2020 open-access PMC articles and extract Introduction/Discussion prose.

Output: corpora/pmc/<pmcid>_{intro,discussion}.txt  and corpora/pmc/index.json
(title, journal, year, abstract) used later to build topic-matched AI prompts.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

from paths import WS
OUT = os.path.join(WS, "corpora", "pmc")
os.makedirs(OUT, exist_ok=True)

TOPICS = [
    "neuroscience", "ecology", "epidemiology", "genomics", "microbiology",
    "psychology", "materials", "climate change", "oncology", "public health",
    "agriculture", "immunology", "cardiology", "education",
]
PER_TOPIC = int(sys.argv[1]) if len(sys.argv) > 1 else 6
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return r.read()
        except Exception as e:  # network hiccup / 429
            time.sleep(2 + 3 * i)
    raise RuntimeError("failed: " + url)


def text_of(el):
    """Flatten an element's text, dropping citations, formulas, tables, figures."""
    drop = {"xref", "inline-formula", "disp-formula", "table-wrap", "fig",
            "tex-math", "mml:math", "{http://www.w3.org/1998/Math/MathML}math",
            "supplementary-material", "ext-link"}
    parts = []

    def walk(e):
        tag = e.tag if isinstance(e.tag, str) else ""
        if tag in drop or tag.endswith("}math"):
            if e.tail:
                parts.append(e.tail)
            return
        if e.text:
            parts.append(e.text)
        for c in e:
            walk(c)
        if e.tail:
            parts.append(e.tail)

    if el.text:
        parts.append(el.text)
    for c in el:
        walk(c)
    s = "".join(parts)
    # clean citation debris: "[ ]", "( )", "[, ]", "(; )", "–" leftovers
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\[\s*[,;–\-\s]*\]", "", s)
    s = re.sub(r"\(\s*(?:see\s+)?(?:(?:Supplementary\s+)?(?:Figs?\.?|Figures?|Tables?|Additional file \d*|Appendix)\s*)?[A-Za-z]?[,;–\-\s]*\)", "", s)
    s = re.sub(r"\(\s*[,;–\-\s]*\)", "", s)
    s = re.sub(r"(?:\s*[,–—\-]\s*)+(?=[.;:!?)])", "", s)
    s = re.sub(r"(?:,\s*){2,}", ", ", s)
    s = re.sub(r"\s+([,.;:])", r"\1", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


def sec_kind(sec):
    st = (sec.get("sec-type") or "").lower()
    title_el = sec.find("title")
    title = (title_el.text or "").lower() if title_el is not None else ""
    if "intro" in st or re.search(r"\b(introduction|background)\b", title):
        return "intro"
    if "discussion" in st or re.search(r"\bdiscussion\b", title):
        return "discussion"
    return None


def paragraphs(sec):
    out = []
    skip = set()
    for tag in ("fig", "table-wrap", "caption", "boxed-text", "supplementary-material", "fn", "list"):
        for box in sec.iter(tag):
            for p in box.iter("p"):
                skip.add(id(p))
    for p in sec.iter("p"):
        if id(p) in skip:
            continue
        t = text_of(p)
        if len(t.split()) >= 12:
            out.append(t)
    return out


def main():
    index = {}
    idx_path = os.path.join(OUT, "index.json")
    if os.path.exists(idx_path):
        index = json.load(open(idx_path))
    for topic in TOPICS:
        term = f'{topic}[Title/Abstract] AND open access[filter] AND 2015:2019[pdat] AND "research-article"[filter]'
        q = urllib.parse.urlencode({"db": "pmc", "term": term, "retmax": PER_TOPIC * 4,
                                    "retmode": "json", "sort": "relevance"})
        try:
            ids = json.loads(get(EUTILS + "esearch.fcgi?" + q))["esearchresult"]["idlist"]
        except Exception:
            ids = []
        if not ids:
            term = f'{topic}[Title/Abstract] AND open access[filter] AND 2015:2019[pdat]'
            q = urllib.parse.urlencode({"db": "pmc", "term": term, "retmax": PER_TOPIC * 4,
                                        "retmode": "json", "sort": "relevance"})
            ids = json.loads(get(EUTILS + "esearch.fcgi?" + q))["esearchresult"]["idlist"]
        time.sleep(0.5)
        got = 0
        for pid in ids:
            if got >= PER_TOPIC:
                break
            if pid in index:
                got += 1
                continue
            try:
                cache = os.path.join(OUT, "raw", pid + ".xml")
                os.makedirs(os.path.dirname(cache), exist_ok=True)
                if os.path.exists(cache):
                    raw = open(cache, "rb").read()
                else:
                    raw = get(EUTILS + "efetch.fcgi?" + urllib.parse.urlencode({"db": "pmc", "id": pid}))
                    open(cache, "wb").write(raw)
                root = ET.fromstring(raw)
            except Exception as e:
                print("skip", pid, e, file=sys.stderr)
                continue
            time.sleep(0.4)
            art = root.find("article")
            if art is None:
                continue
            if art.get("article-type") not in (None, "research-article"):
                continue
            lang = art.get("{http://www.w3.org/XML/1998/namespace}lang", "en")
            if lang and not lang.startswith("en"):
                continue
            meta = art.find("front/article-meta")
            title = text_of(meta.find("title-group/article-title")) if meta is not None and meta.find("title-group/article-title") is not None else ""
            jn = art.find("front/journal-meta/journal-title-group/journal-title")
            journal = jn.text if jn is not None else ""
            yr = None
            for pd in (meta.findall("pub-date") if meta is not None else []):
                y = pd.find("year")
                if y is not None and y.text and y.text.isdigit():
                    yr = int(y.text) if yr is None else min(yr, int(y.text))
            if yr is None or yr > 2019:
                continue
            ab = meta.find("abstract") if meta is not None else None
            abstract = " ".join(paragraphs(ab)) if ab is not None else ""
            if not abstract and ab is not None:
                abstract = text_of(ab)
            body = art.find("body")
            if body is None:
                continue
            found = {}
            for sec in body.findall("sec"):
                k = sec_kind(sec)
                if k and k not in found:
                    ps = paragraphs(sec)
                    if sum(len(p.split()) for p in ps) >= 250:
                        found[k] = ps
            if not found:
                continue
            for k, ps in found.items():
                with open(os.path.join(OUT, f"PMC{pid}_{k}.txt"), "w") as f:
                    f.write("\n\n".join(ps) + "\n")
            index[pid] = {"topic": topic, "title": title, "journal": journal, "year": yr,
                          "abstract": abstract, "sections": sorted(found)}
            got += 1
            print(f"[{topic}] PMC{pid} {yr} {sorted(found)} {title[:70]}")
            json.dump(index, open(idx_path, "w"), indent=1)
    print("articles:", len(index))


if __name__ == "__main__":
    main()
