# Calibration: what was measured, how, and how well the gate works

The research papers give *directions* ("AI text has fewer proper nouns"). A verification loop
needs *numbers*: how many is human-like, in which language, for which kind of text, at which
length, against which model. This file documents how `scripts/data/calibration.json` and
`scripts/data/markers_<lang>.json` were built, what they show, and how to rebuild them.
The table of every metric in every register is in `calibration-tables.md`.

## Contents
1. Data
2. Procedure
3. How well the gate separates
4. The fingerprint
5. Two experiments behind the design
6. Marker words
7. Growth bands (for the length rule)
8. How long the baselines ran
9. Continuation probe
10. Rebuilding
11. Caveats

---

## 1. Data

**Human text.** All of it was written before public LLMs (the newest source is dated
2019-12-31). Each text was cut at a paragraph boundary to at most 950 words.

| Register | English | n | French | n |
|---|---|---|---|---|
| scientific | PubMed Central open-access research articles, 2015–2019, 14 fields: Introduction and Discussion sections, citations and figures removed | 145 | French-language PubMed Central articles 2015–2019 (106) and articles from 64 OpenEdition journals in the humanities and social sciences, 2012–2019 (117) | 223 |
| abstract | arXiv abstracts 2017–2019, 10 categories, at least 150 words | 86 | HAL abstracts 2015–2019, 16 from each of 11 domains, theses included (176), and OpenEdition résumés (16) | 192 |
| general | Brown corpus informative genres, 1961 (294); The Conversation 2015–2019 (170), Wikinews 2012–2019 (110), Wikipedia featured articles as of 2019-12-31 (78) | 652 | The Conversation France 2015–2019 (170), Wikinews (93), Wikipedia featured articles as of 2019-12-31 (70) | 333 |
| extra check | Brown "learned" category, 1961 journal prose | 80 | | |
| long documents | longer versions of the same sources (up to 2,600 words) | 37 + 67 | | 150 + 100 |

One of the 192 French abstracts is laid out as a list and has no running sentences, so 191 enter
the bands: 1,630 human texts in all for the six registers.

**AI text.** Two current Claude tiers (called the Sonnet tier and the Haiku tier here) answered
ordinary requests, with no style instruction, on topics taken from the human texts:

- *scientific*: "I'm writing a research paper titled "…" for <journal>. Here is the abstract: …
  Please draft the Introduction (or Discussion) section (about 700 words). Plain paragraphs, no
  headings, no reference citations." Titles and abstracts are those of human articles in the
  corpus. 30 texts per tier and language.
- *abstract*: "Write the abstract (about 200 words) for a <field> paper titled "…"". 20 per tier
  and language.
- *general*: requests matched to the human genres (news reports, op-eds, reviews, how-to guides,
  explanatory articles "written by an academic" under real The Conversation titles). 34 per
  tier in English, 20 per tier in French.

That makes 168 English and 140 French calibration texts. A further 23 texts (8 English and 8
French answers to other requests, and 7 English general texts that a Haiku-tier agent wrote on
topics of its own) were kept out of everything and used only for the check in §3.

## 2. Procedure

Scoring during calibration calls the shipped `sci_metrics.evaluate`, so the gate and its
calibration cannot diverge. The steps:

1. **Fixed lengths.** Every text is measured in windows of 150, 200, 300, 450, 600, 750 and 900
   analysed words (whole sentences; a window ends at the sentence boundary nearest the target).
   A length is calibrated when at least 40 human and 15 AI documents reach it. Abstracts stop
   at 300 words.
2. **Human bands.** For every metric and length: the human percentiles 2.5, 5, 10, 25, 50, 75,
   90, 95, 97.5.
3. **Which metrics count.** For each tier, AUC = P(AI value > human value) at equal length,
   averaged over lengths. A metric is scored when at least one tier separates (|AUC − 0.5| ≥
   0.15). If the two tiers sit on opposite sides of the human median, it is scored on both
   sides. A research guard (the direction the literature documents as the AI side) is never
   reversed: if current models go the other way, the metric is only reported.
