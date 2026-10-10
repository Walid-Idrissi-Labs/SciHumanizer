"""English language pack for SciHumanizer.

Every list notes where it comes from:
  [R] reported in the research analysed for this skill (references/research-digest.md)
  [P] practitioner-observed tell (e.g. Wikipedia "Signs of AI writing"), not measured in those papers
  [L] standard linguistic operationalisation (Biber 1988; Hyland 2005; plain-language style guides)
  [C] confirmed or derived by this skill's own calibration (references/calibration.md)
Single words are LEMMAS (dictionary forms) unless noted; multi-word entries are matched as phrases.
"""
import re

NAME = "English"

# --- sentence splitting ----------------------------------------------------------------
ABBREVIATIONS = {"e.g", "i.e", "etc", "vs", "cf", "al", "fig", "figs", "eq", "eqs", "ref", "refs",
                 "dr", "mr", "mrs", "ms", "prof", "st", "no", "nos", "approx", "ca", "jr", "sr", "inc",
                 "ltd", "co", "corp", "dept", "univ", "vol", "vols", "pp", "p", "sec", "ch", "chap",
                 "tab", "suppl", "resp", "est", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep",
                 "sept", "oct", "nov", "dec", "u.s", "u.k", "a.m", "p.m", "ph.d", "m.sc", "b.sc",
                 "viz", "incl", "n.b", "e.u", "u.n", "op", "cit", "ibid", "ed", "eds", "rev", "gen",
                 "gov", "sen", "rep", "mt", "ft", "sq", "wt", "var", "sp", "spp", "subsp"}
SENTENCE_FINAL_ABBREV = {"al", "etc"}
SENTENCE_STARTERS = {"the", "this", "these", "those", "that", "they", "we", "it", "in", "however",
                     "our", "their", "a", "an", "such", "as", "for", "when", "while", "although",
                     "but", "and", "here", "there", "to", "on", "at", "by", "with", "from", "his",
                     "her", "its", "several", "many", "most", "some", "other", "others", "both",
                     "further", "moreover", "similarly", "thus", "therefore", "hence", "after",
                     "before", "since", "because", "if", "one", "two", "three", "each", "all"}

# --- closed classes [L] -----------------------------------------------------------------
FIRST_PERSON = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}
THIRD_PERSON = {"he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
                "they", "them", "their", "theirs", "themselves"}
SUBJECT_PRONOUNS = {"i", "we", "you", "they", "he", "she", "it"}
MODALS = {"can", "could", "may", "might", "must", "shall", "should", "will", "would", "ought"}
BE_FORMS = {"am", "is", "are", "was", "were", "be", "been", "being"}
NEGATIONS = ["not", "no", "never", "none", "nor", "neither", "nobody", "nothing", "nowhere", "n't",
             "cannot", "without", "lack", "lacks", "lacked", "absence", "absent", "fail", "fails", "failed"]
COORDINATORS = {"and", "but", "or", "so", "yet", "nor"}
AND_OR = {"and", "or"}
SUBORDINATORS = {"because", "although", "though", "while", "whereas", "when", "whenever", "if",
                 "unless", "since", "as", "after", "before", "until", "once", "whether", "where",
                 "wherever", "given", "even", "how", "why", "what", "which", "who", "whoever"}
PREPOSITIONS = {"in", "on", "at", "for", "with", "by", "from", "during", "among", "across", "under",
                "over", "through", "within", "without", "between", "despite", "unlike", "like",
                "of", "to", "into", "onto", "upon", "toward", "towards", "beyond", "against",
                "along", "around", "via", "per", "throughout", "near", "above", "below", "beneath",
                "behind", "beside", "besides", "outside", "inside", "amid", "amongst", "following",
                "regarding", "concerning", "compared", "after", "before", "since", "until"}
OF_WORD = "of"
STOPWORDS = set("""a about above after again against all almost also although am among an and any are as at
be because been before being below between both but by can could did do does doing down during each
either else even ever every few for from further had has have having he her here hers herself him
himself his how however i if in into is it its itself just least less let like may me might more most
much must my myself neither no nor not now of off often on once only or other others otherwise ought
our ours ourselves out over own per perhaps quite rather really same shall she should since so some
still such than that the their theirs them themselves then there therefore these they this those
though through thus to too toward towards under until up upon us very via was we well were what when
where whether which while who whom whose why will with within without would yet you your yours
yourself yourselves s t n't 's 're 've 'll 'd 'm one two three first second also""".split())

# --- function-word profile [R] ------------------------------------------------------------
# Survey of 44 studies (arXiv:2510.05136), citing Desaire et al., Kim & Desaire, Fujiwara.
AI_FAVORED_FW = ["and", "can", "by", "with", "for", "their"]
HUMAN_FAVORED_FW = ["however", "but", "although", "because", "if", "that", "or", "when", "as",
                    "this", "i", "they", "my", "it", "us", "to", "will", "would", "might", "could",
                    "up", "out", "off"]

