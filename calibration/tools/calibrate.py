#!/usr/bin/env python3
"""Calibrate the SciHumanizer gate: pre-2020 human text vs current-model text, per register, per length.

  calibrate.py CONFIG.json [--write] [--md out.md] [--only en.scientific,...]

CONFIG: {"run": "runs/x.jsonl", "registers": {"en.scientific": {"human": ["H_scientific"],
         "ai": {"Sonnet tier": ["A_scientific"], "Haiku tier": ["Ah_scientific"]}, "extra_human": ["H_scibrown"]}}}

Method
  * Lengths. Every text was measured in windows of fixed length (batch_metrics.py); a length is
    calibrated when at least MIN_H human texts and MIN_A AI texts reach it. Human bands, the
    composite threshold and the dimension bands are computed separately for each length.
  * Which metrics count. For each AI model tier, AUC = P(AI value > human value) at matched length,
    averaged over lengths. A metric is gated when at least one tier separates (|AUC - 0.5| >= GAP).
    If the tiers err on opposite sides, the metric is two-sided. A research guard (the direction the
    literature documents as an AI tell) is never reversed: evidence against it only removes the metric.
  * Classic guards. Research-documented tells are checked against the extreme human range even when
    current models do not show them.
  * Composite. For each AI tier, the weighted mean of the dimension scores, the weights being that
    tier's deviation from human text on each dimension divided by the score's variance (a diagonal
    linear discriminant); the larger tier value counts. It replaced an unweighted root-mean-square,
    which let weak dimensions dilute strong ones (composite_experiment.py).
  * Thresholds and validation. Every document is scored out of fold: 5 folds by document, twice, with
    metric selection, directions, bands and weights rebuilt on the other folds. The composite threshold is the
    90th percentile of the out-of-fold human composites (so about one human text in ten fails by
    design); the dimension bands and the AI pass rates come from the same out-of-fold scores.
    Classic guards and the over-correction limit (99th percentile of the far-side score in human
    texts, never tighter than other human corpora of the register reach) fail a few more. Metrics
    whose far side is harmless (HARMLESS_FAR) are left out of the far-side score.
    Leave-one-tier-out: the whole procedure without one model tier, applied to that tier's texts.
Scoring is delegated to sci_metrics.evaluate so the shipped gate and the calibration cannot diverge.
"""
import collections, json, os, random, statistics, sys

from paths import DATA, REPO, WS
import sci_metrics as S  # noqa: E402
import textcore as T  # noqa: E402

MIN_H, MIN_A, GAP = 40, 15, 0.15

