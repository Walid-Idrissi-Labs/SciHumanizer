#!/usr/bin/env python3
"""Measure every text of a corpus at several fixed lengths and write flat rows as JSONL.

  batch_metrics.py OUT.jsonl LABEL=FOLDER[:lang] ... [--lengths=150,200,300,450,600,750] [--max-windows=3]

For each text and each length L (in analysed words) the text is cut into up to --max-windows
consecutive windows of L words (whole sentences) and each window is measured, so human and AI
texts are always compared at the same length. One extra row per text holds the uncut text (_L = 0).
Rows carry _set, _file, _L, _win (0 = the start of the text).
"""
import glob, json, multiprocessing, os, sys

import paths  # noqa: F401  (puts the skill's scripts on sys.path)
import sci_metrics as S  # noqa: E402
import textcore as T  # noqa: E402

KEEP_DICTS = ("ai_fw_detail", "human_fw_detail", "initial_connectives", "stock_hits", "top_hedges", "top_attitude",
              "wordy_hits", "metadiscourse_hits", "shell_hits", "ai_vocab_hits")


def flatten(m, prefix=""):
    out = {}
    for k, v in m.items():
        key = prefix + k
        if isinstance(v, dict):
            if k in ("per1k", "opener_classes"):
                for kk, vv in v.items():
                    out[key + "." + kk] = vv
            elif k in KEEP_DICTS:
                out[key] = v
            else:
                out.update(flatten(v, key + "."))
        elif isinstance(v, (int, float, bool, str)) or v is None:
            out[key] = v
    return out


def work(job):
    fp, label, lang, lengths, max_windows = job
    text = open(fp, encoding="utf-8", errors="ignore").read()
    doc = T.Doc(text, lang)
    rows = []

    def row(d, L, win):
        r = flatten(S.metrics_of(d))
        r.update({"_file": os.path.basename(fp), "_set": label, "_L": L, "_win": win, "_doc_words": doc.n_words,
                  "_ctypes": len(S.content_types(d)), "_ftypes": len(S.fact_types(d))})
        rows.append(r)

    row(doc, 0, 0)
    for L in lengths:
        start, win = 0, 0
        while win < max_windows and start < len(doc.sentences):
            wtext, n, nxt = doc.window_text(L, start)
            if n < 0.6 * L:            # not enough text left for a window of about L words
                break
            row(T.Doc(wtext, doc.lang), L, win)
            start, win = nxt, win + 1
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = {a.split("=")[0]: a.split("=")[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
    lengths = [int(x) for x in opt.get("--lengths", "150,200,300,450,600,750").split(",")]
    maxw = int(opt.get("--max-windows", "3"))
    out = args[0]
    jobs = []
    for spec in args[1:]:
        label, folder = spec.split("=", 1)
        lang = None
        if ":" in folder:
            folder, lang = folder.rsplit(":", 1)
        fps = sorted(glob.glob(os.path.join(folder, "*.txt")) + glob.glob(os.path.join(folder, "*.md")))
        jobs += [(fp, label, lang, lengths, maxw) for fp in fps]
        print(label, len(fps), "files")
    with multiprocessing.Pool(max(1, (os.cpu_count() or 2) - 1)) as pool, open(out, "w", encoding="utf-8") as fh:
        n = 0
        for rows in pool.imap(work, jobs, chunksize=4):     # ordered, so that a rerun writes the same file
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                n += 1
    print("rows:", n, "->", out)


if __name__ == "__main__":
    main()
