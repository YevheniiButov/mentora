#!/bin/bash

# Template Protection Script
# This script protects the automated_practice.html template from modifications

TEMPLATE_PATH="templates/learning/automated_practice.html"
PROTECTION_SCRIPT="template_protection.py"
MONITOR_SCRIPT="template_monitor.py"

echo "🛡️  Template Protection System"
echo "================================"

# Check if template exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "❌ Template not found: $TEMPLATE_PATH"
    exit 1
fi

# Create protected backup
echo "📁 Creating protected backup..."
python3 "$PROTECTION_SCRIPT"

if [ $? -eq 0 ]; then
    echo "✅ Template protection setup complete"
else
    echo "❌ Template protection setup failed"
    exit 1
fi

# Create systemd service for monitoring
echo "🔧 Creating monitoring service..."
python3 "$MONITOR_SCRIPT" --create-service

# Start monitoring in background
echo "🚀 Starting template monitoring..."
nohup python3 "$MONITOR_SCRIPT" --template "$TEMPLATE_PATH" --interval 30 > template_monitor.log 2>&1 &
MONITOR_PID=$!

echo "✅ Template monitoring started (PID: $MONITOR_PID)"
echo "📝 Monitor log: template_monitor.log"
echo ""
echo "🛡️  Template is now protected!"
echo "   - Any modifications will be automatically reverted"
echo "   - Monitor runs every 30 seconds"
echo "   - Check 'template_monitor.log' for status"
echo ""
echo "To stop monitoring: kill $MONITOR_PID"
echo "To check status: python3 $MONITOR_SCRIPT --status"



