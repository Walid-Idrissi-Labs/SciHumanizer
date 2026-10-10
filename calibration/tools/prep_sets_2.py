#!/usr/bin/env python3
"""French human sets, a modern English general set, long human texts, and the second prompt list.

Run after fetch_corpora.py (and after fetch_pmc.py for the long English scientific texts):

  prep_sets_2.py corpora    build calib/fr/human/{scientific,abstract,general}, calib/human/general_modern,
                            and calib/long/<lang>.<register>/ (long human texts for the long-document check)
  prep_sets_2.py prompts    write prompts_2.json once (topic-matched requests, no style instructions)
"""
import collections, glob, html, json, os, random, re, sys

from paths import WS
C = os.path.join(WS, "corpora")
K = os.path.join(WS, "calib")
CAP, LONG_CAP = 950, 2600


def idx(lang, src):
    p = os.path.join(C, lang, src, "index.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def read(lang, src, name):
    return open(os.path.join(C, lang, src, name + ".txt"), encoding="utf-8").read()


def cut(paras, cap, minw):
    """Whole paragraphs up to cap words (a single oversized paragraph is cut at a sentence end)."""
    out, n = [], 0
    for p in paras:
        k = len(p.split())
        if out and n + k > cap:
            break
        if not out and k > cap * 1.3:
            acc, m = [], 0
            for s in re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-ÖØ-Þ«\"])", p):
                if acc and m + len(s.split()) > cap:
                    break
                acc.append(s)
                m += len(s.split())
            p, k = " ".join(acc), m
        out.append(p)
        n += k
    return ("\n\n".join(out) + "\n", n) if n >= minw else (None, n)


def put(folder, name, text):
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, name + ".txt"), "w", encoding="utf-8").write(text)


def clean_dir(folder):
    for f in glob.glob(os.path.join(folder, "*.txt")):
        os.remove(f)


def oe_sections(text):
    secs, cur, title = [], [], "(début)"
    for block in text.split("\n\n"):
        block = block.strip()
        if block.startswith("## "):
            if cur:
                secs.append((title, cur))
            title, cur = block[3:].strip(), []
        elif block:
            cur.append(block)
    if cur:
        secs.append((title, cur))
    return secs


