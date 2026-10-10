# French (`--lang fr`)

Read this before drafting or auditing French text. The loop, the ground rules, the gate and the
length rules in `SKILL.md` apply unchanged. This file gives what is specific to French: the
measured fingerprint, the habits and their fixes with French examples, the calibrated word
lists, typography, and the limits.

## Contents
1. Where the French rules come from
2. Running the scripts on French
3. The measured fingerprint
4. Pattern catalog (FR-1 to FR-13)
5. Calibrated word lists
6. Typography
7. The fact ledger in French
8. Limits

---

## 1. Where the French rules come from

None of the ten papers behind this skill gives a French fingerprint. Of the 44 studies in the
survey, 40 analyse English, and French appears in one, which does not report the languages
separately (research-digest §7). So every French rule here has one of three sources, marked in
the text:

- **[C] calibrated**: measured in this skill's own corpora. Human side: 223 French research
  articles (106 from PubMed Central, 117 from 64 OpenEdition journals in the humanities and
  social sciences), 192 abstracts (HAL and OpenEdition), and 333 general texts (The Conversation
  France, Wikinews, Wikipedia), all written before 2020. AI side: 140 texts from two current
  Claude tiers answering ordinary French requests on the same topics.
- **[R-analogue]**: the French counterpart of a habit that research documents for English
  (formulaic openers, stock formulas, comment clauses, missing stance). Checked as classic
  guards; the calibration says whether current models show them.
- **[P] practitioner**: commonly reported by editors and not measured here (calques from
  English, some stock phrases). Reported as pointers, never gated.

## 2. Running the scripts on French

```bash
python3 $S/scripts/sci_metrics.py analyze brouillon.md --register scientific --sentences
python3 $S/scripts/sci_metrics.py analyze tribune.md --register general --target-words 600 --source consigne.md
python3 $S/scripts/sci_metrics.py growth avant.md apres.md --register scientific --source notes.md
python3 $S/scripts/fact_ledger.py source.md brouillon.md --facts faits.md
```

- The language is detected from the text; `--lang fr` forces it (useful for a short text full of
  English terms).
- **Registers.** `scientific`: articles de recherche, mémoires, rapports (introduction and
  discussion style). `abstract`: résumés up to about 300 words. `general`: tribunes, articles de
  vulgarisation, presse, textes encyclopédiques, essais.
- **Counting.** `l'étude`, `qu'il`, `aujourd'hui`, `c'est-à-dire` and `a-t-on` are one word each.
  A lone `:`, `?`, `%` or `»` is not a word. For part-of-speech and lemma statistics the elided
  form is split (`l'` + `étude`), so `l'` counts as an article and `qu'` as *que*.
- **Tagging.** A lexicon of 61,425 forms (Lexique 3.83 and UD_French-GSD, both CC BY-SA 4.0)
  with context rules; 90.5% coarse-tag accuracy on the UD_French-GSD test set. Rates are
  reliable for a document, not for a single sentence.
- The report is in English; the examples in the fix lines are French.

## 3. The measured fingerprint

Medians, human → Sonnet tier / Haiku tier [C]. Scientific and general at 450 words, abstracts at
200.

