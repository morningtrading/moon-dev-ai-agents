#!/bin/bash
# 🌙 Moon Dev's RBI Agent Monitor

echo "=========================================="
echo "🌙 RBI Agent Progress Monitor"
echo "=========================================="
echo ""

# Check if running
if ps aux | grep -q "[r]bi_agent_pp_multi"; then
    echo "✅ RBI Agent Status: RUNNING"
    PID=$(ps aux | grep "[r]bi_agent_pp_multi" | awk '{print $2}')
    echo "📍 PID: $PID"
else
    echo "❌ RBI Agent Status: NOT RUNNING"
    exit 1
fi

echo ""
echo "📊 Strategies Processed:"
wc -l /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/processed_ideas.log 2>/dev/null | awk '{print "   " $1 " strategies"}'

echo ""
echo "📈 Working Strategies Generated:"
ls -1 /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_03_2025/backtests_working/*.py 2>/dev/null | wc -l | awk '{print "   " $1 " strategies"}'

echo ""
echo "📋 Latest Stats:"
tail -3 /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/backtest_stats.csv 2>/dev/null | tail -2 | column -t -s,

echo ""
echo "📝 Recent Log (last 20 lines):"
echo "----------------------------------------"
tail -20 /tmp/rbi_leverage.log 2>/dev/null
echo "----------------------------------------"

echo ""
echo "💡 Commands:"
echo "   Watch live: tail -f /tmp/rbi_leverage.log"
echo "   Stop RBI:   kill $PID"
echo "   Re-run:     bash $0"