# key -> (label, fix hint)
CANDIDATES = {
    "rhythm.sent_len_mean": ("mean sentence length (words)", "Too long: split sentences that chain clauses with commas; one main idea per sentence, two at most. Too short: join clipped sentences that belong to one thought."),
    "rhythm.long_share": ("share of long sentences (>=30 words)", "Split sentences that carry three or more ideas at their logical joints (because, but, which)."),
    "rhythm.short_share": ("share of short sentences (<=10 words)", "Give a key finding or a turn in the argument its own short sentence, but do not chop every thought into fragments."),
    "punctuation.comma_per_sentence": ("commas per sentence", "Break comma-chained enumerations and clause strings; one idea per clause."),
    "rhythm.sent_len_cv": ("sentence-length variation (CV)", "Vary sentence length with the content: a short plain sentence where a point lands, a long qualified one where reasoning needs room. Break the uniform run shown under 'Where to look'."),
    "rhythm.masd_norm": ("sentence-to-sentence length change", "Alternate lengths where the content allows."),
    "rhythm.uniform_run_max": ("longest run of similar-length sentences", "Break the run: merge two of its sentences or isolate one point."),
    "paragraphs.para_words_cv": ("paragraph-length variation", "Let paragraph length follow the content: a short paragraph for a pivot or a key result, a longer one for an argument."),
    "paragraphs.para_sents_cv": ("variation in sentences per paragraph", "Same as paragraph-length variation."),
    "lexical.mattr50": ("word variety, all words (MATTR-50 on lemmas)", "Variety above the human range rarely comes from synonyms. It comes from compressed phrasing: few articles and 'of', few forms of 'be', a new content word in every slot. Write full clauses, and reuse the established term instead of a variant."),
    "lexical.mtld_wrap": ("word variety, all words (MTLD)", "Same as MATTR."),
    "lexical.types_at_100": ("distinct lemmas per 100 words (rarefied)", "Same as MATTR."),
    "lexical.yule_k": ("repeat rate (Yule's K)", "Too low means the common words are spread too thin: let 'the', 'of', 'is' and the key terms recur as they do in ordinary prose."),
    "lexical.content_types_at_50": ("content-word variety (distinct per 50 content words)", "Too high: stop rotating near-synonyms and upgraded words; name a thing once and keep the name. Too low: the same few abstract words are recycled; use the precise word for each thing."),
    "lexical.content_mattr25": ("content-word variety (MATTR-25 on content words)", "Same as content-word variety."),
    "lexical.glue_per100": ("glue words per 100 tokens", "Unpack compressed phrases into ordinary clauses: 'coastal erosion risk assessment tools' -> 'tools for assessing the risk of erosion on the coast'; 'X remains unclear' -> 'it is not clear whether X'. Use 'is/are/was' with an adjective or noun where that is the plain way to say it."),
    "pos.lexical_density": ("lexical density (content words / all words)", "The text packs too many content words per sentence. Spread the load: one claim per clause, with its articles, prepositions and auxiliaries."),
    "lexical.fw_types_at_50": ("function-word variety", "Do not rotate connectors and prepositions for variety (across, within, through, amid, beyond); the plain ones (in, of, on, for) recur in human text."),
    "lexical.word_len_mean": ("mean word length (letters)", "Prefer the short everyday word where it says the same thing: use (not utilise), show (not demonstrate), need (not necessitate), about (not approximately), help (not facilitate)."),
    "lexical.long_word_pct": ("long words (>= 9 letters, %)", "Same as mean word length."),
    "markers.ai_function_per1k": ("function words current models over-use, per 1k", "Cut or rephrase the listed words (see 'Words current models over-use'): 'how/what/whether' clauses used as abstract objects ('understanding how X shapes Y' -> 'the effect of X on Y'), 'rather than', 'across', 'through', 'despite', 'beyond', 'itself', 'yet'."),
    "markers.ai_content_per1k": ("content words current models over-use, per 1k", "Replace the listed words with the plain one a specialist would use, or drop the sentence if it only frames (see 'Words current models over-use')."),
    "markers.human_function_per1k": ("everyday function words people use more (also, as, by, there, such ...), per 1k", "Write the ordinary way: 'there is', 'such as', 'as well', 'also', 'by' after a passive, 'we' where the genre allows. Do not replace them with tighter constructions."),
    "markers.plain_per1k": ("plain workhorse words people use, per 1k", "Use the ordinary verbs and adjectives of the field: use, show, find, include, increase, lead to; high, low, new, similar, good."),
    "pos.specificity_pct": ("names + acronyms + numbers (% of tokens)", "Surface the specific names, abbreviations and numbers already in the source instead of category words ('several cities' -> 'Lyon and Turin'). Never invent."),
    "pos.propn_pct": ("proper nouns (% of tokens)", "Use the names the source provides (datasets, methods, places, authors, instruments). Never invent them."),
    "pos.num_pct": ("numbers (% of tokens)", "State the quantities the source gives (sample sizes, effect sizes, dates) where the text now says 'many', 'large', 'recent'."),
    "punctuation.punct_entropy_nodash": ("punctuation variety (dashes excluded)", "Use parentheses for abbreviations, asides and exact values; a semicolon between tightly related clauses; a colon to introduce. Not dashes."),
    "punctuation.nonbasic_share_nodash": ("share of marks other than , and . (dashes excluded)", "Same as punctuation variety."),
    "punctuation.per1k.parenthesis": ("parentheses per 1k", "Put abbreviations, units, exact values and brief asides in parentheses, as papers do."),
    "pos.deriv_adv_pct": ("derived adverbs (-ly / -ment, % of tokens)", "Cut intensifying and decorative adverbs (dramatically, increasingly, fundamentally, particularly); keep those that carry information (rarely, previously, randomly)."),
    "pos.adj_pct": ("adjectives (% of tokens)", "Cut stacked evaluative adjectives; keep the ones that classify (thermal, randomized, 1-km)."),
    "pos.verb_pct": ("lexical verbs (% of tokens)", "Too many action verbs doing abstract work (shapes, reflects, requires, enables, remains): say what is the case with 'is/are/has' or name who did what."),
    "pos.aux_pct": ("auxiliaries: be / have / do (% of tokens)", "Human prose leans on 'is', 'are', 'was', 'has been'. Let simple statements be simple: 'X is common in Y'."),
    "structure.passive_sentence_share": ("sentences with a passive", "People use the passive where the doer is unknown or beside the point ('the samples were stored at 4 °C', 'the bill was passed'). Do not force every sentence active."),
    "nominal.nominal_heavy_share": ("sentences with >=3 nominalisations", "Rewrite the listed clusters with verbs."),
    "nominal.nominalization_per1k": ("nominalisations per 1k", "Convert -tion/-ment/-ness/-ity nouns back into verbs where an actor exists."),
    "pos.noun_verb_ratio": ("noun-to-verb ratio", "Turn nominalisations back into verbs: 'the optimization of X' -> 'optimizing X'."),
    "pos.nominal_verbal_ratio": ("nominal vs verbal style", "More verbs and pronouns, fewer noun stacks."),
    "pos.of_per100": ("'of' per 100 words", "Too low is as telling as too high: human prose uses 'of' phrases freely ('the rate of loss', 'most of the samples')."),
    "padding.participial_clause_per1k": ("comment clauses after a comma (', highlighting ...') per 1k", "Cut the trailing clause or turn it into its own sentence with a subject and a finite verb that states a fact."),
    "padding.shell_noun_per1k": ("abstract framing nouns per 1k", "Replace the frame with the thing: 'plays a role in the regulation of' -> 'regulates'; 'the challenge of X' -> 'X is hard because ...'."),
    "padding.metadiscourse_per1k": ("announcements about the text per 1k", "Say the thing instead of announcing it ('It is worth noting that X' -> 'X')."),
    "padding.wordy_per1k": ("wordy stock phrases per 1k", "Shorten where nothing is lost ('in order to' -> 'to'). A few are normal in human prose; a pile is filler."),
    "padding.double_hedge_per1k": ("stacked hedges per 1k", "One hedge per claim: 'may potentially suggest' -> 'suggests' or 'may'."),
    "padding.binomial_per1k": ("doublets ('robust and reliable') per 1k", "Keep the word that carries the meaning; drop its near-synonym."),
    "padding.restatement_share": ("sentences that mostly repeat an earlier one", "Delete the restatement or make it add a fact, a number or a consequence."),
    "padding.expletive_opener_share": ("sentences opening with 'There is / It is ... that'", "Start with the subject that does something."),
    "stock.triad_lists_per1k": ("lists of three per 1k", "Keep lists the content needs; cut padded enumerations; one precise example beats three vague ones."),
    "stock.stock_per1k": ("stock phrases per 1k", "Replace each listed stock phrase with the specific claim, or delete it."),
    "stock.significance_echo_per1k": ("significance-echo sentences per 1k", "Delete sentences that only restate importance."),
    "stock.extraposition_per1k": ("'it is important to...' formulas per 1k", "State the point directly."),
    "document.paragraph_wrapup_share": ("paragraphs ending on a summary/significance line", "End paragraphs on the last substantive point."),
    "connectives.connective_initial_share": ("sentences opening with a connective", "Delete connectives whose logic is already obvious."),
    "connectives.formulaic_initial_share": ("formulaic openers (Furthermore / Moreover / Overall ...)", "Delete them; if a relation is needed, state it inside the sentence."),
    "connectives.logical_connective_share": ("logical connectives share (contrast / cause / condition)", "Make the reasoning explicit where it exists: but, because, although, unless."),
    "stance.hedges_per1k": ("hedges per 1k", "Hedge only where evidence is uncertain, tied to the specific claim."),
    "stance.attitude_per1k": ("attitude markers per 1k", "Say what is surprising, disappointing or unexpected when the source supports it."),
    "stance.self_mention_per1k": ("self-mention per 1k", "Let the authors appear where the genre allows ('we measured', 'we suspect')."),
    "stance.stance_per1k": ("stance markers per 1k", "Take positions the evidence supports; mark real uncertainty; evaluate."),
    "pos.comparative_per1k": ("comparatives / superlatives per 1k", "State comparisons the evidence supports, with what is compared to what."),
    "sentiment.critical_per1k": ("critical / negative evaluation per 1k", "Keep problems and limitations at the strength the source states them."),
    "sentiment.promo_per1k": ("promotional vocabulary per 1k", "Cut promotional adjectives (crucial, robust, comprehensive, transformative, invaluable ...)."),
    "structure.subject_initial_share": ("subject-first sentences", "Open some sentences with the condition, contrast, time or cause that frames them ('Because ...', 'In 2018 ...', 'Unlike X ...')."),
    "structure.varied_opener_share": ("varied openers (subordinate / prepositional / adverbial ...)", "Same as subject-first."),
    "structure.skeleton_entropy": ("sentence-skeleton variety", "Vary sentence architecture, not just words."),
    "structure.top_first_word_share": ("most common first word share", "Vary sentence openings."),
    "function_words.ai_fw_per1k": ("function words reported as AI-favoured (and / can / by / with / for / their) per 1k", "Fewer additive 'and' chains and 'can + verb' generalities; say who does what."),
    "function_words.human_fw_per1k": ("function words reported as human-favoured per 1k", "Reason out loud: but, because, although, if, when, would, might."),
    "pos.cconj_pct": ("coordinating conjunctions (% of tokens)", "Fewer 'X and Y and Z' chains; subordinate instead (because, although, when)."),
    "pos.pron_pct": ("pronouns (% of tokens)", "Refer back with it / this / they / we where the referent is clear instead of repeating full noun phrases."),
    "lexical.repeated_3gram_per1k": ("repeated 3-grams per 1k", "Rephrase recycled phrases (protect real technical terms with --protect)."),
    "lexical.repeated_frame_share": ("repeated sentence frames", "Vary openers: 'This approach ...', 'These findings ...' repeated is a template."),
}
# French registers: the same labels in English (the report has one language), with fix hints that name the
# French constructions. Keys absent here fall back to the general text above.
FR_TEXT = {
    "lexical.glue_per100": ("glue words per 100 tokens", "French human prose leans on être and avoir (compound tenses, passives, « il y a », « c'est », « il est possible que ») and on « en ». Rewrite verb-heavy formulas with them: « X constitue un enjeu majeur » -> « X est important parce que ... » ; « cette approche permet d'identifier » -> « avec cette approche, on a identifié »."),
    "pos.aux_pct": ("auxiliaries: être / avoir (% of tokens)", "Use the passé composé and the passive where a French paper would (« nous avons mesuré », « les patients ont été suivis ») and plain « est / sont / a / ont » instead of constituer, demeurer, s'avérer, représenter."),
    "pos.lexical_density": ("lexical density (content words / all words)", "The text packs too many content words per sentence. Spread the load: one claim per clause, with its articles, prepositions and auxiliaries (« l'analyse des données de mortalité hospitalière » -> « nous avons analysé les données de mortalité recueillies à l'hôpital »)."),
    "lexical.word_len_mean": ("mean word length (letters)", "Prefer the everyday word where it says the same thing: utiliser, montrer, aider, environ, faire, avoir (not mobiliser, mettre en évidence, favoriser, approximativement, effectuer, disposer de). Keep the field's own terms."),
    "pos.deriv_adv_pct": ("adverbs in -ment (% of tokens)", "Cut intensifying and decorative -ment adverbs (considérablement, particulièrement, fondamentalement, véritablement, largement); keep those that inform (rarement, auparavant, aléatoirement)."),
    "pos.adj_pct": ("adjectives (% of tokens)", "Cut stacked evaluative adjectives (majeur, crucial, essentiel, considérable, complexe, véritable); keep the ones that classify (thermique, randomisé, rénal)."),
    "pos.verb_pct": ("lexical verbs (% of tokens)", "Too many heavy verbs doing abstract work (constituer, permettre, révéler, offrir, s'inscrire, témoigner): say what is the case with être / avoir, or name who did what."),
    "structure.passive_sentence_share": ("sentences with a passive", "French prose uses the passive or « on » where the doer is beside the point (« les patients ont été suivis », « on a mesuré »). Do not force every sentence active."),
    "pos.of_per100": ("« de » per 100 words", "Too low is as telling as too high: human French uses « de » phrases freely (« le taux de perte », « la plupart des échantillons »)."),
    "nominal.nominalization_per1k": ("nominalisations per 1k (-tion, -ment, -ité, -ance ...)", "Turn the noun back into a verb where an actor exists: « la réalisation de l'analyse » -> « nous avons analysé » ; « en raison du vieillissement des mécanismes » -> « parce que les mécanismes vieillissent »."),
    "nominal.nominal_heavy_share": ("sentences with >=3 nominalisations", "Rewrite the listed clusters with verbs."),
    "padding.participial_clause_per1k": ("participial clauses tacked on after a comma (« , soulignant ainsi ... », « , permettant de ... ») per 1k", "Cut the clause, or make it a sentence with a subject and a conjugated verb that states a fact."),
    "padding.wordy_per1k": ("heavy locutions per 1k", "Lighten where nothing is lost (« dans le but de » -> « pour », « au niveau de » -> « dans », « permet de mesurer » -> « mesure »). A few are normal in human French; a pile is filler."),
    "padding.metadiscourse_per1k": ("announcements about the text per 1k", "Say the thing instead of announcing it (« Il convient de souligner que X » -> « X »)."),
    "padding.shell_noun_per1k": ("abstract framing nouns per 1k (enjeu, cadre, dynamique, démarche, logique, levier ...)", "Replace the frame with the thing: « joue un rôle dans la régulation de » -> « régule » ; « constitue un enjeu majeur » -> say what is at stake and for whom."),
    "connectives.formulaic_initial_share": ("formulaic sentence openers (De plus / En outre / En effet / En somme ...)", "Delete them; if a logical link is needed, state it inside the sentence."),
    "markers.ai_function_per1k": ("function words current models over-use, per 1k", "In French this is mostly the demonstrative (ce / cette / ces + noun) pointing back at the previous sentence (« Cette approche ... », « Ces résultats ... »). Name the thing, use a pronoun, or join the two sentences."),
    "markers.ai_content_per1k": ("content words current models over-use, per 1k", "Replace the listed words with the plain one a specialist would use (constituer -> être ; demeurer -> rester ; offrir -> donner ; révéler -> montrer ; enjeu -> say what is at stake), or drop the sentence if it only frames."),
    "markers.human_function_per1k": ("everyday function words people use more (il, nous, on, très, alors), per 1k", "Write the ordinary way: « il y a », « il faut », « on observe », « nous avons ». Do not replace them with tighter constructions."),
    "markers.plain_per1k": ("plain workhorse words people use, per 1k", "Use the ordinary verbs of the field, « faire » first of all."),
    "stance.self_mention_per1k": ("self-mention per 1k (nous, notre, je)", "Let the authors appear where the genre allows (« nous avons mesuré », « nous pensons que »)."),
    "structure.subject_initial_share": ("subject-first sentences", "Open some sentences with the circumstance that frames them (« En 2018, ... », « Chez les patients âgés, ... », « Parce que ... », « Si ... »)."),
    "punctuation.punct_entropy_nodash": ("punctuation variety (dashes excluded)", "Use parentheses for abbreviations, exact values and brief asides; the semicolon between two closely linked clauses; the colon to introduce; guillemets for quotations. Not dashes."),
}

