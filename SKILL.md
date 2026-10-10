---
name: scihumanizer
description: >-
  Research-calibrated humanizer for English and French prose: scientific and academic writing
  first, also essays, articles and reports. Writes or rewrites text without the measurable
  fingerprints of LLM output: compressed phrasing with too few articles and auxiliaries,
  inflated vocabulary, sentences longer or more uniform than human ones, flat punctuation, few
  names or numbers, comment clauses, framing nouns, missing stance, stock phrases. Runs a
  verification loop: a Python analyzer scores drafts against human bands per language, register
  and length; a fact ledger proves no number, citation, negation or hedge changed; length
  targets are met with substance, never padding, and a growth check measures it. Use when asked
  to humanize text, make it sound less like AI, remove AI tells, polish a paper section or
  abstract, hit a word count without filler, audit text for AI patterns, or match the user's
  voice; also in French (« humaniser ce texte », « ça fait trop IA », « rends ce texte plus
  naturel »).
---

# SciHumanizer

Language models write by picking a high-probability continuation at every free choice, so their
prose carries a statistical fingerprint. It shows in rhythm, vocabulary, syntax, punctuation,
stance and document shape, and it survives surface style instructions (a detector still reached
99.5 F1 on text generated with prompts such as "write in the style of a high-school student").
This skill removes the fingerprint by changing the choices themselves, then **measures** the
result against human writing of the same language, register and length instead of trusting its
own impression.

Two rules carry most of the work.

**Spend surprise where the choice is free, never where it is forced.** Terminology, names,
numbers and established collocations are forced choices: keep them exactly. Openers,
transitions, framing verbs, modifiers, examples, the order of information and the last sentence
of each paragraph are free choices. Those are where AI text takes the most probable option and
where human writers make specific, situated ones. Surprise means *precision*: the exact name,
the actual number, the real caveat, the plain word the field uses. Random rare words are not
surprise (blind synonym substitution wrecks both fluency and meaning).

**Human prose is looser than model prose, and looser is not padded.** Measured against human
text of the same kind, current models compress. In English papers and articles they use a
quarter to a third fewer of *the, of, be, to, in* (up to half in abstracts); in French papers,
barely more than half as many of *être, avoir, en, dans*. In both languages they pack more
content words into each sentence and choose longer words. What they add instead is content-free
*content*: abstract framing nouns, comment clauses tacked on after a comma, decorative adverbs.
So the two fixes go together: give sentences back their ordinary grammar, and delete what
carries nothing.

Evidence behind every rule: `references/research-digest.md` (the papers, with numbers and with
what did not survive a check against them). Formulas: `references/metrics.md`. How the bands were
measured, and how well the gate separates: `references/calibration.md`. French patterns:
`references/french.md`. Full runs on real drafts: `references/worked-example.md`.

## Ground rules

These outrank every metric in this file.

1. **Meaning is fixed.** Every claim, number, unit, citation, name, negation, hedge and scope
   statement in the source survives with the same strength. A rewrite that reads beautifully
   but turns "may reduce" into "reduces" or loses a "not" has failed. `fact_ledger.py` checks this
   mechanically. You check the rest by reading. One exception: when the source is itself an AI
   draft and the user gives the facts separately, the user's facts are the ground truth, and the
   draft's unsupported specifics are not protected (see Phase 1).
2. **Invent nothing.** Specificity is the strongest human signal, and it is also where
   fabrication creeps in. Never add facts, names, numbers, dates, sources, quotations, examples,
   anecdotes or first-person experiences that the source or user did not supply. If a sentence
   needs a detail you do not have, ask for it, write around it, or cut the sentence. Two things
   are allowed: evaluation the source supports ("surprisingly", "the weaker result"), and
   arithmetic on the source's own numbers (38 sensors at US$45 is US$1,710), shown in the
   verification block. Fiction and explicitly invented samples are exempt, but label a
   hypothetical example as hypothetical.
3. **Length is met with substance.** A requested length is a target for content, not a quota of
   words. Reach it with material the source supports. If the source cannot fill it, deliver the
   shorter text and say what is missing. Filler is the habit this skill removes.
4. **Metrics serve the reader.** If moving a number would make the text less clear, less
   accurate or less appropriate for the register, leave the number where it is and say so in
   the report. Never game a metric (see "Performative humanizing").
5. **Register and voice outrank defaults.** A writing sample from the user beats every default
   target here. Match it with `compare`. Scientific conventions (terminology consistency, hedging
   tied to evidence, passive voice in Methods, exact reporting) are features, not tells.
6. **This is a writing-quality tool.** Its statistics describe prose. They are not evidence about
   who wrote a text. Do not use them to accuse anyone, and do not promise that output will pass
   any particular AI detector. The skill does not target or remove provenance watermarks, which
   are keyed and invisible at the writing level (research-digest §8).

## Quick start

All scripts are standard-library Python 3.8+. `$S` is this skill's directory.

```bash
python3 $S/scripts/sci_metrics.py analyze draft.md --register scientific --sentences   # report + gate
python3 $S/scripts/sci_metrics.py analyze draft.md --register general --target-words 600 --source brief.md
python3 $S/scripts/sci_metrics.py count draft.md --target-words 600                    # the word count
python3 $S/scripts/sci_metrics.py growth before.md after.md --register scientific --source notes.md  # did longer mean more?
python3 $S/scripts/sci_metrics.py compare draft.md --ref writer_sample.md              # voice match
python3 $S/scripts/fact_ledger.py source.md draft.md --facts notes.md --protect "t1,t2" # hard-fact check
python3 $S/scripts/dna_probe.py split draft.md                                          # optional probe
```

- **Registers:** `scientific` (papers, theses, technical and trial reports, results summaries:
  introduction and discussion style), `abstract` (abstracts of papers, up to about 300 words),
  `general` (essays, articles, op-eds, reviews, guides, encyclopedic and news writing). Choose
  once, in Phase 0, and keep it for every check of the same text.
- **Languages:** English and French, detected from the text (`--lang en|fr` forces one). For
  French, read `references/french.md` before drafting: the loop is the same, the habits differ.
- Write drafts to files (`draft_v1.md`, `draft_v2.md`) so the scripts can read them. Keep each
  version; `growth` and the verification block need the earlier one.
- Exit code 1 means the style gate, the length check, the growth check or the fact ledger
  failed. Read the report; do not loop on the exit code alone.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| **REWRITE** | "humanize / de-AI / make this sound natural", a pasted or linked draft | Final text + short verification block |
| **WRITE** | A writing request where human-quality prose matters | Final text + short verification block |
| **AUDIT** | "does this sound like AI?", "check my text" | Findings by dimension with sentence numbers, top fixes; no rewrite unless asked |
| **MATCH** | Continue or insert into the user's own document, or "write like me" | Text that passes `compare` against the surrounding or sample text |

All four modes use the same loop. AUDIT runs Phase 0 and Phase 1 on the user's text, applies the
Phase 4 checklist to it, and reports without rewriting.

