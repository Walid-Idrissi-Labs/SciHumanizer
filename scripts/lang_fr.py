"""Pack de langue français pour SciHumanizer (French language pack).

Provenance of each list:
  [R] reported in the research analysed for this skill; almost all of it concerns English, so
      French lists marked [R] are the French counterparts of an English finding
  [P] practitioner-observed tell in French LLM output, not measured in those papers
  [L] standard linguistic operationalisation (Biber 1988; Hyland 2005; guides de rédaction claire)
  [C] confirmed or derived by this skill's own French calibration (references/calibration.md)
Single words are LEMMAS (formes du dictionnaire) unless noted; multi-word entries are phrases.
"""
import re

NAME = "French"

# --- découpage en phrases ------------------------------------------------------------------
ABBREVIATIONS = {"etc", "cf", "p", "pp", "vol", "fig", "tab", "éd", "ed", "éds", "eds", "coll", "chap", "art",
                 "al", "env", "ex", "av", "apr", "j.-c", "st", "ste", "dr", "pr", "mgr", "ibid", "op", "cit",
                 "sq", "sqq", "trad", "dir", "no", "n", "t", "s", "h", "m", "mm", "mme", "mlle", "c.-à-d",
                 "n.b", "p.s", "réf", "ref", "éq", "eq", "tél", "boul", "bd", "resp", "min", "max", "sec",
                 "janv", "févr", "avr", "juil", "sept", "oct", "nov", "déc", "approx", "vs", "e.g", "i.e",
                 "suppl", "ann", "paragr", "sect", "nb"}
SENTENCE_FINAL_ABBREV = {"al", "etc"}
SENTENCE_STARTERS = {"le", "la", "les", "un", "une", "des", "ce", "cette", "ces", "il", "elle", "ils", "elles",
                     "nous", "on", "en", "dans", "pour", "cependant", "toutefois", "ainsi", "de", "du", "au",
                     "aux", "à", "par", "sur", "avec", "mais", "et", "or", "donc", "si", "lorsque", "quand",
                     "comme", "notre", "nos", "leur", "leurs", "son", "sa", "ses", "plusieurs", "certains",
                     "certaines", "d'autres", "enfin", "puis", "ensuite", "selon", "après", "avant", "depuis",
                     "chaque", "tous", "toutes", "tout", "cela", "ceci", "c", "l", "d", "j", "qu"}

# --- classes fermées [L] ----------------------------------------------------------------------
FIRST_PERSON = {"je", "j'", "me", "m'", "moi", "mon", "ma", "mes", "nous", "notre", "nos", "nôtre", "nôtres"}
SECOND_PERSON = {"tu", "te", "t'", "toi", "ton", "ta", "tes", "vous", "votre", "vos"}
THIRD_PERSON = {"il", "elle", "ils", "elles", "lui", "leur", "leurs", "se", "s'", "son", "sa", "ses", "eux", "on"}
SUBJECT_PRONOUNS = {"je", "j'", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "ce", "c'", "qui"}
MODALS = {"pouvoir", "devoir", "falloir", "vouloir"}
BE_FORMS = {"est", "sont", "était", "étaient", "sera", "seront", "serait", "seraient", "fut", "furent", "soit",
            "soient", "été", "être", "étant", "suis", "sommes", "êtes", "étais", "étions", "serai", "serons"}
NEGATIONS = ["ne", "n'", "sans", "non", "ni", "aucun", "aucune", "jamais", "absence", "échoue", "échouent", "échoué"]
COORDINATORS = {"et", "mais", "ou", "donc", "or", "ni", "car"}
AND_OR = {"et", "ou"}
SUBORDINATORS = {"si", "puisque", "puisqu'", "comme", "quoique", "quoiqu'", "lorsque", "lorsqu'", "quand", "où",
                 "comment", "pourquoi", "que", "qu'", "qui"}
# multi-word subordinators that open a clause (checked on the sentence start)
SUBORD_PHRASES = ["parce que", "parce qu'", "bien que", "bien qu'", "alors que", "alors qu'", "tandis que",
                  "tandis qu'", "même si", "dès que", "dès qu'", "dès lors que", "après que", "avant que",
                  "pendant que", "afin que", "afin de", "afin d'", "pour que", "étant donné que", "vu que",
                  "à moins que", "pourvu que", "depuis que", "une fois que", "sans que", "s'il", "s'ils",
                  "à mesure que", "au moment où", "de même que", "ainsi que", "quel que soit", "quelle que soit"]
PREPOSITIONS = {"dans", "sur", "sous", "à", "au", "aux", "pour", "avec", "par", "de", "du", "des", "depuis",
                "pendant", "durant", "parmi", "entre", "malgré", "contrairement", "selon", "vers", "chez",
                "sans", "contre", "outre", "après", "avant", "dès", "lors", "face", "grâce", "suite", "quant",
                "concernant", "suivant", "devant", "derrière", "hors", "via", "en", "d'après", "jusqu'",
                "jusque", "auprès", "autour", "près", "loin", "à travers", "au-delà", "au-dessus", "au-dessous"}
OF_WORD = "de"
STOPWORDS = set("""à au aux avec ce ces cet cette dans de des du elle elles en et eux il ils je la le les leur leurs lui
ma mais me même mes moi mon ne nos notre nous on ou où par pas pour qu que qui sa se ses son sur ta te tes toi ton tu
un une vos votre vous c d j l m n s t y été étée étées étés étant suis es est sommes êtes sont serai seras sera
serons serez seront serais serait serions seriez seraient étais était étions étiez étaient fus fut fûmes fûtes
furent sois soit soyons soyez soient ai as avons avez ont aurai auras aura aurons aurez auront aurais aurait aurions
auriez auraient avais avait avions aviez avaient eut eurent aie aies ait ayons ayez aient eu ayant plus moins très
aussi ainsi alors donc or ni car si comme tout tous toute toutes autre autres cela ceci ça dont quel quelle quels
quelles lors bien peu trop encore déjà toujours jamais ici là puis ensuite enfin entre vers chez sans sous après
avant pendant depuis selon contre parmi afin lorsque puisque quand comment pourquoi deux trois un être avoir faire
celui celle ceux celles ci leur y l' d' j' n' s' m' t' c' qu' jusqu' lorsqu' puisqu' quoiqu'""".split())