GUARD = {k: "ceiling" for k in [
    "connectives.formulaic_initial_share", "connectives.connective_initial_share", "stock.stock_per1k",
    "stock.significance_echo_per1k", "stock.extraposition_per1k", "lexical.repeated_3gram_per1k",
    "lexical.repeated_frame_share", "document.paragraph_wrapup_share", "stock.triad_lists_per1k",
    "sentiment.promo_per1k", "nominal.nominalization_per1k", "nominal.nominal_heavy_share", "pos.noun_verb_ratio",
    "pos.nominal_verbal_ratio", "rhythm.uniform_run_max", "structure.top_first_word_share", "pos.cconj_pct",
    "function_words.ai_fw_per1k", "structure.subject_initial_share", "padding.participial_clause_per1k",
    "padding.shell_noun_per1k", "padding.metadiscourse_per1k", "padding.wordy_per1k", "padding.double_hedge_per1k",
    "padding.binomial_per1k", "padding.restatement_share", "padding.expletive_opener_share",
    "markers.ai_function_per1k", "markers.ai_content_per1k", "pos.deriv_adv_pct"]}
GUARD.update({k: "floor" for k in [
    "rhythm.sent_len_cv", "rhythm.masd_norm", "paragraphs.para_words_cv", "paragraphs.para_sents_cv",
    "punctuation.punct_entropy_nodash", "punctuation.nonbasic_share_nodash", "punctuation.per1k.parenthesis",
    "pos.specificity_pct", "pos.propn_pct", "pos.num_pct", "stance.self_mention_per1k",
    "function_words.human_fw_per1k", "connectives.logical_connective_share", "sentiment.critical_per1k",
    "stance.attitude_per1k", "structure.varied_opener_share", "structure.skeleton_entropy", "pos.pron_pct",
    "stance.stance_per1k", "markers.plain_per1k", "markers.human_function_per1k"]})
