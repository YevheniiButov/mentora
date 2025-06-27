# data/dutch_assessment_questions.py
# Вопросы для оценки готовности к работе стоматологом в Нидерландах

DUTCH_DENTAL_QUESTIONS = [
    # ===== NEDERLANDSE ZORGSTANDAARDEN (15 вопросов) =====
    {
        "category": "dutch_standards",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой орган отвечает за разработку клинических руководств в нидерландской стоматологии?",
        "options": [
            "KNMT (Koninklijke Nederlandse Maatschappij tot bevordering der Tandheelkunde)",
            "NVvT (Nederlandse Vereniging voor Tandheelkunde)",
            "RIVM (Rijksinstituut voor Volksgezondheid en Milieu)",
            "IGJ (Inspectie Gezondheidszorg en Jeugd)"
        ],
        "correct_answer": 0,
        "explanation": "KNMT - Королевское нидерландское общество содействия стоматологии является основным органом, разрабатывающим клинические руководства.",
        "related_modules": [101, 102]
    },
    {
        "category": "dutch_standards",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой стандарт качества применяется в нидерландских стоматологических клиниках?",
        "options": [
            "ISO 9001",
            "NEN-EN-ISO 13485",
            "HKZ (Harmonisatie Kwaliteitsbeoordeling in de Zorgsector)",
            "NIAZ (Nederlands Instituut voor Accreditatie in de Zorg)"
        ],
        "correct_answer": 2,
        "explanation": "HKZ - Гармонизация оценки качества в секторе здравоохранения является основным стандартом для нидерландских клиник.",
        "related_modules": [103, 104]
    },
    {
        "category": "dutch_standards",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой протокол лечения кариеса рекомендован KNMT для взрослых пациентов?",
        "options": [
            "Немедленное препарирование и пломбирование",
            "Наблюдение при начальном кариесе, лечение при прогрессировании",
            "Профилактические меры без лечения",
            "Направление к специалисту"
        ],
        "correct_answer": 1,
        "explanation": "KNMT рекомендует консервативный подход: наблюдение за начальным кариесом и лечение только при прогрессировании.",
        "related_modules": [105, 106]
    },
    {
        "category": "dutch_standards",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой минимальный возраст для начала ортодонтического лечения в Нидерландах?",
        "options": [
            "6 лет",
            "8 лет", 
            "10 лет",
            "12 лет"
        ],
        "correct_answer": 1,
        "explanation": "В Нидерландах ортодонтическое лечение обычно начинается в возрасте 8-9 лет, когда прорезываются постоянные резцы.",
        "related_modules": [107, 108]
    },
    {
        "category": "dutch_standards",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой протокол применяется при лечении пациентов с сердечно-сосудистыми заболеваниями?",
        "options": [
            "Антибиотикопрофилактика для всех процедур",
            "Антибиотикопрофилактика только для инвазивных процедур",
            "Консультация с кардиологом перед лечением",
            "Отказ от лечения"
        ],
        "correct_answer": 1,
        "explanation": "Антибиотикопрофилактика применяется только для инвазивных процедур у пациентов с высоким риском эндокардита.",
        "related_modules": [109, 110]
    },

    # ===== ZORGSTELSEL EN FINANCIERING (12 вопросов) =====
    {
        "category": "healthcare_system",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Что означает аббревиатура DBC в нидерландской системе здравоохранения?",
        "options": [
            "Diagnose Behandeling Combinatie",
            "Dental Basic Care",
            "Dutch Basic Coverage",
            "Diagnosis Based Care"
        ],
        "correct_answer": 0,
        "explanation": "DBC (Diagnose Behandeling Combinatie) - система диагностико-лечебных комбинаций для тарификации медицинских услуг.",
        "related_modules": [201, 202]
    },
    {
        "category": "healthcare_system",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой тип страхования покрывает базовую стоматологическую помощь в Нидерландах?",
        "options": [
            "Basisverzekering (базовое страхование)",
            "Aanvullendeverzekering (дополнительное страхование)",
            "Tandartsverzekering (стоматологическое страхование)",
            "Geen verzekering (без страхования)"
        ],
        "correct_answer": 1,
        "explanation": "Дополнительное страхование (Aanvullendeverzekering) покрывает базовую стоматологическую помощь для взрослых.",
        "related_modules": [203, 204]
    },
    {
        "category": "healthcare_system",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой орган определяет тарифы на стоматологические услуги?",
        "options": [
            "NZa (Nederlandse Zorgautoriteit)",
            "CVZ (College voor Zorgverzekeringen)",
            "KNMT",
            "Ministerie van VWS"
        ],
        "correct_answer": 0,
        "explanation": "NZa (Нидерландская организация здравоохранения) определяет тарифы на медицинские и стоматологические услуги.",
        "related_modules": [205, 206]
    },
    {
        "category": "healthcare_system",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой процент от стоимости лечения покрывает базовое стоматологическое страхование для детей до 18 лет?",
        "options": [
            "50%",
            "75%",
            "90%",
            "100%"
        ],
        "correct_answer": 3,
        "explanation": "Базовое страхование покрывает 100% стоимости стоматологического лечения для детей до 18 лет.",
        "related_modules": [207, 208]
    },

    # ===== PREVENTIEVE TANDHEELKUNDE (14 вопросов) =====
    {
        "category": "preventive_care",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой возраст является оптимальным для начала фторирования зубов в Нидерландах?",
        "options": [
            "С момента прорезывания первого зуба",
            "2-3 года",
            "4-5 лет",
            "6-7 лет"
        ],
        "correct_answer": 0,
        "explanation": "Фторирование рекомендуется начинать с момента прорезывания первого молочного зуба.",
        "related_modules": [301, 302]
    },
    {
        "category": "preventive_care",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой протокол герметизации фиссур применяется в нидерландской практике?",
        "options": [
            "Герметизация всех постоянных моляров",
            "Герметизация только глубоких фиссур",
            "Герметизация по показаниям (риск кариеса)",
            "Герметизация не применяется"
        ],
        "correct_answer": 2,
        "explanation": "В Нидерландах герметизация применяется по показаниям, основываясь на оценке риска кариеса.",
        "related_modules": [303, 304]
    },
    {
        "category": "preventive_care",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой орган отвечает за программы скрининга здоровья детей (JGZ)?",
        "options": [
            "Gemeente (муниципалитет)",
            "GGD (Gemeentelijke Gezondheidsdienst)",
            "RIVM",
            "Ministerie van VWS"
        ],
        "correct_answer": 1,
        "explanation": "GGD (Муниципальная служба здравоохранения) отвечает за программы JGZ и скрининг здоровья детей.",
        "related_modules": [305, 306]
    },
    {
        "category": "preventive_care",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой интервал между профилактическими осмотрами рекомендуется для взрослых пациентов?",
        "options": [
            "3 месяца",
            "6 месяцев",
            "1 год",
            "Индивидуально по риску"
        ],
        "correct_answer": 3,
        "explanation": "Интервал между осмотрами определяется индивидуально на основе риска кариеса и заболеваний пародонта.",
        "related_modules": [307, 308]
    },

    # ===== KLINISCHE PRAKTIJK (15 вопросов) =====
    {
        "category": "clinical_practice",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой материал является предпочтительным для реставраций в нидерландской практике?",
        "options": [
            "Амальгама",
            "Композитные материалы",
            "Керамика",
            "Стеклоиономер"
        ],
        "correct_answer": 1,
        "explanation": "Композитные материалы являются предпочтительными для реставраций из-за эстетики и адгезии.",
        "related_modules": [401, 402]
    },
    {
        "category": "clinical_practice",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой протокол применяется при лечении пульпита в Нидерландах?",
        "options": [
            "Немедленная экстирпация пульпы",
            "Попытка сохранения пульпы (витальная ампутация)",
            "Наблюдение",
            "Направление к эндодонтисту"
        ],
        "correct_answer": 1,
        "explanation": "В Нидерландах предпочтение отдается сохранению пульпы при возможности (витальная ампутация).",
        "related_modules": [403, 404]
    },
    {
        "category": "clinical_practice",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой минимально инвазивный подход применяется при лечении кариеса?",
        "options": [
            "Традиционное препарирование",
            "Air-abrasion",
            "Лазерная обработка",
            "Комбинация методов"
        ],
        "correct_answer": 3,
        "explanation": "Применяется комбинация минимально инвазивных методов в зависимости от клинической ситуации.",
        "related_modules": [405, 406]
    },

    # ===== PATIËNTCOMMUNICATIE NL (10 вопросов) =====
    {
        "category": "patient_communication",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой уровень голландского языка требуется для работы стоматологом?",
        "options": [
            "A2 (базовый)",
            "B1 (средний)",
            "B2 (выше среднего)",
            "C1 (продвинутый)"
        ],
        "correct_answer": 2,
        "explanation": "Для работы стоматологом требуется уровень B2, позволяющий эффективно общаться с пациентами.",
        "related_modules": [501, 502]
    },
    {
        "category": "patient_communication",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой документ необходим для получения информированного согласия?",
        "options": [
            "Устное согласие",
            "Письменное согласие на голландском языке",
            "Перевод на родной язык пациента",
            "Видеозапись согласия"
        ],
        "correct_answer": 1,
        "explanation": "Информированное согласие должно быть получено в письменной форме на голландском языке.",
        "related_modules": [503, 504]
    },

    # ===== HYGIËNE EN VEILIGHEID (10 вопросов) =====
    {
        "category": "hygiene_safety",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой протокол стерилизации применяется в нидерландских клиниках?",
        "options": [
            "Автоклавирование при 121°C",
            "Автоклавирование при 134°C",
            "Химическая стерилизация",
            "Ультрафиолетовое облучение"
        ],
        "correct_answer": 1,
        "explanation": "В Нидерландах применяется автоклавирование при 134°C в течение 3-4 минут.",
        "related_modules": [601, 602]
    },
    {
        "category": "hygiene_safety",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой орган разрабатывает руководства по инфекционному контролю?",
        "options": [
            "RIVM",
            "KNMT",
            "IGJ",
            "Ministerie van VWS"
        ],
        "correct_answer": 0,
        "explanation": "RIVM (Национальный институт общественного здравоохранения) разрабатывает руководства по инфекционному контролю.",
        "related_modules": [603, 604]
    },

    # ===== JURIDISCHE ASPECTEN (8 вопросов) =====
    {
        "category": "legal_ethics",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Что означает аббревиатура BIG в контексте регистрации стоматологов?",
        "options": [
            "Beroepen in de Individuele Gezondheidszorg",
            "Basis Inschrijving Gezondheidszorg",
            "Beroepsregister In de Gezondheidszorg",
            "Bevoegdheid In de Gezondheidszorg"
        ],
        "correct_answer": 0,
        "explanation": "BIG (Beroepen in de Individuele Gezondheidszorg) - Закон о профессиях в индивидуальном здравоохранении.",
        "related_modules": [701, 702]
    },
    {
        "category": "legal_ethics",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой орган рассматривает жалобы на стоматологов в Нидерландах?",
        "options": [
            "Tuchtcollege voor de Gezondheidszorg",
            "KNMT",
            "IGJ",
            "Rechtbank"
        ],
        "correct_answer": 0,
        "explanation": "Дисциплинарный совет здравоохранения (Tuchtcollege) рассматривает жалобы на медицинских работников.",
        "related_modules": [703, 704]
    }
]

