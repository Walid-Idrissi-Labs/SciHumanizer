#!/usr/bin/env python3
"""Render calibration.json as markdown tables for SKILL.md and references/calibration.md.

  render_tables.py power|compact|fingerprint|full|growth [lang]
"""
import json, os, sys

from paths import DATA
C = json.load(open(os.path.join(DATA, "calibration.json"), encoding="utf-8"))
REF = {"scientific": 450, "abstract": 200, "general": 450}


def f(x):
    if x is None:
        return "-"
    ax = abs(x)
    if ax >= 100:
        return "%.0f" % x
    if ax >= 10:
        return "%.1f" % x
    if ax >= 1:
        return "%.2f" % x
    return "%.3f" % x


def regs(lang):
    return [(k, v) for k, v in C["registers"].items() if lang is None or k.startswith(lang + ".")]


def ref_len(name, reg):
    want = REF.get(name.split(".")[1], 450)
    return str(min(reg["lengths"], key=lambda L: abs(L - want)))


def sep(sp):
    return max([max(u, 1 - u) for u in sp["auc"].values()] or [0.5])


def power(lang):
    out = []
    for name, reg in regs(lang):
        tiers = list(reg["n_ai"])
        out.append("**%s** (human texts: %d; AI texts: %s)\n" % (name, reg["n_human"], ", ".join("%s %d" % kv for kv in reg["n_ai"].items())))
        out.append("| Words | Threshold | Human texts passing | AI texts passing | " + " | ".join(tiers) + " |")
        out.append("|---|---|---|---|" + "---|" * len(tiers))
        for L in reg["lengths"]:
            p = reg["power"].get(str(L))
            if not p:
                continue
            out.append("| %d | %.2f | %.0f%% | %.0f%% | %s |" % (L, reg["composite"]["threshold"][str(L)], 100 * p["human_pass"], 100 * p["ai_pass"],
                       " | ".join("%.0f%%" % (100 * p["ai_pass " + t]) if ("ai_pass " + t) in p else "-" for t in tiers)))
        v = reg["validation"]
        if v.get("leave_one_tier_out_ai_pass"):
            out.append("\nGate rebuilt without one tier, applied to that tier: " + "; ".join("%s %.0f%% pass" % (t, 100 * x) for t, x in v["leave_one_tier_out_ai_pass"].items() if x is not None) + ".")
        if v.get("extra_human_pass"):
            out.append("Other human corpora: " + "; ".join("%s %.0f%% pass" % (t, 100 * x) for t, x in v["extra_human_pass"].items()) + ".")
        out.append("")
    return "\n".join(out)


def compact(lang, n=12):
    out = []
    for name, reg in regs(lang):
        L = ref_len(name, reg)
        tiers = list(reg["n_ai"])
        out.append("**%s**, at %s words\n" % (name, L))
        out.append("| Metric | Human median [p10–p90] | " + " | ".join(tiers) + " | AI is | Separation |")
        out.append("|---|---|" + "---|" * len(tiers) + "---|---|")
        rows = sorted([(k, v) for k, v in reg["metrics"].items() if v["gate"] and L in v["bands"]], key=lambda kv: -sep(kv[1]))
        for k, v in rows[:n]:
            h = v["bands"][L]
            out.append("| %s | %s [%s–%s] | %s | %s | %.2f |" % (
                v["label"], f(h["p50"]), f(h["p10"]), f(h["p90"]),
                " | ".join(f(v["ai_p50"].get(t, {}).get(L)) for t in tiers),
                {1: "higher", -1: "lower", 0: "off both ways"}[v["ai_direction"]], sep(v)))
        out.append("")
    return "\n".join(out)


