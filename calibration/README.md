# Rebuilding the calibration

Everything the skill knows about human and machine prose is in four data files under `scripts/data/`: the calibration (`calibration.json`), the marker words (`markers_en.json`, `markers_fr.json`) and the two lexicons. This folder holds the tools that produced them, the configuration they ran with, and the reports of the last run. With the measurement files of a release, you can repeat the calibration in a few minutes and check that it gives the shipped file byte for byte. With the corpora, you can go further and add a model, a register or a language.

| Path | Content |
|---|---|
| `run_all.sh` | The whole pipeline in five steps; `run_all.sh 4` starts at step 4 |
| `config/` | Which sets form each register (`calibrate_<lang>.json`) and which texts the marker words are drawn from (`marker_sets_<lang>.json`) |
| `tools/` | One script per job: fetching, preparing the sets, measuring, calibrating, checking, rendering the tables of the documentation |
| `reports/` | The output of the last run: pass rates by length, marker words with their held-out validation, the two design experiments, the checks |
| `workspace/` | Corpora, text sets and measurements. It is not in git. Set `SCIHUMANIZER_WORKSPACE` to keep it somewhere else |

The tools use the Python standard library only, and they import the analyzer from `scripts/`, so the calibration and the shipped gate cannot drift apart.

## The short way: from the released measurements

Each release has two files attached, `measurements_en.jsonl.gz` and `measurements_fr.jsonl.gz`. A row holds the metric values of one text at one length, with the name of the set it belongs to and the identifier of the source document. There is no running text in them.

```bash
mkdir -p calibration/workspace/runs && cd calibration/workspace/runs
curl -LO https://github.com/Walid-Idrissi-Labs/SciHumanizer/releases/latest/download/measurements_en.jsonl.gz
curl -LO https://github.com/Walid-Idrissi-Labs/SciHumanizer/releases/latest/download/measurements_fr.jsonl.gz
gunzip measurements_en.jsonl.gz measurements_fr.jsonl.gz
cd ../../..
sh calibration/run_all.sh 4
git status --short scripts/data calibration/reports
```

Step 4 selects the metrics, sets the bands, weights and thresholds, and scores every text out of fold. It writes `scripts/data/calibration.json` and the two reports `reports/calibration_<lang>.txt`. The last command should print nothing: the procedure has no hidden randomness, and two runs on the same measurements give the same bytes (checked with Python 3.8, 3.9 and 3.14). Step 5 is skipped, because it needs the texts.

## The long way: from the sources

The texts themselves are not redistributed (see `NOTICE.md`), so the long way starts with fetching them. A fresh fetch will not return exactly the corpus that was used: several sources are sampled at random, and Wikipedia, Wikinews and The Conversation change. Expect bands that differ in the second decimal.

### 1. Fetch the human texts

The fetch tools pause between requests and cache every answer under `workspace/corpora/`, so an interrupted run continues where it stopped. `fetch_corpora.py` names a contact address in its requests and refuses to run without one. Read the terms of each source before you fetch from it. The arguments below give corpora of about the size that was used; the exact counts are in `references/calibration.md`, section 1.

```bash
export SCIHUMANIZER_CONTACT="you@example.org"
python3 calibration/tools/fetch_pmc.py 6                       # English PubMed Central, 6 articles for each of 14 topics
python3 calibration/tools/fetch_arxiv.py                       # arXiv abstracts, 10 categories
python3 calibration/tools/fetch_corpora.py conversation 2200   # The Conversation: 2,200 article ids sampled, English and French kept
python3 calibration/tools/fetch_corpora.py wikinews en 130
python3 calibration/tools/fetch_corpora.py wikinews fr 95
python3 calibration/tools/fetch_corpora.py wikipedia en 110
python3 calibration/tools/fetch_corpora.py wikipedia fr 110
python3 calibration/tools/fetch_corpora.py openedition 150     # French journal articles with their abstracts
python3 calibration/tools/fetch_corpora.py hal 170             # French abstracts, spread over 11 domains
python3 calibration/tools/fetch_corpora.py pmcfr 87            # French PubMed Central articles
```

Three resources are downloaded by hand:

- the Brown corpus (`brown.zip` from the NLTK data repository), unpacked into `workspace/corpora/brown/`;
- `Lexique383.tsv` from <http://www.lexique.org>, placed in `workspace/fr/lex/`;
- the three `fr_gsd-ud-*.conllu` files of UD_French-GSD, placed in the same folder.

Then build the plain-text Brown corpus and the two lexicons:

```bash
python3 calibration/tools/build_brown.py          # workspace/corpora/brown_txt/, workspace/en_lexicon.tsv, a held-out test set
python3 calibration/tools/build_fr_lexicon.py     # workspace/fr/fr_lexicon.tsv
```

Both lexicons are written to the workspace. Copy them over the files in `scripts/data/` only if you mean to change them. `eval_en_tagger.py` and `eval_fr_tagger.py` measure the accuracy of the two taggers on sentences that the lexicons have not seen (`reports/tagger_<lang>.txt`; 91% for English and 90.5% for French in the last run).

### 2. Build the human sets and the prompts

