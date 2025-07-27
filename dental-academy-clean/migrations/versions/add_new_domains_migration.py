"""Add new domains to BI-toets system

Revision ID: add_new_domains_001
Revises: add_created_at_big_domain
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_new_domains_001'
down_revision = 'add_created_at_big_domain'
branch_labels = None
depends_on = None

def upgrade():
    """Add new domains to the big_domain table"""
    
    # New domains data
    new_domains = [
        {
            'code': 'EMERGENCY',
            'name': 'Неотложная помощь',
            'description': 'Экстренная стоматологическая помощь, острые состояния, неотложные вмешательства',
            'weight_percentage': 8.0,
            'order': 16,
            'is_active': True
        },
        {
            'code': 'SYSTEMIC',
            'name': 'Системные заболевания',
            'description': 'Системные заболевания и их влияние на стоматологическую практику',
            'weight_percentage': 7.0,
            'order': 17,
            'is_active': True
        },
        {
            'code': 'PHARMA',
            'name': 'Фармакология',
            'description': 'Фармакология в стоматологии, лекарственные взаимодействия, побочные эффекты',
            'weight_percentage': 6.0,
            'order': 18,
            'is_active': True
        },
        {
            'code': 'INFECTION',
            'name': 'Инфекционный контроль',
            'description': 'Инфекционный контроль, стерилизация, дезинфекция, COVID-19 протоколы',
            'weight_percentage': 5.0,
            'order': 19,
            'is_active': True
        },
        {
            'code': 'SPECIAL',
            'name': 'Специальные группы пациентов',
            'description': 'Стоматологическая помощь пациентам со специальными потребностями',
            'weight_percentage': 4.0,
            'order': 20,
            'is_active': True
        },
        {
            'code': 'DIAGNOSIS',
            'name': 'Сложная диагностика',
            'description': 'Сложные диагностические случаи, дифференциальная диагностика',
            'weight_percentage': 6.0,
            'order': 21,
            'is_active': True
        },
        {
            'code': 'DUTCH',
            'name': 'Голландская система здравоохранения',
            'description': 'Голландская система здравоохранения, BIG, AVG/GDPR, местные протоколы',
            'weight_percentage': 3.0,
            'order': 22,
            'is_active': True
        },
        {
            'code': 'PROFESSIONAL',
            'name': 'Профессиональное развитие',
            'description': 'Профессиональная этика, непрерывное образование, коллегиальная оценка',
            'weight_percentage': 2.0,
            'order': 23,
            'is_active': True
        }
    ]
    
    # Insert new domains
    for domain_data in new_domains:
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
    
    # Update existing domain weights to maintain total 100%
    # Reduce some existing weights to accommodate new domains
    weight_adjustments = {
        'THER': 12.0,      # Keep high priority
        'SURG': 10.0,      # Keep high priority
        'PROTH': 8.0,      # Keep high priority
        'PEDI': 7.0,       # Keep high priority
        'PARO': 8.0,       # Keep high priority
        'ORTHO': 6.0,      # Keep high priority
        'PREV': 5.0,       # Keep high priority
        'ANATOMIE': 4.0,   # Keep moderate
        'FYSIOLOGIE': 4.0, # Keep moderate
        'PATHOLOGIE': 5.0, # Keep moderate
        'MICROBIOLOGIE': 3.0, # Keep low
        'MATERIAALKUNDE': 3.0, # Keep low
        'RADIOLOGIE': 4.0, # Keep moderate
        'ETHIEK': 3.0,     # Keep low
        'ALGEMENE_GENEESKUNDE': 2.0 # Keep low
    }
    
    for code, new_weight in weight_adjustments.items():
        op.execute(f"""
            UPDATE big_domain 
            SET weight_percentage = {new_weight}
            WHERE code = '{code}'
        """)

def downgrade():
    """Remove new domains from the big_domain table"""
    
    # Remove new domains
    new_domain_codes = [
        'EMERGENCY', 'SYSTEMIC', 'PHARMA', 'INFECTION', 
        'SPECIAL', 'DIAGNOSIS', 'DUTCH', 'PROFESSIONAL'
    ]
    
    for code in new_domain_codes:
        op.execute(f"DELETE FROM big_domain WHERE code = '{code}'")
    
    # Restore original weights
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