"""Add new BIG domains - Complete migration

Revision ID: add_new_big_domains_complete
Revises: add_new_domains_001
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_new_big_domains_complete'
down_revision = 'add_new_domains_001'
branch_labels = None
depends_on = None

def upgrade():
    """Добавить новые домены в базу данных"""
    
    # Новые домены с полной информацией
    new_domains_data = [
        {
            'code': 'EMERGENCY',
            'name': 'Неотложная помощь',
            'description': 'Критические ситуации, анафилаксия, сердечно-сосудистые кризы, острые состояния',
            'weight_percentage': 8.0,
            'order': 16,
            'is_active': True
        },
        {
            'code': 'SYSTEMIC',
            'name': 'Системные заболевания',
            'description': 'Диабет, сердечно-сосудистые заболевания, почечная недостаточность, аутоиммунные заболевания',
            'weight_percentage': 7.0,
            'order': 17,
            'is_active': True
        },
        {
            'code': 'PHARMA',
            'name': 'Фармакология',
            'description': 'Лекарственные взаимодействия, антикоагулянты, безопасность медикаментов, побочные эффекты',
            'weight_percentage': 6.0,
            'order': 18,
            'is_active': True
        },
        {
            'code': 'INFECTION',
            'name': 'Инфекционный контроль',
            'description': 'Стерилизация, ВИЧ/HBV профилактика, COVID-19 протоколы, инфекционная безопасность',
            'weight_percentage': 5.0,
            'order': 19,
            'is_active': True
        },
        {
            'code': 'SPECIAL',
            'name': 'Специальные группы пациентов',
            'description': 'Дементия, аутизм, беженцы, паллиативная помощь, пациенты с ограниченными возможностями',
            'weight_percentage': 4.0,
            'order': 20,
            'is_active': True
        },
        {
            'code': 'DIAGNOSIS',
            'name': 'Сложная диагностика',
            'description': 'Дифференциальная диагностика, редкие синдромы, сложные клинические случаи',
            'weight_percentage': 6.0,
            'order': 21,
            'is_active': True
        },
        {
            'code': 'DUTCH',
            'name': 'Голландская система здравоохранения',
            'description': 'AVG/GDPR, BIG-wet, zorgverzekering, голландские протоколы и стандарты',
            'weight_percentage': 3.0,
            'order': 22,
            'is_active': True
        },
        {
            'code': 'PROFESSIONAL',
            'name': 'Профессиональное развитие',
            'description': 'Nascholing, peer review, профессиональная этика, непрерывное образование',
            'weight_percentage': 2.0,
            'order': 23,
            'is_active': True
        }
    ]
    
    # Вставить новые домены
    for domain_data in new_domains_data:
        # Проверить, существует ли домен
        existing = op.get_bind().execute(
            f"SELECT id FROM big_domain WHERE code = '{domain_data['code']}'"
        ).fetchone()
        
        if not existing:
            op.execute(f"""
                INSERT INTO big_domain (code, name, description, weight_percentage, "order", is_active, created_at)
                VALUES (
                    '{domain_data['code']}',
                    '{domain_data['name']}',
                    '{domain_data['description']}',
                    {domain_data['weight_percentage']},
                    {domain_data['order']},
                    {domain_data['is_active']},
                    datetime('now')
                )
            """)
        else:
            # Обновить существующий домен
            op.execute(f"""
                UPDATE big_domain 
                SET name = '{domain_data['name']}',
                    description = '{domain_data['description']}',
                    weight_percentage = {domain_data['weight_percentage']},
                    "order" = {domain_data['order']},
                    is_active = {domain_data['is_active']}
                WHERE code = '{domain_data['code']}'
            """)
    
    # Обновить веса существующих доменов для поддержания баланса
    weight_adjustments = {
        'THER': 12.0,      # Терапевтическая стоматология - высокий приоритет
        'SURG': 10.0,      # Хирургическая стоматология - высокий приоритет
        'PROTH': 8.0,      # Ортопедическая стоматология - высокий приоритет
        'PEDI': 7.0,       # Детская стоматология - высокий приоритет
        'PARO': 8.0,       # Пародонтология - высокий приоритет
        'ORTHO': 6.0,      # Ортодонтия - средний приоритет
        'PREV': 5.0,       # Профилактика - средний приоритет
        'ANATOMIE': 4.0,   # Анатомия - базовый
        'FYSIOLOGIE': 4.0, # Физиология - базовый
        'PATHOLOGIE': 5.0, # Патология - средний приоритет
        'MICROBIOLOGIE': 3.0, # Микробиология - базовый
        'MATERIAALKUNDE': 3.0, # Материаловедение - базовый
        'RADIOLOGIE': 4.0, # Рентгенология - базовый
        'ETHIEK': 3.0,     # Этика - базовый
        'ALGEMENE_GENEESKUNDE': 2.0 # Общая медицина - базовый
    }
    
    for code, new_weight in weight_adjustments.items():
        op.execute(f"""
            UPDATE big_domain 
            SET weight_percentage = {new_weight}
            WHERE code = '{code}'
        """)

def downgrade():
    """Удалить новые домены из базы данных"""
    
    # Удалить новые домены
    new_domain_codes = [
        'EMERGENCY', 'SYSTEMIC', 'PHARMA', 'INFECTION', 
        'SPECIAL', 'DIAGNOSIS', 'DUTCH', 'PROFESSIONAL'
    ]
    
    for code in new_domain_codes:
        op.execute(f"DELETE FROM big_domain WHERE code = '{code}'")
    
    # Восстановить оригинальные веса
    original_weights = {
        'THER': 25.0,
        'SURG': 20.0,
        'PROTH': 15.0,
        'PEDI': 10.0,
        'PARO': 10.0,
        'ORTHO': 8.0,
        'PREV': 7.0,
        'ETHIEK': 5.0
    }
    
    for code, original_weight in original_weights.items():
        op.execute(f"""
            UPDATE big_domain 
            SET weight_percentage = {original_weight}
            WHERE code = '{code}'
        """) 