def corpora():
    rnd = random.Random(42)
    counts = collections.Counter()
    # ---------------- French scientific: OpenEdition (humanities and social sciences) + PMC (medicine)
    out = os.path.join(K, "fr", "human", "scientific")
    longd = os.path.join(K, "long", "fr.scientific")
    clean_dir(out)
    clean_dir(longd)
    # The AI prompts are half OpenEdition introductions and half PMC discussions, so the human set keeps
    # the same balance: one excerpt per OpenEdition article (introduction for two in three, a body section
    # for the third), capped at the number of PMC sections plus ten percent.
    n_pmc = len(idx("fr", "pmc"))
    oe_names = sorted(idx("fr", "openedition"))
    rnd.shuffle(oe_names)
    kept = 0
    for i, name in enumerate(oe_names):
        secs = oe_sections(read("fr", "openedition", name))
        if not secs:
            continue
        allp = [p for _, ps in secs for p in ps]
        t, n = cut(allp, LONG_CAP, 1500)
        if t:
            put(longd, name, t)
            counts["long fr.scientific"] += 1
        if kept >= 1.1 * n_pmc:
            continue
        if i % 3 == 2 and len(secs) >= 3:
            mid = max(secs[1:-1], key=lambda s: len(" ".join(s[1]).split()))
            t, n = cut(mid[1], CAP, 300)
            if t:
                put(out, name + "_body", t)
                counts["fr.scientific openedition body"] += 1
                kept += 1
                continue
        # opening: the text before the second heading, at least 300 words (else the first paragraphs)
        opening = secs[0][1] if len(" ".join(secs[0][1]).split()) >= 300 else allp
        t, n = cut(opening, CAP, 300)
        if t:
            put(out, name + "_intro", t)
            counts["fr.scientific openedition intro"] += 1
            kept += 1
    for name in sorted(idx("fr", "pmc")):
        t, n = cut([p for p in read("fr", "pmc", name).split("\n\n") if p.strip()], CAP, 250)
        if t:
            put(out, name, t)
            counts["fr.scientific pmc"] += 1
    # ---------------- French abstracts: HAL + OpenEdition résumés
    out = os.path.join(K, "fr", "human", "abstract")
    clean_dir(out)
    for src in ("hal", "openedition_abs"):
        names = sorted(idx("fr", src))
        rnd.shuffle(names)
        for name in (names if src == "hal" else names[:24]):      # HAL is balanced over 11 domains; keep it dominant
            t = read("fr", src, name).strip()
            if 140 <= len(t.split()) <= 400:
                put(out, ("oeabs_" + name[3:]) if src == "openedition_abs" else name, t + "\n")
                counts["fr.abstract " + src] += 1
    # ---------------- general: The Conversation, Wikinews, Wikipedia (French; modern English)
    for lang, out, longd in (("fr", os.path.join(K, "fr", "human", "general"), os.path.join(K, "long", "fr.general")),
                             ("en", os.path.join(K, "human", "general_modern"), os.path.join(K, "long", "en.general"))):
        clean_dir(out)
        clean_dir(longd)
        # proportions follow the prompts: analysis pieces, then news, then encyclopedic prose
        for src, limit in ((("conversation", 170), ("wikinews", 95), ("wikipedia", 70)) if lang == "fr" else
                           (("conversation", 170), ("wikinews", 110), ("wikipedia", 78))):
            names = sorted(idx(lang, src))
            rnd.shuffle(names)
            for name in names[:limit]:
                paras = [p for p in read(lang, src, name).split("\n\n") if p.strip()]
                t, n = cut(paras, CAP, 250)
                if t:
                    put(out, name, t)
                    counts["%s.general %s" % (lang, src)] += 1
                t, n = cut(paras, LONG_CAP, 1500)
                if t:
                    put(longd, name, t)
                    counts["long %s.general" % lang] += 1
    # ---------------- long English scientific texts: whole PMC sections; introduction + discussion of one paper
    longd = os.path.join(K, "long", "en.scientific")
    clean_dir(longd)
    by = collections.defaultdict(dict)
    for fp in glob.glob(os.path.join(C, "pmc", "PMC*_*.txt")):
        pid, kind = os.path.basename(fp)[:-4].split("_")
        by[pid][kind] = [p for p in open(fp, encoding="utf-8").read().split("\n\n") if p.strip()]
    for pid, d in sorted(by.items()):
        paras = d.get("intro", []) + d.get("discussion", [])
        t, n = cut(paras, LONG_CAP, 1500)
        if t:
            put(longd, pid, t)
            counts["long en.scientific"] += 1
    for k, v in sorted(counts.items()):
        print("%-36s %d" % (k, v))


DOMAINS = {"shs": "sciences humaines et sociales", "sdv": "sciences du vivant", "info": "informatique",
           "spi": "sciences de l'ingénieur", "phys": "physique", "sde": "sciences de l'environnement",
           "math": "mathématiques", "chim": "chimie", "sdu": "sciences de la Terre", "scco": "sciences cognitives",
           "stat": "statistique"}
