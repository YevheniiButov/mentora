#!/bin/bash

# Quick Template Restoration Script
# Use this to immediately restore the protected template

TEMPLATE_PATH="templates/learning/automated_practice.html"
PROTECTION_SCRIPT="template_protection.py"

echo "🔄 Restoring Protected Template"
echo "==============================="

# Check if template exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "❌ Template not found: $TEMPLATE_PATH"
    exit 1
fi

# Force restore template
echo "🔄 Force restoring template from protected backup..."
python3 -c "
from template_protection import TemplateProtection
protection = TemplateProtection('$TEMPLATE_PATH')
if protection.restore_template():
    print('✅ Template restored successfully')
else:
    print('❌ Template restoration failed')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Template restoration complete!"
    echo "🛡️  Template is now protected and restored"
else
    echo "❌ Template restoration failed"
    exit 1
fi