4. **Dimensions.** Metrics are grouped into dimensions (sentence length, rhythm, paragraphs,
   word variety, content-word variety, grammatical glue, word length, marker words,
   specificity, punctuation, modifiers, verb style, nominal style, padding, stock phrasing,
   stance, evaluation, openers, function words, repetition), so that four correlated variety
   measures count once.
5. **Profiles.** For each tier, weights over the dimensions: how far the tier sits above human
   text on the dimension score, divided by the score's variance, normalised. The composite of a
   text is the largest of its per-profile weighted means.
6. **Thresholds, out of fold.** Documents are split into 5 folds, twice. Metric selection,
   directions, bands and weights are rebuilt without each fold and applied to it. The composite
   threshold at each length is the 90th percentile of these out-of-fold human composites; the
   dimension bands (p75, p90) and the over-correction limit (p99 of the far-side score, never
   below the 97.5th percentile of an extra human corpus) come from the same scores.
7. **Classic guards.** Research-documented tells are checked against the human 97.5th (or 2.5th)
   percentile with a minimum rate, whether or not current models show them. One violation is
   allowed.
8. **Pass rates.** The share of out-of-fold human and AI documents that pass the whole gate, at
   each length (windows of one document are averaged first).
9. **Leave one tier out.** The whole procedure is repeated without one tier and applied to that
   tier's texts: a test of whether the gate only knows the models it was built on.

## 3. How well the gate separates

Share of texts passing the whole gate, by length. "Human" is the out-of-fold pass rate.

| Register | | 150 | 200 | 300 | 450 | 600 | 750 | 900 |
|---|---|---|---|---|---|---|---|---|
| en.scientific | human | 86% | 87% | 86% | 86% | 84% | 84% | 85% |
| | Sonnet tier / Haiku tier | 1 / 3% | 2 / 1% | 0 / 0% | 0 / 0% | 0 / 0% | 0 / 0% | 0 / 0% |
| en.abstract | human | 86% | 86% | 85% | | | | |
| | Sonnet tier / Haiku tier | 0 / 0% | 0 / 0% | 0 / 0% | | | | |
| en.general | human | 87% | 87% | 87% | 87% | 88% | 88% | 87% |
| | Sonnet tier / Haiku tier | 19 / 5% | 17 / 2% | 14 / 2% | 15 / 0% | 9 / 0% | 6 / 0% | 6 / 0% |
| fr.scientific | human | 86% | 84% | 85% | 86% | 86% | 85% | 86% |
| | Sonnet tier / Haiku tier | 7 / 3% | 3 / 0% | 3 / 0% | 0 / 0% | 0 / 0% | 0 / 0% | 0 / 0% |
| fr.abstract | human | 87% | 86% | 85% | | | | |
| | Sonnet tier / Haiku tier | 8 / 0% | 5 / 0% | 0 / 0% | | | | |
| fr.general | human | 87% | 87% | 87% | 86% | 88% | 86% | 85% |
| | Sonnet tier / Haiku tier | 21 / 23% | 12 / 17% | 8 / 8% | 5 / 5% | 5 / 0% | 5 / 0% | 0 / 0% |

Composite thresholds lie between 0.62 and 0.69 (0.69 to 0.78 for English abstracts); the median
human composite is 0.38 to 0.47, and the lowest tenth of AI composites starts at 0.55 to 1.25
depending on register and length.

Further checks:

| Check | Result |
|---|---|
| Gate rebuilt without the Sonnet tier, applied to it (share passing) | en.scientific 2%, en.abstract 9%, en.general 20%, fr.scientific 4%, fr.abstract 13%, fr.general 22% |
| Gate rebuilt without the Haiku tier, applied to it | en.scientific 2%, en.abstract 2%, en.general 2%, fr.scientific 1%, fr.abstract 0%, fr.general 32% |
| Another human corpus: Brown "learned" (1961), en.scientific gate | 91% pass |
| Long human documents, scored in windows | en.scientific 86% (n = 37), en.general 88% (67), fr.scientific 91% (150), fr.general 90% (100) |
| Long AI documents (calibration texts of one tier joined), scored in windows | 0% in all four registers |
| 23 AI texts kept out of the calibration | all fail; composites 0.77 to 1.82 |