FR_NEWS = [
    "Rédige un article de presse (environ 500 mots) : le conseil municipal d'une ville moyenne a voté par 18 voix contre 15 le remplacement d'un parking du centre-ville par un parc public, avec les réactions des habitants et des commerçants.",
    "Rédige un article de presse (environ 500 mots) sur un hôpital régional qui a réduit les temps d'attente aux urgences en réorganisant le tri des patients par les infirmiers.",
    "Rédige un article de presse (environ 500 mots) sur une étude universitaire montrant que la semaine de quatre jours à l'école primaire a des effets contrastés sur les résultats des élèves en zone rurale.",
    "Rédige un article de presse (environ 500 mots) sur un petit port de pêche breton confronté à l'effondrement des prises de coquilles Saint-Jacques.",
    "Rédige un article de presse (environ 500 mots) sur l'inauguration d'une nouvelle ligne de tramway dans une métropole régionale, après trois ans de travaux et un budget dépassé de 12 %.",
    "Rédige un article de presse (environ 500 mots) sur des inondations qui ont touché plusieurs communes d'un département du sud de la France après deux jours de pluies intenses.",
]
FR_ENCY = [
    "Rédige une section d'article encyclopédique (environ 700 mots) sur l'histoire de la bicyclette.",
    "Rédige une section d'article encyclopédique (environ 700 mots) sur l'histoire des cafés en Europe et leur rôle culturel.",
    "Rédige une section d'article encyclopédique (environ 700 mots) sur la géographie et le climat d'un massif montagneux de ton choix.",
    "Rédige une section d'article encyclopédique (environ 700 mots) sur la carrière d'un peintre du XIXe siècle de ton choix.",
]
EN_ENCY = [
    "Write a section of an encyclopedia article (about 700 words) on the history of the bicycle.",
    "Write a section of an encyclopedia article (about 700 words) on the history of coffeehouses in Europe and their cultural role.",
    "Write a section of an encyclopedia article (about 700 words) on the geography and climate of a mountain range of your choice.",
    "Write a section of an encyclopedia article (about 700 words) on the career of a 19th-century painter of your choice.",
]
FR_TEST = [
    {"id": "test_fr_sci_intro", "register": "scientific", "prompt": "Je rédige un article de recherche intitulé « Îlots de chaleur urbains et passages aux urgences des personnes âgées : analyse de séries temporelles dans 12 villes européennes ». Voici le résumé :\n\nContexte : la morbidité liée à la chaleur augmente, mais la contribution des écarts de température à l'intérieur des villes reste mal connue. Méthodes : nous avons relié des estimations quotidiennes de la température de surface à une résolution de 1 km à 1,9 million de passages aux urgences d'adultes de 65 ans et plus dans 12 villes européennes (2008-2018), et ajusté des modèles non linéaires à retards distribués. Résultats : les passages augmentaient de 11 % (IC à 95 % : 8-14 %) les jours dépassant le 95e percentile de température par rapport à la médiane. L'excès de risque était 1,6 fois plus élevé dans le quintile urbain le plus chaud que dans le plus frais. Les causes respiratoires et rénales expliquaient l'essentiel de l'excès ; aucune association nette n'apparaissait pour les causes cardiovasculaires. Conclusions : l'exposition à la chaleur à l'échelle intra-urbaine, et pas seulement la température moyenne de la ville, détermine la morbidité liée à la chaleur chez les personnes âgées.\n\nPeux-tu rédiger l'introduction (environ 700 mots) ? Rédige-la en paragraphes simples, sans intertitres et sans références bibliographiques."},
    {"id": "test_fr_sci_disc", "register": "scientific", "prompt": "Je rédige un article intitulé « Un réseau de capteurs acoustiques à bas coût pour suivre l'activité des chauves-souris le long des autoroutes ». Principaux résultats : 38 capteurs (45 dollars pièce) déployés sur 60 km d'autoroute pendant 14 mois ont enregistré 212 000 passages de chauves-souris ; l'activité chutait de 61 % à moins de 50 m des tronçons éclairés par rapport aux tronçons non éclairés ; l'identification des espèces concordait avec la vérification manuelle par un expert dans 89 % d'un échantillon de validation de 2 000 cris, mais le classifieur confondait deux espèces de Myotis dans 23 % des cas ; 9 capteurs sont tombés en panne en hiver à cause des batteries. Peux-tu rédiger la section Discussion (environ 700 mots) ? En paragraphes simples, sans intertitres et sans références bibliographiques."},
    {"id": "test_fr_gen_tribune", "register": "general", "prompt": "Rédige une tribune (environ 600 mots) défendant l'idée que les bibliothèques municipales devraient rester ouvertes jusqu'à minuit."},
    {"id": "test_fr_gen_analyse", "register": "general", "prompt": "Rédige un article d'analyse grand public (environ 800 mots), signé par un universitaire, intitulé « Pourquoi les villes moyennes perdent-elles leurs commerces de centre-ville ? »."},
]


def journal_title(name):
    p = os.path.join(C, "raw2", "openedition", name + ".html")
    if os.path.exists(p):
        m = re.search(r'<a title="Accueil"[^>]*>\s*<span>(.*?)</span>', open(p, encoding="utf-8", errors="ignore").read(), flags=re.S)
        if m:
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return None


