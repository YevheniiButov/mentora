"""
Обновленное отображение доменов после миграции
Унифицированная структура доменов BI-TOETS
"""

# Унифицированная карта доменов (после миграции)
UNIFIED_DOMAIN_MAPPING = {
    # Основные домены BI-TOETS
    'THER': 'Therapeutic Dentistry',
    'SURG': 'Surgical Dentistry',
    'PROTH': 'Prosthetic Dentistry',
    'PEDI': 'Pediatric Dentistry',
    'PARO': 'Periodontology',
    'ORTHO': 'Orthodontics',
    'PREV': 'Prevention',
    'ANATOMIE': 'Anatomy',
    'FYSIOLOGIE': 'Physiology',
    'PATHOLOGIE': 'Pathology',
    'MICROBIOLOGIE': 'Microbiology',
    'MATERIAALKUNDE': 'Materials Science',
    'RADIOLOGIE': 'Radiology',
    'ALGEMENE_GENEESKUNDE': 'General Medicine',
    'EMERGENCY': 'Emergency Care',
    'SYSTEMIC': 'Systemic Diseases',
    'PHARMACOLOGY': 'Pharmacology',  # Объединено с PHARMA и FARMACOLOGIE
    'INFECTION': 'Infection Control',
    'SPECIAL': 'Special Patient Groups',
    'DIAGNOSIS': 'Diagnostics',  # Объединено с DIAGNOSIS_SPECIAL
    'DUTCH': 'Dutch Healthcare System',
    'PROFESSIONAL': 'Professional Development',
    'ETHIEK': 'Ethics and Law',
    'STATISTICS': 'Statistics and Data Analysis',
    'RESEARCH_METHOD': 'Research Methodology',
    'PRACTICAL_SKILLS': 'Practical Skills',
    'TREATMENT_PLANNING': 'Treatment Planning',
    'COMMUNICATION': 'Communication Skills'
}

# Веса доменов в экзамене
DOMAIN_WEIGHTS = {
    'THER': 15.0,
    'SURG': 10.0,
    'PROTH': 8.0,
    'PEDI': 7.0,
    'PARO': 8.0,
    'ORTHO': 6.0,
    'PREV': 5.0,
    'ANATOMIE': 4.0,
    'FYSIOLOGIE': 4.0,
    'PATHOLOGIE': 5.0,
    'MICROBIOLOGIE': 3.0,
    'MATERIAALKUNDE': 3.0,
    'RADIOLOGIE': 4.0,
    'ALGEMENE_GENEESKUNDE': 2.0,
    'EMERGENCY': 10.0,
    'SYSTEMIC': 7.0,
    'PHARMACOLOGY': 8.0,
    'INFECTION': 5.0,
    'SPECIAL': 4.0,
    'DIAGNOSIS': 10.0,
    'DUTCH': 3.0,
    'PROFESSIONAL': 2.0,
    'ETHIEK': 3.0,
    'STATISTICS': 6.0,
    'RESEARCH_METHOD': 4.0,
    'PRACTICAL_SKILLS': 15.0,
    'TREATMENT_PLANNING': 10.0,
    'COMMUNICATION': 6.0
}

# Категории доменов
DOMAIN_CATEGORIES = {
    'THEORETICAL': ['THER', 'SURG', 'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 
                   'ANATOMIE', 'FYSIOLOGIE', 'PATHOLOGIE', 'MICROBIOLOGIE', 
                   'MATERIAALKUNDE', 'RADIOLOGIE', 'ALGEMENE_GENEESKUNDE', 
                   'EMERGENCY', 'SYSTEMIC', 'PHARMACOLOGY', 'INFECTION', 
                   'SPECIAL', 'DIAGNOSIS', 'DUTCH', 'PROFESSIONAL'],
    'METHODOLOGY': ['STATISTICS', 'RESEARCH_METHOD'],
    'PRACTICAL': ['PRACTICAL_SKILLS'],
    'CLINICAL': ['TREATMENT_PLANNING', 'COMMUNICATION', 'ETHIEK']
}

def get_domain_name(domain_code):
    """Получить название домена по коду"""
    return UNIFIED_DOMAIN_MAPPING.get(domain_code, domain_code)

def get_domain_weight(domain_code):
    """Получить вес домена в экзамене"""
    return DOMAIN_WEIGHTS.get(domain_code, 0.0)

def get_domain_category(domain_code):
    """Получить категорию домена"""
    for category, domains in DOMAIN_CATEGORIES.items():
        if domain_code in domains:
            return category
    return 'OTHER'

def get_all_domains():
    """Получить все домены"""
    return list(UNIFIED_DOMAIN_MAPPING.keys())

def get_domains_by_category(category):
    """Получить домены по категории"""
    return DOMAIN_CATEGORIES.get(category, [])

def convert_abilities_to_new_format(old_abilities):
    """Конвертировать старые способности в новый формат доменов"""
    if not old_abilities:
        return {}
    
    new_abilities = {}
    for old_domain, ability in old_abilities.items():
        # Применяем миграцию доменов
        new_domain = old_domain
        if old_domain == 'PHARMA':
            new_domain = 'PHARMACOLOGY'
        elif old_domain == 'FARMACOLOGIE':
            new_domain = 'PHARMACOLOGY'
        elif old_domain == 'DIAGNOSIS_SPECIAL':
            new_domain = 'DIAGNOSIS'
        
        new_abilities[new_domain] = ability
    
    return new_abilities

def convert_abilities_to_old_format(new_abilities):
    """Конвертировать новые способности в старый формат доменов (для обратной совместимости)"""
    if not new_abilities:
        return {}
    
    old_abilities = {}
    for new_domain, ability in new_abilities.items():
        # Обратная миграция доменов
        old_domain = new_domain
        if new_domain == 'PHARMACOLOGY':
            old_domain = 'PHARMA'  # Используем PHARMA как основной
        elif new_domain == 'DIAGNOSIS':
            old_domain = 'DIAGNOSIS_SPECIAL'  # Используем специальную диагностику
        
        old_abilities[old_domain] = ability
    
    return old_abilities

def map_old_to_new_domain(old_domain):
    """Маппинг старого домена в новый"""
    mapping = {
        'PHARMA': 'PHARMACOLOGY',
        'FARMACOLOGIE': 'PHARMACOLOGY',
        'DIAGNOSIS_SPECIAL': 'DIAGNOSIS'
    }
    return mapping.get(old_domain, old_domain)

# Список всех доменов BIG
ALL_BIG_DOMAINS = list(UNIFIED_DOMAIN_MAPPING.keys())

# Маппинг старых доменов в новые
OLD_TO_NEW_DOMAIN_MAPPING = {
    'PHARMA': 'PHARMACOLOGY',
    'FARMACOLOGIE': 'PHARMACOLOGY',
    'DIAGNOSIS_SPECIAL': 'DIAGNOSIS'
}
