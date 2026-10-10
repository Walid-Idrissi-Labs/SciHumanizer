# Contributing

Thank you for looking at this. The project is small, and a short report is as welcome as a patch.

## The most useful report: a text that the gate judges wrongly

The gate was calibrated on a limited set of corpora and on two models, so its blind spots are best found by other people's texts. Two kinds of report help:

- a human text, written before 2020 or certainly by hand, that fails the gate;
- a model's unedited answer that passes it.

Open an issue with the "Misjudged text" form and give the language, the register you used, the first lines of the report (the gate line and the dimension list) and, for an AI text, the model and the request. Paste the text only if you have the right to share it; otherwise a link or the report alone is enough. A single text proves little, since about one human text in seven fails by design. Several texts of the same kind that fail on the same dimension are a finding.

## Bugs in the scripts

Give the command, a small input that shows the problem, what you expected and what you got, together with your Python version and operating system. Wrong sentence splits, wrong lemmas and numbers that the fact ledger misreads are bugs like any other, and a three-line example is the best report.

## Changes to the instructions

`SKILL.md` and the reference files state rules and numbers. A change to a rule should come with its evidence: a measurement on a corpus, a paper, or a test run in which a model followed the old wording badly and the new wording well (section H of `references/worked-example.md` shows how such runs were reported). Numbers are never edited by hand. They come from `scripts/data/calibration.json` through `calibration/tools/render_tables.py`, or from the reports in `calibration/reports/`.

## Working on the code

There is nothing to install. The scripts and the tools use the Python standard library only, they must keep running on Python 3.8, and the scripts in `scripts/` must not open a network connection.

```bash
python3 -m unittest discover -s tests -v     # the whole suite, a few seconds
python3 scripts/sci_metrics.py selftest      # the analyzer's invariants and the vocabulary formulas
```

The suite scores the texts in `examples/` and compares the verdicts and composites with the documented ones. If your change moves one of them, either the change is wrong or the documentation has to move with it; say which in the pull request. A change to the metrics also changes the measurements, so the calibration has to be rebuilt before the numbers mean anything (`calibration/README.md`).

The README is held to the gate that it describes (`python3 scripts/sci_metrics.py analyze README.md --register general` must pass, and CI checks it). If you edit its prose, run that command first.

## New models, registers and languages

Calibrations for other models are the extension the project needs most. `calibration/README.md` explains the procedure. Please describe the corpora in the pull request (source, dates, number of texts, how the AI texts were requested), and do not add third-party texts to the repository: the tools fetch them, and only statistics are committed.

## Scope

The scores describe prose. Requests to turn the analyzer into a detector of authorship, or to tune the skill against a particular commercial detector, are outside the scope of the project.

## Licence

By contributing you agree that your contribution is released under the MIT licence of the project. Data derived from other resources must be compatible with it or carry its own notice in `NOTICE.md`, as the French lexicon does.
