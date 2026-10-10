# SciHumanizer

English · [Français](README.fr.md)

<p>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT licence"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8 or later">
<img src="https://img.shields.io/badge/languages-English%20%7C%20French-blue.svg" alt="English and French">
</p>

SciHumanizer is a skill for Claude that writes and rewrites English and French prose so that it no longer reads as machine-generated, then verifies its own work with scripts. Although we built it for scientific and academic writing (paper sections, abstracts, theses, reports), it is also calibrated for essays, articles and opinion pieces.

When a text "sounds like AI", the usual treatment is a list of words to avoid. The research behind this project shows why such a list is not enough: in one study, a detector still reached 99.5 F1 on text generated with style prompts such as "write in the style of a high-school student". What gives machine prose away is mostly statistical. It sits in the grammar, in sentence length and in the proportion of names and numbers. Nobody can see it by rereading a draft, so the skill measures it. For every draft, an analyzer makes the comparison with human writing in the same language, in the same register and of the same length. A fact ledger then verifies that no number, citation, negation or hedge has changed, while a length check refuses to reach a word count with filler.

## A rewrite, before and after

On the left is a sentence from an introduction that a model drafted from an abstract (the study is invented; it serves as a test case). On the right, the rewrite keeps every fact and every technical term. Only the grammar changes: one long sentence becomes three, with the verbs and articles that the draft had squeezed out.

| Before | After |
|---|---|
| Age-related declines in thermoregulatory capacity, a higher prevalence of chronic cardiovascular, respiratory, and renal conditions, and greater likelihood of taking medications that impair the body's ability to dissipate heat all combine to make even moderately elevated temperatures more dangerous for older adults than for younger populations. | Thermoregulatory capacity declines with age. Chronic cardiovascular, respiratory and renal conditions are more prevalent in later life, and so is the use of medications that impair the dissipation of heat. Even moderately elevated temperatures are therefore more dangerous for older adults than for younger people. |

Over the whole introduction, the scripts reported the following.

| Measure | Draft | Rewrite | Human median |
|---|---|---|---|
| Words | 694 | 664 | |
| Composite score (the gate passes at 0.67 or below) | 1.57 | 0.54 | |
| Mean sentence length, in words | 46.3 | 26.6 | 26.6 |
| *the, of, be, to, in* per 100 tokens | 12.1 | 18.3 | 17.9 |
| Mean word length, in letters | 6.07 | 5.37 | 5.67 |
| Numbers and citations changed, by the fact ledger | | 0 | |

It took five drafts to get there. Although the first one already passed the gate, it was clearly the worst of the five: it had replaced the field's terms with lay words ("chronic diseases of the heart, the lungs and the kidneys") and ran about 100 words over the allowed length. Both the over-correction line and the length check said so, and later rounds restored the register. All five drafts are in [`examples/`](examples/), next to five other runs in English and French, each of which is discussed in [`references/worked-example.md`](references/worked-example.md).

## What the measurements say about AI prose

We calibrated the analyzer on 1,630 human texts, all written before 2020, and on 308 texts from two model tiers (the Sonnet and Haiku tiers of Claude) that answered ordinary requests on the same topics. The most consistent result is that the models compress. In English papers and articles, they use a quarter to a third fewer of the five commonest grammatical words (*the, of, be, to, in*). In French papers, they use barely more than half as many of *être, avoir, en* and *dans* as human authors do. As the medians below show for English scientific prose at 450 words, they also put more content words into each sentence, choose longer words, and name far fewer people, places and figures.

| Habit | Human | Larger model | Smaller model |
|---|---|---|---|
| *the, of, be, to, in* per 100 tokens | 18.2 | 13.5 | 11.9 |
| Mean sentence length, in words | 26 | 42 | 22 |
| Mean word length, in letters | 5.67 | 6.06 | 6.63 |
| Names, acronyms and numbers, % of tokens | 5.8 | 1.4 | 1.1 |
| Parentheses per 1,000 words | 6.8 | 0 | 0 |

Several tells listed in older guides did not survive measurement. Openers such as "Furthermore" and "Moreover" appear in 70% of the human papers, which is as often as in the smaller model's texts and far more often than in the larger model's (20%). Wordy phrases such as "in order to" are in fact commoner in human papers. About half of the function-word lists published for GPT-3.5-era text also point in the wrong direction for the two models tested here, so we derived the skill's word lists from its own corpora and validated them on held-out texts. All of this evidence is laid out paper by paper in [`references/research-digest.md`](references/research-digest.md), together with the claims that did not survive a check against the papers themselves.

