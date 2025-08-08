#!/usr/bin/env python3
"""
Скрипт для исправления маппинга вопросов к доменам BIG
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Question, ContentDomainMapping
import json
from datetime import datetime, timezone

def analyze_question_domain_mapping():
    """Анализ текущего состояния маппинга вопросов к доменам"""
    
    print("🔍 АНАЛИЗ МАППИНГА ВОПРОСОВ К ДОМЕНАМ BIG")
    print("=" * 60)
    
    with app.app_context():
        
        # 1. Общая статистика
        total_questions = Question.query.count()
        questions_with_domain = Question.query.filter(Question.big_domain_id.isnot(None)).count()
        questions_without_domain = Question.query.filter_by(big_domain_id=None).count()
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего вопросов: {total_questions}")
        print(f"   Вопросов с маппингом к доменам: {questions_with_domain}")
        print(f"   Вопросов без маппинга: {questions_without_domain}")
        
        # 2. Анализ по доменам
        domains = BIGDomain.query.filter_by(is_active=True).all()
        print(f"\n📈 АНАЛИЗ ПО ДОМЕНАМ:")
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            print(f"   • {domain.code}: {domain.name} - {questions_count} вопросов")
        
        # 3. Анализ по категориям вопросов
        print(f"\n🏷️ АНАЛИЗ ПО КАТЕГОРИЯМ:")
        categories = db.session.query(Question.category).distinct().all()
        
        for category in categories:
            category_name = category[0]
            questions_in_category = Question.query.filter_by(category=category_name).count()
            questions_with_domain = Question.query.filter_by(
                category=category_name, 
                big_domain_id=db.not_(None)
            ).count()
            
            print(f"   • {category_name}: {questions_in_category} вопросов ({questions_with_domain} с маппингом)")
        
        # 4. Анализ по полю domain
        print(f"\n🔗 АНАЛИЗ ПО ПОЛЮ 'domain':")
        domain_values = db.session.query(Question.domain).distinct().all()
        
        for domain_value in domain_values:
            domain_name = domain_value[0]
            questions_count = Question.query.filter_by(domain=domain_name).count()
            print(f"   • {domain_name}: {questions_count} вопросов")

def create_question_domain_mapping():
    """Создание маппинга вопросов к доменам на основе ключевых слов"""
    
    print("\n🔧 СОЗДАНИЕ МАППИНГА ВОПРОСОВ К ДОМЕНАМ")
    print("=" * 60)
    
    with app.app_context():
        
        # Ключевые слова для каждого домена
        domain_keywords = {
            'THER': ['caries', 'cavity', 'filling', 'endodontics', 'therapeutic', 'treatment', 'restoration', 'pulp', 'cariës', 'wortelkanaal', 'vulling'],
            'SURG': ['surgery', 'surgical', 'extraction', 'implant', 'implantation', 'extract', 'removal', 'chirurgie', 'extractie', 'implantaat'],
            'PROTH': ['prosthesis', 'crown', 'bridge', 'prosthodontics', 'denture', 'prosthetic', 'kroon', 'brug', 'prothese', 'prothetiek'],
            'PEDI': ['pediatric', 'pediatrics', 'child', 'children', 'milk teeth', 'primary teeth', 'baby teeth', 'kinderen', 'melktanden', 'pediatrie'],
            'PARO': ['periodont', 'periodontal', 'gingiva', 'gum', 'periodontitis', 'gingivitis', 'parodont', 'tandvlees', 'parodontologie'],
            'ORTHO': ['orthodontics', 'orthodontic', 'braces', 'bite', 'malocclusion', 'alignment', 'orthodontie', 'beugel', 'occlusie'],
            'ANATOMIE': ['anatomy', 'anatomical', 'structure', 'tooth', 'jaw', 'bone', 'tissue', 'anatomie', 'structuur', 'kaak'],
            'FYSIOLOGIE': ['physiology', 'physiological', 'function', 'process', 'metabolism', 'fysiologie', 'functie', 'proces'],
            'PATHOLOGIE': ['pathology', 'pathological', 'disease', 'tumor', 'lesion', 'abnormal', 'pathologie', 'ziekte', 'tumor'],
            'MICROBIOLOGIE': ['microbiology', 'microbial', 'bacteria', 'infection', 'microorganism', 'microbiologie', 'bacteriën', 'infectie'],
            'MATERIAALKUNDE': ['material', 'materials', 'composite', 'amalgam', 'cement', 'adhesive', 'materiaal', 'composiet', 'cement'],
            'RADIOLOGIE': ['radiology', 'radiographic', 'x-ray', 'imaging', 'diagnostic', 'radiologie', 'röntgen', 'beeldvorming'],
            'ALGEMENE_GENEESKUNDE': ['general medicine', 'medical', 'systemic', 'health', 'algemene geneeskunde', 'medisch', 'systemisch'],
            'EMERGENCY': ['emergency', 'urgent', 'acute', 'trauma', 'pain', 'nood', 'spoed', 'acuut', 'trauma'],
            'SYSTEMIC': ['systemic', 'system', 'disease', 'condition', 'medical', 'systemisch', 'systeem', 'aandoening'],
            'PHARMA': ['pharmacology', 'drug', 'medication', 'pharmaceutical', 'medicine', 'farmacologie', 'medicijn', 'medicatie'],
            'INFECTION': ['infection', 'infectious', 'contamination', 'sterilization', 'infectie', 'besmetting', 'sterilisatie'],
            'SPECIAL': ['special', 'specialized', 'specific', 'unique', 'particular', 'speciaal', 'specifiek', 'uniek'],
            'DIAGNOSIS': ['diagnosis', 'diagnostic', 'assessment', 'evaluation', 'examination', 'diagnose', 'diagnostiek', 'beoordeling'],
            'DUTCH': ['dutch', 'netherlands', 'holland', 'dutch system', 'nederlands', 'nederland', 'holland'],
            'PROFESSIONAL': ['professional', 'ethics', 'conduct', 'practice', 'standards', 'professioneel', 'ethiek', 'gedrag'],
            'STATISTICS': ['statistics', 'statistical', 'data', 'analysis', 'research', 'statistiek', 'data', 'analyse'],
            'RESEARCH_METHOD': ['research', 'methodology', 'study', 'investigation', 'onderzoek', 'methodologie', 'studie'],
            'PRACTICAL_SKILLS': ['practical', 'skill', 'technique', 'procedure', 'manual', 'praktisch', 'vaardigheid', 'techniek'],
            'TREATMENT_PLANNING': ['treatment planning', 'plan', 'strategy', 'approach', 'behandelplanning', 'plan', 'strategie'],
            'COMMUNICATION': ['communication', 'communicative', 'patient', 'interaction', 'communicatie', 'patiënt', 'interactie']
        }
        
        # Получаем все вопросы без маппинга
        questions_without_mapping = Question.query.filter_by(big_domain_id=None).all()
        print(f"Найдено {len(questions_without_mapping)} вопросов без маппинга")
        
        created_count = 0
        
        for question in questions_without_mapping:
            question_text = f"{question.text} {question.category} {question.domain}".lower()
            
            # Ищем подходящий домен
            best_domain = None
            best_score = 0
            
            for domain_code, keywords in domain_keywords.items():
                domain = BIGDomain.query.filter_by(code=domain_code).first()
                if not domain:
                    continue
                
                score = sum(1 for keyword in keywords if keyword.lower() in question_text)
                if score > best_score:
                    best_score = score
                    best_domain = domain
            
            # Если не нашли по ключевым словам, попробуем по старому полю domain
            if not best_domain and question.domain:
                domain = BIGDomain.query.filter_by(code=question.domain).first()
                if domain:
                    best_domain = domain
                    best_score = 1
                    print(f"   🔄 Используем старое поле domain: {question.domain} -> {domain.code}")
            
            # Создаем маппинг если нашли подходящий домен
            if best_domain and best_score > 0:
                question.big_domain_id = best_domain.id
                created_count += 1
                print(f"   ✅ Question {question.id} -> {best_domain.code} (score: {best_score})")
        
        db.session.commit()
        print(f"\n✅ Создано {created_count} маппингов вопросов к доменам")

def verify_mapping_results():
    """Проверка результатов маппинга"""
    
    print("\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ МАППИНГА")
    print("=" * 60)
    
    with app.app_context():
        
        # 1. Общая статистика после маппинга
        total_questions = Question.query.count()
        questions_with_domain = Question.query.filter(Question.big_domain_id.isnot(None)).count()
        questions_without_domain = Question.query.filter_by(big_domain_id=None).count()
        
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"   Всего вопросов: {total_questions}")
        print(f"   Вопросов с маппингом: {questions_with_domain} ({questions_with_domain/total_questions*100:.1f}%)")
        print(f"   Вопросов без маппинга: {questions_without_domain}")
        
        # 2. Распределение по доменам
        print(f"\n📈 РАСПРЕДЕЛЕНИЕ ПО ДОМЕНАМ:")
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            percentage = (questions_count / total_questions * 100) if total_questions > 0 else 0
            print(f"   • {domain.code}: {questions_count} вопросов ({percentage:.1f}%)")
        
        # 3. Вопросы без маппинга
        if questions_without_domain > 0:
            print(f"\n❌ ВОПРОСЫ БЕЗ МАППИНГА:")
            unmapped_questions = Question.query.filter_by(big_domain_id=None).limit(10).all()
            for question in unmapped_questions:
                print(f"   • ID {question.id}: {question.category} - {question.domain}")

def main():
    """Главная функция"""
    
    print("🚀 Запуск исправления маппинга вопросов к доменам...")
    
    # 1. Анализ текущего состояния
    analyze_question_domain_mapping()
    
    # 2. Создание маппинга
    create_question_domain_mapping()
    
    # 3. Проверка результатов
    verify_mapping_results()
    
    print("\n✅ Исправление маппинга завершено!")

if __name__ == "__main__":
    main() 