#!/usr/bin/env python3
"""Fetch pre-2020 human text for the French registers and for a modern English general register.

  fetch_corpora.py conversation N_IDS          The Conversation, articles of 2015-09..2019-12 by sampled id
                                                (French and English are both kept; translations are skipped)
  fetch_corpora.py wikinews LANG N             Wikinews articles dated 2012..2019, >= 250 words
  fetch_corpora.py wikipedia LANG N            featured articles as they stood on 2019-12-31
  fetch_corpora.py openedition N               French journal articles 2012..2019: full text + résumé (OAI-PMH + HTML)
  fetch_corpora.py hal N                       French abstracts 2012..2019 from HAL, spread over domains
  fetch_corpora.py pmcfr N                     French open-access PMC articles 2015..2019 (Introduction, Discussion)

Everything is cached under corpora/raw2/ and written as plain text under corpora/<lang>/<source>/ with an
index.json (title, date, url, words...). Requests are spaced out; rerunning continues where it stopped.
"""
import hashlib, html, json, os, random, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

from paths import WS, contact
C = os.path.join(WS, "corpora")
RAW = os.path.join(C, "raw2")
UA = None      # set when the tool runs: it carries the contact address of whoever runs it
import textcore as T  # noqa: E402

random.seed(20261009)


def get(url, cache_key=None, pause=0.6, tries=3, accept=None):
    """GET with an on-disk cache. Returns bytes, or None on a permanent error (404, 403, 410)."""
    path = None
    if cache_key:
        path = os.path.join(RAW, cache_key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            return open(path, "rb").read()
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept or "*/*"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            time.sleep(pause)
            if path:
                open(path, "wb").write(data)
            return data
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410, 451):
                time.sleep(pause)
                if path:
                    open(path, "wb").write(b"")
                return None
            time.sleep(3 + 4 * i)
        except Exception:
            time.sleep(3 + 4 * i)
    return None


