#!/usr/bin/env python3
"""Score AI texts that took no part in the calibration, with the shipped gate.

  validate_heldout.py lang.register=PATH[,PATH...] ...

A PATH is a folder of .txt files or a file pattern. Prints one line per text (words, composite,
threshold, classic violations, verdict), then how many texts pass and the range of the composites.
"""
import glob, os, sys
import paths  # noqa: F401  (puts the skill's scripts on sys.path)
import sci_metrics as S

calib = S.load_calibration()
comps, passed = [], 0
for spec in sys.argv[1:]:
    key, rest = spec.split("=", 1)
    lang, register = key.split(".")
    files = []
    for item in rest.split(","):
        files += sorted(glob.glob(os.path.join(item, "*.txt")) if os.path.isdir(item) else glob.glob(item))
    for fp in files:
        doc, m = S.analyze_text(open(fp, encoding="utf-8").read(), lang=lang)
        ev = S.score(doc, m, calib, register)
        if ev is None:
            print("%-14s %-48s too short for the gate" % (key, fp))
            continue
        comps.append(ev["composite"])
        passed += ev["gate_pass"]
        print("%-14s %-48s %4d words  composite %.2f  threshold %.2f  classic %d  %s" % (
            key, fp, m["words"], ev["composite"], ev["composite_threshold"], len(ev["classic_violations"]),
            "PASS" if ev["gate_pass"] else "FAIL"))
if comps:
    print("%d texts, %d pass the gate; composites %.2f to %.2f" % (len(comps), passed, min(comps), max(comps)))
