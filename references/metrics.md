# Metrics reference

How the scripts turn each pattern into a number: units, formulas, word lists, known weaknesses.
Read this when a result looks wrong, when you need to explain a number to the user, or when you
extend the analyzer. English and French use the same definitions; what differs is in the language
packs (`scripts/lang_en.py`, `scripts/lang_fr.py`).

## Contents
1. Units: word, token, lemma, sentence
2. Rhythm and paragraphs
3. Vocabulary: estimators, decomposition, marker words
4. Part-of-speech profile and nominalisation
5. Function words and connectives
6. Stance, sentiment, questions
7. Punctuation
8. Stock phrases and document-level checks
9. Padding
10. Structure: openers, skeletons, passives
11. Scoring: bands by length, dimensions, composite, guards
12. Length check and growth check
13. Compare mode
14. Fact ledger
15. Continuation probe
16. Known limitations

---

## 1. Units: word, token, lemma, sentence

Every script imports these from `scripts/textcore.py`, so a count means the same thing everywhere.

| Unit | Definition | Used for |
|---|---|---|
| **word** | a whitespace-delimited chunk that contains a letter or a digit. `don't`, `well-known`, `1,200`, `91%`, `l'étude`, `N'a-t-on` are one word each. A punctuation mark standing alone (` : `, ` ? `, ` % ` in French typography) is not a word | all lengths (document, paragraph, sentence), the length check, every per-1,000-word rate |
| **token** | a word after splitting clitics and elisions: `don't` → `do` + `n't`; `l'étude` → `l'` + `étude`; `a-t-il` → `a` + `il`. Numbers stay whole | word lists, part-of-speech shares (% of tokens) |
| **lemma** | the dictionary form of a token: `studies` → `study`, `étaient` → `être`, `les` → `le` | vocabulary measures, lemma lists (so inflection is not counted as variety) |
| **sentence** | split on `. ! ? …` followed by whitespace and a capital, digit or opening quote; abbreviations (`e.g.`, `et al.`, `Fig.`, `cf.`, `p.`) and initials do not end a sentence; French spaces before `? !` and guillemets are handled | rhythm, openers, per-sentence shares |

- **The document word count** (`count`, `--target-words`) is body paragraphs + list items +
  headings. Markdown syntax is not counted; code blocks and tables are left out and reported. It
  includes citation markers, as a word processor would.
- **Analysed words** are the body and list items with citation markers removed (`[12]`,
  `(Smith et al., 2020)`, `Smith (2020)`, `(Dupont, 2019 : 23)`): citations are forced choices, not
  style. Rates and the length used to pick calibration bands are based on analysed words.
- Markdown is understood: headings, tables, code blocks and YAML front matter are not prose. Each
  list item is its own paragraph flagged as a list; list items are left out of rhythm and
  paragraph statistics and included in word rates. In plain text, a line of at most 14 words
  that stands alone as a paragraph and has no end punctuation is treated as a heading (a title
  pasted above the text): counted in the document word count, left out of the analysis.
- **Tagging.** A lexicon gives each word form its most likely part of speech and lemma; suffix
  rules cover unknown words; a few context rules disambiguate. English: a word that can be a
  noun or a verb is a noun after a determiner, an adjective, a number or a possessive, a verb
  after `to` (unless it is a plural form: "led to changes"), a modal, a subject pronoun, `who`
  or `which`, and a verb when an article or an object pronoun follows ("needs a table"). French:
  `le/la/les` and `en` as pronouns before a verb, noun or verb after a determiner or clitic.
  English lexicon: 25,318 forms from the tagged Brown corpus, 91.0% coarse-tag accuracy on 5,396
  held-out Brown sentences; about a third of the remaining errors are capitalised common nouns
  and adjectives read as names (Brown is full of headlines and titles), and 6% of verbs are read
  as nouns. French lexicon: 61,425 forms from Lexique 3.83
  and UD_French-GSD (both CC BY-SA 4.0), 90.5% on the UD_French-GSD test set. Document-level
  rates are reliable; single-word judgements are not.