# --- profil des mots-outils --------------------------------------------------------------------
# The English lists come from Desaire et al. / Kim & Desaire / Fujiwara (via the 44-study survey).
# No such study exists for French in the analysed papers, so these are the counterparts [R-analogue];
# the calibration reports them but does not gate on them unless they separate.
AI_FAVORED_FW = ["et", "peut", "peuvent", "par", "avec", "pour", "leur", "leurs"]
HUMAN_FAVORED_FW = ["cependant", "mais", "quoique", "parce", "si", "que", "qu'", "ou", "quand", "comme", "ce",
                    "je", "j'", "ils", "mon", "il", "nous", "on", "donc", "pourtant", "car", "or",
                    "pourrait", "pourraient", "serait", "aurait"]

# --- connecteurs [R-analogue]+[L] -----------------------------------------------------------------
CONNECTIVES = {
    "additive": ["de plus", "en outre", "par ailleurs", "de surcroît", "qui plus est", "également", "aussi",
                 "d'autre part", "d'une part", "de même", "de la même manière", "de la même façon",
                 "parallèlement", "en plus", "ajoutons que", "à cela s'ajoute", "par surcroît"],
    "contrastive": ["cependant", "toutefois", "néanmoins", "pourtant", "mais", "or", "en revanche", "au contraire",
                    "à l'inverse", "par contre", "malgré tout", "quand même", "tout de même", "bien que",
                    "quoique", "alors que", "tandis que", "même si", "certes", "pour autant", "inversement",
                    "d'un autre côté", "il n'en reste pas moins", "il n'empêche", "à l'opposé", "en dépit de cela"],
    "causal": ["car", "parce que", "puisque", "donc", "ainsi", "par conséquent", "en conséquence",
               "c'est pourquoi", "de ce fait", "dès lors", "d'où", "du coup", "de sorte que", "si bien que",
               "étant donné que", "vu que", "voilà pourquoi", "pour cette raison"],
    "conditional": ["si", "sinon", "à moins que", "pourvu que", "à condition que", "dans ce cas",
                    "le cas échéant", "sans quoi", "autrement", "faute de quoi"],
    "exemplifying": ["par exemple", "notamment", "en particulier", "tel que", "tels que", "telle que",
                     "telles que", "à savoir", "c'est-à-dire", "à titre d'exemple", "plus précisément",
                     "entre autres", "pour illustrer", "à titre d'illustration"],
    "sequencing": ["d'abord", "tout d'abord", "premièrement", "deuxièmement", "troisièmement", "ensuite", "puis",
                   "enfin", "dans un premier temps", "dans un second temps", "dans un deuxième temps",
                   "par la suite", "pour commencer", "en premier lieu", "en second lieu", "en dernier lieu"],
    "summarizing": ["en conclusion", "pour conclure", "en somme", "en résumé", "pour résumer", "en définitive",
                    "au final", "finalement", "en fin de compte", "bref", "en bref", "somme toute",
                    "tout compte fait", "globalement", "dans l'ensemble", "au total", "en un mot",
                    "en dernière analyse", "au bout du compte", "en conséquence de quoi"],
    "emphatic": ["en effet", "surtout", "particulièrement", "il est à noter", "force est de constater",
                 "de fait", "en réalité", "bien sûr", "évidemment", "clairement", "à vrai dire", "précisément",
                 "justement", "il faut souligner", "il convient de souligner", "fait notable", "plus encore",
                 "indéniablement", "incontestablement", "avant tout", "fondamentalement", "essentiellement"],
}
FORMULAIC_CONNECTIVE_CLASSES = ("additive", "summarizing", "emphatic")
LOGICAL_CONNECTIVE_CLASSES = ("contrastive", "causal", "conditional")
NOT_ADVERBIAL = {"mais", "et", "ou", "or", "car", "donc", "ni", "si", "bien que", "quoique", "alors que", "tandis que",
                 "même si", "parce que", "puisque", "à moins que", "pourvu que", "à condition que", "étant donné que",
                 "vu que", "de sorte que", "si bien que", "tel que", "tels que", "telle que", "telles que"}
NEED_COMMA = {"aussi", "ainsi", "ensuite", "puis", "enfin", "également", "certes", "autrement", "justement",
              "précisément", "surtout", "notamment", "finalement", "globalement", "parallèlement", "d'abord",
              "bref", "sinon", "particulièrement", "clairement", "évidemment", "inversement", "pourtant"}
UNAMBIGUOUS_CONNECTIVES = {"cependant", "toutefois", "néanmoins", "pourtant", "en revanche", "au contraire",
                           "par contre", "de plus", "en outre", "par ailleurs", "de surcroît", "qui plus est",
                           "par conséquent", "en conséquence", "c'est pourquoi", "de ce fait", "dès lors",
                           "par exemple", "en particulier", "en conclusion", "pour conclure", "en somme",
                           "en résumé", "en définitive", "au final", "en fin de compte", "en effet", "bien que",
                           "quoique", "alors que", "tandis que", "parce que", "puisque", "à moins que", "car",
                           "inversement", "d'une part", "d'autre part", "notamment", "force est de constater"}

# --- prise de position (Hyland 2005) [L] ----------------------------------------------------------
HEDGES = {"lemmas": ["peut-être", "probablement", "vraisemblablement", "possiblement", "éventuellement",
                     "apparemment", "sembler", "paraître", "suggérer", "relativement", "environ",
                     "approximativement", "incertain", "plausible", "plausiblement", "présumer", "supposer",
                     "hypothétique", "provisoirement"],
          "phrases": ["sans doute", "a priori", "il se peut", "il est possible que", "il semblerait", "laisse penser",
                      "laissent penser", "tend à", "tendent à", "quelque peu", "en partie", "dans une certaine mesure",
                      "à peu près", "nous pensons", "je pense", "nous supposons", "à notre avis", "selon nous",
                      "à notre connaissance", "pas nécessairement", "pourrait", "pourraient", "semble-t-il"]}
BOOSTERS = {"lemmas": ["clairement", "évidemment", "certainement", "assurément", "indéniablement",
                       "incontestablement", "indubitablement", "toujours", "jamais", "démontrer", "prouver",
                       "établir", "manifestement", "nettement", "fortement", "résolument", "forcément"],
            "phrases": ["sans aucun doute", "sans conteste", "bien sûr", "bien entendu", "de fait",
                        "il est clair que", "il est évident que", "à l'évidence", "nul doute"]}
