#!/bin/bash
# Monitor RBI leverage strategy generation progress

echo "========================================="
echo "RBI Strategy Generation Monitor (ideasG.txt)"
echo "========================================="
echo ""

# Check if process is running
if ps aux | grep -q "[r]bi_agent_pp_multi.*ideasG"; then
    echo "✅ RBI Process: RUNNING"
    PID=$(ps aux | grep "[r]bi_agent_pp_multi.*ideasG" | awk '{print $2}')
    echo "   PID: $PID"
    echo "   Target: 15% return"
else
    echo "❌ RBI Process: NOT RUNNING"
fi

echo ""
echo "========================================="
echo "Processing Status"
echo "========================================="

# Count completed strategies from today
COMPLETED=$(grep "2025-11-05" /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/processed_ideas.log 2>/dev/null | wc -l)
TOTAL=29

echo "Strategies completed: $COMPLETED / $TOTAL"
echo ""

# Show working strategies
WORKING_DIR="/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working"
if [ -d "$WORKING_DIR" ]; then
    WORKING_COUNT=$(ls -1 "$WORKING_DIR"/*.py 2>/dev/null | wc -l)
    echo "Working strategies saved: $WORKING_COUNT"
    if [ $WORKING_COUNT -gt 0 ]; then
        echo ""
        echo "Latest strategies:"
        ls -1t "$WORKING_DIR"/*.py 2>/dev/null | head -5 | while read file; do
            basename "$file"
        done
    fi
fi

echo ""
echo "========================================="
echo "Recent Activity (last 20 lines)"
echo "========================================="
tail -30 /tmp/rbi_ideasG.log 2>/dev/null | grep -E "Status:|✅.*COMPLETED|🎯.*TARGET|💾.*Saved"

echo ""
echo "========================================="
echo "Run: watch -n 10 bash $0"
echo "to monitor every 10 seconds"
echo "========================================="
