-- Применить миграцию learning_map_tour_completed напрямую
-- Это безопасно, так как миграция уже была применена локально

ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS learning_map_tour_completed BOOLEAN NOT NULL DEFAULT false;

-- Обновить версию миграции в alembic_version (если нужно)
-- Но лучше использовать flask db stamp для этого