ATTITUDE = {"lemmas": ["étonnamment", "curieusement", "malheureusement", "heureusement", "étrangement",
                       "paradoxalement", "remarquablement", "hélas", "franchement", "surprenant", "inattendu",
                       "remarquable", "frappant", "décevant", "troublant", "inquiétant", "encourageant",
                       "regrettable", "curieux", "étonnant", "contre-intuitif", "discutable", "contestable",
                       "trompeur", "erroné", "exagéré", "négligé", "fâcheux", "agaçant", "frustrant", "douteux"],
            "phrases": ["fait surprenant", "de façon surprenante", "de manière inattendue", "il est frappant",
                        "à vrai dire", "chose étonnante", "contre toute attente", "à notre surprise"]}
CASE_SENSITIVE_WORDS = set()

# --- vocabulaire évaluatif [R-analogue: MAGE, neutralité] -------------------------------------------
CRITICAL_LEMMAS = ["problème", "échec", "échouer", "faible", "faiblesse", "défaut", "lacune", "erreur", "erroné",
                   "biais", "biaisé", "manque", "manquer", "flou", "incohérent", "contradictoire", "contredire",
                   "décevant", "pire", "mauvais", "malheureusement", "limite", "limitation", "insuffisant",
                   "insuffisance", "inquiétude", "préoccupation", "trompeur", "surestimer", "sous-estimer",
                   "doute", "douteux", "coûteux", "cher", "lent", "fragile", "détester", "terrible", "affreux",
                   "pénible", "frustrant", "furieux", "impoli", "cassé", "inutile", "confus", "nuire", "nuisible",
                   "risque", "risqué", "difficile", "difficulté", "inadmissible", "scandaleux", "médiocre"]
PROMO_LEMMAS = ["crucial", "vital", "essentiel", "primordial", "clé", "robuste", "exhaustif", "innovant",
                "novateur", "prometteur", "passionnant", "remarquable", "puissant", "fluide", "révolutionnaire",
                "transformateur", "inestimable", "précieux", "holistique", "dynamique", "riche", "profond",
                "exceptionnel", "excellent", "incroyable", "incroyablement", "formidable", "considérable",
                "majeur", "optimiser", "renforcer", "incontournable", "unique", "impressionnant", "convaincant",
                "florissant", "inégalé", "véritable", "fascinant", "captivant", "indispensable", "fondamental",
                "ambitieux", "pertinent", "enrichissant"]

# --- mots typiques des LLM en français [P]; signalés, non bloquants ---------------------------------
AI_VOCAB_LEMMAS = ["crucial", "primordial", "incontournable", "holistique", "multifacette", "transformateur",
                   "novateur", "synergie", "levier", "écosystème", "paradigme", "résilience", "favoriser",
                   "optimiser", "souligner", "naviguer", "plonger", "tapisserie", "paysage", "prisme",
                   "véritable", "notamment", "pertinent", "enjeu", "défi", "essor", "avènement", "méticuleux",
                   "minutieux", "inestimable", "fascinant", "captivant", "dynamique", "démarche", "pilier"]

