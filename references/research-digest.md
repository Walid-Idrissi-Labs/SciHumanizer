# Research digest: what the papers say about how AI text is written

This file is the evidence base behind SKILL.md. The first version condensed the author's analysis
files, one per paper, for eleven papers. This version goes back to the papers themselves: ten of
the eleven were re-read in full, finding by finding, and every quotation used here was checked by
machine against the paper's text. The eleventh (Huynh & McNamara) could not be retrieved (the
publisher blocks automated access), so its numbers still come from the analysis file and are
marked as such.

Evidence labels used below and in SKILL.md:

- **[Strong]**: consensus across many studies (the 44-study survey)
- **[Moderate]**: several studies, or one large benchmark
- **[Single]**: one study, or one model family
- **[Calibrated]**: measured by this skill on its own corpora, human against current models at
  equal length (`calibration.md`). Where a paper and the calibration disagree, both are given
- **[Mechanism]**: explains *why* the pattern appears
- **[Not actionable]**: real, but a writer cannot see or change it

## Contents

1. The generative mechanism
2. Measured differences between AI and human text
3. Numbers worth keeping
4. Contradictions, and how the skill resolves them
5. Length, verbosity, padding and density
6. Text length and the reliability of statistics
7. Languages other than English, French in particular
8. What is not actionable at the writing level
9. Methodological warnings the skill inherits
10. One card per paper
11. Corrections to the first version of this digest

---

## 1. The generative mechanism [Mechanism]

LLMs write by sampling token after token from P(x_t | x_<t). Every source agrees on the
consequence: the output leans toward high-probability choices.

| Mechanism | What it leaves in the text | Source |
|---|---|---|
| Preference for high-probability tokens | Lower perplexity than human text | Review (Li et al. 2026); 2601.03812 |
| Greedy / top-k decoding | Over-represented frequent tokens | Review |
| Nucleus (top-p) truncation | Missing low-probability tokens (the tail is cut off) | Review |
| Low temperature | Rigid, formulaic phrasing | Review |
| Beam search | Overly coherent, "planned" structure without human local inconsistencies | Review |
| Training objective minimises perplexity | No incentive for human-like variation | Survey 2510.05136 |
| No communicative intent | Weak pragmatic goals (stance, audience, purpose) | Survey 2510.05136 |

Detector findings that describe the same property from different angles:

- **Low perplexity / low burstiness**: human writing has bursts of low-probability tokens, while AI
  text has a flatter token-probability profile (2601.03812).
- **DetectGPT probability curvature**: AI text sits near a local maximum of log-probability, so small
  perturbations lower its probability more than they lower human text (Review; 2303.13408).
- **DNA-GPT**: truncate an AI text and regenerate. The regenerations converge on the original's
  n-grams, while human continuations diverge (Review).
- **Ghostbuster** (NAACL 2024): AI text is "too probable" even under *weaker* models (unigram,
  trigram, GPT-3 Ada/Davinci), and ChatGPT documents "tend to be more predictable than human
  documents", a difference that grows toward the end of the document.
- **Spike entropy (KGW)**: a watermark can only act on high-entropy positions. Where the model is
  confident (a fact, a name, a fixed term) the token is forced.
- **Self-information (SIRA)**: the per-token "surprise" I(x) = -log P(x | context) is the useful
  unit for locating where a text is predictable.

**Writing-level translation.** AI prose picks the modal option at every *free* choice: the
opener, the transition, the adjective, the framing verb, the example, the closing sentence.
Forced choices (terminology, names, numbers, established collocations) look the same in human and
AI text. So the working principle of the skill is: **spend surprise where the choice is free and
never where it is forced.** The surprise must be the meaningful kind: a precise, specific,
situated choice. Random rare words do not qualify (see §3, synonym substitution).

One caveat from the review: models of the GPT-4 class "can produce outputs that match or even
surpass human writing in terms of perplexity, syntactic complexity, and information density".
The mechanism still holds, but its surface signs moved, which is why this skill measures current
output instead of trusting older lists (§4, §9).

---

## 2. Measured differences between AI and human text

The survey (44 studies, 2019–2025) is the main source. The last column says what this skill's
calibration found for current Claude models (Sonnet and Haiku tiers) against pre-2020 human text
of the same register and length: **same**, **reversed**, or **depends** (on tier or register).
Numbers are in `calibration.md`.