Reading these numbers:
- **About one human text in seven fails.** The threshold passes 90% of human composites by
  construction; the classic guards and the over-correction limit fail a few more. The gate asks
  for the central range of human writing. It is not a test of authorship.
- **Scientific prose and abstracts are well separated at every length.** General prose is not:
  the larger tier's short general texts pass one time in five or six, and in French so do the
  smaller tier's.
- **Length helps.** With more text the rates stabilise and the AI pass rate falls, which is the
  research finding on short texts (research-digest §6) seen in this data.
- **The gate is not only memorising its two tiers.** Built without one tier it still rejects
  96–99% of that tier's scientific texts. In general prose it carries over less well (68–98%
  rejected), worst in French, where the two tiers write in opposite styles (`french.md` §3).
- It has not been tested on other model families.

## 4. The fingerprint

Medians, human → Sonnet tier / Haiku tier. English; the French table is in `french.md` §3.

| Habit | scientific @450 | abstract @200 | general @450 |
|---|---|---|---|
| Mean sentence length (words) | 26.4 → 41.5 / 21.9 | 25.1 → 44.0 / 20.1 | 21.8 → 33.3 / 17.9 |
| Sentence-length variation (CV) | 0.380 → 0.355 / 0.332 | 0.314 → 0.194 / 0.261 | 0.442 → 0.442 / 0.386 |
| Commas per sentence | 1.41 → 2.92 / 1.00 | 0.88 → 2.55 / 0.70 | 1.18 → 2.17 / 0.87 |
| Paragraph-length variation (CV) | 0.355 → 0.243 / 0.243 | | 0.389 → 0.303 / 0.297 |
| Glue words (the, of, be, to, in) per 100 tokens | 18.2 → 13.5 / 11.9 | 18.1 → 12.7 / 9.09 | 19.3 → 14.8 / 12.9 |
| Auxiliaries (% of tokens) | 4.14 → 3.16 / 2.92 | 3.12 → 1.45 / 0.53 | 4.87 → 3.18 / 3.64 |
| Lexical density | 0.588 → 0.611 / 0.666 | 0.600 → 0.647 / 0.719 | 0.531 → 0.572 / 0.650 |
| Mean word length (letters) | 5.67 → 6.06 / 6.63 | 5.65 → 6.20 / 7.03 | 4.95 → 5.36 / 5.97 |
| Word variety (MATTR-50 on lemmas) | 0.775 → 0.843 / 0.823 | 0.769 → 0.828 / 0.828 | 0.777 → 0.830 / 0.831 |
| Content-word variety (MATTR-25) | 0.899 → 0.952 / 0.921 | 0.906 → 0.938 / 0.920 | 0.930 → 0.960 / 0.931 |
| Over-used function words per 1k | 11.2 → 36.9 / 31.0 | 9.57 → 32.1 / 24.4 | 11.2 → 30.0 / 24.8 |
| Over-used content words per 1k | 15.2 → 36.9 / 53.3 | 18.4 → 31.9 / 56.2 | 6.57 → 17.2 / 31.2 |
| Names + acronyms + numbers (% of tokens) | 5.81 → 1.38 / 1.11 | 4.95 → 0.77 / 0.25 | 10.9 → 4.07 / 3.44 |
| Parentheses per 1k words | 6.80 → 0 / 0 | 9.57 → 0 / 0 | 2.14 → 0 / 0 |
| Derived adverbs in -ly (% of tokens) | 1.32 → 3.19 / 2.00 | 1.08 → 2.10 / 0.74 | 1.10 → 2.67 / 1.80 |
| Adjectives (% of tokens) | 9.37 → 11.0 / 12.0 | 9.23 → 12.1 / 11.2 | 6.16 → 8.50 / 11.6 |
| Sentences with ≥ 3 nominalisations | 0.167 → 0.374 / 0.264 | 0.167 → 0.600 / 0.247 | 0 → 0.077 / 0.071 |
| Nominalisations per 1k | 51.0 → 53.0 / 81.6 | 55.6 → 67.2 / 90.7 | 26.3 → 31.8 / 54.4 |
| Comment clauses after a comma per 1k | 0 → 2.25 / 2.24 | 0 → 5.50 / 4.82 | 0 → 2.22 / 2.20 |
| Abstract framing nouns per 1k | 10.9 → 13.0 / 24.3 | 6.13 → 11.1 / 19.8 | 2.25 → 2.57 / 9.01 |
| Wordy phrases per 1k | 3.28 → 0 / 0 | 0 → 0 / 0 | 0 → 0 / 0 |
| Self-mention per 1k | 4.37 → 3.28 / 0 | 22.0 → 21.7 / 15.3 | 3.58 → 0 / 0 |

