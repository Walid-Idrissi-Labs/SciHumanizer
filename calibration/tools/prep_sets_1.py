#!/usr/bin/env python3
"""English human sets from PubMed Central, arXiv and the Brown corpus, and the first prompt list.

Run once, after fetch_pmc.py, fetch_arxiv.py and build_brown.py:

  calib/human/scientific/        PMC 2015-2019 Introduction and Discussion sections (250 to 800 words)
  calib/human/scientific_brown/  Brown "learned" (1961) excerpts, a second human set used as a check
  calib/human/abstract/          arXiv 2017-2019 abstracts
  calib/human/general/           Brown informative genres (news, editorial, reviews, religion, hobbies, lore,
                                 belles_lettres, government), up to 800 words
  prompts_1.json                 topic-matched requests for the model under study (no style instructions);
                                 kept if it exists, because generated texts depend on it (--force rebuilds it)
"""
import glob, json, os, random, re, sys

from paths import WS
C = os.path.join(WS, "corpora")
OUT = os.path.join(WS, "calib", "human")
random.seed(11)
STOP = set("the of and to a in is that for it as with was on be by are this which from at or an not have has were".split())


def english(t):
    w = re.findall(r"[a-z]+", t.lower())
    return w and sum(x in STOP for x in w) / len(w) > 0.22


def trunc(text, maxw=800, minw=250):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out, n = [], 0
    for p in paras:
        k = len(p.split())
        if out and n + k > maxw:
            break
        out.append(p)
        n += k
    if n > maxw * 1.4:  # single giant paragraph: cut at sentence boundary
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", " ".join(out))
        acc, n = [], 0
        for s in sents:
            if n + len(s.split()) > maxw and acc:
                break
            acc.append(s)
            n += len(s.split())
        out = [" ".join(acc)]
    return ("\n\n".join(out) + "\n") if n >= minw else None


def put(reg, name, text):
    d = os.path.join(OUT, reg)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, name), "w", encoding="utf-8").write(text)


# PMC
pmc_idx = json.load(open(os.path.join(C, "pmc", "index.json"), encoding="utf-8"))
kept = {}
for fp in sorted(glob.glob(os.path.join(C, "pmc", "*.txt"))):
    t = open(fp, encoding="utf-8").read()
    if not english(t):
        continue
    tt = trunc(t)
    if tt:
        name = os.path.basename(fp)
        put("scientific", name, tt)
        kept[name] = True
# Brown
for genre_dir in glob.glob(os.path.join(C, "brown_txt", "*")):
    g = os.path.basename(genre_dir)
    reg = "scientific_brown" if g == "learned" else (
        "general" if g in ("news", "editorial", "reviews", "religion", "hobbies", "lore", "belles_lettres", "government") else None)
    if not reg:
        continue
    for fp in glob.glob(os.path.join(genre_dir, "*.txt")):
        tt = trunc(open(fp, encoding="utf-8").read())
        if tt:
            put(reg, g + "_" + os.path.basename(fp), tt)
# arXiv
ax_idx = json.load(open(os.path.join(C, "arxiv", "index.json"), encoding="utf-8"))
for fp in glob.glob(os.path.join(C, "arxiv", "*.txt")):
    t = open(fp, encoding="utf-8").read().strip()
    if len(t.split()) >= 150:
        put("abstract", os.path.basename(fp), t + "\n")

# ---------------- prompts for the model under study (topic-matched, no style instructions)
prompts = []
arts = [(pid, v) for pid, v in pmc_idx.items() if v.get("abstract") and len(v["abstract"].split()) > 80
        and english(v["abstract"]) and v.get("title")]
random.shuffle(arts)
n_intro = n_disc = 0
for pid, v in arts:
    title = re.sub(r"\s+", " ", v["title"]).strip()
    ab = re.sub(r"\s+", " ", v["abstract"]).strip()
    if "intro" in v["sections"] and n_intro < 16:
        prompts.append({"id": "sci_intro_PMC%s" % pid, "register": "scientific",
                        "prompt": "I'm writing a research paper titled \"%s\" for %s. Here is the abstract:\n\n%s\n\n"
                                  "Please draft the Introduction section (about 700 words). Write it as plain paragraphs, "
                                  "without headings and without reference citations." % (title, v["journal"] or "a peer-reviewed journal", ab)})
        n_intro += 1
    elif "discussion" in v["sections"] and n_disc < 14:
        prompts.append({"id": "sci_disc_PMC%s" % pid, "register": "scientific",
                        "prompt": "I'm writing a research paper titled \"%s\" for %s. Here is the abstract:\n\n%s\n\n"
                                  "Please draft the Discussion section (about 700 words) based on these findings. Write it as "
                                  "plain paragraphs, without headings and without reference citations." % (title, v["journal"] or "a peer-reviewed journal", ab)})
        n_disc += 1
ax = list(ax_idx.items())
random.shuffle(ax)
FIELD = {"cs.CL": "computational linguistics", "cs.LG": "machine learning", "cs.CV": "computer vision",
         "astro-ph.GA": "astrophysics", "cond-mat.mtrl-sci": "materials science", "q-bio.NC": "computational neuroscience",
         "stat.ME": "statistics", "econ.EM": "econometrics", "physics.soc-ph": "physics and society", "eess.SP": "signal processing"}