# --- connectives [R]+[L] --------------------------------------------------------------------
CONNECTIVES = {
    "additive": ["additionally", "furthermore", "moreover", "in addition", "also", "further",
                 "besides", "likewise", "similarly", "equally", "what is more", "on top of that", "as well"],
    "contrastive": ["however", "but", "yet", "although", "though", "even though", "whereas",
                    "nevertheless", "nonetheless", "still", "instead", "conversely",
                    "on the other hand", "in contrast", "by contrast", "rather", "even so",
                    "that said", "despite this", "all the same", "then again"],
    "causal": ["because", "since", "so", "therefore", "thus", "hence", "consequently",
               "as a result", "accordingly", "for this reason", "that is why", "this is why"],
    "conditional": ["if", "unless", "otherwise", "in that case", "provided that", "even if"],
    "exemplifying": ["for example", "for instance", "such as", "e.g.", "namely", "in particular",
                     "specifically", "to illustrate"],
    "sequencing": ["first", "firstly", "second", "secondly", "third", "thirdly", "finally",
                   "lastly", "next", "then", "to begin with", "subsequently", "meanwhile"],
    "summarizing": ["overall", "in conclusion", "in summary", "to summarize", "to sum up",
                    "ultimately", "in short", "taken together", "collectively", "all in all",
                    "in essence", "in sum", "to conclude", "all told", "in the end"],
    "emphatic": ["indeed", "notably", "importantly", "crucially", "significantly", "in fact",
                 "clearly", "of course", "particularly", "especially", "critically",
                 "most importantly", "above all", "undeniably", "essentially"],
}
FORMULAIC_CONNECTIVE_CLASSES = ("additive", "summarizing", "emphatic")
LOGICAL_CONNECTIVE_CLASSES = ("contrastive", "causal", "conditional")
# not counted as sentence-initial connectives: they open subordinate or coordinate structures
NOT_ADVERBIAL = SUBORDINATORS | COORDINATORS | {"even though", "even if", "whereas", "though", "although",
                                               "because", "if", "unless", "since", "as", "when", "while"}
# count as sentence-initial connectives only when followed by a comma
NEED_COMMA = {"then", "still", "first", "second", "third", "next", "rather", "further", "also", "overall",
              "finally", "such as", "similarly", "equally", "instead", "otherwise", "meanwhile", "besides"}
UNAMBIGUOUS_CONNECTIVES = {"however", "moreover", "furthermore", "additionally", "consequently", "therefore", "thus",
                           "hence", "nevertheless", "nonetheless", "in addition", "in contrast", "by contrast",
                           "on the other hand", "as a result", "for example", "for instance", "in conclusion",
                           "in summary", "ultimately", "notably", "importantly", "although", "though", "whereas",
                           "because", "unless", "indeed", "in fact", "crucially", "conversely", "accordingly",
                           "similarly", "likewise", "taken together", "collectively", "specifically", "in particular"}

# --- stance (Hyland 2005) [L]; AI shows fewer epistemic markers and less involvement [R] ----
HEDGES = {"lemmas": ["may", "might", "could", "perhaps", "possibly", "probably", "likely", "unlikely",
                     "seem", "appear", "suggest", "tend", "somewhat", "approximately", "roughly",
                     "largely", "presumably", "arguably", "apparently", "plausibly", "tentatively",
                     "speculate", "speculative", "unclear", "uncertain"],
          "phrases": ["in part", "to some extent", "i think", "we think", "i suspect", "we suspect",
                      "i believe", "we believe", "in our view", "in my view", "as far as we know",
                      "not necessarily"]}
BOOSTERS = {"lemmas": ["clearly", "obviously", "certainly", "definitely", "undoubtedly", "indeed",
                       "surely", "always", "never", "must", "demonstrate", "prove", "establish",
                       "conclusively", "decisively", "strongly"],
            "phrases": ["in fact", "of course", "without doubt", "no doubt"]}
ATTITUDE = {"lemmas": ["surprisingly", "unfortunately", "interestingly", "remarkably", "strikingly",
                       "disappointingly", "curiously", "oddly", "strangely", "fortunately", "hopefully",
                       "admittedly", "frankly", "regrettably", "unexpectedly", "puzzlingly", "ironically",
                       "surprising", "unexpected", "remarkable", "striking", "disappointing", "puzzling",
                       "odd", "strange", "troubling", "worrying", "encouraging", "unfortunate", "curious",
                       "counterintuitive", "counter-intuitive", "annoying", "frustrating", "impressive",
                       "wrong", "misleading", "overstated", "overlooked", "dubious", "questionable"],
            "phrases": []}
CASE_SENSITIVE_WORDS = {"may", "will", "can", "mark", "bill"}       # skip when capitalised mid-sentence

# --- evaluative vocabulary [R: MAGE emotion sanitisation; survey: neutral tone] ----------------
CRITICAL_LEMMAS = ["problem", "problematic", "fail", "failure", "poor", "poorly", "weak", "weakness",
                   "flaw", "flawed", "wrong", "error", "mistake", "mistaken", "bias", "biased", "lack",
                   "lacking", "unclear", "inconsistent", "contradict", "disappointing", "worse", "worst",
                   "bad", "unfortunately", "limitation", "shortcoming", "concern", "misleading",
                   "overestimate", "underestimate", "doubt", "doubtful", "unreliable", "noisy", "costly",
                   "expensive", "slow", "fragile", "brittle", "hate", "terrible", "awful", "annoying",
                   "frustrating", "angry", "rude", "broken", "useless", "confusing", "harm", "harmful",
                   "risk", "risky"]
