#!/bin/bash
# ============================================================================
# Скрипт для применения миграции БД на продакшене
# ============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL не установлен!"
    log_info "Установите переменную окружения: export DATABASE_URL=postgresql://..."
    exit 1
fi

log_info "Начало применения миграции БД..."

# Путь к файлу миграции
MIGRATION_FILE="migrations/add_missing_columns.sql"

# Проверка существования файла миграции
if [ ! -f "$MIGRATION_FILE" ]; then
    log_error "Файл миграции не найден: $MIGRATION_FILE"
    exit 1
fi

log_info "Найден файл миграции: $MIGRATION_FILE"

# Применение миграции
log_info "Применение миграции к базе данных..."
psql "$DATABASE_URL" -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    log_info "✅ Миграция успешно применена!"
else
    log_error "❌ Ошибка при применении миграции"
    exit 1
fi

# Проверка результатов
log_info "Проверка результатов миграции..."

psql "$DATABASE_URL" -c "
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'questions' AND column_name = 'profession'
        ) THEN '✅ questions.profession'
        ELSE '❌ questions.profession'
    END as questions_profession,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'personal_learning_plan' 
            AND column_name = 'spaced_repetition_enabled'
        ) THEN '✅ personal_learning_plan.spaced_repetition_enabled'
        ELSE '❌ personal_learning_plan.spaced_repetition_enabled'
    END as spaced_repetition_enabled,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'personal_learning_plan' 
            AND column_name = 'sr_algorithm'
        ) THEN '✅ personal_learning_plan.sr_algorithm'
        ELSE '❌ personal_learning_plan.sr_algorithm'
    END as sr_algorithm;
"

log_info "🎉 Миграция завершена!"
log_info "Пожалуйста, перезапустите приложение для применения изменений"