## How it works

Every request goes through the same loop, with at most four rounds of revision.

1. First the scope is fixed: language, register (scientific, abstract or general), reader, length, and the terms that must survive word for word.
2. The analyzer measures the source and lists its facts, namely every number, citation, name, hedge and negation.
3. The text is rewritten one paragraph at a time. Only free choices change (openers, transitions, modifiers, the order of information), while terms, names, numbers and citations are copied exactly.
4. Each draft is measured against the style gate, the over-correction limit and the word count.
5. Then the meaning is checked with the fact ledger, a comparison of each paragraph with its source, and a checklist that includes a deletion test for every sentence suspected of padding.
6. Whatever failed is revised, and the dimension that weighs most in the score comes first.
7. Finally the text is delivered with a short verification block.

The checks are plain Python scripts and can be run by hand.

| Check | Command | What it decides |
|---|---|---|
| Style gate | `sci_metrics.py analyze` | The composite score is at or below the 90th percentile of human texts of the same length, there is at most one classic tell, and the text has not overshot human writing on the other side |
| Length | `analyze --target-words N --source notes.md` | ON TARGET, UNDER or OVER; it also lists the facts of the source that the draft does not use and the sentences that are not anchored in the source |
| Growth | `sci_metrics.py growth old.md new.md` | SUBSTANCE, THIN or PADDING: whether the added words brought new content |
| Fact ledger | `fact_ledger.py source.md draft.md` | Numbers compared by value, citations, names and protected terms; the counts of hedges, boosters and negations; derived numbers with their arithmetic |
| Voice | `sci_metrics.py compare draft.md --ref sample.md` | Whether the draft deviates from a sample of the writer's own prose |
| Probe (optional) | `dna_probe.py split draft.md` | Which paragraphs a fresh model can predict from their first half |

Six rules outrank every metric. The meaning is fixed, and nothing is invented: no name, no number, no source, no anecdote. A length is met with substance or not at all, and no metric is ever gamed. The writer's own voice beats the defaults. Finally, because the scores describe prose, they are never evidence about who wrote a text.

### Length without padding

Filler is usually born at the word count, so the skill counts the material before it writes. In one example, a summary of 89 words had to grow to about 300; the trial notes behind it held 151 words. In the longer version, which has 285 words, every added sentence can be traced to a line of the notes or to arithmetic on their numbers ("630 m3/ha or 34% less"). There the growth check says SUBSTANCE. We then stretched the same text to 456 words with the sentences a model typically reaches for ("Water management is an increasingly important issue"). For a 450-word request, the word count alone would have accepted it, but the growth check says PADDING and the style gate fails on five classic tells. If the notes cannot carry the requested length, the skill delivers the shorter text with a list of the material that would fill the rest.

## Install

The scripts need Python 3.8 or later on the `PATH`. As they use only the standard library, there is nothing to install with pip. They make no network calls.

### Claude Code, as a plugin

```bash
claude plugin marketplace add Walid-Idrissi-Labs/SciHumanizer
claude plugin install scihumanizer@scihumanizer
```

Inside a session, the same two commands work with a leading slash (`/plugin marketplace add ...`, then `/plugin install ...`). On recent versions, a single command does both: `claude plugin install scihumanizer --marketplace Walid-Idrissi-Labs/SciHumanizer`. Later, `claude plugin update scihumanizer@scihumanizer` fetches a new release.

### Claude Code, as a skill folder

```bash
git clone https://github.com/Walid-Idrissi-Labs/SciHumanizer.git ~/.claude/skills/scihumanizer
```

After that, the skill is available in all your projects; `git pull` in that folder updates it. For one project only, clone it into `.claude/skills/scihumanizer` inside that project instead.

### Claude apps