PROMO_LEMMAS = ["crucial", "vital", "essential", "pivotal", "key", "robust", "comprehensive",
                "innovative", "promising", "exciting", "remarkable", "powerful", "seamless",
                "seamlessly", "cutting-edge", "groundbreaking", "transformative", "unprecedented",
                "invaluable", "holistic", "vibrant", "rich", "profound", "exceptional", "outstanding",
                "excellent", "incredible", "incredibly", "amazing", "valuable", "enhance", "empower",
                "revolutionize", "revolutionary", "game-changing", "impressive", "compelling", "dynamic",
                "thriving", "flourishing", "unparalleled", "state-of-the-art", "unique", "stunning",
                "delightful", "knowledgeable"]

# --- LLM-typical single words [P]; reported, not gated (several are real terms in some fields) --
AI_VOCAB_LEMMAS = ["delve", "foster", "bolster", "streamline", "elevate", "empower", "leverage", "showcase",
                   "underscore", "harness", "pivotal", "multifaceted", "seamless", "seamlessly", "holistic",
                   "paramount", "meticulous", "meticulously", "commendable", "noteworthy", "intricate",
                   "intricacy", "invaluable", "transformative", "groundbreaking", "unparalleled", "vibrant",
                   "bustling", "nestled", "tapestry", "landscape", "realm", "testament", "interplay", "synergy"]

# --- stock formulas: (regex, label, source), matched case-insensitively -----------------------
STOCK_PATTERNS = [
    (r"\bit is (?:important|worth|essential|crucial|critical|vital|imperative) (?:to note|noting|to remember|to recognize|to emphasize|to highlight|to acknowledge)\b", "it-is-important-to-note", "R"),
    (r"\bit (?:can|could|should|must) be (?:observed|noted|seen|argued|concluded) that\b", "it-can-be-observed-that", "R"),
    (r"\bin conclusion\b", "in-conclusion", "R"),
    (r"\bnot only\b[^.;:!?]{1,80}\bbut(?: also)?\b", "not-only-but-also", "R"),
    (r"\b(?:i|we) apologi[sz]e for (?:the|any) inconvenience\b", "corporate-apology", "R"),
    (r"\bwe strive to\b", "corporate-strive", "R"),
    (r"\b(?:please )?(?:do not hesitate|feel free) to contact\b", "corporate-contact", "R"),
    (r"\bincredibly (?:polite|friendly|helpful|knowledgeable|attentive|delicious)\b", "incredibly-positive", "R"),
    (r"\bstand-?out feature\b", "stand-out-feature", "R"),
    (r"\bplays? an? (?:crucial|pivotal|vital|key|significant|critical|central|important|essential|major|instrumental) role\b", "plays-a-crucial-role", "P"),
    (r"\bin today'?s (?:world|society|digital age|fast-paced|rapidly|ever|increasingly|interconnected|modern)\b", "in-todays-world", "P"),
    (r"\bin the (?:realm|landscape|world) of\b", "in-the-realm-of", "P"),
    (r"\b(?:delve|delves|delving|delved) into\b", "delve-into", "P"),
    (r"\b(?:a|the) (?:rich )?tapestry of\b", "tapestry-of", "P"),
    (r"\b(?:is|are|stands as|serves as) a testament to\b", "testament-to", "P"),
    (r"\b(?:serves?|stands?|acts?) as an? (?:powerful |key |crucial |vital |important |essential |stark |poignant )?(?:reminder|example|catalyst|cornerstone|foundation|bridge|beacon|testament)\b", "serves-as-a", "P"),
    (r"\b(?:shed|sheds|shedding) (?:new )?light on\b", "shed-light-on", "P"),
    (r"\b(?:pave|paves|paved|paving) the way\b", "pave-the-way", "P"),
    (r"\b(?:remains|remain) to be seen\b", "remains-to-be-seen", "P"),
    (r"\bdouble-edged sword\b", "double-edged-sword", "P"),
    (r"\bnavigat(?:e|es|ing) the (?:complexities|challenges|intricacies|landscape)\b", "navigate-the-complexities", "P"),
    (r"\b(?:unlock|unlocks|unlocking|harness|harnesses|harnessing) (?:the )?(?:full )?(?:power|potential)\b", "unlock-the-potential", "P"),
    (r"\b(?:a|the) (?:deeper|better|nuanced|more nuanced|holistic|comprehensive) understanding of\b", "deeper-understanding-of", "P"),
    (r"\bin recent years\b", "in-recent-years", "P"),
    (r"\b(?:the )?(?:rapid|recent|ongoing) (?:advancement|advancements|evolution|proliferation|growth) (?:of|in)\b", "rapid-advancement-of", "P"),
    (r"\bhas (?:emerged|become) (?:as )?(?:an? )?(?:increasingly |particularly )?(?:important|critical|crucial|key|essential|powerful|popular|prominent|central|vital)\b", "has-emerged-as", "P"),
    (r"\bwith the advent of\b|\bthe advent of\b", "advent-of", "P"),
    (r"\b(?:a|an) (?:myriad|plethora|multitude) of\b|\bmyriad\b", "myriad-plethora", "P"),
    (r"\b(?:intricate|complex|dynamic|delicate) (?:interplay|relationship) (?:between|of)\b", "intricate-interplay", "P"),
    (r"\b(?:valuable|key|critical|important|novel|deeper|meaningful) insights? (?:into|on)\b", "valuable-insights-into", "P"),
    (r"\b(?:underscores?|underscoring|highlights?|highlighting|emphasi[sz]es?|emphasi[sz]ing|reinforces?|illustrates?) the (?:importance|need|significance|value|potential|critical role|necessity|urgency)\b", "underscores-the-importance", "P"),
    (r"\b(?:it'?s|it is) not (?:just|only|merely|simply) (?:about )?[^.;:!?]{1,60}[,;:—-]+ ?(?:it'?s|it is|but)\b", "not-just-x-its-y", "P"),
    (r"\bever-(?:evolving|changing|growing|expanding|increasing)\b", "ever-evolving", "P"),
    (r"\b(?:embark|embarks|embarking) on\b", "embark-on", "P"),
    (r"\b(?:game[- ]changer|game[- ]changing|paradigm shift)\b", "game-changer", "P"),
    (r"\bat the (?:heart|core|forefront|intersection) of\b", "at-the-heart-of", "P"),
    (r"\b(?:a|the) (?:key|critical|crucial|vital|essential|fundamental) (?:component|aspect|factor|element|pillar)\b", "a-key-component", "P"),
    (r"\b(?:only time will tell|the future (?:looks|is) (?:bright|promising)|exciting (?:times|possibilities|future))\b", "rosy-ending", "P"),
]
SIGNIFICANCE_ECHO = (r"^(?:this|these|such|together,? these|taken together,? these|overall,? (?:this|these))\b[^.!?]{0,60}\b"
                     r"(?:highlight|highlights|underscore|underscores|demonstrate|demonstrates|illustrate|illustrates|"
                     r"emphasi[sz]e|emphasi[sz]es|reinforce|reinforces|reflect|reflects|show|shows|suggest|suggests|"
                     r"point to|points to|speak to|speaks to)\b[^.!?]{0,40}\b(?:importance|need|value|potential|role|"
                     r"significance|complexity|promise|necessity|relevance|power|urgency)\b")
