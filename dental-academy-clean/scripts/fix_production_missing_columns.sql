-- Fix missing columns in personal_learning_plan table on production
-- This script adds the missing columns that are causing 500 errors

-- Check if columns exist before adding them
DO $$
BEGIN
    -- Add current_category_focus column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'current_category_focus'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN current_category_focus VARCHAR(100) DEFAULT NULL;
        RAISE NOTICE 'Added current_category_focus column';
    ELSE
        RAISE NOTICE 'current_category_focus column already exists';
    END IF;

    -- Add any other missing columns that might be causing issues
    -- (These should already exist from previous migrations, but let's be safe)
    
    -- Check and add weak_categories if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'weak_categories'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN weak_categories JSONB DEFAULT NULL;
        RAISE NOTICE 'Added weak_categories column';
    END IF;

    -- Check and add strong_categories if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'strong_categories'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN strong_categories JSONB DEFAULT NULL;
        RAISE NOTICE 'Added strong_categories column';
    END IF;

    -- Check and add category_abilities if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'category_abilities'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN category_abilities JSONB DEFAULT NULL;
        RAISE NOTICE 'Added category_abilities column';
    END IF;

    -- Check and add category_progress if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'category_progress'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN category_progress JSONB DEFAULT NULL;
        RAISE NOTICE 'Added category_progress column';
    END IF;

    -- Check and add time_invested if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'time_invested'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN time_invested INTEGER DEFAULT 0;
        RAISE NOTICE 'Added time_invested column';
    END IF;

    -- Check and add daily_question_goal if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'daily_question_goal'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN daily_question_goal INTEGER DEFAULT 20;
        RAISE NOTICE 'Added daily_question_goal column';
    END IF;

    -- Check and add daily_time_goal if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'daily_time_goal'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN daily_time_goal INTEGER DEFAULT 30;
        RAISE NOTICE 'Added daily_time_goal column';
    END IF;

    -- Check and add daily_streak if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'daily_streak'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN daily_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added daily_streak column';
    END IF;

    -- Check and add longest_daily_streak if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'longest_daily_streak'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN longest_daily_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added longest_daily_streak column';
    END IF;

    -- Check and add last_activity_date if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'last_activity_date'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN last_activity_date DATE DEFAULT NULL;
        RAISE NOTICE 'Added last_activity_date column';
    END IF;

    -- Check and add daily_goal_met_count if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'daily_goal_met_count'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN daily_goal_met_count INTEGER DEFAULT 0;
        RAISE NOTICE 'Added daily_goal_met_count column';
    END IF;

    -- Check and add learning_velocity if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'learning_velocity'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN learning_velocity FLOAT DEFAULT 0.0;
        RAISE NOTICE 'Added learning_velocity column';
    END IF;

    -- Check and add retention_rate if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'retention_rate'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN retention_rate FLOAT DEFAULT 0.0;
        RAISE NOTICE 'Added retention_rate column';
    END IF;

END $$;

-- Verify the fix by checking if the critical column exists
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'personal_learning_plan' 
            AND column_name = 'current_category_focus'
        ) THEN 'SUCCESS: current_category_focus column exists'
        ELSE 'ERROR: current_category_focus column still missing'
    END as status;

-- Show all columns in personal_learning_plan table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'personal_learning_plan' 
ORDER BY ordinal_position;







