#!/bin/bash

# 🚀 Production Migration Script for Render Shell
# Запустить: bash scripts/run_migration_render.sh

echo "=================================================="
echo "🚀 Production Migration - Personal Learning Plan"
echo "=================================================="
echo ""

# Проверяем, что есть DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ОШИБКА: DATABASE_URL не установлена"
    echo "Установите переменную окружения DATABASE_URL в Render Dashboard"
    exit 1
fi

echo "✅ DATABASE_URL найдена"
echo ""

# Запускаем миграцию
echo "⏳ Запуск миграции..."
echo ""

psql "$DATABASE_URL" << 'MIGRATION_SQL'
-- ============================================================================
-- МИГРАЦИЯ: Добавление отсутствующих столбцов в таблицы
-- ============================================================================

BEGIN;

-- ============================================================================
-- Добавляем недостающие столбцы в personal_learning_plan
-- ============================================================================

-- category_progress
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' AND column_name = 'category_progress'
    ) THEN
        ALTER TABLE personal_learning_plan ADD COLUMN category_progress JSON;
        RAISE NOTICE '✅ Столбец personal_learning_plan.category_progress добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.category_progress уже существует';
    END IF;
END $$;

-- weak_categories
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' AND column_name = 'weak_categories'
    ) THEN
        ALTER TABLE personal_learning_plan ADD COLUMN weak_categories JSON;
        RAISE NOTICE '✅ Столбец personal_learning_plan.weak_categories добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.weak_categories уже существует';
    END IF;
END $$;

-- strong_categories
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' AND column_name = 'strong_categories'
    ) THEN
        ALTER TABLE personal_learning_plan ADD COLUMN strong_categories JSON;
        RAISE NOTICE '✅ Столбец personal_learning_plan.strong_categories добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.strong_categories уже существует';
    END IF;
END $$;

-- category_abilities
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'personal_learning_plan' AND column_name = 'category_abilities'
    ) THEN
        ALTER TABLE personal_learning_plan ADD COLUMN category_abilities JSON;
        RAISE NOTICE '✅ Столбец personal_learning_plan.category_abilities добавлен';
    ELSE
        RAISE NOTICE 'ℹ️  Столбец personal_learning_plan.category_abilities уже существует';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- Проверка успешности миграции
-- ============================================================================

DO $$ 
DECLARE
    category_columns_count INTEGER := 0;
BEGIN
    -- Проверяем personal_learning_plan
    SELECT COUNT(*) INTO category_columns_count
    FROM information_schema.columns 
    WHERE table_name = 'personal_learning_plan' 
    AND column_name IN ('category_progress', 'weak_categories', 'strong_categories', 'category_abilities');
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 РЕЗУЛЬТАТЫ МИГРАЦИИ:';
    RAISE NOTICE '   personal_learning_plan: % / 4 столбцов найдено', category_columns_count;
    
    IF category_columns_count = 4 THEN
        RAISE NOTICE '';
        RAISE NOTICE '✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО';
        RAISE NOTICE '✅ Все необходимые столбцы добавлены';
    ELSE
        RAISE WARNING '⚠️  Не все столбцы были добавлены';
    END IF;
END $$;

MIGRATION_SQL

RESULT=$?

echo ""
echo "=================================================="
if [ $RESULT -eq 0 ]; then
    echo "✅ Миграция выполнена успешно!"
    echo "=================================================="
    echo ""
    echo "🎉 Production БД обновлена!"
    echo "Новые пользователи теперь смогут:"
    echo "  ✓ Пройти диагностику"
    echo "  ✓ Открыть Learning Map"
    echo "  ✓ Видеть свой прогресс"
    echo ""
else
    echo "❌ Ошибка при выполнении миграции!"
    echo "=================================================="
    exit 1
fi