```bash
python3 calibration/tools/prep_sets_1.py           # English sets from PubMed Central, arXiv and Brown; prompts_1.json
python3 calibration/tools/prep_sets_2.py corpora   # French sets, modern English general prose, long documents
python3 calibration/tools/prep_sets_2.py prompts   # prompts_2.json
```

The prompt files hold ordinary requests on the topics of the human texts, with no instruction about style: "I'm writing a research paper titled ... Here is the abstract: ... Please draft the Introduction section (about 700 words)". Both scripts leave an existing prompt file alone, since the generated texts depend on it. A prompt file built after further fetching would draw other titles from The Conversation.

### 3. Generate the AI texts

Give every prompt to the model you want to calibrate against, in a fresh conversation and without a system prompt, and save each answer as `<prompt id>.txt`. The shipped calibration uses two model tiers, and `run_all.sh` expects their answers in these folders of the workspace:

| Prompts | First tier | Second tier |
|---|---|---|
| `prompts_1.json`, register `scientific`, `abstract` or `general` | `calib/ai/<register>/` | `calib/ai_haiku/<register>/` |
| `prompts_1.json`, the four `test_` prompts | `ai_test_baseline/` | `ai_test_baseline_haiku/` |
| `prompts_2.json`, English | `calib/ai/general_modern/` | `calib/ai_haiku/general_modern/` |
| `prompts_2.json`, French, by register | `calib/fr/ai_sonnet/<register>/` | `calib/fr/ai_haiku/<register>/` |
| `prompts_2.json`, the four `test_fr_` prompts | `ai_test_fr/sonnet/` | `ai_test_fr/haiku/` |

The `test_` answers take no part in the calibration. They are the texts that step 5 scores as a check, together with a few more in `calib/ai_haiku_extra/general/` (any AI texts on topics of your own will do there).

### 4. Run the pipeline

```bash
sh calibration/run_all.sh
```

| Step | What it does | Output |
|---|---|---|
| 1 | Rebuilds the human sets from the corpora | `workspace/calib/` |
| 2 | Selects the marker words by log-odds with an informative prior and validates them by cross-fitting | `scripts/data/markers_<lang>.json`, `reports/markers_<lang>.txt` |
| 3 | Measures every text in windows of 150 to 900 words | `workspace/runs/measurements_<lang>.jsonl` |
| 4 | Calibrates each register and scores every text out of fold | `scripts/data/calibration.json`, `reports/calibration_<lang>.txt` |
| 5 | Scores long human documents and the AI texts kept out of the calibration | `reports/long_documents.txt`, `reports/heldout_ai_texts.txt` |

The whole run takes about ten minutes on a laptop. Afterwards, refresh the tables of the documentation from the new file instead of editing numbers by hand:

```bash
python3 calibration/tools/render_tables.py power        # pass rates by length (SKILL.md, references/calibration.md)
python3 calibration/tools/render_tables.py fingerprint en
python3 calibration/tools/render_tables.py full en      # references/calibration-tables.md
python3 -m unittest discover -s tests                   # the examples must still score as documented
```

## The experiments behind two design choices

`vocab_experiment.py` compares vocabulary estimators on three counts: how well each separates human from AI text at equal length, how reliable it is between two halves of the same text, and how much it drifts with length. It is the reason the gate measures variety on lemmas at fixed sample sizes. `composite_experiment.py` compares six ways of combining the dimension scores at a fixed human pass rate; the per-tier weighted mean that the gate uses is variant `f`. Their outputs are in `reports/`, and `references/calibration.md` (section 5) discusses them.

```bash
python3 calibration/tools/vocab_experiment.py > calibration/reports/vocab_experiment_en.txt
python3 calibration/tools/vocab_experiment.py fr > calibration/reports/vocab_experiment_fr.txt
python3 calibration/tools/composite_experiment.py calibration/config/calibrate_en.json > calibration/reports/composite_experiment_en.txt
```

## Adding a model, a register or a language

A new model is the simplest case. Generate its answers to the same prompts, put them in folders of their own, add the folders to `run_all.sh` (steps 2, 3 and 5), and add the tier to the `ai` entry of each register in `config/calibrate_<lang>.json` and to `config/marker_sets_<lang>.json`. The analyzer then reports which profile a draft leans toward. A model that writes very differently from the two shipped tiers will also change which metrics are scored, so read the new `reports/calibration_<lang>.txt` before you trust the gate.

For a register of your own, the quick route needs no workspace at all: `sci_metrics.py calibrate --human DIR --ai DIR --register NAME --base scientific` builds bands from two folders of at least 20 texts each. It cuts every text to one length and does not cross-validate, so its pass rates are optimistic by a few points. For a register with bands at every length and out-of-fold thresholds, add its sets to `run_all.sh` and to the two configuration files, as for a model.

A new language needs more: a language pack next to `scripts/lang_en.py` and `scripts/lang_fr.py` (word lists, a lemma and part-of-speech lexicon, the rules for numbers and typography), human texts dated before 2020 in each register, and AI texts on the same topics. `references/french.md` shows what the French pack had to settle.
