"""restructure_domains_to_30_domains

Revision ID: 61b8e1269fad
Revises: 63cc688d32c8
Create Date: 2025-07-28 22:32:03.690245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '61b8e1269fad'
down_revision = '63cc688d32c8'
branch_labels = None
depends_on = None


def upgrade():
    """Реструктуризация доменов BI-toets до 30 доменов"""
    
    # 1. Добавляем новые поля в таблицу big_domain
    op.add_column('big_domain', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('big_domain', sa.Column('exam_type', sa.String(50), nullable=True))
    op.add_column('big_domain', sa.Column('is_critical', sa.Boolean(), nullable=True, default=False))
    op.add_column('big_domain', sa.Column('subcategories', sa.Text(), nullable=True))
    op.add_column('big_domain', sa.Column('historical_questions', sa.Boolean(), nullable=True, default=True))
    op.add_column('big_domain', sa.Column('open_book', sa.Boolean(), nullable=True, default=False))
    
    # 2. Создаем индексы для новых полей
    op.create_index(op.f('ix_big_domain_category'), 'big_domain', ['category'], unique=False)
    op.create_index(op.f('ix_big_domain_exam_type'), 'big_domain', ['exam_type'], unique=False)
    op.create_index(op.f('ix_big_domain_is_critical'), 'big_domain', ['is_critical'], unique=False)
    
    # 3. Удаляем дублирующие домены
    op.execute("DELETE FROM big_domain WHERE code IN ('FARMACOLOGIE', 'DIAGNOSIS_SPECIAL')")
    
    # 4. Обновляем существующие домены
    # Объединяем PHARMA в PHARMACOLOGY
    op.execute("UPDATE big_domain SET code = 'PHARMACOLOGY', name = 'Фармакология' WHERE code = 'PHARMA'")
    
    # Обновляем веса и категории существующих доменов
    domain_updates = [
        # Критические домены с увеличенными весами
        ("UPDATE big_domain SET weight_percentage = 15.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'THER'"),
        ("UPDATE big_domain SET weight_percentage = 10.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'SURG'"),
        ("UPDATE big_domain SET weight_percentage = 10.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'EMERGENCY'"),
        ("UPDATE big_domain SET weight_percentage = 7.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'SYSTEMIC'"),
        ("UPDATE big_domain SET weight_percentage = 8.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'PHARMACOLOGY'"),
        ("UPDATE big_domain SET weight_percentage = 10.0, category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 1 WHERE code = 'DIAGNOSIS'"),
        
        # Остальные теоретические домены
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PROTH'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PEDI'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PARO'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'ORTHO'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PREV'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'ANATOMIE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'FYSIOLOGIE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PATHOLOGIE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'MICROBIOLOGIE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'MATERIAALKUNDE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'RADIOLOGIE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'ALGEMENE_GENEESKUNDE'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'INFECTION'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'SPECIAL'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'DUTCH'"),
        ("UPDATE big_domain SET category = 'THEORETICAL', exam_type = 'multiple_choice', is_critical = 0 WHERE code = 'PROFESSIONAL'"),
        
        # Клинические домены
        ("UPDATE big_domain SET category = 'CLINICAL', exam_type = 'case_study', is_critical = 0 WHERE code = 'ETHIEK'"),
    ]
    
    for update_sql in domain_updates:
        op.execute(update_sql)
    
    # 5. Добавляем новые домены
    new_domains = [
        # МЕТОДОЛОГИЯ (Open Book)
        {
            'code': 'STATISTICS',
            'name': 'Статистика и анализ данных',
            'weight_percentage': 6.0,
            'category': 'METHODOLOGY',
            'exam_type': 'open_book',
            'is_critical': True,
            'open_book': True,
            'subcategories': '["descriptive", "inferential", "clinical_trials"]'
        },
        {
            'code': 'RESEARCH_METHOD',
            'name': 'Методология исследований',
            'weight_percentage': 6.0,
            'category': 'METHODOLOGY',
            'exam_type': 'open_book',
            'is_critical': True,
            'open_book': True,
            'subcategories': '["study_design", "biostatistics", "evidence_based"]'
        },
        
        # ПРАКТИЧЕСКИЕ НАВЫКИ (Simodont)
        {
            'code': 'PRACTICAL_SKILLS',
            'name': 'Практические навыки',
            'weight_percentage': 15.0,
            'category': 'PRACTICAL',
            'exam_type': 'practical',
            'is_critical': True,
            'open_book': False,
            'subcategories': '["manual_skills", "caries_excavation", "endo_prep", "crown_prep", "gebits_reinigung"]'
        },
        
        # КЛИНИЧЕСКИЕ НАВЫКИ
        {
            'code': 'TREATMENT_PLANNING',
            'name': 'Планирование лечения',
            'weight_percentage': 12.0,
            'category': 'CLINICAL',
            'exam_type': 'case_study',
            'is_critical': True,
            'open_book': False,
            'subcategories': '["comprehensive", "endodontic", "trauma_resorption", "cariology_pediatric"]'
        },
        {
            'code': 'COMMUNICATION',
            'name': 'Коммуникативные навыки',
            'weight_percentage': 8.0,
            'category': 'CLINICAL',
            'exam_type': 'interview',
            'is_critical': True,
            'open_book': False,
            'subcategories': '["intake_gesprek", "patient_interaction", "dutch_medical"]'
        }
    ]
    
    for domain in new_domains:
        op.execute(f"""
            INSERT INTO big_domain (
                code, name, weight_percentage, category, exam_type, 
                is_critical, open_book, subcategories, historical_questions, is_active
            ) VALUES (
                '{domain['code']}', '{domain['name']}', {domain['weight_percentage']}, 
                '{domain['category']}', '{domain['exam_type']}', {1 if domain['is_critical'] else 0},
                {1 if domain['open_book'] else 0}, '{domain['subcategories']}', 1, 1
            )
        """)


def downgrade():
    """Откат реструктуризации доменов"""
    
    # 1. Удаляем новые домены
    op.execute("DELETE FROM big_domain WHERE code IN ('STATISTICS', 'RESEARCH_METHOD', 'PRACTICAL_SKILLS', 'TREATMENT_PLANNING', 'COMMUNICATION')")
    
    # 2. Восстанавливаем дублирующие домены
    op.execute("INSERT INTO big_domain (code, name, weight_percentage, is_active) VALUES ('FARMACOLOGIE', 'Фармакология (альтернативное название)', 3.0, 1)")
    op.execute("INSERT INTO big_domain (code, name, weight_percentage, is_active) VALUES ('DIAGNOSIS_SPECIAL', 'Специальная диагностика', 3.0, 1)")
    
    # 3. Восстанавливаем PHARMA
    op.execute("UPDATE big_domain SET code = 'PHARMA', name = 'Фармакология' WHERE code = 'PHARMACOLOGY'")
    
    # 4. Восстанавливаем старые веса
    op.execute("UPDATE big_domain SET weight_percentage = 12.0 WHERE code = 'THER'")
    op.execute("UPDATE big_domain SET weight_percentage = 10.0 WHERE code = 'SURG'")
    op.execute("UPDATE big_domain SET weight_percentage = 8.0 WHERE code = 'EMERGENCY'")
    op.execute("UPDATE big_domain SET weight_percentage = 7.0 WHERE code = 'SYSTEMIC'")
    op.execute("UPDATE big_domain SET weight_percentage = 6.0 WHERE code = 'PHARMA'")
    op.execute("UPDATE big_domain SET weight_percentage = 6.0 WHERE code = 'DIAGNOSIS'")
    
    # 5. Удаляем индексы
    op.drop_index(op.f('ix_big_domain_is_critical'), table_name='big_domain')
    op.drop_index(op.f('ix_big_domain_exam_type'), table_name='big_domain')
    op.drop_index(op.f('ix_big_domain_category'), table_name='big_domain')
    
    # 6. Удаляем новые поля
    op.drop_column('big_domain', 'open_book')
    op.drop_column('big_domain', 'historical_questions')
    op.drop_column('big_domain', 'subcategories')
    op.drop_column('big_domain', 'is_critical')
    op.drop_column('big_domain', 'exam_type')
    op.drop_column('big_domain', 'category')
