-- Check which columns are missing from personal_learning_plan table
-- This helps identify what needs to be added

-- Expected columns based on the model
WITH expected_columns AS (
    SELECT unnest(ARRAY[
        'id', 'user_id', 'exam_date', 'start_date', 'end_date', 'intensity', 
        'study_time', 'diagnostic_session_id', 'target_ability', 'study_hours_per_week',
        'current_ability', 'overall_progress', 'estimated_readiness', 'domain_analysis',
        'weak_domains', 'strong_domains', 'study_schedule', 'milestones', 'status',
        'last_updated', 'next_diagnostic_date', 'diagnostic_reminder_sent',
        'spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak',
        'total_sr_reviews', 'category_progress', 'weak_categories', 'strong_categories',
        'current_category_focus', 'daily_question_goal', 'daily_time_goal', 'daily_streak',
        'longest_daily_streak', 'last_activity_date', 'daily_goal_met_count',
        'category_abilities', 'learning_velocity', 'retention_rate', 'time_invested'
    ]) AS column_name
),
actual_columns AS (
    SELECT column_name
    FROM information_schema.columns 
    WHERE table_name = 'personal_learning_plan'
)
SELECT 
    ec.column_name,
    CASE 
        WHEN ac.column_name IS NOT NULL THEN 'EXISTS' 
        ELSE 'MISSING' 
    END as status
FROM expected_columns ec
LEFT JOIN actual_columns ac ON ec.column_name = ac.column_name
ORDER BY 
    CASE WHEN ac.column_name IS NULL THEN 0 ELSE 1 END,
    ec.column_name;

-- Show the critical missing columns
SELECT 'CRITICAL MISSING COLUMNS:' as info
UNION ALL
SELECT column_name
FROM expected_columns ec
LEFT JOIN actual_columns ac ON ec.column_name = ac.column_name
WHERE ac.column_name IS NULL
AND ec.column_name IN (
    'current_category_focus', 'weak_categories', 'strong_categories', 
    'category_abilities', 'time_invested', 'daily_question_goal',
    'daily_time_goal', 'daily_streak', 'last_activity_date'
);