# --- formules figées: (regex, étiquette, source) ------------------------------------------------------
STOCK_PATTERNS = [
    (r"\bil (?:est|convient|importe|faut) (?:important |essentiel |crucial |primordial |intéressant |utile |nécessaire )?(?:de |d')(?:noter|souligner|rappeler|mentionner|préciser|remarquer|signaler)\b", "il-est-important-de-noter", "R"),
    (r"\bil (?:est|peut être) (?:possible |permis )?(?:de |d')(?:observer|constater|conclure|affirmer) que\b", "il-est-possible-d-observer", "R"),
    (r"\ben conclusion\b|\bpour conclure\b", "en-conclusion", "R"),
    (r"\bnon seulement\b[^.;:!?]{1,90}\bmais (?:aussi|également|encore|surtout)\b", "non-seulement-mais-aussi", "R"),
    (r"\bnous (?:vous )?(?:prions de nous excuser|présentons nos excuses) pour (?:la|le|ce|cette|tout|ces) (?:gêne|désagrément|inconvénient)", "excuses-commerciales", "R"),
    (r"\bnous nous efforçons de\b|\bn'hésitez pas à (?:nous )?contacter\b", "formule-service-client", "R"),
    (r"\bjou(?:e|ent|ant|ait|aient|er) un rôle (?:crucial|clé|essentiel|majeur|central|déterminant|primordial|fondamental|important|prépondérant|capital|de premier plan)\b", "joue-un-role-crucial", "P"),
    (r"\bdans un (?:monde|contexte|environnement) (?:où|de plus en plus|en constante|en perpétuelle|en pleine)\b", "dans-un-monde-ou", "P"),
    (r"\bà l'(?:ère|heure) (?:du|de la|de l'|des|où)\b", "a-l-ere-de", "P"),
    (r"\bau (?:cœur|coeur) d(?:e|u|es)\b", "au-coeur-de", "P"),
    (r"\ben (?:constante|perpétuelle|pleine) (?:évolution|mutation|expansion|transformation|croissance)\b", "en-constante-evolution", "P"),
    (r"\b(?:met|mettent|mettant|mettre|mis|mise) en lumière\b", "met-en-lumiere", "P"),
    (r"\b(?:soulign|rappell|illustr)(?:e|ent|ant) (?:l'importance|la nécessité|l'urgence|le rôle|la pertinence|l'intérêt|le potentiel)\b", "souligne-l-importance", "P"),
    (r"\btémoign(?:e|ent|ant) d(?:e|u|es|')", "temoigne-de", "P"),
    (r"\bforce est de constater\b", "force-est-de-constater", "P"),
    (r"\bil va sans dire\b|\bcela va sans dire\b", "il-va-sans-dire", "P"),
    (r"\b(?:ouvr|pav)(?:e|ent|ant|ir|er) la voie\b", "ouvre-la-voie", "P"),
    (r"\b(?:plong|plonge|plongeons|plongent|plongeant|plonger) (?:dans|au cœur)\b", "plonger-dans", "P"),
    (r"\bnavigu(?:e|er|ent|ant) (?:dans|à travers|entre)\b", "naviguer-dans", "P"),
    (r"\bune (?:myriade|pléthore|multitude|kyrielle) d(?:e|')", "une-myriade-de", "P"),
    (r"\bun (?:large|vaste) éventail d(?:e|')", "un-large-eventail", "P"),
    (r"\b(?:tir|tire|tirent|tirant|tirer) (?:pleinement )?parti d(?:e|u|es)\b", "tirer-parti-de", "P"),
    (r"\b(?:exploit|libér|révél)(?:e|er|ent|ant) (?:pleinement )?(?:le|tout le|son|leur) (?:plein )?potentiel\b", "liberer-le-potentiel", "P"),
    (r"\b(?:revêt|revêtent) une importance\b", "revet-une-importance", "P"),
    (r"\bs'(?:avère|avèrent) (?:crucial|essentiel|nécessaire|indispensable|primordial|déterminant)", "s-avere-crucial", "P"),
    (r"\bconstitu(?:e|ent) un(?:e)? (?:véritable )?(?:enjeu|défi|levier|pilier|atout|étape|avancée) (?:majeur|clé|essentiel|crucial|important|de taille|incontournable)", "constitue-un-enjeu-majeur", "P"),
    (r"\b(?:enjeux?|défis?) (?:majeurs?|cruciaux|crucial|de taille|considérables?)\b", "enjeu-majeur", "P"),
    (r"\bces dernières (?:années|décennies)\b|\bau cours des dernières (?:années|décennies)\b", "ces-dernieres-annees", "P"),
    (r"\bde nos jours\b|\baujourd'hui plus que jamais\b", "de-nos-jours", "P"),
    (r"\bil est (?:crucial|essentiel|primordial|impératif|indispensable|fondamental|capital) (?:de |d'|que)", "il-est-crucial-de", "P"),
    (r"\bque ce soit\b[^.;:!?]{1,80}\bou\b", "que-ce-soit-ou", "P"),
    (r"\bun(?:e)? (?:compréhension|vision|approche) (?:plus )?(?:approfondie|fine|nuancée|globale|holistique) d(?:e|u|es)\b", "une-comprehension-approfondie", "P"),
    (r"\bs'inscri(?:t|vent|vant) dans (?:une|un|le|la|cette|ce) (?:démarche|logique|dynamique|perspective|cadre|contexte|volonté)\b", "s-inscrit-dans-une-demarche", "P"),
    (r"\b(?:un|une|de) véritables? \w+", "un-veritable", "P"),
    (r"\bce n'est pas (?:seulement|simplement|qu'un|qu'une|juste)[^.;:!?]{1,70}[,;:] ?c'est\b", "ce-n-est-pas-x-c-est-y", "P"),
    (r"\bl'avenir (?:s'annonce|est) (?:prometteur|radieux)\b|\bseul l'avenir (?:nous )?le dira\b|\breste à voir\b", "fin-optimiste", "P"),
    (r"\ben fin de compte\b|\bau bout du compte\b", "en-fin-de-compte", "P"),
    (r"\bpiliers? (?:fondamental|fondamentaux|essentiels?|majeurs?)\b|\bpierre angulaire\b|\bfer de lance\b", "pierre-angulaire", "P"),
]
SIGNIFICANCE_ECHO = (r"^(?:ce|cet|cette|ces|ceci|cela|l'ensemble de ces|pris ensemble,? ces|globalement,? ces?)\b[^.!?]{0,70}\b"
                     r"(?:souligne|soulignent|met en évidence|mettent en évidence|met en lumière|mettent en lumière|démontre|"
                     r"démontrent|illustre|illustrent|rappelle|rappellent|confirme|confirment|montre|montrent|suggère|"
                     r"suggèrent|témoigne|témoignent|révèle|révèlent)\b[^.!?]{0,50}\b(?:importance|nécessité|valeur|potentiel|"
                     r"rôle|pertinence|complexité|intérêt|urgence|enjeu|enjeux|portée)\b")
STOCK_OPENERS = [
    r"^(?:ces dernières|depuis quelques|au cours des dernières|au fil des dernières) (?:années|décennies)",
    r"^(?:de nos jours|aujourd'hui,|à l'heure actuelle|à l'ère d|à l'heure d|dans un monde|dans un contexte)",
    r"^(?:l'essor|l'avènement|l'émergence|le développement rapide|la montée en puissance|l'évolution rapide|la multiplication) d",
    r"^(?:avec|face à|devant) (?:l'essor|l'avènement|l'émergence|la montée|le développement|la multiplication|l'augmentation)",
    r"^[a-zà-ÿ' \-]{0,45} (?:est devenu|est devenue|sont devenus|sont devenues|s'est imposé|s'est imposée|s'impose) (?:comme )?(?:un|une|des|l')",
    r"^depuis (?:plusieurs|quelques|de nombreuses) (?:années|décennies)",
    r"^(?:alors que|à mesure que|tandis que) (?:le|la|les|l') [a-zà-ÿ' \-]{0,40} (?:continue|continuent|ne cesse|ne cessent)",
    r"^imaginez un monde",
]
FORMULAIC_ENDING = (r"\b(?:en conclusion|pour conclure|en somme|en résumé|en définitive|au final|en fin de compte|"
                    r"dans l'ensemble|globalement|somme toute|à l'avenir|il conviendra|il serait intéressant d|"
                    r"des recherches futures|de futures recherches|les travaux futurs|de futurs travaux|"
                    r"ouvre la voie|ouvrent la voie|ouvrant la voie|reste à voir|seul l'avenir|"
                    r"perspectives? (?:prometteuses?|encourageantes?)|pistes? (?:de recherche )?prometteuses?|"
                    r"continu(?:e|ent|era|eront) (?:d'|de |à )(?:évoluer|façonner|croître))\b")
EXTRAPOSITION = (r"\bil (?:est|était|serait|semble|paraît|demeure|reste|convient|importe|s'avère) (?:\w+ ){0,2}"
                 r"(?:important|essentiel|crucial|primordial|nécessaire|clair|évident|intéressant|possible|probable|"
                 r"utile|indispensable|impératif|judicieux|pertinent|notable) (?:de|d'|que|qu')")

