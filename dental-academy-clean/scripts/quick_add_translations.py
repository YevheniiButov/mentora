#!/usr/bin/env python3
"""
Quick script to add Learning Map translations to remaining language files
"""

import os

# Translations for each language
translations = {
    'pt': {
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
        'clinical_foundations': 'Fundamentos Clínicos',
        'medical_sciences': 'Ciências Médicas',
        'diagnostics_imaging': 'Diagnóstico e Imagem',
        'basic_sciences': 'Ciências Básicas',
        'research_methodology': 'Pesquisa e Metodologia',
        'clinical_practice': 'Prática Clínica',
        'professional_development': 'Desenvolvimento Profissional',
        'internal_medicine': 'Medicina Interna',
        'pediatrics': 'Pediatria',
        'gynecology': 'Ginecologia',
        'psychiatry': 'Psiquiatria',
        'emergency_medicine': 'Medicina de Emergência',
        'preventive_medicine': 'Medicina Preventiva',
        'geriatrics': 'Geriatria',
        'family_medicine': 'Medicina de Família',
    },
    
    'uk': {
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
        'clinical_foundations': 'Клінічні Основи',
        'medical_sciences': 'Медичні Науки',
        'diagnostics_imaging': 'Діагностика та Візуалізація',
        'basic_sciences': 'Базові Науки',
        'research_methodology': 'Дослідження та Методологія',
        'clinical_practice': 'Клінічна Практика',
        'professional_development': 'Професійний Розвиток',
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
        'clinical_foundations': 'Klinik Temeller',
        'medical_sciences': 'Tıp Bilimleri',
        'diagnostics_imaging': 'Tanı ve Görüntüleme',
        'basic_sciences': 'Temel Bilimler',
        'research_methodology': 'Araştırma ve Metodoloji',
        'clinical_practice': 'Klinik Uygulama',
        'professional_development': 'Mesleki Gelişim',
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
        'clinical_foundations': 'مبانی بالینی',
        'medical_sciences': 'علوم پزشکی',
        'diagnostics_imaging': 'تشخیص و تصویربرداری',
        'basic_sciences': 'علوم پایه',
        'research_methodology': 'پژوهش و روش‌شناسی',
        'clinical_practice': 'عمل بالینی',
        'professional_development': 'توسعه حرفه‌ای',
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

def add_translations(lang_code, translations_dict):
    """Add translations to a language file"""
    file_path = f"translations/{lang_code}.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return False
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the last closing brace
    last_brace = content.rfind('}')
    if last_brace == -1:
        print(f"❌ Could not find closing brace in {file_path}")
        return False
    
    # Insert new translations before the last closing brace
    new_translations = ",\n    ".join([f"'{key}': '{value}'" for key, value in translations_dict.items()])
    new_content = content[:last_brace] + f",\n    \n    # Learning Map translations\n    {new_translations}\n" + content[last_brace:]
    
    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Added {len(translations_dict)} translations to {file_path}")
    return True

def main():
    """Main function"""
    print("🌍 Adding Learning Map translations to remaining language files...")
    
    for lang_code, lang_translations in translations.items():
        print(f"\n📝 Processing {lang_code}...")
        success = add_translations(lang_code, lang_translations)
        if not success:
            print(f"❌ Failed to add translations for {lang_code}")
    
    print("\n🎉 All Learning Map translations added!")

if __name__ == '__main__':
    main()