CLASSIC = {  # research-documented tells, checked even when current models do not show them: key -> minimum violation
    "connectives.formulaic_initial_share": 0.10, "stock.stock_per1k": 3.0, "stock.significance_echo_per1k": 2.0,
    "stock.extraposition_per1k": 2.0, "document.paragraph_wrapup_share": 0.34, "lexical.repeated_frame_share": 0.15,
    "rhythm.uniform_run_max": 0.0, "punctuation.nonbasic_share_nodash": 0.0, "stance.stance_per1k": 0.0,
    "rhythm.sent_len_cv": 0.0, "padding.metadiscourse_per1k": 3.0, "padding.wordy_per1k": 6.0,
    "padding.double_hedge_per1k": 2.0, "padding.participial_clause_per1k": 4.0, "padding.restatement_share": 0.10,
    "padding.shell_noun_per1k": 0.0}
GROUPS = {
    "sentence length": ["rhythm.sent_len_mean", "rhythm.long_share", "rhythm.short_share", "punctuation.comma_per_sentence"],
    "rhythm": ["rhythm.sent_len_cv", "rhythm.masd_norm", "rhythm.uniform_run_max"],
    "paragraphs": ["paragraphs.para_words_cv", "paragraphs.para_sents_cv"],
    "word variety": ["lexical.mattr50", "lexical.mtld_wrap", "lexical.types_at_100", "lexical.yule_k"],
    "content-word variety": ["lexical.content_types_at_50", "lexical.content_mattr25"],
    "grammatical glue": ["lexical.glue_per100", "pos.lexical_density", "pos.aux_pct", "pos.of_per100"],
    "word length": ["lexical.word_len_mean", "lexical.long_word_pct"],
    "marker words": ["markers.ai_function_per1k", "markers.ai_content_per1k", "markers.human_function_per1k", "markers.plain_per1k"],
    "specificity": ["pos.specificity_pct", "pos.propn_pct", "pos.num_pct"],
    "punctuation": ["punctuation.punct_entropy_nodash", "punctuation.nonbasic_share_nodash", "punctuation.per1k.parenthesis"],
    "modifiers": ["pos.deriv_adv_pct", "pos.adj_pct"],
    "verb style": ["pos.verb_pct", "structure.passive_sentence_share"],
    "nominal style": ["nominal.nominal_heavy_share", "nominal.nominalization_per1k", "pos.noun_verb_ratio", "pos.nominal_verbal_ratio"],
    "padding": ["padding.participial_clause_per1k", "padding.shell_noun_per1k", "padding.metadiscourse_per1k",
                "padding.wordy_per1k", "padding.double_hedge_per1k", "padding.binomial_per1k",
                "padding.restatement_share", "padding.expletive_opener_share", "stock.triad_lists_per1k"],
    "stock phrasing": ["stock.stock_per1k", "stock.significance_echo_per1k", "stock.extraposition_per1k",
                       "document.paragraph_wrapup_share"],
    "connectives": ["connectives.connective_initial_share", "connectives.formulaic_initial_share",
                    "connectives.logical_connective_share"],
    "stance": ["stance.hedges_per1k", "stance.attitude_per1k", "stance.self_mention_per1k", "stance.stance_per1k",
               "pos.comparative_per1k"],
    "evaluation": ["sentiment.critical_per1k", "sentiment.promo_per1k"],
    "openers": ["structure.subject_initial_share", "structure.varied_opener_share", "structure.skeleton_entropy",
                "structure.top_first_word_share"],
    "function words": ["function_words.ai_fw_per1k", "function_words.human_fw_per1k", "pos.cconj_pct", "pos.pron_pct",
                       "lexical.fw_types_at_50"],
    "repetition": ["lexical.repeated_3gram_per1k", "lexical.repeated_frame_share"],
}
GROUP = {k: g for g, ks in GROUPS.items() for k in ks}
# Beyond the human median on the far side of these is no writing fault (less filler, fewer stock phrases
# or model-typical words, more names and numbers): they never count as over-correction.
HARMLESS_FAR = set(GROUPS["padding"]) | set(GROUPS["stock phrasing"]) | set(GROUPS["specificity"]) | {
    "sentiment.promo_per1k", "markers.ai_function_per1k", "markers.ai_content_per1k",
    "connectives.formulaic_initial_share", "connectives.connective_initial_share", "function_words.ai_fw_per1k",
    "lexical.repeated_frame_share", "rhythm.uniform_run_max", "structure.top_first_word_share"}
