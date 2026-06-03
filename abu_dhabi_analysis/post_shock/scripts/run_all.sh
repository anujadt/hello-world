#!/usr/bin/env bash
# Post-shock analysis pipeline. Run from repo root.
# Regenerates the parquet first (in case .gitignored), then runs all phases.
set -euo pipefail

cd "$(dirname "$0")/../../.."

echo "=== Regenerating clean parquet (Phase 0 + Phase 1) ==="
python3 abu_dhabi_analysis/scripts/phase0_profile.py
python3 abu_dhabi_analysis/scripts/phase1_clean.py

echo
echo "=== Post-shock v3 main analysis ==="
python3 abu_dhabi_analysis/post_shock/scripts/run_post_shock_v3.py
python3 abu_dhabi_analysis/post_shock/scripts/phase_f_memo_v3.py

echo
echo "=== Items 2-4 (sourcing, IRR, triangulation refresh) ==="
python3 abu_dhabi_analysis/post_shock/scripts/items_2_3_sourcing_irr.py
python3 abu_dhabi_analysis/post_shock/scripts/item_4_triangulation_refresh.py

echo
echo "=== Studio YoY ==="
python3 abu_dhabi_analysis/post_shock/scripts/studio_yoy.py

echo
echo "=== v3.5 refinements (Rounds 1, 2, 4) ==="
python3 abu_dhabi_analysis/post_shock/scripts/v3_5_round1_rigor.py
python3 abu_dhabi_analysis/post_shock/scripts/v3_5_round2_decision.py
python3 abu_dhabi_analysis/post_shock/scripts/v3_5_round4_strategic.py

echo
echo "=== Pipeline complete ==="
echo "Main outputs:    abu_dhabi_analysis/post_shock/outputs/v3/"
echo "Refinements:     abu_dhabi_analysis/post_shock/outputs/v3_5/"
echo "Studios cut:     abu_dhabi_analysis/post_shock/outputs/studios/"
