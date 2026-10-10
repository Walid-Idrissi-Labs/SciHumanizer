# Worked examples: the loop on real drafts

Six runs made with the shipped scripts and calibration. Every number and report line below is
copied from those runs. Read the case closest to your task; case A is the full walk-through.

## Contents
- A. Rewriting an AI-drafted Introduction (English): the full loop, including an over-correction
- B. Lengthening without padding (English): substance, the padded alternative, and when to stop
- C. Writing a Discussion from a brief (English): derived numbers and general knowledge
- D. Rewriting an AI-drafted Introduction (French)
- E. A French tribune that failed by overshooting
- F. An English column: reporting a THIN verdict
- G. All runs at a glance
- H. What independent runs got wrong, and what changed

---

## A. Rewriting an AI-drafted Introduction (English)

### Phase 0: scope
- Request: "My AI assistant drafted this Introduction for my paper. It reads like AI: long
  sentences, generic, no specifics. Please humanize it. Keep every claim. Here is my abstract
  for the facts."
- Mode REWRITE, register `scientific`, reader: reviewers in environmental epidemiology.
- Protected terms: land-surface temperature, urban heat island, intra-urban, emergency
  admissions, distributed-lag non-linear models.
- Length: the user gave no target. An Introduction has to fit its slot, so the draft's length
  (694 words) is taken as the target: `--target-words 700`, allowed 630–770.
- Files: `source.md` (the draft), `user_facts.md` (the abstract).

### Phase 1: baseline
`sci_metrics.py analyze source.md --register scientific --sentences` (excerpt):
```
words=694  sentences=15  paragraphs=6
## Style gate (en.scientific, bands for 694-word texts)  composite=1.574  threshold=0.667  ->  FAIL
at this length the gate passes 84% of held-out human texts and 0% of unedited AI texts
closest AI profile: Sonnet tier. Dimensions are listed by how much of the composite they explain
- [FAIL] marker words: z=2.14 (human p75 0.63, p90 0.91), 22% of the composite
    [FAIL] function words current models over-use, per 1k = 38.9  (human p10 / p50 / p90: 5.35 / 12.1 / 22.8; AI: 35.7 Sonnet tier, 30.7 Haiku tier; AI higher)
    [FAIL] plain workhorse words people use, per 1k = 4.32  (human p10 / p50 / p90: 6.61 / 14.8 / 27; ...; AI lower)
- [FAIL] word variety: z=2.37 ..., 15% of the composite
- [FAIL] punctuation: z=1.71 ..., 12% of the composite
    [FAIL] parentheses per 1k = 0  (human p10 / p50 / p90: 0.838 / 6.86 / 23.9; AI: 0 Sonnet tier, 0 Haiku tier; AI lower)
- [FAIL] sentence length: z=2.90 ..., 11% of the composite
    [FAIL] mean sentence length (words) = 46.3  (human p10 / p50 / p90: 21.3 / 26.6 / 33.9; AI: 40.5 Sonnet tier, 22.3 Haiku tier; AI off on both sides)
- [FAIL] modifiers: z=2.01 ..., 9%      - [FAIL] specificity: z=1.03 ..., 7%
- [FAIL] grammatical glue: z=1.56 ..., 7% of the composite
    [FAIL] glue words per 100 tokens (the, of, be, to, in) = 12.1  (human p10 / p50 / p90: 14.3 / 17.9 / 22.3; AI: 13.7 Sonnet tier, 11.6 Haiku tier; AI lower)

## Where to look
- Long / comma-chained sentences: s14 (74w, 8 commas), s15 (72w, 7 commas), s9 (64w, 6 commas) ...
- Compressed sentences (few glue words: the/of/be/to/in): s5 (1 in 21 tokens), s7 (3 in 54 tokens) ...
- Specifics: 2 proper nouns, 0 acronyms, 5 numbers | punctuation: 0 parentheses, 0 semicolons, 0 colons
- Words current models over-use (calibrated list): or(5), across(5), than(4), how(4), ... examine(3), kind(3), represent(2) ...
- Padding candidates, comment clauses after a comma: s12 ', capturing ...'
- Nominalization clusters (>=3 per sentence): s2 capacity/conditions/medications/ability/populations; ...
- Opening sentence uses a stock opener.
```
Reading it:
- The draft leans toward the long-sentence profile: 15 sentences of 46 words on average, three
  commas each, no parentheses, few glue words. The job is to cut sentences at their joints,
  restore ordinary grammar, and bring in the abstract's specifics.
