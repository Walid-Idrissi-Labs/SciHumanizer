# Calibration tables: every metric, every register

Generated from `scripts/data/calibration.json` by `calibration/tools/render_tables.py full`. Read
`calibration.md` first: it explains the method. Values are given at one reference length per
register (450 words; 200 for abstracts); the calibration file holds them for every calibrated
length.

- **Scored**: the direction in which the metric counts toward the composite (blank: reported only).
- **Guard**: `ceiling` / `floor` is the direction research documents as the AI side; `classic` marks
  a classic guard; `contradicted` means current models go the other way, so the metric is not scored.
- **AUC**: P(AI value > human value) at equal length, averaged over lengths; 0.5 = no separation.

## Contents
- English: en.scientific, en.abstract, en.general
- French: fr.scientific, fr.abstract, fr.general

### en.scientific (values at 450 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.93 / 0.70 | 0.846 / 0.899 / 0.937 | 0.952 / 0.921 |
| `lexical.content_types_at_50` | content-word variety | AI higher |  | 0.81 / 0.50 | 0.776 / 0.855 / 0.898 | 0.885 / 0.853 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.45 / 0.66 | 0.000 / 2.17 / 6.61 | 0.000 / 2.30 |
| `lexical.fw_types_at_50` | function words | AI higher |  | 0.88 / 0.70 | 0.368 / 0.411 / 0.460 | 0.466 / 0.435 |
| `pos.pron_pct` | function words | AI lower | floor | 0.56 / 0.28 | 0.826 / 1.85 / 3.41 | 1.80 / 1.08 |
| `pos.cconj_pct` | function words | AI higher | ceiling | 0.58 / 0.66 | 2.47 / 4.04 / 5.83 | 4.48 / 4.83 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.70 / 0.96 | 0.535 / 0.588 / 0.631 | 0.611 / 0.666 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.11 / 0.07 | 14.5 / 18.2 / 22.5 | 13.5 / 11.9 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.29 / 0.18 | 2.88 / 4.14 / 5.80 | 3.16 / 2.92 |
| `pos.of_per100` | grammatical glue | AI lower |  | 0.29 / 0.26 | 2.76 / 4.14 / 5.88 | 3.42 / 2.91 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.94 / 0.98 | 4.74 / 15.2 / 28.3 | 36.9 / 53.3 |
| `markers.ai_function_per1k` | marker words | AI higher | ceiling | 0.95 / 0.88 | 4.40 / 11.2 / 22.9 | 36.9 / 31.0 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.24 / 0.11 | 21.8 / 37.5 / 51.4 | 24.4 / 17.6 |
| `markers.plain_per1k` | marker words | AI lower | floor | 0.18 / 0.22 | 6.44 / 15.6 / 28.8 | 6.58 / 6.68 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.92 / 0.72 | 0.538 / 1.32 / 2.50 | 3.19 / 2.00 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.68 / 0.76 | 6.44 / 9.37 / 12.6 | 11.0 / 12.0 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.56 / 0.84 | 29.0 / 51.0 / 80.6 | 53.0 / 81.6 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.77 / 0.67 | 0.000 / 0.167 / 0.429 | 0.374 / 0.264 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.57 / 0.26 | 0.874 / 0.957 / 1.00 | 1.00 / 0.887 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.65 / 0.74 | 0.357 / 0.571 / 0.767 | 0.655 / 0.691 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.62 / 0.33 | 0.100 / 0.231 / 0.442 | 0.300 / 0.159 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.57 / 0.80 | 2.47 / 10.9 / 24.7 | 13.0 / 24.3 |
| `paragraphs.para_words_cv` | paragraphs | AI lower | floor | 0.39 / 0.33 | 0.179 / 0.355 / 0.568 | 0.243 / 0.243 |
| `paragraphs.para_sents_cv` | paragraphs | AI lower | floor | 0.43 / 0.35 | 0.137 / 0.380 / 0.603 | 0.265 / 0.283 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.08 / 0.15 | 0.337 / 0.469 / 0.611 | 0.310 / 0.333 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.11 / 0.13 | 0.000 / 6.80 / 23.4 | 0.000 / 0.000 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.15 / 0.14 | 0.019 / 0.107 / 0.291 | 0.021 / 0.000 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.45 / 0.30 | 0.293 / 0.380 / 0.480 | 0.355 / 0.332 |
| `rhythm.masd_norm` | rhythm | AI lower | floor | 0.56 / 0.34 | 0.295 / 0.448 / 0.585 | 0.457 / 0.390 |
| `rhythm.long_share` | sentence length | both sides |  | 0.94 / 0.22 | 0.121 / 0.333 / 0.615 | 0.773 / 0.150 |
| `punctuation.comma_per_sentence` | sentence length | both sides |  | 0.93 / 0.30 | 0.804 / 1.41 / 2.23 | 2.92 / 1.00 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.92 / 0.21 | 20.8 / 26.4 / 34.7 | 41.5 / 21.9 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.12 / 0.12 | 1.58 / 5.81 / 13.2 | 1.38 / 1.11 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.20 / 0.18 | 0.440 / 2.81 / 7.55 | 0.590 / 0.325 |
| `pos.num_pct` | specificity | AI lower | floor | 0.25 / 0.21 | 0.220 / 1.30 / 4.36 | 0.455 / 0.340 |
| `stance.self_mention_per1k` | stance | AI lower | floor | 0.43 / 0.30 | 0.000 / 4.37 / 16.5 | 3.28 / 0.000 |
| `stance.hedges_per1k` | stance | AI higher |  | 0.58 / 0.65 | 0.000 / 6.70 / 16.9 | 8.60 / 11.2 |
| `pos.verb_pct` | verb style | AI higher |  | 0.80 / 0.85 | 8.03 / 10.3 / 12.5 | 12.4 / 12.8 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.62 / 0.18 | 0.137 / 0.286 / 0.490 | 0.357 / 0.140 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.87 / 0.99 | 5.36 / 5.67 / 6.05 | 6.06 / 6.63 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.74 / 0.95 | 15.4 / 20.6 / 25.5 | 23.7 / 29.0 |
| `lexical.mattr50` | word variety | AI higher |  | 0.96 / 0.89 | 0.734 / 0.775 / 0.814 | 0.843 / 0.823 |
| `lexical.mtld_wrap` | word variety | AI higher |  | 0.95 / 0.88 | 50.4 / 65.0 / 88.9 | 105 / 95.7 |
| `lexical.yule_k` | word variety | AI lower |  | 0.08 / 0.15 | 103 / 135 / 178 | 95.1 / 99.6 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.92 / 0.81 | 0.633 / 0.679 / 0.725 | 0.739 / 0.724 |
| `connectives.connective_initial_share` | connectives |  | ceiling; contradicted | 0.15 / 0.36 | 0.000 / 0.160 / 0.333 | 0.000 / 0.108 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic; contradicted | 0.27 / 0.40 | 0.000 / 0.053 / 0.147 | 0.000 / 0.000 |
| `connectives.logical_connective_share` | connectives |  | floor | 0.51 / 0.54 | 0.250 / 0.646 / 1.00 | 0.667 / 0.750 |
| `sentiment.critical_per1k` | evaluation |  | floor | 0.62 / 0.57 | 0.000 / 4.16 / 12.3 | 6.75 / 5.75 |
| `function_words.ai_fw_per1k` | function words |  | ceiling | 0.40 / 0.63 | 45.5 / 63.3 / 88.8 | 60.6 / 73.0 |
| `function_words.human_fw_per1k` | function words |  | floor | 0.62 / 0.38 | 56.7 / 75.7 / 98.8 | 84.4 / 70.0 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling; contradicted | 0.23 / 0.41 | 2.29 / 2.94 / 3.86 | 2.33 / 2.76 |
| `pos.nominal_verbal_ratio` | nominal style |  | ceiling; contradicted | 0.23 / 0.50 | 2.19 / 2.85 / 3.59 | 2.42 / 2.99 |
| `structure.top_first_word_share` | openers |  | ceiling | 0.54 / 0.55 | 0.111 / 0.176 / 0.288 | 0.174 / 0.171 |
| `padding.wordy_per1k` | padding |  | ceiling, classic; contradicted | 0.30 / 0.25 | 0.000 / 3.28 / 8.60 | 0.000 / 0.000 |
| `padding.participial_clause_per1k` | padding |  | ceiling, classic | 0.65 / 0.62 | 0.000 / 0.000 / 4.34 | 2.25 / 2.24 |
| `padding.binomial_per1k` | padding |  | ceiling | 0.46 / 0.64 | 3.90 / 13.0 / 23.9 | 11.0 / 16.7 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.36 / 0.43 | 0.000 / 0.000 / 0.105 | 0.000 / 0.000 |
| `padding.expletive_opener_share` | padding |  | ceiling | 0.40 / 0.37 | 0.000 / 0.000 / 0.077 | 0.000 / 0.000 |
| `stock.triad_lists_per1k` | padding |  | ceiling | 0.59 / 0.60 | 0.000 / 4.44 / 11.5 | 6.78 / 4.75 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.49 / 0.56 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.49 / 0.48 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling; contradicted | 0.29 / 0.40 | 6.69 / 24.2 / 62.7 | 15.3 / 18.2 |
| `lexical.repeated_frame_share` | repetition |  | ceiling, classic | 0.40 / 0.48 | 0.000 / 0.000 / 0.143 | 0.000 / 0.000 |
| `rhythm.uniform_run_max` | rhythm |  | ceiling, classic | 0.38 / 0.64 | 2.00 / 3.00 / 5.00 | 3.00 / 4.00 |
| `rhythm.short_share` | sentence length |  |  | 0.53 / 0.52 | 0.000 / 0.000 / 0.111 | 0.000 / 0.044 |
| `pos.comparative_per1k` | stance |  |  | 0.61 / 0.44 | 3.20 / 9.97 / 22.7 | 12.9 / 6.69 |
| `stance.stance_per1k` | stance |  | floor, classic | 0.51 / 0.54 | 3.28 / 15.8 / 32.8 | 14.4 / 17.4 |
| `stance.attitude_per1k` | stance |  | floor | 0.53 / 0.49 | 0.000 / 0.000 / 2.25 | 0.000 / 0.000 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.46 / 0.42 | 0.000 / 0.000 / 2.30 | 0.000 / 0.000 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.50 / 0.55 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.stock_per1k` | stock phrasing |  | ceiling, classic | 0.47 / 0.53 | 0.000 / 0.000 / 2.31 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.49 / 0.53 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |

### en.abstract (values at 200 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.77 / 0.63 | 0.857 / 0.906 / 0.939 | 0.938 / 0.920 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.49 / 0.73 | 0.000 / 0.000 / 10.0 | 0.000 / 7.52 |
| `lexical.fw_types_at_50` | function words | AI higher |  | 0.82 / 0.66 | 0.340 / 0.386 / 0.446 | 0.449 / 0.428 |
| `pos.cconj_pct` | function words | AI higher | ceiling | 0.67 / 0.81 | 1.52 / 3.12 / 4.61 | 3.85 / 4.82 |
| `pos.pron_pct` | function words | AI lower | floor | 0.52 / 0.24 | 0.986 / 2.99 / 4.72 | 3.16 / 1.91 |
| `function_words.human_fw_per1k` | function words | AI lower | floor | 0.48 / 0.26 | 34.0 / 62.5 / 93.2 | 58.5 / 46.5 |
| `function_words.ai_fw_per1k` | function words | AI higher | ceiling | 0.52 / 0.71 | 37.5 / 56.2 / 85.2 | 60.1 / 70.9 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.82 / 0.99 | 0.531 / 0.600 / 0.645 | 0.647 / 0.719 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.12 / 0.04 | 13.1 / 18.1 / 24.2 | 12.7 / 9.09 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.21 / 0.11 | 1.21 / 3.12 / 4.81 | 1.45 / 0.525 |
| `pos.of_per100` | grammatical glue | AI lower |  | 0.33 / 0.28 | 2.01 / 4.04 / 6.09 | 3.13 / 2.94 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.83 / 0.97 | 5.13 / 18.4 / 30.6 | 31.9 / 56.2 |
| `markers.ai_function_per1k` | marker words | AI higher | ceiling | 0.91 / 0.84 | 0.000 / 9.57 / 25.1 | 32.1 / 24.4 |
| `markers.plain_per1k` | marker words | AI lower | floor | 0.24 / 0.10 | 5.45 / 14.9 / 33.3 | 10.1 / 4.93 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.48 / 0.15 | 25.0 / 46.9 / 76.3 | 44.8 / 26.2 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.71 / 0.42 | 0.000 / 1.08 / 2.80 | 2.10 / 0.740 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.66 / 0.69 | 5.83 / 9.23 / 12.3 | 12.1 / 11.2 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.83 / 0.60 | 0.000 / 0.167 / 0.412 | 0.600 / 0.247 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.56 / 0.80 | 30.3 / 55.6 / 89.4 | 67.2 / 90.7 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.63 / 0.83 | 0.400 / 0.625 / 0.881 | 0.775 / 0.833 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.51 / 0.18 | 0.000 / 0.250 / 0.500 | 0.225 / 0.087 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.56 / 0.30 | 0.831 / 1.00 / 1.00 | 1.00 / 0.880 |
| `padding.participial_clause_per1k` | padding | AI higher | ceiling, classic | 0.82 / 0.66 | 0.000 / 0.000 / 5.38 | 5.50 / 4.82 |
| `padding.binomial_per1k` | padding | AI higher | ceiling | 0.65 / 0.81 | 0.000 / 5.53 / 16.0 | 10.2 / 19.4 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.62 / 0.81 | 0.000 / 6.13 / 20.1 | 11.1 / 19.8 |
| `stock.triad_lists_per1k` | padding | AI higher | ceiling | 0.71 / 0.72 | 0.000 / 0.000 / 6.43 | 5.07 / 5.20 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.06 / 0.16 | 0.327 / 0.476 / 0.581 | 0.286 / 0.330 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.09 / 0.13 | 0.000 / 0.133 / 0.269 | 0.000 / 0.000 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.12 / 0.12 | 0.000 / 9.57 / 23.8 | 0.000 / 0.000 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.15 / 0.29 | 0.200 / 0.314 / 0.428 | 0.194 / 0.261 |
| `rhythm.masd_norm` | rhythm | AI lower | floor | 0.20 / 0.33 | 0.223 / 0.353 / 0.586 | 0.244 / 0.296 |
| `rhythm.uniform_run_max` | rhythm | AI higher | ceiling, classic | 0.54 / 0.71 | 2.00 / 3.00 / 4.00 | 3.00 / 3.00 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.98 / 0.16 | 19.5 / 25.1 / 31.1 | 44.0 / 20.1 |
| `rhythm.long_share` | sentence length | both sides |  | 0.96 / 0.12 | 0.000 / 0.286 / 0.667 | 1.00 / 0.000 |
| `punctuation.comma_per_sentence` | sentence length | AI higher |  | 0.95 / 0.36 | 0.500 / 0.880 / 1.76 | 2.55 / 0.700 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.10 / 0.09 | 1.62 / 4.95 / 12.8 | 0.770 / 0.245 |
| `pos.num_pct` | specificity | AI lower | floor | 0.17 / 0.18 | 0.000 / 1.18 / 3.69 | 0.000 / 0.000 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.28 / 0.20 | 0.000 / 1.54 / 5.92 | 0.495 / 0.000 |
| `pos.comparative_per1k` | stance | AI lower |  | 0.52 / 0.31 | 0.000 / 5.38 / 15.7 | 5.34 / 0.000 |
| `pos.verb_pct` | verb style | AI higher |  | 0.67 / 0.83 | 7.72 / 11.7 / 15.7 | 13.0 / 15.4 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.58 / 0.18 | 0.000 / 0.222 / 0.571 | 0.225 / 0.000 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.90 / 1.00 | 5.10 / 5.65 / 6.07 | 6.20 / 7.03 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.83 / 0.99 | 14.2 / 19.6 / 25.7 | 27.1 / 35.0 |
| `lexical.mattr50` | word variety | AI higher |  | 0.90 / 0.88 | 0.710 / 0.769 / 0.811 | 0.828 / 0.828 |
| `lexical.mtld_wrap` | word variety | AI higher |  | 0.88 / 0.86 | 45.6 / 65.6 / 85.2 | 92.5 / 96.0 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.80 / 0.82 | 0.600 / 0.665 / 0.712 | 0.709 / 0.720 |
| `lexical.yule_k` | word variety | AI lower |  | 0.18 / 0.18 | 98.6 / 142 / 209 | 105 / 97.9 |
| `connectives.connective_initial_share` | connectives |  | ceiling; contradicted | 0.26 / 0.46 | 0.000 / 0.091 / 0.250 | 0.000 / 0.096 |
| `connectives.logical_connective_share` | connectives |  | floor; contradicted | - / 0.69 | 0.000 / 0.500 / 1.00 | - / 1.00 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic | 0.42 / 0.46 | 0.000 / 0.000 / 0.111 | 0.000 / 0.000 |
| `lexical.content_types_at_50` | content-word variety |  |  | 0.56 / 0.40 | 0.764 / 0.843 / 0.881 | 0.847 / 0.820 |
| `sentiment.critical_per1k` | evaluation |  | floor | 0.47 / 0.51 | 0.000 / 0.000 / 13.1 | 0.000 / 2.34 |
| `pos.nominal_verbal_ratio` | nominal style |  | ceiling | 0.48 / 0.57 | 2.06 / 3.03 / 4.25 | 2.79 / 3.22 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling | 0.47 / 0.49 | 1.82 / 2.67 / 4.09 | 2.70 / 2.54 |
| `structure.top_first_word_share` | openers |  | ceiling | 0.61 / 0.37 | 0.150 / 0.300 / 0.500 | 0.400 / 0.273 |
| `padding.wordy_per1k` | padding |  | ceiling, classic; contradicted | 0.38 / 0.34 | 0.000 / 0.000 / 12.7 | 0.000 / 0.000 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.45 / 0.47 | 0.000 / 0.000 / 0.111 | 0.000 / 0.000 |
| `padding.expletive_opener_share` | padding |  | ceiling | 0.49 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling | 0.42 / 0.43 | 0.000 / 12.3 / 42.8 | 10.2 / 12.5 |
| `lexical.repeated_frame_share` | repetition |  | ceiling, classic | 0.47 / 0.53 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `rhythm.short_share` | sentence length |  |  | 0.38 / 0.41 | 0.000 / 0.000 / 0.125 | 0.000 / 0.000 |
| `stance.self_mention_per1k` | stance |  | floor | 0.55 / 0.41 | 5.34 / 22.0 / 33.6 | 21.7 / 15.3 |
| `stance.hedges_per1k` | stance |  |  | 0.48 / 0.55 | 0.000 / 0.000 / 9.96 | 0.000 / 0.000 |
| `stance.stance_per1k` | stance |  | floor, classic | 0.54 / 0.48 | 6.16 / 26.6 / 39.8 | 26.9 / 24.4 |
| `stance.attitude_per1k` | stance |  | floor | 0.54 / 0.51 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.stock_per1k` | stock phrasing |  | ceiling, classic | 0.48 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.49 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.49 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |

