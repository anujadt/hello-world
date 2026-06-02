#!/usr/bin/env bash
# Run the full Abu Dhabi DARI pipeline end-to-end.
# Phase 0 is the hard-stop per the brief; this script runs through, but in a fresh setting
# you should pause and review outputs/data_dictionary.md before letting Phase 1 onward proceed.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/phase0_profile.py
python3 scripts/phase1_clean.py
python3 scripts/phase2_core.py
python3 scripts/phase3_appreciation.py
python3 scripts/phase4_yields_offplan.py
python3 scripts/phase5_triangulate.py
python3 scripts/phase6_score_shortlist.py
python3 scripts/phase7_memo.py

echo
echo "Pipeline complete. Open outputs/insight_memo.md."
