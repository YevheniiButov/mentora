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
-- 1. Добавляем недостающие поля в таблицу questions
-- ============================================================================

-- big_domain_id
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'big_domain_id'
    ) THEN
        ALTER TABLE questions ADD COLUMN big_domain_id INTEGER;
        CREATE INDEX IF NOT EXISTS ix_questions_big_domain_id ON questions(big_domain_id);
        RAISE NOTICE '✅ Столбец questions.big_domain_id добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.big_domain_id уже существует';
    END IF;
END $$;

-- question_type
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'question_type'
    ) THEN
        ALTER TABLE questions ADD COLUMN question_type VARCHAR(50) DEFAULT 'multiple_choice';
        RAISE NOTICE '✅ Столбец questions.question_type добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.question_type уже существует';
    END IF;
END $$;

-- clinical_context
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'clinical_context'
    ) THEN
        ALTER TABLE questions ADD COLUMN clinical_context TEXT;
        RAISE NOTICE '✅ Столбец questions.clinical_context добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.clinical_context уже существует';
    END IF;
END $$;

-- learning_objectives
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'learning_objectives'
    ) THEN
        ALTER TABLE questions ADD COLUMN learning_objectives JSON;
        RAISE NOTICE '✅ Столбец questions.learning_objectives добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.learning_objectives уже существует';
    END IF;
END $$;

-- profession
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'questions' AND column_name = 'profession'
    ) THEN
        ALTER TABLE questions ADD COLUMN profession VARCHAR(50);
        CREATE INDEX IF NOT EXISTS ix_questions_profession ON questions(profession);
        RAISE NOTICE '✅ Столбец questions.profession добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец questions.profession уже существует';
    END IF;
END $$;

-- ============================================================================
-- 2. Добавляем связь с big_domain (foreign key constraint)
-- ============================================================================

DO $$ 
BEGIN
    -- Проверяем, существует ли foreign key
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'questions_big_domain_id_fkey'
        AND table_name = 'questions'
    ) THEN
        -- Добавляем foreign key constraint
        ALTER TABLE questions 
        ADD CONSTRAINT questions_big_domain_id_fkey 
        FOREIGN KEY (big_domain_id) REFERENCES big_domain(id);
        
        RAISE NOTICE '✅ Foreign key constraint добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Foreign key constraint уже существует';
    END IF;
END $$;

-- ============================================================================
-- 3. Добавляем поля Spaced Repetition в personal_learning_plan
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
-- 4. Проверка успешности миграции
-- ============================================================================

DO $$ 
DECLARE
    questions_columns_count INTEGER := 0;
    plan_columns_count INTEGER := 0;
BEGIN
    -- Проверяем questions
    SELECT COUNT(*) INTO questions_columns_count
    FROM information_schema.columns 
    WHERE table_name = 'questions' 
    AND column_name IN ('big_domain_id', 'question_type', 'clinical_context', 'learning_objectives', 'profession');
    
    -- Проверяем personal_learning_plan
    SELECT COUNT(*) INTO plan_columns_count
    FROM information_schema.columns 
    WHERE table_name = 'personal_learning_plan' 
    AND column_name IN ('spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak', 'total_sr_reviews');
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 РЕЗУЛЬТАТЫ МИГРАЦИИ:';
    RAISE NOTICE '   questions: % / 5 столбцов добавлено', questions_columns_count;
    RAISE NOTICE '   personal_learning_plan: % / 5 столбцов добавлено', plan_columns_count;
    
    IF questions_columns_count = 5 AND plan_columns_count = 5 THEN
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