### en.general (values at 450 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.75 / 0.48 | 0.874 / 0.930 / 0.965 | 0.960 / 0.931 |
| `lexical.content_types_at_50` | content-word variety | AI lower |  | 0.62 / 0.33 | 0.834 / 0.900 / 0.941 | 0.919 / 0.869 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.49 / 0.70 | 0.000 / 0.000 / 4.45 | 0.000 / 2.24 |
| `pos.pron_pct` | function words | AI lower | floor | 0.41 / 0.23 | 1.78 / 4.18 / 8.26 | 3.33 / 2.15 |
| `lexical.fw_types_at_50` | function words | AI higher |  | 0.73 / 0.60 | 0.389 / 0.446 / 0.492 | 0.479 / 0.465 |
| `pos.cconj_pct` | function words | AI higher | ceiling | 0.55 / 0.68 | 2.11 / 3.49 / 5.14 | 3.68 / 4.26 |
| `function_words.human_fw_per1k` | function words | AI lower | floor | 0.53 / 0.33 | 52.5 / 84.8 / 122 | 85.7 / 69.8 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.74 / 0.96 | 0.478 / 0.531 / 0.581 | 0.572 / 0.650 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.13 / 0.05 | 15.4 / 19.3 / 23.6 | 14.8 / 12.9 |
| `pos.of_per100` | grammatical glue | AI lower |  | 0.38 / 0.23 | 1.90 / 3.36 / 5.35 | 2.95 / 2.03 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.28 / 0.27 | 3.00 / 4.87 / 6.93 | 3.18 / 3.64 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.85 / 0.97 | 0.000 / 6.57 / 14.5 | 17.2 / 31.2 |
| `markers.ai_function_per1k` | marker words | AI higher | ceiling | 0.88 / 0.83 | 2.83 / 11.2 / 23.7 | 30.0 / 24.8 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.29 / 0.16 | 22.2 / 35.6 / 54.5 | 26.8 / 20.1 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.72 / 0.90 | 3.42 / 6.16 / 9.35 | 8.50 / 11.6 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.89 / 0.80 | 0.310 / 1.10 / 2.03 | 2.67 / 1.80 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.54 / 0.80 | 9.09 / 26.3 / 52.2 | 31.8 / 54.4 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.65 / 0.61 | 0.000 / 0.000 / 0.160 | 0.077 / 0.071 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.53 / 0.22 | 0.890 / 0.962 / 1.00 | 0.980 / 0.898 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.32 / 0.27 | 0.125 / 0.300 / 0.500 | 0.214 / 0.195 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.67 / 0.70 | 0.438 / 0.652 / 0.833 | 0.769 / 0.750 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.52 / 0.79 | 0.000 / 2.25 / 9.45 | 2.57 / 9.01 |
| `stock.triad_lists_per1k` | padding | AI higher | ceiling | 0.60 / 0.71 | 0.000 / 2.42 / 8.81 | 4.43 / 6.67 |
| `padding.participial_clause_per1k` | padding | AI higher | ceiling, classic | 0.67 / 0.61 | 0.000 / 0.000 / 3.60 | 2.22 / 2.20 |
| `padding.binomial_per1k` | padding | AI higher | ceiling | 0.43 / 0.67 | 2.21 / 7.71 / 16.5 | 6.54 / 11.0 |
| `paragraphs.para_sents_cv` | paragraphs | AI lower | floor | 0.35 / 0.28 | 0.256 / 0.421 / 0.627 | 0.337 / 0.319 |
| `paragraphs.para_words_cv` | paragraphs | AI lower | floor | 0.38 / 0.29 | 0.232 / 0.389 / 0.609 | 0.303 / 0.297 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.27 / 0.18 | 0.029 / 0.130 / 0.267 | 0.064 / 0.027 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.20 / 0.19 | 0.379 / 0.505 / 0.633 | 0.399 / 0.381 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.27 / 0.35 | 0.000 / 2.14 / 8.88 | 0.000 / 0.000 |
| `lexical.repeated_frame_share` | repetition | AI higher | ceiling, classic | 0.44 / 0.67 | 0.000 / 0.000 / 0.167 | 0.000 / 0.091 |
| `rhythm.uniform_run_max` | rhythm | AI higher | ceiling, classic; contradicted | 0.32 / 0.66 | 2.00 / 3.00 / 4.00 | 2.00 / 4.00 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.50 / 0.34 | 0.333 / 0.442 / 0.602 | 0.442 / 0.386 |
| `rhythm.masd_norm` | rhythm | AI lower | floor | 0.61 / 0.34 | 0.363 / 0.498 / 0.689 | 0.571 / 0.429 |
| `rhythm.long_share` | sentence length | both sides |  | 0.87 / 0.20 | 0.048 / 0.190 / 0.438 | 0.600 / 0.083 |
| `punctuation.comma_per_sentence` | sentence length | both sides |  | 0.85 / 0.32 | 0.670 / 1.18 / 2.00 | 2.17 / 0.870 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.84 / 0.21 | 16.8 / 21.8 / 28.7 | 33.3 / 17.9 |
| `rhythm.short_share` | sentence length | AI higher |  | 0.41 / 0.65 | 0.000 / 0.111 / 0.269 | 0.062 / 0.192 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.16 / 0.14 | 3.14 / 10.9 / 21.6 | 4.07 / 3.44 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.16 / 0.15 | 1.72 / 8.18 / 17.2 | 2.00 / 2.03 |
| `pos.num_pct` | specificity | AI lower | floor | 0.36 / 0.29 | 0.610 / 1.90 / 5.27 | 1.32 / 0.670 |
| `pos.comparative_per1k` | stance | AI higher |  | 0.74 / 0.68 | 2.24 / 8.99 / 20.1 | 17.2 / 13.2 |
| `stance.hedges_per1k` | stance | AI higher |  | 0.58 / 0.65 | 0.000 / 4.43 / 12.9 | 6.54 / 8.79 |
| `pos.verb_pct` | verb style | AI higher |  | 0.77 / 0.81 | 7.76 / 10.4 / 13.0 | 12.5 / 12.8 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.33 / 0.22 | 0.067 / 0.214 / 0.421 | 0.125 / 0.087 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.66 / 0.95 | 4.51 / 4.95 / 5.37 | 5.36 / 5.97 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.60 / 0.90 | 7.09 / 11.9 / 17.2 | 15.0 / 21.1 |
| `lexical.yule_k` | word variety | AI lower |  | 0.20 / 0.12 | 108 / 140 / 191 | 104 / 96.6 |
| `lexical.mattr50` | word variety | AI higher |  | 0.87 / 0.86 | 0.735 / 0.777 / 0.818 | 0.830 / 0.831 |
| `lexical.mtld_wrap` | word variety | AI higher |  | 0.87 / 0.83 | 51.1 / 70.7 / 100 | 108 / 103 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.82 / 0.81 | 0.648 / 0.697 / 0.738 | 0.741 / 0.744 |
| `connectives.connective_initial_share` | connectives |  | ceiling | 0.38 / 0.48 | 0.000 / 0.000 / 0.105 | 0.000 / 0.024 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic | 0.42 / 0.48 | 0.000 / 0.000 / 0.053 | 0.000 / 0.000 |
| `connectives.logical_connective_share` | connectives |  | floor | 0.52 / 0.53 | 0.000 / 1.00 / 1.00 | 0.834 / 1.00 |
| `sentiment.critical_per1k` | evaluation |  | floor | 0.62 / 0.61 | 0.000 / 2.23 / 7.03 | 4.54 / 4.35 |
| `function_words.ai_fw_per1k` | function words |  | ceiling | 0.44 / 0.60 | 38.5 / 54.4 / 74.5 | 49.9 / 56.4 |
| `markers.plain_per1k` | marker words |  | floor | 0.48 / 0.43 | 0.000 / 6.59 / 15.3 | 4.54 / 4.41 |
| `pos.nominal_verbal_ratio` | nominal style |  | ceiling | 0.48 / 0.63 | 1.46 / 2.12 / 2.94 | 2.08 / 2.40 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling | 0.45 / 0.61 | 1.53 / 2.18 / 3.12 | 2.04 / 2.55 |
| `structure.top_first_word_share` | openers |  | ceiling | 0.59 / 0.61 | 0.111 / 0.182 / 0.333 | 0.200 / 0.238 |
| `padding.wordy_per1k` | padding |  | ceiling, classic | 0.37 / 0.40 | 0.000 / 0.000 / 4.39 | 0.000 / 0.000 |
| `padding.expletive_opener_share` | padding |  | ceiling | 0.42 / 0.41 | 0.000 / 0.000 / 0.056 | 0.000 / 0.000 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.43 / 0.54 | 0.000 / 0.000 / 0.053 | 0.000 / 0.000 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.52 / 0.47 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.49 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling; contradicted | 0.32 / 0.51 | 2.23 / 11.0 / 33.9 | 6.38 / 13.3 |
| `stance.attitude_per1k` | stance |  | floor | 0.62 / 0.57 | 0.000 / 0.000 / 2.45 | 0.000 / 0.000 |
| `stance.self_mention_per1k` | stance |  | floor | 0.42 / 0.38 | 0.000 / 3.58 / 24.2 | 0.000 / 0.000 |
| `stance.stance_per1k` | stance |  | floor, classic | 0.52 / 0.53 | 2.71 / 13.6 / 38.1 | 13.1 / 15.6 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.46 / 0.47 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.stock_per1k` | stock phrasing |  | ceiling, classic | 0.48 / 0.50 | 0.000 / 0.000 / 2.22 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |

### fr.scientific (values at 450 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.89 / 0.77 | 0.887 / 0.933 / 0.967 | 0.970 / 0.956 |
| `lexical.content_types_at_50` | content-word variety | AI higher |  | 0.74 / 0.65 | 0.842 / 0.901 / 0.939 | 0.928 / 0.921 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.70 / 0.83 | 0.000 / 2.15 / 6.03 | 4.33 / 6.70 |
| `lexical.fw_types_at_50` | function words | AI lower |  | 0.57 / 0.20 | 0.316 / 0.355 / 0.402 | 0.366 / 0.313 |
| `pos.pron_pct` | function words | AI lower | floor | 0.49 / 0.23 | 1.77 / 3.67 / 7.11 | 3.74 / 2.08 |
| `function_words.human_fw_per1k` | function words | AI lower | floor | 0.41 / 0.33 | 19.4 / 39.7 / 72.5 | 33.6 / 28.6 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.82 / 0.95 | 0.480 / 0.510 / 0.545 | 0.542 / 0.573 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.10 / 0.06 | 4.39 / 6.39 / 8.87 | 3.66 / 3.52 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.08 / 0.12 | 1.88 / 3.47 / 5.50 | 1.49 / 1.57 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.91 / 0.97 | 0.000 / 4.51 / 11.2 | 16.1 / 24.2 |
| `markers.ai_function_per1k` | marker words | AI higher | ceiling | 0.81 / 0.82 | 2.28 / 8.93 / 18.3 | 15.5 / 17.5 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.27 / 0.18 | 4.63 / 14.7 / 29.8 | 8.55 / 3.28 |
| `markers.plain_per1k` | marker words | AI lower | floor | 0.36 / 0.30 | 0.000 / 2.21 / 6.59 | 0.000 / 0.000 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.82 / 0.92 | 6.01 / 8.96 / 12.6 | 12.4 / 14.7 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.80 / 0.84 | 0.234 / 0.840 / 1.45 | 1.70 / 1.70 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.91 / 0.66 | 0.000 / 0.176 / 0.429 | 0.500 / 0.250 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.77 / 0.89 | 28.2 / 50.3 / 77.4 | 68.7 / 84.6 |
| `pos.nominal_verbal_ratio` | nominal style | AI higher | ceiling | 0.57 / 0.73 | 2.29 / 3.42 / 4.57 | 3.52 / 4.17 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.37 / 0.19 | 0.759 / 0.894 / 1.00 | 0.819 / 0.730 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.32 / 0.27 | 0.100 / 0.250 / 0.455 | 0.182 / 0.143 |
| `structure.top_first_word_share` | openers | AI higher | ceiling | 0.73 / 0.56 | 0.118 / 0.188 / 0.286 | 0.250 / 0.195 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.71 / 0.73 | 0.417 / 0.667 / 0.844 | 0.818 / 0.796 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.69 / 0.81 | 0.000 / 6.65 / 19.0 | 10.9 / 15.5 |
| `padding.participial_clause_per1k` | padding | AI higher | ceiling, classic | 0.67 / 0.74 | 0.000 / 0.000 / 2.32 | 0.000 / 4.38 |
| `padding.binomial_per1k` | padding | AI higher | ceiling | 0.55 / 0.70 | 0.000 / 2.83 / 8.96 | 4.49 / 7.71 |
| `paragraphs.para_words_cv` | paragraphs | AI lower | floor | 0.20 / 0.17 | 0.204 / 0.423 / 0.696 | 0.236 / 0.213 |
| `paragraphs.para_sents_cv` | paragraphs | AI lower | floor | 0.20 / 0.18 | 0.252 / 0.444 / 0.731 | 0.255 / 0.234 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.09 / 0.29 | 0.402 / 0.515 / 0.675 | 0.359 / 0.442 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.10 / 0.33 | 0.000 / 6.68 / 17.9 | 0.000 / 2.20 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.16 / 0.25 | 0.056 / 0.150 / 0.305 | 0.045 / 0.065 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.15 / 0.16 | 0.328 / 0.454 / 0.622 | 0.329 / 0.332 |
| `rhythm.masd_norm` | rhythm | AI lower | floor | 0.26 / 0.20 | 0.375 / 0.513 / 0.724 | 0.382 / 0.365 |
| `rhythm.long_share` | sentence length | both sides |  | 0.93 / 0.16 | 0.136 / 0.333 / 0.727 | 0.800 / 0.107 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.93 / 0.20 | 20.0 / 26.6 / 39.0 | 42.5 / 20.6 |
| `punctuation.comma_per_sentence` | sentence length | both sides |  | 0.90 / 0.31 | 0.690 / 1.59 / 2.91 | 3.00 / 1.10 |
| `rhythm.short_share` | sentence length | AI lower |  | 0.26 / 0.44 | 0.000 / 0.056 / 0.222 | 0.000 / 0.045 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.13 / 0.17 | 1.73 / 5.26 / 11.8 | 1.55 / 1.48 |
| `pos.num_pct` | specificity | AI lower | floor | 0.20 / 0.20 | 0.320 / 1.71 / 4.65 | 0.610 / 0.420 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.21 / 0.25 | 0.210 / 2.25 / 7.54 | 0.420 / 0.525 |
| `stance.self_mention_per1k` | stance | AI lower | floor | 0.42 / 0.20 | 0.000 / 2.82 / 15.8 | 0.000 / 0.000 |
| `stock.stock_per1k` | stock phrasing | AI higher | ceiling, classic | 0.56 / 0.66 | 0.000 / 0.000 / 2.62 | 0.000 / 2.20 |
| `pos.verb_pct` | verb style | AI higher |  | 0.77 / 0.72 | 6.40 / 8.35 / 11.0 | 9.84 / 9.54 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.41 / 0.27 | 0.057 / 0.214 / 0.429 | 0.182 / 0.098 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.88 / 0.97 | 4.95 / 5.40 / 5.80 | 5.93 / 6.24 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.85 / 0.96 | 13.9 / 19.7 / 25.3 | 25.8 / 30.6 |
| `lexical.mattr50` | word variety | AI higher |  | 0.89 / 0.79 | 0.679 / 0.719 / 0.759 | 0.765 / 0.744 |
| `lexical.mtld_wrap` | word variety | AI higher |  | 0.88 / 0.78 | 34.5 / 44.4 / 60.2 | 64.4 / 56.1 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.82 / 0.77 | 0.598 / 0.642 / 0.679 | 0.674 / 0.666 |
| `lexical.yule_k` | word variety | AI lower |  | 0.32 / 0.41 | 213 / 274 / 343 | 235 / 267 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic; contradicted | 0.41 / 0.34 | 0.000 / 0.000 / 0.118 | 0.000 / 0.000 |
| `connectives.logical_connective_share` | connectives |  | floor | 0.55 / 0.62 | 0.000 / 0.500 / 1.00 | 0.667 / 0.667 |
| `connectives.connective_initial_share` | connectives |  | ceiling | 0.40 / 0.48 | 0.000 / 0.059 / 0.189 | 0.000 / 0.048 |
| `sentiment.critical_per1k` | evaluation |  | floor | 0.62 / 0.65 | 0.000 / 2.56 / 9.46 | 4.49 / 4.49 |
| `pos.cconj_pct` | function words |  | ceiling | 0.45 / 0.57 | 1.89 / 3.16 / 4.56 | 3.05 / 3.30 |
| `function_words.ai_fw_per1k` | function words |  | ceiling | 0.45 / 0.51 | 33.3 / 47.4 / 66.6 | 46.8 / 45.7 |
| `pos.of_per100` | grammatical glue |  |  | 0.45 / 0.44 | 3.89 / 5.80 / 7.47 | 5.53 / 5.04 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling; contradicted | 0.31 / 0.44 | 2.04 / 2.96 / 4.16 | 2.52 / 2.93 |
| `padding.wordy_per1k` | padding |  | ceiling, classic | 0.47 / 0.39 | 0.000 / 3.39 / 8.97 | 2.29 / 2.20 |
| `padding.expletive_opener_share` | padding |  | ceiling | 0.42 / 0.39 | 0.000 / 0.000 / 0.083 | 0.000 / 0.000 |
| `stock.triad_lists_per1k` | padding |  | ceiling | 0.41 / 0.55 | 0.000 / 2.22 / 6.64 | 0.000 / 2.21 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.41 / 0.41 | 0.000 / 0.000 / 0.059 | 0.000 / 0.000 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.53 / 0.47 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.50 / 0.51 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling; contradicted | 0.34 / 0.30 | 6.74 / 24.2 / 58.9 | 13.8 / 14.6 |
| `lexical.repeated_frame_share` | repetition |  | ceiling, classic | 0.41 / 0.46 | 0.000 / 0.000 / 0.211 | 0.000 / 0.000 |
| `rhythm.uniform_run_max` | rhythm |  | ceiling, classic | 0.41 / 0.61 | 2.00 / 3.00 / 4.00 | 3.00 / 3.00 |
| `stance.attitude_per1k` | stance |  | floor | 0.55 / 0.63 | 0.000 / 0.000 / 2.17 | 0.000 / 0.000 |
| `stance.stance_per1k` | stance |  | floor, classic | 0.42 / 0.38 | 2.21 / 8.99 / 22.7 | 6.85 / 6.62 |
| `pos.comparative_per1k` | stance |  |  | 0.58 / 0.43 | 0.000 / 6.06 / 15.6 | 6.85 / 4.39 |
| `stance.hedges_per1k` | stance |  |  | 0.43 / 0.58 | 0.000 / 2.27 / 6.83 | 2.17 / 2.25 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.53 / 0.58 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.54 / 0.52 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.46 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |

### fr.abstract (values at 200 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.79 / 0.59 | 0.873 / 0.937 / 0.973 | 0.964 / 0.949 |
| `lexical.content_types_at_50` | content-word variety | AI higher |  | 0.66 / 0.48 | 0.797 / 0.869 / 0.929 | 0.894 / 0.874 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.53 / 0.84 | 0.000 / 0.000 / 11.4 | 4.81 / 10.3 |
| `lexical.fw_types_at_50` | function words | AI lower |  | 0.40 / 0.11 | 0.273 / 0.317 / 0.368 | 0.306 / 0.249 |
| `pos.pron_pct` | function words | AI lower | floor | 0.33 / 0.16 | 0.493 / 2.42 / 6.24 | 1.60 / 0.690 |
| `function_words.human_fw_per1k` | function words | AI lower | floor | 0.36 / 0.17 | 10.1 / 29.0 / 59.9 | 20.8 / 12.6 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.10 / 0.02 | 1.22 / 2.81 / 5.15 | 0.935 / 0.000 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.11 / 0.03 | 3.73 / 5.96 / 8.71 | 3.06 / 1.41 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.77 / 0.96 | 0.484 / 0.525 / 0.558 | 0.548 / 0.591 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.67 / 0.99 | 0.000 / 5.18 / 15.0 | 9.35 / 36.6 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.18 / 0.11 | 0.000 / 12.5 / 34.5 | 0.000 / 0.000 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.69 / 0.86 | 6.14 / 9.13 / 12.9 | 11.0 / 13.0 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.75 / 0.59 | 0.000 / 0.620 / 1.69 | 1.37 / 1.03 |
| `pos.nominal_verbal_ratio` | nominal style | AI higher | ceiling | 0.72 / 0.91 | 2.86 / 4.09 / 5.85 | 4.91 / 6.59 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.82 / 0.57 | 0.000 / 0.286 / 0.667 | 0.600 / 0.409 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.65 / 0.81 | 39.1 / 70.9 / 104 | 80.6 / 108 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.89 / 0.88 | 0.400 / 0.667 / 1.00 | 1.00 / 1.00 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.19 / 0.12 | 0.750 / 0.917 / 1.00 | 0.750 / 0.667 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.21 / 0.16 | 0.000 / 0.200 / 0.500 | 0.000 / 0.000 |
| `structure.top_first_word_share` | openers | AI higher | ceiling | 0.65 / 0.66 | 0.167 / 0.250 / 0.429 | 0.366 / 0.317 |
| `padding.participial_clause_per1k` | padding | AI higher | ceiling, classic | 0.59 / 0.77 | 0.000 / 0.000 / 5.02 | 0.000 / 4.90 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.56 / 0.73 | 0.000 / 9.83 / 32.4 | 14.4 / 20.9 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.13 / 0.32 | 0.320 / 0.481 / 0.634 | 0.318 / 0.409 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.16 / 0.37 | 0.000 / 6.60 / 24.7 | 0.000 / 0.000 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.17 / 0.32 | 0.000 / 0.140 / 0.316 | 0.000 / 0.054 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.12 / 0.14 | 0.222 / 0.360 / 0.561 | 0.203 / 0.209 |
| `rhythm.masd_norm` | rhythm | AI lower | floor | 0.23 / 0.19 | 0.270 / 0.436 / 0.759 | 0.329 / 0.261 |
| `rhythm.uniform_run_max` | rhythm | AI higher | ceiling, classic | 0.58 / 0.79 | 1.00 / 2.00 / 4.00 | 3.00 / 3.50 |
| `rhythm.long_share` | sentence length | both sides |  | 0.92 / 0.14 | 0.111 / 0.375 / 0.750 | 1.00 / 0.111 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.87 / 0.20 | 20.5 / 27.7 / 41.2 | 41.4 / 22.9 |
| `punctuation.comma_per_sentence` | sentence length | AI higher |  | 0.84 / 0.36 | 0.500 / 1.20 / 2.31 | 2.40 / 1.05 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.17 / 0.23 | 0.480 / 3.69 / 12.5 | 0.940 / 1.23 |
| `pos.num_pct` | specificity | AI lower | floor | 0.20 / 0.21 | 0.000 / 1.04 / 3.76 | 0.000 / 0.000 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.28 / 0.31 | 0.000 / 1.46 / 6.50 | 0.235 / 0.000 |
| `stance.self_mention_per1k` | stance | AI lower | floor | 0.28 / 0.26 | 0.000 / 5.05 / 26.2 | 0.000 / 0.000 |
| `stance.stance_per1k` | stance | AI lower | floor, classic | 0.33 / 0.34 | 0.000 / 9.57 / 28.4 | 4.88 / 4.90 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.41 / 0.12 | 0.000 / 0.250 / 0.567 | 0.200 / 0.000 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.82 / 0.97 | 5.23 / 5.64 / 6.06 | 5.96 / 6.58 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.78 / 0.96 | 18.3 / 23.3 / 28.2 | 26.9 / 34.6 |
| `lexical.mattr50` | word variety | AI higher |  | 0.66 / 0.57 | 0.659 / 0.706 / 0.753 | 0.724 / 0.719 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.65 / 0.56 | 0.554 / 0.614 / 0.663 | 0.635 / 0.624 |
| `connectives.connective_initial_share` | connectives |  | ceiling; contradicted | 0.26 / 0.37 | 0.000 / 0.000 / 0.286 | 0.000 / 0.000 |
| `connectives.logical_connective_share` | connectives |  | floor; contradicted | 0.51 / 0.68 | 0.000 / 0.125 / 1.00 | 0.000 / 1.00 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic | 0.40 / 0.43 | 0.000 / 0.000 / 0.138 | 0.000 / 0.000 |
| `sentiment.critical_per1k` | evaluation |  | floor | 0.57 / 0.49 | 0.000 / 0.000 / 11.5 | 4.90 / 0.000 |
| `pos.cconj_pct` | function words |  | ceiling | 0.61 / 0.64 | 1.41 / 2.83 / 5.07 | 3.50 / 3.62 |
| `function_words.ai_fw_per1k` | function words |  | ceiling | 0.51 / 0.53 | 31.9 / 50.0 / 78.6 | 49.9 / 56.2 |
| `pos.of_per100` | grammatical glue |  |  | 0.62 / 0.49 | 4.71 / 6.83 / 9.67 | 8.29 / 6.76 |
| `markers.ai_function_per1k` | marker words |  | ceiling | 0.58 / 0.63 | 5.01 / 14.0 / 24.8 | 14.7 / 17.8 |
| `markers.plain_per1k` | marker words |  | floor | 0.45 / 0.38 | 0.000 / 0.000 / 5.50 | 0.000 / 0.000 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling | 0.49 / 0.59 | 2.25 / 3.02 / 4.53 | 3.21 / 3.32 |
| `padding.wordy_per1k` | padding |  | ceiling, classic; contradicted | 0.54 / 0.34 | 0.000 / 5.17 / 15.5 | 5.62 / 0.000 |
| `padding.binomial_per1k` | padding |  | ceiling | 0.58 / 0.64 | 0.000 / 4.74 / 13.6 | 5.27 / 5.26 |
| `stock.triad_lists_per1k` | padding |  | ceiling | 0.56 / 0.59 | 0.000 / 0.000 / 7.05 | 0.000 / 0.000 |
| `padding.expletive_opener_share` | padding |  | ceiling | 0.47 / 0.47 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.48 / 0.48 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.48 / 0.51 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.50 / 0.51 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling | 0.38 / 0.46 | 0.000 / 20.6 / 61.4 | 14.5 / 17.8 |
| `lexical.repeated_frame_share` | repetition |  | ceiling, classic | 0.50 / 0.57 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `rhythm.short_share` | sentence length |  |  | 0.38 / 0.44 | 0.000 / 0.000 / 0.143 | 0.000 / 0.000 |
| `pos.comparative_per1k` | stance |  |  | 0.59 / 0.41 | 0.000 / 4.63 / 12.6 | 5.01 / 0.000 |
| `stance.hedges_per1k` | stance |  |  | 0.45 / 0.56 | 0.000 / 0.000 / 6.79 | 0.000 / 0.000 |
| `stance.attitude_per1k` | stance |  | floor | 0.53 / 0.54 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.stock_per1k` | stock phrasing |  | ceiling, classic | 0.50 / 0.56 | 0.000 / 0.000 / 5.07 | 0.000 / 0.000 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.54 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.47 / 0.47 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.52 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `pos.verb_pct` | verb style |  |  | 0.62 / 0.63 | 6.17 / 8.74 / 11.6 | 9.44 / 9.46 |
| `lexical.mtld_wrap` | word variety |  |  | 0.63 / 0.53 | 28.9 / 39.6 / 56.0 | 43.5 / 41.0 |
| `lexical.yule_k` | word variety |  |  | 0.55 / 0.59 | 230 / 322 / 413 | 327 / 337 |