### 2.1 Lexicon

| Feature | AI text (papers) | Strength | Current Claude [Calibrated] |
|---|---|---|---|
| Lexical diversity | Lower in most studies; higher than human for GPT-4 (Herbold et al.); higher in two essay studies | [Strong], model-dependent | **Reversed**: higher on every all-word measure. The cause is density, not synonyms (§4.1) |
| Vocabulary size, repetition | Smaller vocabulary, more repetition, more frequent word n-grams (n ≥ 3) | [Strong] | **Reversed** for repeated 3-grams (fewer than human) |
| Diversity of function words | Lower (Zindela; André et al.) | [Single] | **Reversed**: the few commonest function words are under-used, the rest spread wider |
| Function words more frequent in AI | `and`, `can`, `by`, `with`, `for`, `their` | [Moderate] (Desaire et al.; Kim & Desaire; Fujiwara) | **Depends**: `can` holds outside abstracts, `and` for the Haiku tier; `by` is now *less* frequent in every register, `with` in scientific text |
| Function words less frequent in AI | `however`, `but`, `although`, `because`, `if`, `that`, `or`, `when`, `as`; `this`, `I`, `they`, `my`, `it`, `us`; `to`, `as`, `before`, `about`, `since`; `will`, `would`, `might`, `could`; `up`, `out`, `off` | [Moderate] | **Depends**: `although`, `will` and, mostly, `to` and `as` hold; `or` is now *more* frequent in every register, `this`, `might`, `would` in scientific text |
| The commonest grammatical words (`the`, `of`, `in`, `be`, `to`) | Not studied as a group; "more determiners and adpositions" in older models | n/a | **AI far lower**: a quarter to a third fewer in papers and general prose, up to half in abstracts, in both tiers. The most consistent signal measured (§4.9) |
| Word length | Longer tokens (André et al.); no difference in one study | [Single] | **Same**: longer words in both tiers |
| Content words | AI: `others`, `researchers`, `stand out feature`, `incredibly polite`, `knowledgeable`. Human: `say`, `feels like`, `felt sick`, `hate`, sensing verbs (`read`, `look`, `hear`) | [Moderate] | Different words now: see the calibrated marker list in `calibration.md` |
| Aggressive or rude expressions | Absent | [Single] (Mitrović et al.) | not measured |
| Idioms | Fewer | [Moderate] | not measured |
| Non-existent words and names | Present (fake drug and disease names, Japanese clinical text) | [Single] | Invented vivid detail when writing from a brief (SKILL.md, F5) |
| Punctuation variety | Lower: commas and periods dominate. Fewer commas, question marks, dashes, parentheses, semicolons, colons; more single quotes and periods (Desaire et al.; Simon et al.) | [Moderate] | **Same** for variety, parentheses, semicolons, colons. **Reversed** for commas in the Sonnet tier (more) |

### 2.2 Grammar

| Feature | AI text (papers) | Strength | Current Claude [Calibrated] |
|---|---|---|---|
| Syntactic complexity (dependency distance) | Higher (4 of the 5 studies that find a difference) | [Strong] | not measured directly |
| Sentence-length variance | Lower | [Strong] | **Depends**: lower in the Haiku tier and in French; human-like in the Sonnet tier in English |
| Average sentence length | "little consensus" | n/a | **Depends on the tier**: Sonnet much longer than human, Haiku shorter (§4.11) |
| Nouns, determiners, adpositions, coordinating conjunctions | More | [Strong] (older models) | **Reversed** for adpositions and for the article `the`; nouns higher only in the Haiku tier |
| Adverbs | Fewer | [Strong] (older models) | **Reversed**: more, above all derived adverbs in -ly / -ment |
| Auxiliary and copula relations | More (Liao et al.; Muñoz-Ortiz et al.) | [Single] | **Reversed**: fewer forms of be / have |
| Adjectives | Fewer in news (Muñoz-Ortiz et al.) | [Single] | **Reversed**: more |
| Proper nouns, first-person pronouns | Fewer | [Strong] | **Same** |
| Nominalisation | More (Herbold et al.; Reinhart et al.) | [Strong] | **Same** as clusters (sentences with three or more); overall rate higher mainly in the Haiku tier |
| SVO word order | Rigidly canonical; humans vary constituent order more | [Strong] | **Same** (more subject-first sentences) |
| Phrasal coordination, **present participial clauses**, that-clauses as subjects | More (Reinhart et al., Llama 3 and GPT-4o) | [Moderate] | **Same** for participial clauses tacked on after a comma |
| Coordination ("enumeration") | More (Strübbe et al., English / French / German) | [Single] | **Same**, weakly (lists of three) |
| POS-sequence templates | More repetitive (Shaib et al.) | [Moderate] | not gated |
| Discourse markers | Less frequent, more repetitive | [Moderate] | **Same** in English (fewer sentence-initial connectives than human scientists) |
| Modal and epistemic markers | Fewer | [Moderate] | **Depends**: hedges slightly more frequent, but generic |
| Comparatives and superlatives | Fewer (Simon et al.) | [Single] | **Reversed** in general prose |
| Readability | Lower (Markowitz et al.) | [Single] | consistent with longer words and denser phrasing |
| Cohesive devices and formulaic constructions | Heavy reliance (Wu) | [Single] | see stock phrasing, §2.4 |

