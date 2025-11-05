#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "2022 Bear Market Backtest Status"
echo "════════════════════════════════════════════════════════════════"
tail -1 /tmp/rbi_bear2022.log | grep -E "Status:|💤"
echo ""
echo "Completed strategies (>1% return):"
grep "11/05 19:" /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/backtest_stats.csv 2>/dev/null | wc -l
echo ""
echo "Top 5 performers:"
grep "11/05 19:" /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/backtest_stats.csv 2>/dev/null | \
  awk -F',' '{printf "%-25s %8s%%\n", $1, $3}' | sort -t'%' -k2 -rn | head -5
echo "════════════════════════════════════════════════════════════════"
