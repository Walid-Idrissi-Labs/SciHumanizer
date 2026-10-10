"""Checks for the repository. Standard library only.

    python -m unittest discover -s tests -v

They cover the scripts' own self-tests, the shipped data files, the command-line tools on the
worked examples (the verdicts and composites stated in references/worked-example.md), input and
output encodings, and the README, which is held to the style gate it describes.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")
EXAMPLES = os.path.join(REPO, "examples")
TOLERANCE = 0.002


def run(script, *args, **kw):
    env = dict(os.environ)
    env.update(kw.get("env", {}))
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args), cwd=REPO, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def ex(*parts):
    return os.path.join(EXAMPLES, *parts)


def gate(path, register, *extra):
    code, out, err = run("sci_metrics.py", "analyze", path, "--register", register, "--json", *extra)
    assert out.strip(), err
    return json.loads(out)


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as fh:
        return fh.read()


class SelfTests(unittest.TestCase):
    def test_analyzer_selftest(self):
        code, out, err = run("sci_metrics.py", "selftest")
        self.assertEqual(code, 0, out[-2000:] + err)
        self.assertIn("all checks passed", out)

    def test_vocabulary_formulas(self):
        code, out, err = run("lexstats.py")
        self.assertEqual(code, 0, out[-2000:] + err)


class Data(unittest.TestCase):
    def test_calibration_has_six_registers(self):
        calib = json.loads(read("scripts", "data", "calibration.json"))
        self.assertEqual(sorted(calib["registers"]), ["en.abstract", "en.general", "en.scientific",
                                                      "fr.abstract", "fr.general", "fr.scientific"])
        for name, reg in calib["registers"].items():
            self.assertEqual(sorted(reg["n_ai"]), ["Haiku tier", "Sonnet tier"], name)
            for length, threshold in reg["composite"]["threshold"].items():
                self.assertTrue(0.5 < threshold < 0.9, (name, length, threshold))

    def test_marker_lists(self):
        for lang, glue in (("en", ["the", "of", "be", "to", "in"]), ("fr", ["être", "en", "avoir", "dans"])):
            markers = json.loads(read("scripts", "data", "markers_%s.json" % lang))
            self.assertEqual(markers["glue"], glue)
            self.assertTrue(markers["ai_content"])

    def test_json_files_parse(self):
        for parts in ((".claude-plugin", "plugin.json"), (".claude-plugin", "marketplace.json"), ("evals", "evals.json"),
                      ("calibration", "config", "calibrate_en.json"), ("calibration", "config", "calibrate_fr.json"),
                      ("calibration", "config", "marker_sets_en.json"), ("calibration", "config", "marker_sets_fr.json")):
            json.loads(read(*parts))

    def test_eval_files_exist(self):
        for case in json.loads(read("evals", "evals.json"))["evals"]:
            for f in case.get("files", []):
                self.assertTrue(os.path.exists(os.path.join(REPO, "evals", f)) or os.path.exists(os.path.join(REPO, f)), f)


class Packaging(unittest.TestCase):
    def test_skill_frontmatter(self):
        text = read("SKILL.md")
        m = re.match(r"---\n(.*?)\n---\n", text, flags=re.S)
        self.assertTrue(m)
        front = m.group(1)
        self.assertRegex(front, r"(?m)^name: scihumanizer$")
        desc = " ".join(line.strip() for line in front.split("description: >-\n", 1)[1].split("\n"))
        self.assertLessEqual(len(desc), 1024)

    def test_versions_agree(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))
        self.assertEqual(plugin["name"], "scihumanizer")
        version = plugin["version"]
        self.assertRegex(read("CITATION.cff"), r"(?m)^version: \"?%s\"?$" % re.escape(version))
        self.assertRegex(read("CHANGELOG.md"), r"(?m)^## \[?%s\]?" % re.escape(version))

    def test_files_named_in_skill_exist(self):
        text = read("SKILL.md")
        table = text[text.index("## Files"):]
        for name in re.findall(r"`((?:scripts|references|evals)/[A-Za-z0-9_./-]+)`", table):
            self.assertTrue(os.path.exists(os.path.join(REPO, name)), name)

    def test_everything_compiles(self):
        for folder in ("scripts", os.path.join("calibration", "tools"), "tests"):
            for name in sorted(os.listdir(os.path.join(REPO, folder))):
                if name.endswith(".py"):
                    compile(read(folder, name), name, "exec")


class Examples(unittest.TestCase):
    """The six cases of references/worked-example.md."""

    FINAL = [   # folder, register, composite
        ("A-rewrite-introduction-en", "scientific", 0.539),
        ("B-lengthen-summary-en", "scientific", 0.288),
        ("C-write-discussion-en", "scientific", 0.424),
        ("D-rewrite-introduction-fr", "scientific", 0.269),
        ("E-write-tribune-fr", "general", 0.369),
        ("F-write-column-en", "general", 0.374),
    ]
    UNEDITED = [    # file, register, composite
        (("A-rewrite-introduction-en", "source.md"), "scientific", 1.574),
        (("C-write-discussion-en", "unedited_larger_model.md"), "scientific", 1.477),
        (("C-write-discussion-en", "unedited_smaller_model.md"), "scientific", 1.818),
        (("D-rewrite-introduction-fr", "source.md"), "scientific", 1.134),
        (("E-write-tribune-fr", "unedited_larger_model.md"), "general", 0.844),
        (("E-write-tribune-fr", "unedited_smaller_model.md"), "general", 0.980),
        (("F-write-column-en", "unedited_larger_model.md"), "general", 1.108),
        (("F-write-column-en", "unedited_smaller_model.md"), "general", 1.572),
    ]

    def test_final_texts_pass(self):
        for folder, register, composite in self.FINAL:
            name = "draft_v2.md" if folder.startswith("B-") else "final.md"
            ev = gate(ex(folder, name), register)["evaluation"]
            self.assertTrue(ev["gate_pass"], folder)
            self.assertAlmostEqual(ev["composite"], composite, delta=TOLERANCE, msg=folder)
            self.assertLessEqual(ev["composite"], ev["composite_threshold"], folder)
            self.assertLessEqual(ev["overcorrection"], ev["overcorrection_limit"], folder)

    def test_unedited_texts_fail(self):
        for parts, register, composite in self.UNEDITED:
            ev = gate(ex(*parts), register)["evaluation"]
            self.assertFalse(ev["gate_pass"], parts)
            self.assertAlmostEqual(ev["composite"], composite, delta=TOLERANCE, msg=parts)

    def test_overshoot_fails_on_the_far_side(self):
        ev = gate(ex("E-write-tribune-fr", "draft_v1.md"), "general")["evaluation"]
        self.assertLess(ev["composite"], ev["composite_threshold"])
        self.assertGreater(ev["overcorrection"], ev["overcorrection_limit"])
        self.assertFalse(ev["gate_pass"])

    def test_padded_text_fails_on_classic_tells(self):
        ev = gate(ex("B-lengthen-summary-en", "padded.md"), "scientific")["evaluation"]
        self.assertLess(ev["composite"], ev["composite_threshold"])
        self.assertEqual(len(ev["classic_violations"]), 5)
        self.assertFalse(ev["gate_pass"])

    def test_growth_verdicts(self):
        b = "B-lengthen-summary-en"
        for old, new, extra, verdict, code in (
                (ex(b, "summary.md"), ex(b, "draft_v2.md"), ["--register", "scientific", "--source", ex(b, "notes.md")], "SUBSTANCE", 0),
                (ex(b, "draft_v2.md"), ex(b, "padded.md"), ["--register", "scientific", "--source", ex(b, "notes.md")], "PADDING", 1),
                (ex("F-write-column-en", "draft_v1.md"), ex("F-write-column-en", "final.md"), ["--register", "general"], "THIN", None)):
            rc, out, err = run("sci_metrics.py", "growth", old, new, "--json", *extra)
            self.assertEqual(json.loads(out)["status"], verdict, new)
            if code is not None:
                self.assertEqual(rc, code, new)

    def test_length_check(self):
        b = "B-lengthen-summary-en"
        length = gate(ex(b, "summary.md"), "scientific", "--target-words", "300", "--source", ex(b, "notes.md"))["length"]
        self.assertEqual(length["words"], 89)
        self.assertEqual(length["status"], "UNDER")
        length = gate(ex(b, "draft_v2.md"), "scientific", "--target-words", "300", "--source", ex(b, "notes.md"))["length"]
        self.assertEqual(length["words"], 285)
        self.assertEqual(length["status"], "ON TARGET")

    def test_fact_ledger(self):
        a, b, c, d = "A-rewrite-introduction-en", "B-lengthen-summary-en", "C-write-discussion-en", "D-rewrite-introduction-fr"
        for args in ((ex(a, "source.md"), ex(a, "final.md"), "--facts", ex(a, "user_facts.md")),
                     (ex(b, "summary.md"), ex(b, "draft_v2.md"), "--facts", ex(b, "notes.md")),
                     (ex(c, "brief.md"), ex(c, "final.md"), "--write"),
                     (ex(d, "source.md"), ex(d, "final.md"), "--facts", ex(d, "user_facts.md")),
                     (ex("E-write-tribune-fr", "brief.md"), ex("E-write-tribune-fr", "final.md"), "--write"),
                     (ex("F-write-column-en", "brief.md"), ex("F-write-column-en", "final.md"), "--write")):
            rc, out, err = run("fact_ledger.py", *args)
            self.assertEqual(rc, 0, out[:600])
            self.assertIn("verdict: OK", out)
        rc, out, err = run("fact_ledger.py", ex(b, "summary.md"), ex(b, "draft_v2.md"), "--facts", ex(b, "notes.md"))
        self.assertIn("630 = 1840 - 1210", out)
        rc, out, err = run("fact_ledger.py", ex(c, "brief.md"), ex(c, "final.md"), "--write")
        self.assertIn("1710 = 38 x 45", out)

    def test_ledger_catches_a_changed_number(self):
        a = "A-rewrite-introduction-en"
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.md")
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(read("examples", a, "final.md").replace("1.9 million", "2.9 million"))
            rc, out, err = run("fact_ledger.py", ex(a, "source.md"), bad, "--facts", ex(a, "user_facts.md"))
        self.assertEqual(rc, 1, out[:600])


class Encodings(unittest.TestCase):
    def test_ascii_console_and_legacy_file(self):
        text = read("examples", "D-rewrite-introduction-fr", "final.md")
        with tempfile.TemporaryDirectory() as tmp:
            legacy = os.path.join(tmp, "cp1252.md")
            with open(legacy, "wb") as fh:
                fh.write(text.encode("cp1252", "replace"))
            bom = os.path.join(tmp, "bom.md")
            with open(bom, "wb") as fh:
                fh.write(b"\xef\xbb\xbf" + text.encode("utf-8"))
            for path in (legacy, bom):
                rc, out, err = run("sci_metrics.py", "analyze", path, "--register", "scientific",
                                   env={"PYTHONIOENCODING": "ascii"})
                self.assertIn(rc, (0, 1), err[-800:])
                self.assertIn("Style gate", out)
                self.assertNotIn("Traceback", err)


class Readme(unittest.TestCase):
    def test_readme_passes_its_own_gate(self):
        for name, register in (("README.md", "general"), ("README.fr.md", "general")):
            ev = gate(os.path.join(REPO, name), register)["evaluation"]
            self.assertTrue(ev["gate_pass"], "%s: composite %.3f against %.3f, classic %s, over-correction %.2f (limit %.2f)" % (
                name, ev["composite"], ev["composite_threshold"], ev["classic_violations"],
                ev["overcorrection"], ev["overcorrection_limit"]))


if __name__ == "__main__":
    unittest.main()