Also measured by 2601.03812 on HC3 (ChatGPT answers): more NOUN, VERB, ADP, AUX tags; more
linking words; lower perplexity; lower burstiness; more uniform readability scores.

### 2.3 Style, stance, emotion (survey; MAGE)

| Feature | AI text | Strength |
|---|---|---|
| Formality | Higher | [Moderate], genre-dependent |
| Analytic / descriptive vs narrative | More analytic, less narrative | [Moderate] |
| Involvement | Less (impersonal; fewer personal references) | [Moderate] |
| Abstraction | More, depending on genre (Sardinha) | [Moderate] |
| Neutral sentiment | More | [Strong] |
| Negative emotion in opinion text | Sanitised: anger and disgust absent, higher valence | [Moderate] (MAGE) |
| Emotion in reviews | Sometimes *more* emotional | [Single] (Markowitz), so genre matters |

### 2.4 Discourse and document level

- **Neutral, non-committal phrasing** carries the highest attention weight in SHAP analysis of a
  detector (Review, Mitrović et al.). Implied patterns: "It is important to note that…",
  "Furthermore, it can be observed…", "In conclusion…".
- **Excessive connectives**: "furthermore", "moreover", "additionally", "consequently",
  "therefore". Formulaic balance: "Not only X, but also Y" (Review).
- **Nominal rephrasing**: "The analysis of the data is performed by the model" instead of "The
  model analyzes the data" (Review).
- **Argument templates**: rigid claim → evidence → rebuttal → conclusion structure with
  predictable paragraph-level organisation (ArguGPT, in Review).
- **Paragraph over-coherence**: AI paragraphs are more internally coherent than human ones
  (Review).
- **Hybrid boundaries**: where human and AI text meet, style shifts abruptly (Review).
- **Audience insensitivity** ("uniformity drift"): GPT-4o (June 2025) gave all four reader profiles
  nearly identical output. Human writers, and GPT-4.1, adjust to the reader (Huynh & McNamara,
  from the analysis file).
- **Formal upgrading**: human "was sent off" became AI "was dismissed for a second bookable
  offence" (MAGE, example pair).
- **Corporate template for negative experience**: an angry review continued as "I apologize for
  the inconvenience you experienced. We strive to provide exceptional service…" (MAGE).
- **Hallucinated specifics**: plausible but wrong names (MAGE; survey). Topic drift in weaker
  models (a football report continued as a wellness text).

### 2.5 Model fingerprints [Single] and [Calibrated]

From Huynh & McNamara (analysis file; text simplification task): Claude 3.5 had the highest
noun-to-verb index and the most "sophisticated" wording of four models; GPT-4o the longest
sentences and highest cohesion. Ten regenerations of one prompt showed no significant linguistic
variation, and fingerprints drifted between versions of the same model.