| Habit | Scientific | Abstract | General |
|---|---|---|---|
| Mean sentence length (words) | 26.6 → 42.5 / 20.6 | 27.7 → 41.4 / 22.9 | 25.3 → 40.6 / 15.1 |
| Sentence-length variation (CV) | 0.454 → 0.329 / 0.332 | 0.360 → 0.203 / 0.209 | 0.455 → 0.377 / 0.459 |
| Commas per sentence | 1.59 → 3.00 / 1.10 | 1.20 → 2.40 / 1.05 | 1.53 → 2.86 / 1.07 |
| Paragraph-length variation (CV) | 0.423 → 0.236 / 0.213 | | 0.380 → 0.251 / 0.225 |
| Glue words (*être, en, avoir, dans*) per 100 tokens | 6.39 → 3.66 / 3.52 | 5.96 → 3.06 / 1.41 | 6.16 → 3.25 / 5.04 |
| Auxiliaries (% of tokens) | 3.47 → 1.49 / 1.57 | 2.81 → 0.94 / 0.00 | 3.25 → 1.22 / 3.15 |
| Lexical density | 0.510 → 0.542 / 0.573 | 0.525 → 0.548 / 0.591 | 0.514 → 0.546 / 0.548 |
| Mean word length (letters) | 5.40 → 5.93 / 6.24 | 5.64 → 5.96 / 6.58 | 5.14 → 5.73 / 5.76 |
| Word variety (MATTR-50 on lemmas) | 0.719 → 0.765 / 0.744 | 0.706 → 0.724 / 0.719 | 0.734 → 0.757 / 0.759 |
| Over-used content words per 1k | 4.51 → 16.1 / 24.2 | 5.18 → 9.35 / 36.6 | 3.24 → 12.5 / 15.6 |
| Demonstrative *ce / cette / ces* + noun, per 1k | 8.93 → 15.5 / 17.5 | 14.0 → 14.7 / 17.8 | 6.91 → 11.5 / 8.80 |
| Names + acronyms + numbers (% of tokens) | 5.26 → 1.55 / 1.48 | 3.69 → 0.94 / 1.23 | 7.39 → 1.79 / 4.83 |
| Parentheses per 1k words | 6.68 → 0 / 2.20 | 6.60 → 0 / 0 | 4.48 → 0 / 0 |
| Adverbs in *-ment* (% of tokens) | 0.84 → 1.70 / 1.70 | 0.62 → 1.37 / 1.03 | 0.67 → 1.53 / 1.57 |
| Adjectives (% of tokens) | 8.96 → 12.4 / 14.7 | 9.13 → 11.0 / 13.0 | 7.38 → 11.6 / 9.22 |
| Nominalisations per 1k | 50.3 → 68.7 / 84.6 | 70.9 → 80.6 / 108 | 35.8 → 66.5 / 57.6 |
| Sentences with ≥ 3 nominalisations | 0.18 → 0.50 / 0.25 | 0.29 → 0.60 / 0.41 | 0.07 → 0.48 / 0.07 |
| Abstract framing nouns per 1k | 6.65 → 10.9 / 15.5 | 9.83 → 14.4 / 20.9 | 2.92 → 6.10 / 8.81 |
| Comment clauses after a comma, per 1k | 0 → 0 / 4.38 | 0 → 0 / 4.90 | 0 → 2.13 / 0 |
| Wordy phrases per 1k | 3.39 → 2.29 / 2.20 | 5.17 → 5.62 / 0 | 2.21 → 2.23 / 0 |
| Self-mention (*nous, je, notre*) per 1k | 2.82 → 0 / 0 | 5.05 → 0 / 0 | 0 → 0 / 1.08 |

How French differs from English:

- **The missing glue is the verb, not the article.** French keeps its articles and *de* (the
  rates of *le* and *de* are about the same in human and model text). What disappears is *être*
  and *avoir*: in scientific text *être* falls from 25 to 10–12 per 1,000 tokens and *avoir*
  from 12 to 4–5. Copular sentences, the passé composé, the passive and "il y a" all go with
  them.
- **Rhythm is flatter than in English.** In scientific French both tiers vary their sentence
  lengths much less than human authors do (CV 0.33 against 0.45). In English the same
  difference is small.
- **The two tiers part ways in general prose.** The larger tier keeps its long, dense,
  verb-poor sentences (40 words on average, auxiliaries at a third of the human rate). The
  smaller tier switches to short declaratives (15 words on average) built on *c'est*, *mais*
  and *pas*, with human-like rates of *être* and *avoir*. A gate rebuilt without one tier lets
  22–32% of that tier's general texts through, against 1–4% in scientific prose: for general
  French, read the report's "closest AI profile" line and rely more on Phase 4.
- **The function-word marker is a single word.** Only the demonstrative *ce / cette / ces*
  passed the selection rule (twice the human rate in scientific text); see FR-5.