STOCK_OPENERS = [
    r"^in (?:recent years|recent decades|today'?s|the modern era|an era|the past (?:few )?(?:years|decades?))",
    r"^(?:the )?(?:rapid|recent|ongoing|unprecedented) (?:advancement|advancements|growth|development|developments|evolution|rise|proliferation)",
    r"^(?:with|given) the (?:rapid|increasing|growing|recent|ever)",
    r"^as (?:\w+ ){1,4}continues? to (?:evolve|grow|advance|expand)",
    r"^[a-z][\w\- ]{0,40} (?:has|have) (?:become|emerged as) (?:an? )?(?:increasingly|a (?:critical|crucial|key|vital|central))",
    r"^(?:over|during) the (?:past|last) (?:few |several |two |three )?(?:years|decades?)",
    r"^the advent of",
    r"^(?:as|with) (?:global |average )?(?:temperatures|the climate|the planet|sea levels?|climate change) (?:rise|rises|rising|warms|warming|continues?)",
    r"^rising (?:global )?(?:temperatures|sea levels|costs|demand)",
    r"^imagine a world",
]
FORMULAIC_ENDING = (r"\b(?:in conclusion|in summary|to summarize|to sum up|overall|ultimately|taken together|collectively|"
                    r"in essence|moving forward|going forward|looking ahead|future (?:research|work|studies|directions?) "
                    r"(?:should|could|will|may|must)|pave the way|remains to be seen|only time will tell|"
                    r"promising (?:avenue|direction|future)|exciting (?:future|possibilities)|continue to (?:evolve|grow|shape))\b")
EXTRAPOSITION = (r"\bit (?:is|was|has been|may be|can be|should be|would be|remains?) (?:\w+ ){0,2}"
                 r"(?:important|essential|crucial|critical|worth|necessary|clear|evident|noteworthy|interesting|possible|"
                 r"likely|notable|vital|imperative|apparent) (?:to|that)\b")

# --- padding lexicons ---------------------------------------------------------------------
# Wordy constructions with a shorter equivalent (plain-language style guides) [L]
WORDY = ["in order to", "in order for", "due to the fact that", "owing to the fact that", "in light of the fact that",
         "in spite of the fact that", "despite the fact that", "the fact that", "in the event that", "in the event of",
         "at this point in time", "at the present time", "at the current time", "in the near future",
         "in the process of", "for the purpose of", "with the purpose of", "with the aim of", "with the goal of",
         "with regard to", "with regards to", "in regard to", "in relation to", "on the basis of",
         "by means of", "by virtue of", "in the context of", "in the field of", "in the area of", "in the realm of",
         "in a manner that", "in such a way that", "in a way that", "to the extent that", "a large number of",
         "a wide range of", "a wide variety of", "a broad range of", "a variety of", "a range of", "the majority of",
         "a significant amount of", "a significant number of", "has the ability to", "have the ability to",
         "has the potential to", "have the potential to", "has the capacity to", "have the capacity to",
         "is able to", "are able to", "was able to", "were able to", "is capable of", "are capable of",
         "serves to", "serve to", "make use of", "makes use of", "making use of", "take into account",
         "takes into account", "taking into account", "take into consideration", "it is clear that",
         "it is evident that", "it is obvious that", "it is possible that", "it is likely that", "it is true that",
         "there is a need to", "there is a need for", "there is no doubt that", "it goes without saying",
         "needless to say", "as a matter of fact", "for all intents and purposes", "each and every",
         "first and foremost", "when it comes to", "the ways in which", "the way in which", "the extent to which",
         "the degree to which", "the manner in which", "as well as", "in terms of", "in addition to",
         "plays a role in", "play a role in", "is essential for", "is crucial for", "is critical for",
         "whether or not", "on a regular basis", "on a daily basis", "at all times", "in close proximity"]