# --- remplissage ---------------------------------------------------------------------------------
WORDY = ["dans le but de", "dans le but d'", "dans l'optique de", "dans l'objectif de", "en vue de", "de manière à",
         "de façon à", "dans la mesure où", "en raison du fait que", "du fait que", "le fait que", "le fait qu'",
         "compte tenu du fait que", "au niveau de", "au niveau du", "au niveau des", "en termes de",
         "en matière de", "dans le cadre de", "dans le cadre du", "dans le contexte de", "dans le domaine de",
         "dans le domaine du", "en ce qui concerne", "pour ce qui est de", "à l'heure actuelle", "à ce jour",
         "au jour d'aujourd'hui", "dans un premier temps", "dans un second temps", "un certain nombre de",
         "un grand nombre de", "une grande variété de", "un large éventail de", "une multitude de",
         "la majorité de", "la plupart de", "est en mesure de", "sont en mesure de", "a la capacité de",
         "ont la capacité de", "a le potentiel de", "ont le potentiel de", "permet de", "permettent de",
         "permettant de", "permet d'", "permettent d'", "permettant d'", "il est possible de", "il est nécessaire de",
         "il est important de", "il est essentiel de", "il s'agit de", "il s'agit d'", "il est clair que",
         "il est évident que", "il va sans dire que", "comme par exemple", "voire même", "à travers", "au sein de",
         "au sein du", "au sein des", "à l'échelle de", "sur le plan de", "d'un point de vue", "de par", "et ce,",
         "ainsi que", "afin de pouvoir", "dans le sens où", "par le biais de", "par l'intermédiaire de",
         "en l'occurrence", "à savoir que", "de manière générale", "d'une manière générale", "de façon générale",
         "en règle générale", "au fur et à mesure", "prendre en compte", "prend en compte", "prennent en compte",
         "tenir compte de", "mettre en place", "met en place", "mettent en place", "mise en place",
         "mettre en œuvre", "met en œuvre", "mise en œuvre", "faire en sorte que", "apporter une contribution",
         "jouer un rôle dans", "joue un rôle dans"]
METADISCOURSE = ["dans cette section", "dans cet article", "dans ce chapitre", "dans cette partie", "dans ce qui suit",
                 "comme mentionné précédemment", "comme mentionné plus haut", "comme indiqué précédemment",
                 "comme indiqué plus haut", "comme évoqué précédemment", "comme nous l'avons vu",
                 "comme nous le verrons", "comme nous venons de le voir", "nous allons voir", "nous verrons que",
                 "rappelons que", "notons que", "soulignons que", "précisons que", "remarquons que",
                 "en d'autres termes", "autrement dit", "pour le dire simplement", "pour le dire autrement",
                 "il convient de souligner", "il est à noter", "à noter que", "il est important de noter",
                 "il est intéressant de noter", "intéressons-nous", "penchons-nous", "passons maintenant",
                 "abordons maintenant", "avant d'aborder", "ce qu'il faut retenir",
                 "ce que cela signifie", "en ce sens", "à cet égard", "dans cette optique", "dans cette perspective"]
SHELL_NOUNS = ["importance", "rôle", "aspect", "facteur", "élément", "composante", "enjeu", "défi", "opportunité",
               "implication", "considération", "contexte", "paysage", "cadre", "approche", "stratégie", "dynamique",
               "complexité", "nature", "potentiel", "perspective", "initiative", "dimension", "facette", "pilier",
               "fondement", "moteur", "levier", "catalyseur", "acteur", "interaction", "synergie", "nuance",
               "trajectoire", "paradigme", "écosystème", "récit", "parcours", "prisme", "démarche",
               "problématique", "thématique", "notion", "concept", "phénomène", "besoin", "capacité", "question"]
DOUBLE_HEDGES = [r"\b(?:pourrait|pourraient|peut|peuvent) (?:potentiellement|éventuellement|peut-être|possiblement)\b",
                 r"\b(?:potentiellement|éventuellement|peut-être) (?:pouvoir|pourrait|pourraient)\b",
                 r"\b(?:semble|semblent|paraît|paraissent) (?:suggérer|indiquer|laisser penser)\b",
                 r"\b(?:pourrait|pourraient) (?:suggérer|indiquer|laisser penser) qu[e'][^.;]{0,90}\b(?:pourrait|pourraient)\b",
                 r"\b(?:relativement|plutôt|assez) (?:probable|possible|incertain|flou)\b",
                 r"\bdans une certaine mesure\b[^.;]{0,60}\b(?:pourrait|pourraient|peut|peuvent)\b"]
EXPLETIVE_OPENER = r"^(?:il (?:y a|existe|existait|est|était|s'agit|convient|importe|faut)\b|c'est (?:\w+ ){0,3}(?:que|qui)\b)"

# --- morphologie ------------------------------------------------------------------------------------
NOMINAL_SUFFIXES = ("tion", "sion", "ment", "ité", "ance", "ence")            # analogue de Biber 1988 [L]
NOMINAL_EXCLUDE = {"question", "moment", "élément", "document", "monument", "argument", "instrument", "bâtiment",
                   "vêtement", "médicament", "aliment", "segment", "fragment", "ciment", "supplément",
                   "département", "tempérament", "nation", "station", "ration", "portion", "fraction", "section",
                   "notion", "option", "cité", "université", "société", "communauté", "qualité", "quantité",
                   "comment", "silence", "science", "distance", "instance", "essence", "licence", "agence",
                   "enfance", "vacance", "ambulance", "finance", "provence", "france", "appartement", "logement"}