# BIG EXAM MEDICAL KNOWLEDGE QUESTIONS (добавить к существующему массиву)

# ===== BASIC MEDICAL SCIENCES (25 вопросов) =====
BIG_MEDICAL_QUESTIONS = [
    {
        "category": "big_medical_knowledge",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой нерв отвечает за иннервацию верхних резцов?",
        "options": [
            "Передний верхний альвеолярный нерв",
            "Средний верхний альвеолярный нерв", 
            "Задний верхний альвеолярный нерв",
            "Носонебный нерв"
        ],
        "correct_answer": 0,
        "explanation": "Передний верхний альвеолярный нерв (ветвь подглазничного нерва) иннервирует верхние резцы и клыки.",
        "related_modules": [101, 102]
    },
    {
        "category": "big_medical_knowledge", 
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какова нормальная последовательность свертывания крови?",
        "options": [
            "Активация тромбоцитов → активация коагуляционного каскада → образование фибрина",
            "Активация коагуляционного каскада → активация тромбоцитов → образование фибрина",
            "Образование фибрина → активация тромбоцитов → активация каскада",
            "Активация тромбоцитов → образование фибрина → активация каскада"
        ],
        "correct_answer": 0,
        "explanation": "Гемостаз происходит в три этапа: первичный (тромбоцитарный), вторичный (коагуляционный) и фибринолиз.",
        "related_modules": [103, 104]
    },
    {
        "category": "big_medical_knowledge",
        "difficulty": 3, 
        "time_limit": 90,
        "question": "Какой витамин необходим для синтеза коллагена?",
        "options": [
            "Витамин A",
            "Витамин B12",
            "Витамин C", 
            "Витамин D"
        ],
        "correct_answer": 2,
        "explanation": "Витамин C (аскорбиновая кислота) является кофактором для ферментов, участвующих в гидроксилировании пролина и лизина при синтезе коллагена.",
        "related_modules": [105, 106]
    }
]