for fn, v in ax[:20]:
    prompts.append({"id": "abs_" + fn, "register": "abstract",
                    "prompt": "Write the abstract (about 200 words) for a %s paper titled \"%s\"." % (FIELD.get(v["cat"], "research"), v["title"])})
GENERAL = [
    "Write a local news article (about 600 words) reporting that the city council of a mid-sized town voted 5-4 to replace a downtown parking lot with a public park, including reactions from residents and business owners.",
    "Write a news article (about 600 words) about a regional hospital that has cut emergency-room wait times by redesigning how nurses triage patients.",
    "Write a news report (about 600 words) on a university study finding that four-day school weeks in rural districts had mixed effects on student test scores.",
    "Write a news article (about 600 words) about a small coastal fishing town dealing with the collapse of its lobster catch.",
    "Write an opinion column (about 600 words) arguing that cities should stop building new highways.",
    "Write an op-ed (about 600 words) arguing that high schools should teach personal finance as a required course.",
    "Write an editorial (about 600 words) on whether remote work is good or bad for young employees early in their careers.",
    "Write an opinion piece (about 600 words) arguing against banning smartphones in schools.",
    "Write a customer review (about 400 words) of a car rental experience that went badly: the company didn't have the full-size car we had reserved, the staff blamed us, and the car they gave us barely fit our baby seat.",
    "Write a review (about 600 words) of a new neighborhood Italian restaurant that has great pasta but slow, disorganized service.",
    "Write a book review (about 600 words) of a popular-science book about the history of vaccines.",
    "Write a review (about 600 words) of a mid-range pair of wireless noise-cancelling headphones after two months of daily use.",
    "Write an article (about 600 words) explaining how to start a vegetable garden on a small apartment balcony.",
    "Write a guide (about 600 words) for beginners on how to restore an old wooden chair.",
    "Write an article (about 600 words) for amateur photographers on how to take better photos at night.",
    "Write a how-to piece (about 600 words) on training for a first half-marathon.",
    "Write a magazine feature (about 600 words) on the history of the bicycle.",
    "Write an essay (about 600 words) on why people collect things.",
    "Write a feature article (about 600 words) about the cultural history of coffeehouses.",
    "Write a reflective essay (about 600 words) on what a long career in teaching taught you about patience.",
]
for i, p in enumerate(GENERAL):
    prompts.append({"id": "gen_%02d" % i, "register": "general", "prompt": p})
# held-out test prompts (unedited answers used to test the skill; not used for calibration)
TEST = [
    {"id": "test_sci_intro", "register": "scientific", "prompt": "I'm writing a research paper titled \"Urban heat islands and emergency hospital admissions among older adults: a time-series analysis of 12 European cities\". Here is the abstract:\n\nBackground: Heat-related morbidity is rising, but the contribution of intra-urban temperature differences is unclear. Methods: We linked daily land-surface temperature estimates at 1 km resolution to 1.9 million emergency admissions of adults aged 65+ in 12 European cities (2008-2018) and fitted distributed-lag non-linear models. Results: Admissions rose 11% (95% CI 8-14%) on days above the 95th temperature percentile compared with the median. The excess risk was 1.6 times higher in the hottest urban quintile than in the coolest. Respiratory and renal admissions drove most of the excess; cardiovascular admissions showed no clear association. Conclusions: Intra-urban heat exposure, not only city-wide temperature, shapes heat-related morbidity in older adults.\n\nPlease draft the Introduction section (about 700 words). Write it as plain paragraphs, without headings and without reference citations."},
    {"id": "test_sci_disc", "register": "scientific", "prompt": "I'm writing a paper titled \"A low-cost acoustic sensor network for monitoring bat activity along highways\". Main findings: 38 sensors (US$45 each) deployed along 60 km of highway for 14 months recorded 212,000 bat passes; activity dropped 61% within 50 m of lit road sections compared with unlit ones; species detection agreed with expert manual review in 89% of a 2,000-call validation sample, but the classifier confused two Myotis species in 23% of cases; 9 sensors failed in winter because of battery issues. Please draft the Discussion section (about 700 words). Plain paragraphs, no headings, no reference citations."},
    {"id": "test_gen_oped", "register": "general", "prompt": "Write an opinion column (about 600 words) arguing that public libraries should stay open until midnight."},
    {"id": "test_gen_review", "register": "general", "prompt": "Write a review (about 500 words) of a hotel stay where the room was clean and the location great, but the air conditioning broke on the hottest night and the front desk took nine hours to respond."},
]
prompts += TEST
path = os.path.join(WS, "prompts_1.json")
for reg in ("scientific", "scientific_brown", "abstract", "general"):
    print(reg, len(glob.glob(os.path.join(OUT, reg, "*.txt"))))
if os.path.exists(path) and "--force" not in sys.argv:
    print("prompts_1.json exists and was kept (generated texts may depend on it); use --force to rebuild")
else:
    json.dump(prompts, open(path, "w", encoding="utf-8"), indent=1)
    print("prompts:", len(prompts), {r: sum(p["register"] == r for p in prompts) for r in ("scientific", "abstract", "general")})