Medians hide what occurs once per text. Share of **whole documents containing at least one**:

| At least one… | EN scientific: human / Sonnet / Haiku | EN general | FR scientific | FR general |
|---|---|---|---|---|
| parenthesis | 90 / 0 / 17% | 63 / 6 / 24% | 88 / 0 / 60% | 86 / 0 / 25% |
| semicolon | 52 / 30 / 7% | 51 / 47 / 38% | 52 / 17 / 27% | 39 / 10 / 45% |
| dash | 17 / 0 / 73% | 63 / 6 / 76% | 22 / 17 / 0% | 29 / 0 / 70% |
| comment clause after a comma | 51 / 90 / 70% | 48 / 82 / 71% | 31 / 77 / 73% | 47 / 75 / 50% |
| formulaic ending | 6 / 30 / 13% | 1 / 12 / 9% | 2 / 27 / 0% | 2 / 10 / 0% |
| significance echo | 1 / 0 / 20% | 0 / 0 / 0% | 0 / 10 / 27% | 1 / 0 / 0% |
| stacked hedge | 3 / 0 / 20% | 2 / 0 / 0% | 0 / 0 / 3% | 1 / 0 / 0% |
| stock phrase | 32 / 33 / 40% | 20 / 15 / 29% | 35 / 63 / 70% | 29 / 45 / 45% |
| formulaic opener (Furthermore…, De plus…) | 70 / 20 / 70% | 29 / 6 / 29% | 49 / 30 / 10% | 41 / 15 / 20% |
| wordy phrase | 85 / 57 / 47% | 55 / 21 / 24% | 83 / 83 / 73% | 71 / 60 / 40% |
| self-mention | 86 / 87 / 67% | 78 / 47 / 47% | 75 / 50 / 3% | 55 / 20 / 60% |

What the two tables say together:
- **Compression is shared.** Fewer glue words and auxiliaries, higher density, longer words, in
  both tiers, both languages and every register (one exception: the Haiku tier's French general
  prose keeps human rates of *être* and *avoir*).
- **Rhythm separates the tiers.** The Sonnet tier writes sentences half as long again as human
  ones, with twice the commas; the Haiku tier writes shorter ones. Hence the two-sided score.