FP = [("rhythm.sent_len_mean", "Mean sentence length (words)"), ("rhythm.sent_len_cv", "Sentence-length variation (CV)"),
      ("punctuation.comma_per_sentence", "Commas per sentence"), ("paragraphs.para_words_cv", "Paragraph-length variation (CV)"),
      ("lexical.glue_per100", "Glue words per 100 tokens"), ("pos.lexical_density", "Lexical density"),
      ("lexical.mattr50", "Word variety (MATTR-50)"), ("lexical.content_mattr25", "Content-word variety (MATTR-25)"),
      ("lexical.word_len_mean", "Mean word length (letters)"), ("markers.ai_function_per1k", "Over-used function words per 1k"),
      ("markers.ai_content_per1k", "Over-used content words per 1k"), ("pos.specificity_pct", "Names + acronyms + numbers (% of tokens)"),
      ("punctuation.per1k.parenthesis", "Parentheses per 1k words"), ("pos.deriv_adv_pct", "Derived adverbs (% of tokens)"),
      ("pos.adj_pct", "Adjectives (% of tokens)"), ("pos.aux_pct", "Auxiliaries (% of tokens)"),
      ("nominal.nominal_heavy_share", "Sentences with >= 3 nominalisations"), ("nominal.nominalization_per1k", "Nominalisations per 1k"),
      ("padding.participial_clause_per1k", "Comment clauses after a comma per 1k"), ("padding.shell_noun_per1k", "Abstract framing nouns per 1k"),
      ("padding.wordy_per1k", "Wordy stock phrases per 1k"), ("stock.stock_per1k", "Stock phrases per 1k"),
      ("connectives.formulaic_initial_share", "Formulaic sentence openers (share)"), ("stance.self_mention_per1k", "Self-mention per 1k")]


def fingerprint(lang):
    rs = regs(lang)
    out = ["| Habit (median: human → " + " / ".join(next(iter(rs))[1]["n_ai"]) + ") | " + " | ".join("%s @%s" % (n.split(".")[1], ref_len(n, r)) for n, r in rs) + " |",
           "|---|" + "---|" * len(rs)]
    for key, label in FP:
        cells = []
        for name, reg in rs:
            L = ref_len(name, reg)
            sp = reg["metrics"].get(key)
            if not sp or L not in sp["bands"]:
                cells.append("-")
                continue
            cells.append("%s → %s" % (f(sp["bands"][L]["p50"]), " / ".join(f(sp["ai_p50"].get(t, {}).get(L)) for t in reg["n_ai"])))
        out.append("| %s | %s |" % (label, " | ".join(cells)))
    return "\n".join(out)


def full(lang):
    out = []
    for name, reg in regs(lang):
        L = ref_len(name, reg)
        tiers = list(reg["n_ai"])
        out.append("### %s (values at %s words)\n" % (name, L))
        out.append("| Metric | Dimension | Scored | Guard | AUC " + " / ".join(tiers) + " | Human p10 / p50 / p90 | AI median " + " / ".join(tiers) + " |")
        out.append("|---|---|---|---|---|---|---|")
        for k, v in sorted(reg["metrics"].items(), key=lambda kv: (-kv[1]["gate"], kv[1]["group"], -sep(kv[1]))):
            if L not in v["bands"]:
                continue
            h = v["bands"][L]
            out.append("| `%s` | %s | %s | %s | %s | %s / %s / %s | %s |" % (
                k, v["group"], {1: "AI higher", -1: "AI lower", 0: "both sides"}[v["ai_direction"]] if v["gate"] else "",
                (v.get("guard") or "") + (", classic" if v.get("classic") else "") + ("; contradicted" if v.get("conflicts_with_research") else ""),
                " / ".join("%.2f" % v["auc"][t] if t in v["auc"] else "-" for t in tiers),
                f(h["p10"]), f(h["p50"]), f(h["p90"]), " / ".join(f(v["ai_p50"].get(t, {}).get(L)) for t in tiers)))
        out.append("")
    return "\n".join(out)


def growth(lang):
    out = ["| Register | Growing from (words) | New content words per 100 added: p10 / p25 / median | New specifics per 100 added: p25 / median |", "|---|---|---|---|"]
    for name, reg in regs(lang):
        for L, g in reg.get("growth", {}).items():
            out.append("| %s | %s | %.1f / %.1f / %.1f | %.1f / %.1f |" % (name, L, g["content_p10"], g["content_p25"], g["content_p50"], g["specifics_p25"], g["specifics_p50"]))
    return "\n".join(out)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "power"
    lang = sys.argv[2] if len(sys.argv) > 2 else None
    print({"power": power, "compact": compact, "fingerprint": fingerprint, "full": full, "growth": growth}[which](lang))