LY_EXCLUDE = {"comment", "moment", "seulement"}
DEGREE_WORDS = {"plus", "moins", "mieux", "pire", "meilleur", "meilleure", "meilleurs", "meilleures", "moindre"}
IRREGULAR_PARTICIPLES = set("""fait faite faits faites dit dite dits dites pris prise prises mis mise mises vu vue vus
vues su sue pu dû due dus dues eu eue reçu reçue reçus reçues conçu conçue conçus conçues perçu perçue perçus perçues
construit construite construits construites produit produite produits produites réduit réduite réduits réduites
conduit conduite conduits conduites écrit écrite écrits écrites décrit décrite décrits décrites inscrit inscrite
ouvert ouverte ouverts ouvertes couvert couverte couverts couvertes offert offerte offerts offertes atteint atteinte
atteints atteintes peint peinte joint jointe joints jointes craint crainte connu connue connus connues reconnu
reconnue reconnus reconnues tenu tenue tenus tenues obtenu obtenue obtenus obtenues retenu retenue retenus retenues
soutenu soutenue soutenus soutenues contenu contenue rendu rendue rendus rendues vendu vendue perdu perdue perdus
perdues entendu entendue attendu attendue attendus attendues défendu défendue répandu répandue répandus répandues
rompu rompue résolu résolue résolus résolues traduit traduite traduits traduites introduit introduite introduits
introduites compris comprise comprises admis admise admises permis permise permises soumis soumise soumises
transmis transmise transmises acquis acquise acquises requis requise requises exclu exclue exclus exclues inclus
incluse incluses conclu conclue conclus conclues élu élue élus élues lu lue lus lues""".split())
ETRE_VERB_PARTICIPLES = {"allé", "allée", "allés", "allées", "venu", "venue", "venus", "venues", "arrivé", "arrivée",
                         "arrivés", "arrivées", "parti", "partie", "partis", "parties", "resté", "restée", "restés",
                         "restées", "devenu", "devenue", "devenus", "devenues", "né", "née", "nés", "nées", "mort",
                         "morte", "morts", "mortes", "tombé", "tombée", "tombés", "tombées", "entré", "entrée",
                         "entrés", "entrées", "sorti", "sortie", "sortis", "sorties", "revenu", "revenue", "revenus",
                         "revenues", "intervenu", "intervenue", "parvenu", "parvenue", "parvenus", "parvenues",
                         "survenu", "survenue", "apparu", "apparue", "apparus", "apparues", "demeuré", "demeurée",
                         "passé", "passée", "passés", "passées", "retourné", "retournée", "monté", "montée",
                         "descendu", "descendue", "rentré", "rentrée", "décédé", "décédée"}
PASSIVE_SKIP = {"pas", "aussi", "souvent", "alors", "encore", "bien", "déjà", "toujours", "généralement",
                "habituellement", "ainsi", "donc", "plus", "très", "largement", "principalement", "également", "été"}
REFLEXIVES = {"se", "s'", "me", "m'", "te", "t'"}
PARTICIPLE_FORM = r"(?:ant|é|ée|és|ées)$"
MODAL_LEMMAS = MODALS            # French modals are ordinary verbs in the lexicon: counted by lemma
# final words that elide before a vowel: a phrase ending in one of them also matches its elided form
ELIDING_FINALS = ("de", "que", "ne", "se", "ce", "lorsque", "puisque", "quoique", "jusque")
# Proposition participiale ou gérondif accolé après une virgule : « , soulignant ainsi l'importance de ... »,
# « , permettant de ... », « , tout en restant ... ». French counterpart of the English participial tail
# ([R-analogue]: Reinhart et al. 2024 for English; [P] for French).
PARTICIPIAL_CLAUSE = (r", (?:tout en |en |et |)?([a-zà-ÿ]+ant)"
                      r"(?= (?:de|d'|du|des|le|la|les|l'|un|une|à|au|aux|ainsi|en|que|qu'|son|sa|ses|leur|leurs|ce|"
                      r"cette|ces|sur|dans|par|pour|avec|aussi|donc|également|notamment|chaque|plus|moins|toute|tout|"
                      r"tous|toutes|ainsi|se|s'|y|ne|n'|pas)(?![a-zà-ÿ]))")
PARTICIPIAL_EXCLUDE = {"pendant", "avant", "devant", "maintenant", "cependant", "pourtant", "autant", "tant", "durant",
                       "suivant", "concernant", "moyennant", "nonobstant", "auparavant", "dorénavant", "quant",
                       "étant", "important", "restant", "instant", "courant"}

CLITIC_TAGS = {"l'": ("DET", "le"), "d'": ("ADP", "de"), "j'": ("PRON", "je"), "n'": ("ADV", "ne"),
               "s'": ("PRON", "se"), "m'": ("PRON", "me"), "t'": ("PRON", "te"), "c'": ("PRON", "c'"),
               "qu'": ("SCONJ", "que"), "jusqu'": ("ADP", "jusque"), "lorsqu'": ("SCONJ", "lorsque"),
               "puisqu'": ("SCONJ", "puisque"), "quoiqu'": ("SCONJ", "quoique")}
_ELISION = re.compile(r"^(l|d|j|n|s|m|t|c|qu|jusqu|lorsqu|puisqu|quoiqu)'(.+)$", re.I)
_KEEP_WHOLE = {"aujourd'hui", "quelqu'un", "quelqu'une", "presqu'île", "prud'homme", "prud'hommes", "c'est-à-dire",
               "d'abord", "d'accord", "d'ailleurs", "d'emblée", "d'ores", "d'autant", "d'après"}
_INVERSION = re.compile(r"^(.+?)-(?:t-)?(je|tu|il|elle|on|nous|vous|ils|elles|ce|y|en|le|la|les|lui|leur|moi|toi)$", re.I)
LEMMA_OVERRIDES = {"la": "le", "les": "le", "une": "un", "elle": "il", "elles": "il", "ils": "il", "cette": "ce",
                   "cet": "ce", "ces": "ce", "ma": "mon", "mes": "mon", "ta": "ton", "tes": "ton", "sa": "son",
                   "ses": "son", "nos": "notre", "vos": "votre", "leurs": "leur", "toute": "tout", "tous": "tout",
                   "toutes": "tout", "aux": "au", "des": "de", "du": "de"}
_FUNCTION_LEMMA = {"la": "le", "les": "le", "une": "un", "des": "de", "du": "de", "au": "à", "aux": "à", "cette": "ce",
                   "cet": "ce", "ces": "ce", "ma": "mon", "mes": "mon", "ta": "ton", "tes": "ton", "sa": "son",
                   "ses": "son", "nos": "notre", "vos": "votre", "leurs": "leur", "elle": "il", "elles": "il",
                   "ils": "il", "toute": "tout", "tous": "tout", "toutes": "tout"}


_CE_PRONOUN_NEXT = {"qui", "que", "qu'", "dont", "sont", "est", "sera", "serait", "seront", "soit", "fut", "furent",
                    "ne", "n'", "doit", "peut", "pourrait", "devrait", "à"}


