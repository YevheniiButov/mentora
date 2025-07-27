#!/usr/bin/env python3
"""
Скрипт для создания демонстрационной подтемы "Interacties & Contraindicaties"
с интерактивным Drug Interaction Checker
"""

import sys
import os
import json
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Module, Lesson, Subject

def create_interactive_demo():
    """Создает демонстрационную подтему с интерактивным Drug Interaction Checker"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Находим или создаем предмет "Algemene Farmacologie"
            subject = Subject.query.filter_by(name='Algemene Farmacologie').first()
            
            if not subject:
                # Создаем новый предмет
                subject = Subject(
                    name='Algemene Farmacologie',
                    description='Основы фармакологии для BIG экзамена',
                    learning_path_id=1,  # Предполагаем, что это первый learning path
                    order=1
                )
                db.session.add(subject)
                db.session.commit()
                print(f"✅ Создан новый предмет: {subject.name}")
            
            # Находим или создаем модуль для фармакологии
            module = Module.query.filter_by(title='Farmacokinetiek Basis').first()
            
            if not module:
                # Создаем новый модуль если не найден
                module = Module(
                    title='Farmacokinetiek Basis',
                    description='Основы фармакокинетики и лекарственных взаимодействий',
                    subject_id=subject.id,
                    order=1,
                    is_premium=False
                )
                db.session.add(module)
                db.session.commit()
                print(f"✅ Создан новый модуль: {module.title}")
            
            # Создаем урок с подтемой "Interacties & Contraindicaties"
            lesson_content = {
                "cards": [
                    {
                        "card_id": "interacties_intro",
                        "question": "Wat zijn medicijninteracties?",
                        "answer": """
                        <h4>Medicijninteracties</h4>
                        <p>Medicijninteracties zijn situaties waarbij het ene medicijn de werking van het andere medicijn beïnvloedt. Dit kan gebeuren op verschillende manieren:</p>
                        
                        <ul>
                            <li><strong>Farmacokinetische interacties:</strong> Beïnvloeding van absorptie, distributie, metabolisme of excretie</li>
                            <li><strong>Farmacodynamische interacties:</strong> Beïnvloeding van het werkingsmechanisme</li>
                            <li><strong>Fysisch-chemische interacties:</strong> Onverenigbaarheid van medicijnen</li>
                        </ul>
                        
                        <h5>Belangrijke voorbeelden:</h5>
                        <ul>
                            <li>Warfarine + Ibuprofen → Verhoogd bloedingsrisico</li>
                            <li>Digoxine + Furosemide → Digitalis toxiciteit</li>
                            <li>Simvastatine + Amiodarone → Rhabdomyolyse risico</li>
                        </ul>
                        """
                    },
                    {
                        "card_id": "contraindicaties_basis",
                        "question": "Wat zijn contra-indicaties?",
                        "answer": """
                        <h4>Contra-indicaties</h4>
                        <p>Contra-indicaties zijn situaties waarin een medicijn NIET mag worden voorgeschreven vanwege het risico op ernstige bijwerkingen.</p>
                        
                        <h5>Types contra-indicaties:</h5>
                        <ul>
                            <li><strong>Absolute contra-indicaties:</strong> Medicijn mag nooit worden gebruikt</li>
                            <li><strong>Relatieve contra-indicaties:</strong> Medicijn kan worden gebruikt met extra voorzichtigheid</li>
                        </ul>
                        
                        <h5>Veelvoorkomende contra-indicaties:</h5>
                        <ul>
                            <li>Zwangerschap en borstvoeding</li>
                            <li>Lever- of nierfunctiestoornissen</li>
                            <li>Allergieën voor medicijn of bestanddelen</li>
                            <li>Bepaalde leeftijdsgroepen (kinderen, ouderen)</li>
                        </ul>
                        """
                    }
                ]
            }
            
            # Создаем урок
            lesson = Lesson(
                title='Interacties & Contraindicaties',
                content=json.dumps(lesson_content),
                content_type='learning_card',
                module_id=module.id,
                order=1,
                subtopic='Interacties & Contraindicaties',
                subtopic_slug='interacties-contraindicaties',
                subtopic_order=1
            )
            
            db.session.add(lesson)
            db.session.commit()
            
            print(f"✅ Создан урок: {lesson.title}")
            print(f"📝 Подтема: {lesson.subtopic}")
            print(f"🔗 Slug: {lesson.subtopic_slug}")
            print(f"📚 Модуль: {module.title}")
            print(f"🎯 Предмет: {module.subject.name if module.subject else 'N/A'}")
            
            print("\n🎉 Демонстрационная подтема создана успешно!")
            print("💡 Интерактивный Drug Interaction Checker будет автоматически активирован")
            print(f"🔗 URL для доступа: /{{lang}}/modules/{module.id}/subtopic/interacties-contraindicaties")
            
        except Exception as e:
            print(f"❌ Ошибка при создании демо: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_interactive_demo() 