- **Wordy phrases are not a model habit.** "Dans le cadre de", "au sein de", "en termes de"
  are as frequent in human academic French as in model French, or more.

## 4. Pattern catalog

Each entry: the habit, the evidence, the check in the report, the fix, the over-correction.
Examples marked *(real)* come from an unedited model draft and its validated rewrite
(`worked-example.md`); the others are illustrative, with the source facts stated.

### FR-1. Phrase-fleuve, ou phrases hachées [C]
*Habit, long profile:* one sentence of 50 to 70 words carrying four or five ideas, held together
by commas, *dont*, *qui* and participles (*dont* is 2.6 times as frequent as in human scientific
text). *Habit, short profile:* a string of clipped declaratives, one claim each. *Check:* the
sentence-length dimension (two-sided), "Long / comma-chained sentences" under "Where to look".
*Fix, long:* cut at the logical joints and say the relation (*car, donc, mais, or, c'est
pourquoi*). *Fix, short:* join what belongs to one thought. *Over-correction:* a telegraphic
text; in a tribune, a first draft with 34 sentences in 596 words failed the over-correction
limit until sentences were joined (26 sentences in 569 words passed).

> Avant *(real, 62 words)* : « Le réchauffement climatique s'accompagne d'une augmentation bien documentée de la fréquence et de l'intensité des vagues de chaleur, dont les conséquences sanitaires pèsent de manière disproportionnée sur les populations âgées, plus vulnérables aux effets physiologiques de la chaleur extrême en raison du vieillissement des mécanismes de thermorégulation et de la prévalence élevée de comorbidités cardiovasculaires, respiratoires et rénales dans cette tranche d'âge. »
>
> Après *(real)* : « Avec le réchauffement climatique, les vagues de chaleur sont devenues plus fréquentes et plus intenses ; ce fait est bien documenté. Ce sont les personnes âgées qui en souffrent le plus. Avec l'âge, la thermorégulation fonctionne moins bien, et les maladies cardiovasculaires, respiratoires et rénales sont fréquentes dans cette tranche d'âge : la chaleur extrême est donc plus dangereuse pour elles que pour le reste de la population. »

> Avant (short profile) : « Les rythmes de vie ont changé. Les gens ne travaillent plus de neuf à dix-sept heures. Les bibliothèques ferment tôt. C'est un problème. »
>
> Après : « Les rythmes de vie ont changé : beaucoup de gens ne travaillent plus de neuf à dix-sept heures, et quand ils sortent, la bibliothèque est déjà fermée. »

### FR-2. Prose comprimée : il manque *être* et *avoir* [C]
*Habit:* abstract nouns as subjects of heavy verbs, enumerations without articles, no copula, no
compound past, no passive, no "il y a", no "il est possible de". This is the most consistent
French signal: a human scientific text has more of *être, en, avoir, dans* than a model text in
96% of comparisons on whole documents (95% for abstracts, 78% for general prose). *Check:*
grammatical-glue dimension; "Compressed sentences" under "Where to look". *Fix:* say it with
*être* or *avoir*: a property becomes "X est Y", a finding becomes "nous avons observé", "on a
mesuré", "il existe", "il y a". Give enumerations their articles. *Over-correction:* "il y a"
and "le fait que" in every sentence, or strings of "qui est / qui sont". The report marks OVER
when glue passes the human range.

> Avant *(real)* : « Cette hétérogénéité intra-urbaine résulte de la combinaison de plusieurs facteurs bien identifiés : densité du bâti, proportion de surfaces imperméabilisées et minérales par rapport aux espaces végétalisés, capacité thermique des matériaux de construction, et configuration des rues qui conditionne la ventilation naturelle des quartiers. »
>
> Après *(real)* : « Ces écarts ont plusieurs causes, qui sont bien identifiées : la densité du bâti, la part des surfaces imperméabilisées et minérales par rapport aux espaces végétalisés, la capacité thermique des matériaux de construction, et la configuration des rues, dont dépend la ventilation naturelle des quartiers. »

