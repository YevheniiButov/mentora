-- ============================================================================
-- МИГРАЦИЯ: Добавление системы медицинской терминологии (Phase 1)
-- ============================================================================
-- 
-- Создает две новые таблицы для системы flashcard-ов медицинских терминов:
-- 1. medical_term - словарь медицинских терминов на 8 языках
-- 2. user_term_progress - прогресс пользователя с системой SM-2 спейсд репетишена
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- Таблица medical_term - словарь медицинских терминов
-- ============================================================================

CREATE TABLE IF NOT EXISTS medical_term (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Основной термин на голландском (источник)
    term_nl VARCHAR(200) NOT NULL UNIQUE,
    definition_nl TEXT,
    
    -- Переводы на 8 языков
    term_en VARCHAR(200),
    term_ru VARCHAR(200),
    term_uk VARCHAR(200),
    term_es VARCHAR(200),
    term_pt VARCHAR(200),
    term_tr VARCHAR(200),
    term_fa VARCHAR(200),
    term_ar VARCHAR(200),
    
    -- Метаданные
    category VARCHAR(50) NOT NULL,  -- anatomy, symptoms, diseases, treatments, dental, hospital, communication
    difficulty INTEGER DEFAULT 1,   -- 1-5 scale
    frequency INTEGER DEFAULT 1,    -- 1-5 scale (how common)
    
    -- Аудио для произношения
    audio_url VARCHAR(500),
    
    -- Временные метки
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для эффективных запросов
CREATE INDEX IF NOT EXISTS ix_medical_term_nl ON medical_term(term_nl);
CREATE INDEX IF NOT EXISTS ix_medical_term_category ON medical_term(category);

-- ============================================================================
-- Таблица user_term_progress - прогресс пользователя в изучении терминов
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_term_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Связи с пользователем и термином
    user_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    
    -- SM-2 алгоритм спейсд репетишена
    ease_factor FLOAT DEFAULT 2.5,      -- 1.3 - 2.6
    interval INTEGER DEFAULT 1,         -- дни до следующего повтора
    repetitions INTEGER DEFAULT 0,      -- кол-во успешных повторов
    next_review DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Статистика
    times_reviewed INTEGER DEFAULT 0,   -- всего попыток
    times_correct INTEGER DEFAULT 0,    -- правильных ответов
    mastery_level INTEGER DEFAULT 0,    -- 0-5 scale (0=новичок, 5=мастер)
    last_quality INTEGER,               -- качество последнего ответа (1-5)
    
    -- Временные метки
    last_reviewed DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES medical_term(id) ON DELETE CASCADE,
    
    -- Уникальное сочетание пользователя и термина
    UNIQUE(user_id, term_id)
);

-- Индексы для эффективных запросов
CREATE INDEX IF NOT EXISTS ix_user_term_progress_user ON user_term_progress(user_id);
CREATE INDEX IF NOT EXISTS ix_user_term_progress_user_next_review ON user_term_progress(user_id, next_review);
CREATE INDEX IF NOT EXISTS ix_user_term_progress_is_due ON user_term_progress(next_review);

COMMIT;

-- ============================================================================
-- Проверка успешности миграции
-- ============================================================================

-- Проверяем, что таблицы созданы
SELECT COUNT(*) as medical_term_count FROM medical_term;
SELECT COUNT(*) as user_term_progress_count FROM user_term_progress;