# measured, reported, but never part of the composite (corpus era or genre would decide, not authorship)
NEVER_GATE = set()


def num(r, k):
    v = r.get(k)
    return v if S.is_num(v) else None


def vals(rows, k):
    return [v for v in (num(r, k) for r in rows) if v is not None]


class Data:
    def __init__(self, rows):
        self.by = collections.defaultdict(list)
        for r in sorted(rows, key=lambda r: (r["_set"], r["_file"], r["_L"], r["_win"])):
            self.by[(r["_set"], r["_L"])].append(r)

    def rows(self, sets, L, files=None):
        out = []
        for s in sets:
            out += [r for r in self.by.get((s, L), []) if files is None or r["_file"] in files]
        return out

    def files(self, sets, L=0):
        return sorted({r["_file"] for s in sets for r in self.by.get((s, L), [])})

    def n_docs(self, sets, L=0):
        """Number of documents (the same prompt answered by two model tiers is two documents)."""
        return sum(len({r["_file"] for r in self.by.get((s, L), [])}) for s in sets)


def build(data, cfg, lang, lengths, hfiles=None, afiles=None, tiers=None):
    """Metric specifications for one register from the given human and AI documents."""
    tiers = tiers or list(cfg["ai"])
    H = {L: data.rows(cfg["human"], L, hfiles) for L in lengths}
    A = {t: {L: data.rows(cfg["ai"][t], L, afiles) for L in lengths} for t in tiers}
    top = str(lengths[-1])
    metrics = {}
    for key, (label, fix) in CANDIDATES.items():
        if lang == "fr" and key in FR_TEXT:
            label, fix = FR_TEXT[key]
        if key == "lexical.glue_per100":
            label = "glue words per 100 tokens (%s)" % ", ".join(T.pack(lang).GLUE_LEMMAS)
        bands = {}
        for L in lengths:
            hv = vals(H[L], key)
            if len(hv) >= 30:
                bands[str(L)] = S.quantiles(hv)
        if not bands:
            continue
        aucs, ai_p50 = {}, {}
        for t in tiers:
            num_, den, p50 = 0.0, 0.0, {}
            for L in lengths:
                hv, av = vals(H[L], key), vals(A[t][L], key)
                nd = len({r["_file"] for r in A[t][L]})
                if len(hv) >= 30 and len(av) >= 8 and nd >= 8:
                    num_ += nd * S.auc(hv, av)
                    den += nd
                    p50[str(L)] = round(S.pct(av, .5), 5)
            if den:
                aucs[t] = round(num_ / den, 3)
                ai_p50[t] = p50
        guard = GUARD.get(key)
        sides = {(1 if u > 0.5 else -1) for u in aucs.values() if abs(u - 0.5) >= GAP}
        conflict = bool((guard == "ceiling" and -1 in sides) or (guard == "floor" and 1 in sides))
        if guard == "ceiling":
            sides.discard(-1)
        if guard == "floor":
            sides.discard(1)
        gate = bool(sides) and key not in NEVER_GATE
        direction = 0 if len(sides) == 2 else (sides.pop() if sides else (1 if guard == "ceiling" else -1 if guard == "floor" else
                                                                          (1 if statistics.mean(aucs.values() or [0.5]) >= 0.5 else -1)))
        ref = bands.get(top) or bands[sorted(bands, key=int)[-1]]
        spec = {"label": label, "fix": fix, "group": GROUP.get(key, key), "gate": gate, "ai_direction": direction,
                "guard": guard, "auc": aucs, "conflicts_with_research": conflict, "bands": bands, "ai_p50": ai_p50,
                "min_scale": round(max(1e-6, 0.05 * (abs(ref["p50"]) or 1)), 6)}
        if key in HARMLESS_FAR:
            spec["far_side"] = False
        if key in CLASSIC:
            spec["classic"] = True
            if CLASSIC[key]:
                spec["min_violation"] = CLASSIC[key]
        metrics[key] = spec
    return metrics