def one_line(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def prompts():
    path = os.path.join(WS, "prompts_2.json")
    if os.path.exists(path) and "--force" not in sys.argv:
        sys.exit("prompts_2.json exists (generated texts may already depend on it); use --force to rebuild")
    rnd = random.Random(7)
    out = []
    # --- French scientific: 15 introductions (OpenEdition), 15 discussions (PMC, French)
    oe = [(k, v) for k, v in sorted(idx("fr", "openedition").items()) if 120 <= len(v.get("abstract", "").split()) <= 330 and v.get("title")]
    rnd.shuffle(oe)
    n = 0
    for name, v in oe:
        jt = journal_title(name)
        if not jt or n >= 15:
            continue
        out.append({"id": "frsci_intro_" + name, "lang": "fr", "register": "scientific", "dir": "fr/{tier}/scientific",
                    "prompt": "Je rédige un article de recherche intitulé « %s » pour la revue %s. Voici le résumé :\n\n%s\n\n"
                              "Peux-tu rédiger l'introduction (environ 700 mots) ? Rédige-la en paragraphes simples, sans "
                              "intertitres et sans références bibliographiques." % (one_line(v["title"]), jt, one_line(v["abstract"]))})
        n += 1
    pm = [(k, v) for k, v in sorted(idx("fr", "pmc").items()) if v["section"] == "discussion" and 70 <= len(v.get("abstract", "").split()) <= 330]
    rnd.shuffle(pm)
    for name, v in pm[:15]:
        out.append({"id": "frsci_disc_" + name.split("_")[0], "lang": "fr", "register": "scientific", "dir": "fr/{tier}/scientific",
                    "prompt": "Je rédige un article intitulé « %s » pour la revue %s. Voici le résumé :\n\n%s\n\n"
                              "Peux-tu rédiger la section Discussion (environ 700 mots) à partir de ces éléments ? Rédige-la en "
                              "paragraphes simples, sans intertitres et sans références bibliographiques." % (
                                  one_line(v["title"]), v["journal"], one_line(v["abstract"]))})
    # --- French abstracts: 20 from HAL titles, spread over domains
    hal = sorted(idx("fr", "hal").items())
    rnd.shuffle(hal)
    seen = collections.Counter()
    for name, v in hal:
        if seen[v["domain"]] >= 2 or sum(seen.values()) >= 20 or not v.get("title") or len(v["title"].split()) < 5:
            continue
        seen[v["domain"]] += 1
        kind = "d'une thèse en %s intitulée" % DOMAINS[v["domain"]] if v["type"] == "THESE" else "d'un article en %s intitulé" % DOMAINS[v["domain"]]
        out.append({"id": "frabs_" + name, "lang": "fr", "register": "abstract", "dir": "fr/{tier}/abstract",
                    "prompt": "Rédige le résumé (environ 220 mots) %s « %s »." % (kind, one_line(v["title"]))})
    # --- French general: 10 analysis pieces matched to The Conversation titles, 6 news, 4 encyclopedic
    tc = sorted(idx("fr", "conversation").items())
    rnd.shuffle(tc)
    for name, v in tc[:10]:
        out.append({"id": "frgen_" + name, "lang": "fr", "register": "general", "dir": "fr/{tier}/general",
                    "prompt": "Rédige un article d'analyse grand public (environ 800 mots), signé par un universitaire, intitulé « %s »." % one_line(v["title"])})
    for i, p in enumerate(FR_NEWS):
        out.append({"id": "frgen_news_%02d" % i, "lang": "fr", "register": "general", "dir": "fr/{tier}/general", "prompt": p})
    for i, p in enumerate(FR_ENCY):
        out.append({"id": "frgen_ency_%02d" % i, "lang": "fr", "register": "general", "dir": "fr/{tier}/general", "prompt": p})
    for t in FR_TEST:
        out.append(dict(t, lang="fr", dir="fr/test_{tier}"))
    # --- English general, modern genres: 10 analysis pieces matched to The Conversation titles, 4 encyclopedic
    tc = sorted(idx("en", "conversation").items())
    rnd.shuffle(tc)
    for name, v in tc[:10]:
        out.append({"id": "engen_" + name, "lang": "en", "register": "general", "dir": "en/{tier}/general_modern",
                    "prompt": "Write an explanatory article for a general audience (about 800 words), written by an academic, titled \"%s\"." % one_line(v["title"])})
    for i, p in enumerate(EN_ENCY):
        out.append({"id": "engen_ency_%02d" % i, "lang": "en", "register": "general", "dir": "en/{tier}/general_modern", "prompt": p})
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("prompts:", len(out), dict(collections.Counter((p["lang"], p["register"]) for p in out)))


if __name__ == "__main__":
    {"corpora": corpora, "prompts": prompts}[sys.argv[1]]()
