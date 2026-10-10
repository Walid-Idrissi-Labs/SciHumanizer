#!/usr/bin/env python3
"""Check the gate on documents longer than the calibrated lengths (scored in windows).

  validate_long.py lang.register=HUMAN_LONG_DIR[:AI_DIR,AI_DIR...] ...

Human side: real long texts (1,500-2,600 words). AI side: no long AI documents exist in the corpora, so
three calibration texts of one model tier are joined into one pseudo-document; this tests the windowing
arithmetic, not a model's long-form behaviour.
"""
import glob, os, random, statistics, sys
import paths  # noqa: F401  (puts the skill's scripts on sys.path)
import sci_metrics as S, textcore as T

calib = S.load_calibration()
rng = random.Random(9)
for spec in sys.argv[1:]:
    key, rest = spec.split("=", 1)
    lang, register = key.split(".")
    hdir, _, adirs = rest.partition(":")
    res, nwin, mode = [], [], []
    for fp in sorted(glob.glob(os.path.join(hdir, "*.txt"))):
        doc, m = S.analyze_text(open(fp, encoding="utf-8").read(), lang=lang)
        ev = S.score(doc, m, calib, register)
        if ev is None:
            continue
        res.append(ev["gate_pass"])
        mode.append(ev["mode"])
        nwin.append(len(ev.get("windows", [])) or 1)
    print("%s human long texts: n=%d, scored in windows: %d, windows per text median %s, PASS %.0f%%" % (
        key, len(res), mode.count("windows"), statistics.median(nwin) if nwin else "-", 100 * statistics.mean(res) if res else 0))
    for ad in [a for a in adirs.split(",") if a]:
        files = sorted(glob.glob(os.path.join(ad, "*.txt")))
        rng.shuffle(files)
        res = []
        for i in range(0, len(files) - 2, 3):
            text = "\n\n".join(open(f, encoding="utf-8").read().strip() for f in files[i:i + 3])
            doc, m = S.analyze_text(text, lang=lang)
            ev = S.score(doc, m, calib, register)
            if ev:
                res.append(ev["gate_pass"])
        print("   AI pseudo-documents from %s: n=%d, PASS %.0f%%" % (ad, len(res), 100 * statistics.mean(res) if res else 0))
