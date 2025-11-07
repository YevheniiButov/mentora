#!/bin/bash

# Start Template Protection System
# This script starts the template monitoring in the background

TEMPLATE_PATH="templates/learning/automated_practice.html"
MONITOR_SCRIPT="template_monitor.py"
LOG_FILE="template_monitor.log"

echo "🛡️  Starting Template Protection System"
echo "======================================"

# Check if template exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "❌ Template not found: $TEMPLATE_PATH"
    exit 1
fi

# Check if monitoring is already running
if pgrep -f "$MONITOR_SCRIPT" > /dev/null; then
    echo "⚠️  Template monitoring is already running"
    echo "   To stop: pkill -f '$MONITOR_SCRIPT'"
    echo "   To restart: pkill -f '$MONITOR_SCRIPT' && $0"
    exit 1
fi

# Start monitoring in background
echo "🚀 Starting template monitoring..."
nohup python3 "$MONITOR_SCRIPT" --template "$TEMPLATE_PATH" --interval 30 > "$LOG_FILE" 2>&1 &
MONITOR_PID=$!

# Wait a moment and check if it started successfully
sleep 2
if ps -p $MONITOR_PID > /dev/null; then
    echo "✅ Template monitoring started successfully!"
    echo "   PID: $MONITOR_PID"
    echo "   Log: $LOG_FILE"
    echo "   Template: $TEMPLATE_PATH"
    echo ""
    echo "🛡️  Template is now protected!"
    echo "   - Monitoring every 30 seconds"
    echo "   - Auto-restore on modifications"
    echo "   - Logs saved to $LOG_FILE"
    echo ""
    echo "Commands:"
    echo "   Check status: python3 $MONITOR_SCRIPT --status"
    echo "   Stop monitoring: pkill -f '$MONITOR_SCRIPT'"
    echo "   View logs: tail -f $LOG_FILE"
    echo "   Force restore: ./restore_template.sh"
else
    echo "❌ Failed to start template monitoring"
    echo "   Check $LOG_FILE for errors"
    exit 1
fi