def split_token(t):
    """l'eau -> l' + eau; a-t-il -> a + il; aujourd'hui stays whole. Original case of the base is kept."""
    low = t.lower()
    if low in _KEEP_WHOLE:
        return [t]
    m = _ELISION.match(t)
    if m:
        rest = t[len(m.group(1)) + 1:]
        return [m.group(1).lower() + "'"] + split_token(rest)
    m = _INVERSION.match(t)
    if m and len(m.group(1)) >= 1 and low not in ("peut-être", "celui-là", "celle-là", "ceux-là", "au-delà", "là-bas"):
        return [m.group(1), m.group(2)]
    return [t]


def lower_ok_capital(lw, cands):
    return False


def opener_hint(low, toks, tags):
    """Gérondif or present participle opening the sentence: « En comparant ... », « S'appuyant sur ... »."""
    if re.match(r"^(?:tout )?en [a-zà-ÿ]+ant\b", low) or re.match(r"^(?:s'|se )?[a-zà-ÿ]{3,}ant\b", low) and \
            low.split()[0] not in PARTICIPIAL_EXCLUDE and (tags and "VERB" in tags[:2]):
        return "participial"
    return None


def guess_tag(w, first, known):
    lw = w.lower()
    if w[:1].isupper() and not first:
        return "PROPN"
    if lw.endswith(("emment", "amment")):
        return "ADV"
    if lw.endswith("ment") and len(lw) > 7:
        # Unknown -ment word: adverbs are built on a feminine adjective (statistique-ment, expérimentale-ment),
        # nouns on a verb stem (échantillonne-ment). Decide from the adjective-like ending of the stem.
        stem = lw[:-4]
        if stem.endswith(("ique", "elle", "ale", "ive", "euse", "aire", "ble", "ière", "ète", "oire", "ine",
                          "aine", "ique", "iste", "ente", "ante", "ue", "ie", "ée")):
            return "ADV"
        return "NOUN"
    if lw.endswith(("tion", "tions", "sion", "sions", "ité", "ités", "isme", "ismes", "ance", "ances", "ence",
                    "ences", "eur", "eurs", "age", "ages", "ure", "ures", "logie", "logies", "graphie")):
        return "NOUN"
    if lw.endswith(("ique", "iques", "able", "ables", "ible", "ibles", "eux", "euse", "euses", "if", "ifs", "ive",
                    "ives", "al", "ale", "ales", "aux", "aire", "aires", "el", "elle", "els", "elles", "ien",
                    "ienne", "iens", "iennes", "oire", "oires", "ïde", "ïdes")):
        return "ADJ"
    if lw.endswith(("er", "ir", "ant", "ée", "ées", "és", "é", "ait", "aient", "ons", "ez", "eront", "era",
                    "isent", "issent", "iser", "ifier")):
        return "VERB"
    return "NOUN"


def disambiguate(lw, cands, toks, tags, i, lex):
    """A few context rules for French homographs (le/la/les, en, noun/verb pairs)."""
    kinds = {c[0]: c[1] for c in cands}
    nxt = toks[i + 1] if i + 1 < len(toks) else None
    nxt_tag = (lex.get(nxt) or [(None, None)])[0][0] if nxt else None
    pw = toks[i - 1] if i > 0 else None
    pt = tags[i - 1] if i > 0 else None
    if lw == "ce" and nxt in _CE_PRONOUN_NEXT:               # ce qui, ce que, ce sont, ce n'est pas
        return ("PRON", "c'")
    if lw in ("le", "la", "les") and "PRON" in kinds and nxt_tag in ("VERB", "AUX") and pt != "ADP":
        return ("PRON", kinds["PRON"])
    if lw == "en" and "PRON" in kinds and nxt_tag in ("VERB", "AUX") and not (nxt or "").endswith("ant"):
        return ("PRON", kinds["PRON"])
    if "NOUN" in kinds and ("VERB" in kinds or "AUX" in kinds):
        v = "VERB" if "VERB" in kinds else "AUX"
        if pt in ("DET", "NUM") or pw in ("l'", "d'", "de", "du", "des", "au", "aux"):
            return ("NOUN", kinds["NOUN"])
        if pw in SUBJECT_PRONOUNS or pw in ("ne", "n'", "se", "s'", "me", "m'", "te", "t'", "y", "nous", "vous"):
            return (v, kinds[v])
        if pw in ("à", "pour", "sans", "de") and lw.endswith(("er", "ir", "re", "oir")):
            return (v, kinds[v])
    if "ADJ" in kinds and "VERB" in kinds and pw in BE_FORMS and cands[0][0] == "ADJ":
        return None
    return None


def lemma(w, tag, known):
    """Lemma for words missing from the lexicon: undo the regular plural and feminine."""
    if w in _FUNCTION_LEMMA:
        return _FUNCTION_LEMMA[w]
    if len(w) <= 3 or "-" in w:
        return w
    if w.endswith("aux") and w[:-3] + "al" in known:
        return w[:-3] + "al"
    if w.endswith(("s", "x")) and w[:-1] in known:
        return w[:-1]
    if tag in ("ADJ", "NOUN") and w.endswith("es") and w[:-2] in known:
        return w[:-2]
    if tag == "ADJ" and w.endswith("e") and w[:-1] in known:
        return w[:-1]
    if w.endswith("s") and tag in ("NOUN", "ADJ", "PROPN") and len(w) > 4:
        return w[:-1]
    return w


def lemma_candidates(tok, lem):
    yield lem
    yield tok


def is_nominalization(tok, lem, tag):
    w = (lem or tok).lower()
    return tag == "NOUN" and len(w) >= 7 and w.endswith(NOMINAL_SUFFIXES) and w not in NOMINAL_EXCLUDE


def is_derived_adverb(tok, tag):
    """Adverbes en -ment (the French counterpart of -ly adverbs): 'considérablement', 'notamment'."""
    return tag == "ADV" and tok.endswith("ment") and len(tok) > 6 and tok not in LY_EXCLUDE


def is_participle(tok, tag):
    return tok in IRREGULAR_PARTICIPLES or (tok.endswith(("é", "ée", "és", "ées", "i", "ie", "is", "ies", "u", "ue", "us", "ues")) and tag in ("VERB", "ADJ") and len(tok) > 3)