**Light path.** For text under about 300 words, or a quick casual request, one pass is enough:
draft with the pattern catalog, run `analyze` once and `fact_ledger` once, answer the checklist,
and deliver. Run the full loop (up to 4 revision rounds) for longer documents, anything that
will be submitted or published, or when the user asks for rigor.

---

## The verification loop

```
Phase 0  Scope        language, register, audience, voice sample, protected terms, length target
Phase 1  Baseline     analyze the source; build the fact inventory; read the pointers
Phase 2  Draft        rewrite or write using the pattern catalog; free choices only
Phase 3  Measure      style gate, over-correction limit, length check
Phase 4  Semantic     fact ledger; paragraph equivalence; checklist with the deletion test
Phase 5  Revise       fix what failed, from the top of the report; at most 4 rounds
Phase 6  Deliver      final text + verification block
```

### Phase 0: Scope
- **Language and register.** Choose `scientific`, `abstract` or `general`. For mixed documents,
  analyze each part with its own register.
- **Audience.** Name the reader in one line ("reviewers in environmental epidemiology",
  "readers of a city newspaper"). The same content for a different reader should come out
  measurably different.
- **Voice.** If the user has prior writing, save 300+ words of it as `writer_sample.md`. It
  becomes the target via `compare`, and it overrides the default bands.
- **Protected terms.** List technical terms, names and phrases that must survive verbatim. They are
  excluded from repetition checks (`--protect`), because repeating a term consistently is correct.
- **Length target.** "About 700 words" becomes `--target-words 700` (allowed range ±10%). "At
  most 250 words" becomes `--max-words 250`. In REWRITE mode with no stated length, the draft's
  own length (`count`) is the target: a faithful rewrite usually comes out about as long as the
  draft, because cutting filler and restoring grammar roughly cancel. If removing unsupported
  or empty material leaves less to say, do not refill it: deliver the shorter text and say why
  (ground rule 3).
- **Can the material carry the length?** When the user supplies the material (notes, facts, a
  short text) and a length, `count` the material before writing. Notes turn into prose of up to
  about twice their length (in the worked example, 151 words of notes carried 285 words of
  summary); a text that interprets, such as a discussion, can carry more, because its reasoning
  is content. If the request is several times what the material can carry, say so in your
  reply, deliver what it does carry, and list what would fill the rest. Do not write toward the
  number.
- **Short texts.** Under 150 words no gate is applied (too little text for stable statistics).
  Use the pointers and do Phase 4 thoroughly.

### Phase 1: Baseline (REWRITE, AUDIT, MATCH)
```bash
python3 $S/scripts/sci_metrics.py analyze source.md --register scientific --sentences > report_v0.txt
```
Read four things:
1. The **gate line and the dimension list.** Dimensions are sorted by how much of the composite
   each explains. The top three or four are the job.
2. **Where to look**: the exact sentences behind each problem (long or comma-chained sentences,
   compressed sentences with almost no glue words, uniform-length runs, formulaic openers, stock
   phrases, nominalization clusters, repeated frames), the words current models over-use that
   occur in the text, the padding candidates, the counts of names, numbers and punctuation
   marks, and the count of glue words next to the number a human text of that length has (a
   target you can count toward, and not past). `--sentences` prints every sentence numbered
   with its length and flags.
3. The **fact inventory**: every number, citation, named entity, hedge and negation. This is what
   `fact_ledger.py` will check later. Note hedges and negations yourself as well: the script counts
   them but does not know which claim each belongs to.
4. **Provenance of the draft's details.** If the source is an AI draft and the user supplied the
   real facts (a brief, notes, an abstract), read the draft against those facts and sort what
   the facts do not cover into two kinds. Current models invent both freely.
   - *Details about the user's own study or experience* (what happened, times, distances,
     names, quotes, ratings, figures, properties of their sample or sites): the user's facts are
     the ground truth. Remove these and list them in the verification block as questions ("Was
     a refund offered? If so, I can add it"). Use inline placeholders ("[time of first call?]")
     only when the user is clearly drafting and will fill them in. Do not replace a removed
     detail with a vaguer version of the same claim.
   - *Background claims about the world* (what is generally known in the field, how
     instruments are usually sited, what earlier work did): if the user asked to keep the
     draft's claims, keep them at the strength the draft gives them and list them in the block
     as "from the draft, unverified: cite or cut". If the user gave no such instruction, keep
     only what is uncontroversial and flag the rest the same way.
   Then run the ledger against the *user's facts* (`fact_ledger.py user_facts.md source.md
   --write`), so that numbers the draft invented show up as "added". Claims without digits are
   invisible to the ledger: only this reading finds them.

In WRITE mode, Phase 1 is collecting material instead. Before drafting, list the names, numbers,
dates, places, methods, datasets, prior studies and the actual stance (what is known, what is
uncertain, what is surprising, what is the limitation) available from the user or sources. If the
brief has no specifics and the text needs them, ask the user once, concisely, before writing.
When you must write without them:
- Use only the numbers and names supplied. Draw on general knowledge only when it is uncontroversial
  ("many hospital staff work night shifts"), never for precise statistics, named studies, quotes or
  anecdotes recalled from memory.
- Where a specific would normally go, write the sentence without it or leave a visible placeholder
  if the user is drafting ("[cite: light avoidance in Myotis]"). List the missing specifics in the
  verification block.
- Specificity then comes from precise reasoning: the exact mechanism, the real trade-off, the
  concrete consequence. A lower specificity score is the honest outcome. Report it; do not fake it.

### Phase 2: Draft
Rewrite paragraph by paragraph, not word by word. Rewriting in context, several sentences at a
time, holds together better than sentence-level patching, and reordering alone changes nothing
that matters. Write what the material supports, once, at the length it comes to; count
afterwards (Phase 3). A draft written toward a word count is padded before any check runs. For
each paragraph:

1. State its one job in a few words (report a result, explain a mechanism, concede a limit).
2. Keep the forced material (terms, numbers, names, citations) and rebuild the free material around
   it using the pattern catalog below.
3. Write full clauses: a subject, a plain verb, the articles and prepositions that ordinary
   grammar wants. Let the content set the rhythm: a short sentence where a point lands, a long
   one where a qualification needs its clauses.
4. Change the grammar around the field's words, not the words. "Thermoregulatory capacity
   declines with age" is a full clause and keeps the term. "The body gets worse at keeping
   cool" has left the register. The usual first-draft error of this loop is prose that is too
   plain: lay words for field terms, every phrase unpacked, no adjectives left.
5. End on the last substantive point, not on a summary of the paragraph's significance.

Touch what needs touching. Wholesale paraphrase invites meaning drift: in the rewriting studies,
measured meaning preservation fell with every additional pass (0.92 after one, 0.86 after five).

### Phase 3: Measure
```bash
python3 $S/scripts/sci_metrics.py analyze draft_v1.md --register scientific --target-words 700 --protect "..." > report_v1.txt
```
The report has three verdicts.

**Style gate.** It passes when all three hold:
- **Composite ≤ threshold.** Each dimension gets a score: how far the text sits from the human
  median toward the AI side, in human standard deviations. The composite is the weighted mean of
  those scores for each calibrated AI profile (weights: how strongly that model tier deviates
  from human text on each dimension), and the larger profile value counts. The threshold is the
  90th percentile of human texts **of the draft's own length**. The line under the gate says how
  many held-out human and AI texts pass at that length.
- **At most one classic violation.** Classic tells come from the research literature (formulaic
  openers, stock formulas, significance echoes, paragraph wrap-ups, repeated frames, uniform
  rhythm, flat punctuation, missing stance, piled-up filler). They are checked against the
  extreme human range even though current models rarely show them.
- **Over-correction within its limit.** The same scores measured on the far side of the human
  median: too much glue, words too short, variety too low, too many passives. A text that
  overshoots human writing fails here. Less filler, fewer model-typical words and more names
  and numbers than the median human text are never counted as over-correction.

**Dimension verdicts.** One PASS / WARN / FAIL per dimension, against the distribution of that
dimension's score in human texts of the same length. Under each weak dimension the report lists
its metrics with the human band, the typical value of each AI tier and one fix per habit. A
metric marked **OVER** is beyond the human range on the far side: pull it back.

**Length.** ON TARGET, UNDER or OVER, from the one word count every script shares (body, list
items and headings; a contraction, a hyphenated word or `l'étude` is one word; code and tables
are not counted). Always pass `--source` when the user gave notes, a brief or a text to work
from. The report then lists the numbers and names of the source that the draft does not use,
and the **sentences of the draft that are not anchored in the source** (no number or name,
little of its vocabulary), with the share of the words they hold. When that share is a quarter
or more and the count is in range, the report says CHECK THE LENGTH: in a text that reports (a
summary, results, a description) those sentences are padding and the length has not really
been reached; in a text that interprets (a discussion, an argument) they are the reasoning,
and each must follow from the source's facts.