def add_profiles(reg, data, cfg, lengths, hfiles=None, afiles=None, tiers=None):
    """One weight vector per AI tier: how strongly that tier's texts deviate from human texts on each
    dimension score (S.profile_weights), from the given documents, all lengths pooled."""
    tiers = tiers or list(cfg["ai"])
    reg.pop("profiles", None)
    reg.setdefault("composite", {"threshold": {str(L): 99.0 for L in lengths}})
    wrap = {"registers": {"x.calib": reg}}

    def dimz(sets, files):
        out = collections.defaultdict(list)
        for L in lengths:
            for r in data.rows(sets, L, files):
                for d in S.evaluate(r, wrap, "calib", n_words=L, lang="x")["dimensions"]:
                    out[d["dimension"]].append(d["z"])
        return out
    hz = dimz(cfg["human"], hfiles)
    reg["profiles"] = {}
    for t in tiers:                       # largest weight first, so that the file does not depend on row order
        w = S.profile_weights(hz, dimz(cfg["ai"][t], afiles))
        reg["profiles"][t] = dict(sorted(w.items(), key=lambda kv: (-kv[1], kv[0])))
    return reg


def out_of_fold(data, cfg, lang, lengths, rng, tiers=None, K=5, repeats=2):
    """Score every document with a gate built without it: K folds by document, for humans and for each
    AI tier; metric selection, directions and bands all come from the other folds. Returns
    {L: [(file, composite, classic violations, {dimension: z})]} for humans, and the same per AI tier."""
    tiers = tiers or list(cfg["ai"])
    hdocs = data.files(cfg["human"], lengths[0])
    adocs = {t: data.files(cfg["ai"][t], lengths[0]) for t in cfg["ai"]}
    Hs = {L: [] for L in lengths}
    As = {t: {L: [] for L in lengths} for t in cfg["ai"]}
    for _ in range(repeats):
        hs = hdocs[:]
        rng.shuffle(hs)
        hfold = {f: i % K for i, f in enumerate(hs)}
        afold = {}
        for t, d in adocs.items():
            d = d[:]
            rng.shuffle(d)
            afold.update({f: i % K for i, f in enumerate(d)})
        for k in range(K):
            htr = {f for f in hdocs if hfold[f] != k}
            atr = {f for f, i in afold.items() if i != k}
            reg = {"lang": lang, "metrics": build(data, cfg, lang, lengths, htr, atr, tiers), "max_classic_violations": 1,
                   "composite": {"threshold": {str(L): 99.0 for L in lengths}}}
            add_profiles(reg, data, cfg, lengths, htr, atr, tiers)
            wrap = {"registers": {"x.calib": reg}}
            for L in lengths:
                for r in data.rows(cfg["human"], L):
                    if hfold.get(r["_file"]) == k:
                        e = S.evaluate(r, wrap, "calib", n_words=L, lang="x")
                        Hs[L].append((r["_file"], e["composite"], len(e["classic_violations"]), {d["dimension"]: d["z"] for d in e["dimensions"]}, e["overcorrection"]))
                for t in cfg["ai"]:
                    for r in data.rows(cfg["ai"][t], L):
                        if afold.get(r["_file"]) == k or t not in tiers:
                            e = S.evaluate(r, wrap, "calib", n_words=L, lang="x")
                            As[t][L].append((r["_file"], e["composite"], len(e["classic_violations"]), {}, e["overcorrection"]))
    return Hs, As


