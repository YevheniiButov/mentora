#!/bin/bash

# 🚨 URGENT: Fix Production Database Missing Columns
# This script fixes the missing columns causing 500 errors

echo "🚨 Starting production database fix..."
echo "================================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable not set"
    exit 1
fi

echo "✅ DATABASE_URL found"
echo "🔧 Connecting to production database..."

# Run the diagnostic script first
echo ""
echo "📊 Step 1: Checking missing columns..."
psql "$DATABASE_URL" -f scripts/check_missing_columns.sql

echo ""
echo "🔧 Step 2: Adding missing columns..."
psql "$DATABASE_URL" -f scripts/fix_production_missing_columns.sql

echo ""
echo "✅ Step 3: Verification..."
psql "$DATABASE_URL" -c "
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'personal_learning_plan' 
            AND column_name = 'current_category_focus'
        ) THEN 'SUCCESS: current_category_focus column exists'
        ELSE 'ERROR: current_category_focus column still missing'
    END as status;
"

echo ""
echo "🎉 Production database fix completed!"
echo "================================================"
echo "✅ Check the status above"
echo "✅ Test your Learning Map now"
echo "✅ API endpoints should work (200 instead of 500)"