def strip_tags(s):
    s = re.sub(r"<(script|style|figure|figcaption|table|sup|math|noscript)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = s.replace("­", "")
    return re.sub(r"\s+", " ", s).strip()


def save(lang, source, name, paras, meta, index):
    d = os.path.join(C, lang, source)
    os.makedirs(d, exist_ok=True)
    text = "\n\n".join(paras) + "\n"
    open(os.path.join(d, name + ".txt"), "w", encoding="utf-8").write(text)
    meta = dict(meta, words=len(text.split()))
    index[name] = meta
    json.dump(index, open(os.path.join(d, "index.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return meta["words"]


def load_index(lang, source):
    p = os.path.join(C, lang, source, "index.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


# ------------------------------------------------------------------------------- The Conversation
TRANSLATED = re.compile(r"version originale de cet article|traduit (?:de l[’']anglais|par)|traduction\s*:|"
                        r"originally published in (?:french|spanish|indonesian|portuguese)|translated (?:from|by)|"
                        r"this article was translated|publié en anglais|read (?:this|the) (?:article|story) in|"
                        r"lire cet article en|leer en español", re.I)


def conversation(n_ids):
    idx = {"fr": load_index("fr", "conversation"), "en": load_index("en", "conversation")}
    ids = random.sample(range(46000, 129500), n_ids)
    kept = {"fr": 0, "en": 0}
    for k, aid in enumerate(ids):
        raw = get("https://theconversation.com/a-%d" % aid, "conversation/%d.html" % aid, accept="text/html")
        if not raw:
            continue
        s = raw.decode("utf-8", "ignore")
        m = re.search(r'<meta name="pubdate" content="(\d{8})"', s)
        i = s.find('itemprop="articleBody"')
        if not m or i < 0 or not ("20150901" <= m.group(1) <= "20191231"):
            continue
        body = s[i:]
        for end in ('class="grid-ten', "<footer", 'class="content-authors', 'id="comments"', 'class="article-footer'):
            j = body.find(end)
            if j > 0:
                body = body[:j]
        if TRANSLATED.search(strip_tags(body)[-900:]) or TRANSLATED.search(strip_tags(body)[:600]):
            continue
        body = re.sub(r"<blockquote\b.*?</blockquote>", " ", body, flags=re.S)
        paras = [strip_tags(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", body, flags=re.S)]
        paras = [p for p in paras if len(p.split()) >= 12 and not re.match(r"^(?:Read more|À lire aussi|Lire aussi|Lire la suite)\b", p)
                 and not re.match(r"^\[.*\]$", p) and not re.search(r"newsletter|Abonnez-vous|Sign up for", p)]
        text = "\n\n".join(paras)
        if len(text.split()) < 450:
            continue
        lang = T.detect_lang(text)
        toks = re.findall(r"[a-zà-ÿ]+", text.lower())[:3000]
        en_hits, fr_hits = sum(w in T._EN_HINT for w in toks), sum(w in T._FR_HINT for w in toks)
        if max(en_hits, fr_hits) < 0.15 * len(toks) or min(en_hits, fr_hits) > 0.55 * max(en_hits, fr_hits):
            continue                                   # Spanish, Indonesian, Portuguese ... editions
        t = re.search(r"<title>(.*?)</title>", s, flags=re.S)
        title = strip_tags(t.group(1)) if t else ""
        save(lang, "conversation", "tc_%d" % aid, paras, {"id": aid, "date": m.group(1), "title": title,
                                                          "url": "https://theconversation.com/a-%d" % aid}, idx[lang])
        kept[lang] += 1
        if k % 50 == 0:
            print("conversation %d/%d ids, kept %s" % (k, n_ids, kept), flush=True)
    print("conversation done: kept", kept, "| index sizes", {k: len(v) for k, v in idx.items()})


# ------------------------------------------------------------------------------- Wikimedia
MONTHS = {"fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                 "novembre", "décembre"],
          "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"]}


def mw(host, **params):
    params.update(format="json", formatversion="2")
    key = "mw/%s/%s.json" % (host, hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest())
    raw = get("https://%s/w/api.php?%s" % (host, urllib.parse.urlencode(params)), key, pause=0.35)
    try:
        return json.loads(raw) if raw else {}
    except ValueError:
        return {}


def wiki_paragraphs(htm):
    htm = re.sub(r"<(table|style|script|figure|blockquote|ol|ul|dl)\b.*?</\1>", " ", htm, flags=re.S | re.I)
    htm = re.sub(r'<div[^>]*class="[^"]*(?:infobox|navbox|thumb|reflist|hatnote|bandeau|metadata|noprint|toc)[^"]*".*?</div>', " ", htm, flags=re.S)
    htm = re.sub(r'<sup\b.*?</sup>', "", htm, flags=re.S)
    htm = re.sub(r'<span class="mw-editsection".*?</span>\s*</span>', "", htm, flags=re.S)
    paras = [strip_tags(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", htm, flags=re.S)]
    paras = [re.sub(r"\[\s*(?:\d+|réf\.[^\]]*|citation needed|note \d+|N \d+)\s*\]", "", p) for p in paras]
    return [re.sub(r"\s+([,.;])", r"\1", p).strip() for p in paras if len(p.split()) >= 12]


def wikinews(lang, n):
    host = "%s.wikinews.org" % lang
    idx = load_index(lang, "wikinews")
    days = [(y, m, d) for y in range(2012, 2020) for m in range(1, 13) for d in range(1, 29)]
    random.shuffle(days)
    for (y, m, d) in days:
        if len(idx) >= n:
            break
        cat = ("Catégorie:%d %s %d" % (d, MONTHS["fr"][m - 1], y)) if lang == "fr" else \
              ("Category:%s %d, %d" % (MONTHS["en"][m - 1], d, y))
        res = mw(host, action="query", list="categorymembers", cmtitle=cat, cmlimit="20", cmnamespace="0")
        for page in res.get("query", {}).get("categorymembers", []):
            name = "wn_%d" % page["pageid"]
            if name in idx:
                continue
            pr = mw(host, action="parse", pageid=str(page["pageid"]), prop="text", disablelimitreport="1", disableeditsection="1")
            paras = wiki_paragraphs(pr.get("parse", {}).get("text", ""))
            paras = [re.sub(r"^(?:Publié le \d{1,2}(?:er)? \S+ \d{4}|\w+day, \w+ \d{1,2}, \d{4})\s*", "", p) for p in paras]
            paras = [p for p in paras if len(p.split()) >= 12 and
                     not re.match(r"^(?:Cet article|Sources?\b|Voir aussi|This article|Have an opinion|Share this)", p)]
            text = "\n\n".join(paras)
            if len(text.split()) < 250 or T.detect_lang(text) != lang:
                continue
            save(lang, "wikinews", name, paras, {"title": page["title"], "date": "%04d%02d%02d" % (y, m, d)}, idx)
            if len(idx) % 20 == 0:
                print("wikinews %s: %d" % (lang, len(idx)), flush=True)
    print("wikinews %s done: %d" % (lang, len(idx)))


def wikipedia(lang, n):
    host = "%s.wikipedia.org" % lang
    idx = load_index(lang, "wikipedia")
    cat = "Catégorie:Article de qualité" if lang == "fr" else "Category:Featured articles"
    titles, cont = [], None
    while len(titles) < 6000:
        kw = dict(action="query", list="categorymembers", cmtitle=cat, cmlimit="500", cmnamespace="0")
        if cont:
            kw["cmcontinue"] = cont
        res = mw(host, **kw)
        titles += [p["title"] for p in res.get("query", {}).get("categorymembers", [])]
        cont = res.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    random.shuffle(titles)
    for title in titles:
        if len(idx) >= n:
            break
        rv = mw(host, action="query", prop="revisions", titles=title, rvstart="2019-12-31T23:59:59Z", rvlimit="1", rvprop="ids|timestamp")
        pages = rv.get("query", {}).get("pages", [])
        revs = pages[0].get("revisions") if pages else None
        if not revs:
            continue
        name = "wp_%d" % pages[0]["pageid"]
        if name in idx:
            continue
        pr = mw(host, action="parse", oldid=str(revs[0]["revid"]), prop="text", disablelimitreport="1", disableeditsection="1")
        paras = wiki_paragraphs(pr.get("parse", {}).get("text", ""))
        # skip the lead (a summary) and keep running prose from the body, up to about 1,800 words
        body, nw = [], 0
        for p in paras[3:]:
            if nw > 1800:
                break
            body.append(p)
            nw += len(p.split())
        if nw < 600 or T.detect_lang(" ".join(body)) != lang:
            continue
        save(lang, "wikipedia", name, body, {"title": title, "revid": revs[0]["revid"], "date": revs[0]["timestamp"][:10]}, idx)
        if len(idx) % 20 == 0:
            print("wikipedia %s: %d" % (lang, len(idx)), flush=True)
    print("wikipedia %s done: %d" % (lang, len(idx)))


# ------------------------------------------------------------------------------- OpenEdition (French journals)
def openedition(n):
    idx = load_index("fr", "openedition")
    absidx = load_index("fr", "openedition_abs")
    days = [(y, m, d) for y in range(2012, 2020) for m in range(1, 13) for d in (3, 9, 15, 21, 27)]
    random.shuffle(days)
    per_journal = {}
    for v in idx.values():
        per_journal[v["journal"]] = per_journal.get(v["journal"], 0) + 1
    for (y, m, d) in days:
        if len(idx) >= n:
            break
        frm = "%04d-%02d-%02d" % (y, m, d)
        until = "%04d-%02d-%02d" % (y, m, min(d + 3, 28))
        raw = get("https://oai.openedition.org/?verb=ListRecords&metadataPrefix=oai_dc&set=journals&from=%s&until=%s" % (frm, until),
                  "openedition/oai_%s.xml" % frm, pause=1.0)
        if not raw:
            continue
        recs = re.findall(r"<record>(.*?)</record>", raw.decode("utf-8", "ignore"), flags=re.S)
        random.shuffle(recs)
        for r in recs:
            if len(idx) >= n:
                break
            f = lambda tag: [html.unescape(x).strip() for x in re.findall(r"<dc:%s[^>]*>(.*?)</dc:%s>" % (tag, tag), r, flags=re.S)]  # noqa: E731
            if not ({"fr", "fre"} & set(f("language"))) or "info:eu-repo/semantics/openAccess" not in f("rights"):
                continue
            if not any(t in ("article",) for t in f("type")):
                continue
            url = next((u for u in f("identifier") if u.startswith("https://journals.openedition.org/")), None)
            date = (f("date") or [""])[0][:10]
            if not url or not ("2012" <= date[:4] <= "2019"):
                continue
            journal = url.split("/")[3]
            if per_journal.get(journal, 0) >= 3:
                continue
            name = "oe_%s_%s" % (journal, url.rstrip("/").split("/")[-1])
            if name in idx:
                continue
            title = (f("title") or [""])[0]
            abstracts = [strip_tags(a) for a in f("description")]
            fr_abs = next((a for a in abstracts if len(a.split()) >= 100 and T.detect_lang(a) == "fr"), None)
            page = get(url, "openedition/%s.html" % name, pause=1.2, accept="text/html")
            if not page:
                continue
            s = page.decode("utf-8", "ignore")
            i = s.find('id="text"')
            body = s[i:] if i > 0 else s
            for end in ('id="notes"', 'id="bibliography"', 'id="quotation"', 'id="annexes"'):
                j = body.find(end)
                if j > 0:
                    body = body[:j]
            body = re.sub(r'<a class="footnotecall".*?</a>', "", body, flags=re.S)
            body = re.sub(r'<span class="paranumber">.*?</span>', "", body, flags=re.S)
            parts = re.split(r'(<h[1-3] class="texte"[^>]*>.*?</h[1-3]>)', body, flags=re.S)
            out, section = [], "(début)"
            for part in parts:
                if part.startswith("<h"):
                    section = strip_tags(part)
                    out.append("## " + section)
                    continue
                for p in re.findall(r'<p class="texte"[^>]*>(.*?)</p>', part, flags=re.S):
                    t = strip_tags(p)
                    if len(t.split()) >= 12:
                        out.append(t)
            prose = [p for p in out if not p.startswith("## ")]
            if sum(len(p.split()) for p in prose) < 1500 or T.detect_lang(" ".join(prose[:12])) != "fr":
                continue
            save("fr", "openedition", name, out, {"title": title, "journal": journal, "date": date, "url": url,
                                                  "abstract": fr_abs or ""}, idx)
            per_journal[journal] = per_journal.get(journal, 0) + 1
            if fr_abs and 120 <= len(fr_abs.split()) <= 400:
                save("fr", "openedition_abs", name, [fr_abs], {"title": title, "journal": journal, "date": date}, absidx)
            if len(idx) % 10 == 0:
                print("openedition: %d articles, %d journals, %d abstracts" % (len(idx), len(per_journal), len(absidx)), flush=True)
    print("openedition done: %d articles from %d journals; abstracts %d" % (len(idx), len(per_journal), len(absidx)))


# ------------------------------------------------------------------------------- HAL (French abstracts)
HAL_DOMAINS = ["shs", "sdv", "info", "spi", "phys", "sde", "math", "chim", "sdu", "scco", "stat", "qfin"]


def hal(n):
    idx = load_index("fr", "hal")
    per = max(4, n // len(HAL_DOMAINS) + 2)
    for dom in HAL_DOMAINS:
        got = sum(1 for v in idx.values() if v["domain"] == dom)
        for attempt in range(8):
            if got >= per:
                break
            start = random.randint(0, 1500)
            q = urllib.parse.urlencode({"q": "*:*", "rows": "60", "start": str(start), "wt": "json",
                                        "fl": "halId_s,fr_title_s,fr_abstract_s,producedDateY_i,docType_s",
                                        "sort": "producedDate_tdate desc"}) + \
                "&fq=" + urllib.parse.quote("language_s:fr") + "&fq=" + urllib.parse.quote("primaryDomain_s:%s*" % dom) + \
                "&fq=" + urllib.parse.quote("docType_s:(ART OR THESE OR COMM)") + \
                "&fq=" + urllib.parse.quote("producedDateY_i:[2012 TO 2019]") + "&fq=" + urllib.parse.quote("fr_abstract_s:[* TO *]")
            raw = get("https://api.archives-ouvertes.fr/search/?" + q, "hal/%s_%d.json" % (dom, start), pause=0.8)
            if not raw:
                continue
            for doc in json.loads(raw).get("response", {}).get("docs", []):
                if got >= per:
                    break
                ab = re.sub(r"\s+", " ", (doc.get("fr_abstract_s") or [""])[0]).strip()
                name = "hal_" + doc["halId_s"].replace("-", "_")
                if name in idx or not (140 <= len(ab.split()) <= 380) or T.detect_lang(ab) != "fr":
                    continue
                if re.search(r"\$|\\[a-z]+\{|<[a-z]+>", ab):       # LaTeX or markup
                    continue
                save("fr", "hal", name, [ab], {"title": (doc.get("fr_title_s") or [""])[0], "domain": dom,
                                               "year": doc.get("producedDateY_i"), "type": doc.get("docType_s")}, idx)
                got += 1
        print("hal %s: %d" % (dom, got), flush=True)
    print("hal done:", len(idx))


# ------------------------------------------------------------------------------- PMC (French)
def pmcfr(n):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    argv, sys.argv = sys.argv, sys.argv[:1]
    import fetch_pmc as P
    sys.argv = argv
    idx = load_index("fr", "pmc")
    q = urllib.parse.urlencode({"db": "pmc", "term": "fre[la] AND open access[filter] AND 2015:2019[dp]",
                                "retmax": "2400", "retmode": "json"})
    ids = json.loads(get(P.EUTILS + "esearch.fcgi?" + q, "pmcfr/esearch.json"))["esearchresult"]["idlist"]
    random.shuffle(ids)
    per_journal = {}
    for v in idx.values():
        per_journal[v["journal"]] = per_journal.get(v["journal"], 0) + 1
    arts = len({k.split("_")[0] for k in idx})
    for pid in ids:
        if arts >= n:
            break
        if any(k.startswith("PMC%s_" % pid) for k in idx):
            continue
        raw = get(P.EUTILS + "efetch.fcgi?" + urllib.parse.urlencode({"db": "pmc", "id": pid}), "pmcfr/%s.xml" % pid, pause=0.4)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue
        art = root.find("article")
        if art is None or art.find("body") is None:
            continue
        meta = art.find("front/article-meta")
        jn = art.find("front/journal-meta/journal-title-group/journal-title")
        journal = (jn.text or "") if jn is not None else ""
        if per_journal.get(journal, 0) >= max(12, 2 * n // 3):
            continue
        tt = meta.find("title-group/article-title") if meta is not None else None
        title = P.text_of(tt) if tt is not None else ""
        abstract = ""
        for ab in (meta.findall("abstract") + meta.findall("trans-abstract")) if meta is not None else []:
            t = " ".join(P.paragraphs(ab)) or P.text_of(ab)
            if len(t.split()) >= 60 and T.detect_lang(t) == "fr":
                abstract = t
                break
        found = {}
        for sec in art.find("body").findall("sec"):
            k = P.sec_kind(sec)
            if k and k not in found:
                ps = P.paragraphs(sec)
                if sum(len(p.split()) for p in ps) >= 250 and T.detect_lang(" ".join(ps)) == "fr":
                    found[k] = ps
        if not found:
            continue
        yr = min([int(pd.find("year").text) for pd in meta.findall("pub-date") if pd.find("year") is not None and (pd.find("year").text or "").isdigit()] or [0])
        if not (2015 <= yr <= 2019):
            continue
        for k, ps in found.items():
            save("fr", "pmc", "PMC%s_%s" % (pid, k), ps, {"title": title, "journal": journal, "year": yr, "abstract": abstract,
                                                         "section": k}, idx)
        per_journal[journal] = per_journal.get(journal, 0) + 1
        arts += 1
        if arts % 10 == 0:
            print("pmcfr: %d articles %s" % (arts, dict(sorted(per_journal.items(), key=lambda kv: -kv[1])[:6])), flush=True)
    print("pmcfr done: %d articles, %d section files" % (arts, len(idx)))


if __name__ == "__main__":
    UA = "SciHumanizer-corpus/1.0 (research sampling of pre-2020 text; %s)" % contact()
    cmd = sys.argv[1]
    if cmd == "conversation":
        conversation(int(sys.argv[2]))
    elif cmd == "wikinews":
        wikinews(sys.argv[2], int(sys.argv[3]))
    elif cmd == "wikipedia":
        wikipedia(sys.argv[2], int(sys.argv[3]))
    elif cmd == "openedition":
        openedition(int(sys.argv[2]))
    elif cmd == "hal":
        hal(int(sys.argv[2]))
    elif cmd == "pmcfr":
        pmcfr(int(sys.argv[2]))