- **Provenance.** `fact_ledger.py user_facts.md source.md --write` reports no added number: the
  draft's figures (twelve cities, eleven years, 65 and older, one kilometer) are in the
  abstract. Two background claims have no source and no digits, so only reading finds them:
  temperatures differing "by several degrees Celsius" between neighborhoods, "only a few
  kilometers away". They are ordinary background for the field. They stay, and the
  verification block asks the user for a citation.

### Phase 2: one paragraph
> Draft (3 sentences: 25, 45, 55 words): "Advances in satellite-derived land-surface temperature estimation now make it possible to examine this question with a level of spatial detail that was not previously feasible. Rather than relying on one or a handful of ground-based weather stations, satellite platforms can provide land-surface temperature estimates at resolutions as fine as one kilometer across an entire urban area, capturing the kind of neighborhood-level thermal variation that citywide station-based measurements necessarily average away. Pairing this kind of high-resolution temperature data with large, individual-level health outcome datasets offers an opportunity to examine not just whether extreme heat overall is associated with adverse health outcomes, a relationship already well established in the literature, but specifically whether the location of a person's exposure within the urban heat landscape modifies their risk."
>
> Final (4 sentences): "Satellite-derived estimates of land-surface temperature (LST) now make it possible to examine this question in spatial detail that was not previously feasible. A satellite does not depend on one or a handful of ground-based weather stations. It provides LST at a resolution as fine as 1 km over an entire urban area, and so records the variation between neighborhoods that is averaged away in station-based measurements. When these data are linked to large datasets of individual health records, the analysis can go beyond the general association between extreme heat and adverse health outcomes, which is already well established in the literature: it can test whether the risk to a person depends on the part of the city in which that person is exposed."

What changed: the comment clause (", capturing the kind of...") became a finite clause; "rather
than", "across", "not just... but specifically" and "the urban heat landscape" are gone; the
abbreviation sits in parentheses; "1 km" comes from the abstract. The field's terms stayed.

### Phases 3 to 5: four rounds
| Draft | Words | Composite (threshold) | Over-correction (limit) | Sentence length | Glue per 100 | Word length | What happened |
|---|---|---|---|---|---|---|---|
| source | 694 | 1.574 (0.667) FAIL | 0.36 | 46.3 | 12.1 | 6.07 | |
| v1 | 872 | 0.239 (0.674) | 1.15 (2.02): word length 3.1, glue 1.9 | 32.3 | 25.5 | 4.71 | every phrase unpacked; length OVER (allowed 630–770) |
| v2 | 730 | 0.312 | 0.98: word length 2.7 | 29.2 | 23.6 | 4.82 | unpacking that added nothing was cut; ON TARGET |
| v3 | 728 | 0.331 | 0.94: word length 2.6 | 29.1 | 23.4 | 4.85 | two terms restored (thermoregulation; cardiovascular, respiratory and renal); still too plain |
| v4 | 664 | 0.548 (0.669) | 0.45 | 26.6 | 18.4 | 5.37 | field terms restored |
| v5 | 664 | 0.539 | 0.43 | 26.6 | 18.3 | 5.37 | one term per concept ("variation", "entire") |

Human medians at this length: sentence length 26.6, glue 17.9, word length 5.67.

