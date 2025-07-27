"""
Question Importer Utility
Утилита для импорта вопросов из JSON файлов в базу данных
"""

import json
import logging
import click
from typing import Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Question, BIGDomain

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionImporter:
    """Класс для импорта вопросов из JSON файлов"""
    
    def __init__(self):
        self.imported_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.errors = []
        
        # Загрузить домены для автоматического назначения
        self.domains = self.load_domains()
    
    def load_domains(self) -> Dict[str, BIGDomain]:
        """Загрузить все активные домены"""
        domains = BIGDomain.query.filter_by(is_active=True).all()
        return {domain.code: domain for domain in domains}
    
    def validate_question_data(self, question_data: Dict) -> bool:
        """Проверить корректность данных вопроса"""
        required_fields = ['id', 'text', 'options', 'correct_answer_index', 'explanation']
        
        for field in required_fields:
            if field not in question_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Проверить, что options - это список
        if not isinstance(question_data['options'], list):
            logger.error(f"Options must be a list for question {question_data['id']}")
            return False
        
        # Проверить, что correct_answer_index в пределах options
        if question_data['correct_answer_index'] >= len(question_data['options']):
            logger.error(f"Correct answer index out of range for question {question_data['id']}")
            return False
        
        return True
    
    def auto_assign_domain(self, question_data: Dict) -> Optional[str]:
        """Автоматически назначить домен на основе содержимого вопроса"""
        text = question_data.get('text', '').lower()
        explanation = question_data.get('explanation', '').lower()
        category = question_data.get('category', '').lower()
        tags = question_data.get('tags', [])
        
        # Если домен уже указан, проверить его существование
        if 'domain' in question_data and question_data['domain'] in self.domains:
            return question_data['domain']
        
        # Правила назначения доменов на основе ключевых слов
        domain_rules = {
            'EMERGENCY': [
                'emergency', 'urgent', 'acute', 'anaphylaxis', 'cardiac', 'crisis',
                'неотложная', 'экстренная', 'астма', 'аллергия', 'шок'
            ],
            'SYSTEMIC': [
                'diabetes', 'hypertension', 'renal', 'cardiac', 'autoimmune',
                'диабет', 'гипертония', 'почечная', 'сердечная', 'аутоиммунная'
            ],
            'PHARMA': [
                'medication', 'drug', 'antibiotic', 'anticoagulant', 'interaction',
                'лекарство', 'препарат', 'антибиотик', 'антикоагулянт', 'взаимодействие'
            ],
            'INFECTION': [
                'infection', 'sterilization', 'hiv', 'hbv', 'covid', 'protocol',
                'инфекция', 'стерилизация', 'вич', 'гепатит', 'протокол'
            ],
            'SPECIAL': [
                'dementia', 'autism', 'refugee', 'palliative', 'disability',
                'деменция', 'аутизм', 'беженец', 'паллиативная', 'инвалидность'
            ],
            'DIAGNOSIS': [
                'diagnosis', 'differential', 'syndrome', 'rare', 'complex',
                'диагноз', 'дифференциальный', 'синдром', 'редкий', 'сложный'
            ],
            'DUTCH': [
                'avg', 'gdpr', 'big-wet', 'zorgverzekering', 'dutch', 'netherlands',
                'голландская', 'нидерланды', 'закон', 'страховка'
            ],
            'PROFESSIONAL': [
                'nascholing', 'peer review', 'ethics', 'professional', 'development',
                'образование', 'этика', 'профессиональное', 'развитие', 'коллеги'
            ]
        }
        
        # Проверить каждый домен
        for domain_code, keywords in domain_rules.items():
            for keyword in keywords:
                if (keyword in text or keyword in explanation or 
                    keyword in category or keyword in [tag.lower() for tag in tags]):
                    return domain_code
        
        # Если не найден подходящий домен, вернуть None
        return None
    
    def create_question(self, question_data: Dict) -> Optional[Question]:
        """Создать объект вопроса из данных"""
        try:
            # Автоматически назначить домен, если не указан
            domain_code = question_data.get('domain')
            if not domain_code:
                domain_code = self.auto_assign_domain(question_data)
                if domain_code:
                    logger.info(f"Auto-assigned domain {domain_code} to question {question_data['id']}")
                else:
                    logger.warning(f"Could not auto-assign domain to question {question_data['id']}")
                    domain_code = 'THER'  # Домен по умолчанию
            
            # Создать IRT параметры
            irt_params = question_data.get('irt_params', {})
            if not irt_params:
                # Создать базовые IRT параметры
                irt_params = {
                    'difficulty': question_data.get('difficulty_level', 1) * 0.5,
                    'discrimination': 1.5,
                    'guessing': 0.25
                }
            
            # Создать объект вопроса
            question = Question(
                id=question_data['id'],
                text=question_data['text'],
                options=json.dumps(question_data['options']),
                correct_answer=question_data['correct_answer_index'],
                explanation=question_data['explanation'],
                category=question_data.get('category', ''),
                domain=domain_code,
                difficulty_level=question_data.get('difficulty_level', 1),
                image_url=question_data.get('image_url'),
                tags=json.dumps(question_data.get('tags', [])),
                irt_params=json.dumps(irt_params),
                created_at=datetime.now(timezone.utc)
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Error creating question {question_data.get('id', 'unknown')}: {str(e)}")
            self.errors.append(f"Question {question_data.get('id', 'unknown')}: {str(e)}")
            return None
    
    def import_questions_from_json(self, json_file_path: str, dry_run: bool = False) -> Dict:
        """Импортировать вопросы из JSON файла"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            logger.info(f"Starting import of {len(questions_data)} questions from {json_file_path}")
            
            if dry_run:
                logger.info("DRY RUN MODE - No changes will be made to database")
            
            for question_data in questions_data:
                try:
                    # Проверить корректность данных
                    if not self.validate_question_data(question_data):
                        self.error_count += 1
                        continue
                    
                    # Проверить, существует ли вопрос
                    existing_question = Question.query.get(question_data['id'])
                    if existing_question:
                        logger.info(f"Question {question_data['id']} already exists, skipping...")
                        self.skipped_count += 1
                        continue
                    
                    # Создать вопрос
                    question = self.create_question(question_data)
                    if not question:
                        self.error_count += 1
                        continue
                    
                    if not dry_run:
                        # Добавить в базу данных
                        db.session.add(question)
                        db.session.commit()
                        self.imported_count += 1
                        logger.info(f"Imported question {question_data['id']}")
                    else:
                        self.imported_count += 1
                        logger.info(f"Would import question {question_data['id']} (dry run)")
                
                except IntegrityError as e:
                    logger.error(f"Integrity error for question {question_data.get('id', 'unknown')}: {str(e)}")
                    db.session.rollback()
                    self.error_count += 1
                    self.errors.append(f"Integrity error for question {question_data.get('id', 'unknown')}: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error processing question {question_data.get('id', 'unknown')}: {str(e)}")
                    self.error_count += 1
                    self.errors.append(f"Error processing question {question_data.get('id', 'unknown')}: {str(e)}")
            
            # Финальная статистика
            stats = {
                'imported': self.imported_count,
                'skipped': self.skipped_count,
                'errors': self.error_count,
                'total_processed': len(questions_data),
                'error_details': self.errors
            }
            
            logger.info(f"Import completed. Stats: {stats}")
            return stats
            
        except FileNotFoundError:
            error_msg = f"File not found: {json_file_path}"
            logger.error(error_msg)
            return {'error': error_msg}
        
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in file {json_file_path}: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
        
        except Exception as e:
            error_msg = f"Unexpected error during import: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def import_questions_from_directory(self, directory_path: str, pattern: str = "*.json", dry_run: bool = False) -> Dict:
        """Импортировать вопросы из всех JSON файлов в директории"""
        import glob
        import os
        
        json_files = glob.glob(os.path.join(directory_path, pattern))
        
        if not json_files:
            return {'error': f"No JSON files found in {directory_path} matching pattern {pattern}"}
        
        total_stats = {
            'files_processed': 0,
            'total_imported': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'file_results': []
        }
        
        for json_file in json_files:
            logger.info(f"Processing file: {json_file}")
            
            # Сбросить счетчики для каждого файла
            self.imported_count = 0
            self.skipped_count = 0
            self.error_count = 0
            self.errors = []
            
            # Импортировать вопросы из файла
            result = self.import_questions_from_json(json_file, dry_run)
            
            if 'error' in result:
                total_stats['file_results'].append({
                    'file': json_file,
                    'error': result['error']
                })
            else:
                total_stats['files_processed'] += 1
                total_stats['total_imported'] += result['imported']
                total_stats['total_skipped'] += result['skipped']
                total_stats['total_errors'] += result['errors']
                
                total_stats['file_results'].append({
                    'file': json_file,
                    'stats': result
                })
        
        logger.info(f"Directory import completed. Total stats: {total_stats}")
        return total_stats

def import_questions_from_json(json_file_path: str, dry_run: bool = False) -> Dict:
    """Функция-обертка для импорта вопросов"""
    importer = QuestionImporter()
    return importer.import_questions_from_json(json_file_path, dry_run)

def import_questions_from_directory(directory_path: str, pattern: str = "*.json", dry_run: bool = False) -> Dict:
    """Функция-обертка для импорта вопросов из директории"""
    importer = QuestionImporter()
    return importer.import_questions_from_directory(directory_path, pattern, dry_run)

# Flask CLI команды
def register_cli_commands(app):
    """Зарегистрировать CLI команды для Flask"""
    
    @app.cli.command()
    @click.argument('json_file')
    @click.option('--dry-run', is_flag=True, help='Run without making changes to database')
    def import_questions(json_file, dry_run):
        """Import questions from JSON file"""
        import click
        
        result = import_questions_from_json(json_file, dry_run)
        
        if 'error' in result:
            click.echo(f"Error: {result['error']}", err=True)
            return 1
        
        click.echo(f"Import completed successfully!")
        click.echo(f"Imported: {result['imported']}")
        click.echo(f"Skipped: {result['skipped']}")
        click.echo(f"Errors: {result['errors']}")
        
        if result['errors'] > 0:
            click.echo("\nError details:")
            for error in result['error_details']:
                click.echo(f"  - {error}")
        
        return 0
    
    @app.cli.command()
    @click.argument('directory')
    @click.option('--pattern', default='*.json', help='File pattern to match')
    @click.option('--dry-run', is_flag=True, help='Run without making changes to database')
    def import_questions_batch(directory, pattern, dry_run):
        """Import questions from all JSON files in directory"""
        import click
        
        result = import_questions_from_directory(directory, pattern, dry_run)
        
        if 'error' in result:
            click.echo(f"Error: {result['error']}", err=True)
            return 1
        
        click.echo(f"Batch import completed successfully!")
        click.echo(f"Files processed: {result['files_processed']}")
        click.echo(f"Total imported: {result['total_imported']}")
        click.echo(f"Total skipped: {result['total_skipped']}")
        click.echo(f"Total errors: {result['total_errors']}")
        
        click.echo("\nFile results:")
        for file_result in result['file_results']:
            if 'error' in file_result:
                click.echo(f"  {file_result['file']}: ERROR - {file_result['error']}")
            else:
                stats = file_result['stats']
                click.echo(f"  {file_result['file']}: {stats['imported']} imported, {stats['skipped']} skipped, {stats['errors']} errors")
        
        return 0 