Documents longer than about 1,200 words are scored in equal windows of calibrated length; the
report lists each window, which shows where a long text is weakest. If a writer sample exists,
also run `compare` and resolve deviations with |z| ≥ 2.58 first.

### Phase 4: Semantic gate
1. **Fact ledger.**
   ```bash
   python3 $S/scripts/fact_ledger.py source.md draft_v1.md --protect "..."                        # REWRITE / MATCH
   python3 $S/scripts/fact_ledger.py source.md draft_v1.md --facts user_facts.md --protect "..."  # REWRITE + extra user facts
   python3 $S/scripts/fact_ledger.py brief.md draft_v1.md --write                                 # WRITE (source = the brief)
   ```
   In REWRITE and MATCH mode, exit 1 (a number, citation or protected term missing or added)
   blocks delivery. Values from `--facts` may appear without counting as added, but they are not
   required. With `--write` only additions fail: a brief's numbers need not all be used, and
   "about 700 words" is not a fact.
   - Numbers are compared by value (`1,900,000` = `1.9 million`; French `3,5 %` = `3.5%`,
     `1 200` = `1200`). Citations are compared as references, so moving "(Smith et al., 2020)"
     into the sentence as "Smith et al. (2020)" is not a change.
   - A number that is absent from the source counts as derived when it equals arithmetic on two
     source numbers standing in the same paragraph of the draft: a total, a ratio, a percentage,
     a relative change ("1710 = 38 x 45", "34% = 100 x (1840 - 1210) / 1840"). The ledger lists
     the formulas it found; confirm the one you meant and show it in the verification block. If
     the operands stand elsewhere, the number counts as added: state the calculation where the
     reader can check it. Any other added number must be plain general knowledge ("24 hours")
     or go.
   - Review every added name or acronym (was it invented?) and every certainty warning (dropped
     hedge, added booster, changed negation count). A changed negation count is often a harmless
     rephrasing, but check each one: a lost "not" flips a finding.
2. **Paragraph equivalence.** Rate each draft paragraph against its source on a 5-point scale:
   5 = same meaning, 4 = nearly equivalent (nuance only), 3 = something changed, ≤ 2 = different.
   Everything must be ≥ 4. For a 3 or below, name the change and fix it.
3. **Checklist.** Answer each item honestly. Any "no" means revise.
   - [ ] **Traceable.** Every name, number, example and citation comes from the source or user.
   - [ ] **Draft-only claims.** When the user supplied the facts separately from an AI draft:
         every factual statement that stands in the draft but not in the user's facts (with or
         without digits) was removed or is listed in the verification block for the user to
         confirm.
   - [ ] **Deletion test.** For every sentence the report lists as a padding candidate, and for
         every sentence added to reach a length: delete it. Does the reader lose a fact, a step
         of the reasoning, a condition, a limit or a consequence? If not, it stays deleted.
   - [ ] **Stance.** The text commits where the evidence is strong, qualifies where it is weak, and
         says (if the source supports it) what is surprising, limited or most important.
   - [ ] **Specific.** No category word ("several studies", "various stakeholders") remains where
         the source offers the specific.
   - [ ] **Emotion calibrated.** Negative experiences and limitations keep the strength the source
         gives them. No apology or politeness template, no borrowed enthusiasm.
   - [ ] **Register held.** Nothing informal was upgraded to officialese, and nothing technical
         was replaced by lay words ("cardiovascular, respiratory and renal disease" stays; it
         does not become "diseases of the heart, lungs and kidneys" in a paper).
   - [ ] **Audience.** The text is written for the reader named in Phase 0.
   - [ ] **Paragraph moves.** Paragraphs do different jobs in different shapes. None ends by
         restating its own importance.
   - [ ] **Opening and ending.** The first sentence is specific to this text. The last paragraph
         adds something (a limitation, a concrete next step the source names, an implication it
         states) instead of restating or forecasting vaguely.
   - [ ] **No performative humanizing.** No fake casualness, slang, rhetorical questions for
         effect, typos, invented anecdotes or forced idioms.
   - [ ] **Voice (MATCH mode).** `compare` shows no deviation with |z| ≥ 2.58.
4. **Continuation probe (optional, needs a fresh subagent).** For high-stakes text, or when the
   gate passes but the prose still feels predictable: `dna_probe.py split draft.md`, give the
   printed prompt to a subagent that has never seen the draft, save its JSON reply, then
   `dna_probe.py score draft.probe.json continuations.json`. It prints each real second half next
   to the fresh model's version. Rate every pair: **2** = same points in the same order, **1** =
   partly overlapping, **0** = different points. In a blind calibration on 24 scientific
   paragraphs, 42% of AI-written paragraphs were rated 2 against 8% of human ones. Rework every
   paragraph rated 2 by adding what only this text can say or cutting the predictable half.

### Phase 5: Targeted revision
- Fix the failing dimensions from the top of the list, then the checklist items. Re-run Phases 3
  and 4 after each round.