- **v1 passed the gate with the lowest composite of all and was the worst text.** It was 100
  words over the limit, its glue rate (25.5) was above the human 90th percentile (22.3), and it
  read like a simplified summary: "As the body ages it becomes less able to regulate its own
  temperature", "chronic diseases of the heart, the lungs and the kidneys", "a pressing need
  ... to establish the way in which exposure to heat leads to acute illness". The
  over-correction line and the length check said so.
  `growth draft_v5.md draft_v1.md` gives THIN with "padding went up: wordy phrases per 1k
  0 -> 3.44": the extra 208 words were unpacking, not content.
- **v3 still carried "word length 2.6" on the far side.** The cause was the rewrite, not the
  subject: "the capacity for thermoregulation declines" for "thermoregulatory capacity
  declines", "differences in temperature inside the city" for "intra-urban variation in
  temperature". Round 4 put the field's terms back. The composite rose from 0.33 to 0.55,
  still well under 0.67, and every far-side dimension fell below 1.5.
- The composite is a ceiling. The better text is v5, not v1.

### Phase 4: semantic gate
`fact_ledger.py source.md final.md --facts user_facts.md`:
```
verdict: OK (no hard-fact changes)
- names/acronyms added (review: invented?): LST
- spelled-out numbers added (review: counting word, or an invented fact?): 2 ...Two trends add to the urgenc...
- certainty: hedges 4.32->4.52 per1k; boosters 2.88->4.52 per1k; negations 5.76->4.52 per1k
  WARNING: Boosters increased: check for overclaiming (e.g. 'shows' -> 'proves', 'may' -> 'will').
  WARNING: Negation count changed (4 -> 3): verify that no negation was lost or added.
```
Each item was checked by reading:
- LST is defined in the text; "Two trends" is a counting word.
- Boosters: the three hits are "establish" (the aim, "necessary to establish whether"), "in
  fact" (for the draft's "actually experienced") and "strongly" (kept). No claim was strengthened.
- Negations: "mortality data alone cannot provide" became "more completely ... than mortality
  data alone can"; "not just whether ... but" became "can go beyond"; "rather than relying on"
  became "does not depend on". No finding was flipped. All three "may" of the draft survive.
- Paragraph equivalence: all six paragraphs at 4/5 or 5/5.
- Still on the AI side: content-word variety (an introduction covers a lot of ground in few
  words) and specificity (the abstract names no people, places or instruments). Neither can
  move without inventing material, and the gate passes with them.

### Phase 6: the verification block
```
Verification (scientific register, English)
- Gate: composite 1.57 -> 0.54 (threshold 0.67 at this length), PASS; classic violations 0
- Biggest shifts: sentence length 46 -> 27 words; glue words 12.1 -> 18.3 per 100; over-used
  function words 39 -> 21 per 1k; -ly adverbs 3.5% -> 2.0%; parentheses 0 -> 2
- Still on the AI side: content-word variety (an introduction covers much ground); specificity
  (the facts name no people, places or instruments)
- Far side: none at 1.5 or more (round 3 was at 2.6 on word length; round 4 restored field terms)
- Length: 664 words against a target of 700 (allowed 630-770), ON TARGET
- Fact ledger (--facts abstract): OK; added acronym LST (defined in the text); negations 4 -> 3,
  boosters 2 -> 3, checked: rephrasings, no finding flipped, no claim strengthened
- From the draft, without a source: "several degrees Celsius", "a few kilometers" (cite or cut)
- Paragraph equivalence: all >= 4/5. Unresolved: none
```

---

## B. Lengthening without padding (English)

Request: "This summary is for our growers' association report; they want about 300 words. Here
are my trial notes. Please lengthen it, but no filler." The summary has 89 words and uses four
of the notes' facts.