# ===== CLINICAL DIAGNOSIS (20 вопросов) =====
BIG_CLINICAL_QUESTIONS = [
    {
        "category": "big_clinical_skills",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какой наиболее надежный метод диагностики пульпита?",
        "options": [
            "Рентгенография",
            "Тест на чувствительность к холоду",
            "Электроодонтометрия (ЭОМ)",
            "Комбинация клинических тестов и анамнеза"
        ],
        "correct_answer": 3,
        "explanation": "Диагностика пульпита требует комплексного подхода: анамнез + клинические тесты + рентген. Ни один тест не является абсолютно надежным.",
        "related_modules": [107, 108]
    },
    {
        "category": "big_clinical_skills",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой признак наиболее характерен для острого периодонтита?",
        "options": [
            "Боль при накусывании",
            "Спонтанная ночная боль",
            "Чувствительность к холодному",
            "Изменение цвета зуба"
        ],
        "correct_answer": 0,
        "explanation": "Болезненность при перкуссии и накусывании - классический симптом острого периодонтита из-за воспаления в периодонтальной связке.",
        "related_modules": [109, 110]
    }
]

# ===== PATIENT SAFETY (15 вопросов) =====
BIG_SAFETY_QUESTIONS = [
    {
        "category": "big_patient_safety",
        "difficulty": 4,
        "time_limit": 120,
        "question": "Какая концентрация адреналина в местном анестетике безопасна для пациентов с сердечно-сосудистыми заболеваниями?",
        "options": [
            "1:50,000",
            "1:80,000", 
            "1:100,000",
            "1:200,000"
        ],
        "correct_answer": 3,
        "explanation": "Для пациентов с ССЗ рекомендуется концентрация адреналина не выше 1:200,000 для минимизации системных эффектов.",
        "related_modules": [111, 112]
    },
    {
        "category": "big_patient_safety",
        "difficulty": 3,
        "time_limit": 90,
        "question": "Какой препарат является антагонистом варфарина?",
        "options": [
            "Протамин сульфат",
            "Витамин K",
            "Аминокапроновая кислота",
            "Транексамовая кислота"
        ],
        "correct_answer": 1,
        "explanation": "Витамин K является специфическим антагонистом варфарина, восстанавливая синтез витамин K-зависимых факторов свертывания.",
        "related_modules": [113, 114]
    }
]

# Объединяем все вопросы
ALL_DUTCH_QUESTIONS = DUTCH_DENTAL_QUESTIONS + BIG_MEDICAL_QUESTIONS + BIG_CLINICAL_QUESTIONS + BIG_SAFETY_QUESTIONS 