## What changes

## Evidence

<!-- For a rule or a number: the measurement, paper or test run behind it. For code: the case that failed before. -->

## Checks

- [ ] `python3 -m unittest discover -s tests` passes
- [ ] No number in the documentation was edited by hand (tables come from `calibration/tools/render_tables.py`)
- [ ] If the metrics changed, the calibration was rebuilt (`calibration/README.md`)
- [ ] If the README's prose changed, `python3 scripts/sci_metrics.py analyze README.md --register general` still passes
