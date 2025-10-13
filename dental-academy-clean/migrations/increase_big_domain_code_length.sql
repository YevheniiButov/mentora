-- Увеличение длины поля code в таблице big_domain с 20 до 50 символов
-- Необходимо для поддержки длинных кодов доменов (например, THERAPEUTIC_DENTISTRY)

ALTER TABLE big_domain 
ALTER COLUMN code TYPE VARCHAR(50);

-- Также увеличим длину для category и exam_type на всякий случай
ALTER TABLE big_domain 
ALTER COLUMN category TYPE VARCHAR(100);

ALTER TABLE big_domain 
ALTER COLUMN exam_type TYPE VARCHAR(100);