def composite_threshold(scores):
    """The 90th percentile of the out-of-fold human composites: one human text in ten is beyond it.
    The classic guards and the over-correction limit fail a few more, so the whole gate passes
    somewhat fewer than 90% of human texts; the measured rate is reported with every register."""
    return S.pct([sc[1] for sc in scores], 0.90)


def doc_pass(scores, thr, over_thr=1e9, maxv=1):
    """Share of documents passing (windows and repeats of one document are averaged first)."""
    per = collections.defaultdict(list)
    for sc in scores:
        per[sc[0]].append(sc[1] <= thr and sc[2] <= maxv and sc[4] <= over_thr)
    return statistics.mean(statistics.mean(v) for v in per.values()) if per else None


def calibrate_register(name, cfg, data, rng):
    lang = name.split(".")[0]
    all_ai = [s for t in cfg["ai"].values() for s in t]
    lengths = [L for L in sorted({L for (s, L) in data.by if L > 0})
               if data.n_docs(cfg["human"], L) >= MIN_H and data.n_docs(all_ai, L) >= MIN_A]
    if not lengths:
        return None, "no calibrated length"
    reg = {"lang": lang, "lengths": lengths, "metrics": build(data, cfg, lang, lengths), "max_classic_violations": 1}
    add_profiles(reg, data, cfg, lengths)
    # ---- thresholds from out-of-fold scores: a new human text meets bands it did not help to set
    Hs, As = out_of_fold(data, cfg, lang, lengths, rng)
    thr, othr, groups, power = {}, {}, collections.defaultdict(dict), {}
    for L in lengths:
        comps = [sc[1] for sc in Hs[L]]
        othr[str(L)] = round(S.pct([sc[4] for sc in Hs[L]], 0.99), 3)
        thr[str(L)] = round(composite_threshold(Hs[L]), 3)
        gz = collections.defaultdict(list)
        for sc in Hs[L]:
            for g, z in sc[3].items():
                gz[g].append(z)
        for g, v in gz.items():
            if len(v) >= 30:
                groups[g][str(L)] = {"p50": round(S.pct(v, .5), 4), "p75": round(S.pct(v, .75), 4), "p90": round(S.pct(v, .90), 4)}
        p = {"human_pass": round(doc_pass(Hs[L], thr[str(L)], othr[str(L)]), 3)}
        allai = [x for t in As for x in As[t][L]]
        if allai:
            p["ai_pass"] = round(doc_pass(allai, thr[str(L)], othr[str(L)]), 3)
            for t in As:
                if len({sc[0] for sc in As[t][L]}) >= 8:
                    p["ai_pass " + t] = round(doc_pass(As[t][L], thr[str(L)], othr[str(L)]), 3)
            p["ai_composite_p10"] = round(S.pct([sc[1] for sc in allai], 0.10), 3)
            p["human_composite_p50"] = round(S.pct(comps, 0.50), 3)
            power[str(L)] = p
    reg["composite"] = {"threshold": thr, "over_threshold": othr}
    reg["groups"] = {g: v for g, v in groups.items() if len(v) == len(lengths)}
    reg["power"] = power
    # ---- leave one model tier out: is the gate specific to the tiers it was built on?
    loo = {}
    if len(cfg["ai"]) > 1:
        for t in cfg["ai"]:
            H2, A2 = out_of_fold(data, cfg, lang, lengths, rng, tiers=[x for x in cfg["ai"] if x != t], repeats=1)
            rates = []
            for L in lengths:
                if A2[t][L]:
                    rates.append(doc_pass(A2[t][L], composite_threshold(H2[L]), S.pct([sc[4] for sc in H2[L]], 0.99)))
            loo[t] = round(statistics.mean(rates), 3) if rates else None
    wrap = {"registers": {"x.calib": reg}}
    extra, escores = {}, collections.defaultdict(dict)
    for s_ in cfg.get("extra_human", []):
        for L in lengths:
            rows = data.rows([s_], L)
            if rows:
                sc = []
                for r in rows:
                    e = S.evaluate(r, wrap, "calib", n_words=L, lang="x")
                    sc.append((r["_file"], e["composite"], len(e["classic_violations"]), {}, e["overcorrection"]))
                escores[s_][L] = sc
                # the far-side limit must admit other human prose of the register (older, looser styles)
                if len(sc) >= 30:
                    othr[str(L)] = round(max(othr[str(L)], S.pct([x[4] for x in sc], 0.975)), 3)
    for s_, by_len in escores.items():
        rates = [doc_pass(sc, thr[str(L)], othr[str(L)]) for L, sc in by_len.items()]
        extra[s_] = round(statistics.mean(rates), 3)
    for L in lengths:                                  # pass rates with the final limits
        if str(L) in power:
            power[str(L)]["human_pass"] = round(doc_pass(Hs[L], thr[str(L)], othr[str(L)]), 3)
            allai = [x for t in As for x in As[t][L]]
            power[str(L)]["ai_pass"] = round(doc_pass(allai, thr[str(L)], othr[str(L)]), 3)
            for t in As:
                if ("ai_pass " + t) in power[str(L)]:
                    power[str(L)]["ai_pass " + t] = round(doc_pass(As[t][L], thr[str(L)], othr[str(L)]), 3)
    reg["composite"]["over_threshold"] = othr
    # ---- vocabulary growth: new content words and new specifics per 100 added words (prefix windows)
    growth = {}
    pref = {L: {r["_file"]: r for r in data.rows(cfg["human"], L) if r["_win"] == 0} for L in lengths}
    for a_, b_ in zip(lengths, lengths[1:]):
        cg, fg = [], []
        for f, rb in pref[b_].items():
            ra = pref[a_].get(f)
            if ra and rb["words"] > ra["words"]:
                dw = rb["words"] - ra["words"]
                cg.append(100.0 * (rb["_ctypes"] - ra["_ctypes"]) / dw)
                fg.append(100.0 * (rb["_ftypes"] - ra["_ftypes"]) / dw)
        if len(cg) >= 30:
            growth[str(a_)] = {"content_p10": round(S.pct(cg, .10), 2), "content_p25": round(S.pct(cg, .25), 2),
                               "content_p50": round(S.pct(cg, .50), 2), "specifics_p25": round(S.pct(fg, .25), 2),
                               "specifics_p50": round(S.pct(fg, .50), 2), "n": len(cg)}
    reg["growth"] = growth
    hdocs = data.files(cfg["human"], lengths[0])
    reg.update({"n_human": len(hdocs), "n_ai": {t: len(data.files(sets, lengths[0])) for t, sets in cfg["ai"].items()},
                "validation": {"leave_one_tier_out_ai_pass": loo, "extra_human_pass": extra}})
    gated = sorted({m["group"] for m in reg["metrics"].values() if m["gate"]})
    reg["note"] = ("Human n=%d; AI %s. Calibrated lengths %s words. Gated dimensions: %s." % (
        len(hdocs), ", ".join("%s n=%d" % kv for kv in reg["n_ai"].items()), "/".join(map(str, lengths)), ", ".join(gated)))
    return reg, None


