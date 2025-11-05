#!/bin/bash
# Batch backtest script for active strategies
# Generated automatically

CONDA_ENV="tflow"
RESULTS_DIR="/home/titus/moon-dev-ai-agents/retest_results"
mkdir -p "$RESULTS_DIR"

echo "════════════════════════════════════════════════════════════════"
echo "Re-testing 12 Active Strategies"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Testing AnchoredReversion..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T09_AnchoredReversion_OPT_v6_1.5pct.py" > "$RESULTS_DIR/AnchoredReversion.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing MomentumCrest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T03_MomentumCrest_OPT_v5_1.1pct.py" > "$RESULTS_DIR/MomentumCrest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing MomentumCrest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T03_MomentumCrest_OPT_v8_3.3pct.py" > "$RESULTS_DIR/MomentumCrest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing MitigativeBreaker..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T12_MitigativeBreaker_OPT_v1_5.4pct.py" > "$RESULTS_DIR/MitigativeBreaker.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing ConfluenceSweep..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T17_ConfluenceSweep_OPT_v7_2.4pct.py" > "$RESULTS_DIR/ConfluenceSweep.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing StructuralRetest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T06_StructuralRetest_OPT_v2_1.6pct.py" > "$RESULTS_DIR/StructuralRetest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing StructuralRetest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T06_StructuralRetest_OPT_v3_3.0pct.py" > "$RESULTS_DIR/StructuralRetest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing EquispacedFilter..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T10_EquispacedFilter_OPT_v1_9.9pct.py" > "$RESULTS_DIR/EquispacedFilter.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing EquispacedFilter..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T10_EquispacedFilter_OPT_v3_26.5pct.py" > "$RESULTS_DIR/EquispacedFilter.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing SequentialRetest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T08_SequentialRetest_OPT_v4_1.6pct.py" > "$RESULTS_DIR/SequentialRetest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing SequentialRetest..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T08_SequentialRetest_OPT_v5_4.2pct.py" > "$RESULTS_DIR/SequentialRetest.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "Testing StableInfluxTrigger..."
conda run -n $CONDA_ENV python "/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T07_StableInfluxTrigger_DEBUG_v1_141.3pct.py" > "$RESULTS_DIR/StableInfluxTrigger.log" 2>&1
echo "  ✓ Complete"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ All backtests complete! Results in: $RESULTS_DIR"
echo "════════════════════════════════════════════════════════════════"