From the survey: GPT-4 has higher lexical diversity than GPT-3.5 and than human essays (Herbold et
al.); GPT-4 "gives shorter answers and exhibits a larger vocabulary size and density" than
GPT-3.5 (Rosenfeld & Lazebnik); GPT-4o uses downtoners (`barely`, `nearly`) and Llama 3 clausal
coordination (Reinhart et al.). MAGE: removing lexical-richness features helps detection for
some families (OpenAI, Llama, GLM) and hurts it for others (FLAN-T5, OPT, BigScience), so
families cluster into groups with different lexical behaviour.

From this skill's calibration: the two Claude tiers share most of their fingerprint (compressed,
dense, long-worded, few specifics, flat punctuation, extra derived adverbs) and differ in rhythm.
The Sonnet tier writes sentences far longer than human ones; the Haiku tier writes shorter, more
uniform sentences in short paragraphs, with more nouns and nominalisations. **A gate tuned to one
tier misses the other**, so metrics on which the tiers err in opposite directions are scored on
both sides.

---

## 3. Numbers worth keeping

**Lexical richness (MAGE: 284 features, 27 models from 7 families, 10 domains, English)**
- Lexical richness is the strongest feature area: removing it costs 13.1 F1 points in the main
  setting, against 1.8 for the next area. Linguistic features alone reach 82.7 macro-F1.
- The three features are the raw type-token ratio, **global hapax legomena** ("the number of
  tokens per text that only occur once across the whole dataset", a measure of rare, specific
  words, not of words used once within the text) and lexical density (share of adjectives, nouns,
  verbs and adverbs).
- Raw TTR: human around 0.6, AI around 0.8, read by the authors as humans using "a more varied
  vocabulary relative to text length". The paper's own examples show why the raw value cannot be
  compared: 822 human tokens against 108 AI tokens, 978 against 160, 1,191 against 190. "AI-generated
  continuations are typically shorter but exhibit higher TTR and lexical density"; "human-written
  texts tend to be longer with lower TTR due to natural repetition". See §6.
- Human-AI separation on lexical richness is weakest for scientific text (SciGen) and short
  factual answers (SQuAD).
- Emotion (Yelp pairs): the human review scores anger and disgust; the AI continuation has
  neither and a higher valence.

**Document length (Ghostbuster)**: "may be unreliable for documents with ≤ 100 tokens, and its
performance levels off with ≥ 500 tokens". The 91 TOEFL essays on which detectors failed were
short (median 104 words; the other datasets were above 350). More in §6.

**Edits and paraphrase**
- Swapping adjacent sentences or paragraphs barely affects a probability-based detector
  (Ghostbuster): "most global edits do not significantly affect performance and numerous local
  edits are required". **Reordering is not rewriting.**
- Blind synonym substitution destroys both fluency and meaning: in SIRA's comparison it gives
  perplexity 252.85 and a sentence-embedding similarity near zero, where model paraphrases keep
  perplexity at 9–12 (the unedited text: 9–16) and similarity at 0.75–0.88.
- Paraphrasing in context and several sentences at a time scores better on automatic quality
  measures than sentence-by-sentence paraphrasing without context (DIPPER: preferred in 71% of
  comparisons or more).
- Meaning preservation is measured in the paraphrase literature on a 5-point equivalence scale
  (DIPPER: three annotators put over 80% of paraphrases at 4 or 5) and by sentence-embedding
  similarity (SIRA, Chainwash). The skill borrows the scale: every paragraph must stay at 4/5 or
  better.
- Meaning drifts with every extra rewrite pass (Chainwash: mean semantic preservation is above
  0.92 after one rewrite and about 0.86 after five). Rework the implicated sentences; do not
  re-paraphrase the whole text.
- An instruction to "humanize" is not a stronger rewrite than a plain paraphrase. In Chainwash it
  was the weakest of five instructions for one rewriter (54.8% against 83.3%) and "weaker in some
  settings" overall.
- Style prompts alone do not hide the probabilistic signature: Ghostbuster "achieved 99.5 F1
  across prompt variants", including requests "to write in the style of a high-school student".

**Watermark statistics (for completeness)**: KGW's test is a one-proportion z-test,
z = (|s|_G − γT) / √(Tγ(1−γ)), with z > 4 giving a false-positive rate of 3 × 10⁻⁵. The same
logic (a count against its expected value under a reference rate) is reused in
`sci_metrics.py compare`. Its power grows with length: detection is possible "from short spans of
tokens (as few as 25 tokens)" in the best case and takes about 128 tokens at the paper's settings.

