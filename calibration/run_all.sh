#!/bin/sh
# Rebuild everything the skill derives from text: human sets, marker words, measurements, calibration.
#
#   calibration/run_all.sh [FIRST_STEP]
#
#   1  human sets            needs the fetched corpora            -> workspace/calib/
#   2  marker words          needs the human and the AI texts     -> scripts/data/markers_<lang>.json
#   3  measurements          needs the human and the AI texts     -> workspace/runs/measurements_<lang>.jsonl
#   4  calibration           needs the measurements only          -> scripts/data/calibration.json
#   5  checks                needs the human and the AI texts     -> reports/long_documents.txt, heldout_ai_texts.txt
#
# FIRST_STEP defaults to 1. With the measurement files of a release in workspace/runs/, "run_all.sh 4"
# rebuilds the calibration without any corpus (step 5 is skipped when the text sets are missing).
# The workspace is calibration/workspace unless SCIHUMANIZER_WORKSPACE names another directory.
# See calibration/README.md.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/tools"
CFG="$HERE/config"
REP="$HERE/reports"
WS="${SCIHUMANIZER_WORKSPACE:-$HERE/workspace}"
PY="${PYTHON:-python3}"
FROM="${1:-1}"
L="--lengths=150,200,300,450,600,750,900"
SHOW="^===|^ +[0-9]+ +[0-9.]+|leave-one|^profile"

[ -d "$WS" ] || { echo "no workspace at $WS (see calibration/README.md)"; exit 1; }
cd "$WS"
mkdir -p runs "$REP"

if [ "$FROM" -le 1 ]; then
  echo "== 1. human sets"
  "$PY" "$TOOLS/prep_sets_2.py" corpora | tail -20
fi

if [ "$FROM" -le 2 ]; then
  echo "== 2. marker words"
  "$PY" "$TOOLS/build_markers.py" "$CFG/marker_sets_en.json" --write > "$REP/markers_en.txt"
  "$PY" "$TOOLS/build_markers.py" "$CFG/marker_sets_fr.json" --write > "$REP/markers_fr.txt"
  tail -12 "$REP/markers_en.txt" | cut -c1-400
  tail -12 "$REP/markers_fr.txt" | cut -c1-400
fi

if [ "$FROM" -le 3 ]; then
  echo "== 3. measurements (both languages at once; a few minutes)"
  "$PY" "$TOOLS/batch_metrics.py" runs/measurements_en.jsonl \
    H_scientific=calib/human/scientific:en H_scibrown=calib/human/scientific_brown:en \
    H_abstract=calib/human/abstract:en H_general=calib/human/general:en H_general_modern=calib/human/general_modern:en \
    A_scientific=calib/ai/scientific:en A_abstract=calib/ai/abstract:en A_general=calib/ai/general:en \
    A_general_modern=calib/ai/general_modern:en \
    Ah_scientific=calib/ai_haiku/scientific:en Ah_abstract=calib/ai_haiku/abstract:en Ah_general=calib/ai_haiku/general:en \
    Ah_general_modern=calib/ai_haiku/general_modern:en \
    T_sonnet=ai_test_baseline:en T_haiku=ai_test_baseline_haiku:en $L > runs/measurements_en.log 2>&1 &
  P1=$!
  "$PY" "$TOOLS/batch_metrics.py" runs/measurements_fr.jsonl \
    H_fr_scientific=calib/fr/human/scientific:fr H_fr_abstract=calib/fr/human/abstract:fr H_fr_general=calib/fr/human/general:fr \
    A_fr_scientific=calib/fr/ai_sonnet/scientific:fr A_fr_abstract=calib/fr/ai_sonnet/abstract:fr \
    A_fr_general=calib/fr/ai_sonnet/general:fr \
    Ah_fr_scientific=calib/fr/ai_haiku/scientific:fr Ah_fr_abstract=calib/fr/ai_haiku/abstract:fr \
    Ah_fr_general=calib/fr/ai_haiku/general:fr \
    T_fr_sonnet=ai_test_fr/sonnet:fr T_fr_haiku=ai_test_fr/haiku:fr $L > runs/measurements_fr.log 2>&1 &
  P2=$!
  wait $P1
  wait $P2
  tail -1 runs/measurements_en.log
  tail -1 runs/measurements_fr.log
fi

if [ "$FROM" -le 4 ]; then
  echo "== 4. calibration"
  "$PY" "$TOOLS/calibrate.py" "$CFG/calibrate_en.json" --write --md "$REP/calibration_en.txt" | grep -E "$SHOW" | cut -c1-260
  "$PY" "$TOOLS/calibrate.py" "$CFG/calibrate_fr.json" --write --md "$REP/calibration_fr.txt" | grep -E "$SHOW" | cut -c1-260
fi

if [ "$FROM" -le 5 ]; then
  echo "== 5. checks: long documents, AI texts kept out of the calibration"
  if [ -d calib/long ]; then
    "$PY" "$TOOLS/validate_long.py" \
      en.scientific=calib/long/en.scientific:calib/ai/scientific,calib/ai_haiku/scientific \
      en.general=calib/long/en.general:calib/ai/general,calib/ai_haiku/general \
      fr.scientific=calib/long/fr.scientific:calib/fr/ai_sonnet/scientific,calib/fr/ai_haiku/scientific \
      fr.general=calib/long/fr.general:calib/fr/ai_sonnet/general,calib/fr/ai_haiku/general | tee "$REP/long_documents.txt"
    "$PY" "$TOOLS/validate_heldout.py" \
      "en.scientific=ai_test_baseline/test_sci_*.txt,ai_test_baseline_haiku/test_sci_*.txt" \
      "en.general=ai_test_baseline/test_gen_*.txt,ai_test_baseline_haiku/test_gen_*.txt,calib/ai_haiku_extra/general" \
      "fr.scientific=ai_test_fr/sonnet/test_fr_sci_*.txt,ai_test_fr/haiku/test_fr_sci_*.txt" \
      "fr.general=ai_test_fr/sonnet/test_fr_gen_*.txt,ai_test_fr/haiku/test_fr_gen_*.txt" | tee "$REP/heldout_ai_texts.txt"
  else
    echo "skipped: no text sets in $WS/calib/long"
  fi
fi
