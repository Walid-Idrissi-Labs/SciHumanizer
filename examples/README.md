# Examples

These are the six runs that `references/worked-example.md` walks through, with every draft. The studies in them do not exist: the heat and hospital admissions study, the bat sensors, the irrigation trial and their figures were invented as test material. The "unedited" files are what two models answered to the same request without the skill, and they are kept for comparison.

| Folder | Request | Unedited AI text | Final text | Threshold |
|---|---|---|---|---|
| `A-rewrite-introduction-en` | Humanize an AI-drafted Introduction; the facts are in the abstract | 1.57 (`source.md`) | 0.54 | 0.67 |
| `B-lengthen-summary-en` | Lengthen an 89-word summary to about 300 words from trial notes, without filler | | 0.29 (`draft_v2.md`) | 0.65 |
| `C-write-discussion-en` | Write a Discussion of about 700 words from a brief | 1.48 and 1.82 | 0.42 | 0.67 |
| `D-rewrite-introduction-fr` | The same Introduction as A, in French | 1.13 (`source.md`) | 0.27 | 0.65 |
| `E-write-tribune-fr` | Write a French op-ed of about 600 words | 0.84 and 0.98 | 0.37 | 0.68 |
| `F-write-column-en` | Write an English column of about 600 words | 1.11 and 1.57 | 0.37 | 0.68 |

The numbers are composite scores; a text passes the gate at or below the threshold for its length. In each folder, `final.md` is a copy of the last draft.

## What to look at

- In A, `draft_v1.md` passes the gate with the lowest composite of the five drafts (0.24) and is the worst text: lay words for the field's terms, and 872 words where 630 to 770 were allowed. Drafts 4 and 5 restore the register.
- In B, `padded.md` stretches the 285 words of `draft_v2.md` to 456 with the sentences a model reaches for. The word count is on target for a 450-word request, the growth check says PADDING, and the gate fails on five classic tells.
- In E, `draft_v1.md` has a composite well under the threshold (0.48) and still fails, because it overshoots human writing on the far side (over-correction 1.50 against a limit of 1.37).
- In F, the brief has no facts at all. The final text passes, the growth check says THIN, and the verification block reported it.

## Reproducing the numbers

Run the commands from the repository root.

```bash
S=scripts; A=examples/A-rewrite-introduction-en; B=examples/B-lengthen-summary-en

python3 $S/sci_metrics.py analyze $A/source.md --register scientific --sentences
python3 $S/sci_metrics.py analyze $A/final.md --register scientific --target-words 700
python3 $S/fact_ledger.py $A/source.md $A/final.md --facts $A/user_facts.md

python3 $S/sci_metrics.py analyze $B/summary.md --register scientific --target-words 300 --source $B/notes.md
python3 $S/sci_metrics.py growth $B/summary.md $B/draft_v2.md --register scientific --source $B/notes.md
python3 $S/sci_metrics.py growth $B/draft_v2.md $B/padded.md --register scientific --source $B/notes.md
python3 $S/fact_ledger.py $B/summary.md $B/draft_v2.md --facts $B/notes.md

python3 $S/sci_metrics.py analyze examples/D-rewrite-introduction-fr/final.md --register scientific
python3 $S/sci_metrics.py analyze examples/E-write-tribune-fr/draft_v1.md --register general
python3 $S/fact_ledger.py examples/C-write-discussion-en/brief.md examples/C-write-discussion-en/final.md --write
```

The registers are `scientific` for A to D and `general` for E and F. The same checks run in CI (`tests/test_skill.py`), so a change to the scripts or to the calibration that moves one of these scores is noticed.