- Language is detected from the commonest function words, or set with `--lang en|fr`.

## 2. Rhythm and paragraphs

| Metric | Formula | Pattern |
|---|---|---|
| `sent_len_mean`, `sent_len_sd` | mean and population SD of words per sentence | too long (one model tier) or too short (another): scored on both sides |
| `sent_len_cv` | SD / mean | uniform rhythm: lower sentence-length variance [Strong] |
| `short_share`, `long_share` | share of sentences ≤ 10 words / ≥ 30 words | |
| `masd_norm` | mean \|len_i − len_{i−1}\| / mean | sentence-to-sentence change |
| `uniform_run_max` | longest run of consecutive sentences whose lengths all fit in a band of ±max(4, 0.25·mean) words; `uniform_run_at` gives its place | the "metronome", localised |
| `para_words_cv`, `para_sents_cv` | CV of paragraph length in words / sentences (≥ 3 paragraphs) | uniform blocks |
| `single_sentence_para_share` | share of one-sentence paragraphs | |

## 3. Vocabulary

### 3.1 Why not the type-token ratio
The raw ratio of distinct words to words falls as a text gets longer (Heaps' law), so texts of
different lengths cannot be compared with it. In the self-test, 300 and 2,400 words drawn from the
*same* source give 0.515 and 0.297. It is reported as `ttr_raw` and never scored.

### 3.2 Estimators (in `scripts/lexstats.py`, all on lemmas)

| Metric | Definition | Property |
|---|---|---|
| `types_at_100` | expected number of distinct lemmas in a random sample of 100 of the text's lemma tokens, divided by 100 | exact, order-free |
| `hapax_at_100` | expected number of lemmas occurring once in that sample, divided by 100 | exact, order-free |
| `mattr50` | mean type-token ratio over every window of 50 consecutive lemmas (Covington & McFall 2010) | sees where repeats fall |
| `mtld_wrap` | mean number of lemmas read, from every start position and wrapping around, until the running type-token ratio first falls to 0.72 (McCarthy & Jarvis 2010, wrap-around variant) | no partial factors |
| `yule_k` | 10⁴·(Σ f² − N)/N², f = lemma frequencies | repeat rate; driven by the commonest words; lower = more spread |
| `dispersion50` | `mattr50` divided by (rarefied types at 50)/50 | < 1: repeats cluster (a writer staying with a term); > 1: repeats avoid each other |
| `content_types_at_50`, `content_mattr25` | the same two ideas on content-word lemmas only (nouns, verbs, adjectives, adverbs) | variety of the content vocabulary alone |
| `fw_types_at_50` | rarefied distinct lemmas per 50 function-word tokens | variety of the grammatical vocabulary |

The sampling formulas are the hypergeometric expectations used in ecology (rarefaction) and behind
HD-D. For a lemma with frequency f in a text of N tokens, the chance that a random sample of n
tokens misses it is C(N−f, n)/C(N, n), so

    E[distinct lemmas in the sample]     = Σ_i [ 1 − C(N−f_i, n)/C(N, n) ]
    E[lemmas occurring once in the sample] = Σ_i f_i · C(N−f_i, n−1)/C(N, n)

`python3 scripts/sci_metrics.py selftest` checks both against Monte Carlo sampling, the boundary
cases (n = N gives the observed counts; n = 1 gives 1), their independence from word order, and
that the measures stay put between 300 and 2,400 words of one source while the raw ratio does not.

### 3.3 Which estimators are scored, and why
`calibration.md` (vocabulary experiment) reports, for each candidate, the separation between
human and AI text at equal length, the reliability (agreement between the two halves of one
text) and the drift with length on real text. In short: the window measures (MATTR, MTLD) do
not drift with length on real text but are noisier; the sampling measures are steadier but drift
upward in longer texts, because real texts change topic as they go; the hapax-per-100-window
measure of the first version was the least reliable. The gate therefore averages four all-word
measures in one dimension (`mattr50`, `mtld_wrap`, `types_at_100`, `yule_k`), compares every text
with human texts cut to the same length, and gives the dimension one verdict.

### 3.4 Decomposition: what drives a variety score
An all-word variety score mixes three things, which are measured separately:

| Part | Metric | Reading |
|---|---|---|
| grammatical glue | `glue_per100`: lemmas of the language's commonest grammatical words per 100 tokens (English: the, of, be, to, in; French: see `french.md`; the lists are derived from the corpora, see `calibration.md`) | too low = compressed prose; these words repeat constantly in human text, and their absence is what pushes all-word variety up |
| density | `lexical_density`: content-word tokens / tokens | too high = too many content words per sentence |
| content-word variety | `content_types_at_50`, `content_mattr25` | too high = synonym rotation and upgraded words; too low = a few abstract words recycled |

When the all-word dimension fails, look at these three to see which habit to change. Under
"Where to look" the report also prints the number of glue words in the text, by word, next to
the number a human text of that length has (median, 10th and 90th percentile of the band times
the text's token count): a target to count toward, and not past.

### 3.5 Marker words
`markers.ai_function_per1k`, `markers.ai_content_per1k`, `markers.human_function_per1k`,
`markers.plain_per1k`: rates of four word lists stored in `scripts/data/markers_<lang>.json`.
The lists are not hand-written. They come from the calibration corpora by the log-odds ratio with
an informative Dirichlet prior (Monroe, Colaresi & Quinn 2008), keeping only words that separate
AI from human text in at least two registers with the same sign. The file records, for each
list, the separation measured on documents that took no part in building it. A marker word is not
a forbidden word: the metric is a rate, and the fix is to bring the rate down, not to zero.

### 3.6 Other lexical measures
- `word_len_mean`, `long_word_pct` (≥ 9 letters): word length in letters, over alphabetic tokens.
- `rare_word_pct`: lower-case words absent from the tagging lexicon (field-specific vocabulary).
  Reported, not scored: it depends on the lexicon's coverage of the field and period.
- `compress_ratio`: zlib-compressed size / size. Reported, not scored.
- `repeated_3gram_per1k`, `repeated_4gram_per1k`: extra occurrences of within-sentence n-grams seen
  at least twice, without all-stopword and numeric n-grams and without `--protect` terms.
- `repeated_frames`: sentence-initial bigrams used at least twice ("This approach…").
- `top_content_words`: most frequent content lemmas, to spot recycled vocabulary.

## 4. Part-of-speech profile and nominalisation
- `noun_pct`, `verb_pct` (lexical verbs), `aux_pct` (be / have / do; être / avoir), `modal_pct`,
  `adj_pct`, `adv_pct`, `pron_pct`, `det_pct`, `adp_pct`, `cconj_pct`, `sconj_pct`, `num_pct`,
  `propn_pct`, `acronym_pct`: share of tokens, in percent.
- `deriv_adv_pct`: derived adverbs, English -ly (dramatically, increasingly; not only, early,
  likely) and French -ment (considérablement, notamment; not comment, moment). The plain adverb
  share also counts comparatives and question words, which should not be pushed down.
- `lexical_density`: (nouns + proper nouns + acronyms + lexical verbs + adjectives + adverbs) / tokens.
- `noun_verb_ratio` = nouns / lexical verbs. `nominal_verbal_ratio` = (NOUN+ADJ+ADP+DET) /
  (VERB+ADV+PRON+AUX+MODAL).
- `specificity_pct` = proper nouns + acronyms + numbers, % of tokens. **Never raise this by
  inventing specifics.**
- `first_person_per1k`, `second_person_per1k`, `pronoun_per1k`, `comparative_per1k`,
  `of_per100` (English `of`, French `de`).
- `nominalization_per1k`: nouns of at least 7 letters ending in -tion, -sion, -ment, -ness, -ity
  (English, after Biber 1988) or -tion, -sion, -ment, -ité, -ance, -ence (French), minus a
  stoplist (nation, moment, city; question, élément, société…). `nominal_heavy_sentences` lists
  sentences with three or more.

## 5. Function words and connectives
- `ai_fw_per1k`, `human_fw_per1k`, `fw_ratio`: the word lists published in the research (Desaire
  et al.; Kim & Desaire; Fujiwara, via the survey). They were derived from GPT-3.5-era English
  text and transfer only partly to current models (research-digest §4.9), so they are reported
  for comparison; the calibrated lists of §3.5 carry the weight. The French lists are
  translations of the English ones; like every metric, they count only where the French
  calibration shows a separation.
- Connectives are grouped into additive, contrastive, causal, conditional, exemplifying,
  sequencing, summarising and emphatic.
  - `connective_initial_share`: sentences opening with a connective.
  - `formulaic_initial_share`: sentences opening with an **additive, summarising or emphatic**
    one (Furthermore, Moreover, Overall, In conclusion; De plus, En outre, En effet, En somme).
  - `logical_connective_share`: of the unambiguous connectives anywhere in the text, the share
    that are contrastive, causal or conditional.
  - `connective_type_diversity`: distinct sentence-initial connectives / their tokens.
- Subordinators (Because, Although, If; Parce que, Bien que, Si) and coordinators (But, And, So;
  Mais, Or, Car) are **not** sentence-initial connectives: they open clauses and count as varied
  openers. Ambiguous adverbs (then, still, also, overall; ainsi, aussi, enfin, puis) count only
  when followed by a comma.

## 6. Stance, sentiment, questions
Categories follow Hyland's (2005) model of stance:
- `hedges_per1k` (may, might, perhaps, seems, suggests; peut-être, sembler, pourrait, sans doute)
- `boosters_per1k` (clearly, certainly, demonstrates; clairement, démontrer, sans aucun doute)
- `attitude_per1k` (surprisingly, unfortunately, puzzling; étonnamment, malheureusement, discutable)
- `self_mention_per1k` (I, we, our; je, nous, notre)
- `stance_per1k` = the sum. Single words are matched as lemmas; capitalised `May`/`Will`
  mid-sentence are skipped.
- `question_share`: sentences ending in `?`.
- `critical_per1k`, `promo_per1k`: two small evaluative lexicons (problem, weak, flawed, risk;
  crucial, robust, comprehensive, transformative; French: problème, lacune, insuffisant;
  crucial, primordial, incontournable, véritable). Noisy on short texts.

## 7. Punctuation
- `per1k` for comma, period (sentence-final), semicolon, colon (not inside times or ratios),
  question mark, exclamation mark, opening parenthesis, quotation (pairs of " " or one «), and
  dash (em dash, spaced en dash, spaced `--`).
- `punct_entropy_nodash`: Shannon entropy over the eight marks other than dashes, divided by log2(8).
- `nonbasic_share_nodash`: share of those marks that are not commas or periods.
  **Dashes are excluded on purpose**: human punctuation is more varied, but many LLMs over-use em
  dashes, so variety must come from parentheses, semicolons, colons, questions and quotations.
- `em_dash_per1k`, `comma_per_sentence`, `contraction_per1k` (English).
- French typography is checked and reported, never scored: missing space before `; : ! ?`,
  straight quotes instead of « », an unspaced em dash, a decimal point before `%`, `etc...`,
  ordinals in `ème`.

## 8. Stock phrases and document-level checks
- `stock_per1k`: multi-word formulas, split into research-cited (`stock_research_per1k`) and
  practitioner-observed (`stock_practitioner_per1k`). Patterns are matched on lower-cased text
  with straight apostrophes.
- `ai_vocab_per1k`: single words from practitioner lists (delve, tapestry, foster; enjeu, levier,
  paradigme). Reported, not scored: several are legitimate terms in some fields.
- `significance_echo_sentences`: sentences like "These findings highlight the importance of…".
- `extraposition_per1k`: "it is important / essential / worth … to / that"; "il est important /
  essentiel … de / que".
- `triad_lists_per1k`: coordinated lists of three or more parallel items, with or without the
  serial comma (so dropping the comma cannot game it).
- `stock_opener`: the first sentence matches a stock opening ("In recent years…", "Ces dernières
  années…", "À l'ère de…").
- `formulaic_ending`: the final paragraph opens with a summarising connective or contains
  future-outlook boilerplate.
- `paragraph_wrapup_share`: paragraphs (≥ 3 sentences) whose last sentence is a summary connective
  or a significance echo.

## 9. Padding
Padding is text that can be deleted without the reader losing a fact, a step of reasoning, a
condition, a limit or a consequence. A word list cannot decide that; it can point at candidates.

| Metric | What it counts | Note |
|---|---|---|
| `participial_clause_per1k` | a clause tacked on after a comma with a present participle followed by a function word: ", highlighting the…", ", making it…", ", soulignant ainsi…", ", permettant de…" | more frequent in AI text (Reinhart et al.; calibration). Lists of gerunds are excluded |
| `shell_noun_per1k` | abstract framing nouns (role, challenge, framework, landscape, dynamics; enjeu, cadre, démarche, dynamique, levier), counted only where the tagger reads the word as a noun ("a need", not "it needs") | after Schmid's "shell nouns": they frame content without being content |
| `metadiscourse_per1k` | the text announcing or commenting on itself ("it is worth noting", "as mentioned above", "in other words"; "il convient de souligner", "autrement dit") | |
| `wordy_per1k` | phrases with a shorter equivalent ("in order to", "due to the fact that"; "dans le but de", "au niveau de") | **human scientists use more of these than current models do.** It is a ceiling guard against piling them up, not a target of zero |
| `double_hedge_per1k` | stacked hedges ("may potentially", "seems to suggest"; "pourrait éventuellement") | |
| `binomial_per1k` | two words of one class (as tagged in the sentence) joined by and / or outside a longer list ("robust and reliable") | noisy; many doublets are real pairs, and human texts have plenty |
| `restatement_share` | sentences of which at least 60% of the content lemmas already stood together in one earlier sentence | candidates for the deletion test |
| `expletive_opener_share` | sentences opening with "There is / It is … that"; "Il y a / Il est … que / C'est … qui" | |
| `intro_outro_overlap` | share of the last paragraph's content lemmas already present in the first paragraph | an ending that repeats the opening |

Overlapping phrases are counted once (the longest wins: "due to the fact that" does not also
count "the fact that"). In French, a phrase ending in `de`, `que`, `ne`, `se`, `ce` also matches
its elided form (`afin d'`, `bien qu'`).

## 10. Structure: openers, skeletons, passives
- Opener classes: `connective`, `subject`, `subordinate`, `prepositional`, `adverbial`,
  `participial` (English -ing / -ed first; French present participle, gérondif "En comparant…",
  past participle), `verb-initial`, `coordinator`.
  - `subject_initial_share`; `varied_opener_share` = subordinate + prepositional + adverbial +
    participial + coordinator; `top_first_word_share`.
- `skeleton_entropy`: normalised entropy of the first three tags of each sentence.
- `passive_sentence_share`: English be / get + participle within three tokens; French être +
  past participle, excluding verbs conjugated with être (aller, venir, devenir…) and pronominal
  verbs. An approximation in both languages.

## 11. Scoring

`scripts/data/calibration.json` holds one entry per language and register (`en.scientific`,
`fr.general`, …). For each metric it stores the human percentiles **at each calibrated text
length**, the separation per AI model tier, the direction, the dimension, the research guard and a
fix hint; for each length it stores the composite threshold, the bands of each dimension score
and the measured pass rates.

1. **Length matching.** The bands used for a draft are those of human texts cut to the draft's
   own length, interpolated linearly between the two nearest calibrated lengths (outside the
   calibrated range, the nearest one). This matters because the spread of every rate shrinks as
   a text gets longer, and several measures shift with length.
2. **Metric score.** z = (distance from the human median toward the AI side) / (spread of the
   human values on that side, as a standard deviation), clipped to [0, 4]. The spread comes from
   the first quantile on that side that differs from the median (p75 or p25, else p90 or p10,
   else p97.5 or p2.5), because count metrics are zero for most human texts. Direction: +1 (AI
   higher), −1 (AI lower) or both sides, when the model tiers err in opposite directions.
3. **Which metrics count.** A metric enters the composite when at least one AI tier separates
   from human text on it (|AUC − 0.5| ≥ 0.15, averaged over lengths). A research guard (the
   direction the literature documents as a tell) is never reversed: evidence against it only
   removes the metric from the composite.
4. **Dimension score and verdict.** The mean z of a dimension's metrics. PASS / WARN / FAIL are set
   against the distribution of that same score in human texts of the same length (at or below
   the human 75th percentile / 90th / above). One verdict per dimension, however many metrics
   it holds.
5. **Composite: the lean toward the nearest AI profile.** The calibration stores one weight
   vector per AI model tier. The weight of a dimension is how far that tier's texts sit above
   human texts on the dimension score, divided by the score's variance (the two groups' variances
   averaged, with a floor of 0.05), set to zero where the tier does not deviate, and normalised
   to sum to 1. This is a linear discriminant that treats the dimensions as independent. For a
   draft, each profile gives the weighted mean of the draft's dimension scores, and the composite
   is the largest of them: the draft is judged against the model it most resembles. The report
   names that profile and prints, for each dimension, its share of the composite. An unweighted
   root-mean-square was tried first and rejected: it let weak dimensions dilute strong ones
   (`calibration.md`, composite experiment). A register calibrated without profiles falls back
   to the root-mean-square.
6. **Gate 1: composite within the threshold.** The threshold is the 90th percentile of human
   composites at the draft's length. Thresholds and dimension bands come from **out-of-fold**
   scores: every human text is scored by bands, metric choices and weights it did not help to
   set (5 folds by document, repeated twice), so the threshold is not flattered by its own data.
7. **Gate 2: classic guards.** Research-documented tells (formulaic openers, stock formulas,
   significance echoes, paragraph wrap-ups, repeated frames, uniform runs, flat punctuation,
   missing stance, piled-up padding) are checked against the extreme human range (p97.5 or p2.5,
   with a minimum rate for counts) even when current models do not show them. At most one
   violation is allowed.
8. **Gate 3: over-correction.** Each one-sided metric is also scored on the far side of the
   human median (the side away from the AI profile), with the same formula. The far-side scores
   are averaged per dimension, and the root-mean-square over dimensions must stay within the
   99th percentile of out-of-fold human texts at that length (never tighter than the 97.5th
   percentile of other human corpora of the register, where one exists). The report prints the
   value, the limit and every dimension at 1.5 or more; a metric beyond the human 97.5th (or
   2.5th) percentile on the far side is marked OVER. Metrics whose far side is harmless carry
   `"far_side": false` and are left out: the padding and stock-phrase counts, the over-used
   marker words, promotional vocabulary, and names and numbers. Less of the first four and more
   of the last is not a fault. Two-sided metrics (sentence length) are already scored on both
   sides in the composite.
9. **Long documents.** Beyond 1.35 times the longest calibrated length the text is cut into
   equal windows of calibrated length; each window is scored against the bands for its length.
   The document passes when the mean window composite is within the threshold, no window exceeds
   the classic-guard allowance, and the mean over-correction is within its limit. The report
   lists each window.
10. `--waive DIMENSION[,DIMENSION]` removes dimensions that cannot move without fabrication (for
    example `specificity` when the source has no names or numbers). The report prints the waiver.

The z-scores only rank texts. The error rates of the gate (how many human and AI texts pass at
each length) are measured, not derived from a normality assumption; they are in `calibration.md`
and are printed with every gate line.

## 12. Length check and growth check
- `count FILE` prints the document word count and its parts. With `--target-words N` (allowed
  range ±10%, `--tolerance` changes it), `--min-words`, `--max-words` it prints ON TARGET, UNDER
  or OVER and exits 1 when off. The same options on `analyze` add the verdict to the report, and
  `--source FILE` lists the numbers and names of the source that the draft has not used.
- `growth OLD NEW --register R [--source FILE]` answers one question after a draft was
  lengthened: did the added words bring information? OLD is the text before lengthening began.
  It reports three things.
  1. Per 100 added words, the **new content lemmas** (content words absent from the old
     version) and the **new specifics** (numbers, names, acronyms absent from the old version),
     next to what human texts of that register add when they grow from the same length
     (percentiles in the calibration file; the human reference is the growth of the first N
     words of a text into its first M words, N < M among the calibrated lengths).
  2. **Padding rates that went up.** A rate "went up" when the new version has at least two
     occurrences more than the old rate predicts for its length, the rate rose by 30% or more,
     and it now exceeds the rate of the median human text of that length. One more framing noun
     in 600 words is not padding.
  3. **Unanchored added sentences.** A sentence of NEW is *added* when no sentence of OLD
     contains 70% of its content lemmas. An added sentence is *unanchored* when fewer than 40%
     of its content lemmas occur in OLD or in the source (`--source`: the notes or the brief)
     and it carries no number, name or acronym. The report quotes up to ten of them, least
     anchored first, and gives the share of the added words they hold. General statements about
     the topic, comments on the importance of a result and claims the source does not make all
     land here; so, sometimes, does a legitimate consequence stated in new words, which is why
     the list is a prompt for the deletion test and not a verdict by itself.
  - PADDING: fewer new content lemmas than 90% of human texts add (the addition mostly repeats),
    or two or more padding rates went up, or 40% or more of the added words are in unanchored
    sentences.
  - THIN: one padding rate went up, or no new specific at all, or 25% or more of the added
    words are in unanchored sentences, or fewer new content lemmas than three quarters of human
    texts add together with fewer specifics than the human median.
  - SUBSTANCE otherwise.
  Generic filler brings many new *abstract* words, so the content-lemma rate alone does not
  catch it (in one test, filler brought 43 new content words per 100 added, real material 30);
  the padding rates, the missing specifics and the unanchored sentences do. The 40% anchoring
  bound and the 25% / 40% shares are set from worked cases, not from a corpus: a text lengthened
  from its notes had 9% of its added words in unanchored sentences, a deliberately padded one
  45 to 71%, and a model's padded answer 29% (`worked-example.md`, case B). Every new specific
  must still pass the fact ledger. The check compares vocabularies, so it is meant for a
  version that only adds to the earlier one: after a full rewrite, changed wording counts as
  new content.
- `analyze --source FILE` applies the same anchoring test to the whole draft against the source
  (when the source has at least 60 words; a one-line brief anchors nothing). It prints the
  share of the draft's words that stand in unanchored sentences, lists those sentences under
  "Where to look", and prints CHECK THE LENGTH when the share is 25% or more and the count is
  in range or above it. In a text that reports, such sentences are padding; in a text that
  interprets (a discussion written from a list of findings had 37%), they are the reasoning,
  and the reader of the report decides sentence by sentence.
- With `--source` and a draft that is UNDER its target, `analyze` also says when the draft
  already uses the source's numbers: from there on, only calculations and consequences of the
  source's facts can add length, and the instruction is to stop.

## 13. Compare mode
`sci_metrics.py compare draft --ref reference` runs two-proportion z-tests on word-level rates
(nominalisations, pronouns, function-word lists, derived adverbs, nouns, verbs, adjectives,
specifics, commas, other punctuation, dashes, padding and stance markers) and sentence-level
rates (initial connectives, passives, questions, subject-first openings), plus a two-sample
Kolmogorov–Smirnov test on the sentence-length distributions. |z| ≥ 1.96 means the draft differs
from the reference at p < .05. Vocabulary is compared with the fixed-sample measures of §3.2,
so the two texts may differ in length. Power is low under about 300 words per side.

## 14. Fact ledger
`fact_ledger.py SOURCE DRAFT` extracts and compares:
- **numbers**, normalised by value: English `1,900,000` = `1.9 million`, `11 percent` = `11%`;
  French `1 200` = `1200`, `3,5 %` = `3.5%`, `1,9 million`. Number words are review items.
- **citations**, as references: `[4, 7]` and `[3-5]` by number, `(Smith et al., 2020)` and
  `Smith et al. (2020)` as the same key `smith 2020`. Moving a citation into the sentence is not
  a change; dropping or adding a reference is.
- capitalised names and acronyms (review list), `--protect` terms (hard fail if lost).
- hedges, boosters and negations per 1,000 words, with warnings when hedges drop, boosters rise
  or the negation count changes.
- **derived numbers**: a number that is absent from the source but equals simple arithmetic on
  two source numbers, rounded as written, is listed with the formulas found (at most three)
  instead of failing: a product (38 × 45 = 1710), a ratio (60 / 38 = 1.6), a sum or difference,
  a percentage (100 × 9 / 38 = 24%), a relative change (100 × (1840 − 1210) / 1840 = 34%), a
  complement (2000 × (100 − 89%) = 220). Three conditions keep coincidences out. The operands
  must stand in the **same paragraph of the draft** as the derived number, and operands in the
  same sentence are tried first (a number already accepted as derived can serve as an operand
  of the next). Percentages are accepted only from
  percentage arithmetic. Bare integers under 10 are never accepted. Without the first
  condition the check would prove nothing: a source with thirty numbers has about 900 ordered
  pairs, and some pair matches almost any two-digit percentage. A number that matches only
  operands standing elsewhere is reported with that formula and still counts as added. The
  writer confirms which formula is meant.
Exit code 1 means a hard fact changed. `--write` (source is a brief) fails only on additions,
and sentences of the brief that are requests ("Please draft the Discussion, about 700 words")
are not treated as facts. `--facts FILE` names extra facts from the user (an abstract, notes):
values found there may appear in the draft without counting as added, but are not required.

## 15. Continuation probe
`dna_probe.py split draft` cuts every paragraph of at least four sentences in half and prints a
prompt for a **fresh** model to continue each first half; `dna_probe.py score` puts each real
second half next to the continuation and computes a weighted n-gram overlap as a ranking aid.
The judgement is the reader's: when the fresh model made the same points in the same order,
the paragraph only says what comes next by default.

## 16. Known limitations
- English and French only.
- The taggers are about 90% accurate at the level of coarse classes; noun/verb homographs are
  the main source of error in English.
- Under 150 words no gate is applied; under about 300 words compare mode has low power.
- Word lists cannot tell a statistical "significant" from a promotional one, or a technical
  "landscape" from a figurative one. Read the hits in context.
- Padding metrics point at candidates; whether a sentence is filler is decided by the deletion
  test, which only a reader can run.
- The calibration covers two tiers of one model family and the human corpora listed in
  `calibration.md`. Other fields, genres or models may differ; rebuild with
  `sci_metrics.py calibrate`.
- These are descriptive statistics about prose. They are **not** evidence about who wrote a text
  and must not be used to accuse anyone.
