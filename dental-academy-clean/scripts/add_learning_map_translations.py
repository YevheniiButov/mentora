#!/usr/bin/env python3
"""
Script to add Learning Map translations to all language files
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Learning Map translations to add
LEARNING_MAP_TRANSLATIONS = {
    'en': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Individual Plan',
        'daily_study_plan': 'Your Daily Study Plan',
        'daily_streak': 'Daily Streak',
        'days': 'days',
        'daily_progress': 'Daily Progress',
        'categories_progress': 'Progress per Category',
        'focus_on_category': 'Focus on Category',
        'overall_stats': 'Overall Stats',
        'total_progress': 'Total Progress',
        'time_invested': 'Time Invested',
        'retention_rate': 'Retention Rate',
        'start_daily_session': 'Start Daily Session',
        'quick_diagnostic': 'Quick Diagnostic',
        'quick_diagnostic_title': 'Quick Diagnostic Test',
        'quick_diagnostic_description': '30 questions, 20 minutes to assess your current knowledge level',
        'start_quick_test': 'Start Quick Test',
        'cancel': 'Cancel',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Progress Overview',
        'total_questions_answered': 'Questions Answered',
        'study_time': 'Study Time',
        'categories_breakdown': 'Categories Breakdown',
        'study_activity': 'Study Activity',
        'recent_sessions': 'Recent Sessions',
        'streak_badges': 'Streak Badges',
        'question_badges': 'Question Badges',
        'category_badges': 'Category Badges',
        'earned': 'Earned',
        'locked': 'Locked',
        'more_days': 'More days',
        'more_questions': 'More questions',
        'more_categories': 'More categories',
        
        # Category names for Tandarts
        'clinical_foundations': 'Clinical Foundations',
        'medical_sciences': 'Medical Sciences',
        'diagnostics_imaging': 'Diagnostics & Imaging',
        'basic_sciences': 'Basic Sciences',
        'research_methodology': 'Research & Methodology',
        'clinical_practice': 'Clinical Practice',
        'professional_development': 'Professional Development',
        
        # Category names for Huisarts
        'internal_medicine': 'Internal Medicine',
        'pediatrics': 'Pediatrics',
        'gynecology': 'Gynecology',
        'psychiatry': 'Psychiatry',
        'emergency_medicine': 'Emergency Medicine',
        'preventive_medicine': 'Preventive Medicine',
        'geriatrics': 'Geriatrics',
        'family_medicine': 'Family Medicine',
    },
    
    'nl': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Individueel Plan',
        'daily_study_plan': 'Je dagelijkse studieplan',
        'daily_streak': 'Dagelijkse Streak',
        'days': 'dagen',
        'daily_progress': 'Dagelijkse Voortgang',
        'categories_progress': 'Voortgang per categorie',
        'focus_on_category': 'Focus op Categorie',
        'overall_stats': 'Algemene Statistieken',
        'total_progress': 'Totale voortgang',
        'time_invested': 'Geïnvesteerde tijd',
        'retention_rate': 'Retentie rate',
        'start_daily_session': 'Start dagelijkse sessie',
        'quick_diagnostic': 'Snelle Diagnostiek',
        'quick_diagnostic_title': 'Snelle Diagnostische Test',
        'quick_diagnostic_description': '30 vragen, 20 minuten om je huidige kennisniveau te beoordelen',
        'start_quick_test': 'Start Snelle Test',
        'cancel': 'Annuleren',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Voortgang Overzicht',
        'total_questions_answered': 'Vragen beantwoord',
        'study_time': 'Studietijd',
        'categories_breakdown': 'Categorieën Overzicht',
        'study_activity': 'Studie Activiteit',
        'recent_sessions': 'Recente Sessies',
        'streak_badges': 'Streak Badges',
        'question_badges': 'Vraag Badges',
        'category_badges': 'Categorie Badges',
        'earned': 'Verdiend',
        'locked': 'Vergrendeld',
        'more_days': 'Meer dagen',
        'more_questions': 'Meer vragen',
        'more_categories': 'Meer categorieën',
        
        # Category names for Tandarts
        'clinical_foundations': 'Klinische Grondslagen',
        'medical_sciences': 'Medische Wetenschappen',
        'diagnostics_imaging': 'Diagnostiek & Beeldvorming',
        'basic_sciences': 'Basiswetenschappen',
        'research_methodology': 'Onderzoek & Methodologie',
        'clinical_practice': 'Klinische Praktijk',
        'professional_development': 'Professionele Ontwikkeling',
        
        # Category names for Huisarts
        'internal_medicine': 'Interne Geneeskunde',
        'pediatrics': 'Kindergeneeskunde',
        'gynecology': 'Gynaecologie',
        'psychiatry': 'Psychiatrie',
        'emergency_medicine': 'Spoedeisende Hulp',
        'preventive_medicine': 'Preventieve Geneeskunde',
        'geriatrics': 'Geriatrie',
        'family_medicine': 'Huisartsgeneeskunde',
    },
    
    'es': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Plan Individual',
        'daily_study_plan': 'Tu Plan de Estudio Diario',
        'daily_streak': 'Racha Diaria',
        'days': 'días',
        'daily_progress': 'Progreso Diario',
        'categories_progress': 'Progreso por Categoría',
        'focus_on_category': 'Enfocarse en Categoría',
        'overall_stats': 'Estadísticas Generales',
        'total_progress': 'Progreso Total',
        'time_invested': 'Tiempo Invertido',
        'retention_rate': 'Tasa de Retención',
        'start_daily_session': 'Iniciar Sesión Diaria',
        'quick_diagnostic': 'Diagnóstico Rápido',
        'quick_diagnostic_title': 'Prueba de Diagnóstico Rápido',
        'quick_diagnostic_description': '30 preguntas, 20 minutos para evaluar tu nivel actual de conocimiento',
        'start_quick_test': 'Iniciar Prueba Rápida',
        'cancel': 'Cancelar',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Resumen de Progreso',
        'total_questions_answered': 'Preguntas Respondidas',
        'study_time': 'Tiempo de Estudio',
        'categories_breakdown': 'Desglose por Categorías',
        'study_activity': 'Actividad de Estudio',
        'recent_sessions': 'Sesiones Recientes',
        'streak_badges': 'Insignias de Racha',
        'question_badges': 'Insignias de Preguntas',
        'category_badges': 'Insignias de Categoría',
        'earned': 'Ganado',
        'locked': 'Bloqueado',
        'more_days': 'Más días',
        'more_questions': 'Más preguntas',
        'more_categories': 'Más categorías',
        
        # Category names for Tandarts
        'clinical_foundations': 'Fundamentos Clínicos',
        'medical_sciences': 'Ciencias Médicas',
        'diagnostics_imaging': 'Diagnóstico e Imagenología',
        'basic_sciences': 'Ciencias Básicas',
        'research_methodology': 'Investigación y Metodología',
        'clinical_practice': 'Práctica Clínica',
        'professional_development': 'Desarrollo Profesional',
        
        # Category names for Huisarts
        'internal_medicine': 'Medicina Interna',
        'pediatrics': 'Pediatría',
        'gynecology': 'Ginecología',
        'psychiatry': 'Psiquiatría',
        'emergency_medicine': 'Medicina de Emergencia',
        'preventive_medicine': 'Medicina Preventiva',
        'geriatrics': 'Geriatría',
        'family_medicine': 'Medicina Familiar',
    },
    
    'pt': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Plano Individual',
        'daily_study_plan': 'Seu Plano de Estudo Diário',
        'daily_streak': 'Sequência Diária',
        'days': 'dias',
        'daily_progress': 'Progresso Diário',
        'categories_progress': 'Progresso por Categoria',
        'focus_on_category': 'Focar na Categoria',
        'overall_stats': 'Estatísticas Gerais',
        'total_progress': 'Progresso Total',
        'time_invested': 'Tempo Investido',
        'retention_rate': 'Taxa de Retenção',
        'start_daily_session': 'Iniciar Sessão Diária',
        'quick_diagnostic': 'Diagnóstico Rápido',
        'quick_diagnostic_title': 'Teste de Diagnóstico Rápido',
        'quick_diagnostic_description': '30 perguntas, 20 minutos para avaliar seu nível atual de conhecimento',
        'start_quick_test': 'Iniciar Teste Rápido',
        'cancel': 'Cancelar',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Visão Geral do Progresso',
        'total_questions_answered': 'Perguntas Respondidas',
        'study_time': 'Tempo de Estudo',
        'categories_breakdown': 'Detalhamento por Categorias',
        'study_activity': 'Atividade de Estudo',
        'recent_sessions': 'Sessões Recentes',
        'streak_badges': 'Emblemas de Sequência',
        'question_badges': 'Emblemas de Perguntas',
        'category_badges': 'Emblemas de Categoria',
        'earned': 'Conquistado',
        'locked': 'Bloqueado',
        'more_days': 'Mais dias',
        'more_questions': 'Mais perguntas',
        'more_categories': 'Mais categorias',
        
        # Category names for Tandarts
        'clinical_foundations': 'Fundamentos Clínicos',
        'medical_sciences': 'Ciências Médicas',
        'diagnostics_imaging': 'Diagnóstico e Imagem',
        'basic_sciences': 'Ciências Básicas',
        'research_methodology': 'Pesquisa e Metodologia',
        'clinical_practice': 'Prática Clínica',
        'professional_development': 'Desenvolvimento Profissional',
        
        # Category names for Huisarts
        'internal_medicine': 'Medicina Interna',
        'pediatrics': 'Pediatria',
        'gynecology': 'Ginecologia',
        'psychiatry': 'Psiquiatria',
        'emergency_medicine': 'Medicina de Emergência',
        'preventive_medicine': 'Medicina Preventiva',
        'geriatrics': 'Geriatria',
        'family_medicine': 'Medicina de Família',
    },
    
    'ru': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Индивидуальный План',
        'daily_study_plan': 'Ваш ежедневный план обучения',
        'daily_streak': 'Ежедневная Серия',
        'days': 'дней',
        'daily_progress': 'Ежедневный Прогресс',
        'categories_progress': 'Прогресс по категориям',
        'focus_on_category': 'Сосредоточиться на категории',
        'overall_stats': 'Общая Статистика',
        'total_progress': 'Общий прогресс',
        'time_invested': 'Потраченное время',
        'retention_rate': 'Коэффициент удержания',
        'start_daily_session': 'Начать ежедневную сессию',
        'quick_diagnostic': 'Быстрая Диагностика',
        'quick_diagnostic_title': 'Быстрый Диагностический Тест',
        'quick_diagnostic_description': '30 вопросов, 20 минут для оценки вашего текущего уровня знаний',
        'start_quick_test': 'Начать Быстрый Тест',
        'cancel': 'Отмена',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Обзор Прогресса',
        'total_questions_answered': 'Отвечено вопросов',
        'study_time': 'Время обучения',
        'categories_breakdown': 'Разбивка по категориям',
        'study_activity': 'Учебная активность',
        'recent_sessions': 'Недавние сессии',
        'streak_badges': 'Значки серий',
        'question_badges': 'Значки вопросов',
        'category_badges': 'Значки категорий',
        'earned': 'Заработано',
        'locked': 'Заблокировано',
        'more_days': 'Больше дней',
        'more_questions': 'Больше вопросов',
        'more_categories': 'Больше категорий',
        
        # Category names for Tandarts
        'clinical_foundations': 'Клинические Основы',
        'medical_sciences': 'Медицинские Науки',
        'diagnostics_imaging': 'Диагностика и Визуализация',
        'basic_sciences': 'Базовые Науки',
        'research_methodology': 'Исследования и Методология',
        'clinical_practice': 'Клиническая Практика',
        'professional_development': 'Профессиональное Развитие',
        
        # Category names for Huisarts
        'internal_medicine': 'Внутренняя Медицина',
        'pediatrics': 'Педиатрия',
        'gynecology': 'Гинекология',
        'psychiatry': 'Психиатрия',
        'emergency_medicine': 'Неотложная Медицина',
        'preventive_medicine': 'Профилактическая Медицина',
        'geriatrics': 'Гериатрия',
        'family_medicine': 'Семейная Медицина',
    },
    
    'uk': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Індивідуальний План',
        'daily_study_plan': 'Ваш щоденний план навчання',
        'daily_streak': 'Щоденна Серія',
        'days': 'днів',
        'daily_progress': 'Щоденний Прогрес',
        'categories_progress': 'Прогрес за категоріями',
        'focus_on_category': 'Зосередитися на категорії',
        'overall_stats': 'Загальна Статистика',
        'total_progress': 'Загальний прогрес',
        'time_invested': 'Витрачений час',
        'retention_rate': 'Коефіцієнт утримання',
        'start_daily_session': 'Почати щоденну сесію',
        'quick_diagnostic': 'Швидка Діагностика',
        'quick_diagnostic_title': 'Швидкий Діагностичний Тест',
        'quick_diagnostic_description': '30 питань, 20 хвилин для оцінки вашого поточного рівня знань',
        'start_quick_test': 'Почати Швидкий Тест',
        'cancel': 'Скасувати',
        
        # Learning Map - Progress Tab
        'progress_overview': 'Огляд Прогресу',
        'total_questions_answered': 'Відповіли питань',
        'study_time': 'Час навчання',
        'categories_breakdown': 'Розбивка за категоріями',
        'study_activity': 'Навчальна активність',
        'recent_sessions': 'Останні сесії',
        'streak_badges': 'Значки серій',
        'question_badges': 'Значки питань',
        'category_badges': 'Значки категорій',
        'earned': 'Зароблено',
        'locked': 'Заблоковано',
        'more_days': 'Більше днів',
        'more_questions': 'Більше питань',
        'more_categories': 'Більше категорій',
        
        # Category names for Tandarts
        'clinical_foundations': 'Клінічні Основи',
        'medical_sciences': 'Медичні Науки',
        'diagnostics_imaging': 'Діагностика та Візуалізація',
        'basic_sciences': 'Базові Науки',
        'research_methodology': 'Дослідження та Методологія',
        'clinical_practice': 'Клінічна Практика',
        'professional_development': 'Професійний Розвиток',
        
        # Category names for Huisarts
        'internal_medicine': 'Внутрішня Медицина',
        'pediatrics': 'Педіатрія',
        'gynecology': 'Гінекологія',
        'psychiatry': 'Психіатрія',
        'emergency_medicine': 'Негайна Медицина',
        'preventive_medicine': 'Профілактична Медицина',
        'geriatrics': 'Геріатрія',
        'family_medicine': 'Сімейна Медицина',
    },
    
    'tr': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'Bireysel Plan',
        'daily_study_plan': 'Günlük Çalışma Planınız',
        'daily_streak': 'Günlük Seri',
        'days': 'gün',
        'daily_progress': 'Günlük İlerleme',
        'categories_progress': 'Kategoriye Göre İlerleme',
        'focus_on_category': 'Kategoriye Odaklan',
        'overall_stats': 'Genel İstatistikler',
        'total_progress': 'Toplam İlerleme',
        'time_invested': 'Harcanan Zaman',
        'retention_rate': 'Hatırlama Oranı',
        'start_daily_session': 'Günlük Oturumu Başlat',
        'quick_diagnostic': 'Hızlı Tanı',
        'quick_diagnostic_title': 'Hızlı Tanı Testi',
        'quick_diagnostic_description': 'Mevcut bilgi seviyenizi değerlendirmek için 30 soru, 20 dakika',
        'start_quick_test': 'Hızlı Testi Başlat',
        'cancel': 'İptal',
        
        # Learning Map - Progress Tab
        'progress_overview': 'İlerleme Genel Bakış',
        'total_questions_answered': 'Cevaplanan Sorular',
        'study_time': 'Çalışma Süresi',
        'categories_breakdown': 'Kategori Detayları',
        'study_activity': 'Çalışma Aktivitesi',
        'recent_sessions': 'Son Oturumlar',
        'streak_badges': 'Seri Rozetleri',
        'question_badges': 'Soru Rozetleri',
        'category_badges': 'Kategori Rozetleri',
        'earned': 'Kazanıldı',
        'locked': 'Kilitli',
        'more_days': 'Daha fazla gün',
        'more_questions': 'Daha fazla soru',
        'more_categories': 'Daha fazla kategori',
        
        # Category names for Tandarts
        'clinical_foundations': 'Klinik Temeller',
        'medical_sciences': 'Tıp Bilimleri',
        'diagnostics_imaging': 'Tanı ve Görüntüleme',
        'basic_sciences': 'Temel Bilimler',
        'research_methodology': 'Araştırma ve Metodoloji',
        'clinical_practice': 'Klinik Uygulama',
        'professional_development': 'Mesleki Gelişim',
        
        # Category names for Huisarts
        'internal_medicine': 'İç Hastalıkları',
        'pediatrics': 'Pediatri',
        'gynecology': 'Jinekoloji',
        'psychiatry': 'Psikiyatri',
        'emergency_medicine': 'Acil Tıp',
        'preventive_medicine': 'Koruyucu Tıp',
        'geriatrics': 'Geriatri',
        'family_medicine': 'Aile Hekimliği',
    },
    
    'fa': {
        # Learning Map - Individual Plan Tab
        'individual_plan': 'برنامه فردی',
        'daily_study_plan': 'برنامه مطالعه روزانه شما',
        'daily_streak': 'سری روزانه',
        'days': 'روز',
        'daily_progress': 'پیشرفت روزانه',
        'categories_progress': 'پیشرفت بر اساس دسته‌بندی',
        'focus_on_category': 'تمرکز بر دسته‌بندی',
        'overall_stats': 'آمار کلی',
        'total_progress': 'پیشرفت کل',
        'time_invested': 'زمان سرمایه‌گذاری شده',
        'retention_rate': 'نرخ حفظ',
        'start_daily_session': 'شروع جلسه روزانه',
        'quick_diagnostic': 'تشخیص سریع',
        'quick_diagnostic_title': 'تست تشخیص سریع',
        'quick_diagnostic_description': '30 سوال، 20 دقیقه برای ارزیابی سطح فعلی دانش شما',
        'start_quick_test': 'شروع تست سریع',
        'cancel': 'لغو',
        
        # Learning Map - Progress Tab
        'progress_overview': 'نمای کلی پیشرفت',
        'total_questions_answered': 'سوالات پاسخ داده شده',
        'study_time': 'زمان مطالعه',
        'categories_breakdown': 'تفکیک دسته‌بندی‌ها',
        'study_activity': 'فعالیت مطالعه',
        'recent_sessions': 'جلسات اخیر',
        'streak_badges': 'نشان‌های سری',
        'question_badges': 'نشان‌های سوال',
        'category_badges': 'نشان‌های دسته‌بندی',
        'earned': 'کسب شده',
        'locked': 'قفل شده',
        'more_days': 'روزهای بیشتر',
        'more_questions': 'سوالات بیشتر',
        'more_categories': 'دسته‌بندی‌های بیشتر',
        
        # Category names for Tandarts
        'clinical_foundations': 'مبانی بالینی',
        'medical_sciences': 'علوم پزشکی',
        'diagnostics_imaging': 'تشخیص و تصویربرداری',
        'basic_sciences': 'علوم پایه',
        'research_methodology': 'پژوهش و روش‌شناسی',
        'clinical_practice': 'عمل بالینی',
        'professional_development': 'توسعه حرفه‌ای',
        
        # Category names for Huisarts
        'internal_medicine': 'پزشکی داخلی',
        'pediatrics': 'کودکان',
        'gynecology': 'زنان و زایمان',
        'psychiatry': 'روانپزشکی',
        'emergency_medicine': 'پزشکی اورژانس',
        'preventive_medicine': 'پزشکی پیشگیرانه',
        'geriatrics': 'پزشکی سالمندان',
        'family_medicine': 'پزشکی خانواده',
    }
}

def add_translations_to_file(lang_code, translations):
    """Add translations to a specific language file"""
    file_path = f"translations/{lang_code}.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return False
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if translations already exist
    if any(key in content for key in translations.keys()):
        print(f"⚠️ Some translations already exist in {file_path}")
        return False
    
    # Find the last closing brace
    last_brace = content.rfind('}')
    if last_brace == -1:
        print(f"❌ Could not find closing brace in {file_path}")
        return False
    
    # Insert new translations before the last closing brace
    new_translations = ",\n    ".join([f"'{key}': '{value}'" for key, value in translations.items()])
    new_content = content[:last_brace] + f",\n    \n    # Learning Map translations\n    {new_translations}\n" + content[last_brace:]
    
    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Added {len(translations)} translations to {file_path}")
    return True

def main():
    """Main function to add translations to all language files"""
    print("🌍 Adding Learning Map translations to all language files...")
    
    # Languages to process (excluding en, nl, ru which we already updated)
    languages = ['es', 'pt', 'uk', 'tr', 'fa']
    
    for lang in languages:
        if lang in LEARNING_MAP_TRANSLATIONS:
            print(f"\n📝 Processing {lang}...")
            success = add_translations_to_file(lang, LEARNING_MAP_TRANSLATIONS[lang])
            if not success:
                print(f"❌ Failed to add translations for {lang}")
        else:
            print(f"⚠️ No translations defined for {lang}")
    
    print("\n🎉 Learning Map translations added to all language files!")

if __name__ == '__main__':
    main()