### fr.general (values at 450 words)

| Metric | Dimension | Scored | Guard | AUC Sonnet tier / Haiku tier | Human p10 / p50 / p90 | AI median Sonnet tier / Haiku tier |
|---|---|---|---|---|---|---|
| `lexical.content_mattr25` | content-word variety | AI higher |  | 0.86 / 0.77 | 0.905 / 0.945 / 0.970 | 0.973 / 0.966 |
| `lexical.content_types_at_50` | content-word variety | AI higher |  | 0.75 / 0.69 | 0.862 / 0.910 / 0.942 | 0.937 / 0.928 |
| `sentiment.promo_per1k` | evaluation | AI higher | ceiling | 0.70 / 0.69 | 0.000 / 0.000 / 4.97 | 3.96 / 4.43 |
| `pos.pron_pct` | function words | AI lower | floor | 0.31 / 0.44 | 2.31 / 4.36 / 7.45 | 3.33 / 4.01 |
| `function_words.human_fw_per1k` | function words | AI lower | floor | 0.34 / 0.45 | 21.1 / 42.8 / 73.0 | 35.4 / 33.5 |
| `pos.aux_pct` | grammatical glue | AI lower |  | 0.12 / 0.45 | 1.75 / 3.25 / 5.45 | 1.22 / 3.15 |
| `lexical.glue_per100` | grammatical glue | AI lower |  | 0.12 / 0.31 | 4.30 / 6.16 / 8.49 | 3.25 / 5.04 |
| `pos.lexical_density` | grammatical glue | AI higher |  | 0.74 / 0.83 | 0.481 / 0.514 / 0.566 | 0.546 / 0.548 |
| `pos.of_per100` | grammatical glue | AI lower |  | 0.51 / 0.21 | 3.97 / 5.78 / 7.74 | 6.08 / 4.04 |
| `markers.ai_content_per1k` | marker words | AI higher | ceiling | 0.83 / 0.88 | 0.000 / 3.24 / 10.8 | 12.5 / 15.6 |
| `markers.human_function_per1k` | marker words | AI lower | floor | 0.23 / 0.46 | 2.28 / 15.5 / 33.1 | 4.49 / 14.5 |
| `markers.ai_function_per1k` | marker words | AI higher | ceiling | 0.71 / 0.58 | 0.000 / 6.91 / 15.7 | 11.5 / 8.80 |
| `markers.plain_per1k` | marker words | AI lower | floor | 0.34 / 0.35 | 0.000 / 2.26 / 7.07 | 0.000 / 0.000 |
| `pos.deriv_adv_pct` | modifiers | AI higher | ceiling | 0.84 / 0.81 | 0.000 / 0.670 / 1.44 | 1.53 / 1.57 |
| `pos.adj_pct` | modifiers | AI higher |  | 0.81 / 0.77 | 5.03 / 7.38 / 10.3 | 11.6 / 9.22 |
| `nominal.nominal_heavy_share` | nominal style | AI higher | ceiling | 0.89 / 0.48 | 0.000 / 0.067 / 0.286 | 0.477 / 0.073 |
| `nominal.nominalization_per1k` | nominal style | AI higher | ceiling | 0.79 / 0.77 | 8.99 / 35.8 / 70.3 | 66.5 / 57.6 |
| `pos.nominal_verbal_ratio` | nominal style | AI higher | ceiling | 0.69 / 0.43 | 2.06 / 2.94 / 4.92 | 3.73 / 2.76 |
| `structure.skeleton_entropy` | openers | AI lower | floor | 0.32 / 0.26 | 0.803 / 0.907 / 0.977 | 0.850 / 0.820 |
| `structure.top_first_word_share` | openers | AI higher | ceiling | 0.72 / 0.62 | 0.105 / 0.167 / 0.286 | 0.250 / 0.200 |
| `structure.subject_initial_share` | openers | AI higher | ceiling | 0.71 / 0.64 | 0.400 / 0.625 / 0.833 | 0.750 / 0.696 |
| `structure.varied_opener_share` | openers | AI lower | floor | 0.31 / 0.39 | 0.118 / 0.292 / 0.500 | 0.250 / 0.242 |
| `padding.shell_noun_per1k` | padding | AI higher | ceiling, classic | 0.65 / 0.69 | 0.000 / 2.92 / 13.2 | 6.10 / 8.81 |
| `paragraphs.para_words_cv` | paragraphs | AI lower | floor | 0.38 / 0.23 | 0.230 / 0.380 / 0.584 | 0.251 / 0.225 |
| `paragraphs.para_sents_cv` | paragraphs | AI lower | floor | 0.27 / 0.24 | 0.255 / 0.434 / 0.624 | 0.267 / 0.255 |
| `punctuation.punct_entropy_nodash` | punctuation | AI lower | floor | 0.09 / 0.47 | 0.396 / 0.526 / 0.657 | 0.379 / 0.538 |
| `punctuation.per1k.parenthesis` | punctuation | AI lower | floor | 0.13 / 0.21 | 0.000 / 4.48 / 13.9 | 0.000 / 0.000 |
| `punctuation.nonbasic_share_nodash` | punctuation | AI lower | floor, classic | 0.16 / 0.44 | 0.048 / 0.146 / 0.272 | 0.059 / 0.148 |
| `rhythm.sent_len_cv` | rhythm | AI lower | floor, classic | 0.31 / 0.53 | 0.346 / 0.455 / 0.612 | 0.377 / 0.459 |
| `rhythm.sent_len_mean` | sentence length | both sides |  | 0.93 / 0.03 | 19.5 / 25.3 / 32.9 | 40.6 / 15.1 |
| `rhythm.long_share` | sentence length | both sides |  | 0.93 / 0.04 | 0.130 / 0.294 / 0.537 | 0.750 / 0.035 |
| `rhythm.short_share` | sentence length | both sides |  | 0.29 / 0.92 | 0.000 / 0.071 / 0.217 | 0.000 / 0.323 |
| `punctuation.comma_per_sentence` | sentence length | both sides |  | 0.87 / 0.22 | 0.890 / 1.53 / 2.44 | 2.86 / 1.07 |
| `pos.specificity_pct` | specificity | AI lower | floor | 0.16 / 0.29 | 2.22 / 7.39 / 15.8 | 1.79 / 4.83 |
| `pos.propn_pct` | specificity | AI lower | floor | 0.21 / 0.33 | 0.852 / 4.62 / 11.4 | 0.840 / 3.04 |
| `pos.num_pct` | specificity | AI lower | floor | 0.23 / 0.35 | 0.410 / 1.67 / 4.86 | 0.505 / 1.45 |
| `pos.comparative_per1k` | stance | AI higher |  | 0.68 / 0.49 | 0.000 / 6.45 / 15.2 | 10.7 / 5.54 |
| `stance.self_mention_per1k` | stance | AI lower | floor | 0.35 / 0.49 | 0.000 / 0.000 / 13.1 | 0.000 / 1.08 |
| `pos.verb_pct` | verb style | AI higher |  | 0.57 / 0.74 | 6.05 / 9.28 / 11.8 | 9.31 / 11.1 |
| `structure.passive_sentence_share` | verb style | AI lower |  | 0.36 / 0.27 | 0.000 / 0.143 / 0.347 | 0.111 / 0.044 |
| `lexical.word_len_mean` | word length | AI higher |  | 0.90 / 0.95 | 4.82 / 5.14 / 5.51 | 5.73 / 5.76 |
| `lexical.long_word_pct` | word length | AI higher |  | 0.85 / 0.88 | 11.8 / 16.2 / 21.5 | 22.9 / 22.5 |
| `lexical.types_at_100` | word variety | AI higher |  | 0.72 / 0.77 | 0.614 / 0.654 / 0.692 | 0.674 / 0.683 |
| `lexical.mtld_wrap` | word variety | AI higher |  | 0.69 / 0.73 | 36.3 / 49.3 / 68.8 | 58.0 / 63.0 |
| `lexical.mattr50` | word variety | AI higher |  | 0.72 / 0.71 | 0.696 / 0.734 / 0.773 | 0.757 / 0.759 |
| `connectives.connective_initial_share` | connectives |  | ceiling | 0.36 / 0.42 | 0.000 / 0.043 / 0.167 | 0.000 / 0.033 |
| `connectives.logical_connective_share` | connectives |  | floor | 0.59 / 0.62 | 0.000 / 0.500 / 1.00 | 0.600 / 1.00 |
| `connectives.formulaic_initial_share` | connectives |  | ceiling, classic | 0.41 / 0.41 | 0.000 / 0.000 / 0.077 | 0.000 / 0.000 |
| `sentiment.critical_per1k` | evaluation |  | floor; contradicted | 0.69 / 0.69 | 0.000 / 2.19 / 7.67 | 5.12 / 4.36 |
| `function_words.ai_fw_per1k` | function words |  | ceiling | 0.52 / 0.40 | 24.2 / 45.4 / 64.7 | 43.8 / 41.3 |
| `lexical.fw_types_at_50` | function words |  |  | 0.46 / 0.45 | 0.293 / 0.361 / 0.406 | 0.358 / 0.354 |
| `pos.cconj_pct` | function words |  | ceiling | 0.49 / 0.50 | 1.04 / 2.88 / 4.24 | 2.79 / 2.81 |
| `pos.noun_verb_ratio` | nominal style |  | ceiling | 0.57 / 0.43 | 1.78 / 2.49 / 4.38 | 2.67 / 2.48 |
| `padding.wordy_per1k` | padding |  | ceiling, classic; contradicted | 0.46 / 0.32 | 0.000 / 2.21 / 7.24 | 2.23 / 0.000 |
| `padding.expletive_opener_share` | padding |  | ceiling; contradicted | 0.34 / 0.46 | 0.000 / 0.000 / 0.071 | 0.000 / 0.000 |
| `padding.participial_clause_per1k` | padding |  | ceiling, classic | 0.63 / 0.55 | 0.000 / 0.000 / 2.85 | 2.13 / 0.000 |
| `padding.binomial_per1k` | padding |  | ceiling | 0.57 / 0.59 | 0.000 / 2.31 / 8.79 | 4.41 / 4.42 |
| `padding.restatement_share` | padding |  | ceiling, classic | 0.43 / 0.43 | 0.000 / 0.000 / 0.050 | 0.000 / 0.000 |
| `stock.triad_lists_per1k` | padding |  | ceiling | 0.51 / 0.55 | 0.000 / 2.20 / 6.67 | 2.16 / 2.19 |
| `padding.metadiscourse_per1k` | padding |  | ceiling, classic | 0.52 / 0.48 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `padding.double_hedge_per1k` | padding |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.repeated_3gram_per1k` | repetition |  | ceiling; contradicted | 0.41 / 0.26 | 4.46 / 15.5 / 42.9 | 8.08 / 5.57 |
| `lexical.repeated_frame_share` | repetition |  | ceiling, classic | 0.49 / 0.65 | 0.000 / 0.000 / 0.176 | 0.000 / 0.089 |
| `rhythm.uniform_run_max` | rhythm |  | ceiling, classic; contradicted | 0.32 / 0.61 | 2.00 / 3.00 / 4.00 | 2.00 / 3.00 |
| `rhythm.masd_norm` | rhythm |  | floor | 0.49 / 0.54 | 0.373 / 0.514 / 0.696 | 0.518 / 0.520 |
| `stance.hedges_per1k` | stance |  |  | 0.54 / 0.58 | 0.000 / 2.19 / 6.69 | 2.25 / 2.22 |
| `stance.attitude_per1k` | stance |  | floor | 0.55 / 0.58 | 0.000 / 0.000 / 2.20 | 0.000 / 0.000 |
| `stance.stance_per1k` | stance |  | floor, classic | 0.48 / 0.55 | 0.000 / 5.30 / 18.5 | 5.58 / 7.77 |
| `stock.stock_per1k` | stock phrasing |  | ceiling, classic | 0.57 / 0.58 | 0.000 / 0.000 / 2.29 | 0.000 / 0.000 |
| `stock.extraposition_per1k` | stock phrasing |  | ceiling, classic | 0.47 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `document.paragraph_wrapup_share` | stock phrasing |  | ceiling, classic | 0.51 / 0.49 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `stock.significance_echo_per1k` | stock phrasing |  | ceiling, classic | 0.50 / 0.50 | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 |
| `lexical.yule_k` | word variety |  |  | 0.55 / 0.46 | 174 / 254 / 333 | 262 / 241 |