> Avant *(real)* : « Les progrès récents de la télédétection satellitaire offrent une occasion inédite de combler cette lacune. »
>
> Après *(real)* : « La télédétection par satellite a beaucoup progressé récemment, et il est maintenant possible de répondre à cette question. »

### FR-3. Verbes lourds à la place des verbes simples [C]
*Habit:* *constituer* (3 to 5 times the human rate in scientific text), *demeurer* (about 15
times), *offrir* (6 to 8 times), *révéler*, *contribuer*, *rester*, *reconnaître*, *réduire*,
*créer*; while *être*, *avoir* and *faire* (2.3 → 1.1 / 0.5 per 1,000 tokens) recede. *Check:*
marker-words dimension; the report lists the hits. *Fix:* the plain verb: *constituer* → *être*;
*demeurer* → *rester*, *être encore*; *offrir une occasion de* → *permettre de*, or say what
can now be done; *révéler* → *montrer*; *contribuer à* → say what it does. *Over-correction:*
swapping each verb for a synonym of the same weight (*représenter*, *s'avérer*, *témoigner de*).

> Avant *(real)* : « Comprendre la contribution spécifique des écarts de température intra-urbains à la morbidité liée à la chaleur constitue ainsi un enjeu à la fois scientifique et opérationnel de premier plan. »
>
> Après *(real)* : « Il est donc important, pour la recherche comme pour l'action publique, de savoir quelle part de la morbidité liée à la chaleur est due aux écarts de température intra-urbains. »

### FR-4. Noms-cadres et mots passe-partout [C]
*Habit:* nouns that frame without saying anything: *contexte* (3 to 7 times the human rate in
scientific text), *enjeu*, *approche*, *compréhension*, *dynamique*, *dimension*, *cadre*,
*défi*, *rôle*; with the adjectives *majeur*, *critique*, *simple* and the adverbs
*particulièrement*, *largement*, *directement*. Framing nouns run at 1.5 to 3 times the human
rate, depending on register and tier. *Check:* padding dimension (abstract framing nouns) and
marker words. *Fix:* replace the frame with the thing: "dans un contexte de vieillissement" →
"comme la population vieillit";
"l'enjeu de X" → what is at stake; "une meilleure compréhension de X" → "mieux comprendre X",
or what remains unknown. *Over-correction:* none; fewer framing nouns than the human median is
not a fault and is not counted as over-correction.

> Avant *(real)* : « ..., dans un contexte où l'intensification attendue des vagues de chaleur rend cette question de plus en plus pressante pour les villes européennes et leurs populations vieillissantes. »
>
> Après *(real)* : « La question est de plus en plus pressante pour les villes européennes, dont la population vieillit et où l'on s'attend à des vagues de chaleur plus intenses. »

### FR-5. Le démonstratif de reprise [C]
*Habit:* sentences and paragraphs that start by pointing back with *ce / cette / ces* + an
abstract noun: « Cette hétérogénéité... », « Cette limite méthodologique... », « Cette
approche... », « Ces facteurs... ». Nearly twice the human rate in scientific text (9.3 → 17
per 1,000 tokens). The pronoun in *c'est* and *ce qui* is counted separately and is not a
marker. The signal is moderate in scientific and general prose and absent in abstracts.
*Check:* "function words current models over-use" in the marker-words dimension. *Fix:* name
the thing again, use a pronoun, start with the actor (« Nous avons... »), or join the two
sentences. *Over-correction:* removing every demonstrative; the human median is not zero.

> Avant *(real, three paragraph openings of one draft)* : « Cette hétérogénéité intra-urbaine résulte de... » / « Cette limite méthodologique n'est pas sans conséquence... » / « Cette approche permet de dépasser... »
>
> Après *(real)* : « Ces écarts ont plusieurs causes... » / « Cette limite de méthode a des conséquences... » / « Nous avons ainsi pu aller plus loin que les études antérieures sur trois points. »

### FR-6. Les sujets absents : *nous*, *on*, *il* [C]
*Habit:* no one acts. Human research prose in French uses *nous* (2.1 per 1,000 tokens), *on*
(2.0) and impersonal *il* (*il existe, il s'agit, il faut, il est possible*); model text has
almost no *nous* (0.15 / 0), a quarter to a third of the *on*, and makes "cette étude",
"l'analyse" or "ces résultats" the subject. The plain intensifier *très* and the connector
*alors* fall to a third of their human rate. *Check:* stance dimension
(self-mention), marker words ("everyday function words people use more"). *Fix:* let the authors
act where the genre allows: « nous avons relié », « on observe », « il existe ». In a tribune,
*je* and *nous* are normal. *Over-correction:* a *nous* in every sentence.

> Avant *(real)* : « En répondant à ces questions, cette étude entend contribuer à une meilleure caractérisation des déterminants spatiaux fins de la morbidité liée à la chaleur chez les personnes âgées en milieu urbain... »
>
> Après *(real)* : « Nous espérons ainsi mieux décrire les déterminants spatiaux fins de la morbidité liée à la chaleur chez les personnes âgées qui vivent en ville. »

### FR-7. Adverbes en *-ment* et adjectifs [C]
*Habit:* about twice the human rate of *-ment* adverbs in every register (*considérablement,
sensiblement, particulièrement*), and a fifth to two thirds more adjectives. *Check:* modifiers
dimension; "Most used derived adverbs" under "Where to look". *Fix:* delete the adverb that
only intensifies; keep the one that informs (*rarement,
quotidiennement, statistiquement*). Use the number if the source has it. *Très* and *beaucoup*
are ordinary French and are under-used by models. *Over-correction:* stripping adjectives that
classify (*intra-urbain, respiratoire, quotidien*).

> Faits de la source : excès de risque 1,6 fois plus élevé dans le quintile le plus chaud.
> Avant : « Le risque est considérablement plus élevé dans les quartiers particulièrement exposés. »
> Après : « L'excès de risque est 1,6 fois plus élevé dans le quintile le plus chaud que dans le plus frais. »

### FR-8. Nominalisations en chaîne [C]
*Habit:* 69 to 85 nominalisations per 1,000 words against 50 in human scientific text; in the
larger tier half of the sentences carry three or more. *Check:* nominal-style dimension;
"Nominalization clusters". *Fix:* find who does what and give the action its verb.
*Over-correction:* terms of art stay nouns (*thermorégulation, morbidité, télédétection*).

> Avant *(real)* : « ... fournir des éléments susceptibles d'éclairer la conception de politiques de prévention et d'adaptation plus finement ciblées... »
>
> Après *(real)* : « Nous voulons aussi fournir des éléments utiles pour concevoir des politiques de prévention et d'adaptation mieux ciblées, à l'échelle du quartier. »

### FR-9. Rythme et paragraphes uniformes [C]
*Habit:* sentences of similar length in a row, and paragraphs of the same size (paragraph-length
CV 0.42 → 0.24 / 0.21). *Check:* rhythm and paragraphs dimensions; "Uniform-length run". *Fix:*
a short sentence where a point lands (« Mais à dix-neuf heures, elle est fermée. »), a long one
where the reasoning needs its clauses; a short paragraph for a pivot. *Over-correction:*
one-line paragraphs for effect; nominal sentences in a research article.

### FR-10. Ponctuation [C] and [P]
*Habit:* commas and full stops only. Human scientific French uses about 7 parentheses per 1,000
words; the larger tier none. Semicolons and colons are rare in model text. Some model text uses
the English em dash without spaces (« la température intra-urbaine—celle expérimentée à
l'intérieur des villes—varie considérablement »).
*Check:* punctuation dimension; the "Specifics | punctuation" line; the "Typography:" lines.
*Fix:* parentheses for a gloss, a unit, a period or a sample size (« (2008-2018) », « (c'est
l'îlot de chaleur urbain) »); a semicolon between two closely linked statements; a colon to
introduce a cause, a list or a consequence. For an aside, French uses spaced dashes ( – ) or
commas. *Over-correction:* decorative semicolons.

### FR-11. Remplissage [C] and [R-analogue]
The deletion test of `SKILL.md` decides; these are the places to look.

- **Participiale ou gérondif après une virgule** [C]: « ..., négligeant ainsi une dimension
  pourtant bien connue », « ..., permettant de mieux cibler... », « ..., tout en restant... »,
  « ..., en traitant de manière uniforme... ». Human median 0 per 1,000 words; 4 to 5 in the
  smaller tier's scientific text, 2 in the larger tier's general prose. Cut it, or make it a
  sentence with a subject and a conjugated verb.
- **Annonces** [R-analogue]: « il convient de souligner que », « notons que », « il est
  important de noter que », « en d'autres termes », « comme mentionné précédemment ». Say the
  thing.
- **Formules** [P]: « joue un rôle crucial », « constitue un enjeu majeur », « s'inscrit dans
  une démarche », « met en lumière », « souligne l'importance de », « ouvre la voie à », « à
  l'ère de », « au cœur de », « force est de constater », « un véritable... », « ce n'est pas
  seulement X, c'est Y ». Replace with the specific claim, or delete.
- **Phrase de clôture** [R-analogue]: a paragraph that ends by restating its own importance
  (« Ces résultats soulignent l'importance de... »), or a text that ends on « En conclusion »,
  « des recherches futures devront » or « ouvre des perspectives prometteuses ».
- **Doublets et triplets** : « scientifique et opérationnel », « riche et complexe »,
  « efficace, durable et inclusive ». Keep the word that carries the meaning.
- **Locutions lourdes: a guard, not a target** [C]: « dans le cadre de », « au sein de », « en
  termes de », « permet de », « afin de pouvoir », « la mise en place de ». Human academic
  French uses them as much as models do. Shorten where nothing is lost (« permet de montrer » →
  « montre »), but zero is not the goal, and adding them to gain length fails the classic guard.

### FR-12. Connecteurs en tête de phrase [R-analogue]
*Habit:* « En effet, », « Par ailleurs, », « De plus, », « En outre, », « Ainsi, », « En
somme, », « En définitive, » at the head of sentence after sentence. The two calibrated tiers
do this less than human authors (at least one such opener in 49% of human scientific texts,
30% of the larger tier's, 10% of the smaller tier's), but other models and older drafts pile
them up, so it stays a classic guard. *Check:* "formulaic openers". *Fix:* delete the connective when the relation is
obvious; otherwise put it inside the sentence, or use the conjunction that states the logic:
*mais, or, car, donc*. Model text under-uses *car* and, in the larger tier, *donc*.

### FR-13. Calques de l'anglais [P]
Not measured by the scripts: check by reading. Seen in the model drafts used for calibration:
« conditions chroniques » (*maladies* or *affections chroniques*), « la température
expérimentée » (*ressentie*, *subie*), a glued em dash. Common elsewhere: « basé sur » (*fondé
sur*), « adresser un problème » (*traiter*), « faire sens » (*avoir du sens*), « impacter »
(*toucher, affecter, peser sur*), « opportunité » for *occasion*, « définitivement » for
*assurément*, « initier » for *lancer*, « en charge de » (*chargé de*), « supporter » for
*soutenir*, « digital » for *numérique*, « au final » (*finalement, en fin de compte*). Use the
French term the field uses; a real borrowed term of art (« machine learning » in a computing
paper that uses it) is a forced choice and stays.

---

## 5. Calibrated word lists [C]

Built by the rule used for English: log-odds ratio with an informative Dirichlet prior, |z| ≥ 3
in at least two registers with the same sign, none opposite. Three topic words that the
selection picked up from the prompts (*imagerie, social, clinique*) are excluded by hand.
Held-out AUC is
P(AI rate > human rate) for lists built on the other half of the documents (0.5 = no signal).

| List | Words | Held-out AUC: scientific / abstract / general |
|---|---|---|
| Glue (under-used by models) | être, en, avoir, dans | 0.04 / 0.05 / 0.22 |
| Over-used content words | constituer, demeurer, offrir, contexte, largement, décennie, compréhension, particulièrement, révéler, contribuer, rester, directement, majeur, plutôt, critique, créer, enjeu, reconnaître, simple, approche, réduire | 0.91 / 0.78 / 0.76 |
| Over-used function word | ce (determiner: ce, cet, cette, ces) | 0.76 / 0.44 / 0.75 |
| Under-used function words | il, nous, on, très, alors | 0.25 / 0.18 / 0.35 |
| Under-used content word | faire | 0.31 / 0.44 / 0.35 |

Reading the table: the glue list and the content-word list are strong in scientific text and
abstracts and weaker in general prose. The demonstrative carries no signal in abstracts. The
lists are rates to bring toward the human median, not banned words: *rester*, *simple* and
*plutôt* are ordinary French.

The other French lists in `scripts/lang_fr.py` (connectives, hedges, boosters, stock patterns,
wordy phrases, framing nouns, announcements) are translations and counterparts of the English
ones, tagged [R-analogue], [L] or [P] in the file. They feed reported metrics and classic
guards; the calibration decides which of them count in the composite.

## 6. Typography

A French text that follows English typography reads as machine-made or as translated. The
analyzer reports the first six conventions below as "Typography:" lines under "Where to look"
and never gates on them; the last two are for your own reading.

| Convention | Wrong | Right | Reported |
|---|---|---|---|
| Space before `; : ! ?` (non-breaking) | `la cause: la chaleur` | `la cause : la chaleur` | yes |
| Guillemets | `"îlot de chaleur"` | `« îlot de chaleur »` | yes |
| Decimal comma before `%` | `3.5 %` | `3,5 %` | yes |
| Ordinals | `2ème`, `95ème` | `2e`, `95e` | yes |
| Dashes for an aside | `mot—mot` | `mot – mot` (spaced), or commas | yes |
| `etc.` | `etc...` | `etc.` | yes |
| Thousands | `1,200 patients` | `1 200 patients` | no |
| Titles and headings | `Les Effets De La Chaleur` | `Les effets de la chaleur` | no |

## 7. The fact ledger in French

- Numbers are compared by value: `1,9 million` = `1.9 million` = `1 900 000`; `11 %` = `11%`;
  `1 200` = `1200`; `douze villes` = `12 villes`; `95e percentile` keeps its 95.
- Citations: « (Dupont et al., 2019) », « Dupont et coll. (2019) », « Dupont et Martin (2019) »
  and `[12]` are compared as references, so moving a citation into the sentence is not a change.
  Month names and words such as « Figure » or « Tableau » before a year are not read as authors.
- Hedges and boosters are counted with French lists (*pourrait, semble, suggère, probablement,
  sans doute* ; *démontre, prouve, clairement, à l'évidence*). The conditional is the usual French
  hedge: « réduirait » and « pourrait réduire » are hedged, « réduit » is not. The script does
  not parse the conditional of every verb, so check by reading that no conditional became an
  indicative.
- Negation counts cover *ne, n', sans, aucun, jamais, ni*. « ne... que » is a restriction, not
  a negation: a changed count is often this, but check each case.

## 8. Limits

- The human scientific corpus is medicine (PubMed Central) and humanities and social sciences
  (OpenEdition). French physics, chemistry or engineering papers, which are rare, are not
  represented. The medical half comes almost entirely from one journal (*The Pan African
  Medical Journal*: 97 of 106 sections).
- The general register mixes explanatory journalism, news and encyclopedic text. Literary
  essays, legal and administrative French have other norms.
- The AI side is two tiers of one model family. In general prose they differ so much that each
  is poorly predicted by the other (§3), so a third model may differ again.
- Short general texts are the weakest case: at 150 words 22% of unedited AI texts pass, at 300
  words 8% (table in `SKILL.md`).
- Calques, register slips (*tu / vous*, familiar words in a formal text) and agreement errors
  are not measured. Read for them.
- Texts from Québec, Belgium, Switzerland or Africa follow the same grammar; their typographic
  and lexical conventions can differ (for example no space before `:` in some Canadian styles).
  Follow the user's.