Download `scihumanizer-skill.zip` from the [latest release](https://github.com/Walid-Idrissi-Labs/SciHumanizer/releases/latest) and upload it in the app's settings (Customize, then Skills, then "Upload a skill"). Because the checks are scripts, code execution has to be switched on. We have not tested this route yet.

### Other agents

The skill is a folder with a `SKILL.md` and some Python scripts, so any agent that can read files and run Python should be able to follow it. So far it has only been run with Claude.

### What it costs

In Claude Code, the skill's description takes about 260 tokens in every session. Once the skill is used, `SKILL.md` is loaded as well, which adds about 16,000 tokens: the file has 913 lines, well above the 500 that the skill guidelines recommend. The reference files are read only when a case calls for them. Each script run takes well under a second, so the time of a full loop goes almost entirely to the rewriting rounds.

## Use

Ask in ordinary words. The skill is picked up for requests like these:

```text
Humanize the introduction in draft.md. The facts are in abstract.md, and every claim has to stay.
Write the discussion from these results, about 700 words, for reviewers in road ecology.
Does this text sound like AI? Audit it, do not rewrite it.
Here are three pages I wrote last year. Continue chapter 2 in my voice.
Ce texte fait trop IA. Reprends-le sans changer un seul chiffre.
```

In Claude Code, the skill can also be called by name, as `/scihumanizer` (or `/scihumanizer:scihumanizer` when it was installed as a plugin).

| Mode | When | What comes back |
|---|---|---|
| Rewrite | "Humanize this", "make it sound natural", with a draft | The final text and a verification block |
| Write | A writing request in which the prose has to read as human | The final text and a verification block |
| Audit | "Does this sound like AI?", "check my text" | Findings by dimension, with sentence numbers; no rewrite |
| Match | "Continue this in my voice", with a sample of 300 words or more | Text that passes the comparison with the sample |

The reply is the text, followed by a block like this one, which belongs to the run shown above:

```text
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

Results are noticeably better when the request includes the facts (notes, an abstract, the data), the reader, the length and, if you have one, a sample of your own writing. The skill will not make up a detail to raise a score. If the brief has no names or numbers, it reports that the specificity score stays low and lists the details it would need.

## The scripts on their own

The scripts need no model, and they are useful on any draft.

```bash
python3 scripts/sci_metrics.py analyze draft.md --register scientific --sentences
python3 scripts/sci_metrics.py analyze draft.md --register general --target-words 600 --source notes.md
python3 scripts/sci_metrics.py count draft.md --target-words 600
python3 scripts/sci_metrics.py growth before.md after.md --register scientific --source notes.md
python3 scripts/sci_metrics.py compare draft.md --ref my_own_writing.md
python3 scripts/fact_ledger.py source.md draft.md --facts notes.md
```

There are three registers: `scientific`, `abstract` and `general`. The language is detected automatically, and `--lang en` or `--lang fr` forces it. An exit code of 1 means that a check failed, and with `--json` the report can be read by another program. To see what a failing report looks like, run the analyzer on one of the examples:

```bash
python3 scripts/sci_metrics.py analyze examples/A-rewrite-introduction-en/source.md --register scientific
```

With two folders of at least 20 texts each, you can calibrate a register of your own (a field, a genre, another model):

```bash
python3 scripts/sci_metrics.py calibrate --human my_human_texts/ --ai my_ai_texts/ --register law --base scientific
```

## What was measured

The table gives the share of unedited AI texts that pass the whole gate, by length. Each text was scored with bands that it had not helped to set.

| Register | 150 words | 200 | 300 | 450 | 600 | 750 | 900 | Human texts that pass |
|---|---|---|---|---|---|---|---|---|
| English scientific | 2% | 2% | 0% | 0% | 0% | 0% | 0% | 84–87% |
| English abstract | 0% | 0% | 0% | | | | | 85–86% |
| English general | 12% | 10% | 8% | 7% | 4% | 3% | 4% | 87–88% |
| French scientific | 5% | 2% | 2% | 0% | 0% | 0% | 0% | 84–86% |
| French abstract | 5% | 2% | 0% | | | | | 85–87% |
| French general | 22% | 15% | 8% | 5% | 2% | 2% | 0% | 85–88% |

Three things can be read from it. First, about one human text in seven fails. As the gate asks for the central range of human writing, a failure says nothing about who wrote a text. Second, short general prose is clearly the weak point: at 150 words, one unedited AI text in eight gets through in English, one in five in French. Third, we rebuilt the gate without one of the two models before applying it to that model's texts. It still rejected 96 to 99% of the scientific ones and 68 to 98% of the general ones, which is some evidence, though not proof, that the gate is not tuned to one model.

We made three further checks. All 23 AI texts that had been kept out of the calibration fail, with composites from 0.77 to 1.82. Long human documents, which are scored in windows, pass in 86 to 91% of cases, whereas none of the long documents assembled from AI texts does. Finally, the five texts written with the loop for the examples score between 0.27 and 0.54 against thresholds of 0.65 to 0.68; the unedited answers to the same requests score between 0.84 and 1.82.

The instructions were also tested on a reader that knew nothing else. Three times over, we gave a smaller model only the skill folder with two requests. After each round, we revised the instructions. In the first round, it padded a summary to 682 words, while in a French rewrite it reported a composite of 0.652 against a threshold of 0.651 as nearly passing. By the third round, it stopped at 287 words, said that the notes were used up, and copied the verdicts exactly as the scripts had printed them. What was still wrong at the end is recorded in section H of the worked example, after the account of the three rounds.

## Limits

- Only English and French are covered, in three registers. A legal brief, a poem or a product page follows other norms.
- On the AI side, the calibration rests on two tiers of one model family. Other models may deviate in directions that the gate does not weigh.
- We have not tested the skill against commercial AI detectors, and it promises nothing about them. It neither looks for provenance watermarks nor removes them.
- The scores describe prose. Since one human text in seven fails the gate, a score must never be used to accuse someone.
- Under 150 words there is no gate, because the statistics are not stable on so little text.
- The part-of-speech taggers are about 90% accurate, so their rates can be trusted for a whole document but not for a single sentence.
- The padding metrics only find candidates; the deletion test decides.
- The rules added after the third independent round have not been tested again.
- A text produced with the skill is still a text written with the help of AI. Where a journal, a university or an employer asks for that to be disclosed, the obligation is unchanged.

## How it was built

The patterns come from eleven papers on machine-generated text, its detection and its linguistic features. Ten of them were reread in full, with every quotation in the digest checked automatically against the paper's text. Because the papers give directions ("AI text has fewer proper nouns") but no usable thresholds, we measured them. Human texts from PubMed Central, arXiv, HAL, OpenEdition, The Conversation, Wikinews, Wikipedia and the Brown corpus were compared with the two models' texts at equal length. A metric counts in the gate only if it separates human from model text for at least one of the two models. Every text is scored with bands, weights and thresholds that were set without it, each threshold being the 90th percentile of the human scores at that length.

| Path | Content |
|---|---|
| `SKILL.md` | The instructions: the ground rules, the loop, the catalogue of patterns, the notes on scientific writing and on French |
| `scripts/` | The analyzer, the fact ledger, the probe, and their data (the calibration, the marker words, the two lexicons) |
| `references/` | The research digest, the formulas, the calibration report with its tables, the French catalogue, the worked example |
| `examples/` | Six runs with every draft: the sources, the unedited model answers, the final texts |
| `evals/` | Nine test requests with their input files |
| `calibration/` | The tools that fetch the corpora, measure them and rebuild the data files, with their reports |
| `tests/` | The test suite, which also holds this README to its own gate |

To rebuild the calibration, or to add a model or a language, start with [`calibration/README.md`](calibration/README.md). The measurements behind the shipped data are attached to each release, so the calibration step can be repeated without fetching a single corpus.

## Sources

Section 10 of the research digest lists the eleven papers with what the skill takes from each. Among them are the Ghostbuster detector (Verma, Tomlin and Klein, NAACL 2024), the DIPPER paraphraser (Krishna et al., NeurIPS 2023) and the watermark of Kirchenbauer et al. (ICML 2023). Two surveys carry much of the weight: one of 44 studies on the linguistic characteristics of AI text, the other a review of detection methods by Li, Hu, Liu and Xiang. For the marker words, we used the log-odds method of Monroe, Colaresi and Quinn (2008). All corpora and both lexicons are credited in [`NOTICE.md`](NOTICE.md).

## Contributing

The most useful contribution is probably a report of text that the gate judges wrongly, in either direction: human prose that fails, or model prose that passes. How to send one, and how to run the tests, is explained in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence and citation

Code and documentation are released under the [MIT licence](LICENSE). The French lexicon is derived from Lexique 3.83 and UD_French-GSD and is therefore under CC BY-SA 4.0. The English lexicon is derived from the Brown corpus; `NOTICE.md` has the details. To cite the project, use [`CITATION.cff`](CITATION.cff) or the "Cite this repository" button on GitHub.
