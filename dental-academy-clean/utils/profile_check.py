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