# Text talking about itself or announcing what it will do [L]
METADISCOURSE = ["this section", "this paper will", "this essay will", "this article will", "this chapter will",
                 "in this section", "in what follows", "as mentioned above", "as mentioned earlier",
                 "as mentioned previously", "as noted above", "as noted earlier", "as discussed above",
                 "as discussed earlier", "as described above", "as we have seen", "as we will see",
                 "as stated earlier", "as stated above", "as previously mentioned", "it is worth noting",
                 "it is worth mentioning", "it should be noted", "it is important to note", "it bears mentioning",
                 "note that", "in other words", "that is to say", "to put it simply", "simply put",
                 "put differently", "put another way", "let us", "let's", "consider the following",
                 "the following section", "we now turn to", "turning to", "before discussing", "having established",
                 "with this in mind", "with that in mind", "it is also worth", "what this means is",
                 "here's the thing", "the key takeaway", "the bottom line"]
# Abstract framing nouns that carry little content by themselves (shell nouns: Schmid 2000) [L]
SHELL_NOUNS = ["importance", "significance", "role", "aspect", "factor", "element", "component", "challenge",
               "opportunity", "implication", "consideration", "landscape", "framework", "dynamic", "complexity",
               "nature", "realm", "potential", "insight", "perspective", "initiative", "dimension", "facet",
               "cornerstone", "foundation", "driver", "catalyst", "stakeholder", "interplay", "synergy", "nuance",
               "intricacy", "trajectory", "paradigm", "ecosystem", "narrative", "journey", "lens", "approach",
               "strategy", "context", "issue", "concept", "notion", "phenomenon", "need", "ability", "capacity"]
DOUBLE_HEDGES = [r"\b(?:may|might|could|can) (?:potentially|possibly|perhaps|conceivably)\b",
                 r"\b(?:potentially|possibly|perhaps) (?:may|might|could)\b",
                 r"\b(?:seems?|appears?) to (?:suggest|indicate|imply)\b",
                 r"\b(?:may|might|could) (?:suggest|indicate|imply) that\b[^.;]{0,80}\b(?:may|might|could)\b",
                 r"\b(?:somewhat|relatively|fairly|rather) (?:likely|possible|unclear|uncertain)\b",
                 r"\bto some (?:extent|degree)\b[^.;]{0,60}\b(?:may|might|could)\b"]
EXPLETIVE_OPENER = r"^(?:there (?:is|are|was|were|has been|have been|exists?|remains?)|it (?:is|was) (?:\w+ ){0,2}(?:that|to))\b"

# --- morphology ----------------------------------------------------------------------------
NOMINAL_SUFFIXES = ("tion", "sion", "ment", "ness", "ity")          # Biber 1988 (+ -sion) [L]
NOMINAL_EXCLUDE = {"nation", "station", "ration", "portion", "potion", "lotion", "motion", "notion", "option",
                   "caution", "city", "pity", "entity", "moment", "cement", "garment", "comment", "segment",
                   "fragment", "element", "pigment", "sediment", "ointment", "torment", "question", "mention",
                   "section", "fraction", "business", "witness", "harness", "wilderness", "quality", "quantity",
                   "university", "community", "society"}
LY_EXCLUDE = {"only", "early", "likely", "daily", "weekly", "monthly", "yearly", "family", "rely", "apply",
              "supply", "reply", "fly", "italy", "july", "holy", "ugly", "silly", "friendly", "lonely", "unlikely"}
DEGREE_WORDS = {"more", "most", "less", "least", "better", "best", "worse", "worst"}
IRREGULAR_PARTICIPLES = set("""arisen awoken borne born beaten become begun bent bet bid bitten blown
broken brought built burnt burst bought cast caught chosen come cost crept cut dealt dug done drawn
dreamt drunk driven eaten fallen fed felt fought found fled flung flown forbidden forecast forgotten
forgiven frozen gotten given gone ground grown hung heard hidden hit held hurt kept knelt known laid
led leant leapt learnt left lent let lain lit lost made meant met mistaken overcome overtaken paid
proven put quit read ridden rung risen run said seen sought sold sent set sewn shaken shed shone shot
shown shrunk shut sung sunk sat slain slept slid slung spoken sped spent spilt spun spread sprung
stood stolen stuck stung stridden struck strung sworn swept swollen swum swung taken taught torn told
thought thrown thrust trodden understood undertaken upheld upset woken worn woven wept won wound
withdrawn withheld written""".split())
PASSIVE_SKIP = {"not", "also", "often", "then", "further", "being", "been", "well", "now", "still", "already",
                "usually", "generally", "typically"}
PARTICIPLE_FORM = r"(?:ing|ed)$"
MODAL_LEMMAS = set()            # English modals carry their own tag in the lexicon
ELIDING_FINALS = ()
SUBORD_PHRASES = ["even though", "even if", "as soon as", "so that", "given that", "provided that", "now that",
                  "in order to", "rather than"]
