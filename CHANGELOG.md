# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[semantic versioning](https://semver.org/).

## [2.0.0] - 2026-10-10

First public release.

### Added

- French: the analyzer, the fact ledger and the calibration handle French directly (elisions, a
  lemma and part-of-speech lexicon, decimal commas and spaced thousands, typography checks), with
  bands for the same three registers. `references/french.md` holds the French catalogue.
- A modern English general corpus (The Conversation, Wikinews, Wikipedia, 2012–2019) next to the
  Brown texts of 1961.
- Length rules: the material is counted before writing, and a length that the source cannot carry
  is reported instead of filled. `analyze --source` lists the facts of the source that a draft does
  not use and the sentences that are not anchored in it. The new `growth` command says whether a
  longer version added content (SUBSTANCE, THIN or PADDING).
- `count`: one word count shared by every script and every rule.
- An over-correction limit, so that a text which overshoots human writing on the far side fails.
- Derived numbers in the fact ledger: a number absent from the source is accepted when it is
  arithmetic on source numbers that stand in the same paragraph, and the formula is printed.
- Six worked examples with every draft (`examples/`), nine eval requests, a test suite, and the
  calibration tools with their reports (`calibration/`).
- Packaging as a plugin with its own marketplace entry.

### Changed

- Every metric is now compared at equal length. Texts are measured in windows of 150 to 900 words,
  and bands, weights and thresholds are set separately for each length.
- Vocabulary is measured on lemmas at fixed sample sizes, with exact estimators
  (`scripts/lexstats.py`), because the earlier measures drifted with text length.
- The composite score is the weighted mean of the dimension scores for each calibrated model
  profile, and the larger value counts. It replaces an unweighted root mean square. Thresholds come
  from out-of-fold human scores.
- Marker words are selected from the calibration corpora by log-odds with an informative prior and
  validated on held-out texts. The hand-written marker lists are gone.
- The research digest was rewritten from the papers themselves. Eleven points of the first version
  did not survive that reading; they are listed in its section 11.
- The scripts read UTF-8 with or without a byte-order mark, fall back to Windows-1252, and no
  longer fail on consoles that cannot print accented characters.

### Removed

- `scripts/lexicons.py`, replaced by `textcore.py`, `lang_en.py` and `lang_fr.py`.

## [1.0.0] - 2026-09-26

Not published. English only: the instructions, the analyzer with one set of bands per register,
the fact ledger and the continuation probe, calibrated on PubMed Central, arXiv and Brown texts.

[2.0.0]: https://github.com/Walid-Idrissi-Labs/SciHumanizer/releases/tag/v2.0.0