### Step 0: count, and compare with the material
`sci_metrics.py analyze summary.md --register scientific --target-words 300 --source notes.md`:
```
## Length: 89 words  (allowed 270-330)  ->  UNDER
- 181 words short. Add substance, never filler: ...
- In the source, not in the draft: numbers 0.8, 110, 2011, 3, 4, 6, 107, 38, 30, 96, 0.41, 12, 23.1, 24, 610, 405, 5, 20 ... | names and terms Brix, June, September, July ...
- The source has 151 words, this text 89. Not anchored in the source: 0% of the words ...
```
The notes hold 151 words. A 300-word summary is about twice that: within what notes can carry.

### Steps 1 to 3: what was added, by kind
| Kind of substance | Added |
|---|---|
| Unused facts | plot size, rootstock and planting year; the two schedules in detail; season length and rainfall against the 30-year mean; pump energy; berry sugar; p-value and sample; the two sensor failures; the labour for readings |
| Derived quantities | "630 m3/ha or 34% less" (from 1,840 and 1,210) |
| What follows from the facts | "The method has a cost": what a grower needs in order to adopt it (spare instruments, someone to read them every day) |
| Limits and their consequence | one season, one site, sandy-loam soil, a dry year; so repeat in a wetter year and on a heavier soil before recommending it |
| Missing grammar | none added: the summary was not compressed |

Result: 285 words, ON TARGET, composite 0.288 (threshold 0.653).

`sci_metrics.py growth summary.md draft_v2.md --register scientific --source notes.md`:
```
# Growth check: 89 -> 285 words (+196 analysed words)  ->  SUBSTANCE
- new content words per 100 added words: 30.1  (human texts growing from this length: p10 25.0, p25 30.0, median 36.1)
- new numbers, names and acronyms per 100 added words: 15.3  (human: p25 0.0, median 1.9)
- added sentences with no number or name and little vocabulary from the source or the old version (9% of the added words). ...
    s12 (16w, 38% anchored): A grower who adopts the method needs spare instruments and someone to read them every day.
```
The one listed sentence is a consequence of two facts in the notes (the failures, the daily
readings). It stays, and the block says where it comes from.

`fact_ledger.py summary.md draft_v2.md --facts notes.md`:
```
verdict: OK (no hard-fact changes)
- numbers not in the source that are arithmetic on source numbers of the same paragraph (confirm each ...):
    630 = 1840 - 1210
    34% = 100 x (1840 - 1210) / 1840 or 100 x 630 / 1840
```
Both derived numbers were confirmed and shown in the verification block. The report also listed
"word length 3.8" on the far side: a summary dense in units (ha, mm, kPa, t, kWh) has short
words. That is the subject, not the rewrite; it was reported and left.