- **Aim at the human median, not past it.** The composite is a ceiling, not a score to
  minimize. The commonest way to fail the second round is to overshoot: after "restore the glue
  words", every sentence becomes "it is the case that there is". When the over-correction line
  names a dimension at 2 or more, or a metric says OVER, find the cause. Usually it is the
  rewrite: field terms replaced by lay words, every phrase unpacked, classifying adjectives
  stripped. Put the register back, even if the composite rises a little (in one test run it
  went from 0.33 to 0.54, well under the threshold, and the text read like a paper again).
  Sometimes it is the subject or the genre (a paper about bats and roads has shorter words
  than one about thermoregulation; a plain-spoken column has few nominalizations): then leave
  it and say so in the verification block.
- **Stop** when the gate passes, no far-side dimension of the rewrite's own making remains, the
  length is on target (or honestly short, see below), the ledger is clean, every paragraph is
  ≥ 4/5 and the checklist is all "yes". **Also stop** after 4 rounds, or when a round improves
  neither the composite nor the over-correction line. Then report what remains and why.
- If a dimension cannot move without inventing facts (typically `specificity` when the source
  has no names or numbers), re-run with `--waive specificity` and state the waiver and its
  reason in the verification block. Waive only what honesty blocks.
- Never trade a Phase 4 failure for a Phase 3 pass. Meaning wins.

### Length without padding
A length check that says UNDER is the moment padding is born. Lengthen in this order, and stop
as soon as the count is in range.

1. **Unused source material.** `analyze --source` lists the source's numbers and names that the
   draft does not use. Add those that belong in this text.
2. **What follows from the facts.** For each claim, ask what a careful reader would ask next and
   answer it *from the source*: how it was measured, how large it is, compared with what, under
   which condition, with what consequence, limited by what. Arithmetic on the source's numbers
   counts (a total, a rate, a share), shown as arithmetic.
3. **Grammar the draft is missing.** Only where the report lists compressed sentences or the
   grammatical-glue dimension is not PASS: write those sentences as full clauses. This is repair,
   not a way to gain length. Where glue already passes, do not add any.
4. **Stop.** When the report says the draft already uses the source's numbers, or says CHECK
   THE LENGTH, and you cannot name where the next sentence would come from, the source does not
   support the requested length. Deliver the text at its honest length, give the count, and
   list the material that would fill the rest. Example: "This is 290 words. Your notes support
   no more without filler. For 700 I would need: results from another season or site, the cost
   of the sensors and of the water, how the fixed schedule was chosen."