def report(name, reg):
    L = reg["lengths"]
    out = ["", "=== %s | human n=%d | AI %s | lengths %s" % (name, reg["n_human"], reg["n_ai"], L)]
    out.append("length    threshold  human pass   AI pass   per tier                              composite: human p50 / AI p10")
    for l in L:
        p = reg["power"].get(str(l), {})
        out.append("%6d    %7.3f   %8s   %8s   %-38s %s" % (
            l, reg["composite"]["threshold"][str(l)], "%.0f%%" % (100 * p["human_pass"]) if p else "-",
            "%.0f%%" % (100 * p["ai_pass"]) if p else "-",
            ", ".join("%s %.0f%%" % (k[8:], 100 * v) for k, v in p.items() if k.startswith("ai_pass ")),
            "%.2f / %.2f" % (p["human_composite_p50"], p["ai_composite_p10"]) if p else ""))
    v = reg["validation"]
    out.append("leave-one-tier-out AI pass: %s | other human sets pass: %s" % (v["leave_one_tier_out_ai_pass"], v["extra_human_pass"]))
    for t, w in reg.get("profiles", {}).items():
        out.append("profile %s: " % t + ", ".join("%s %.0f%%" % (g, 100 * x) for g, x in sorted(w.items(), key=lambda kv: -kv[1]) if x >= 0.02))
    out.append("growth (new content words / new specifics per 100 added words, human): " + "; ".join(
        "%s+: content p10 %.1f p50 %.1f, specifics p50 %.1f" % (k, g["content_p10"], g["content_p50"], g["specifics_p50"]) for k, g in reg["growth"].items()))
    mid = str(L[len(L) // 2])
    out.append("%-44s %-22s %4s %4s %4s  %-24s %s" % ("metric", "AUC per tier", "dir", "gate", "cls", "human p10/p50/p90 @%s" % mid, "AI p50 per tier"))
    def strength(sp):
        return max([abs(u - 0.5) for u in sp["auc"].values()] or [0])
    for key, sp in sorted(reg["metrics"].items(), key=lambda kv: (-kv[1]["gate"], kv[1]["group"], -strength(kv[1]))):
        h = sp["bands"].get(mid) or list(sp["bands"].values())[-1]
        out.append("%-44s %-22s %4s %4s %4s  %-24s %s%s" % (
            key, " ".join("%.2f" % u for u in sp["auc"].values()), {1: "+", -1: "-", 0: "+/-"}[sp["ai_direction"]],
            "Y" if sp["gate"] else "", "Y" if sp.get("classic") else "", "%.3g/%.3g/%.3g" % (h["p10"], h["p50"], h["p90"]),
            " ".join("%.3g" % (p.get(mid) if p.get(mid) is not None else float("nan")) for p in sp["ai_p50"].values()),
            "  [%s%s]" % (sp["group"], "; contradicts research guard" if sp["conflicts_with_research"] else "")))
    return out


def main():
    cfg = json.load(open(sys.argv[1]))
    write = "--write" in sys.argv
    md = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else None
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    rows = []
    for path in (cfg["run"] if isinstance(cfg["run"], list) else [cfg["run"]]):
        rows += [json.loads(l) for l in open(os.path.join(WS, path), encoding="utf-8")]
    data = Data(rows)
    out_path = os.path.join(DATA, "calibration.json")
    calib = json.load(open(out_path)) if os.path.exists(out_path) else {}
    if calib.get("version") != 3:
        calib = {"version": 3, "registers": {}}
    calib["method"] = ("pre-2020 human text vs current-model text on the same topics, per register and per text length; "
                       "see references/calibration.md")
    lines = []
    rng = random.Random(3)
    for name, rc in cfg["registers"].items():
        if only and name not in only:
            continue
        reg, err = calibrate_register(name, rc, data, rng)
        if err:
            print("skip", name, err)
            continue
        calib["registers"][name] = reg
        lines += report(name, reg)
    print("\n".join(lines))
    if md:
        open(md, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    if write:
        json.dump(calib, open(out_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("\nwrote", os.path.relpath(out_path, REPO).replace(os.sep, "/"), "(%d bytes)" % os.path.getsize(out_path))


if __name__ == "__main__":
    main()