# Comment clause tacked on with a present participle: ", highlighting the need for ...", ", making it ...".
# AI text uses more present-participial clauses [R: Reinhart et al. 2024, via the survey]; the tail that
# restates significance is also a practitioner-observed tell [P]. The word after the participle must be a
# function word, which keeps out lists of gerunds ("running, swimming, and cycling").
PARTICIPIAL_CLAUSE = (r", (?:thereby |thus |further |ultimately |effectively |in turn |often |potentially )?([a-z]+ing)"
                      r"(?= (?:the|a|an|that|it|its|their|his|her|our|my|your|this|these|those|to|in|on|for|with|from|into|"
                      r"onto|up|out|off|over|how|what|whether|why|which|them|us|him|me|you|both|each|all|some|any|no|"
                      r"more|less|as|at|by|of|about|through|across|against|between|among|toward|towards|upon|within|"
                      r"without|new|further|only|not|one|two)\b)")
PARTICIPIAL_EXCLUDE = {"including", "according", "regarding", "concerning", "following", "during", "considering",
                       "excluding", "depending", "assuming", "notwithstanding", "barring", "pending", "owing",
                       "something", "nothing", "anything", "everything", "morning", "evening", "being"}

LEMMA_OVERRIDES = {}
CLITIC_TAGS = {"n't": ("ADV", "not"), "'s": ("PRT", "'s"), "'re": ("AUX", "be"), "'m": ("AUX", "be"),
               "'ve": ("AUX", "have"), "'ll": ("MODAL", "will"), "'d": ("MODAL", "would")}

_IRREG = {
    "is": "be", "are": "be", "was": "be", "were": "be", "been": "be", "being": "be", "am": "be",
    "has": "have", "had": "have", "having": "have", "does": "do", "did": "do", "done": "do", "doing": "do",
    "went": "go", "gone": "go", "goes": "go", "made": "make", "said": "say", "took": "take", "taken": "take",
    "came": "come", "saw": "see", "seen": "see", "got": "get", "gotten": "get", "gave": "give", "given": "give",
    "found": "find", "thought": "think", "told": "tell", "became": "become", "showed": "show", "shown": "show",
    "left": "leave", "felt": "feel", "brought": "bring", "began": "begin", "begun": "begin", "kept": "keep",
    "held": "hold", "wrote": "write", "written": "write", "stood": "stand", "heard": "hear", "meant": "mean",
    "met": "meet", "ran": "run", "paid": "pay", "sat": "sit", "spoke": "speak", "spoken": "speak", "led": "lead",
    "grew": "grow", "grown": "grow", "lost": "lose", "fell": "fall", "fallen": "fall", "sent": "send",
    "built": "build", "understood": "understand", "drew": "draw", "drawn": "draw", "broke": "break",
    "broken": "break", "spent": "spend", "rose": "rise", "risen": "rise", "drove": "drive", "driven": "drive",
    "bought": "buy", "wore": "wear", "worn": "wear", "chose": "choose", "chosen": "choose", "sought": "seek",
    "threw": "throw", "thrown": "throw", "caught": "catch", "dealt": "deal", "won": "win", "forgot": "forget",
    "forgotten": "forget", "laid": "lay", "knew": "know", "known": "know", "taught": "teach", "sold": "sell",
    "ate": "eat", "eaten": "eat", "flew": "fly", "flown": "fly", "lay": "lie", "lain": "lie", "hid": "hide",
    "hidden": "hide", "struck": "strike", "sang": "sing", "sung": "sing", "swam": "swim", "shook": "shake",
    "shaken": "shake", "arose": "arise", "arisen": "arise", "bore": "bear", "borne": "bear", "fed": "feed",
    "fought": "fight", "hung": "hang", "lent": "lend", "shot": "shoot", "slept": "sleep", "stuck": "stick",
    "swept": "sweep", "tore": "tear", "torn": "tear", "woke": "wake", "undertook": "undertake",
    "undertaken": "undertake", "withdrew": "withdraw", "withdrawn": "withdraw", "overcame": "overcome",
    "men": "man", "women": "woman", "children": "child", "feet": "foot", "teeth": "tooth", "mice": "mouse",
    "criteria": "criterion", "phenomena": "phenomenon", "analyses": "analysis", "hypotheses": "hypothesis",
    "theses": "thesis", "crises": "crisis", "indices": "index", "matrices": "matrix", "vertices": "vertex",
    "appendices": "appendix", "bacteria": "bacterium", "larvae": "larva", "lives": "life", "leaves": "leaf",
    "selves": "self", "halves": "half", "wolves": "wolf", "knives": "knife", "wives": "wife", "shelves": "shelf",
    "better": "good", "best": "good", "worse": "bad", "worst": "bad", "further": "far", "furthest": "far",
    "an": "a", "these": "this", "those": "that", "me": "i", "my": "i", "us": "we", "our": "we", "him": "he",
    "his": "he", "her": "she", "them": "they", "their": "they", "its": "it", "your": "you",
}
_S_KEEP = {"as", "this", "thus", "its", "his", "us", "is", "was", "has", "does", "yes", "less", "unless", "across",
           "always", "perhaps", "besides", "sometimes", "afterwards", "towards", "whereas", "analysis", "basis",
           "crisis", "thesis", "hypothesis", "emphasis", "synthesis", "diagnosis", "axis", "bias", "gas", "atlas",
           "lens", "news", "series", "species", "means", "diabetes", "measles", "rabies", "corps", "chaos",
           "cosmos", "ethos", "pathos", "kudos", "canvas", "alias", "campus", "census", "consensus", "corpus",
           "focus", "genus", "locus", "nexus", "radius", "status", "stimulus", "surplus", "syllabus", "virus",
           "bonus", "apparatus", "hiatus", "nucleus", "fungus", "cactus", "terminus", "exodus", "versus", "plus",
           "minus", "bus", "pus", "data", "media", "politics", "ethics", "physics", "mathematics", "economics",
           "statistics", "linguistics", "genetics", "dynamics", "mechanics", "electronics", "semantics"}


