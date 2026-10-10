# Notices

The code and the documentation of this repository are released under the MIT licence
(`LICENSE`). Two data files are derived from other people's resources and keep the terms of
those resources. The calibration statistics were computed on texts that are not redistributed
here.

## Data files derived from other resources

### `scripts/data/fr_lexicon.tsv`: CC BY-SA 4.0

A table of 61,425 French word forms, each with its two most likely readings (part of speech,
lemma, weight). It is built by `calibration/tools/build_fr_lexicon.py` from two sources:

- **Lexique 3.83** (New, Pallier, Brysbaert and Ferrand, 2004, "Lexique 2: A new French lexical
  database", *Behavior Research Methods, Instruments, & Computers* 36(3), 516–524;
  <http://www.lexique.org>), licensed CC BY-SA 4.0. It supplies forms, lemmas, categories and
  frequencies.
- **UD_French-GSD**, training and development parts (Universal Dependencies;
  <https://github.com/UniversalDependencies/UD_French-GSD>), licensed CC BY-SA 4.0. It supplies
  the reading each form takes most often in running text.

Both sources are share-alike, so the derived file is distributed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and not under the MIT licence.

### `scripts/data/en_lexicon.tsv`

A table of 25,318 English word forms with the counts of their two most frequent coarse parts of
speech. It is built by `calibration/tools/build_brown.py` from the tagged **Brown Corpus**
(W. N. Francis and H. Kučera, *A Standard Corpus of Present-Day Edited American English*, Brown
University, 1964; revised 1971 and 1979), in the copy distributed with NLTK data. The file
holds counts of word and tag pairs and no running text.

Two statements about the corpus's terms exist, and they are not the same. The README
distributed with the corpus says: "Distributed with the permission of the copyright holder,
redistribution permitted." The NLTK data index lists the package with the note "May be used for
non-commercial purposes." If the second statement matters for your use, rebuild the lexicon
from a tagged corpus whose terms suit you; `build_brown.py` shows the format the analyzer
reads.

## Texts used for statistics, not redistributed

`scripts/data/calibration.json` and `scripts/data/markers_<lang>.json` hold percentile bands,
weights, thresholds, pass rates and word lists. They were computed from the texts below.
`references/calibration.md` gives the counts and the method, and `calibration/README.md`
explains how to fetch the texts again.

Human text, all dated before 2020:

- PubMed Central, open-access research articles in English and in French, 2015–2019
  (Introduction and Discussion sections), through the NCBI E-utilities.
- arXiv abstracts, 2017–2019, through the arXiv API.
- The Brown Corpus, 1961 (informative genres and the "learned" category).
- The Conversation, English and French editions, 2015–2019.
- Wikinews, English and French, 2012–2019.
- Wikipedia featured articles, English and French, in their revision of 31 December 2019.
- OpenEdition Journals, French articles and abstracts in the humanities and social sciences,
  2012–2019.
- HAL, French abstracts, 2015–2019.

AI text: 308 texts written for this project by two tiers of one model family (the Sonnet and
Haiku tiers of Claude), in answer to ordinary requests on the topics of the human texts, and 23
more that were kept out of the calibration and used as a check.

The measurement files attached to the releases hold one row of numbers per text and per
length, labelled with the identifier of the source document. They contain no running text.

## Research

The patterns the skill looks for come from eleven papers on machine-generated text, its
detection and its linguistic features. They are listed, with what each contributed and what
did not survive a check against the papers themselves, in `references/research-digest.md`.
