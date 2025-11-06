# 🚨 URGENT: Fix Production Database Missing Columns

## Problem
Production database is missing critical columns in `personal_learning_plan` table:
- `current_category_focus` (causing 500 errors)
- Other columns may also be missing

## Error Details
```
psycopg2.errors.UndefinedColumn: column personal_learning_plan.current_category_focus does not exist
```

## Solution
Run the SQL script to add missing columns.

## Method 1: PostgreSQL Console (Recommended)

1. **Go to Render Dashboard**
   - Navigate to your PostgreSQL database service
   - Click on "Connect" → "External Connection"

2. **Connect via psql**
   ```bash
   psql "postgresql://username:password@hostname:port/database"
   ```

3. **Run the fix script**
   ```sql
   \i /path/to/fix_production_missing_columns.sql
   ```
   
   Or copy-paste the contents of `scripts/fix_production_missing_columns.sql`

## Method 2: Render Shell

1. **Open Render Shell**
   - Go to your web service
   - Click "Shell" tab

2. **Run the script**
   ```bash
   cd /opt/render/project/src
   psql $DATABASE_URL -f scripts/fix_production_missing_columns.sql
   ```

## Method 3: Direct SQL Execution

1. **Copy the SQL content** from `scripts/fix_production_missing_columns.sql`
2. **Paste into PostgreSQL console** and execute

## Verification

After running the script, verify the fix:

```sql
-- Check if critical column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'personal_learning_plan' 
AND column_name = 'current_category_focus';

-- Should return: current_category_focus
```

## Expected Result

- ✅ `current_category_focus` column added
- ✅ All other missing columns added
- ✅ API endpoints return 200 instead of 500
- ✅ Learning Map loads without errors

## Rollback (if needed)

If something goes wrong, you can remove the columns:

```sql
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS current_category_focus;
-- (repeat for other columns if needed)
```

## Status
- [ ] Script executed
- [ ] Columns verified
- [ ] API tested
- [ ] Production working

## Contact
If issues persist, check the logs for any remaining column errors.