_BASE_FORMS = {"need", "feed", "seed", "weed", "heed", "speed", "breed", "bleed", "embed", "shed", "wed", "shred",
               "bring", "sing", "ring", "spring", "string", "swing", "cling", "fling", "sting", "wring", "sling"}


def split_token(t):
    """'don't' -> ['do', "n't"]; "Poisson's" -> ['Poisson', "'s"]; keeps the base's original case."""
    lw = t.lower()
    if lw.endswith("n't") and len(lw) > 3:
        base = {"ca": "can", "wo": "will", "sha": "shall"}.get(lw[:-3])
        return [base if base else t[:-3], "n't"]
    m = re.match(r"^(.+?)('s|'re|'ve|'ll|'d|'m)$", lw)
    if m:
        return [t[:len(m.group(1))], m.group(2)]
    return [t]


def lower_ok_capital(lw, cands):
    return False


def opener_hint(low, toks, tags):
    return None


def guess_tag(w, first, known):
    lw = w.lower()
    if w[:1].isupper() and not first:
        return "PROPN"
    if lw.endswith(("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ancy", "ency", "ism", "ist",
                    "ship", "hood", "ure", "ogy", "ics", "ers", "ors", "ists", "isms")):
        return "NOUN"
    if lw.endswith("ly"):
        return "ADV"
    if lw.endswith(("ous", "ful", "ive", "able", "ible", "al", "ic", "less", "ish", "ary", "ical")):
        return "ADJ"
    if lw.endswith(("ize", "ise", "ify", "izes", "ises", "ifies", "ized", "ised", "ified", "ed", "ing")):
        return "VERB"
    return "NOUN"


# a noun/verb homograph directly before one of these is a verb with its object ("needs a table")
_OBJECT_STARTERS = {"a", "an", "the", "my", "your", "his", "her", "its", "our", "their", "it", "them", "him", "us", "me"}
_POSSESSIVES = {"my", "your", "his", "her", "its", "our", "their"}
_VERB_SUBJECTS = {"who", "which", "nobody", "everyone", "everybody", "someone", "somebody", "anyone", "anybody",
                  "nothing", "something", "everything"}


def disambiguate(lw, cands, toks, tags, i, lex):
    """Noun/verb homographs ('use', 'study', 'increase'): decide from the previous token, then from
    the next one."""
    kinds = {c[0] for c in cands}
    if {"NOUN", "VERB"} <= kinds and i > 0:
        pt, pw = tags[i - 1], toks[i - 1]
        ppt = tags[i - 2] if i > 1 else None
        if pt in ("DET", "ADJ", "ADJC", "ADJS", "NUM", "PRT") or pw == "'s" or pw in _POSSESSIVES:
            return ("NOUN", None)
        if pt in ("TO", "MODAL") and lw.endswith("s") and not lw.endswith("ss") and lw[:-1] in lex:
            return ("NOUN", None)       # an infinitive is a base form: 'led to changes', not a verb
        if pt in ("TO", "MODAL") or pw in SUBJECT_PRONOUNS or (pw in ("not", "n't") and ppt in ("MODAL", "AUX")):
            return ("VERB", None)
        if pw in _VERB_SUBJECTS:
            return ("VERB", None)
        if pt != "ADP" and i + 1 < len(toks) and toks[i + 1] in _OBJECT_STARTERS:
            return ("VERB", None)
    return None


def _undouble(stem, known):
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
        return stem[:-1]
    if len(stem) > 2 and stem[-1] == stem[-2] and stem[:-1] in known and stem not in known:
        return stem[:-1]
    return None


def _strip(w, n, known):
    """Remove an n-letter inflectional ending, restoring a dropped 'e' or a doubled consonant."""
    stem = w[:-n]
    # A stem ending vowel+consonant would have doubled its consonant (hop -> hopped), so when the
    # e-form exists the word comes from it (hoped -> hope, used -> use, noted -> note).
    cvc = (len(stem) >= 2 and stem[-1] not in "aeiouwxy" and stem[-2] in "aeiou"
           and (len(stem) < 3 or stem[-3] not in "aeiou"))
    if cvc and stem + "e" in known:
        return stem + "e"
    if stem in known:
        return stem
    if stem + "e" in known:
        return stem + "e"
    und = _undouble(stem, known)
    if und:
        return und
    if stem.endswith("i") and len(stem) > 2:
        return stem[:-1] + "y"
    return w if len(stem) <= 2 else stem


