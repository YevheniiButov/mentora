"""
Utility functions for checking profile completeness
"""

def check_profile_complete(user):
    """
    Проверяет полноту профиля пользователя для доступа к карте обучения
    
    Требования:
    - Обязательные поля: profession, study_country
    - Хотя бы одно поле об образовании должно быть заполнено:
      * university_name
      * degree_type
      * diploma_info
      * medical_specialization
      * additional_education_info
    
    Returns:
        dict: {
            'is_complete': bool,
            'missing_fields': list[str],
            'missing_education': bool
        }
    """
    required_fields = {
        'profession': user.profession,
        'study_country': user.study_country,
    }
    
    # Хотя бы одно из полей об образовании должно быть заполнено
    education_fields = [
        user.university_name,
        user.degree_type,
        user.diploma_info,
        user.medical_specialization,
        user.additional_education_info
    ]
    has_education_info = any(field for field in education_fields if field and str(field).strip())
    
    # Проверяем обязательные поля
    missing_required = [field for field, value in required_fields.items() if not value or not str(value).strip()]
    
    # Профиль считается неполным, если отсутствуют обязательные поля или информация об образовании
    is_complete = len(missing_required) == 0 and has_education_info
    
    return {
        'is_complete': is_complete,
        'missing_fields': missing_required,
        'missing_education': not has_education_info
    }


def calculate_profile_completion_percentage(user):
    """
    Рассчитывает процент заполнения профиля пользователя
    
    Поля для проверки:
    - Основная информация (30%): first_name, last_name, email, phone, date_of_birth
    - Профессиональная информация (40%): profession, study_country, medical_specialization
    - Образование (30%): university_name, degree_type, diploma_info, additional_education_info
    
    Returns:
        int: Процент заполнения профиля (0-100)
    """
    # Основная информация (5 полей - 30%)
    basic_fields = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': getattr(user, 'phone', None),
        'date_of_birth': getattr(user, 'date_of_birth', None),
    }
    basic_filled = sum(1 for value in basic_fields.values() if value and str(value).strip())
    basic_percentage = (basic_filled / len(basic_fields)) * 30
    
    # Профессиональная информация (3 поля - 40%)
    professional_fields = {
        'profession': user.profession,
        'study_country': user.study_country,
        'medical_specialization': getattr(user, 'medical_specialization', None),
    }
    professional_filled = sum(1 for value in professional_fields.values() if value and str(value).strip())
    professional_percentage = (professional_filled / len(professional_fields)) * 40
    
    # Образование (4 поля - 30%)
    education_fields = {
        'university_name': getattr(user, 'university_name', None),
        'degree_type': getattr(user, 'degree_type', None),
        'diploma_info': getattr(user, 'diploma_info', None),
        'additional_education_info': getattr(user, 'additional_education_info', None),
    }
    education_filled = sum(1 for value in education_fields.values() if value and str(value).strip())
    education_percentage = (education_filled / len(education_fields)) * 30
    
    # Итоговый процент
    total_percentage = basic_percentage + professional_percentage + education_percentage
    
    return min(100, int(total_percentage))