def passive(toks, tags):
    """être + (adverbes) + participe passé, hors verbes à auxiliaire être et verbes pronominaux."""
    for i, w in enumerate(toks):
        if w in BE_FORMS and w not in ("être", "étant") or w in ("être",):
            if i > 0 and toks[i - 1] in REFLEXIVES:
                continue
            if i > 1 and toks[i - 2] in REFLEXIVES and toks[i - 1] in ("est", "sont", "était", "étaient"):
                continue
            for j in range(i + 1, min(i + 4, len(toks))):
                x = toks[j]
                if x in ETRE_VERB_PARTICIPLES:
                    break
                if is_participle(x, tags[j]) and x not in PASSIVE_SKIP:
                    return True
                if not (x.endswith("ment") or x in PASSIVE_SKIP):
                    break
    return False


# --- calibrated marker words [C] ---------------------------------------------------------------
# Not hand-written: derived from the calibration corpora by log-odds with an informative Dirichlet prior
# (calibration/tools/build_markers.py; method and held-out results in references/calibration.md). GLUE_LEMMAS
# are the most frequent grammatical words of the language, which current models use far less than people do.
import textcore as _T  # noqa: E402
MARKERS = _T.load_markers("fr")
GLUE_LEMMAS = MARKERS.get("glue") or ["le", "de", "être", "à"]
GLUE_REFERENCE = MARKERS.get("glue_reference") or 26.0      # human median, glue words per 100 tokens
MARKER_AI_FUNCTION = MARKERS.get("ai_function", [])
MARKER_HUMAN_FUNCTION = MARKERS.get("human_function", [])
MARKER_AI_CONTENT = MARKERS.get("ai_content", [])
MARKER_HUMAN_CONTENT = MARKERS.get("human_content", [])

# --- registre des faits (fact ledger) -----------------------------------------------------------------
NUMWORDS = {"zéro": 0, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9,
            "dix": 10, "onze": 11, "douze": 12, "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16,
            "vingt": 20, "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60, "cent": 100,
            "dizaine": 10, "douzaine": 12, "vingtaine": 20, "trentaine": 30, "centaine": 100, "millier": 1000,
            "triple": 3, "quadruple": 4}
# compound numerals up to 99: dix-huit, vingt et un, vingt-cinq, soixante-douze, quatre-vingt-dix-neuf
_UNITS = (("un", 1), ("une", 1), ("deux", 2), ("trois", 3), ("quatre", 4), ("cinq", 5), ("six", 6), ("sept", 7),
          ("huit", 8), ("neuf", 9))
_TEENS = (("dix", 10), ("onze", 11), ("douze", 12), ("treize", 13), ("quatorze", 14), ("quinze", 15), ("seize", 16),
          ("dix-sept", 17), ("dix-huit", 18), ("dix-neuf", 19))
NUMWORDS.update({"dix-sept": 17, "dix-huit": 18, "dix-neuf": 19, "quatre-vingt": 80, "quatre-vingts": 80})
for _t, _tv in (("vingt", 20), ("trente", 30), ("quarante", 40), ("cinquante", 50), ("soixante", 60),
                ("septante", 70), ("huitante", 80), ("octante", 80), ("nonante", 90)):
    NUMWORDS[_t] = _tv
    for _u, _uv in _UNITS:
        for _f in (("%s et %s", "%s-et-%s") if _uv == 1 else ("%s-%s",)):
            NUMWORDS[_f % (_t, _u)] = _tv + _uv
for _u, _uv in _UNITS:
    NUMWORDS["quatre-vingt-%s" % _u] = 80 + _uv
for _b, _bv in (("soixante", 60), ("quatre-vingt", 80)):
    for _n, _nv in _TEENS:
        for _f in (("%s et %s", "%s-et-%s") if (_b == "soixante" and _nv == 11) else ("%s-%s",)):
            NUMWORDS[_f % (_b, _n)] = _bv + _nv
SCALE = {"cent": 1e2, "cents": 1e2, "mille": 1e3, "million": 1e6, "millions": 1e6, "milliard": 1e9, "milliards": 1e9}
PERCENT_WORDS = r"(?:pour cent|pourcent|p\. ?100)"
DECIMAL_COMMA = True
NOT_AUTHORS = {"janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
               "novembre", "décembre", "en", "depuis", "dès", "avant", "après", "vers", "entre", "jusqu'en", "début",
               "fin", "printemps", "été", "automne", "hiver", "figure", "tableau", "voir", "année", "version",
               "étude", "phase", "loi", "décret", "recensement", "le", "la", "les", "de", "du"}
LEDGER_HEDGES = ["peut-être", "probablement", "vraisemblablement", "possiblement", "éventuellement", "apparemment",
                 "semble", "semblent", "semblait", "semblerait", "paraît", "paraissent", "suggère", "suggèrent",
                 "pourrait", "pourraient", "environ", "approximativement", "sans doute", "il se peut",
                 "il est possible que", "tend à", "tendent à", "en partie", "dans une certaine mesure"]
LEDGER_BOOSTERS = ["clairement", "évidemment", "certainement", "assurément", "indéniablement", "incontestablement",
                   "démontre", "démontrent", "prouve", "prouvent", "établit", "sans aucun doute", "bien sûr",
                   "il est clair que", "il est évident que", "manifestement"]

# --- typographie française: conventions vérifiables [L] ---------------------------------------------------
# (regex on the raw text, label, what the convention is). Reported, never gated.
TYPOGRAPHY = [
    (r"[A-Za-zÀ-ÿ0-9»\"')][;:!?](?=\s|$)", "ponctuation haute sans espace avant (« mot: » au lieu de « mot : »)"),
    (r"(?<![\w«])\"[^\"\n]{2,200}\"", "guillemets droits \"…\" au lieu de « … »"),
    (r"[A-Za-zÀ-ÿ]—[A-Za-zÀ-ÿ]", "tiret cadratin collé (usage anglais) au lieu d'un tiret d'incise espacé"),
    (r"\b\d+\.\d+\s?%", "point décimal devant % (3.5 %) au lieu de la virgule (3,5 %)"),
    (r"\betc\.{2,}|\betc…", "« etc... » au lieu de « etc. »"),
    (r"\b\d+(?:ème|ième)s?\b", "ordinal en « ème » (2ème) au lieu de « e » (2e)"),
]
