-- ============================================================================
-- МИГРАЦИЯ: Добавление отсутствующих столбцов в таблицы
-- ============================================================================
-- 
-- ПРОБЛЕМА: На продакшене отсутствуют столбцы:
-- 1. questions.profession - для фильтрации вопросов по профессиям
-- 2. personal_learning_plan.spaced_repetition_enabled - для включения/отключения spaced repetition
-- 3. personal_learning_plan.sr_algorithm - алгоритм spaced repetition
-- 4. personal_learning_plan.next_review_date - дата следующего повторения
-- 5. personal_learning_plan.sr_streak - серия повторений
-- 6. personal_learning_plan.total_sr_reviews - всего повторений
--
-- ДАТА: 2025-10-26
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Добавляем поле profession в таблицу questions
-- ============================================================================

-- Проверяем, существует ли поле
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'questions' 
        AND column_name = 'profession'
    ) THEN
        -- Добавляем поле profession
        ALTER TABLE questions 
        ADD COLUMN profession VARCHAR(50);
        
        -- Создаем индекс для быстрой фильтрации
        CREATE INDEX IF NOT EXISTS ix_questions_profession 
        ON questions(profession);
        
        -- Добавляем комментарий
        COMMENT ON COLUMN questions.profession IS 'Профессия (tandarts, apotheker, huisarts, verpleegkundige)';
        
        RAISE NOTICE '✅ Столбец questions.profession добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.profession уже существует';
    END IF;
END $$;

-- ============================================================================
-- 2. Добавляем поля Spaced Repetition в personal_learning_plan
-- ============================================================================

-- spaced_repetition_enabled
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'spaced_repetition_enabled'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN spaced_repetition_enabled BOOLEAN DEFAULT TRUE;
        
        RAISE NOTICE '✅ Столбец personal_learning_plan.spaced_repetition_enabled добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.spaced_repetition_enabled уже существует';
    END IF;
END $$;

-- sr_algorithm
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'sr_algorithm'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN sr_algorithm VARCHAR(20) DEFAULT 'sm2';
        
        RAISE NOTICE '✅ Столбец personal_learning_plan.sr_algorithm добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.sr_algorithm уже существует';
    END IF;
END $$;

-- next_review_date
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'next_review_date'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN next_review_date DATE;
        
        RAISE NOTICE '✅ Столбец personal_learning_plan.next_review_date добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.next_review_date уже существует';
    END IF;
END $$;

-- sr_streak
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'sr_streak'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN sr_streak INTEGER DEFAULT 0;
        
        RAISE NOTICE '✅ Столбец personal_learning_plan.sr_streak добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.sr_streak уже существует';
    END IF;
END $$;

-- total_sr_reviews
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name = 'total_sr_reviews'
    ) THEN
        ALTER TABLE personal_learning_plan 
        ADD COLUMN total_sr_reviews INTEGER DEFAULT 0;
        
        RAISE NOTICE '✅ Столбец personal_learning_plan.total_sr_reviews добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.total_sr_reviews уже существует';
    END IF;
END $$;

-- ============================================================================
-- 3. Проверка успешности миграции
-- ============================================================================

DO $$ 
DECLARE
    questions_ok BOOLEAN := FALSE;
    plan_ok BOOLEAN := FALSE;
BEGIN
    -- Проверяем questions
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'profession'
    ) INTO questions_ok;
    
    -- Проверяем personal_learning_plan
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' 
        AND column_name IN ('spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak', 'total_sr_reviews')
    ) INTO plan_ok;
    
    IF questions_ok AND plan_ok THEN
        RAISE NOTICE '';
        RAISE NOTICE '✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО';
        RAISE NOTICE '✅ Все необходимые столбцы добавлены';
    ELSE
        RAISE WARNING '⚠️  Не все столбцы были добавлены';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- ИСТОРИЯ ИЗМЕНЕНИЙ
-- ============================================================================
-- 2025-10-26: Первая версия миграции
--             Добавлены отсутствующие столбцы для работы с профессиями 
--             и spaced repetition
-- ============================================================================
