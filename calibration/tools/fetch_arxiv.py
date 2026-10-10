#!/usr/bin/env python3
"""Fetch 2017-2019 arXiv abstracts (pre-ChatGPT human scientific prose)."""
import json, os, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

from paths import WS
OUT = os.path.join(WS, "corpora", "arxiv")
os.makedirs(OUT, exist_ok=True)
NS = {"a": "http://www.w3.org/2005/Atom"}
CATS = ["cs.CL", "cs.LG", "cs.CV", "astro-ph.GA", "cond-mat.mtrl-sci",
        "q-bio.NC", "stat.ME", "econ.EM", "physics.soc-ph", "eess.SP"]
PER = 14

index = {}
for i, cat in enumerate(CATS):
    year = 2017 + (i % 3)
    q = f"cat:{cat} AND submittedDate:[{year}03010000 TO {year}10312359]"
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "start": 0, "max_results": PER * 2, "sortBy": "relevance"})
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(url, timeout=90).read()
            break
        except Exception:
            time.sleep(5 + 5 * attempt)
    root = ET.fromstring(raw)
    n = 0
    for e in root.findall("a:entry", NS):
        if n >= PER:
            break
        aid = e.find("a:id", NS).text.rsplit("/", 1)[-1]
        title = re.sub(r"\s+", " ", e.find("a:title", NS).text).strip()
        summ = re.sub(r"\s+", " ", e.find("a:summary", NS).text).strip()
        if len(summ.split()) < 120 or "$" in summ:
            continue
        fn = re.sub(r"[^A-Za-z0-9.]+", "_", aid)
        with open(os.path.join(OUT, f"{fn}.txt"), "w") as f:
            f.write(summ + "\n")
        index[fn] = {"cat": cat, "year": year, "title": title, "words": len(summ.split())}
        n += 1
    print(cat, year, n)
    time.sleep(3.5)
json.dump(index, open(os.path.join(OUT, "index.json"), "w"), indent=1)
print("abstracts:", len(index))