### The padded alternative
The same 285 words stretched to 456 with the sentences a model reaches for ("Water management
is an increasingly important issue...", "It is worth noting that...", ", underscoring the wider
benefits of the method", "Overall, these results demonstrate the significant potential...").
The length check says ON TARGET for a 450-word request. The other checks
(`growth draft_v2.md padded.md --register scientific --source notes.md`, then `analyze`):
```
# Growth check: 285 -> 456 words (+171 analysed words)  ->  PADDING
- new content words per 100 added words: 43.3  (human ... median 30.6)
- new numbers, names and acronyms per 100 added words: 0.0  (human: p25 1.2, median 2.3)
- padding went up: announcements per 1k 0 -> 4.386
- padding went up: comment clauses per 1k 0 -> 6.579
- padding went up: abstract framing nouns per 1k 3.509 -> 19.737
- padding went up: significance-echo sentences per 1k 0 -> 4.386
- padding went up: stock phrases per 1k 0 -> 10.965
- added sentences with no number or name and little vocabulary from the source or the old version (71% of the added words). ...
    s18 (20w, 0% anchored): These practical considerations highlight the importance of careful planning and adequate training, ...
    s6 (21w, 8% anchored): This approach reflects a broader shift toward data-driven decision-making in viticulture, ...
    s8 (24w, 10% anchored): It is worth noting that such conditions are particularly relevant, ...

## Style gate ... composite=0.477  threshold=0.66  ->  FAIL
classic tells beyond the human range (max allowed 1): padding.participial_clause_per1k, padding.metadiscourse_per1k, stock.stock_per1k, stock.significance_echo_per1k, document.paragraph_wrapup_share
```
Three things to take from it:
- Filler brings *more* new content words than real material does (43 per 100 against 30),
  because abstract vocabulary is cheap. The count of new words proves nothing; the missing
  specifics, the padding rates and the unanchored sentences do.
- The composite alone would have passed this text. The classic guards exist for this.
- The fact ledger reports OK: filler invents no numbers. It cannot see padding.

### When the notes run out
Had the association asked for 700 words, the notes would not carry it: at 285 words every fact
in them is used, and the report says so ("The draft already uses the source's numbers ...
STOP: deliver the text at 285 words and tell the user what material would be needed for
more"). The right delivery is the 285-word text with this note, not 700 words:

> "This is 285 words. Your notes support no more without filler. To reach 700 I would need
> material such as: results from another season or site, the cost of the tensiometers and of
> the water, how the fixed schedule was chosen, what growers in the association do now."

---

## C. Writing a Discussion from a brief (English)

Brief: findings of a study on a low-cost acoustic sensor network for bats along a highway (38
sensors at US$45, 60 km, 14 months, 212,000 passes, activity 61% lower within 50 m of lit
sections, 89% agreement in a 2,000-call validation sample, two Myotis species confused in 23%
of cases, 9 sensors failed in winter). "About 700 words, plain paragraphs, no citations."

- First draft: 560 words, UNDER (allowed 630–770), composite 0.667 against 0.669. Every number
  of the brief was already used, so step 1 of the length procedure had nothing to add.
- Step 2, the reader's next questions, supplied the rest: what the hardware cost in total and
  how far apart the sensors were; whether lighting or something that comes with lighting
  explains the 61%; what one annual cycle can and cannot show; how many calls the 89% leaves
  misclassified and what that means for each kind of question; what the winter failures cost
  the data set.
- Final: 634 words, ON TARGET, composite 0.424 (threshold 0.670), after four drafts. As in case
  A, the third draft was too plain (glue 23.9 per 100, word length 4.66) and the fourth restored
  the register. Word length stays at 2.8 on the far side: the subject's own words are short
  (bat, road, lit, call), which the verification block says.

`fact_ledger.py brief.md final.md --write`:
```
verdict: OK (no hard-fact changes)
- numbers not in the source that are arithmetic on source numbers of the same paragraph (confirm each ...):
    1710 = 38 x 45            ...38 sensors costing US$45 each, or US$1,710 for the acoustic hardware...
    1.6 = 60 / 38             ...an average spacing of about 1.6 km between sensors...
    220 = 2000 x (100 - 89%)  ...which leaves about 220 calls classified differently...
    24% = 100 x 9 / 38        ...Nine of the 38 sensors (24%) failed in winter...
- spelled-out numbers added (review ...): 3 ...recorded by only three quarters of the network...
```
All four are the intended calculations ("three quarters" is 29 of 38 sensors). In the
verification block:
```
- Derived from your numbers: US$1,710 = 38 x US$45; 1.6 km = 60 km / 38; about 220 calls = 11% of
  2,000; 24% = 9 of 38
- General knowledge, no citation (confirm or cut): many bat species avoid artificial light; lit
  road sections tend to lie near junctions and settlements; bat activity is lowest in winter in
  temperate regions
- Not in your brief, so not in the text: comparison with other monitoring methods, species list,
  site description
```

---

## D. Rewriting an AI-drafted Introduction (French)

Same study as case A, in French: a 698-word draft and a French abstract.

Baseline (`--register scientific`, language detected):
```
## Style gate (fr.scientific, bands for 698-word texts)  composite=1.134  threshold=0.646  ->  FAIL
classic tells beyond the human range (max allowed 1): padding.participial_clause_per1k
- [FAIL] grammatical glue: z=2.10 ..., 20% of the composite
    [FAIL] glue words per 100 tokens (être, en, avoir, dans) = 2.59  (human p10 / p50 / p90: 4.68 / 6.47 / 8.82; AI: 4.06 Sonnet tier, 3.5 Haiku tier; AI lower)
    [FAIL] auxiliaries: être / avoir (% of tokens) = 0.82  (human p10 / p50 / p90: 2.1 / 3.65 / 5.47; ...)
- [FAIL] specificity: z=1.48 ..., 12%     - [FAIL] punctuation: z=1.62 ..., 12%
- [FAIL] marker words: z=1.15 ..., 12%    - [FAIL] sentence length: z=1.29 ..., 10%
## Where to look
- Long / comma-chained sentences: s6 (87w, 5 commas), s15 (79w, 4 commas), s2 (63w, 3 commas) ...
- Compressed sentences (few glue words: être/en/avoir/dans): s3 (0 in 43 tokens), s9 (0 in 56 tokens) ...
- Words current models over-use (calibrated list): ce(12), plutôt(2), demeurer(1), constituer(1), enjeu(1), offrir(1) ...
- Padding candidates, comment clauses after a comma: s2 ', négligeant ...', s6 ', traitant ...', s10 ', articulant ...', s14 ', distinguant ...'
- Repeated sentence frames: 'elle permet' x3
```
What the rewrite did (examples in `french.md`, FR-1 to FR-8): 15 sentences became 25; *être*
and *avoir* came back (auxiliaries 0.82% → 4.76%, glue 2.59 → 6.94 per 100, human median 6.47:
19 glue words became 49, where the report gives about 46 for a human text of this length);
the authors appear ("nous avons relié", "nous avons vérifié"); the four comment clauses became
sentences or disappeared; the abstract's figures entered the text.

Three statements of the draft are not covered by the abstract. None carries a digit, so the
ledger did not see them: they were found by reading the draft against the abstract, and
handled by kind (Phase 1, point 4).
- A detail about the study itself: the twelve cities "présentant des climats et des
  morphologies urbaines contrastés". Removed, and put to the user as a question.
- Two background claims: the reference station "généralement installée en périphérie des
  villes" and temperature estimates "désormais produites de manière routinière pour de
  nombreuses villes européennes". The user asked to keep every claim, so both stay, at the
  draft's strength, and the block lists them as unverified.

Result after three drafts: 687 words (target 700, ON TARGET), composite 0.269 (threshold
0.646), no far-side dimension at 1.5 or more, ledger OK.
```
Vérification (registre scientifique, français)
- Grille : composite 1,13 -> 0,27 (seuil 0,65 à cette longueur), PASS ; aucun signal classique
- Principaux écarts corrigés : longueur des phrases 46 -> 27 mots ; être/avoir/en/dans 2,6 -> 6,9
  pour 100 ; participiales après virgule 4 -> 0 ; parenthèses 0 -> 3
- Encore du côté IA : spécificité (le résumé ne nomme ni lieux, ni personnes, ni instruments)
- Longueur : 687 mots pour une cible de 700 (630-770), ON TARGET
- Registre des faits (--facts résumé) : OK ; chiffres ajoutés issus du résumé : 1 km, 1,9 million,
  65 ans, 12 villes, 2008-2018
- Retiré car absent du résumé (à rétablir si c'est exact) : villes « aux climats et aux
  morphologies urbaines contrastés »
- Repris du brouillon, non vérifié (à citer ou à supprimer) : station de référence « en
  périphérie des villes » ; estimations « produites de façon routinière pour de nombreuses
  villes européennes » ; écarts de « plusieurs degrés » à « quelques kilomètres »
- Équivalence des paragraphes : tous >= 4/5
```

---

## E. A French tribune that failed by overshooting

Brief: « Rédige une tribune (environ 600 mots) défendant l'idée que les bibliothèques
municipales devraient rester ouvertes jusqu'à minuit. »

First draft: 596 words in 34 sentences, written "against" the long-sentence habit.
```
## Style gate (fr.general, bands for 596-word texts)  composite=0.477  threshold=0.678  ->  FAIL
closest AI profile: Haiku tier.
over-correction 1.504 (limit 1.37) -> TOO FAR: the text now overshoots human writing; beyond the human median on the far side: function words 3.2, word length 2.7, marker words 1.8, grammatical glue 1.7, modifiers 1.6
- [FAIL] sentence length: z=1.81 ..., 47% of the composite
    [FAIL] share of short sentences (<=10 words) = 0.294  (human p10 / p50 / p90: 0 / 0.0798 / 0.197; AI: 0 Sonnet tier, 0.306 Haiku tier; AI off on both sides)
    [OVER] everyday function words people use more (il, nous, on, très, alors), per 1k = 53.7  (human p10 / p50 / p90: 3.36 / 16.6 / 30.7; ...)
```
The composite was under the threshold and the text still failed. Three sentences in ten had
ten words or fewer, which is the smaller tier's own rhythm (the report names it as the closest
profile), and the pronoun subjects *il / elle* and *on* ran at three times the human rate.
Avoiding one model's habits had produced another's.

Second draft: sentences that belonged to one thought were joined (34 → 26 sentences, 17.5 →
21.9 words on average), which removed half of the pronoun subjects (*il / elle* 24 → 12, *on*
8 → 5); others gave way to nouns ("une municipalité", "la bibliothèque"). Result: 569 words, composite 0.369 (threshold 0.676),
over-correction 1.06 (limit 1.37). Two far-side dimensions remain just above 2 (function
words, word length): a first-person column in everyday words. They were reported as genre.

The ledger (`--write`) listed the number words for review: closing "à dix-huit ou dix-neuf
heures", "cinq heures d'ouverture de plus" (19 h to midnight), "six mois". The first is general
knowledge and was flagged for the user to check against their town; the others are the text's
own arithmetic and its proposal.

---

## F. An English column: reporting a THIN verdict

Brief: "Write an opinion column (about 600 words) arguing that public libraries should stay
open until midnight." No facts supplied.

- First draft 502 words (UNDER, allowed 540–660), composite 0.529. With no source material,
  lengthening had to come from the argument: a second and third objection with their answers,
  and a testable proposal (a one-year pilot in two or three branches, counting visitors by the
  hour).
- Final: 601 words, composite 0.374 (threshold 0.677).
- `growth draft_v1.md final.md --register general`: **THIN**, 23.2 new content words per 100
  added (human p25 26.0) and 1.0 new specific (human median 4.7). Each added sentence then went
  through the deletion test: sentences that only announced or repeated were shortened or
  folded into their neighbours (631 → 601 words), and what remains carries a step of the
  argument. The verdict stayed THIN, and the verification block says why: "No facts were
  supplied, so the added length is argument, not data. Give me your city's opening hours,
  visitor counts or budget and I will replace the general statements."
- The unedited model answers to the same brief score 1.11 and 1.57.

---

## G. All runs at a glance

| Run | Mode | Words | Unedited AI text, same request | Final composite | Threshold | Over-correction (limit) | Drafts | Ledger |
|---|---|---|---|---|---|---|---|---|
| A. Introduction, EN | rewrite | 694 → 664 | 1.57 | 0.54 | 0.67 | 0.43 (2.02) | 5 | OK |
| B. Summary, EN | lengthen to 300 | 89 → 285 | | 0.29 | 0.65 | 1.23 (1.88) | 1 | OK, 2 derived |
| B. Padded variant | (negative example) | 456 | | 0.48, FAIL on 5 classic tells | 0.66 | 0.70 (1.99) | | OK |
| C. Discussion, EN | write, 700 | 634 | 1.48 / 1.82 | 0.42 | 0.67 | 0.90 (2.02) | 4 | OK, 4 derived |
| D. Introduction, FR | rewrite | 698 → 687 | 1.13 | 0.27 | 0.65 | 0.48 (1.49) | 3 | OK |
| E. Tribune, FR | write, 600 | 569 | 0.84 / 0.98 | 0.37 | 0.68 | 1.06 (1.37) | 2 | OK |
| F. Column, EN | write, 600 | 601 | 1.11 / 1.57 | 0.37 | 0.68 | 0.94 (1.37) | 3 | OK |

"Unedited AI text" gives the composites of the two calibrated tiers' own answers to the same
request (one value where only one draft existed). The source and the final text of each case are
in the repository under `examples/`.

What the runs have in common:
- The first draft of a rewrite tends to overshoot toward plain prose. The over-correction line
  and the far-side list caught it every time; in A and C, two drafts went to pulling back.
- The gate never needed a waiver, but specificity stayed on the AI side wherever the user's
  material named no people, places or instruments. It was reported each time, never patched
  with invented detail.
- Length was reached with source facts, derived quantities and reasoning. Where there was no
  source (F), the growth check said THIN and the block said so.

---

## H. What independent runs got wrong, and what changed

The runs above were made by a larger model, in a session that already knew why each rule
exists. To test the instructions on a reader that knew nothing else, a smaller model (the Haiku tier) was given only the skill folder
and two requests, three times over, with the instructions revised between rounds. One run per
case and round, so the pattern matters more than any single number. Every figure below was
re-measured after the run; the runs' own reports were not taken on trust.

| Round | Length the notes cannot carry (case B's notes, "can you get it to 700?") | French rewrite (case D's draft) |
|---|---|---|
| 1 | 682 words, reported ON TARGET; gate FAIL (0.81); 29% of the added words unanchored. Growth check run against its own padded draft, so it said SUBSTANCE | 1.13 → 0.652 against a threshold of 0.651: FAIL, presented to the user as "quasi-passant"; a far-side dimension at 1.6 reported as none |
| 2 | 632 words, the lower edge of the allowed range; gate PASS (0.49); no outside facts, but written toward the count: 28% unanchored; growth check skipped | 1.13 → 0.714: FAIL, reported as FAIL; glue words still at 2.9 per 100 |
| 3 | 287 words; gate PASS (0.42); 8% unanchored; growth SUBSTANCE; the reply says the notes are used up and lists what 700 words would need | 1.13 → 0.462: PASS; glue 2.6 → 5.3 per 100; verdicts copied as printed |

What round 1 looked like in the text: "In a region where electricity costs are rising, this
difference matters considerably." "Clay soils might show different results because they drain
more slowly." "Higher sugar at harvest is often associated with improved wine quality, and this
result is noteworthy." None of it is in the notes. The fact ledger said OK, because none of it
contains a number.

What changed between rounds, in the order it was added:
1. The growth check quotes the added sentences that carry no number or name and little of the
   source's vocabulary, and counts their share. Its baseline is the text before lengthening
   began, never a draft that already holds the additions.
2. Verdicts are copied as printed, a FAIL by any margin is a FAIL, and every ledger WARNING and
   far-side dimension is answered in the block.
3. The material is counted before writing, and the draft is written at the length the
   material comes to, not toward the number. `analyze --source` reports the unanchored share
   on every run and says CHECK THE LENGTH when a count was reached with it.
4. The report gives the number of glue words next to the number a human text of that length
   has, which turned "restore the grammar" into something countable.

Still wrong in round 3, and addressed by rules that were added afterwards and not re-tested:
background claims of the draft were kept without being listed as unverified (Phase 1, point 4);
results from the abstract were moved into the Introduction to raise specificity (Scientific
writing notes); one small unsupported clause was added ("without affecting the trial").