**Classifier landscape (2601.03812)**: TF-IDF + logistic regression 82.87%; BiLSTM 88.86%;
DistilBERT 88.11%; a RoBERTa with POS, readability, perplexity and burstiness features reaches
99% on HC3. With topic-based splits performance holds: detectors learn *style*, not topic.

---

## 4. Contradictions, and how the skill resolves them

### 4.1 Is AI lexical diversity lower or higher?
- The survey: lower in most studies, but "while lexical diversity is higher in HWT compared to
  AIGT produced by GPT-3.5, it is also lower compared to text generated by GPT-4" (Herbold et
  al.). MAGE: raw TTR higher for AI, on much shorter texts.
- This skill's calibration, at equal length: current Claude is higher on every all-word measure
  (MATTR, MTLD, rarefied types, Yule's K), in three registers and two tiers.
- **Why** (`calibration.md`, vocabulary experiment): the excess is mostly not synonym rotation. AI
  text uses far fewer of the commonest grammatical words (§4.9) and more content words per
  sentence, so any 50-word window holds fewer repeats. When the part explained by lexical
  density or by the share of the top function words is removed, the Haiku tier's excess
  disappears. Content-word variety at a fixed number of content words is higher for the Sonnet
  tier (clearly so in scientific prose) and not for the Haiku tier, whose general prose is
  *lower* than human.
- **Resolution:** measure variety at fixed sample sizes and equal length; report the three parts
  separately (all-word variety, content-word variety, grammatical glue); fix the part that is off.
- **What never helps:** raising or lowering variety by cycling synonyms for the same concept.

### 4.2 Are connectives over-used or under-used?
- The Review and 2601.03812 say over-used. The survey says less frequent and more repetitive.
- **Resolution:** AI over-uses a *small set of formulaic, mostly additive and summarising*
  connectives at sentence starts (Furthermore, Moreover, Additionally, Overall, In conclusion), and
  under-uses logical words inside sentences. The skill measures the two separately. Current Claude
  in English opens *fewer* sentences with connectives than human scientists do, so the formulaic
  share is a guard (never rewarded), not a gated metric. French differs: see `french.md`.

### 4.3 Does AI hedge more or less?
- The Review describes "neutral, non-committal" phrasing. The survey finds fewer modal and
  epistemic markers.
- **Resolution:** AI hedging is generic ("it is important to note", "can potentially"), while
  *stance* (commitment, calibrated doubt, evaluation from a point of view) is missing. Remove
  formulaic hedges; keep or add hedges only where the evidence is uncertain.

### 4.4 Complex but uniform
- Higher syntactic complexity, lower sentence-length variance, lower readability.
- **Resolution:** AI prose is *uniformly* complex. Vary complexity with the content.

### 4.5 "researchers" and "others" as AI words
- The survey lists them as AI content words. In scientific corpora the same words mark human
  citation practice ("others have shown [12]").
- **Resolution:** the tell is the *unattributed generic agent* ("researchers have found",
  "studies show"). A named, cited agent is fine.

### 4.6 Numbers and symbols
- AI news uses more numbers and symbols (Muñoz-Ortiz et al.), yet specificity is a human trait,
  and human text has more of MAGE's rare, dataset-unique tokens.
- **Resolution:** this depends on genre. Never add numbers; keep every number the source has.

### 4.7 Emotion
- AI removes fear and anger in news and sanitises negative reviews (MAGE), but is *more* emotional
  in some reviews (Markowitz et al.).
- **Resolution:** AI emotion is *templated*. The target is emotion proportional to what the writer
  or source actually expresses, in their words.

### 4.8 There is no single "AI style"
- Fingerprints differ between models and drift across versions (§2.5).
- **Resolution:** the skill targets the *human* band for the register and length, measures the
  draft in front of it, and treats a metric as a tell when at least one calibrated tier
  separates from human text on it.

### 4.9 Function words: the published lists against today's text
- The lists in §2.1 come from studies of GPT-3.5-era text. Tested on current Claude, about half
  of their words point the other way in at least one register (`by` and `or` in all three).
- What replicates across all three registers and both tiers is simpler and much stronger: the
  handful of commonest grammatical words (`the`, `of`, `in`, `be`, `to`) is used a quarter to a
  third less often in papers and general prose and up to half less often in abstracts, and a
  small set of others (`how`, `across`, `rather`, `than`, `through`, `where`, `without`,
  `within`, `toward`) more often.
- **Resolution:** the research lists stay in the report for comparison but do not decide the
  gate. The gate uses word lists derived from the calibration corpora by a rule that requires
  replication in at least two registers, with held-out validation (`calibration.md`).

### 4.10 Verbose or dense?
- See §5. Both findings exist; they concern different models and tasks.

### 4.11 Sentence length
- The survey: "there is little consensus regarding whether LLMs produce longer sentences than
  humans or vice versa".
- **Resolution:** it depends on the model. In the calibration one tier is far above the human
  band and the other below it, so sentence length is scored on both sides of the human median.

---

## 5. Length, verbosity, padding and density

None of the ten papers measures padding as such. What they report about length and density:

| Finding | Setting | Source |
|---|---|---|
| "the human-produced answers are shorter and contain a larger vocabulary size", in English and more strongly in Chinese | question answering, GPT-3.5 | Guo et al. 2023, via the survey |
| GPT-4 "gives shorter answers and exhibits a larger vocabulary size and density" than GPT-3.5 | question answering | Rosenfeld & Lazebnik 2024, via the survey |
| AI essays are "very information-dense" | essays, GPT-3.5 | Sardinha 2024, via the survey |
| "AI-generated continuations are typically shorter but exhibit higher TTR and lexical density" | news continuations | MAGE |
| GPT-4-class output can "match or even surpass human writing in terms of perplexity, syntactic complexity, and information density" | review statement | Li et al. 2026 |
| More repeated words and expressions, more frequent word n-grams (n ≥ 3), repeated POS templates, "cohesive devices and formulaic syntactic constructions" | several genres and models | Simon et al.; André et al.; Merrill et al.; Shaib et al.; Wu, via the survey |

So the literature supports two different pictures. The long, repetitive, wordy answer belongs to
GPT-3.5-era chat models answering questions. For essays and for newer models the reports point the
other way: shorter, denser text.

What this skill measured on current Claude models [Calibrated]:

- The text is **denser** than human text (more content words per 100 words, longer words) and
  uses **fewer** of the classic wordy phrases ("in order to", "due to the fact that") than human
  scientists do. Whole-sentence restatements are no more frequent than in human text.
- What it adds instead is content-free *content*: comment clauses tacked on after a comma
  (", highlighting the need for…"), abstract framing nouns (role, challenge, framework, dynamics)
  and, in abstracts, lists of three. Framing nouns run at about twice the human rate in the
  Haiku tier (four times in its general prose) and at 1.5 to 3 times in French, in both tiers
  (`french.md`).
- When an AI text grows, the added words bring new vocabulary at the human rate or above, but
  **almost no new specifics**: growing from 300 to 450 words, human scientific text adds a
  median of 2.2 new numbers, names or acronyms per 100 added words (3.4 in French), the AI
  baselines 0 to 0.6. In general prose the figures are 5.4 against 0.6 to 2.3.

**Resolution used by the skill.** Padding is defined by what the words carry, not by how many
there are:

1. *Slack is not padding.* Articles, prepositions, auxiliaries and the occasional "in order to"
   are how people write; current models strip them. Restoring them is part of the fix (§4.9).
2. *Filler is padding*: any clause or sentence that can be deleted without the reader losing a
   fact, a step of reasoning, a condition, a limit or a consequence. The analyzer lists
   candidates; the deletion test decides.
3. *Length is met with substance.* When a draft is short of a requested length, the missing
   words must come from unused source material or from reasoning the source supports. The
   `growth` check compares the longer version with the shorter one: new content words and new
   specifics per 100 added words, against what human texts add when they grow.

---

## 6. Text length and the reliability of statistics

- **Short texts carry little signal.** Ghostbuster: unreliable at or below 100 tokens, levelling
  off from 500. The review lists methods built specifically for short texts and a framework that
  bounds false positives by calibrating on text length (multiscale conformal prediction, Zhu et
  al.). KGW's watermark test needs more tokens as the per-token signal weakens.
- **Raw ratios depend on length.** The raw type-token ratio falls as a text gets longer (Heaps'
  law). MAGE's most predictive feature area is partly this effect, because its AI texts were
  several times shorter than the human ones.
- **Datasets that control length** (Ghostbuster generated its AI texts to match the human
  documents' lengths) avoid the problem by design.

What the skill does about it: one word count for everything; vocabulary measures defined at fixed
sample sizes (exact formulas in `metrics.md`); human bands, thresholds and error rates computed
separately at each text length and interpolated between them; no gate under 150 words; documents
longer than the calibrated range scored in windows. The pass rates by length are in
`calibration.md`.

---

## 7. Languages other than English, French in particular

- Of the 44 surveyed studies, 40 (91%) analyse English. Eleven languages appear at all: English,
  Japanese, Chinese, Spanish, Italian, Arabic, Indonesian, Russian, Urdu, French, German.
- **French appears in one study** (Strübbe, Sidorenko & Lampe 2025: GPT-4o, o1, GPT-3.5, GPT-4;
  news and Wikipedia articles; English, French and German). The survey reports one result from
  it, more coordination ("enumeration") in AI text, without separating the languages.
- Cross-language evidence is thin but consistent where it exists: the answer-length and
  vocabulary-size differences of Guo et al. hold in English and Chinese; grammatical errors are
  rarer in English AI text but present in Japanese clinical text (Yanagita et al.).
- MAGE (English only) warns that "the applicability of the feature definitions, especially for
  lexical richness, depends on the particular language".

So there is no published French fingerprint to rely on. The French register bands in this skill
rest entirely on its own calibration: pre-2020 French human text (OpenEdition journals, French
articles in PubMed Central, HAL abstracts, The Conversation France, Wikinews, Wikipedia) against
French text from the same two model tiers. `french.md` gives the French patterns and how they
differ from the English ones.

---

## 8. What is not actionable at the writing level [Not actionable]

- **Watermarks** (KGW and its descendants, SynthID, watermarks for diffusion language models).
  These are keyed changes to sampling, invisible in the text; a writer cannot target them, and
  they need the key to detect. The watermark papers are used here only for what they show about
  token predictability, about test statistics and about meaning-preserving rewriting. This skill
  is a writing-quality tool, **not a watermark remover**, and contains no procedure for removing
  provenance signals.
- **Log-probability detectors** (DetectGPT, Fast-DetectGPT, Binoculars, white-box DNA-GPT) need model
  probabilities. The skill uses black-box proxies: rhythm, lexical, structural and stance
  statistics, plus an optional continuation probe (the black-box DNA-GPT idea).
- **Retrieval detection** matches meaning against a provider's generation logs. Rewriting
  preserves meaning, so this is outside the scope of style.

---

## 9. Methodological warnings the skill inherits

1. **Old and narrow model coverage.** GPT-3.5 appears in 25 of the 44 surveyed studies (57%), and
   only 15 (34%) compare models from more than one family. Section 2 shows how many of those
   findings reverse on current models. The skill therefore calibrates on current output and marks
   every list by provenance.
2. **English dominance** (§7).
3. **Genre effects:** abstraction, emotion and formality depend on genre. Bands are per register.
4. **Prompt sensitivity:** the survey notes that most studies "fail to address the issue of prompt
   sensitivity". No single threshold is absolute.
5. **Length** (§6).
6. **Non-native writers:** detectors misclassified short essays by non-native writers. The metrics
   here must never be used to accuse a person of using AI. They describe prose. They do not prove
   authorship. Forensic work on watermark detectors makes the same point from another side:
   verdicts flip under small threshold changes and produce false positives on human text
   (2607.16010).
7. **Concept drift:** the fingerprint changes with model versions. Re-run calibration when models
   change.
8. **Two tiers are not all models.** The calibration covers two tiers of one model family. A
   gate built without one tier still rejects most of that tier's texts (`calibration.md`,
   leave-one-tier-out), which is some evidence of generality, not proof.

---

## 10. One card per paper

| # | Paper | Type | What the skill takes from it |
|---|---|---|---|
| 1 | Li, Hu, Liu, Xiang, *AI-Generated Text Detection: A Comprehensive Review* (CMC 2026) | Survey | Decoding artifacts; neutral tone and hedging formulas, connectives, nominal rephrasing, argument templates, paragraph over-coherence, hybrid boundaries; length-calibrated thresholds; the caveat that GPT-4-class text can match human perplexity and density |
| 2 | Kirchenbauer et al., *A Watermark for Large Language Models* (KGW, ICML 2023) | Watermark | Spike entropy: forced vs free positions. The z-test logic used in compare mode. Power grows with length |
| 3 | *Self-Information Rewrite Attack* (SIRA, 2505.05190) | Attack | Self-information as the unit of predictability. Blind synonym substitution wrecks fluency (perplexity 252.85) |
| 4 | Tamim & Khan, *Watermark evidence and forensic readiness* (2607.16010) | Forensics | Detector verdicts are unstable under small threshold changes and produce false positives on human text. Metrics describe style; they are not proof |
| 5 | Ameen et al., *Chainwash* (2605.05503) | Attack on watermarks for diffusion language models | Meaning drifts as rewrite passes accumulate (0.92 → 0.86 over five). A "humanize" instruction is not a deeper rewrite than a plain paraphrase: avoid performative humanising |
| 6 | Verma, Tomlin, Klein, *Ghostbuster* (NAACL 2024) | Detector | Weak-model probabilities; predictability toward the end; length limits (≤ 100 tokens unreliable, ≥ 500 plateau); length-matched data; reordering and style prompts ineffective |
| 7 | Huynh & McNamara, *Linguistic consistency of LLM outputs* (Electronics 2026) | Linguistic profiling | Model fingerprints; regenerations do not vary; audience-insensitive "uniformity drift". **Full text not retrieved; numbers from the analysis file** |
| 8 | Alikhanov et al., *AI Generated Text Detection* (2601.03812) | Detector comparison | POS and readability features, perplexity and burstiness; detectors learn style, not topic |
| 9 | *Linguistic Characteristics of AI-Generated Text: A Survey* (2510.05136) | Survey of 44 studies | The consensus list (§2), function-word lists, model differences, length and density findings (§5), language coverage (§7), methodological warnings |
| 10 | Krishna et al., *Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense* (DIPPER, NeurIPS 2023) | Attack / defense | The 5-point meaning-preservation scale. Rewriting in context, several sentences at a time, scores better than sentence-by-sentence rewriting |
| 11 | *MAGE linguistic features* (2606.04177) | Feature study, 284 features | Lexical richness as the strongest feature area, and its length confound; lexical density; global hapax (rare words); emotion sanitisation, formal upgrading, invented names |

---

## 11. Corrections to the first version of this digest

The first version was written from the analysis files alone. Reading the papers changed these points:

1. **MAGE's "hapax legomena"** are counted across the whole dataset (rare, specific tokens), not
   within one text. The first version treated them as within-text once-only words.
2. **MAGE's raw TTR values** quoted in the first version (0.27–0.29 human, 0.56–0.69 AI) are those
   of three example pairs with very different lengths. The pooled distributions centre near 0.6
   and 0.8. Neither pair of numbers can be compared across lengths.
3. **Lexical diversity "lower in 12 of 14 studies"** could not be found in the survey's text. The
   survey says the finding is near-universal with two exceptions, and separately that GPT-4 text
   is more diverse than human essays (Herbold et al.).
4. **"57% of the studies used only GPT-3.5"** should read: GPT-3.5 appears in 57% of the studies;
   34% compare more than one model family.
5. **Function-word diversity** (lower in AI text, per two studies) was missing.
6. **Punctuation**: the survey lists which marks are rarer in AI text (commas, question marks,
   dashes, parentheses, semicolons, colons) and which are more frequent (single quotes, periods).
7. **Present participial clauses** (more frequent in AI text) were missing; they are now measured.
8. **Length and density findings** (§5) and **language coverage** (§7) were missing.
9. **DIPPER's 71% preference figures** come from automatic quality measures (a language model's
   perplexity and a ranking model), not from human raters as the first version said. Its human
   evaluation concerns meaning preservation (over 80% of paraphrases rated 4 or 5 of 5).
10. **"Humans detect AI text at chance (58–59%)"** was attributed to the DIPPER paper. The paper
   contains no such result; the claim is dropped.
11. Attack success rates from the watermark papers were quoted in one analysis file with values
   that do not match the paper's table. They are not used anywhere in this skill.
