#!/usr/bin/env python3
"""
Миграция к системе специальностей
Создание специальностей, доменов и обновление существующих данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import Question, IRTParameters, DiagnosticSession, User, BIGDomain
from models_specialty import Specialty, SpecialtyDomain, PilotResponse, DiagnosticResult

def create_specialties():
    """Создать специальности"""
    with app.app_context():
        try:
            # 1. Создать специальность "Стоматолог"
            dentist_specialty = Specialty(
                code='DENTIST',
                name='Стоматолог',
                name_en='Dentist',
                name_nl='Tandarts',
                is_active=True,
                is_calibrated=True,
                total_questions=410,
                calibrated_questions=410,
                irt_model='3PL',
                calibration_threshold=5
            )
            
            # Проверяем, не существует ли уже
            existing_dentist = Specialty.query.filter_by(code='DENTIST').first()
            if not existing_dentist:
                db.session.add(dentist_specialty)
                print("✅ Created DENTIST specialty")
            else:
                dentist_specialty = existing_dentist
                print("✅ DENTIST specialty already exists")
            
            # 2. Создать специальность "Врач общей практики"
            gp_specialty = Specialty(
                code='GP',
                name='Врач общей практики',
                name_en='General Practitioner',
                name_nl='Huisarts',
                is_active=True,
                is_calibrated=False,
                total_questions=0,
                calibrated_questions=0,
                irt_model='3PL',
                calibration_threshold=5
            )
            
            existing_gp = Specialty.query.filter_by(code='GP').first()
            if not existing_gp:
                db.session.add(gp_specialty)
                print("✅ Created GP specialty")
            else:
                gp_specialty = existing_gp
                print("✅ GP specialty already exists")
            
            db.session.commit()
            return dentist_specialty, gp_specialty
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating specialties: {str(e)}")
            raise

def create_dentist_domains(dentist_specialty):
    """Создать домены для стоматологов"""
    with app.app_context():
        try:
            # Домены стоматологов (из существующей системы)
            dentist_domains = [
                # ТЕОРЕТИЧЕСКИЕ ДОМЕНЫ (70%)
                {'code': 'PHARMACOLOGY', 'name': 'Фармакология', 'name_en': 'Pharmacology', 'name_nl': 'Farmacologie', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'THERAPEUTIC_DENTISTRY', 'name': 'Терапевтическая стоматология', 'name_en': 'Therapeutic Dentistry', 'name_nl': 'Therapeutische tandheelkunde', 'weight': 8.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'SURGICAL_DENTISTRY', 'name': 'Хирургическая стоматология', 'name_en': 'Surgical Dentistry', 'name_nl': 'Chirurgische tandheelkunde', 'weight': 7.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PROSTHODONTICS', 'name': 'Ортопедическая стоматология', 'name_en': 'Prosthodontics', 'name_nl': 'Prosthodontiek', 'weight': 6.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PEDIATRIC_DENTISTRY', 'name': 'Детская стоматология', 'name_en': 'Pediatric Dentistry', 'name_nl': 'Kindertandheelkunde', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PERIODONTOLOGY', 'name': 'Пародонтология', 'name_en': 'Periodontology', 'name_nl': 'Parodontologie', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'ORTHODONTICS', 'name': 'Ортодонтия', 'name_en': 'Orthodontics', 'name_nl': 'Orthodontie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': False},
                {'code': 'PREVENTIVE_DENTISTRY', 'name': 'Профилактическая стоматология', 'name_en': 'Preventive Dentistry', 'name_nl': 'Preventieve tandheelkunde', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'ANATOMY', 'name': 'Анатомия', 'name_en': 'Anatomy', 'name_nl': 'Anatomie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PHYSIOLOGY', 'name': 'Физиология', 'name_en': 'Physiology', 'name_nl': 'Fysiologie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PATHOLOGY', 'name': 'Патология', 'name_en': 'Pathology', 'name_nl': 'Pathologie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'RADIOLOGY', 'name': 'Рентгенология', 'name_en': 'Radiology', 'name_nl': 'Radiologie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'MICROBIOLOGY', 'name': 'Микробиология', 'name_en': 'Microbiology', 'name_nl': 'Microbiologie', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'MATERIALS_SCIENCE', 'name': 'Материаловедение', 'name_en': 'Materials Science', 'name_nl': 'Materiaalkunde', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'GENERAL_MEDICINE', 'name': 'Общая медицина', 'name_en': 'General Medicine', 'name_nl': 'Algemene geneeskunde', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'EMERGENCY_MEDICINE', 'name': 'Неотложная помощь', 'name_en': 'Emergency Medicine', 'name_nl': 'Spoedeisende hulp', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'SYSTEMIC_DISEASES', 'name': 'Системные заболевания', 'name_en': 'Systemic Diseases', 'name_nl': 'Systeemziekten', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'INFECTIOUS_DISEASES', 'name': 'Инфекционные заболевания', 'name_en': 'Infectious Diseases', 'name_nl': 'Infectieziekten', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'SPECIAL_CASES', 'name': 'Специальные группы пациентов', 'name_en': 'Special Cases', 'name_nl': 'Speciale gevallen', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': False},
                {'code': 'DUTCH_DENTISTRY', 'name': 'Голландская стоматология', 'name_en': 'Dutch Dentistry', 'name_nl': 'Nederlandse tandheelkunde', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'DIAGNOSTICS', 'name': 'Диагностика', 'name_en': 'Diagnostics', 'name_nl': 'Diagnostiek', 'weight': 2.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'ETHICS_NL', 'name': 'Этика (Нидерланды)', 'name_en': 'Ethics (Netherlands)', 'name_nl': 'Ethiek (Nederland)', 'weight': 1.0, 'category': 'THEORETICAL', 'critical': True},
                
                # МЕТОДОЛОГИЧЕСКИЕ ДОМЕНЫ (10%)
                {'code': 'PROFESSIONAL_ETHICS', 'name': 'Профессиональная этика', 'name_en': 'Professional Ethics', 'name_nl': 'Professionele ethiek', 'weight': 2.0, 'category': 'METHODOLOGY', 'critical': True},
                {'code': 'STATISTICS', 'name': 'Статистика', 'name_en': 'Statistics', 'name_nl': 'Statistiek', 'weight': 2.0, 'category': 'METHODOLOGY', 'critical': False},
                {'code': 'RESEARCH_METHOD', 'name': 'Методы исследования', 'name_en': 'Research Methods', 'name_nl': 'Onderzoeksmethoden', 'weight': 1.0, 'category': 'METHODOLOGY', 'critical': False},
                
                # ПРАКТИЧЕСКИЕ ДОМЕНЫ (15%)
                {'code': 'TREATMENT_PLANNING', 'name': 'Планирование лечения', 'name_en': 'Treatment Planning', 'name_nl': 'Behandelplanning', 'weight': 3.0, 'category': 'PRACTICAL', 'critical': True},
                {'code': 'COMMUNICATION', 'name': 'Коммуникация', 'name_en': 'Communication', 'name_nl': 'Communicatie', 'weight': 2.0, 'category': 'PRACTICAL', 'critical': True},
                {'code': 'PRACTICAL_THEORY', 'name': 'Практическая теория', 'name_en': 'Practical Theory', 'name_nl': 'Praktische theorie', 'weight': 2.0, 'category': 'PRACTICAL', 'critical': True},
                
                # КЛИНИЧЕСКИЕ ДОМЕНЫ (5%)
                {'code': 'SPECIAL_DIAGNOSTICS', 'name': 'Специальная диагностика', 'name_en': 'Special Diagnostics', 'name_nl': 'Speciale diagnostiek', 'weight': 1.0, 'category': 'CLINICAL', 'critical': True},
                {'code': 'CLINICAL_SKILLS', 'name': 'Клинические навыки', 'name_en': 'Clinical Skills', 'name_nl': 'Klinische vaardigheden', 'weight': 1.0, 'category': 'CLINICAL', 'critical': True},
                {'code': 'PATIENT_MANAGEMENT', 'name': 'Управление пациентами', 'name_en': 'Patient Management', 'name_nl': 'Patiëntbeheer', 'weight': 1.0, 'category': 'CLINICAL', 'critical': True},
            ]
            
            created_count = 0
            for domain_data in dentist_domains:
                # Проверяем, не существует ли уже
                existing = SpecialtyDomain.query.filter_by(
                    specialty_id=dentist_specialty.id,
                    domain_code=domain_data['code']
                ).first()
                
                if not existing:
                    domain = SpecialtyDomain(
                        specialty_id=dentist_specialty.id,
                        domain_code=domain_data['code'],
                        domain_name=domain_data['name'],
                        domain_name_en=domain_data['name_en'],
                        domain_name_nl=domain_data['name_nl'],
                        weight_percentage=domain_data['weight'],
                        is_critical=domain_data['critical'],
                        category=domain_data['category']
                    )
                    db.session.add(domain)
                    created_count += 1
            
            db.session.commit()
            print(f"✅ Created {created_count} dentist domains")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating dentist domains: {str(e)}")
            raise

def create_gp_domains(gp_specialty):
    """Создать домены для врачей общей практики"""
    with app.app_context():
        try:
            # Домены врачей общей практики
            gp_domains = [
                # ТЕОРЕТИЧЕСКИЕ ДОМЕНЫ
                {'code': 'CARDIOLOGY', 'name': 'Кардиология', 'name_en': 'Cardiology', 'name_nl': 'Cardiologie', 'weight': 8.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PULMONOLOGY', 'name': 'Пульмонология', 'name_en': 'Pulmonology', 'name_nl': 'Pulmonologie', 'weight': 6.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'GASTROENTEROLOGY', 'name': 'Гастроэнтерология', 'name_en': 'Gastroenterology', 'name_nl': 'Gastro-enterologie', 'weight': 6.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'ENDOCRINOLOGY', 'name': 'Эндокринология', 'name_en': 'Endocrinology', 'name_nl': 'Endocrinologie', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'NEPHROLOGY', 'name': 'Нефрология', 'name_en': 'Nephrology', 'name_nl': 'Nefrologie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'NEUROLOGY', 'name': 'Неврология', 'name_en': 'Neurology', 'name_nl': 'Neurologie', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'DERMATOLOGY', 'name': 'Дерматология', 'name_en': 'Dermatology', 'name_nl': 'Dermatologie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'RHEUMATOLOGY', 'name': 'Ревматология', 'name_en': 'Rheumatology', 'name_nl': 'Reumatologie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'INFECTIOUS_DISEASES_GP', 'name': 'Инфекционные заболевания', 'name_en': 'Infectious Diseases', 'name_nl': 'Infectieziekten', 'weight': 6.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PEDIATRICS_GP', 'name': 'Педиатрия', 'name_en': 'Pediatrics', 'name_nl': 'Pediatrie', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'GERIATRICS', 'name': 'Гериатрия', 'name_en': 'Geriatrics', 'name_nl': 'Geriatrie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PSYCHIATRY_GP', 'name': 'Психиатрия', 'name_en': 'Psychiatry', 'name_nl': 'Psychiatrie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'GYNECOLOGY', 'name': 'Гинекология', 'name_en': 'Gynecology', 'name_nl': 'Gynaecologie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'UROLOGY', 'name': 'Урология', 'name_en': 'Urology', 'name_nl': 'Urologie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'OPHTHALMOLOGY', 'name': 'Офтальмология', 'name_en': 'Ophthalmology', 'name_nl': 'Oogheelkunde', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'OTOLARYNGOLOGY', 'name': 'Отоларингология', 'name_en': 'Otolaryngology', 'name_nl': 'Keel-, neus- en oorheelkunde', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'ORTHOPEDICS', 'name': 'Ортопедия', 'name_en': 'Orthopedics', 'name_nl': 'Orthopedie', 'weight': 3.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'EMERGENCY_MEDICINE_GP', 'name': 'Неотложная медицина', 'name_en': 'Emergency Medicine', 'name_nl': 'Spoedeisende geneeskunde', 'weight': 5.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'PHARMACOLOGY_GP', 'name': 'Фармакология', 'name_en': 'Pharmacology', 'name_nl': 'Farmacologie', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                {'code': 'DIAGNOSTICS_GP', 'name': 'Диагностика', 'name_en': 'Diagnostics', 'name_nl': 'Diagnostiek', 'weight': 4.0, 'category': 'THEORETICAL', 'critical': True},
                
                # МЕТОДОЛОГИЧЕСКИЕ ДОМЕНЫ
                {'code': 'EVIDENCE_BASED_MEDICINE', 'name': 'Доказательная медицина', 'name_en': 'Evidence-Based Medicine', 'name_nl': 'Evidence-based geneeskunde', 'weight': 3.0, 'category': 'METHODOLOGY', 'critical': True},
                {'code': 'CLINICAL_REASONING', 'name': 'Клиническое мышление', 'name_en': 'Clinical Reasoning', 'name_nl': 'Klinisch redeneren', 'weight': 3.0, 'category': 'METHODOLOGY', 'critical': True},
                {'code': 'MEDICAL_ETHICS', 'name': 'Медицинская этика', 'name_en': 'Medical Ethics', 'name_nl': 'Medische ethiek', 'weight': 2.0, 'category': 'METHODOLOGY', 'critical': True},
                
                # ПРАКТИЧЕСКИЕ ДОМЕНЫ
                {'code': 'PATIENT_COMMUNICATION', 'name': 'Коммуникация с пациентами', 'name_en': 'Patient Communication', 'name_nl': 'Patiëntcommunicatie', 'weight': 4.0, 'category': 'PRACTICAL', 'critical': True},
                {'code': 'PREVENTIVE_CARE', 'name': 'Профилактическая помощь', 'name_en': 'Preventive Care', 'name_nl': 'Preventieve zorg', 'weight': 3.0, 'category': 'PRACTICAL', 'critical': True},
                {'code': 'CHRONIC_DISEASE_MANAGEMENT', 'name': 'Управление хроническими заболеваниями', 'name_en': 'Chronic Disease Management', 'name_nl': 'Chronische ziektebeheer', 'weight': 4.0, 'category': 'PRACTICAL', 'critical': True},
                
                # КЛИНИЧЕСКИЕ ДОМЕНЫ
                {'code': 'CLINICAL_EXAMINATION', 'name': 'Клиническое обследование', 'name_en': 'Clinical Examination', 'name_nl': 'Klinisch onderzoek', 'weight': 3.0, 'category': 'CLINICAL', 'critical': True},
                {'code': 'PROCEDURES_GP', 'name': 'Процедуры', 'name_en': 'Procedures', 'name_nl': 'Procedures', 'weight': 2.0, 'category': 'CLINICAL', 'critical': True},
            ]
            
            created_count = 0
            for domain_data in gp_domains:
                # Проверяем, не существует ли уже
                existing = SpecialtyDomain.query.filter_by(
                    specialty_id=gp_specialty.id,
                    domain_code=domain_data['code']
                ).first()
                
                if not existing:
                    domain = SpecialtyDomain(
                        specialty_id=gp_specialty.id,
                        domain_code=domain_data['code'],
                        domain_name=domain_data['name'],
                        domain_name_en=domain_data['name_en'],
                        domain_name_nl=domain_data['name_nl'],
                        weight_percentage=domain_data['weight'],
                        is_critical=domain_data['critical'],
                        category=domain_data['category']
                    )
                    db.session.add(domain)
                    created_count += 1
            
            db.session.commit()
            print(f"✅ Created {created_count} GP domains")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating GP domains: {str(e)}")
            raise

def migrate_existing_data(dentist_specialty):
    """Мигрировать существующие данные к системе специальностей"""
    with app.app_context():
        try:
            # 1. Обновить существующие вопросы
            existing_questions = Question.query.all()
            updated_questions = 0
            
            for question in existing_questions:
                if not hasattr(question, 'specialty_id') or question.specialty_id is None:
                    question.specialty_id = dentist_specialty.id
                    question.is_calibrated = True
                    question.calibration_status = 'calibrated'
                    updated_questions += 1
            
            print(f"✅ Updated {updated_questions} questions")
            
            # 2. Обновить IRT параметры
            existing_irt_params = IRTParameters.query.all()
            updated_irt_params = 0
            
            for params in existing_irt_params:
                if not hasattr(params, 'specialty_id') or params.specialty_id is None:
                    params.specialty_id = dentist_specialty.id
                    updated_irt_params += 1
            
            print(f"✅ Updated {updated_irt_params} IRT parameters")
            
            # 3. Обновить диагностические сессии
            existing_sessions = DiagnosticSession.query.all()
            updated_sessions = 0
            
            for session in existing_sessions:
                if not hasattr(session, 'specialty_id') or session.specialty_id is None:
                    session.specialty_id = dentist_specialty.id
                    session.assessment_mode = 'assessment'
                    session.session_type = 'diagnostic'
                    updated_sessions += 1
            
            print(f"✅ Updated {updated_sessions} diagnostic sessions")
            
            # 4. Обновить счетчики доменов
            for domain in dentist_specialty.domains:
                question_count = Question.query.filter_by(
                    specialty_id=dentist_specialty.id,
                    domain=domain.domain_code
                ).count()
                
                calibrated_count = Question.query.filter(
                    Question.specialty_id == dentist_specialty.id,
                    Question.domain == domain.domain_code,
                    Question.is_calibrated == True
                ).count()
                
                domain.question_count = question_count
                domain.calibrated_count = calibrated_count
            
            db.session.commit()
            print("✅ Updated domain statistics")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error migrating existing data: {str(e)}")
            raise

def main():
    """Основная функция миграции"""
    print("🚀 Starting specialty system migration...")
    
    try:
        # 1. Создать специальности
        dentist_specialty, gp_specialty = create_specialties()
        
        # 2. Создать домены для стоматологов
        create_dentist_domains(dentist_specialty)
        
        # 3. Создать домены для врачей общей практики
        create_gp_domains(gp_specialty)
        
        # 4. Мигрировать существующие данные
        migrate_existing_data(dentist_specialty)
        
        print("🎉 Specialty system migration completed successfully!")
        
        # Выводим статистику
        print("\n📊 Migration Statistics:")
        print(f"Dentist specialty: {dentist_specialty.total_questions} questions, {dentist_specialty.calibrated_questions} calibrated")
        print(f"GP specialty: {gp_specialty.total_questions} questions, {gp_specialty.calibrated_questions} calibrated")
        print(f"Dentist domains: {dentist_specialty.domains.count()}")
        print(f"GP domains: {gp_specialty.domains.count()}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()