- **Specifics are missing**: typically a fifth to a third of the human share of names,
  acronyms and numbers (the Haiku tier's French general prose is the exception, at two thirds).
  Part of this is the task (the models wrote from a title and an
  abstract; the human authors had their data). It is also the situation the skill works in: AI
  prose is unspecific unless it is given specifics.
- **Punctuation is flat in the Sonnet tier** (no parentheses in any scientific text, dashes
  almost never) and dash-heavy in the Haiku tier.
- **Comment clauses are the padding habit of both tiers** (in 70–90% of texts in most sets,
  against half of human ones or fewer). Framing nouns and significance echoes belong mainly to the Haiku tier.
  Formulaic endings belong mainly to the Sonnet tier.
- **Older tells that no longer discriminate:** formulaic openers and wordy phrases are as
  common in human text, or more so. They remain as classic guards against piles of them.
- **Reversed against the older literature:** all-word lexical diversity is *higher* than human
  (§5.1); repeated word 3-grams are *fewer* (24 per 1,000 words in human scientific text, 15 to
  18 in model text); half of the published function-word lists point the other way
  (research-digest §4.9).

**Invented vivid detail.** From one-line briefs describing an experience, the models filled the
gaps with specifics nobody supplied: for a car-rental complaint, a five-hour flight, a
nine-month-old and a quoted remark from the clerk; for a restaurant review, a name, a street
corner and a server's comment; in a French introduction, a temperature gradient "dépassant
10 °C" that the abstract did not contain. For fiction that is the task. For a user's real
experience or a factual document it is fabrication.

## 5. Two experiments behind the design

### 5.1 Which vocabulary estimators, and what drives them
For each candidate: separation from AI text at 450 words (AUC per tier), reliability
(correlation between the odd-sentence half and the even-sentence half of one human text), and
drift (150 versus 600 words of the same human text, in between-text standard deviations).
English scientific prose, 121 human texts:

| Estimator | AUC Sonnet / Haiku | Split-half r | Drift 150 → 600 |
|---|---|---|---|
| raw type-token ratio | 0.91 / 0.71 | 0.52 | −3.65 SD |
| distinct lemmas per 100, rarefied | 0.95 / 0.86 | 0.65 | +0.94 |
| MATTR-50 on lemmas | 0.98 / 0.92 | 0.57 | +0.23 |
| MTLD, wrap-around | 0.99 / 0.91 | 0.50 | +0.21 |
| Yule's K (negated) | 0.94 / 0.88 | 0.65 | +0.50 |
| hapax share per 100-word window (first version of the skill) | 0.95 / 0.85 | 0.41 | +0.38 |
| content-word types per 50 content words | 0.84 / 0.50 | 0.71 | +0.86 |
| lexical density | 0.66 / 0.97 | 0.60 | +0.08 |
| share of the five commonest function words | 0.15 / 0.09 | 0.56 | −0.75 |

- The raw ratio moves by more than three standard deviations between 150 and 600 words of the
  same text. It cannot be compared across lengths, which is why every band is length-matched
  and the raw ratio is only reported.
- No estimator is both the most reliable and free of drift, so the gate averages four of them
  in one dimension and compares at equal length. The first version's windowed hapax measure
  was the least reliable and was dropped.
- **What drives the difference.** Remove from MATTR-50 the part that lexical density predicts
  (regression fitted on human texts) and the Haiku tier's separation falls from 0.92 to 0.57;
  remove the part predicted by the share of the five commonest function words and it falls to
  0.60. For the Sonnet tier the same removals leave 0.98 and 0.93: its excess is also in the
  content words (content-word MATTR-25: AUC 0.95). The same pattern holds in English general
  prose and in French scientific prose: density explains the Haiku tier's excess and not the
  Sonnet tier's. So "high
  lexical diversity" in current models is mostly compression, plus real rotation of content
  words in the larger tier. This is why the report splits variety into glue, density and
  content-word variety.

### 5.2 How to combine the dimensions
AI texts passing at the threshold that passes 90% of out-of-fold human composites (Sonnet tier /
Haiku tier), for three ways of combining dimension scores:

| Register, length | Unweighted root-mean-square | Per-tier weighted mean, larger counts | Same, weights divided by variance (adopted) |
|---|---|---|---|
| en.scientific, 150 words | 18 / 11% | 6 / 3% | 1 / 3% |
| en.scientific, 450 | 3 / 3% | 0 / 0% | 0 / 0% |
| en.general, 150 | 49 / 11% | 29 / 5% | 21 / 4% |
| en.general, 450 | 26 / 0% | 24 / 0% | 15 / 0% |
| fr.scientific, 150 | 32 / 17% | 20 / 7% | 7 / 3% |
| fr.scientific, 450 | 20 / 3% | 5 / 0% | 0 / 0% |
| fr.general, 150 | 43 / 58% | 33 / 22% | 22 / 22% |
| fr.general, 450 | 15 / 25% | 15 / 5% | 5 / 5% |

The root-mean-square treats all dimensions alike, so the many on which a text looks human
dilute the few on which it does not. Weighting by how strongly each tier deviates removes most
of that, and taking the larger of the two profile scores keeps a text from hiding between the
profiles. The weights of the strongest dimensions, as shares of a profile:

| Register | Sonnet tier | Haiku tier |
|---|---|---|
| en.scientific | marker words 16%, punctuation 11%, specificity 11%, word variety 10%, content-word variety 9% | marker words 17%, specificity 11%, punctuation 10%, word length 9%, glue 9% |
| en.general | glue 13%, marker words 12%, specificity 12%, function words 9%, punctuation 8% | marker words 13%, glue 11%, specificity 9%, function words 9%, punctuation 7% |
| fr.scientific | marker words 11%, glue 11%, specificity 9%, sentence length 9%, content-word variety 9% | marker words 16%, glue 13%, word length 8%, specificity 8%, modifiers 6% |
| fr.general | marker words 10%, punctuation 10%, content-word variety 10%, specificity 10%, glue 9% | marker words 14%, sentence length 12%, word length 11%, content-word variety 9%, glue 9% |

## 6. Marker words

`scripts/data/markers_<lang>.json`, built by `calibration/tools/build_markers.py`:

1. Lemma counts per register, human against AI (both tiers pooled).
2. For each lemma and register, the log-odds ratio with an informative Dirichlet prior (Monroe,
   Colaresi & Quinn 2008) and its z-score. The prior is the pooled frequency, so rare words
   need strong evidence.
3. A lemma enters a list when |z| ≥ 3 in at least two registers with the same sign and no
   register has the opposite sign at that strength. Function words and content words are
   listed separately. Topic words that came from the prompts are excluded by hand in the
   configuration (three in French).
4. Validation: the lists are rebuilt on half of the documents and their rates compared on the
   other half. AUC = P(AI rate > human rate).

English (z in scientific / abstract / general):

| List | Words | Held-out AUC sci / abs / gen |
|---|---|---|
| Glue (human-favoured) | the −14/−11/−20, of −10/−6/−11, be −14/−9/−15, to −4/−5/−12, in −13/−2/−12 | 0.05 / 0.06 / 0.05 |
| AI function words | rather +8/+4/+12, how +11/+5/+7, across +9/+6/+7, than +5/+2/+11, or +4/+2/+10, where +6/+2/+6, toward, what, through, without, itself, beyond, yet, within, might, single | 0.92 / 0.87 / 0.85 |
| AI content words (39) | require +8/+2/+9, pattern +6/+1/+9, represent, approach, substantial, actually, particularly, specific, reflect, create, broad, suggest, shape, substantially, shift, particular, kind, structure, attention, establish, condition, system, decade, practical, mechanism, remain, address, challenge, capture, multiple, quality, framework, reveal, offer, extend, enable, manage, examine, matter | 0.91 / 0.76 / 0.84 |
| Human function words | as −7/−2/−7, also, there, on, by, we, will, after, all, such, very | 0.17 / 0.35 / 0.21 |
| Human content words ("plain workhorse words") | study, use, example, show, lead, base, include, part, know | 0.39 / 0.27 / 0.53 |

French: lists and held-out values are in `french.md` §5.

The in-sample values are better than the held-out ones (for the English content words, 0.98
against 0.91 in scientific text), which is the selection effect the held-out figure exists to
remove. The human content-word list holds up weakly in scientific text and abstracts and not
at all in general prose; it is one of four metrics in its dimension and never decides alone.

## 7. Growth bands (for the length rule)

What human texts add when they grow: the first N words of a text against its first M words (the
next calibrated length), counted as new content lemmas and new specifics (numbers, names,
acronyms) per 100 added words.

| Register | Growing from | New content words per 100 added: p10 / p25 / median | New specifics per 100 added: p25 / median |
|---|---|---|---|
| en.scientific | 150 | 25.0 / 30.0 / 36.1 | 0.0 / 1.9 |
| en.scientific | 300 | 22.4 / 26.4 / 30.1 | 1.3 / 2.2 |
| en.scientific | 450 | 18.6 / 22.7 / 27.0 | 0.7 / 2.1 |
| en.scientific | 600 | 14.7 / 19.1 / 24.6 | 0.0 / 1.4 |
| en.general | 150 | 27.8 / 31.9 / 37.5 | 1.6 / 5.6 |
| en.general | 300 | 24.8 / 28.9 / 32.9 | 2.6 / 5.4 |
| en.general | 450 | 21.8 / 26.6 / 30.7 | 1.9 / 5.0 |
| en.general | 600 | 20.7 / 24.8 / 29.2 | 1.5 / 4.3 |
| fr.scientific | 150 | 29.1 / 34.8 / 40.0 | 0.0 / 2.9 |
| fr.scientific | 300 | 24.8 / 29.1 / 33.9 | 1.3 / 3.4 |
| fr.scientific | 450 | 22.4 / 26.2 / 31.4 | 1.2 / 2.7 |
| fr.scientific | 600 | 18.9 / 23.2 / 28.1 | 0.7 / 2.6 |
| fr.general | 150 | 30.0 / 35.5 / 40.4 | 1.8 / 5.6 |
| fr.general | 300 | 27.3 / 30.6 / 34.8 | 1.9 / 4.1 |
| fr.general | 450 | 24.6 / 28.4 / 32.4 | 1.4 / 4.0 |
| fr.general | 600 | 23.9 / 27.0 / 30.1 | 1.3 / 3.1 |

(All calibrated lengths are in the calibration file.) The same measurement on the AI texts,
growing from 300 to 450 words:

| | New content words per 100 added (median) | New specifics per 100 added (median) |
|---|---|---|
| en.scientific: human / Sonnet / Haiku | 30.1 / 34.6 / 31.2 | 2.2 / 0.0 / 0.0 |
| en.general | 32.9 / 36.1 / 35.2 | 5.4 / 2.3 / 0.6 |
| fr.scientific | 33.9 / 36.5 / 36.4 | 3.4 / 0.6 / 0.3 |
| fr.general | 34.8 / 39.6 / 41.7 | 4.1 / 0.7 / 1.6 |

A model text that gets longer brings new vocabulary at the human rate or above, and almost no
new specifics. That is why the growth check looks at both, and why the count of new words alone
cannot detect filler (`worked-example.md`, case B). The third thing the check reports, the
share of added words in sentences that are not anchored in the source, has no corpus behind
it: its bounds come from worked cases and are documented as such in `metrics.md` §12.

## 8. How long the baselines ran

Words delivered divided by words requested:

| Set | Sonnet tier: median (range) | Haiku tier: median (range) |
|---|---|---|
| English scientific, "about 700 words" | 1.03 (0.99–1.14) | 0.86 (0.66–1.37) |
| English abstracts, "about 200 words" | 1.10 (1.02–1.17) | 1.17 (1.02–1.26) |
| English general, 400–800 words | 1.03 (0.91–1.12); 0.99 (0.95–1.07) | 0.95 (0.83–1.35); 1.24 (0.88–1.49) |
| French scientific, "environ 700 mots" | 0.89 (0.81–1.04) | 0.78 (0.64–0.88) |
| French abstracts, "environ 220 mots" | 1.16 (1.06–1.34) | 0.93 (0.80–1.20) |
| French general, 500–800 words | 0.97 (0.90–1.08) | 0.88 (0.74–0.98) |

(The two figures for English general prose are the two prompt sets.) The Haiku-tier figures are
an upper bound on its accuracy: its first batch answered 500-to-800-word requests with about
250 words after a run of abstracts, and was regenerated with the length range restated. The
practical point for the skill: a stated length is missed by a quarter in either direction often
enough that the count must be measured.

## 9. Continuation probe

Question: does a fresh model, given the first half of a paragraph, reproduce the second half
more often for AI-written paragraphs than for human ones (the DNA-GPT idea, in a black-box
version)?

Design (English, first version of the skill): 12 human paragraphs (PMC sections) and 12 AI
paragraphs (Sonnet tier, scientific), each of 4 to 9 sentences, split at the middle sentence. A
separate Sonnet-tier agent that had seen none of the texts continued each first half to the
original's length. Items were shuffled and unlabelled.

| Measure | Human | AI | Separation |
|---|---|---|---|
| Weighted n-gram containment (n = 2–4) | mean 0.0040, median 0.0017 | mean 0.0054, median 0.0033 | AUC 0.63 (weak) |
| Semantic move match, rated blind (0 = different points, 1 = partial, 2 = same points in the same order) | mean 0.75 | mean 1.17 | AUC 0.65 |
| Share rated **2** (fully predicted) | **8%** (1 of 12) | **42%** (5 of 12) | |
| Share rated 0 | 33% | 25% | |

With one continuation per paragraph, exact n-gram overlap is almost zero for everyone, so it
cannot carry a threshold. The semantic version shows the expected effect: a fresh model fully
anticipated the points of five times as many AI-written paragraphs. The shipped probe prints
real and continued halves side by side for a 0/1/2 rating and uses the n-gram score only to
rank paragraphs. The sample is small (24 items, one rater, blind to the labels), so the probe
is a diagnostic, not a gate. It has not been repeated in French.

## 10. Rebuilding

**The shipped registers** are rebuilt by one command in the skill's repository
(`calibration/run_all.sh`; `calibration/README.md` explains the steps): human sets → marker
words → measurements at fixed lengths → calibration with out-of-fold thresholds →
long-document check. It needs the corpora and takes a few minutes. Rebuild when the analyzer's measurements change, when a new model tier is added,
or when a register gets better human data.

**Your own register** (a field, a genre, another model), without the corpora:
```bash
# 20+ human texts of the target kind (known human, ideally pre-2020) and 20+ AI texts from the model you use
python3 scripts/sci_metrics.py calibrate --human path/to/human_txts --ai path/to/ai_txts \
        --register law --lang en --base scientific
python3 scripts/sci_metrics.py analyze draft.md --register law
```
This shorter procedure cuts every text to one common length (the 25th percentile of the human
lengths), reuses the metric definitions, research guards and dimensions of the base register,
recomputes bands, directions, weights and the threshold, and prints *in-sample* pass rates. It
does not cross-validate and sets no over-correction limit. With fewer than about 50 human
texts, expect the true human pass rate to be a few points below the in-sample 90%.

## 11. Caveats

- **Two tiers of one model family** generated the AI side. Other families differ (Huynh &
  McNamara: GPT-4o writes long, highly cohesive sentences, Claude 3.5 nominal and
  "sophisticated" ones), and fingerprints drift between versions. The classic guards and the
  two-sided scores are the protection; a new calibration is the remedy.
- **Task mismatch in the scientific sets.** The models wrote from titles and abstracts; the
  human sections had full data behind them. Part of the specificity gap is missing input, not
  style.
- **Era.** A third of the English general corpus is from 1961 (Brown). Dash and contraction
  rates are reported, not scored, for that reason. The French and the modern English sources
  are from 2012–2019.
- **Fields.** English scientific text is biomedical and life-science heavy (PubMed Central),
  French scientific text is medicine plus humanities and social sciences. Mathematics, law or
  engineering reports may sit elsewhere in the bands; word length is the first place it shows
  (`worked-example.md`, cases B and C).
- **One journal behind French medicine.** 97 of the 106 French PubMed Central sections (80 of
  87 articles) come from *The Pan African Medical Journal*. The OpenEdition half is spread
  over 64 journals.
- **Sample sizes.** 20 to 34 AI texts per tier and register. Pass rates of a few percent rest
  on one or two documents.
- **Percentile bands are descriptive.** One genuine human text in seven fails the gate. That is
  acceptable for a revision aid and would be unacceptable for an accusation.
