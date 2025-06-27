# data/dutch_assessment_categories.py
# Категории оценки для работы стоматологов в Нидерландах

DUTCH_ASSESSMENT_CATEGORIES = [
    {
        'name': 'Nederlandse Zorgstandaarden',
        'name_en': 'Dutch Healthcare Standards', 
        'name_ru': 'Голландские стандарты здравоохранения',
        'slug': 'dutch_standards',
        'description': 'Знание нидерландских протоколов лечения, клинических руководств NVvT, KNMT и стандартов качества',
        'weight': 2.0,  # Очень важно
        'min_questions': 10,
        'max_questions': 15,
        'color': '#FF6B35',  # Оранжевый (цвет Нидерландов)
        'icon': 'flag',
        'is_dutch_specific': True,
        'critical_for_netherlands': True
    },
    {
        'name': 'Zorgstelsel en Financiering',
        'name_en': 'Healthcare System & Insurance',
        'name_ru': 'Система здравоохранения и страхование', 
        'slug': 'healthcare_system',
        'description': 'Понимание DBC-системы, zorgverzekering, CVZ, сотрудничество с hygienisten и mondhygienisten',
        'weight': 1.8,
        'min_questions': 8,
        'max_questions': 12,
        'color': '#0066CC',  # Синий
        'icon': 'building',
        'is_dutch_specific': True,
        'critical_for_netherlands': True
    },
    {
        'name': 'Preventieve Tandheelkunde', 
        'name_en': 'Preventive Dentistry',
        'name_ru': 'Профилактическая стоматология',
        'slug': 'preventive_care',
        'description': 'Фокус на профилактике: фторирование, герметизация, JGZ (jeugdgezondheidszorg), программы скрининга',
        'weight': 1.9,  # Очень важно в Нидерландах
        'min_questions': 10,
        'max_questions': 14,
        'color': '#22C55E',  # Зеленый
        'icon': 'shield-check',
        'is_dutch_specific': True,
        'critical_for_netherlands': True
    },
    {
        'name': 'Klinische Praktijk',
        'name_en': 'Clinical Practice',
        'name_ru': 'Клиническая практика',
        'slug': 'clinical_practice', 
        'description': 'Современные методы лечения, минимально инвазивная стоматология, композитные реставрации, эндодонтия',
        'weight': 1.7,
        'min_questions': 10,
        'max_questions': 15,
        'color': '#8B5CF6',  # Фиолетовый
        'icon': 'tools',
        'is_dutch_specific': True,
        'critical_for_netherlands': False
    },
    {
        'name': 'Patiëntcommunicatie NL',
        'name_en': 'Patient Communication (Dutch)',
        'name_ru': 'Общение с пациентами (нидерландский)',
        'slug': 'patient_communication',
        'description': 'Коммуникация на нидерландском языке, informed consent, культурные особенности, работа с жалобами',
        'weight': 1.5,
        'min_questions': 6,
        'max_questions': 10,
        'color': '#F59E0B',  # Желтый
        'icon': 'chat-dots',
        'is_dutch_specific': True,
        'critical_for_netherlands': False
    },
    {
        'name': 'Hygiëne en Veiligheid',
        'name_en': 'Hygiene & Safety',
        'name_ru': 'Гигиена и безопасность',
        'slug': 'hygiene_safety',
        'description': 'Инфекционный контроль, sterilisatie, RIVM-richtlijnen, работа с Hepatitis/HIV, COVID-19 протоколы',
        'weight': 1.6,
        'min_questions': 6,
        'max_questions': 10,
        'color': '#EF4444',  # Красный
        'icon': 'shield',
        'is_dutch_specific': True,
        'critical_for_netherlands': False
    },
    {
        'name': 'Juridische Aspecten',
        'name_en': 'Legal & Ethical Aspects',
        'name_ru': 'Правовые и этические аспекты',
        'slug': 'legal_ethics',
        'description': 'BIG-register, tuchtrecht, privacy (AVG/GDPR), beroepsgeheim, samenwerking met IGJ',
        'weight': 1.4,
        'min_questions': 5,
        'max_questions': 8,
        'color': '#64748B',  # Серый
        'icon': 'scale',
        'is_dutch_specific': True,
        'critical_for_netherlands': False
    }
]

# Специфичные пороговые значения для работы в Нидерландах
DUTCH_COMPETENCY_LEVELS = {
    'insufficient': {
        'threshold': 60,
        'description': 'Требуется дополнительное обучение перед началом работы',
        'recommendation': 'Рекомендуется курс адаптации для иностранных стоматологов'
    },
    'basic': {
        'threshold': 70,
        'description': 'Базовый уровень, может работать под супервизией',
        'recommendation': 'Необходимо кураторство опытного нидерландского стоматолога'
    },
    'competent': {
        'threshold': 80,
        'description': 'Соответствует нидерландским стандартам',
        'recommendation': 'Готов к самостоятельной работе в Нидерландах'
    },
    'proficient': {
        'threshold': 90,
        'description': 'Высокий уровень соответствия',
        'recommendation': 'Отличная подготовка для работы в нидерландской системе здравоохранения'
    }
}

# Специфичные требования для разных регионов
REGIONAL_FOCUS = {
    'urban': {
        'name': 'Grote steden (Amsterdam, Rotterdam, Den Haag)',
        'focus': ['Multicultural patients', 'Insurance complexity', 'Specialist referrals'],
        'additional_weight': {
            'patient_communication': 1.2,
            'healthcare_system': 1.3
        }
    },
    'rural': {
        'name': 'Landelijke gebieden',
        'focus': ['General practice', 'Preventive care', 'Community health'],
        'additional_weight': {
            'preventive_care': 1.3,
            'clinical_practice': 1.2
        }
    }
} 