**Name the source of every added sentence** before you keep it: a line of the notes, a
calculation, or a condition, limit or consequence that follows from stated facts. These are not
sources, and sentences built on them are padding or invention:
- general knowledge about the topic ("clay soils drain more slowly", "electricity prices are
  rising", "higher sugar is often associated with better wine");
- the importance of the subject ("water management is an increasingly important issue");
- commentary on the result ("this finding is noteworthy", "this difference matters
  considerably", "offers a practical path forward");
- what future work might show, unless the source says it.
A user who says "I have nothing beyond these notes" has told you where the text ends.

Then test what you added. This step is not optional when the user gave a text to lengthen.
`before.md` is the text as it stood before lengthening began (the user's text, or your last
draft that used only source material), never a draft that already contains the additions:
```bash
python3 $S/scripts/sci_metrics.py growth before.md after.md --register scientific --source notes.md
```
It reports:
- new content words and new specifics per 100 added words, next to what human texts of that
  register add when they grow from the same length;
- any padding rate that went up (by at least two occurrences, to above the human median);
- the **added sentences that carry no number or name and share little vocabulary with the
  source or the earlier version**, quoted one by one. These are the usual seat of filler and of
  claims the source does not make. Judge each: fact of the source, calculation, consequence of
  its facts, or cut.

**PADDING** means undo the addition. **THIN** means run the deletion test on every added
sentence, the listed ones first, and keep only what survives; a THIN verdict that survives the
test (an argument with no new names or numbers to add, for instance) is reported, not hidden.
**SUBSTANCE** means the added words carry content at the human rate; every new specific must
still pass the ledger. The check compares vocabularies, so run it on a version that only adds
to the earlier one: across a full rewrite, changed wording counts as new.

When the check says OVER, cut in this order: sentences that repeat an earlier one,
announcements, comment clauses, doublets, generic openers and closers. If the text is still
over, the remaining cuts remove content: ask the user which content matters least.

### Phase 6: Deliver
Return the final text first. Then give a verification block of about ten lines, unless the user
asks for more:

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
(From a real run; see `references/worked-example.md`.) In WRITE mode with a length target, add
the growth verdict and any derived numbers with their arithmetic. In file mode, write only the
final text to the file and put the verification block in chat. In AUDIT mode, list findings by
dimension with sentence numbers and end with the five changes that would move the composite most.

The block reports what the scripts printed, on the final text, with the register chosen in
Phase 0:
- **Verdicts are copied, not paraphrased.** PASS or FAIL; ON TARGET, UNDER or OVER; SUBSTANCE,
  THIN or PADDING. A composite above the threshold is FAIL by any margin: 0.652 against 0.651
  is not "nearly passing".
- **If the gate still fails when you stop**, the first line of the block says so, with both
  numbers, the dimensions that remain and what you would try next. A failing text may be
  delivered. It may not be presented as passing.
- **Every WARNING of the ledger gets an answer**: the word concerned, and why the change is
  harmless or what you restored. A dropped hedge is restored unless the source itself is flat.
- **Every far-side dimension at 1.5 or more is named**, with its cause (the rewrite, or the
  subject).

---

## What the gate was measured to do

Human bands come from pre-2020 human text; the AI side is text from two current Claude tiers
(Sonnet and Haiku) answering ordinary requests on the same topics. Every text is scored by bands
it did not help to set. Share of **unedited AI texts that pass the whole gate**, by length:

| Register | 150 words | 200 | 300 | 450 | 600 | 750 | 900 | Human texts passing |
|---|---|---|---|---|---|---|---|---|
| English scientific | 2% | 2% | 0% | 0% | 0% | 0% | 0% | 84–87% |
| English abstract | 0% | 0% | 0% | | | | | 85–86% |
| English general | 12% | 10% | 8% | 7% | 4% | 3% | 4% | 87–88% |
| French scientific | 5% | 2% | 2% | 0% | 0% | 0% | 0% | 84–86% |
| French abstract | 5% | 2% | 0% | | | | | 85–87% |
| French general | 22% | 15% | 8% | 5% | 2% | 2% | 0% | 85–88% |

How to read it:
- About one human text in seven fails. The gate asks for the central range of human writing, so
  failing it says nothing about who wrote a text.
- Short general prose is where the gate is weakest: at 150 words one unedited AI text in eight
  (English) or one in five (French) gets through. There, Phase 4 does more of the work.
- A gate rebuilt without one model tier still rejects that tier's texts 96–99% of the time in
  scientific prose and 68–98% of the time in general prose, which is some evidence that it is
  not tuned to one model. It has not been tested on other model families.
- 23 further AI texts that played no part in the calibration all fail (composites 0.77–1.82).
  Five texts produced with this loop (two rewrites of AI drafts and three texts written from a
  brief; English and French; scientific and general) score 0.27–0.54 where unedited answers to
  the same requests score 0.84–1.82, against thresholds of 0.65–0.68.
- Documents too long to score whole are scored in windows: 86–91% of long human documents pass,
  and none of the long documents assembled from AI texts.

## Know your fingerprint

Medians at 450 words, English scientific prose, human → Sonnet tier / Haiku tier. The other
English registers are in `references/calibration.md` §4, French in `references/french.md` §3.

| Habit | Human | Sonnet tier | Haiku tier |
|---|---|---|---|
| Glue words (the, of, be, to, in) per 100 tokens | 18.2 | 13.5 | 11.9 |
| Lexical density (content words / all words) | 0.59 | 0.61 | 0.67 |
| Mean word length (letters) | 5.67 | 6.06 | 6.63 |
| Over-used function words per 1k (how, across, rather, than ...) | 11 | 37 | 31 |
| Over-used content words per 1k (require, pattern, approach ...) | 15 | 37 | 53 |
| Word variety (MATTR-50 on lemmas) | 0.775 | 0.843 | 0.823 |
| Names + acronyms + numbers (% of tokens) | 5.8 | 1.4 | 1.1 |
| Parentheses per 1k words | 6.8 | 0 | 0 |
| Derived adverbs in -ly (% of tokens) | 1.3 | 3.2 | 2.0 |
| Auxiliaries be / have / do (% of tokens) | 4.1 | 3.2 | 2.9 |
| Sentences with ≥ 3 nominalisations | 17% | 37% | 26% |
| Comment clauses after a comma, per 1k | 0 | 2.3 | 2.2 |
| Abstract framing nouns per 1k | 11 | 13 | 24 |
| Paragraph-length variation (CV) | 0.36 | 0.24 | 0.24 |
| **Mean sentence length (words)** | **26** | **42** | **22** |
| Sentence-length variation (CV) | 0.38 | 0.36 | 0.33 |

What the table says:
- **Both tiers compress.** Fewer glue words, more content words per sentence, longer words. This,
  and not synonym rotation, is most of why all-word variety scores run high.
- **The tiers differ in rhythm.** The larger model writes sentences far longer than human ones
  and chains them with commas. The smaller one writes shorter, more even sentences in short
  paragraphs and leans harder on nouns and framing words. Sentence length is therefore scored on
  both sides, and "split long sentences" is advice for one profile only: read which profile the
  report says the draft leans toward.
- **Some older tells are gone, some are not.** Formulaic openers ("Furthermore", "Moreover")
  are no longer a tell: 70% of human papers contain at least one, as do 70% of the smaller
  tier's and 20% of the larger tier's. Classic wordy phrases ("in order to", "due to the fact
  that") are commoner in human text (85% of papers against about half of model texts). What
  survives: formulaic endings (30% of the larger tier's scientific texts, 6% of human ones),
  and in the smaller tier significance echoes and stacked hedges (each in 20% of its scientific
  texts, under 3% of human ones). The classic guards keep checking all of these, because other
  models and older drafts still produce them.
- **Half the published function-word lists no longer hold.** Lists from GPT-3.5-era studies have
  AI text over-using *by* and *with* and under-using *or*, *this* and *might*. In the
  calibration corpora *by* is rarer and *or* commoner in AI text in every register and both
  tiers, and in scientific prose the reversal extends to *with*, *this*, *might* and *would*.
  The marker lists in this skill are derived from the calibration corpora and validated on
  held-out texts (`calibration.md` §6).

Two habits no table shows. **Invented vivid detail:** asked for a complaint about a car rental,
a model added a five-hour flight, a nine-month-old and a quoted remark from the clerk; none was
in the brief. **Length drift:** asked for about 700 words, the baselines delivered between 450
and 960; in French both tiers ran short (medians 624 and 548 words). In one batch a model
answered 800-word requests with 250 words after a run of short abstracts. Count; do not
estimate.

Fingerprints drift between model versions, so measure the draft in front of you.

---

## Pattern catalog

Each pattern gives the **signature** (with evidence), the **check** (what the analyzer reports),
the **fix**, and the **over-correction** to avoid. Examples are illustrative. Where an "after"
uses a detail, that detail is stated as present in the source. French versions of each pattern:
`references/french.md`.

### A. Sentence architecture

**A1. Sentence length off the human band.** *Signature, long profile:* one sentence carries four
or five ideas joined by commas, relative clauses and participles (42 words on average against 26).
*Signature, short profile:* a run of clipped sentences of similar length, one claim each (22
words, with little variation). *Check:* `sent_len_mean`, `long_share`, `short_share`,
`comma_per_sentence`; the dimension is two-sided. *Fix, long:* split at the logical joints and
make the logic explicit (because, but, so, which means); one main idea per sentence, two at
most. *Fix, short:* join sentences that belong to one thought, with the relation stated.
*Over-correction:* chopping everything to 12 words, or welding everything into 40.
> Before: "Coral bleaching, which is triggered by prolonged marine heatwaves that disrupt the symbiosis between corals and their photosynthetic algae, can lead to widespread mortality, particularly in shallow reef systems, thereby threatening the biodiversity and coastal protection that reefs provide."
> After: "Prolonged marine heatwaves break the symbiosis between corals and their photosynthetic algae. Shallow reefs suffer most, and when the corals die, so do the biodiversity and the coastal protection that the reef provided."

**A2. Uniform rhythm.** *Signature:* sentence lengths cluster tightly, with runs of similar
length. Lower sentence-length variance is a consensus finding. In the calibration it is clear in
abstracts and in French scientific prose (both tiers), mild for the smaller tier in English, and
absent for the larger tier in English general prose. *Check:* `sent_len_cv`, `masd_norm`,
`uniform_run_max` and its location. *Fix:* let a key result or a turn in the
argument stand alone as a short sentence; allow one long sentence where a qualification needs
it. *Over-correction:* fragments for drama ("No effect. None.").

**A3. Subject-first monotony.** *Signature:* nearly every sentence starts with its grammatical
subject. *Check:* `subject_initial_share`, `varied_opener_share`, `skeleton_entropy`. *Fix:* open
some sentences with the frame that governs them: the condition ("If the dose is halved, ..."),
the time ("Between 2012 and 2015, ..."), the contrast ("Unlike the field trials, ..."), the cause
("Because the sensors drift, ..."). *Over-correction:* inverted syntax everywhere, or dangling
participles.

**A4. Uniform paragraphs.** *Signature:* every paragraph has three or four sentences of similar
length. *Check:* `para_words_cv`, `para_sents_cv`. *Fix:* let a pivot or a single key result be a
short paragraph, and let an argument run long. *Over-correction:* one-sentence paragraphs
throughout in a scientific text.

### B. Words and grammar

**B1. Compressed prose (missing glue).** *Signature:* noun stacks and abstract subjects doing
action verbs, with the small words stripped out: few articles, few "of" phrases, few forms of
"be", few "there is" or "it is". This is the most consistent signal measured: the five
commonest English grammatical words are a quarter to a half rarer in model text, in every
register and both tiers, and a human text has more of them than an AI text in about nine
comparisons out of ten (95% on whole documents). *Check:* `glue_per100`, `lexical_density`,
`aux_pct`, `of_per100`, and the list of compressed sentences.
*Fix:* say it as a clause. Give the noun stack its prepositions ("the quality of the data on
patient outcomes"), let simple statements be simple ("X is common in Y"), use the passive where
a paper would. *Over-correction:* "it is the case that there is". Glue has a human median too;
past the 90th percentile the text reads as filler, and the report says OVER.
> Before: "Machine-learning models increasingly guide clinical decisions, yet performance often degrades across hospitals, raising questions about how reliably such tools generalize beyond training sites."
> After: "Machine-learning models are now used in clinical decisions, but their performance often drops when they are moved to another hospital. It is not clear how well they generalize beyond the sites where they were trained."

**B2. Over-used words (calibrated list).** *Signature:* a small set of words appears two to four
times as often as in human text on the same topics. Function words: *rather, how, across, than,
or, where, toward, what, through, without, itself, beyond, yet, within, might, single.* Content
words: *require, pattern, represent, approach, substantial(ly), actually, particular(ly),
specific, reflect, create, broad, suggest, shape, shift, kind, structure, attention, establish,
condition, system, decade, practical, mechanism, remain, address, challenge, capture, multiple,
quality, framework, reveal, offer, extend, enable, manage, examine, matter.* Under-used:
*as, also, there, on, by, we, will, after, all, such, very*, and the workhorse words *study, use,
show, example, include, lead.* *Check:* `markers.*`, and the report lists the hits. *Fix:* most
hits come from a few constructions. "How / what / whether" clauses used as abstract objects
("understanding how X shapes Y") become plain noun phrases or statements ("the effect of X on
Y"); "rather than", "across" and "through" become "not", "in" and "by"; "requires", "reflects",
"remains", "offers" become what is actually the case. *Over-correction:* treating the list as
banned words, or swapping each for a synonym (the synonym is the next marker). It is a rate:
bring it toward the human median.

**B3. Long and upgraded words; thesaurus prose.** *Signature:* plain words upgraded (use →
utilize, show → elucidate) and, in the larger tier's scientific prose, the same entity given
several names ("participants... respondents... the cohort"). *Check:* `word_len_mean`,
`long_word_pct`, `content_types_at_50`, `content_mattr25`. *Fix:* the short everyday word where
it says the same thing, and one term per concept, repeated as the field repeats it.
*Over-correction:* replacing the field's own terms with lay words. Human scientific prose
averages 5.7 letters per word; a rewrite at 4.8 has lost its register.
> Before: "Participants completed the survey. Respondents were then allocated to the intervention, after which subjects underwent reassessment and the cohort's outcomes were juxtaposed with the comparator arm."
> After: "Participants completed the survey and were then randomized. After the intervention we assessed them again and compared their outcomes with those of the control group."

**B4. Modifier load.** *Signature:* stacked adverbs and evaluative adjectives (dramatically,
increasingly, fundamentally, particularly; robust, comprehensive, nuanced, critical). *Check:*
`deriv_adv_pct`, `adj_pct`, `promo_per1k`, and the report's list of most-used adverbs. *Fix:*
delete modifiers that only intensify. Keep those that classify or quantify (randomized, thermal,
twice, only). If the source has the number the adverb gestures at, use the number.
*Over-correction:* stripping adjectives that carry technical meaning.
> Source facts: F1 0.91 vs 0.84 (best baseline); best on 5 of 6 benchmarks; worst on the smallest (n = 212).
> Before: "The proposed method delivers remarkably robust performance, dramatically outperforming existing approaches across a comprehensive range of benchmarks."
> After: "The method reached an F1 of 0.91 against 0.84 for the strongest baseline and won on five of six benchmarks; it lost on the smallest one (n = 212)."

**B5. Nominalization clusters.** *Signature:* actions turned into nouns and stacked ("the
implementation of the optimization of..."). In scientific prose, sentences with three or more
nominalizations are 1.6 to 2.2 times as common in model text. *Check:* `nominal_heavy_share`,
`nominalization_per1k`, plus the listed sentences. *Fix:* find the actor, then give it the verb.
*Over-correction:* scientific terms of art that are nouns (transcription, inflammation) stay
nouns.
> Before: "The implementation of the new timetable resulted in a reduction in the utilization of peak-hour trains and an improvement in commuter satisfaction."
> After: "After the new timetable started, fewer commuters took peak-hour trains, and those who did were more satisfied."

**B6. Category words instead of specifics.** *Signature:* "several studies", "various
stakeholders", "multiple regions", "researchers have found". Model text carries a fifth to a
quarter of the names, acronyms and numbers of human scientific text, and about a third of those
of human articles. *Check:* `specificity_pct`, `propn_pct`, `num_pct`. *Fix:* replace the
category with the specific *from the source*. If the source has none, ask or cut the claim.
Never invent a name, number or citation to raise this metric.
> Source facts: Pereira et al. 2016 (Lisbon); Zhang 2019 and Liu 2020 (two Chinese cohorts).
> Before: "Several studies across multiple regions have documented similar effects in diverse populations."
> After: "Similar effects were reported in Lisbon (Pereira et al., 2016) and in two Chinese cohorts (Zhang, 2019; Liu, 2020)."

**B7. Stock phrases.** *Signature:* formulas the research names ("it is important to note that",
"it can be observed that", "in conclusion", "not only... but also") and practitioner-documented
LLM vocabulary (delve, pivotal, crucial role, landscape, tapestry, testament, shed light, pave
the way, in recent years, valuable insights into). Rare in current Claude output, common in
other models and older drafts. *Check:* `stock_per1k` (classic guard) and the hit list. *Fix:*
replace each with the specific claim it stands in for, or delete it. Some words are legitimate
in context ("landscape" in ecology, "robust" in statistics). *Over-correction:* replacing one
cliché with a synonym cliché.

### C. Cohesion and logic

**C1. Formulaic sentence openers.** *Signature:* "Furthermore,", "Moreover,", "Additionally,",
"Overall,", "Notably,", "In conclusion,". The most-cited tell in the older literature; in the
calibration, human papers use them as often as model texts do, so only a pile of them counts.
*Check:* `formulaic_initial_share` (classic guard), plus the listed sentences. *Fix:* delete
the connective when the relation is obvious; when it matters, state it inside the sentence.
*Over-correction:* none of the logical connectives are banned. Keep "However" when something
actually contrasts.

**C2. Statements side by side instead of related.** *Signature:* facts accumulate without the
relation between them being said. *Check:* `logical_connective_share`, `human_fw_per1k`. *Fix:*
where two statements stand in a relation of cause, contrast, condition or concession, say which.
> Before: "Sales increased in December. Online orders accounted for most of the growth. In-store sales did not change."
> After: "Sales rose in December, mostly because of online orders, but in-store sales did not change."

**C3. Balance formulas.** *Signature:* "not only X but also Y", "it's not just X, it's Y", "while
X, Y" framings that fake nuance. *Fix:* state the claim directly.

### D. Stance and evaluation

**D1. Missing stance.** *Signature:* neutral, non-committal voice. Human writers commit, doubt,
evaluate and appear ("we", "I"). *Check:* `stance_per1k` (classic guard), `self_mention_per1k`.
*Fix:* where the source supports it, say which result is strongest, which is surprising, and
what the limitation is. Let the authors act ("we measured", "we suspect"). *Over-correction:*
manufactured opinions, or enthusiasm the source does not contain.

**D2. Formulaic versus calibrated hedging.** *Signature:* blanket hedges that attach to nothing
("may potentially", "could possibly") alongside flat claims where uncertainty is real. *Check:*
`double_hedge_per1k`, `hedges_per1k`. *Fix:* one hedge per uncertain claim, tied to the reason
for the uncertainty.
> Source facts: HR 0.85, 95% CI 0.71–1.02.
> Before: "The results may suggest that the intervention could potentially have some effect on relapse."
> After: "The intervention probably reduced relapse (HR 0.85), although the confidence interval (0.71–1.02) includes no effect."

**D3. Sanitized or templated emotion.** *Signature:* negative experience turned into politeness
or apology templates, or generic enthusiasm. In one benchmark pair the AI continuation of an
angry review read "I apologize for the inconvenience... We strive to provide exceptional service".
*Check:* `critical_per1k`, `promo_per1k`. *Fix:* keep the grievance and its strength, and name
what went wrong concretely, using the facts given. *Over-correction:* insults or theatrics the
writer did not express.
> Source facts: movers arrived four hours late, broke a table leg, and the company refused a refund for two weeks.
> Before: "While the move presented some challenges, the team worked diligently, and the company was responsive to our feedback."
> After: "The movers showed up four hours late and broke a leg off our table. Then the company spent two weeks refusing a refund."

**D4. Comparisons without a basis.** *Signature:* "more robust", "more nuanced", "most
importantly", with nothing compared. In general prose the larger tier uses nearly twice as many
comparatives as human writers, the smaller tier half as many again. *Check:*
`comparative_per1k` (reported). *Fix:* keep a comparison only with its basis ("twice as fast as
the 2019 pipeline"). Otherwise cut it.

**D5. Audience blindness.** *Signature:* the same text regardless of reader. *Fix:* decide what
this reader already knows and needs. Experts get field terms and denser sentences; newcomers get
definitions and shorter ones.

### E. Punctuation

**E1. Comma-and-period monoculture.** *Signature:* nearly all punctuation is commas and
periods. Nine human papers in ten contain parentheses (about 7 per 1,000 words); none of the
larger tier's scientific texts does, and one in six of the smaller tier's. *Check:*
`punct_entropy_nodash`, `nonbasic_share_nodash`, `per1k.parenthesis`. *Fix:* use each mark for
its real job. Parentheses carry abbreviations,
exact values, sample sizes and brief asides ("(n = 212)", "(OECD data)"). A semicolon joins two
tightly linked clauses. A colon introduces what it promises.
> Before: "The Organisation for Economic Co-operation and Development reported that unemployment fell to 5.1 percent, which was lower than the previous year, and this decline was concentrated among younger workers."
> After: "Unemployment fell to 5.1% (OECD figures); most of the decline came among younger workers."

**E2. Dashes.** *Signature:* many LLMs over-use em dashes (a practitioner observation, not a
finding of the papers). Three quarters of the smaller Claude tier's English texts contain at
least one, almost none of the larger tier's; among human texts, 17% of papers and 63% of
articles. *Check:* `em_dash_per1k`; dashes are excluded from the variety metrics on purpose.
*Fix:* keep dashes rare unless the writer sample uses them.

### F. Document shape

**F1. Stock openings.** *Signature:* "In recent years,", "The rapid advancement of...", "X has
emerged as a...". *Check:* `stock_opener`. *Fix:* open with the specific subject of this text:
its question, its tension or its first concrete fact from the source.
> Source facts: the study found microplastics in 94% of 312 Baltic sediment samples.
> Before: "In recent years, microplastics have emerged as a pervasive environmental concern with far-reaching implications."
> After: "Microplastics were present in 94% of the 312 Baltic sediment samples we analyzed."

**F2. Predictable endings.** *Signature:* "In conclusion...", "future research should
explore...", "paves the way for...", or a last paragraph that repeats the first. AI text is most
predictable toward the end of a document, and 30% of the larger tier's scientific texts end on
such a formula (6% of human ones). *Check:* `formulaic_ending`, `intro_outro_overlap`,
`paragraph_wrapup_share`. *Fix:* end on the last thing the reader needs from this source: the
key limitation and its consequence, the specific next step the authors name, or the finding that
matters most, stated plainly. Do not add a moral.

**F3. Templated arguments.** *Signature:* every paragraph runs claim → evidence → rebuttal →
conclusion, or topic sentence → three supports → wrap-up. *Fix:* vary what paragraphs do. A
result can stand without a wrap-up, and a limitation can sit beside the result it limits.

**F4. Hallucinated specifics and drift.** *Signature:* plausible but wrong names and numbers, and
invented vivid detail when writing from a brief. *Check:* `fact_ledger.py` (added numbers,
citations and names). Invented events and descriptions carry no digits, so the ledger cannot see
them: re-read against the brief. *Fix:* delete anything not traceable, or mark it as a
placeholder for the user to confirm.

**F5. Hybrid seams (MATCH mode).** *Signature:* abrupt style shifts where new text meets the
user's own. *Check:* `compare` between the new part and the surrounding text. *Fix:* match the
surrounding measured profile.

### G. Padding

Padding is text that can be deleted without the reader losing a fact, a step of reasoning, a
condition, a limit or a consequence. The analyzer points at candidates; the deletion test
decides. None of the papers behind this skill measures padding directly. The verbose chatbot
answer they describe belongs to older models; what current models add is listed here.

**G1. Comment clauses after a comma.** *Signature:* ", highlighting the need for...", ", making
it...", ", thereby reducing...". Human scientific text: median 0 per 1,000 words; models 2 to 5.
*Check:* `participial_clause_per1k` (classic guard), with sentence numbers. *Fix:* cut the
clause, or make it a sentence with a subject and a finite verb that states a fact.

**G2. Abstract framing nouns.** *Signature:* role, challenge, framework, landscape, dynamics,
implications, potential: nouns that frame content without being content. A little over twice
the human rate in the smaller tier's scientific prose, four times in its general prose, and 1.5
to 3 times in French. *Check:* `shell_noun_per1k`. *Fix:* replace the frame with the thing
("plays a role in the regulation of" → "regulates"; "the challenge of X" → "X is hard because
...").

**G3. Announcements and restatements.** *Signature:* "It is worth noting that", "As mentioned
above", "In other words"; a sentence most of whose content words already stood together in an
earlier one; a closing sentence about significance. *Check:* `metadiscourse_per1k`,
`restatement_share`, `significance_echo_per1k`. *Fix:* say the thing once.

**G4. Doublets, stacked hedges, lists of three.** *Signature:* "robust and reliable", "may
potentially", "accuracy, efficiency and scalability". *Check:* `binomial_per1k`,
`double_hedge_per1k`, `triad_lists_per1k`. *Fix:* keep the word that carries the meaning; keep
lists the content requires (all study sites, all outcomes) and cut decorative ones.

**G5. Wordy phrases: a guard, not a target.** "In order to", "due to the fact that", "as well
as" are *more* frequent in human scientific prose than in model prose. Shorten them where
nothing is lost, but zero is not the goal, and piling them up to gain length fails the classic
guard. *Check:* `wordy_per1k`.

### H. Formatting artifacts
Bold phrases scattered through prose, bullets with bold lead-ins, title-case headings and emoji
in documents that do not use them are chatbot formatting, not writing. The analyzer reports them
under `format`. Use headings and lists only where the document type calls for them.

---

## Performative humanizing: never do this

The research shows why cosmetic tricks fail. Style instructions alone left the probabilistic
signature intact (99.5 F1). An instruction to "humanize" was the *weakest* of five rewrite
instructions for one rewriter in a watermark-removal study. Blind synonym swaps destroyed
fluency and meaning. Beyond that, these tricks make writing worse:

- inserting typos, lowercase sloppiness, slang, "lol", filler ("honestly", "look,")
- rhetorical questions and exclamation marks for "energy"
- fragments and one-line paragraphs for drama
- invented first-person anecdotes, feelings or experiences
- rotating synonyms or rare words to change a variety score
- sprinkling "the", "of", "there is" or wordy phrases to raise the glue count
- adding sentences to reach a word count: background the source does not contain, the
  importance of the topic, comments on how notable a result is
- swapping every listed marker word for its nearest synonym
- deleting all hedges, all passives or all technical terms
- replacing every em dash with another decorative device

If a metric can only be moved by one of these, leave it and report it.

## Scientific writing notes

- **Introduction.** The human shape moves from what is known (with named prior work) to the
  specific gap, to what this study does. The AI shape opens with generic background, fills in
  with importance claims, and states the aim vaguely. Open with the specific problem, and name
  prior studies where the source provides them. Do not carry results from the abstract into an
  introduction to raise specificity: it says what was asked and what was done (design, sample,
  period), not what was found, unless the draft or the journal's style does.
- **Methods.** Passive voice and repeated terminology are normal here. Do not "vary" them.
  Precision over rhythm.
- **Results.** Numbers with units, effect sizes and intervals in parentheses. Avoid interpretive
  adjectives ("striking increase") unless the authors interpret. Past tense for what was found.
- **Discussion.** Human authors interpret, compare with *named* earlier findings, admit
  surprises, and give limitations with their consequence ("so the estimates are conservative").
  AI discussions restate results, list generic limitations and close with "future research
  should explore...". Keep every limitation the source states, specific to this study.
- **Abstract.** Dense, but the density comes from specifics (numbers, sites, named methods), not
  from nominalizations and adjectives.
- **Hedging** tracks evidence: "suggests" for correlational data, "shows" for a replicated,
  controlled result. Never strengthen a claim to sound confident.
- **Terminology** stays fixed once defined, and abbreviations are defined once in parentheses.
- **Citations and numbers** are forced choices. Copy them exactly.

## French

The scripts handle French directly: elisions (`l'étude` is one word and two tokens), a French
lemma and part-of-speech lexicon, decimal commas and spaced thousands in the ledger, and bands
calibrated on French human and AI text for the same three registers. The loop, the ground rules
and the catalog's logic are unchanged. What differs, in short:

- The missing glue is *être* and *avoir* (and *en*, *dans*), not articles. Model French avoids
  the copula, the passé composé, the passive, "il y a", "il est possible que", and "nous / on / il".
  Scientific text from both tiers has less than half the auxiliaries of human text.
- Heavy verbs and framing nouns take their place: *constituer, demeurer, offrir, révéler,
  contribuer; enjeu, contexte, approche, compréhension*; and adjectives (*majeur, critique*) and
  adverbs in *-ment* (*particulièrement, largement, directement*) pile up, at about twice the
  human rate.
- In scientific French, sentence lengths vary much less than in human text (both tiers), and
  sentences are either very long (larger tier, 42 words on average) or short and clipped
  (smaller tier, 15 to 21 words).
- French typography is checked and reported (space before `; : ! ?`, guillemets, decimal comma).

`references/french.md` has the French catalog with before/after examples, the calibrated French
word lists and the measured fingerprint.

## Limits

- English and French only.
- Under 150 words no gate is applied; rely on Phase 4.
- The AI side of the calibration is two tiers of one model family. Other models may deviate in
  directions the gate does not weigh. Re-calibrate with `sci_metrics.py calibrate --human DIR
  --ai DIR --register NAME` when you have 20+ texts of each kind.
- Short general prose passes more unedited AI text than any other case (table above).
- The human corpora set the idea of "human": research articles in medicine, life and social
  sciences, arXiv and HAL abstracts, news, encyclopedic and explanatory writing. A legal brief,
  a poem or a product page has other norms.
- Padding metrics find candidates; only the deletion test decides.
- The taggers are about 90% accurate. Part-of-speech rates are reliable for a document, not for
  a sentence.
- Statistics describe prose, not authorship. Never present a score as proof of who wrote a text.

## Files

| File | Purpose |
|---|---|
| `scripts/sci_metrics.py` | analyze / compare / count / growth / calibrate / selftest: all metrics, the gate, pointers |
| `scripts/fact_ledger.py` | numbers, citations, names, protected terms, hedges / boosters / negations; derived numbers |
| `scripts/dna_probe.py` | optional continuation-predictability probe (split / score) |
| `scripts/textcore.py` | the shared definitions: word, token, lemma, sentence; markdown handling; tagger |
| `scripts/lexstats.py` | vocabulary estimators with exact formulas and their self-test |
| `scripts/lang_en.py`, `scripts/lang_fr.py` | word lists and rules per language, each list tagged by provenance |
| `scripts/data/calibration.json` | human bands per language, register and length; AI profiles; thresholds; pass rates |
| `scripts/data/markers_en.json`, `markers_fr.json` | calibrated marker words with their held-out validation |
| `scripts/data/en_lexicon.tsv`, `fr_lexicon.tsv` | part-of-speech and lemma lexicons (French: CC BY-SA 4.0) |
| `references/research-digest.md` | the papers: findings, numbers, contradictions, corrections, what is not actionable |
| `references/metrics.md` | every unit, formula and word list, with known weaknesses |
| `references/calibration.md` | corpora, method, pass rates by length, fingerprints, experiments, marker lists, growth bands |
| `references/calibration-tables.md` | every metric in every register: separation, direction, human band, AI medians |
| `references/french.md` | French patterns, word lists, typography, measured fingerprint |
| `references/worked-example.md` | the loop on real drafts in both languages: reports, rounds, ledger, growth check, verification |
| `evals/evals.json` | test requests (rewrite, write, lengthen, audit; English and French) with their input files |