def lemma(w, tag, known):
    """Rule-based English lemma: irregular table, then -s / -ed / -ing / -er / -est stripping with the
    lexicon as the list of known words. Aims at consistency (studies = study), not perfection."""
    w = re.sub(r"'s$|'$", "", w)
    if w in _IRREG:
        return _IRREG[w]
    if len(w) <= 3 or "-" in w:
        return w
    if tag in ("NOUN", "VERB", "PROPN", "ACRO"):
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith(("sses", "shes", "ches", "xes", "zes")):
            return w[:-2]
        if w.endswith("s") and not w.endswith(("ss", "us", "is", "ous", "ics")) and w not in _S_KEEP:
            return w[:-1]
    if tag == "VERB":
        if w in _BASE_FORMS:
            return w
        if w.endswith("eed"):                       # agreed -> agree, but exceed, proceed, speed are base forms
            return w[:-1] if w[:-1] in known else w
        if w.endswith("ied") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("ed") and len(w) > 3:
            return _strip(w, 2, known)
        if w.endswith("ing") and len(w) > 4:
            return _strip(w, 3, known)
    if tag in ("ADJC", "ADVC") and w.endswith("er") and len(w) > 4:
        return _strip(w, 2, known)
    if tag == "ADJS" and w.endswith("est") and len(w) > 5:
        return _strip(w, 3, known)
    return w


def lemma_candidates(tok, lem):
    """Forms to look up in a lemma list: the lemma, the token, and plain stems for words the lexicon
    does not know (delving -> delve)."""
    yield lem
    yield tok
    if tok.endswith("ing") and len(tok) > 5:
        yield tok[:-3]
        yield tok[:-3] + "e"
    elif tok.endswith("ed") and len(tok) > 4:
        yield tok[:-2]
        yield tok[:-1]
    elif tok.endswith("es") and len(tok) > 4:
        yield tok[:-2]
        yield tok[:-1]
    elif tok.endswith("s") and len(tok) > 3:
        yield tok[:-1]


def is_nominalization(tok, lem, tag):
    w = lem if lem and lem.islower() else tok
    return len(w) >= 7 and w.endswith(NOMINAL_SUFFIXES) and w not in NOMINAL_EXCLUDE and tag in ("NOUN", "PROPN", None)


def is_derived_adverb(tok, tag):
    """-ly manner/degree/stance adverbs: the intensifier class ('dramatically', 'increasingly')."""
    return tag in ("ADV", "ADVC") and tok.endswith("ly") and tok not in LY_EXCLUDE


def is_participle(tok, tag):
    return (tok.endswith("ed") and len(tok) > 4) or tok in IRREGULAR_PARTICIPLES


def passive(toks, tags):
    """be/get + (adverbs) + past participle within three tokens."""
    for i, w in enumerate(toks):
        if w in BE_FORMS or w in ("get", "gets", "got", "gotten", "'re", "'m"):
            for j in range(i + 1, min(i + 4, len(toks))):
                x = toks[j]
                if is_participle(x, tags[j]):
                    if x == "used" and j + 1 < len(toks) and toks[j + 1] == "to":
                        break
                    return True
                if not (x.endswith("ly") or x in PASSIVE_SKIP):
                    break
    return False


# --- calibrated marker words [C] ---------------------------------------------------------------
# Not hand-written: derived from the calibration corpora by log-odds with an informative Dirichlet prior
# (calibration/tools/build_markers.py; method and held-out results in references/calibration.md). GLUE_LEMMAS
# are the most frequent grammatical words of the language, which current models use far less than people do.
import textcore as _T  # noqa: E402
MARKERS = _T.load_markers("en")
GLUE_LEMMAS = MARKERS.get("glue") or ["the", "of", "in", "be"]
GLUE_REFERENCE = MARKERS.get("glue_reference") or 15.5      # human median, glue words per 100 tokens
MARKER_AI_FUNCTION = MARKERS.get("ai_function", [])
MARKER_HUMAN_FUNCTION = MARKERS.get("human_function", [])
MARKER_AI_CONTENT = MARKERS.get("ai_content", [])
MARKER_HUMAN_CONTENT = MARKERS.get("human_content", [])

# --- fact ledger ---------------------------------------------------------------------------
NUMWORDS = {"zero": 0, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
            "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
            "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
            "dozen": 12, "twice": 2, "triple": 3, "thrice": 3}
for _t, _tv in (("twenty", 20), ("thirty", 30), ("forty", 40), ("fifty", 50), ("sixty", 60), ("seventy", 70),
                ("eighty", 80), ("ninety", 90)):
    for _u, _uv in (("one", 1), ("two", 2), ("three", 3), ("four", 4), ("five", 5), ("six", 6), ("seven", 7),
                    ("eight", 8), ("nine", 9)):
        NUMWORDS["%s-%s" % (_t, _u)] = NUMWORDS["%s %s" % (_t, _u)] = _tv + _uv      # twenty-five
SCALE = {"hundred": 1e2, "thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}
PERCENT_WORDS = r"(?:percent|per cent)"
DECIMAL_COMMA = False
NOT_AUTHORS = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
               "november", "december", "in", "since", "by", "during", "until", "from", "after", "before", "around",
               "between", "early", "late", "mid", "spring", "summer", "autumn", "fall", "winter", "figure", "table",
               "see", "circa", "year", "fiscal", "version", "study", "phase", "act", "law", "census", "the"}
LEDGER_HEDGES = HEDGES["lemmas"] + ["seems", "seemed", "appears", "appeared", "suggests", "suggested", "tends",
                                    "tended"] + HEDGES["phrases"]
LEDGER_BOOSTERS = BOOSTERS["lemmas"] + ["demonstrates", "demonstrated", "proves", "proved", "establishes"] + BOOSTERS["phrases"]
