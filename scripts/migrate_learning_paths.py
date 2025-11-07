#!/usr/bin/env python3
"""
Миграция путей обучения на структуру BI-toets для стоматологов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import LearningPath, UserLearningProgress
from extensions import db
import json
from datetime import datetime, timezone

def migrate_learning_paths():
    with app.app_context():
        print("🔄 МИГРАЦИЯ ПУТЕЙ ОБУЧЕНИЯ НА BI-TOETS СТРУКТУРУ")
        print("=" * 60)
        
        # 1. Определяем новые пути обучения для стоматологов
        new_learning_paths = [
            # 1. THEORETICAL TRACK (70% экзамена)
            
            # 1.1 Basic Medical Sciences Track
            {
                "id": "basic_medical_sciences",
                "name": "Basic Medical Sciences",
                "name_nl": "Basismedische Wetenschappen", 
                "name_ru": "Базовые медицинские науки",
                "description": "Anatomie, fysiologie, pathologie, microbiologie voor tandheelkunde",
                "exam_component": "THEORETICAL",
                "exam_weight": 15.0,
                "exam_type": "multiple_choice",
                "duration_weeks": 8,
                "total_estimated_hours": 130,
                "prerequisites": [],
                "modules": [
                    {
                        "id": "anatomy_head_neck",
                        "name": "Anatomie hoofd en hals",
                        "domains": ["ANATOMIE"],
                        "learning_cards_path": "cards/anatomy/",
                        "estimated_hours": 40
                    },
                    {
                        "id": "physiology_oral",
                        "name": "Fysiologie mondholte",
                        "domains": ["FYSIOLOGIE"],
                        "estimated_hours": 30
                    },
                    {
                        "id": "oral_pathology", 
                        "name": "Orale pathologie",
                        "domains": ["PATHOLOGIE"],
                        "estimated_hours": 35
                    },
                    {
                        "id": "microbiology_oral",
                        "name": "Microbiologie mondholte",
                        "domains": ["MICROBIOLOGIE"],
                        "estimated_hours": 25
                    }
                ],
                "assessment": {
                    "type": "multiple_choice",
                    "questions": 50,
                    "time_limit": 90,
                    "passing_score": 5.5
                }
            },
            
            # 1.2 THK I Track (Tandheelkunde Kern I)
            {
                "id": "thk_1",
                "name": "THK I - Tandheelkunde Kern I",
                "name_nl": "THK I - Tandheelkunde Kern I",
                "name_ru": "ТХК I - Основы стоматологии I",
                "description": "Cariologie, speeksel, endodontie, kindertandheelkunde, parodontologie",
                "exam_component": "THEORETICAL",
                "exam_weight": 20.0,
                "exam_type": "multiple_choice",
                "duration_weeks": 12,
                "total_estimated_hours": 190,
                "prerequisites": ["basic_medical_sciences"],
                "modules": [
                    {
                        "id": "cariology",
                        "name": "Cariologie en preventie",
                        "domains": ["THER"],
                        "learning_cards_path": "cards/caries/",
                        "virtual_patients": ["caries_case_1", "caries_case_2"],
                        "estimated_hours": 45
                    },
                    {
                        "id": "endodontics",
                        "name": "Endodontie",
                        "domains": ["THER"],
                        "learning_cards_path": "cards/endodontic/",
                        "virtual_patients": ["pulpitis_case", "retreat_case"],
                        "estimated_hours": 50
                    },
                    {
                        "id": "periodontology",
                        "name": "Parodontologie", 
                        "domains": ["PARO"],
                        "learning_cards_path": "cards/periodontic/",
                        "estimated_hours": 40
                    },
                    {
                        "id": "pediatric_dentistry",
                        "name": "Kindertandheelkunde",
                        "domains": ["PEDI"],
                        "learning_cards_path": "cards/pediatric/",
                        "estimated_hours": 35
                    },
                    {
                        "id": "saliva_function",
                        "name": "Speeksel en functie",
                        "domains": ["FYSIOLOGIE"],
                        "learning_cards_path": "cards/saliva/",
                        "estimated_hours": 20
                    }
                ],
                "assessment": {
                    "type": "multiple_choice",
                    "questions": 60,
                    "time_limit": 120,
                    "passing_score": 5.5
                }
            },
            
            # 1.3 THK II Track (Tandheelkunde Kern II)
            {
                "id": "thk_2",
                "name": "THK II - Tandheelkunde Kern II",
                "name_nl": "THK II - Tandheelkunde Kern II",
                "name_ru": "ТХК II - Основы стоматологии II",
                "description": "Prothetiek, orthodontie, orale chirurgie, kinesiologie",
                "exam_component": "THEORETICAL",
                "exam_weight": 20.0,
                "exam_type": "multiple_choice",
                "duration_weeks": 12,
                "total_estimated_hours": 160,
                "prerequisites": ["thk_1"],
                "modules": [
                    {
                        "id": "prosthetics",
                        "name": "Prothetiek",
                        "domains": ["PROTH"],
                        "sub_modules": [
                            "Uitneembare prothetiek",
                            "Kroon en brug", 
                            "Implantologie",
                            "Volledige gebitsprothese"
                        ],
                        "estimated_hours": 55
                    },
                    {
                        "id": "orthodontics",
                        "name": "Orthodontie",
                        "domains": ["ORTHO"],
                        "estimated_hours": 35
                    },
                    {
                        "id": "oral_surgery",
                        "name": "Orale chirurgie",
                        "domains": ["SURG"],
                        "estimated_hours": 45
                    },
                    {
                        "id": "kinesiology",
                        "name": "Kinesiologie",
                        "domains": ["ANATOMIE", "FYSIOLOGIE"],
                        "estimated_hours": 25
                    }
                ],
                "assessment": {
                    "type": "multiple_choice",
                    "questions": 60,
                    "time_limit": 120,
                    "passing_score": 5.5
                }
            },
            
            # 1.4 Radiology Track
            {
                "id": "radiology",
                "name": "Radiologie",
                "name_nl": "Radiologie",
                "name_ru": "Рентгенология",
                "description": "Röntgendiagnostiek en beeldvorming in tandheelkunde",
                "exam_component": "THEORETICAL",
                "exam_weight": 10.0,
                "exam_type": "multiple_choice",
                "duration_weeks": 6,
                "total_estimated_hours": 70,
                "prerequisites": ["basic_medical_sciences"],
                "modules": [
                    {
                        "id": "xray_interpretation",
                        "name": "Röntgen interpretatie",
                        "domains": ["RADIOLOGIE"],
                        "estimated_hours": 40
                    },
                    {
                        "id": "imaging_techniques",
                        "name": "Beeldvormingstechnieken", 
                        "domains": ["RADIOLOGIE"],
                        "estimated_hours": 30
                    }
                ],
                "assessment": {
                    "type": "multiple_choice",
                    "questions": 40,
                    "time_limit": 60,
                    "passing_score": 5.5
                }
            },
            
            # 2. METHODOLOGY TRACK (10% экзамена, Open Book)
            
            # 2.1 Statistics Track
            {
                "id": "statistics",
                "name": "Statistiek voor tandheelkunde",
                "name_nl": "Statistiek voor tandheelkunde",
                "name_ru": "Статистика для стоматологии",
                "description": "Statistische analyse in dentaal onderzoek",
                "exam_component": "METHODOLOGY",
                "exam_weight": 5.0,
                "exam_type": "open_book",
                "duration_weeks": 4,
                "total_estimated_hours": 55,
                "prerequisites": [],
                "modules": [
                    {
                        "id": "descriptive_stats",
                        "name": "Beschrijvende statistiek",
                        "domains": ["STATISTICS"],
                        "learning_cards_path": "cards/statistics/",
                        "estimated_hours": 25
                    },
                    {
                        "id": "hypothesis_testing",
                        "name": "Hypothese toetsing",
                        "domains": ["STATISTICS"],
                        "estimated_hours": 30
                    }
                ],
                "assessment": {
                    "type": "open_book",
                    "questions": 30,
                    "time_limit": 90,
                    "passing_score": 5.5
                }
            },
            
            # 2.2 Research Methodology Track
            {
                "id": "research_methodology",
                "name": "Onderzoeksmethodologie",
                "name_nl": "Onderzoeksmethodologie",
                "name_ru": "Методология исследований",
                "description": "Wetenschappelijke methodologie in tandheelkunde",
                "exam_component": "METHODOLOGY",
                "exam_weight": 5.0,
                "exam_type": "open_book",
                "duration_weeks": 4,
                "total_estimated_hours": 50,
                "prerequisites": ["statistics"],
                "modules": [
                    {
                        "id": "research_design",
                        "name": "Onderzoeksdesign",
                        "domains": ["RESEARCH_METHOD"],
                        "learning_cards_path": "cards/Methodology/",
                        "estimated_hours": 25
                    },
                    {
                        "id": "evidence_based_dentistry",
                        "name": "Evidence-based tandheelkunde",
                        "domains": ["RESEARCH_METHOD"],
                        "estimated_hours": 25
                    }
                ],
                "assessment": {
                    "type": "open_book",
                    "questions": 30,
                    "time_limit": 90,
                    "passing_score": 5.5
                }
            },
            
            # 3. PRACTICAL SKILLS TRACK (15% экзамена)
            
            # 3.1 Simodont Training Track
            {
                "id": "simodont_training",
                "name": "Praktische vaardigheden (Simodont voorbereiding)",
                "name_nl": "Praktische vaardigheden (Simodont voorbereiding)",
                "name_ru": "Практические навыки (подготовка к Simodont)",
                "description": "Theoretische voorbereiding op praktische examens",
                "exam_component": "PRACTICAL",
                "exam_weight": 15.0,
                "exam_type": "practical_theory",
                "duration_weeks": 8,
                "total_estimated_hours": 95,
                "prerequisites": ["thk_1", "thk_2"],
                "modules": [
                    {
                        "id": "manual_skills_theory",
                        "name": "Handvaardigheden theorie",
                        "domains": ["PRACTICAL_SKILLS"],
                        "content": [
                            "Cross en donut technieken",
                            "Instrumentarium gebruik",
                            "Beoordelingscriteria"
                        ],
                        "estimated_hours": 20
                    },
                    {
                        "id": "crown_preparation_theory",
                        "name": "Kroonpreparatie theorie", 
                        "domains": ["PRACTICAL_SKILLS"],
                        "content": [
                            "Criteria A: Ruimte, ondersnijdingen, buurelementen",
                            "Criteria B: Retentie, schouder, afgerond",
                            "Boren sequentie: 16 red → 10 blue → 14 blue → 16 red"
                        ],
                        "estimated_hours": 25
                    },
                    {
                        "id": "endodontic_access_theory",
                        "name": "Endodontische toegang theorie",
                        "domains": ["PRACTICAL_SKILLS"],
                        "estimated_hours": 20
                    },
                    {
                        "id": "caries_excavation_theory",
                        "name": "Cariës excavatie theorie",
                        "domains": ["PRACTICAL_SKILLS"],
                        "estimated_hours": 15
                    },
                    {
                        "id": "dental_hygiene_theory",
                        "name": "Gebitsreiniging theorie",
                        "domains": ["PRACTICAL_SKILLS"],
                        "estimated_hours": 15
                    }
                ],
                "assessment": {
                    "type": "practical_theory",
                    "questions": 45,
                    "time_limit": 90,
                    "passing_score": 5.5
                }
            },
            
            # 4. CLINICAL SKILLS TRACK (5% экзамена)
            
            # 4.1 Communication & Ethics Track
            {
                "id": "communication_ethics",
                "name": "Communicatie en ethiek",
                "name_nl": "Communicatie en ethiek",
                "name_ru": "Коммуникация и этика",
                "description": "Patiëntcommunicatie en professionele ethiek",
                "exam_component": "CLINICAL",
                "exam_weight": 3.0,
                "exam_type": "interview",
                "duration_weeks": 6,
                "total_estimated_hours": 55,
                "prerequisites": ["thk_1"],
                "modules": [
                    {
                        "id": "intake_skills",
                        "name": "Intake gesprek vaardigheden",
                        "domains": ["COMMUNICATION"],
                        "virtual_patients": "cards/virtual_patient/",
                        "structure": [
                            "Reden van komst",
                            "Eigen indruk gebitsgezondheid", 
                            "Procedures uitleggen",
                            "Consequenties en kosten",
                            "Verbaal en non-verbaal contact",
                            "Empathie en gemoedstoestand",
                            "Doorvragen en samenvatten",
                            "GVL doornemen",
                            "Nadere instructie herkennen",
                            "Nederlandse taalvaardigheid"
                        ],
                        "estimated_hours": 30
                    },
                    {
                        "id": "professional_ethics",
                        "name": "Professionele ethiek",
                        "domains": ["ETHIEK"],
                        "estimated_hours": 25
                    }
                ],
                "assessment": {
                    "type": "interview",
                    "questions": 20,
                    "time_limit": 60,
                    "passing_score": 5.5
                }
            },
            
            # 4.2 Treatment Planning Track
            {
                "id": "treatment_planning",
                "name": "Behandelplanning",
                "name_nl": "Behandelplanning",
                "name_ru": "Планирование лечения",
                "description": "Complexe behandelplanning en diagnostiek",
                "exam_component": "CLINICAL",
                "exam_weight": 2.0,
                "exam_type": "case_study",
                "duration_weeks": 8,
                "total_estimated_hours": 100,
                "prerequisites": ["thk_1", "thk_2"],
                "modules": [
                    {
                        "id": "comprehensive_planning",
                        "name": "Uitgebreide behandelplanning",
                        "domains": ["TREATMENT_PLANNING"],
                        "phases": [
                            "Fase 1: Acute behandeling",
                            "Fase 2: Initiële behandeling", 
                            "Fase 3: Evaluatiefase",
                            "Fase 4: Langetermijnbehandeling",
                            "Fase 5: Nazorg"
                        ],
                        "estimated_hours": 40
                    },
                    {
                        "id": "endodontic_cases",
                        "name": "Endodontische casussen",
                        "domains": ["TREATMENT_PLANNING"],
                        "estimated_hours": 25
                    },
                    {
                        "id": "trauma_resorption",
                        "name": "Trauma en resorptie",
                        "domains": ["TREATMENT_PLANNING"],
                        "estimated_hours": 20
                    },
                    {
                        "id": "pediatric_planning",
                        "name": "Kindertandheelkunde planning",
                        "domains": ["TREATMENT_PLANNING"],
                        "estimated_hours": 15
                    }
                ],
                "assessment": {
                    "type": "case_study",
                    "questions": 25,
                    "time_limit": 90,
                    "passing_score": 5.5
                }
            }
        ]
        
        # 2. Удаляем старые пути обучения
        old_path_ids = [
            'big_toets_voorbereiding',
            'algemene_tandheelkunde',
            'endodontie', 
            'parodontologie',
            'orale_chirurgie',
            'prothetiek',
            'orthodontie'
        ]
        
        print("🗑️ Удаляем старые пути обучения...")
        for old_id in old_path_ids:
            old_path = LearningPath.query.filter_by(id=old_id).first()
            if old_path:
                print(f"   ❌ Удаляем: {old_path.name}")
                db.session.delete(old_path)
        
        # 3. Создаем новые пути обучения
        print("\n✅ Создаем новые пути BI-toets...")
        created_paths = []
        
        for path_data in new_learning_paths:
            # Проверяем, существует ли уже путь с таким ID
            existing_path = LearningPath.query.filter_by(id=path_data["id"]).first()
            if existing_path:
                print(f"   ⚠️ Путь {path_data['id']} уже существует, обновляем...")
                # Обновляем существующий путь
                for key, value in path_data.items():
                    if hasattr(existing_path, key):
                        setattr(existing_path, key, value)
                existing_path.updated_at = datetime.now(timezone.utc)
                created_paths.append(existing_path)
            else:
                # Создаем новый путь
                new_path = LearningPath(**path_data)
                db.session.add(new_path)
                created_paths.append(new_path)
                print(f"   ✅ Создан: {path_data['name']}")
        
        # 4. Мигрируем прогресс пользователей
        print("\n🔄 Мигрируем прогресс пользователей...")
        
        # Получаем все записи прогресса со старыми путями
        old_progress = UserLearningProgress.query.filter(
            UserLearningProgress.learning_path_id.in_(old_path_ids)
        ).all()
        
        migration_mapping = {
            'big_toets_voorbereiding': 'basic_medical_sciences',
            'algemene_tandheelkunde': 'thk_1',
            'endodontie': 'thk_1',
            'parodontologie': 'thk_1',
            'orale_chirurgie': 'thk_2',
            'prothetiek': 'thk_2',
            'orthodontie': 'thk_2'
        }
        
        migrated_count = 0
        for progress in old_progress:
            new_path_id = migration_mapping.get(progress.learning_path_id)
            if new_path_id:
                # Проверяем, есть ли уже прогресс по новому пути
                existing_progress = UserLearningProgress.query.filter_by(
                    user_id=progress.user_id,
                    learning_path_id=new_path_id
                ).first()
                
                if existing_progress:
                    # Объединяем прогресс
                    existing_progress.progress_percentage = max(
                        existing_progress.progress_percentage,
                        progress.progress_percentage
                    )
                    existing_progress.total_time_spent += progress.total_time_spent
                    existing_progress.lessons_completed += progress.lessons_completed
                    existing_progress.tests_passed += progress.tests_passed
                    print(f"   🔄 Объединен прогресс: {progress.user_id} → {new_path_id}")
                else:
                    # Создаем новый прогресс
                    progress.learning_path_id = new_path_id
                    print(f"   ✅ Мигрирован прогресс: {progress.user_id} → {new_path_id}")
                
                migrated_count += 1
        
        # 5. Сохраняем изменения
        try:
            db.session.commit()
            print(f"\n✅ Миграция завершена успешно!")
            print(f"   📊 Создано/обновлено путей: {len(created_paths)}")
            print(f"   📊 Мигрировано записей прогресса: {migrated_count}")
            
        except Exception as e:
            print(f"\n❌ Ошибка при миграции: {e}")
            db.session.rollback()
            return
        
        # 6. Выводим итоговую структуру
        print("\n📋 ИТОГОВАЯ СТРУКТУРА BI-TOETS:")
        print("=" * 60)
        
        components = ['THEORETICAL', 'METHODOLOGY', 'PRACTICAL', 'CLINICAL']
        for component in components:
            paths = LearningPath.query.filter_by(
                exam_component=component,
                is_active=True
            ).all()
            
            if paths:
                total_weight = sum(p.exam_weight for p in paths)
                print(f"\n🎯 {component} ({total_weight:.1f}%):")
                for path in sorted(paths, key=lambda x: x.exam_weight, reverse=True):
                    print(f"   • {path.name} ({path.exam_weight:.1f}%) - {path.exam_type}")
        
        print(f"\n✅ Система готова к работе с новой структурой BI-toets!")

if __name__ == "__main__":
    migrate_learning_paths() 