# translations.py - Обновленная система переводов для Become a Tandarts

translations = {
    'en': {
        # === Базовые переводы приложения (from older version, merged with new) ===
        'app_title': 'Become a Tandarts',
        'app_description': 'Professional platform for BIG exam preparation for dentists in the Netherlands',

        # === Navigation & Auth ===
        'home': 'Home',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Dashboard',
        'about_big': 'About BIG',
        'profile': 'Profile',
        'settings': 'Settings', # Retained from older, assuming this is intended
        'admin_panel': 'Admin Panel',
        'logout': 'Logout',
        'login': 'Login',
        'register': 'Register',

        # === Homepage Content (from newer version, more comprehensive) ===
        'seo_title': 'BIG Exam Preparation for Dentists in the Netherlands - Become a Tandarts',
        'seo_description': 'Online platform preparing dentists for the BIG registration exam (BI-toets) in the Netherlands. Study materials, practice tests, tips and community.',
        'big_exam_for_dentists': 'BIG exam for dentists',
        'successful_path_title': 'Your <span class="text-teal-600">successful path</span> to dental license',
        'complete_preparation': 'Complete online preparation for the BIG exam for foreign dentists in the Netherlands. Start learning today!',
        'start_for_free': 'Start for free',
        'learn_about_big': 'Learn about BIG exam',
        'students': 'Students',
        'success_rate': '% Success rate',
        'rating': 'Rating',
        'alt_big_exam_interface': 'BIG exam interface',
        'start_path_title': 'Start your path to <span class="text-gradient">BIG registration</span>',
        'professional_platform': 'Professional online platform preparing dentists for the BIG exam and licensure in the Netherlands',
        'structured_modules': 'Structured learning modules',
        'professional_dutch': 'Professional Dutch language',
        'practice_exams': 'Practice exams',
        'continue_learning': 'Continue Learning',
        'about_big_exam': 'About BIG Exam',
        'passed_exam': 'Passed the exam',
        'dental_professionals': 'Dental professionals illustration',
        'bi_tests': 'BI tests',
        'exam': 'Exam', # Already existed, retained
        'virtual_patient': 'Virtual Patient', # Added for consistency, already in learning map section
        'why_choose_us': 'WHY CHOOSE US',
        'our_approach': 'Our approach to <span class="text-accent">BIG exam</span> preparation',
        'comprehensive_system': 'We offer a comprehensive preparation system specifically designed for foreign-trained dentists',
        'structured_modules_desc': 'Carefully organized content based on official BIG registration requirements and real experience',
        'interactive_flashcards': 'Interactive Flashcards',
        'interactive_flashcards_desc': 'Effective method for memorizing key concepts using spaced repetition',
        'medical_dutch': 'Medical Dutch',
        'medical_dutch_desc': 'Specialized module on medical terminology and patient communication in Dutch',
        'realistic_tests': 'Realistic Tests',
        'realistic_tests_desc': 'Practice tests that simulate the actual format and difficulty of the BIG exam',
        'personal_analytics': 'Personal Analytics',
        'personal_analytics_desc': 'Track your progress and identify areas that need additional attention',
        'community_support': 'Community Support',
        'community_support_desc': 'Connect with other dentists on the same journey and access insights from successful candidates',
        'ready_to_start': 'Ready to start your BIG exam preparation?',
        'start_learning': 'Start Learning',
        'sign_up_now': 'Sign Up Now',

        # === Learning Map Page Content (from newer version, more comprehensive) ===
        'progress': 'Progress',
        'overall_progress': 'Overall Progress',
        'lessons_completed_of': '{completed} of {total} lessons completed',
        'activity': 'Activity',
        'days_short': 'days',
        'learning_time_minutes': 'Learning time: {minutes} min.',
        'total_time': 'Total Time',
        'total_time_short': 'total time',
        'exam_date_label': 'Date',
        'not_scheduled': 'not scheduled',
        # Phases
        'phase1_title': 'Phase 1: Fundamental Theory',
        'phase2_title': 'Phase 2: Preclinical Skills',
        'phase3_title': 'Phase 3: Clinical Reasoning',
        'phase4_title': 'Phase 4: Exam Strategy',
        # Phase 1 Cards
        'basic_medical_sciences': 'Basic Medical Sciences',
        'basic_medical_knowledge': 'Basic medical knowledge',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Cariology, Endo, Periodontology, Pediatric Dentistry',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Prosthetics, Ortho, Surgery, Kinesiology',
        'radiology': 'Radiology',
        'radiology_subtitle': 'Basics of radiology, image interpretation',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Preclinical Simodont Skills',
        'preclinical_simodont_subtitle': 'Caries preparation, endodontic access, crown preparation',
        'professional_cleaning_title': 'Professional Cleaning', # Gebitsreiniging
        'professional_cleaning_subtitle': 'Professional teeth cleaning, scaling',
        'module_in_development': 'This module is under development',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Interactive Clinical Cases',
        'virtual_patients_desc': 'Practice clinical reasoning and communication skills with interactive virtual patient scenarios.',
        'start_scenarios': 'Start Scenarios',
        'intake_interview_title': 'Intake Interview', # Intake Gesprek
        'intake_interview_subtitle': 'Initial consultation, communication skills',
        'treatment_planning': 'Treatment Planning',
        'treatment_planning_subtitle': 'Basics of treatment planning',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Advanced Treatment Planning',
        'advanced_treatment_planning_subtitle': 'Casus practice, clinical cases',
        'statistics_methodology': 'Statistics & Methodology',
        'statistics_methodology_subtitle': 'Preparation for Open Book',
        # Module/Button Items
        'premium': 'Premium', # Already existed
        'test': 'Test',
        'repeat': 'Repeat', # Already existed
        'repeat_test': 'Repeat Test',
        'continue_progress': 'Continue ({progress}%)',
        'start': 'Start', # Already existed
        'start_test': 'Start Test',
        'loading': 'Loading...',
        'redirecting': 'Redirecting...',

        # === General Learning Map Translations (from newer version) ===
        'subcategories': 'Subcategories',
        'subcategories_title': 'Subcategories',
        'topics_title': 'Topics',
        'lessons_title': 'Lessons',
        'min': 'min', # Already existed
        'days_active': 'Days Active',
        'countdown': 'Countdown', # Already existed
        'days_until_exam': 'days until exam', # Already existed
        'schedule_exam': 'Schedule Exam', # Already existed
        'recommended_for_you': 'Recommendations for you',
        'recommendations': 'Recommendations for you',
        'select_category': 'Select a category to start learning',
        'ready_to_start_learning': 'Ready to start learning?',
        'choose_subject_category': 'Choose a subject or category from the left menu to begin',
        'select_date': 'Choose date', # Already existed
        'cancel': 'Cancel', # Already existed
        'save': 'Save', # Already existed
        'clinical_cases': 'Clinical Cases', # Already existed
        'all_virtual_patients': 'All Virtual Patients',
        # Dashboard
        'learning_dashboard': 'Learning Dashboard',
        'your_progress': 'Your Progress',
        'activity_days': 'Activity Days',
        'exam_date': 'Exam Date',
        'exam_date_placeholder': 'July 15, 2025',
        'change_date': 'Change Date',
        'customize_learning_plan': 'Customize Learning Plan',
        'unlock_all_features': 'Unlock All Features',
        'upgrade_premium_description': 'Upgrade to premium plan for access to all modules',
        'subscribe_now': 'Subscribe Now',
        'recommended_module': 'Recommended Module',
        'continue_this_module': 'Continue this Module',
        'dental_anatomy': 'Dental Anatomy',
        'dental_anatomy_description': 'Basic structure and morphology of teeth',
        'sections': 'sections',
        'go_to_learning': 'Go to Learning',
        'your_modules': 'Your Modules',
        'all_modules': 'All Modules',
        'terminology': 'Terminology',
        'physiology': 'Physiology',
        'diagnostics': 'Diagnostics',
        'set_exam_date': 'Set Exam Date',
        'exam_date_saved': 'Exam date saved successfully', # Already existed
        'error_saving_date': 'Error saving exam date', # Already existed
        'server_error': 'Server error', # Already existed
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Welcome!',
        'welcome_title': 'Welcome to Become a Tandarts!',
        'welcome_subtitle': 'Your path to successful BIG exam preparation',
        'welcome_description': 'Our interactive platform will help you effectively prepare for the exam. Choose a section to start learning or explore recommended topics.',
        # Refined from older version for homepage content
        'select_category_message': 'Select a category to start learning',
        'select_subject_from_left_list': 'Select a subject from the left list',
        # Learning Paths (from older version)
        'knowledge_center': 'Knowledge Center',
        'communication': 'Communication',
        'preclinical_skills': 'Preclinical Skills',
        'workstation': 'Workstation',
        'bi_toets': 'BI-Toets',
        'virtual_patients': 'Virtual Patients',
        'dutch_for_dentists': 'Dutch for Dentists',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Theoretical foundations and key concepts',
        'communication_desc': 'Practice patient communication skills',
        'preclinical_desc': 'Basic dental procedures',
        'workstation_desc': 'Clinical practice and management',
        'bi_toets_desc': 'BI-test preparation and practice',
        # 'virtual_patients_desc': This key already exists in newer version and is more detailed. Retained newer.
        'dutch_desc': 'Professional Dutch language skills',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'lessons completed', # Lowercase for use in combined phrases
        'total_time_minutes': 'total time', # Conflict: using the new `learning_time_minutes` for specific use
        'min': 'min', # Already existed, retained
        'days_active_lower': 'active days', # Lowercase for use in combined phrases
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'Getting Started', # Already existed, retained
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Easy',
        'difficulty_medium': 'Medium',
        'difficulty_hard': 'Hard',
        'attempts_short': 'attempts',
        'continue_vp': 'Continue',
        'no_virtual_patients_for_subject': 'No virtual patients available for this subject yet',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'No modules available yet',
        'modules_coming_soon': 'Modules will be available soon',
        'no_subjects': 'No subjects',
        'subjects_coming_soon': 'Subjects will be available soon',
        'module_description': 'Module description',
        'subject_description': 'Subject description',
        'scenario_description': 'Scenario description',
        'subject_name': 'Subject name',
        'path_description': 'Learning path description',
        # Interface (from older version)
        'change_language': 'Change Language',
        'toggle_theme': 'Toggle Theme',
        'search': 'Search',
        'search_placeholder': 'Search courses, lessons, or topics...',
        'recent_searches': 'Recent Searches',
        'popular_topics': 'Popular Topics',
        'search_tips': 'Tips:',
        'to_navigate': 'to navigate',
        'to_select': 'to select',
        'to_close': 'to close',
        # Interactive Elements (from older version)
        'did_you_know': 'Did you know?',
        'click_to_learn': 'Click to learn an interesting dental fact',
        'fun_fact': 'Fun Fact',
        'tooth_fact': 'Tooth enamel is the hardest substance in the human body!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'An error occurred. Please refresh the page.',
        'ajax_error': 'An error occurred while loading data.',
        'exam_date_saved': 'Exam date saved successfully', # Already existed
        'error_saving_date': 'Error saving exam date', # Already existed
        'server_error': 'Server error', # Already existed

        # Additional keys from index.html that were not in translations.py
        'platform_description': 'Modern educational platform for BIG exam preparation in the Netherlands. High-quality education with an individual approach.',
        'learn_more': 'Learn More',
        'exam_preparation': 'Exam Preparation',
        'languages_supported': 'Languages Supported',
        'availability': 'Availability',
        'interactive_learning': 'Interactive Learning',
        'structured_learning': 'Structured Learning',
        'structured_learning_desc': 'Step-by-step exam preparation program',
        'clinical_cases_desc': 'Practice on realistic medical scenarios',
        'progress_tracking': 'Progress Tracking',
        'progress_tracking_desc': 'Detailed analytics of your learning',
        'theory_title': 'Theory',
        'theory_description': 'Structured modules on anatomy, physiology, and radiology',
        'anatomy': 'Anatomy',
        'physiology': 'Physiology',
        'radiology': 'Radiology',
        'most_popular': 'Most Popular',
        'practice_title': 'Practice',
        'practice_description': 'Clinical cases and patient interaction simulation',
        'case_studies': 'Case Studies',
        'communication': 'Communication',
        'exam_description': 'Preparation for real exams with results analysis',
        'mock_exams': 'Mock Exams',
        'analytics': 'Analytics',
        'strategy': 'Strategy',
        'start_your_journey': 'Start Your Journey',
        'platform_features': 'Platform Features',
        'comprehensive_approach': 'Comprehensive approach to dental preparation',
        'multilingual_support': 'Multilingual Support',
        'multilingual_description': 'Learning in 8 languages for students from different countries',
        'flexible_schedule': 'Flexible Schedule',
        'flexible_description': 'Learn at your convenience and pace',
        'quality_assurance': 'Quality Assurance',
        'quality_description': 'Content developed by dental experts',
        'support_247': '24/7 Support',
        'support_description': 'Round-the-clock user support',
        'learning_approach': 'Learning Approach',
        'our_methodology': 'Our Methodology',
        'evidence_based': 'Evidence-based learning system',
        'adaptive_testing': 'Adaptive Testing',
        'adaptive_testing_desc': 'Tests adapting to your knowledge level for optimal learning',
        'realistic_simulations': 'Realistic Simulations',
        'realistic_simulations_desc': 'Virtual patients and clinical scenarios as close to reality as possible',
        'detailed_analytics': 'Detailed Analytics',
        'detailed_analytics_desc': 'Detailed progress statistics with personalized recommendations',
        'community_learning': 'Community Learning',
        'community_learning_desc': 'Active community of students and experts for knowledge exchange',
        'join_thousands': 'Join thousands of students preparing for the BIG exam with our platform',
        'start_now': 'Start Now',
                # Hero секция
        'welcome_hero_title': 'Become a Tandarts',
        'welcome_hero_subtitle': 'Master dental skills. Pass BIG exam. Transform your career in Netherlands.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Start Free Trial',
        'explore_platform': 'Explore Platform',
        'exam_title': 'BIG Exam Preparation',

        # Особенности платформы
        'why_choose_us': 'Why Choose Dental Academy?',
        'platform_benefits': 'Everything you need to succeed in Dutch dental practice',
        'expert_content': 'Expert Content',
        'expert_content_desc': 'Curated by Dutch dental professionals for BIG exam success',
        'virtual_patients': 'Virtual Patients', 
        'virtual_patients_desc': 'Practice with realistic patient scenarios and case studies',
        'adaptive_learning': 'Adaptive Learning',
        'adaptive_learning_desc': 'AI-powered system adapts to your learning pace and style',
        'multilingual': '8 Languages',
        'multilingual_desc': 'Study in your native language, master Dutch terminology',
        
        # Статистика
        'platform_stats': 'Join Thousands of Successful Students',
        'active_students': 'Active Students',
        'success_rate': 'Success Rate %',
        'practice_questions': 'Practice Questions',
        'languages': 'Languages',
        
        # Отзывы
        'student_success': 'Student Success Stories',
        'testimonial_1': 'Dental Academy helped me pass BIG exam on first attempt. The virtual patients were incredibly realistic!',
        'testimonial_author_1': 'Anna Martinez',
        'dentist_amsterdam': 'Dentist, Amsterdam',
        
        # Финальный CTA
        'ready_to_start': 'Ready to Start Your Journey?',
        'join_thousands_desc': 'Join thousands of dental professionals who trust our platform for BIG exam preparation',
        'get_started_free': 'Get Started Free',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Tip: Add this app to your home screen for the best experience!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands', 
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'فارسی',
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Select Language',
        'toggle_theme': 'Toggle Theme',
        'theme_changed': 'Theme changed',
        'language_changed': 'Language changed successfully',
        'install_prompt': 'Install this app for the best experience!',
        'install_success': 'App installed successfully!',
        'network_error': 'Network error occurred',
        'try_again': 'Try again',
        'loading': 'Loading...',

        # === UI Elements ===
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'language': 'Language',
        'theme': 'Theme',
        'switch_theme': 'Switch Theme',
        'current_language': 'Current Language',
        
        # === Authentication ===
        'register': 'Register',
        'login': 'Login',
        'already_have_account_signin': 'Already have an account? Sign In',
        'create_account': 'Create Account',
        'enter_your_name': 'Enter your name',
        'enter_your_email': 'Enter your email',
        'next': 'Next',
        'back': 'Back',
        'create_strong_password': 'Create a strong password',
        'repeat_password': 'Repeat password',
        'submit': 'Submit',
        'continue': 'Continue',
        'start': 'Start',
        
        # === Navigation (already exists but adding for consistency) ===
        'home': 'Home',
        'learning': 'Learning', 
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        
        # === Additional UI ===
        'settings': 'Settings',
        'profile': 'Profile',
        'logout': 'Logout',
        'loading': 'Loading...',
        'error': 'Error',
        'success': 'Success',
        'cancel': 'Cancel',
        'save': 'Save',
        'patients_coming_soon': 'Patients Coming Soon',
    },

    'ru': {
        # === Базовые переводы приложения (merged) ===
        'app_title': 'Стань Стоматологом',
        'app_description': 'Профессиональная платформа для подготовки к BIG экзамену для стоматологов в Нидерландах',

        # === Навигация и авторизация ===
        'home': 'Главная',
        'learning': 'Обучение',
        'learning_map': 'Карта обучения',
        'tests': 'Тесты',
        'patients': 'Пациенты',
        'ai_assistant': 'AI Помощник',
        'dashboard': 'Дашборд',
        'about_big': 'О BIG',
        'profile': 'Профиль',
        'settings': 'Настройки',
        'admin_panel': 'Админ-панель',
        'logout': 'Выйти',
        'login': 'Войти',
        'register': 'Регистрация',

        # === Homepage Content ===
        'seo_title': 'Подготовка к BIG экзамену для стоматологов в Нидерландах - Become a Tandarts',
        'seo_description': 'Онлайн-платформа для подготовки стоматологов к BIG регистрации (экзамен BI-toets) в Нидерландах. Учебные материалы, тесты, советы и сообщество.',
        'big_exam_for_dentists': 'BIG-экзамен для стоматологов',
        'successful_path_title': 'Ваш <span class="text-teal-600">успешный путь</span> к стоматологической лицензии',
        'complete_preparation': 'Полная онлайн-подготовка к BIG-экзамену для иностранных стоматологов в Нидерландах. Начните обучение сегодня!',
        'start_for_free': 'Начать бесплатно',
        'learn_about_big': 'Узнать о BIG-экзамене',
        'students': 'Студентов',
        'success_rate': '% Успешность',
        'rating': 'Рейтинг',
        'alt_big_exam_interface': 'Интерфейс BIG экзамена',
        'start_path_title': 'Начните свой путь к <span class="text-gradient">BIG-регистрации</span>',
        'professional_platform': 'Профессиональная онлайн-платформа для подготовки стоматологов к экзаменам и процедуре получения лицензии в Нидерландах',
        'structured_modules': 'Структурированные учебные модули',
        'professional_dutch': 'Профессиональный голландский',
        'practice_exams': 'Практические тесты',
        'continue_learning': 'Продолжить обучение',
        'about_big_exam': 'О BIG-экзамене',
        'passed_exam': 'Сдали экзамен',
        'dental_professionals': 'Иллюстрация стоматологических специалистов',
        'bi_tests': 'BI тесты',
        'exam': 'Экзамен',
        'virtual_patient': 'Виртуальный пациент',
        'why_choose_us': 'ПОЧЕМУ МЫ',
        'our_approach': 'Наш подход к подготовке к <span class="text-accent">BIG-экзамену</span>',
        'comprehensive_system': 'Мы предлагаем комплексную систему подготовки, разработанную специально для иностранных стоматологов',
        'structured_modules_desc': 'Тщательно организованный контент, основанный на официальных требованиях BIG-регистрации и реальном опыте',
        'interactive_flashcards': 'Интерактивные флэш-карточки',
        'interactive_flashcards_desc': 'Эффективная методика запоминания ключевых концепций с помощью интервальных повторений',
        'medical_dutch': 'Медицинский голландский',
        'medical_dutch_desc': 'Специализированный модуль по медицинской терминологии и общению с пациентами на голландском языке',
        'realistic_tests': 'Реалистичные тесты',
        'realistic_tests_desc': 'Практические тесты, моделирующие реальный формат и сложность BIG-экзамена',
        'personal_analytics': 'Персональная аналитика',
        'personal_analytics_desc': 'Отслеживание вашего прогресса и выявление областей, требующих дополнительного внимания',
        'community_support': 'Поддержка сообщества',
        'community_support_desc': 'Общение с другими стоматологами, проходящими тот же путь, и доступ к опыту успешных кандидатов',
        'ready_to_start': 'Готовы начать подготовку к BIG-экзамену?',
        'start_learning': 'Начать обучение',
        'sign_up_now': 'Зарегистрироваться',

        # === Learning Map Page ===
        'progress': 'Прогресс',
        'overall_progress': 'Общий прогресс',
        'lessons_completed_of': '{completed} из {total} уроков завершено',
        'activity': 'Активность',
        'days_short': 'дней',
        'learning_time_minutes': 'Время обучения: {minutes} мин.',
        'total_time': 'Общее время',
        'total_time_short': 'всего времени',
        'exam_date_label': 'Дата',
        'not_scheduled': 'не назначена',
        # Phases
        'phase1_title': 'Фаза 1: Фундаментальная Теория',
        'phase2_title': 'Фаза 2: Преклинические Навыки',
        'phase3_title': 'Фаза 3: Клиническое Мышление',
        'phase4_title': 'Фаза 4: Экзаменационная Стратегия',
        # Phase 1 Cards
        'basic_medical_sciences': 'Базовые Медицинские Науки',
        'basic_medical_knowledge': 'Основные медицинские знания',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Кариесология, Эндо, Пародонтология, Детская стоматология',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Протезирование, Орто, Хирургия, Кинезиология',
        'radiology': 'Радиология',
        'radiology_subtitle': 'Основы рентгенологии, интерпретация снимков',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Преклинические Навыки Simodont',
        'preclinical_simodont_subtitle': 'Препарирование кариеса, эндодонтический доступ, препарирование под коронку',
        'professional_cleaning_title': 'Профессиональная Чистка',
        'professional_cleaning_subtitle': 'Профессиональная чистка зубов, скейлинг',
        'module_in_development': 'Этот модуль находится в разработке',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Интерактивные клинические случаи',
        'virtual_patients_desc': 'Тренируйте клиническое мышление и коммуникационные навыки на интерактивных сценариях с виртуальными пациентами.',
        'start_scenarios': 'Начать сценарии',
        'intake_interview_title': 'Первичный Прием',
        'intake_interview_subtitle': 'Первичный прием, коммуникационные навыки',
        'treatment_planning': 'Планирование Лечения',
        'treatment_planning_subtitle': 'Основы планирования лечения',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Продвинутое Планирование Лечения',
        'advanced_treatment_planning_subtitle': 'Практика Casus, клинические случаи',
        'statistics_methodology': 'Статистика и Методология',
        'statistics_methodology_subtitle': 'Подготовка к Open Book',
        # Module/Button Items
        'premium': 'Премиум',
        'test': 'Тест',
        'repeat': 'Повторить',
        'repeat_test': 'Пройти тест снова',
        'continue_progress': 'Продолжить ({progress}%)',
        'start': 'Начать',
        'start_test': 'Начать тест',
        'loading': 'Загрузка...',
        'redirecting': 'Переход...',

        # === General Learning Map Translations ===
        'subcategories': 'Подкатегории',
        'subcategories_title': 'Подкатегории',
        'topics_title': 'Темы',
        'lessons_title': 'Уроки',
        'min': 'мин',
        'days_active': 'Дней активности',
        'countdown': 'Обратный отсчет',
        'days_until_exam': 'дней до экзамена',
        'schedule_exam': 'Запланировать экзамен',
        'recommended_for_you': 'Рекомендации для вас',
        'recommendations': 'Рекомендации для вас',
        'select_category': 'Выберите категорию для начала обучения',
        'ready_to_start_learning': 'Готовы начать обучение?',
        'choose_subject_category': 'Выберите предмет или категорию из меню слева, чтобы начать',
        'select_date': 'Выберите дату',
        'cancel': 'Отмена',
        'save': 'Сохранить',
        'clinical_cases': 'Клинические случаи',
        'all_virtual_patients': 'Все виртуальные пациенты',
        # Dashboard
        'learning_dashboard': 'Панель обучения',
        'your_progress': 'Ваш прогресс',
        'activity_days': 'Дни активности',
        'exam_date': 'Дата экзамена',
        'exam_date_placeholder': '15 июля 2025',
        'change_date': 'Изменить дату',
        'customize_learning_plan': 'Настроить учебный план',
        'unlock_all_features': 'Разблокировать все функции',
        'upgrade_premium_description': 'Перейдите на премиум-план для доступа ко всем модулям',
        'subscribe_now': 'Подписаться сейчас',
        'recommended_module': 'Рекомендуемый модуль',
        'continue_this_module': 'Продолжить этот модуль',
        'dental_anatomy': 'Анатомия зубов',
        'dental_anatomy_description': 'Базовая структура и морфология зубов',
        'sections': 'разделы',
        'go_to_learning': 'Перейти к обучению',
        'your_modules': 'Ваши модули',
        'all_modules': 'Все модули',
        'terminology': 'Терминология',
        'physiology': 'Физиология',
        'diagnostics': 'Диагностика',
        'set_exam_date': 'Установить дату экзамена',
        'exam_date_saved': 'Дата экзамена успешно сохранена',
        'error_saving_date': 'Ошибка сохранения даты экзамена',
        'server_error': 'Ошибка сервера',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Добро пожаловать!',
        'welcome_title': 'Добро пожаловать в Become a Tandarts!',
        'welcome_subtitle': 'Ваш путь к успешной подготовке к BIG экзамену',
        'welcome_description': 'Наша интерактивная платформа поможет вам эффективно подготовиться к экзамену. Выберите раздел для начала обучения или ознакомьтесь с рекомендуемыми темами.',
        'select_subject_from_left_list': 'Выберите предмет из списка слева',
        # Learning Paths (from older version)
        'knowledge_center': 'Центр знаний',
        'communication': 'Коммуникация',
        'preclinical_skills': 'Доклинические навыки',
        'workstation': 'Рабочее место',
        'bi_toets': 'BI-Тест',
        'virtual_patients': 'Виртуальные пациенты',
        'dutch_for_dentists': 'Голландский для стоматологов',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Теоретические основы и ключевые концепции',
        'communication_desc': 'Отработка навыков общения с пациентами',
        'preclinical_desc': 'Базовые стоматологические процедуры',
        'workstation_desc': 'Клиническая практика и управление',
        'bi_toets_desc': 'Подготовка и практика BI-теста',
        'dutch_desc': 'Профессиональные навыки голландского языка',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'уроков завершено',
        'days_active_lower': 'дней активности',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'С чего начать?',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Легкий',
        'difficulty_medium': 'Средний',
        'difficulty_hard': 'Сложный',
        'attempts_short': 'попыток',
        'continue_vp': 'Продолжить',
        'no_virtual_patients_for_subject': 'Для этого предмета пока нет виртуальных пациентов',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'Модули пока недоступны',
        'modules_coming_soon': 'Модули появятся в ближайшее время',
        'no_subjects': 'Нет предметов',
        'subjects_coming_soon': 'Предметы скоро появятся',
        'module_description': 'Описание модуля',
        'subject_description': 'Описание предмета',
        'scenario_description': 'Описание сценария',
        'subject_name': 'Название предмета',
        'path_description': 'Описание пути обучения',
        # Interface (from older version)
        'change_language': 'Изменить язык',
        'toggle_theme': 'Переключить тему',
        'search': 'Поиск',
        'search_placeholder': 'Поиск курсов, уроков или тем...',
        'recent_searches': 'Недавние поиски',
        'popular_topics': 'Популярные темы',
        'search_tips': 'Подсказки:',
        'to_navigate': 'для навигации',
        'to_select': 'для выбора',
        'to_close': 'для закрытия',
        # Interactive Elements (from older version)
        'did_you_know': 'Знаете ли вы?',
        'click_to_learn': 'Нажмите, чтобы узнать интересный факт о стоматологии',
        'fun_fact': 'Интересный факт',
        'tooth_fact': 'Зубная эмаль — самая твёрдая ткань человеческого организма!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Произошла ошибка. Попробуйте обновить страницу.',
        'ajax_error': 'Произошла ошибка при загрузке данных.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'Современная образовательная платформа для подготовки к экзамену BIG в Нидерландах. Качественное обучение с индивидуальным подходом.',
        'learn_more': 'Узнать больше',
        'exam_preparation': 'Подготовка к экзамену',
        'languages_supported': 'Языков поддержки',
        'availability': 'Доступность',
        'interactive_learning': 'Интерактивное обучение',
        'structured_learning': 'Структурированное обучение',
        'structured_learning_desc': 'Пошаговая программа подготовки к экзамену',
        'clinical_cases_desc': 'Практика на реалистичных медицинских сценариях',
        'progress_tracking': 'Отслеживание прогресса',
        'progress_tracking_desc': 'Детальная аналитика вашего обучения',
        'theory_title': 'Теория',
        'theory_description': 'Структурированные модули по анатомии, физиологии и радиологии',
        'anatomy': 'Анатомия',
        'physiology': 'Физиология',
        'radiology': 'Радиология',
        'most_popular': 'Популярное',
        'practice_title': 'Практика',
        'practice_description': 'Клинические случаи и симуляция работы с пациентами',
        'case_studies': 'Клинические случаи',
        'communication': 'Коммуникация', # Already existed, confirm context
        'exam_description': 'Подготовка к реальным экзаменам с анализом результатов',
        'mock_exams': 'Пробные экзамены',
        'analytics': 'Аналитика',
        'strategy': 'Стратегия',
        'start_your_journey': 'Начать путешествие',
        'platform_features': 'Возможности платформы',
        'comprehensive_approach': 'Комплексный подход к подготовке стоматологов',
        'multilingual_support': 'Многоязычность',
        'multilingual_description': 'Обучение на 8 языках для удобства студентов из разных стран',
        'flexible_schedule': 'Гибкий график',
        'flexible_description': 'Учитесь в удобное время в своем темпе',
        'quality_assurance': 'Гарантия качества',
        'quality_description': 'Контент разработан экспертами в области стоматологии',
        'support_247': 'Поддержка 24/7',
        'support_description': 'Круглосуточная поддержка пользователей',
        'learning_approach': 'Подход к обучению',
        'our_methodology': 'Наша методология',
        'evidence_based': 'Основанная на доказательствах система обучения',
        'adaptive_testing': 'Адаптивное тестирование',
        'adaptive_testing_desc': 'Тесты, адаптирующиеся под ваш уровень знаний для оптимального обучения',
        'realistic_simulations': 'Реалистичные симуляции',
        'realistic_simulations_desc': 'Виртуальные пациенты и клинические сценарии, максимально приближенные к реальности',
        'detailed_analytics': 'Подробная аналитика',
        'detailed_analytics_desc': 'Детальная статистика прогресса с персональными рекомендациями',
        'community_learning': 'Обучение в сообществе',
        'community_learning_desc': 'Активное сообщество студентов и экспертов для обмена знаниями',
        'join_thousands': 'Присоединяйтесь к студентам, которые готовятся к BIG экзамену с нашей платформой',
        'start_now': 'Начать сейчас',
                # Hero секция
        'welcome_hero_title': 'Станьте Стоматологом',
        'welcome_hero_subtitle': 'Освойте стоматологические навыки. Сдайте экзамен BIG. Преобразите свою карьеру в Нидерландах.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Начать Бесплатно',
        'explore_platform': 'Изучить Платформу',
        
        # Особенности платформы
        'why_choose_us': 'Почему выбирают Dental Academy?',
        'platform_benefits': 'Всё необходимое для успеха в голландской стоматологической практике',
        'expert_content': 'Экспертный Контент',
        'expert_content_desc': 'Создан голландскими стоматологами для успешной сдачи экзамена BIG',
        'virtual_patients': 'Виртуальные Пациенты',
        'virtual_patients_desc': 'Практикуйтесь с реалистичными сценариями пациентов и клиническими случаями',
        'adaptive_learning': 'Адаптивное Обучение',
        'adaptive_learning_desc': 'ИИ-система адаптируется к вашему темпу и стилю обучения',
        'multilingual': '8 Языков',
        'multilingual_desc': 'Изучайте на родном языке, осваивайте голландскую терминологию',
        
        # Статистика
        'platform_stats': 'Присоединяйтесь к тысячам успешных студентов',
        'active_students': 'Активных Студентов',
        'success_rate': 'Success Rate %',
        'practice_questions': 'Practice Questions',
        'languages': 'Languages',
        
        # Отзывы
        'student_success': 'Student Success Stories',
        'testimonial_1': 'Dental Academy помогла мне сдать экзамен BIG с первой попытки. Виртуальные пациенты были невероятно реалистичными!',
        'testimonial_author_1': 'Anna Martinez',
        'dentist_amsterdam': 'Стоматолог, Амстердам',
        
        # Финальный CTA
        'ready_to_start': 'Готовы Начать Своё Путешествие?',
        'join_thousands_desc': 'Присоединяйтесь к тысячам стоматологов, которые доверяют нашей платформе подготовку к экзамену BIG',
        'get_started_free': 'Начать Бесплатно',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Совет: Добавьте это приложение на главный экран для лучшего опыта!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español', 
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'فارسی',
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Выбрать Язык',
        'toggle_theme': 'Переключить Тему',
        'theme_changed': 'Тема изменена',
        'language_changed': 'Язык успешно изменён',
        'install_prompt': 'Установите это приложение для лучшего опыта!',
        'install_success': 'Приложение успешно установлено!',
        'network_error': 'Произошла ошибка сети',
        'try_again': 'Попробовать снова',
        'loading': 'Загрузка...',

        # === UI Elements ===
        'dark_mode': 'Темная тема',
        'light_mode': 'Светлая тема',
        'language': 'Язык',
        'theme': 'Тема',
        'switch_theme': 'Переключить тему',
        'current_language': 'Текущий язык',
        
        # === Authentication ===
        'register': 'Регистрация',
        'login': 'Войти',
        'already_have_account_signin': 'Уже есть аккаунт? Войти',
        'create_account': 'Создать аккаунт',
        'enter_your_name': 'Введите ваше имя',
        'enter_your_email': 'Введите ваш email',
        'next': 'Далее',
        'back': 'Назад',
        'create_strong_password': 'Создайте надежный пароль',
        'repeat_password': 'Повторите пароль',
        'submit': 'Отправить',
        'continue': 'Продолжить',
        'start': 'Начать',
        
        # === Navigation (already exists but adding for consistency) ===
        'home': 'Home',
        'learning': 'Learning', 
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        
        # === Additional UI ===
        'settings': 'Настройки',
        'profile': 'Профиль',
        'logout': 'Выйти',
        'loading': 'Loading...',
        'error': 'Ошибка',
        'success': 'Успех',
        'cancel': 'Отмена',
        'save': 'Сохранить',
        'patients_coming_soon': 'Пациенты скоро появятся',
    },

    'nl': {
        # === Базовые переводы приложения (merged) ===
        'app_title': 'Word een Tandarts',
        'app_description': 'Professioneel platform voor BIG-examenvoorbereiding voor tandartsen in Nederland',

        # === Навигация и авторизация ===
        'home': 'Home',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Dashboard',
        'about_big': 'Over BIG',
        'profile': 'Profiel',
        'settings': 'Instellingen',
        'admin_panel': 'Adminpaneel',
        'logout': 'Uitloggen',
        'login': 'Inloggen',
        'register': 'Registreren',

        # === Homepage Content ===
        'seo_title': 'Voorbereiding BIG-examen voor Tandartsen in Nederland - Word Tandarts',
        'seo_description': 'Online platform dat tandartsen voorbereidt op het BIG-registratie examen (BI-toets) in Nederland. Studiemateriaal, oefentoetsen, tips en community.',
        'big_exam_for_dentists': 'BIG-examen voor tandartsen',
        'successful_path_title': 'Uw <span class="text-teal-600">succesvolle pad</span> naar de tandartslicentie',
        'complete_preparation': 'Complete online voorbereiding op het BIG-examen voor buitenlandse tandartsen in Nederland. Begin vandaag nog met leren!',
        'start_for_free': 'Start gratis',
        'learn_about_big': 'Leer over het BIG-examen',
        'students': 'Studenten',
        'success_rate': '% Succespercentage',
        'rating': 'Beoordeling',
        'alt_big_exam_interface': 'BIG-examen interface',
        'start_path_title': 'Start uw pad naar <span class="text-gradient">BIG-registratie</span>',
        'professional_platform': 'Professioneel online platform dat tandartsen voorbereidt op het BIG-examen en licentiëring in Nederland',
        'structured_modules': 'Gestructureerde leermodules',
        'professional_dutch': 'Professioneel Nederlands',
        'practice_exams': 'Oefenexamens',
        'continue_learning': 'Ga verder met leren',
        'about_big_exam': 'Over het BIG-examen',
        'passed_exam': 'Geslaagd voor het examen',
        'dental_professionals': 'Illustratie van tandheelkundige professionals',
        'bi_tests': 'BI-toetsen',
        'exam': 'Examen',
        'virtual_patient': 'Virtuele Patiënt',
        'why_choose_us': 'WAAROM VOOR ONS KIEZEN',
        'our_approach': 'Onze aanpak voor de voorbereiding op het <span class="text-accent">BIG-examen</span>',
        'comprehensive_system': 'Wij bieden een uitgebreid voorbereidingssysteem speciaal ontworpen voor in het buitenland opgeleide tandartsen',
        'structured_modules_desc': 'Zorgvuldig georganiseerde inhoud gebaseerd op officiële BIG-registratievereisten en praktijkervaring',
        'interactive_flashcards': 'Interactieve Flashcards',
        'interactive_flashcards_desc': 'Effectieve methode om sleutelconcepten te onthouden met behulp van gespreide herhaling',
        'medical_dutch': 'Medisch Nederlands',
        'medical_dutch_desc': 'Gespecialiseerde module over medische terminologie en patiëntcommunicatie in het Nederlands',
        'realistic_tests': 'Realistische Toetsen',
        'realistic_tests_desc': 'Oefentoetsen die het daadwerkelijke formaat en de moeilijkheidsgraad van het BIG-examen simuleren',
        'personal_analytics': 'Persoonlijke Analyse',
        'personal_analytics_desc': 'Volg uw voortgang en identificeer gebieden die extra aandacht nodig hebben',
        'community_support': 'Community Ondersteuning',
        'community_support_desc': 'Maak contact met andere tandartsen op dezelfde reis en krijg toegang tot inzichten van succesvolle kandidaten',
        'ready_to_start': 'Klaar om te beginnen met uw BIG-examenvoorbereiding?',
        'start_learning': 'Begin met Leren',
        'sign_up_now': 'Meld u nu aan',

        # === Learning Map Page ===
        'progress': 'Voortgang',
        'overall_progress': 'Algehele voortgang',
        'lessons_completed_of': '{completed} van de {total} lessen voltooid',
        'activity': 'Activiteit',
        'days_short': 'dagen',
        'learning_time_minutes': 'Studietijd: {minutes} min.',
        'total_time': 'Totale tijd',
        'total_time_short': 'totaal tijd',
        'learning_time': 'Leertijd', # NL specific
        'learning_time_hours': 'Studietijd: {hours} uur', # NL specific
        'learning_time_hours_minutes': 'Studietijd: {hours} uur {minutes} min.', # NL specific
        'learning_time_minutes_hours': 'Studietijd: {minutes} min. ({hours} uur)', # NL specific
        'exam_date_label': 'Datum',
        'not_scheduled': 'niet gepland',
        # Phases
        'phase1_title': 'Fase 1: Fundamentele Theorie',
        'phase2_title': 'Fase 2: Preklinische Vaardigheden',
        'phase3_title': 'Fase 3: Klinisch Redeneren',
        'phase4_title': 'Fase 4: Examenstrategie',
        # Phase 1 Cards
        'basic_medical_sciences': 'Basale Medische Wetenschappen',
        'basic_medical_knowledge': 'Basale medische kennis',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Cariologie, Endo, Parodontologie, Kindertandheelkunde',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Prothetiek, Ortho, Chirurgie, Kinesiologie',
        'radiology': 'Radiologie',
        'radiology_subtitle': 'Basis radiologie, beeldinterpretatie',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Preklinische Simodont Vaardigheden',
        'preclinical_simodont_subtitle': 'Cariëspreparatie, endodontische toegang, kroonpreparatie',
        'professional_cleaning_title': 'Gebitsreiniging',
        'professional_cleaning_subtitle': 'Professionele gebitsreiniging, scaling',
        'module_in_development': 'Deze module is in ontwikkeling',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Interactieve Klinische Casussen',
        'virtual_patients_desc': 'Oefen klinisch redeneren en communicatieve vaardigheden met interactieve virtuele patiëntscenario\'s.',
        'start_scenarios': 'Start Scenario\'s',
        'intake_interview_title': 'Intake Gesprek',
        'intake_interview_subtitle': 'Eerste consult, communicatieve vaardigheden',
        'treatment_planning': 'Behandelplanning',
        'treatment_planning_subtitle': 'Basis van behandelplanning',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Gevorderde Behandelplanning',
        'advanced_treatment_planning_subtitle': 'Casus oefenen, klinische casussen',
        'statistics_methodology': 'Statistiek & Methodologie',
        'statistics_methodology_subtitle': 'Voorbereiding op Open Boek',
        # Module/Button Items
        'premium': 'Premium',
        'test': 'Test',
        'repeat': 'Herhalen',
        'repeat_test': 'Test Herhalen',
        'continue_progress': 'Doorgaan ({progress}%)',
        'start': 'Start',
        'start_test': 'Start Test',
        'loading': 'Laden...',
        'redirecting': 'Doorsturen...',

        # === General Learning Map Translations ===
        'subcategories': 'Subcategorieën',
        'subcategories_title': 'Subcategorieën',
        'topics_title': 'Onderwerpen',
        'lessons_title': 'Lessen',
        'min': 'min',
        'days_active': 'Actieve Dagen',
        'countdown': 'Aftellen',
        'days_until_exam': 'dagen tot examen',
        'schedule_exam': 'Examen Plannen',
        'recommended_for_you': 'Aanbevelingen voor u',
        'recommendations': 'Aanbevelingen voor u',
        'select_category': 'Selecteer een categorie om te beginnen met leren',
        'ready_to_start_learning': 'Klaar om te beginnen met leren?',
        'choose_subject_category': 'Kies een onderwerp of categorie uit het linkermenu om te beginnen',
        'select_date': 'Kies datum',
        'cancel': 'Annuleren',
        'save': 'Opslaan',
        'clinical_cases': 'Klinische Gevallen',
        'all_virtual_patients': 'Alle Virtuele Patiënten',
        # Dashboard
        'learning_dashboard': 'Leerdashboard',
        'your_progress': 'Uw Voortgang',
        'activity_days': 'Activiteitsdagen',
        'exam_date': 'Examendatum',
        'exam_date_placeholder': '15 juli 2025',
        'change_date': 'Datum Wijzigen',
        'customize_learning_plan': 'Leerplan Aanpassen',
        'unlock_all_features': 'Ontgrendel Alle Functies',
        'upgrade_premium_description': 'Upgrade naar premium abonnement voor toegang tot alle modules',
        'subscribe_now': 'Nu Abonneren',
        'recommended_module': 'Recomenduerend Module',
        'continue_this_module': 'Ga Verder met deze Module',
        'dental_anatomy': 'Tandanatomie',
        'dental_anatomy_description': 'Basisstructuur en morfologie van tanden',
        'sections': 'secties',
        'go_to_learning': 'Ga naar Leren',
        'your_modules': 'Uw Modules',
        'all_modules': 'Alle Modules',
        'terminology': 'Terminologie',
        'physiology': 'Fysiologie',
        'diagnostics': 'Diagnostiek',
        'set_exam_date': 'Examendatum Instellen',
        'exam_date_saved': 'Examendatum succesvol opgeslagen',
        'error_saving_date': 'Fout bij het opslaan van de examendatum',
        'server_error': 'Serverfout',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Welkom!',
        'welcome_title': 'Welkom bij Word een Tandarts!',
        'welcome_subtitle': 'Jouw weg naar succesvolle BIG-examenvoorbereiding',
        'welcome_description': 'Ons interactieve platform helpt je effectief voor te bereiden op het examen. Kies een sectie om te beginnen met leren of verken aanbevolen onderwerpen.',
        'select_subject_from_left_list': 'Selecteer een vak uit de lijst links',
        # Learning Paths (from older version)
        'knowledge_center': 'Kenniscentrum',
        'communication': 'Communicatie',
        'preclinical_skills': 'Preklinische vaardigheden',
        'workstation': 'Werkstation',
        'bi_toets': 'BI-Toets',
        'virtual_patients': 'Virtuele patiënten',
        'dutch_for_dentists': 'Nederlands voor tandartsen',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Theoretische grondslagen en kernconcepten',
        'communication_desc': 'Oefen communicatievaardigheden met patiënten',
        'preclinical_desc': 'Basis tandheelkundige procedures',
        'workstation_desc': 'Klinische praktijk en management',
        'bi_toets_desc': 'BI-toetsvoorbereiding en oefening',
        'dutch_desc': 'Professionele Nederlandse taalvaardigheden',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'lessen voltooid',
        'days_active_lower': 'actieve dagen',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'Aan de slag',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Makkelijk',
        'difficulty_medium': 'Gemiddeld',
        'difficulty_hard': 'Moeilijk',
        'attempts_short': 'pogingen',
        'continue_vp': 'Doorgaan',
        'no_virtual_patients_for_subject': 'Nog geen virtuele patiënten beschikbaar voor dit vak',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'Nog geen modules beschikbaar',
        'modules_coming_soon': 'Modules komen binnenkort beschikbaar',
        'no_subjects': 'Geen vakken',
        'subjects_coming_soon': 'Vakken komen binnenkort beschikbaar',
        'module_description': 'Module beschrijving',
        'subject_description': 'Vak beschrijving',
        'scenario_description': 'Scenario beschrijving',
        'subject_name': 'Vaknaam',
        'path_description': 'Leerpad beschrijving',
        # Interface (from older version)
        'change_language': 'Taal wijzigen',
        'toggle_theme': 'Thema omschakelen',
        'search': 'Zoeken',
        'search_placeholder': 'Zoek cursussen, lessen of onderwerpen...',
        'recent_searches': 'Recente zoekopdrachten',
        'popular_topics': 'Populaire onderwerpen',
        'search_tips': 'Tips:',
        'to_navigate': 'om te navigeren',
        'to_select': 'om te selecteren',
        'to_close': 'om te sluiten',
        # Interactive Elements (from older version)
        'did_you_know': 'Wist je dat?',
        'click_to_learn': 'Klik om een interessant tandfeit te leren',
        'fun_fact': 'Leuk feitje',
        'tooth_fact': 'Tandglazuur is de hardste stof in het menselijk lichaam!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Er is een fout opgetreden. Ververs de pagina.',
        'ajax_error': 'Er is een fout opgetreden bij het laden van gegevens.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'Modern educatieplatform voor BIG-examenvoorbereiding in Nederland. Hoogwaardig onderwijs met een individuele aanpak.',
        'learn_more': 'Meer leren',
        'exam_preparation': 'Examenvoorbereiding',
        'languages_supported': 'Ondersteunde talen',
        'availability': 'Beschikbaarheid',
        'interactive_learning': 'Interactief leren',
        'structured_learning': 'Gestructureerd leren',
        'structured_learning_desc': 'Stapsgewijze examenvoorbereidingsprogramma',
        'clinical_cases_desc': 'Oefenen met realistische medische scenario\'s',
        'progress_tracking': 'Voortgang bijhouden',
        'progress_tracking_desc': 'Gedetailleerde analyse van je leerproces',
        'theory_title': 'Theorie',
        'theory_description': 'Gestructureerde modules over anatomie, fysiologie en radiologie',
        'anatomy': 'Anatomie',
        'physiology': 'Fysiologie',
        'radiology': 'Radiologie',
        'most_popular': 'Meest populair',
        'practice_title': 'Praktijk',
        'practice_description': 'Klinische gevallen en simulatie van patiëntinteractie',
        'case_studies': 'Casestudies',
        'communication': 'Communicatie', # Already existed, confirm context
        'exam_description': 'Voorbereiding op echte examens met resultatenanalyse',
        'mock_exams': 'Proefexamens',
        'analytics': 'Analyse',
        'strategy': 'Strategie',
        'start_your_journey': 'Begin je reis',
        'platform_features': 'Platformfuncties',
        'comprehensive_approach': 'Uitgebreide aanpak voor tandheelkundige voorbereiding',
        'multilingual_support': 'Meertalige ondersteuning',
        'multilingual_description': 'Leren in 8 talen voor studenten uit verschillende landen',
        'flexible_schedule': 'Flexibel schema',
        'flexible_description': 'Leer op je gemak en in je eigen tempo',
        'quality_assurance': 'Kwaliteitsborging',
        'quality_description': 'Inhoud ontwikkeld door tandheelkundige experts',
        'support_247': '24/7 Ondersteuning',
        'support_description': 'Dag en nacht gebruikersondersteuning',
        'learning_approach': 'Leerbenadering',
        'our_methodology': 'Onze methodologie',
        'evidence_based': 'Evidence-based leersysteem',
        'adaptive_testing': 'Adaptieve tests',
        'adaptive_testing_desc': 'Tests die zich aanpassen aan je kennisniveau voor optimaal leren',
        'realistic_simulations': 'Realistische simulaties',
        'realistic_simulations_desc': 'Virtuele patiënten en klinische scenario\'s zo dicht mogelijk bij de werkelijkheid',
        'detailed_analytics': 'Gedetailleerde analyse',
        'detailed_analytics_desc': 'Gedetailleerde voortgangsstatistieken met gepersonaliseerde aanbevelingen',
        'community_learning': 'Gemeenschappelijk leren',
        'community_learning_desc': 'Actieve gemeenschap van studenten en experts voor kennisuitwisseling',
        'join_thousands': 'Sluit je aan bij duizenden studenten die zich voorbereiden op het BIG-examen met ons platform',
        'start_now': 'Nu starten',
                # Hero секция
        'welcome_hero_title': 'Word een Tandarts',
        'welcome_hero_subtitle': 'Beheers tandheelkundige vaardigheden. Slaag voor het BIG-examen. Transformeer je carrière in Nederland.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Start Gratis Proefperiode',
        'explore_platform': 'Verken Platform',
        
        # Особенности платформы
        'why_choose_us': 'Waarom Kiezen voor Dental Academy?',
        'platform_benefits': 'Alles wat je nodig hebt om te slagen in de Nederlandse tandheelkundige praktijk',
        'expert_content': 'Expertinhoud',
        'expert_content_desc': 'Samengesteld door Nederlandse tandheelkundige professionals voor BIG-examensucces',
        'virtual_patients': 'Virtuele Patiënten',
        'virtual_patients_desc': 'Oefen met realistische patiëntscenario\'s en casestudies',
        'adaptive_learning': 'Adaptief Leren',
        'adaptive_learning_desc': 'AI-gestuurd systeem past zich aan jouw leertempo en -stijl aan',
        'multilingual': '8 Talen',
        'multilingual_desc': 'Studeer in je moedertaal, beheers Nederlandse terminologie',
        
        # Статистика
        'platform_stats': 'Sluit je aan bij duizenden succesvolle studenten',
        'active_students': 'Actieve Studenten',
        'success_rate': 'Slagingspercentage %',
        'practice_questions': 'Oefenvragen',
        'languages': 'Talen',
        
        # Отзывы
        'student_success': 'Succesverhalen van Studenten',
        'testimonial_1': 'Dental Academy hielp me het BIG-examen in één keer te halen. De virtuele patiënten waren ongelooflijk realistisch!',
        'testimonial_author_1': 'Anna Martinez',
        'dentist_amsterdam': 'Tandarts, Amsterdam',
        
        # Финальный CTA
        'ready_to_start': 'Klaar om je Reis te Beginnen?',
        'join_thousands_desc': 'Sluit je aan bij duizenden tandheelkundige professionals die ons platform vertrouwen voor BIG-examenvoorbereiding',
        'get_started_free': 'Start Gratis',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Tip: Voeg deze app toe aan je startscherm voor de beste ervaring!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська', 
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'فارسی',
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Selecteer Taal',
        'toggle_theme': 'Wissel Thema',
        'theme_changed': 'Thema gewijzigd',
        'language_changed': 'Taal succesvol gewijzigd',
        'install_prompt': 'Installeer deze app voor de beste ervaring!',
        'install_success': 'App succesvol geïnstalleerd!',
        'network_error': 'Netwerkfout opgetreden',
        'try_again': 'Probeer opnieuw',
        'loading': 'Laden...',
    },

    'es': {
        # === Navigation & Auth ===
        'home': 'Inicio',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Panel',
        'about_big': 'Acerca de BIG',
        'profile': 'Perfil',
        'settings': 'Configuración',
        'admin_panel': 'Panel de administración',
        'logout': 'Cerrar sesión',
        'login': 'Iniciar sesión',
        'register': 'Registrarse',
        # === Homepage Content ===
        'seo_title': 'Preparación para el examen BIG para dentistas en los Países Bajos - Become a Tandarts',
        'seo_description': 'Plataforma online para preparar a dentistas para el examen de registro BIG (BI-toets) en los Países Bajos. Materiales de estudio, exámenes de práctica, consejos y comunidad.',
        'big_exam_for_dentists': 'Examen BIG para dentistas',
        'successful_path_title': 'Su <span class="text-teal-600">camino exitoso</span> hacia la licencia dental',
        'complete_preparation': 'Preparación online completa para el examen BIG para dentistas extranjeros en los Países Bajos. ¡Comience a aprender hoy!',
        'start_for_free': 'Empezar gratis',
        'learn_about_big': 'Aprender sobre el examen BIG',
        'students': 'Estudiantes',
        'success_rate': '% Tasa de éxito',
        'rating': 'Valoración',
        'alt_big_exam_interface': 'Interfaz del examen BIG',
        'start_path_title': 'Comience su camino hacia el <span class="text-gradient">registro BIG</span>',
        'professional_platform': 'Plataforma online profesional que prepara a dentistas para el examen BIG y la licencia en los Países Bajos',
        'structured_modules': 'Módulos de aprendizaje estructurados',
        'professional_dutch': 'Idioma neerlandés profesional',
        'practice_exams': 'Exámenes de práctica',
        'continue_learning': 'Continuar aprendiendo',
        'about_big_exam': 'Sobre el examen BIG',
        'passed_exam': 'Aprobaron el examen',
        'dental_professionals': 'Ilustración de profesionales dentales',
        'bi_tests': 'Pruebas BI',
        'exam': 'Examen',
        'virtual_patient': 'Paciente virtual',
        'why_choose_us': 'POR QUÉ ELEGIRNOS',
        'our_approach': 'Nuestro enfoque para la preparación del <span class="text-accent">examen BIG</span>',
        'comprehensive_system': 'Ofrecemos un sistema de preparación integral diseñado específicamente para dentistas formados en el extranjero',
        'structured_modules_desc': 'Contenido cuidadosamente organizado basado en los requisitos oficiales de registro BIG y la experiencia real',
        'interactive_flashcards': 'Tarjetas didácticas interactivas',
        'interactive_flashcards_desc': 'Método eficaz para memorizar conceptos clave utilizando la repetición espaciada',
        'medical_dutch': 'Neerlandés médico',
        'medical_dutch_desc': 'Módulo especializado en terminología médica y comunicación con el paciente en neerlandés',
        'realistic_tests': 'Pruebas realistas',
        'realistic_tests_desc': 'Exámenes de práctica que simulan el formato y la dificultad reales del examen BIG',
        'personal_analytics': 'Análisis personal',
        'personal_analytics_desc': 'Siga su progreso e identifique las áreas que necesitan atención adicional',
        'community_support': 'Apoyo comunitario',
        'community_support_desc': 'Conéctese con otros dentistas en el mismo viaje y acceda a las ideas de candidatos exitosos',
        'ready_to_start': '¿Listo para comenzar su preparación para el examen BIG?',
        'start_learning': 'Comenzar a aprender',
        'sign_up_now': 'Registrarse ahora',

        # === Learning Map Page ===
        'progress': 'Progreso',
        'overall_progress': 'Progreso general',
        'lessons_completed_of': '{completed} de {total} lecciones completadas',
        'activity': 'Actividad',
        'days_short': 'días',
        'learning_time_minutes': 'Tiempo de estudio: {minutes} min.',
        'total_time': 'Tiempo total',
        'total_time_short': 'tiempo total',
        'exam_date_label': 'Fecha',
        'not_scheduled': 'no programada',
        # Phases
        'phase1_title': 'Fase 1: Teoría Fundamental',
        'phase2_title': 'Fase 2: Habilidades Preclínicas',
        'phase3_title': 'Fase 3: Razonamiento Clínico',
        'phase4_title': 'Fase 4: Estrategia de Examen',
        # Phase 1 Cards
        'basic_medical_sciences': 'Ciencias Médicas Básicas',
        'basic_medical_knowledge': 'Conocimientos médicos básicos',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Cariología, Endo, Periodoncia, Odontopediatría',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Prótesis, Orto, Cirugía, Kinesiología',
        'radiology': 'Radiología',
        'radiology_subtitle': 'Fundamentos de radiología, interpretación de imágenes',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Habilidades Preclínicas Simodont',
        'preclinical_simodont_subtitle': 'Preparación de caries, acceso endodóntico, preparación de corona',
        'professional_cleaning_title': 'Limpieza Profesional',
        'professional_cleaning_subtitle': 'Limpieza dental profesional, raspado',
        'module_in_development': 'Este módulo está en desarrollo',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Casos Clínicos Interactivos',
        'virtual_patients_desc': 'Practique el razonamiento clínico y las habilidades de comunicación con escenarios interactivos de pacientes virtuales.',
        'start_scenarios': 'Iniciar Escenarios',
        'intake_interview_title': 'Entrevista Inicial',
        'intake_interview_subtitle': 'Consulta inicial, habilidades de comunicación',
        'treatment_planning': 'Planificación de Tratamiento',
        'treatment_planning_subtitle': 'Fundamentos de la planificación del tratamiento',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Planificación Avanzada de Tratamiento',
        'advanced_treatment_planning_subtitle': 'Práctica Casus, casos clínicos',
        'statistics_methodology': 'Estadística y Metodología',
        'statistics_methodology_subtitle': 'Preparación para Open Book',
        # Module/Button Items
        'premium': 'Premium',
        'test': 'Test',
        'repeat': 'Repetir',
        'repeat_test': 'Repetir Test',
        'continue_progress': 'Continuar ({progress}%)',
        'start': 'Empezar',
        'start_test': 'Empezar Test',
        'loading': 'Cargando...',
        'redirecting': 'Redirigiendo...',

        # === General Learning Map Translations ===
        'subcategories': 'Subcategorías',
        'subcategories_title': 'Subcategorías',
        'topics_title': 'Temas',
        'lessons_title': 'Lecciones',
        'min': 'min',
        'days_active': 'Días activos',
        'countdown': 'Cuenta regresiva',
        'days_until_exam': 'días hasta el examen',
        'schedule_exam': 'Programar examen',
        'recommended_for_you': 'Recomendaciones para usted',
        'recommendations': 'Recomendaciones para usted',
        'select_category': 'Seleccione una categoría para empezar a aprender',
        'ready_to_start_learning': '¿Listo para empezar a aprender?',
        'choose_subject_category': 'Elija un tema o categoría del menú de la izquierda para comenzar',
        'select_date': 'Elegir fecha',
        'cancel': 'Cancelar',
        'save': 'Guardar',
        'clinical_cases': 'Casos Clínicos',
        'all_virtual_patients': 'Todos los pacientes virtuales',
        # Dashboard
        'learning_dashboard': 'Panel de aprendizaje',
        'your_progress': 'Su progreso',
        'activity_days': 'Días de actividad',
        'exam_date': 'Fecha del examen',
        'exam_date_placeholder': '15 de julio de 2025',
        'change_date': 'Cambiar fecha',
        'customize_learning_plan': 'Personalizar plan de aprendizaje',
        'unlock_all_features': 'Desbloquear todas las funciones',
        'upgrade_premium_description': 'Actualice al plan premium para acceder a todos los módulos',
        'subscribe_now': 'Suscribirse ahora',
        'recommended_module': 'Módulo recomendado',
        'continue_this_module': 'Continuar este módulo',
        'dental_anatomy': 'Anatomía dental',
        'dental_anatomy_description': 'Estructura básica y morfología de los dientes',
        'sections': 'secciones',
        'go_to_learning': 'Ir a aprender',
        'your_modules': 'Sus módulos',
        'all_modules': 'Todos los módulos',
        'terminology': 'Terminología',
        'physiology': 'Fisiología',
        'diagnostics': 'Diagnóstico',
        'set_exam_date': 'Establecer fecha de examen',
        'exam_date_saved': 'Fecha de examen guardada con éxito',
        'error_saving_date': 'Error al guardar la fecha del examen',
        'server_error': 'Error del servidor',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': '¡Bienvenido!',
        'welcome_title': '¡Bienvenido a Become a Tandarts!',
        'welcome_subtitle': 'Su camino hacia una preparación exitosa para el examen BIG',
        'welcome_description': 'Nuestra plataforma interactiva le ayudará a prepararse eficazmente para el examen. Elija una sección para comenzar a aprender o explore temas recomendados.',
        'select_subject_from_left_list': 'Seleccione un tema de la lista de la izquierda',
        # Learning Paths (from older version)
        'knowledge_center': 'Centro de conocimiento',
        'communication': 'Comunicación',
        'preclinical_skills': 'Habilidades preclínicas',
        'workstation': 'Estación de trabajo',
        'bi_toets': 'BI-Toets',
        'virtual_patients': 'Pacientes virtuales',
        'dutch_for_dentists': 'Holandés para dentistas',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Fundamentos teóricos y conceptos clave',
        'communication_desc': 'Practicar habilidades de comunicación con el paciente',
        'preclinical_desc': 'Procedimientos dentales básicos',
        'workstation_desc': 'Práctica clínica y gestión',
        'bi_toets_desc': 'Preparación y práctica de la prueba BI',
        'dutch_desc': 'Habilidades profesionales en el idioma holandés',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'lecciones completadas',
        'days_active_lower': 'días activos',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'Primeros pasos',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Fácil',
        'difficulty_medium': 'Medio',
        'difficulty_hard': 'Difícil',
        'attempts_short': 'intentos',
        'continue_vp': 'Continuar',
        'no_virtual_patients_for_subject': 'No hay pacientes virtuales disponibles para este tema todavía',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'No hay módulos disponibles todavía',
        'modules_coming_soon': 'Los módulos estarán disponibles pronto',
        'no_subjects': 'No hay temas',
        'subjects_coming_soon': 'Los temas estarán disponibles pronto',
        'module_description': 'Descripción del módulo',
        'subject_description': 'Descripción del tema',
        'scenario_description': 'Descripción del escenario',
        'subject_name': 'Nombre del tema',
        'path_description': 'Descripción de la ruta de aprendizaje',
        # Interface (from older version)
        'change_language': 'Cambiar idioma',
        'toggle_theme': 'Cambiar tema',
        'search': 'Buscar',
        'search_placeholder': 'Buscar cursos, lecciones o temas...',
        'recent_searches': 'Búsquedas recientes',
        'popular_topics': 'Temas populares',
        'search_tips': 'Consejos:',
        'to_navigate': 'para navegar',
        'to_select': 'para seleccionar',
        'to_close': 'para cerrar',
        # Interactive Elements (from older version)
        'did_you_know': '¿Sabías que?',
        'click_to_learn': 'Haz clic para aprender un dato dental interesante',
        'fun_fact': 'Dato curioso',
        'tooth_fact': '¡El esmalte dental es el tejido más duro del cuerpo humano!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Ocurrió un error. Por favor, actualice la página.',
        'ajax_error': 'Ocurrió un error al cargar los datos.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'Plataforma educativa moderna para la preparación del examen BIG en los Países Bajos. Educación de alta calidad con un enfoque individualizado.',
        'learn_more': 'Saber más',
        'exam_preparation': 'Preparación para el examen',
        'languages_supported': 'Idiomas compatibles',
        'availability': 'Disponibilidad',
        'interactive_learning': 'Aprendizaje interactivo',
        'structured_learning': 'Aprendizaje estructurado',
        'structured_learning_desc': 'Programa de preparación para el examen paso a paso',
        'clinical_cases_desc': 'Práctica en escenarios médicos realistas',
        'progress_tracking': 'Seguimiento del progreso',
        'progress_tracking_desc': 'Análisis detallado de tu aprendizaje',
        'theory_title': 'Teoría',
        'theory_description': 'Módulos estructurados sobre anatomía, fisiología y radiología',
        'anatomy': 'Anatomía',
        'physiology': 'Fisiología',
        'radiology': 'Radiología',
        'most_popular': 'Más popular',
        'practice_title': 'Práctica',
        'practice_description': 'Casos clínicos y simulación de interacción con pacientes',
        'case_studies': 'Estudios de caso',
        'communication': 'Comunicación', # Already existed, confirm context
        'exam_description': 'Preparación para exámenes reales con análisis de resultados',
        'mock_exams': 'Exámenes simulados',
        'analytics': 'Análisis',
        'strategy': 'Estrategia',
        'start_your_journey': 'Comienza tu viaje',
        'platform_features': 'Características de la plataforma',
        'comprehensive_approach': 'Enfoque integral para la preparación dental',
        'multilingual_support': 'Soporte multilingüe',
        'multilingual_description': 'Aprendizaje en 8 idiomas para estudiantes de diferentes países',
        'flexible_schedule': 'Horario flexible',
        'flexible_description': 'Aprende a tu conveniencia y ritmo',
        'quality_assurance': 'Garantía de calidad',
        'quality_description': 'Contenido desarrollado por expertos dentales',
        'support_247': 'Soporte 24/7',
        'support_description': 'Soporte al usuario las 24 horas',
        'learning_approach': 'Enfoque de aprendizaje',
        'our_methodology': 'Nuestra metodología',
        'evidence_based': 'Sistema de aprendizaje basado en evidencia',
        'adaptive_testing': 'Pruebas adaptativas',
        'adaptive_testing_desc': 'Pruebas que se adaptan a tu nivel de conocimiento para un aprendizaje óptimo',
        'realistic_simulations': 'Simulaciones realistas',
        'realistic_simulations_desc': 'Pacientes virtuales y escenarios clínicos lo más cercanos posible a la realidad',
        'detailed_analytics': 'Análisis detallado',
        'detailed_analytics_desc': 'Estadísticas de progreso detalladas con recomendaciones personalizadas',
        'community_learning': 'Aprendizaje comunitario',
        'community_learning_desc': 'Comunidad activa de estudiantes y expertos para el intercambio de conocimientos',
        'join_thousands': 'Únete a miles de estudiantes que se preparan para el examen BIG con nuestra plataforma',
        'start_now': 'Empezar ahora',
                # Hero секция
        'welcome_hero_title': 'Conviértete en Dentista',
        'welcome_hero_subtitle': 'Domina las habilidades dentales. Aprueba el examen BIG. Transforma tu carrera en los Países Bajos.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Comenzar Prueba Gratuita',
        'explore_platform': 'Explorar Plataforma',
        
        # Особенности платформы
        'why_choose_us': '¿Por qué elegir Dental Academy?',
        'platform_benefits': 'Todo lo que necesitas para tener éxito en la práctica dental holandesa',
        'expert_content': 'Contenido Experto',
        'expert_content_desc': 'Curado por profesionales dentales holandeses para el éxito en el examen BIG',
        'virtual_patients': 'Pacientes Virtuales',
        'virtual_patients_desc': 'Practica con escenarios realistas de pacientes y estudios de casos',
        'adaptive_learning': 'Aprendizaje Adaptativo',
        'adaptive_learning_desc': 'Sistema impulsado por IA que se adapta a tu ritmo y estilo de aprendizaje',
        'multilingual': '8 Idiomas',
        'multilingual_desc': 'Estudia en tu idioma nativo, domina la terminología holandesa',
        
        # Статистика
        'platform_stats': 'Únete a miles de estudiantes exitosos',
        'active_students': 'Estudiantes Activos',
        'success_rate': 'Tasa de Éxito %',
        'practice_questions': 'Preguntas de Práctica',
        'languages': 'Idiomas',
        
        # Отзывы
        'student_success': 'Historias de Éxito de Estudiantes',
        'testimonial_1': '¡Dental Academy me ayudó a aprobar el examen BIG en el primer intento. Los pacientes virtuales fueron increíblemente realistas!',
        'testimonial_author_1': 'Anna Martínez',
        'dentist_amsterdam': 'Dentista, Ámsterdam',
        
        # Финальный CTA
        'ready_to_start': '¿Listo para Comenzar tu Viaje?',
        'join_thousands_desc': 'Únete a miles de profesionales dentales que confían en nuestra plataforma para la preparación del examen BIG',
        'get_started_free': 'Comenzar Gratis',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Consejo: ¡Añade esta app a tu pantalla de inicio para la mejor experiencia!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'فارسی',
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Seleccionar Idioma',
        'toggle_theme': 'Cambiar Tema',
        'theme_changed': 'Tema cambiado',
        'language_changed': 'Idioma cambiado exitosamente',
        'install_prompt': '¡Instala esta app para la mejor experiencia!',
        'install_success': '¡App instalada exitosamente!',
        'network_error': 'Error de red ocurrido',
        'try_again': 'Intentar de nuevo',
        'loading': 'Cargando...',
    },

    'pt': {
        # === Navigation & Auth ===
        'home': 'Início',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Painel',
        'about_big': 'Sobre BIG',
        'profile': 'Perfil',
        'settings': 'Configurações',
        'admin_panel': 'Painel de administração',
        'logout': 'Sair',
        'login': 'Entrar',
        'register': 'Registrar',
        # === Homepage Content ===
        'seo_title': 'Preparação para o Exame BIG para Dentistas na Holanda - Become a Tandarts',
        'seo_description': 'Plataforma online que prepara dentistas para o exame de registo BIG (BI-toets) na Holanda. Materiais de estudo, testes práticos, dicas e comunidade.',
        'big_exam_for_dentists': 'Exame BIG para dentistas',
        'successful_path_title': 'Seu <span class="text-teal-600">caminho de sucesso</span> para a licença odontológica',
        'complete_preparation': 'Preparação online completa para o exame BIG para dentistas estrangeiros na Holanda. Comece a aprender hoje!',
        'start_for_free': 'Começar gratuitamente',
        'learn_about_big': 'Saber mais sobre o exame BIG',
        'students': 'Estudantes',
        'success_rate': '% Taxa de sucesso',
        'rating': 'Classificação',
        'alt_big_exam_interface': 'Interface do exame BIG',
        'start_path_title': 'Comece seu caminho para o <span class="text-gradient">registo BIG</span>',
        'professional_platform': 'Plataforma online profissional que prepara dentistas para o exame BIG e licenciamento na Holanda',
        'structured_modules': 'Módulos de aprendizagem estruturados',
        'professional_dutch': 'Língua holandesa profissional',
        'practice_exams': 'Exames práticos',
        'continue_learning': 'Continuar a aprender',
        'about_big_exam': 'Sobre o Exame BIG',
        'passed_exam': 'Passaram no exame',
        'dental_professionals': 'Ilustração de profissionais de odontologia',
        'bi_tests': 'Testes BI',
        'exam': 'Exame',
        'virtual_patient': 'Paciente Virtual',
        'why_choose_us': 'PORQUÊ ESCOLHER-NOS',
        'our_approach': 'Nossa abordagem para a preparação do <span class="text-accent">exame BIG</span>',
        'comprehensive_system': 'Oferecemos um sistema de preparação abrangente especificamente concebido para dentistas formados no estrangeiro',
        'structured_modules_desc': 'Conteúdo cuidadosamente organizado com base nos requisitos oficiais de registo BIG e experiência real',
        'interactive_flashcards': 'Flashcards Interativos',
        'interactive_flashcards_desc': 'Método eficaz para memorizar conceitos-chave usando repetição espaçada',
        'medical_dutch': 'Holandês Médico',
        'medical_dutch_desc': 'Módulo especializado em terminologia médica e comunicação com o paciente em holandês',
        'realistic_tests': 'Testes Realistas',
        'realistic_tests_desc': 'Testes práticos que simulam o formato e a dificuldade reais do exame BIG',
        'personal_analytics': 'Análise Pessoal',
        'personal_analytics_desc': 'Acompanhe seu progresso e identifique áreas que precisam de atenção adicional',
        'community_support': 'Apoio Comunitário',
        'community_support_desc': 'Conecte-se com outros dentistas na mesma jornada e acesse insights de candidatos bem-sucedidos',
        'ready_to_start': 'Pronto para começar sua preparação para o exame BIG?',
        'start_learning': 'Começar a Aprender',
        'sign_up_now': 'Inscreva-se Agora',

        # === Learning Map Page ===
        'progress': 'Progresso',
        'overall_progress': 'Progresso Geral',
        'lessons_completed_of': '{completed} de {total} lições concluídas',
        'activity': 'Atividade',
        'days_short': 'dias',
        'learning_time_minutes': 'Tempo de estudo: {minutes} min.',
        'total_time': 'Tempo total',
        'total_time_short': 'tempo total',
        'exam_date_label': 'Data',
        'not_scheduled': 'não agendada',
        # Phases
        'phase1_title': 'Fase 1: Teoria Fundamental',
        'phase2_title': 'Fase 2: Habilidades Pré-clínicas',
        'phase3_title': 'Fase 3: Raciocínio Clínico',
        'phase4_title': 'Fase 4: Estratégia de Exame',
        # Phase 1 Cards
        'basic_medical_sciences': 'Ciências Médicas Básicas',
        'basic_medical_knowledge': 'Conhecimento médico básico',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Cariologia, Endo, Periodontia, Odontopediatria',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Prótese, Orto, Cirurgia, Cinesiologia',
        'radiology': 'Radiologia',
        'radiology_subtitle': 'Fundamentos de radiologia, interpretação de imagens',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Habilidades Pré-clínicas Simodont',
        'preclinical_simodont_subtitle': 'Preparo de cárie, acesso endodôntico, preparo para coroa',
        'professional_cleaning_title': 'Limpeza Profissional',
        'professional_cleaning_subtitle': 'Limpeza dentária profissional, raspagem',
        'module_in_development': 'Este módulo está em desenvolvimento',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Casos Clínicos Interativos',
        'virtual_patients_desc': 'Pratique o raciocínio clínico e as habilidades de comunicação com cenários interativos de pacientes virtuais.',
        'start_scenarios': 'Iniciar Cenários',
        'intake_interview_title': 'Entrevista Inicial',
        'intake_interview_subtitle': 'Consulta inicial, habilidades de comunicação',
        'treatment_planning': 'Planejamento de Tratamento',
        'treatment_planning_subtitle': 'Fundamentos do planejamento de tratamento',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Planejamento Avançado de Tratamento',
        'advanced_treatment_planning_subtitle': 'Prática Casus, casos clínicos',
        'statistics_methodology': 'Estatística e Metodologia',
        'statistics_methodology_subtitle': 'Preparação para Open Book',
        # Module/Button Items
        'premium': 'Premium',
        'test': 'Teste',
        'repeat': 'Repetir',
        'repeat_test': 'Repetir Teste',
        'continue_progress': 'Continuar ({progress}%)',
        'start': 'Começar',
        'start_test': 'Começar Teste',
        'loading': 'Carregando...',
        'redirecting': 'Redirecionando...',

        # === General Learning Map Translations ===
        'subcategories': 'Subcategorias',
        'subcategories_title': 'Subcategorias',
        'topics_title': 'Tópicos',
        'lessons_title': 'Lições',
        'min': 'min',
        'days_active': 'Dias ativos',
        'countdown': 'Contagem regressiva',
        'days_until_exam': 'dias até o exame',
        'schedule_exam': 'Agendar exame',
        'recommended_for_you': 'Recomendações para você',
        'recommendations': 'Recomendações para você',
        'select_category': 'Selecione uma categoria para começar a aprender',
        'ready_to_start_learning': 'Pronto para começar a aprender?',
        'choose_subject_category': 'Escolha um assunto ou categoria no menu à esquerda para começar',
        'select_date': 'Escolher data',
        'cancel': 'Cancelar',
        'save': 'Salvar',
        'clinical_cases': 'Casos Clínicos',
        'all_virtual_patients': 'Todos os pacientes virtuais',
        # Dashboard
        'learning_dashboard': 'Painel de aprendizagem',
        'your_progress': 'Seu progresso',
        'activity_days': 'Dias de atividade',
        'exam_date': 'Data do exame',
        'exam_date_placeholder': '15 de julho de 2025',
        'change_date': 'Alterar data',
        'customize_learning_plan': 'Personalizar plano de aprendizagem',
        'unlock_all_features': 'Desbloquear todos os recursos',
        'upgrade_premium_description': 'Atualize para o plano premium para acesso a todos os módulos',
        'subscribe_now': 'Assinar agora',
        'recommended_module': 'Módulo recomendado',
        'continue_this_module': 'Continuar este módulo',
        'dental_anatomy': 'Anatomia dental',
        'dental_anatomy_description': 'Estrutura básica e morfologia dos dentes',
        'sections': 'seções',
        'go_to_learning': 'Ir para aprender',
        'your_modules': 'Seus módulos',
        'all_modules': 'Todos os módulos',
        'terminology': 'Terminologia',
        'physiology': 'Fisiologia',
        'diagnostics': 'Diagnóstico',
        'set_exam_date': 'Definir data do exame',
        'exam_date_saved': 'Data do exame salva com sucesso',
        'error_saving_date': 'Erro ao salvar a data do exame',
        'server_error': 'Erro do servidor',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Bem-vindo!',
        'welcome_title': 'Bem-vindo ao Become a Tandarts!',
        'welcome_subtitle': 'Seu caminho para uma preparação bem-sucedida para o exame BIG',
        'welcome_description': 'Nossa plataforma interativa o ajudará a se preparar eficazmente para o exame. Escolha uma seção para começar a aprender ou explore tópicos recomendados.',
        'select_subject_from_left_list': 'Selecione um tópico na lista à esquerda',
        # Learning Paths (from older version)
        'knowledge_center': 'Centro de conhecimento',
        'communication': 'Comunicação',
        'preclinical_skills': 'Habilidades pré-clínicas',
        'workstation': 'Estação de trabalho',
        'bi_toets': 'BI-Toets',
        'virtual_patients': 'Pacientes virtuais',
        'dutch_for_dentists': 'Holandês para dentistas',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Fundamentos teóricos e conceitos-chave',
        'communication_desc': 'Pratique habilidades de comunicação com o paciente',
        'preclinical_desc': 'Procedimentos odontológicos básicos',
        'workstation_desc': 'Prática clínica e gestão',
        'bi_toets_desc': 'Preparação e prática do teste BI',
        'dutch_desc': 'Habilidades profissionais na língua holandesa',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'lições concluídas',
        'days_active_lower': 'dias ativos',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'Começando',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Fácil',
        'difficulty_medium': 'Médio',
        'difficulty_hard': 'Difícil',
        'attempts_short': 'tentativas',
        'continue_vp': 'Continuar',
        'no_virtual_patients_for_subject': 'Nenhum paciente virtual disponível para este tópico ainda',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'Nenhum módulo disponível ainda',
        'modules_coming_soon': 'Os módulos estarão disponíveis em breve',
        'no_subjects': 'Nenhum tópico',
        'subjects_coming_soon': 'Os tópicos estarão disponíveis em breve',
        'module_description': 'Descrição do módulo',
        'subject_description': 'Descrição do tópico',
        'scenario_description': 'Descrição do cenário',
        'subject_name': 'Nome do tópico',
        'path_description': 'Descrição do caminho de aprendizagem',
        # Interface (from older version)
        'change_language': 'Mudar idioma',
        'toggle_theme': 'Alternar tema',
        'search': 'Pesquisar',
        'search_placeholder': 'Pesquisar cursos, lições ou tópicos...',
        'recent_searches': 'Pesquisas recentes',
        'popular_topics': 'Tópicos populares',
        'search_tips': 'Dicas:',
        'to_navigate': 'para navegar',
        'to_select': 'para selecionar',
        'to_close': 'para fechar',
        # Interactive Elements (from older version)
        'did_you_know': 'Você sabia?',
        'click_to_learn': 'Clique para aprender um fato interessante sobre odontologia',
        'fun_fact': 'Curiosidade',
        'tooth_fact': 'O esmalte dentário é a substância mais dura do corpo humano!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Ocorreu um erro. Por favor, actualize a página.',
        'ajax_error': 'Ocorreu um erro ao carregar os dados.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'Plataforma educacional moderna para a preparação do exame BIG na Holanda. Educação de alta qualidade com uma abordagem individualizada.',
        'learn_more': 'Saiba mais',
        'exam_preparation': 'Preparação para o exame',
        'languages_supported': 'Idiomas suportados',
        'availability': 'Disponibilidade',
        'interactive_learning': 'Aprendizagem interativa',
        'structured_learning': 'Aprendizagem estruturada',
        'structured_learning_desc': 'Programa de preparação para o exame passo a passo',
        'clinical_cases_desc': 'Prática em cenários médicos realistas',
        'progress_tracking': 'Acompanhamento do progresso',
        'progress_tracking_desc': 'Análise detalhada do seu aprendizado',
        'theory_title': 'Teoria',
        'theory_description': 'Módulos estruturados sobre anatomía, fisiología y radiología',
        'anatomy': 'Anatomia',
        'physiology': 'Fisiologia',
        'radiology': 'Radiologia',
        'most_popular': 'Mais popular',
        'practice_title': 'Prática',
        'practice_description': 'Casos clínicos e simulação de interação com pacientes',
        'case_studies': 'Estudos de caso',
        'communication': 'Comunicação', # Already existed, confirm context
        'exam_description': 'Preparação para exames reais com análise de resultados',
        'mock_exams': 'Exames simulados',
        'analytics': 'Análise',
        'strategy': 'Estratégia',
        'start_your_journey': 'Comece sua jornada',
        'platform_features': 'Recursos da plataforma',
        'comprehensive_approach': 'Abordagem abrangente para a preparação odontológica',
        'multilingual_support': 'Suporte multilíngue',
        'multilingual_description': 'Aprendizagem em 8 idiomas para estudantes de diferentes países',
        'flexible_schedule': 'Horário flexível',
        'flexible_description': 'Aprenda no seu ritmo e conveniência',
        'quality_assurance': 'Garantia de qualidade',
        'quality_description': 'Conteúdo desenvolvido por especialistas em odontologia',
        'support_247': 'Suporte 24/7',
        'support_description': 'Suporte ao usuário 24 horas por dia',
        'learning_approach': 'Abordagem de aprendizagem',
        'our_methodology': 'Nossa metodologia',
        'evidence_based': 'Sistema de aprendizagem baseado em evidências',
        'adaptive_testing': 'Testes adaptativos',
        'adaptive_testing_desc': 'Testes que se adaptam ao seu nível de conhecimento para um aprendizado otimizado',
        'realistic_simulations': 'Simulações realistas',
        'realistic_simulations_desc': 'Pacientes virtuais e cenários clínicos o mais próximo possível da realidade',
        'detailed_analytics': 'Análise detalhada',
        'detailed_analytics_desc': 'Estatísticas de progresso detalhadas com recomendações personalizadas',
        'community_learning': 'Aprendizagem comunitária',
        'community_learning_desc': 'Comunidade ativa de estudantes e especialistas para troca de conhecimentos',
        'join_thousands': 'Junte-se a milhares de estudantes que se preparam para o exame BIG com nossa plataforma',
        'start_now': 'Começar agora',
                # Hero секция
        'welcome_hero_title': 'Torne-se um Dentista',
        'welcome_hero_subtitle': 'Domine habilidades dentárias. Passe no exame BIG. Transforme sua carreira na Holanda.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Começar Teste Gratuito',
        'explore_platform': 'Explorar Plataforma',
        
        # Особенности платформы
        'why_choose_us': 'Por que escolher a Dental Academy?',
        'platform_benefits': 'Tudo que você precisa para ter sucesso na prática dentária holandesa',
        'expert_content': 'Conteúdo Especializado',
        'expert_content_desc': 'Curado por profissionais dentários holandeses para o sucesso no exame BIG',
        'virtual_patients': 'Pacientes Virtuais',
        'virtual_patients_desc': 'Pratique com cenários realistas de pacientes e estudos de caso',
        'adaptive_learning': 'Aprendizagem Adaptativa',
        'adaptive_learning_desc': 'Sistema alimentado por IA que se adapta ao seu ritmo e estilo de aprendizagem',
        'multilingual': '8 Idiomas',
        'multilingual_desc': 'Estude em seu idioma nativo, domine a terminologia holandesa',
        
        # Статистика
        'platform_stats': 'Junte-se a milhares de estudantes bem-sucedidos',
        'active_students': 'Estudantes Ativos',
        'success_rate': 'Taxa de Sucesso %',
        'practice_questions': 'Questões de Prática',
        'languages': 'Idiomas',
        
        # Отзывы
        'student_success': 'Histórias de Sucesso de Estudantes',
        'testimonial_1': 'A Dental Academy me ajudou a passar no exame BIG na primeira tentativa. Os pacientes virtuais foram incrivelmente realistas!',
        'testimonial_author_1': 'Anna Martinez',
        'dentist_amsterdam': 'Dentista, Amsterdam',
        
        # Финальный CTA
        'ready_to_start': 'Pronto para Começar sua Jornada?',
        'join_thousands_desc': 'Junte-se a milhares de profissionais dentários que confiam em nossa plataforma para preparação do exame BIG',
        'get_started_free': 'Começar Gratuitamente',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Dica: Adicione este app à sua tela inicial para a melhor experiência!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'فارسی',
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Selecionar Idioma',
        'toggle_theme': 'Alternar Tema',
        'theme_changed': 'Tema alterado',
        'language_changed': 'Idioma alterado com sucesso',
        'install_prompt': 'Instale este app para a melhor experiência!',
        'install_success': 'App instalado com sucesso!',
        'network_error': 'Erro de rede ocorreu',
        'try_again': 'Tentar novamente',
        'loading': 'Carregando...',
    },

    'uk': {
        # === Navigation & Auth ===
        'home': 'Головна',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Дашборд',
        'about_big': 'Про BIG',
        'profile': 'Профіль',
        'settings': 'Налаштування',
        'admin_panel': 'Адмін-панель',
        'logout': 'Вийти',
        'login': 'Увійти',
        'register': 'Реєстрація',
        # === Homepage Content ===
        'seo_title': 'Підготовка до BIG іспиту для стоматологів у Нідерландах - Become a Tandarts',
        'seo_description': 'Онлайн-платформа для підготовки стоматологів до BIG реєстрації (іспит BI-toets) у Нідерландах. Навчальні матеріали, тести, поради та спільнота.',
        'big_exam_for_dentists': 'BIG-іспит для стоматологів',
        'successful_path_title': 'Ваш <span class="text-teal-600">успішний шлях</span> до стоматологічної ліцензії',
        'complete_preparation': 'Повна онлайн-підготовка до BIG-іспиту для іноземних стоматологів у Нідерландах. Почніть навчання сьогодні!',
        'start_for_free': 'Почати безкоштовно',
        'learn_about_big': 'Дізнатися про BIG-іспит',
        'students': 'Студентів',
        'success_rate': '% Успішність',
        'rating': 'Рейтинг',
        'alt_big_exam_interface': 'Інтерфейс BIG іспиту',
        'start_path_title': 'Почніть свій шлях до <span class="text-gradient">BIG-реєстрації</span>',
        'professional_platform': 'Професійна онлайн-платформа для підготовки стоматологів до іспитів та процедури отримання ліцензії в Нідерландах',
        'structured_modules': 'Структуровані навчальні модулі',
        'professional_dutch': 'Професійна голландська',
        'practice_exams': 'Практичні тести',
        'continue_learning': 'Продовжити навчання',
        'about_big_exam': 'Про BIG-іспит',
        'passed_exam': 'Склали іспит',
        'dental_professionals': 'Ілюстрація стоматологічних фахівців',
        'bi_tests': 'BI тести',
        'exam': 'Іспит',
        'virtual_patient': 'Віртуальний пацієнт',
        'why_choose_us': 'ЧОМУ МИ',
        'our_approach': 'Наш підхід до підготовки до <span class="text-accent">BIG-іспиту</span>',
        'comprehensive_system': 'Ми пропонуємо комплексну систему підготовки, розроблену спеціально для іноземних стоматологів',
        'structured_modules_desc': 'Ретельно організований контент, заснований на офіційних вимогах BIG-реєстрації та реальному досвіді',
        'interactive_flashcards': 'Інтерактивні флеш-картки',
        'interactive_flashcards_desc': 'Ефективна методика запам\'ятовування ключових концепцій за допомогою інтервальних повторень',
        'medical_dutch': 'Медична голландська',
        'medical_dutch_desc': 'Спеціалізований модуль з медичної термінології та спілкування з пацієнтами голландською мовою',
        'realistic_tests': 'Реалістичні тести',
        'realistic_tests_desc': 'Практичні тести, що моделюють реальний формат та складність BIG-іспиту',
        'personal_analytics': 'Персональна аналітика',
        'personal_analytics_desc': 'Відстеження вашого прогресу та виявлення областей, що потребують додаткової уваги',
        'community_support': 'Підтримка спільноти',
        'community_support_desc': 'Спілкування з іншими стоматологами, які проходять той самий шлях, та доступ до досвіду успішних кандидатів',
        'ready_to_start': 'Готові розпочати підготовку до BIG-іспиту?',
        'start_learning': 'Почати навчання',
        'sign_up_now': 'Зареєструватися',

        # === Learning Map Page ===
        'progress': 'Прогрес',
        'overall_progress': 'Загальний прогрес',
        'lessons_completed_of': '{completed} з {total} уроків завершено',
        'activity': 'Активність',
        'days_short': 'днів',
        'learning_time_minutes': 'Час навчання: {minutes} хв.',
        'total_time': 'Загальний час',
        'total_time_short': 'загальний час',
        'exam_date_label': 'Дата',
        'not_scheduled': 'не призначено',
        # Phases
        'phase1_title': 'Фаза 1: Фундаментальна Теорія',
        'phase2_title': 'Фаза 2: Преклінічні Навички',
        'phase3_title': 'Фаза 3: Клінічне Мислення',
        'phase4_title': 'Фаза 4: Екзаменаційна Стратегія',
        # Phase 1 Cards
        'basic_medical_sciences': 'Базові Медичні Науки',
        'basic_medical_knowledge': 'Основні медичні знання',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Карієсологія, Ендо, Пародонтологія, Дитяча стоматологія',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Протезування, Орто, Хірургія, Кінезіологія',
        'radiology': 'Радіологія',
        'radiology_subtitle': 'Основи рентгенології, інтерпретація знімків',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Преклінічні Навички Simodont',
        'preclinical_simodont_subtitle': 'Препарування карієсу, ендодонтичний доступ, препарування під коронку',
        'professional_cleaning_title': 'Професійна Чистка',
        'professional_cleaning_subtitle': 'Професійна чистка зубов, скейлінг',
        'module_in_development': 'Цей модуль знаходиться в розробці',
        # Phase 3 Cards
        'interactive_clinical_cases': 'Інтерактивні клінічні випадки',
        'virtual_patients_desc': 'Тренуйте клінічне мислення та комунікаційні навички на інтерактивних сценаріях з віртуальними пацієнтами.',
        'start_scenarios': 'Почати сценарії',
        'intake_interview_title': 'Первинний Прийом',
        'intake_interview_subtitle': 'Первинний прийом, комунікаційні навички',
        'treatment_planning': 'Планування Лікування',
        'treatment_planning_subtitle': 'Основи планування лікування',
        # Phase 4 Cards
        'advanced_treatment_planning': 'Поглиблене Планування Лікування',
        'advanced_treatment_planning_subtitle': 'Практика Casus, клінічні випадки',
        'statistics_methodology': 'Статистика та Методологія',
        'statistics_methodology_subtitle': 'Підготовка до Open Book',
        # Module/Button Items
        'premium': 'Преміум',
        'test': 'Тест',
        'repeat': 'Повторити',
        'repeat_test': 'Пройти тест знову',
        'continue_progress': 'Продовжити ({progress}%)',
        'start': 'Почати',
        'start_test': 'Почати тест',
        'loading': 'Завантаження...',
        'redirecting': 'Перехід...',

        # === General Learning Map Translations ===
        'subcategories': 'Підкатегорії',
        'subcategories_title': 'Підкатегорії',
        'topics_title': 'Теми',
        'lessons_title': 'Уроки',
        'min': 'хв',
        'days_active': 'Дні активності',
        'countdown': 'Зворотний відлік',
        'days_until_exam': 'днів до іспиту',
        'schedule_exam': 'Запланувати іспит',
        'recommended_for_you': 'Рекомендовано для вас',
        'recommendations': 'Рекомендації для вас',
        'select_category': 'Оберіть категорію для початку навчання',
        'ready_to_start_learning': 'Готові розпочати навчання?',
        'choose_subject_category': 'Оберіть предмет або категорію з лівого меню, щоб почати',
        'select_date': 'Вибрати дату',
        'cancel': 'Скасувати',
        'save': 'Зберегти',
        'clinical_cases': 'Клінічні випадки',
        'all_virtual_patients': 'Всі віртуальні пацієнти',
        # Dashboard
        'learning_dashboard': 'Панель навчання',
        'your_progress': 'Ваш прогрес',
        'activity_days': 'Дні активності',
        'exam_date': 'Дата іспиту',
        'exam_date_placeholder': '15 липня 2025',
        'change_date': 'Змінити дату',
        'customize_learning_plan': 'Налаштувати план навчання',
        'unlock_all_features': 'Розблокувати всі функції',
        'upgrade_premium_description': 'Оновіть до преміум-плану для доступу до всіх модулів',
        'subscribe_now': 'Підписатись зараз',
        'recommended_module': 'Рекомендований модуль',
        'continue_this_module': 'Продовжити цей модуль',
        'dental_anatomy': 'Анатомія зубів',
        'dental_anatomy_description': 'Базова структура та морфологія зубів',
        'sections': 'розділи',
        'go_to_learning': 'Перейти до навчання',
        'your_modules': 'Ваші модулі',
        'all_modules': 'Всі модулі',
        'terminology': 'Термінологія',
        'physiology': 'Фізіологія',
        'diagnostics': 'Діагностика',
        'set_exam_date': 'Встановити дату іспиту',
        'exam_date_saved': 'Дату іспиту успішно збережено',
        'error_saving_date': 'Помилка збереження дати іспиту',
        'server_error': 'Помилка сервера',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Ласкаво просимо!',
        'welcome_title': 'Ласкаво просимо до Become a Tandarts!',
        'welcome_subtitle': 'Ваш шлях до успішної підготовки до BIG іспиту',
        'welcome_description': 'Наша інтерактивна платформа допоможе вам ефективно підготуватися до іспиту. Оберіть розділ для початку навчання або ознайомтеся з рекомендованими темами.',
        'select_subject_from_left_list': 'Оберіть предмет зі списку ліворуч',
        # Learning Paths (from older version)
        'knowledge_center': 'Центр знань',
        'communication': 'Комунікація',
        'preclinical_skills': 'Доклінічні навички',
        'workstation': 'Робоче місце',
        'bi_toets': 'BI-Тест',
        'virtual_patients': 'Віртуальні пацієнти',
        'dutch_for_dentists': 'Голландська для стоматологів',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Теоретичні основи та ключові концепції',
        'communication_desc': 'Відпрацювання навичок спілкування з пацієнтами',
        'preclinical_desc': 'Базові стоматологічні процедури',
        'workstation_desc': 'Клінічна практика та управління',
        'bi_toets_desc': 'Підготовка та практика BI-тесту',
        'dutch_desc': 'Професійні навички голландської мови',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'уроків завершено',
        'days_active_lower': 'днів активності',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'З чого почати?',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Легкий',
        'difficulty_medium': 'Середній',
        'difficulty_hard': 'Складний',
        'attempts_short': 'спроб',
        'continue_vp': 'Продовжити',
        'no_virtual_patients_for_subject': 'Для цього предмета поки немає віртуальних пацієнтів',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'Модулі поки недоступні',
        'modules_coming_soon': 'Модулі з\'являться найближчим часом',
        'no_subjects': 'Немає предметів',
        'subjects_coming_soon': 'Предмети скоро з\'являться',
        'module_description': 'Опис модуля',
        'subject_description': 'Опис предмета',
        'scenario_description': 'Опис сценарію',
        'subject_name': 'Назва предмета',
        'path_description': 'Опис шляху навчання',
        # Interface (from older version)
        'change_language': 'Змінити мову',
        'toggle_theme': 'Переключити тему',
        'search': 'Пошук',
        'search_placeholder': 'Пошук курсів, уроків або тем...',
        'recent_searches': 'Останні пошуки',
        'popular_topics': 'Популярні теми',
        'search_tips': 'Поради:',
        'to_navigate': 'для навігації',
        'to_select': 'для вибору',
        'to_close': 'для закриття',
        # Interactive Elements (from older version)
        'did_you_know': 'Чи знаєте ви?',
        'click_to_learn': 'Натисніть, щоб дізнатися цікавий факт про стоматологію',
        'fun_fact': 'Цікавий факт',
        'tooth_fact': 'Зубна емаль — найтвердіша тканина людського організму!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Виникла помилка. Спробуйте оновити сторінку.',
        'ajax_error': 'Виникла помилка під час завантаження даних.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'Сучасна освітня платформа для підготовки до іспиту BIG в Нідерландах. Якісне навчання з індивідуальним підходом.',
        'learn_more': 'Дізнатися більше',
        'exam_preparation': 'Підготовка до іспиту',
        'languages_supported': 'Підтримувані мови',
        'availability': 'Доступність',
        'interactive_learning': 'Інтерактивне навчання',
        'structured_learning': 'Структуроване навчання',
        'structured_learning_desc': 'Покрокова програма підготовки до іспиту',
        'clinical_cases_desc': 'Практика на реалістичних медичних сценаріях',
        'progress_tracking': 'Відстеження прогресу',
        'progress_tracking_desc': 'Детальна аналітика вашого навчання',
        'theory_title': 'Теорія',
        'theory_description': 'Структуровані модулі з анатомії, фізіології та радіології',
        'anatomy': 'Анатомія',
        'physiology': 'Фізіологія',
        'radiology': 'Радіологія',
        'most_popular': 'Найпопулярніше',
        'practice_title': 'Практика',
        'practice_description': 'Клінічні випадки та симуляція роботи з пацієнтами',
        'case_studies': 'Клінічні випадки',
        'communication': 'Комунікація', # Already existed, confirm context
        'exam_description': 'Підготовка до реальних іспитів з аналізом результатів',
        'mock_exams': 'Пробні іспити',
        'analytics': 'Аналітика',
        'strategy': 'Стратегія',
        'start_your_journey': 'Розпочати подорож',
        'platform_features': 'Можливості платформи',
        'comprehensive_approach': 'Комплексний підхід до підготовки стоматологів',
        'multilingual_support': 'Багатомовна підтримка',
        'multilingual_description': 'Навчання 8 мовами для студентів з різних країн',
        'flexible_schedule': 'Гнучкий графік',
        'flexible_description': 'Навчайтеся у зручний час у своєму темпі',
        'quality_assurance': 'Гарантія якості',
        'quality_description': 'Контент розроблений експертами в галузі стоматології',
        'support_247': 'Підтримка 24/7',
        'support_description': 'Цілодобова підтримка користувачів',
        'learning_approach': 'Підхід до навчання',
        'our_methodology': 'Наша методологія',
        'evidence_based': 'Система навчання, заснована на доказах',
        'adaptive_testing': 'Адаптивне тестування',
        'adaptive_testing_desc': 'Тести, що адаптуються до вашого рівня знань для оптимального навчання',
        'realistic_simulations': 'Реалістичні симуляції',
        'realistic_simulations_desc': 'Віртуальні пацієнти та клінічні сценарії, максимально наближені до реальності',
        'detailed_analytics': 'Детальна аналітика',
        'detailed_analytics_desc': 'Детальна статистика прогресу з персональними рекомендаціями',
        'community_learning': 'Навчання у спільноті',
        'community_learning_desc': 'Активна спільнота студентів та експертів для обміну знаннями',
        'join_thousands': 'Приєднуйтесь до тисяч студентів, які готуються до BIG іспиту з нашою платформою',
        'start_now': 'Почати зараз',
                # Hero секция
        'welcome_hero_title': 'Станьте Стоматологом',
        'welcome_hero_subtitle': 'Освойте стоматологічні навички. Здайте іспит BIG. Перетворіть свою кар\'єру в Нідерландах.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Почати Безкоштовно',
        'explore_platform': 'Вивчити Платформу',
        
        # Особенности платформы
        'why_choose_us': 'Чому обирають Dental Academy?',
        'platform_benefits': 'Все необхідне для успіху в голландській стоматологічній практиці',
        'expert_content': 'Експертний Контент',
        'expert_content_desc': 'Створений голландськими стоматологами для успішного складання іспиту BIG',
        'virtual_patients': 'Віртуальні Пацієнти',
        'virtual_patients_desc': 'Практикуйтеся з реалістичними сценаріями пацієнтів та клінічними випадками',
        'adaptive_learning': 'Адаптивне Навчання',
        'adaptive_learning_desc': 'ШІ-система адаптується до вашого темпу та стилю навчання',
        'multilingual': '8 Мов',
        'multilingual_desc': 'Вивчайте рідною мовою, освоюйте голландську термінологію',
        
        # Статистика
        'platform_stats': 'Приєднуйтесь до тисяч успішних студентів',
        'active_students': 'Активних Студентів',
        'success_rate': 'Відсоток Успіху %',
        'practice_questions': 'Практичних Питань',
        'languages': 'Мов',
        
        # Отзывы
        'student_success': 'Історії Успіху Студентів',
        'testimonial_1': 'Dental Academy допомогла мені здати іспит BIG з першої спроби. Віртуальні пацієнти були неймовірно реалістичними!',
        'testimonial_author_1': 'Анна Мартінес',
        'dentist_amsterdam': 'Стоматолог, Амстердам',
        
        # Финальный CTA
        'ready_to_start': 'Готові Розпочати Свою Подорож?',
        'join_thousands_desc': 'Приєднуйтесь до тисяч стоматологів, які довіряють нашій платформі підготовку до іспиту BIG',
        'get_started_free': 'Почати Безкоштовно',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 Порада: Додайте цей додаток на головний екран для кращого досвіду!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'Farsça', # Corrected to Farsça
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Dil Seç',
        'toggle_theme': 'Tema Değiştir',
        'theme_changed': 'Tema değiştirildi',
        'language_changed': 'Dil başarıyla değiştirildi',
        'install_prompt': 'En iyi deneyim için bu uygulamayı yükleyin!',
        'install_success': 'Uygulama başarıyla yüklendi!',
        'network_error': 'Ağ hatası oluştu',
        'try_again': 'Tekrar dene',
        'loading': 'Yükleniyor...',
    },

    'fa': {
        # === Navigation & Auth ===
        'home': 'خانه',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'داشبورد',
        'about_big': 'درباره BIG',
        'profile': 'پروفایل',
        'settings': 'تنظیمات',
        'admin_panel': 'پنل مدیریت',
        'logout': 'خروج',
        'login': 'ورود',
        'register': 'ثبت نام',
        # === Homepage Content ===
        'seo_title': 'آمادگی آزمون BIG برای دندانپزشکان در هلند - دندانپزشک شوید',
        'seo_description': 'پلتفرم آنلاین آمادگی دندانپزشکان برای آزمون ثبت نام BIG (BI-toets) در هلند. مواد مطالعه، آزمون های تمرینی، نکات و جامعه.',
        'big_exam_for_dentists': 'آزمون BIG برای دندانپزشکان',
        'successful_path_title': '<span class="text-teal-600">مسیر موفقیت آمیز</span> شما برای دریافت مجوز دندانپزشکی',
        'complete_preparation': 'آمادگی کامل آنلاین برای آزمون BIG برای دندانپزشکان خارجی در هلند. همین امروز یادگیری را شروع کنید!',
        'start_for_free': 'شروع رایگان',
        'learn_about_big': 'درباره آزمون BIG بیاموزید',
        'students': 'دانشجو',
        'success_rate': '٪ نرخ موفقیت',
        'rating': 'رتبه بندی',
        'alt_big_exam_interface': 'رابط کاربری آزمون BIG',
        'start_path_title': 'مسیر خود را به سمت <span class="text-gradient">ثبت نام BIG</span> شروع کنید',
        'professional_platform': 'پلتفرم آنلاین حرفه ای برای آمادگی دندانپزشکان برای آزمون BIG و کسب مجوز در هلند',
        'structured_modules': 'ماژول های یادگیری ساختاریافته',
        'professional_dutch': 'زبان هلندی حرفه ای',
        'practice_exams': 'آزمون های تمرینی',
        'continue_learning': 'ادامه یادگیری',
        'about_big_exam': 'درباره آزمون BIG',
        'passed_exam': 'قبول شدگان در آزمون',
        'dental_professionals': 'تصویر متخصصان دندانپزشکی',
        'bi_tests': 'تست های BI',
        'exam': 'آزمون',
        'virtual_patient': 'بیمار مجازی',
        'why_choose_us': 'چرا ما را انتخاب کنید',
        'our_approach': 'رویکرد ما برای آمادگی <span class="text-accent">آزمون BIG</span>',
        'comprehensive_system': 'ما یک سیستم آمادگی جامع ارائه می دهیم که به طور خاص برای دندانپزشکان آموزش دیده در خارج از کشور طراحی شده است',
        'structured_modules_desc': 'محتوای با دقت سازماندهی شده بر اساس الزامات رسمی ثبت نام BIG و تجربه واقعی',
        'interactive_flashcards': 'فلش کارت های تعاملی',
        'interactive_flashcards_desc': 'روش موثر برای به خاطر سپردن مفاهیم کلیدی با استفاده از تکرار فاصله دار',
        'medical_dutch': 'هلندی پزشکی',
        'medical_dutch_desc': 'ماژول تخصصی در مورد اصطلاحات پزشکی و ارتباط با بیمار به زبان هلندی',
        'realistic_tests': 'آزمون های واقع گرایانه',
        'realistic_tests_desc': 'آزمون های تمرینی که قالب و دشواری واقعی آزمون BIG را شبیه سازی می کنند',
        'personal_analytics': 'تجزیه و تحلیل شخصی',
        'personal_analytics_desc': 'پیشرفت خود را پیگیری کنید و زمینه هایی را که نیاز به توجه بیشتری دارند شناسایی کنید',
        'community_support': 'پشتیبانی جامعه',
        'community_support_desc': 'با سایر دندانپزشکان در همین مسیر ارتباط برقرار کنید و به بینش های نامزدهای موفق دسترسی پیدا کنید',
        'ready_to_start': 'برای شروع آمادگی آزمون BIG خود آماده اید؟',
        'start_learning': 'شروع یادگیری',
        'sign_up_now': 'اکنون ثبت نام کنید',

        # === Learning Map Page ===
        'progress': 'پیشرفت',
        'overall_progress': 'پیشرفت کلی',
        'lessons_completed_of': '{completed} از {total} درس تکمیل شده',
        'activity': 'فعالیت',
        'days_short': 'روز',
        'learning_time_minutes': 'زمان یادگیری: {minutes} دقیقه',
        'total_time': 'زمان کل',
        'total_time_short': 'زمان کل',
        'exam_date_label': 'تاریخ',
        'not_scheduled': 'برنامه ریزی نشده',
        # Phases
        'phase1_title': 'فاز ۱: تئوری بنیادی',
        'phase2_title': 'فاز ۲: مهارت های پیش بالینی',
        'phase3_title': 'فاز ۳: استدلال بالینی',
        'phase4_title': 'فاز ۴: استراتژی آزمون',
        # Phase 1 Cards
        'basic_medical_sciences': 'علوم پایه پزشکی',
        'basic_medical_knowledge': 'دانش پایه پزشکی',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'کاریولوژی، اندو، پریودنتولوژی، دندانپزشکی کودکان',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'پروتز، ارتودنسی، جراحی، کینزیولوژی',
        'radiology': 'رادیولوژی',
        'radiology_subtitle': 'مبانی رادیولوژی، تفسیر تصویر',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'مهارت های پیش بالینی Simodont',
        'preclinical_simodont_subtitle': 'آماده سازی پوسیدگی، دسترسی اندودنتیک، آماده سازی روکش',
        'professional_cleaning_title': 'تمیز کردن حرفه ای',
        'professional_cleaning_subtitle': 'تمیز کردن حرفه ای دندان ها، جرم گیری',
        'module_in_development': 'این ماژول در حال توسعه است',
        # Phase 3 Cards
        'interactive_clinical_cases': 'موارد بالینی تعاملی',
        'virtual_patients_desc': 'مهارت های استدلال بالینی و ارتباطی را با سناریوهای تعاملی بیمار مجازی تمرین کنید.',
        'start_scenarios': 'شروع سناریوها',
        'intake_interview_title': 'مصاحبه اولیه',
        'intake_interview_subtitle': 'مشاوره اولیه، مهارت های ارتباطی',
        'treatment_planning': 'برنامه ریزی درمان',
        'treatment_planning_subtitle': 'مبانی برنامه ریزی درمان',
        # Phase 4 Cards
        'advanced_treatment_planning': 'برنامه ریزی پیشرفته درمان',
        'advanced_treatment_planning_subtitle': 'تمرین Casus، موارد بالینی',
        'statistics_methodology': 'آمار و روش شناسی',
        'statistics_methodology_subtitle': 'آمادگی برای Open Book',
        # Module/Button Items
        'premium': 'پریمیوم',
        'test': 'تست',
        'repeat': 'تکرار',
        'repeat_test': 'تکرار تست',
        'continue_progress': 'ادامه ({progress}٪)',
        'start': 'شروع',
        'start_test': 'شروع تست',
        'loading': 'در حال بارگذاری...',
        'redirecting': 'در حال هدایت...',

        # === General Learning Map Translations ===
        'subcategories': 'زیرمجموعه ها',
        'subcategories_title': 'زیرمجموعه ها',
        'topics_title': 'موضوعات',
        'lessons_title': 'درس ها',
        'min': 'دقیقه',
        'days_active': 'روزهای فعال',
        'countdown': 'شمارش معکوس',
        'days_until_exam': 'روز تا آزمون',
        'schedule_exam': 'برنامه ریزی آزمون',
        'recommended_for_you': 'توصیه شده برای شما',
        'recommendations': 'توصیه ها برای شما',
        'select_category': 'دسته بندی را برای شروع یادگیری انتخاب کنید',
        'ready_to_start_learning': 'آماده شروع یادگیری هستید؟',
        'choose_subject_category': 'برای شروع، یک موضوع یا دسته را از منوی سمت چپ انتخاب کنید',
        'select_date': 'انتخاب تاریخ',
        'cancel': 'لغو',
        'save': 'ذخیره',
        'clinical_cases': 'موارد بالینی',
        'all_virtual_patients': 'همه بیماران مجازی',
        # Dashboard
        'learning_dashboard': 'داشبورد یادگیری',
        'your_progress': 'پیشرفت شما',
        'activity_days': 'روزهای فعالیت',
        'exam_date': 'تاریخ آزمون',
        'exam_date_placeholder': '۱۵ جولای ۲۰۲۵',
        'change_date': 'تغییر تاریخ',
        'customize_learning_plan': 'سفارشی سازی برنامه یادگیری',
        'unlock_all_features': 'باز کردن قفل همه ویژگی ها',
        'upgrade_premium_description': 'برای دسترسی به تمام ماژول ها به طرح پریمیوم ارتقا دهید',
        'subscribe_now': 'همین حالا عضو شوید',
        'recommended_module': 'ماژول توصیه شده',
        'continue_this_module': 'ادامه این ماژول',
        'dental_anatomy': 'آناتومی دندان',
        'dental_anatomy_description': 'ساختار و مورفولوژی پایه دندان ها',
        'sections': 'بخش ها',
        'go_to_learning': 'رفتن به یادگیری',
        'your_modules': 'ماژول های شما',
        'all_modules': 'همه ماژول ها',
        'terminology': 'اصطلاحات',
        'physiology': 'فیزیولوژی',
        'diagnostics': 'تشخیص',
        'set_exam_date': 'تنظیم تاریخ آزمون',
        'exam_date_saved': 'تاریخ آزمون با موفقیت ذخیره شد',
        'error_saving_date': 'خطا در ذخیره تاریخ آزمون',
        'server_error': 'خطای سرور',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'خوش آمدید!',
        'welcome_title': 'به دندانپزشک شوید خوش آمدید!',
        'welcome_subtitle': 'مسیر شما برای آمادگی موفق در آزمون BIG',
        'welcome_description': 'پلتفرم تعاملی ما به شما کمک می کند تا به طور موثر برای آزمون آماده شوید. بخشی را برای شروع یادگیری انتخاب کنید یا موضوعات توصیه شده را بررسی کنید.',
        'select_subject_from_left_list': 'یک موضوع از لیست سمت چپ انتخاب کنید',
        # Learning Paths (from older version)
        'knowledge_center': 'مرکز دانش',
        'communication': 'ارتباطات',
        'preclinical_skills': 'مهارت های پیش بالینی',
        'workstation': 'ایستگاه کاری',
        'bi_toets': 'تست BI',
        'virtual_patients': 'بیماران مجازی',
        'dutch_for_dentists': 'هلندی برای دندانپزشکان',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'مبانی نظری و مفاهیم کلیدی',
        'communication_desc': 'تمرین مهارت های ارتباط با بیمار',
        'preclinical_desc': 'روش های پایه دندانپزشکی',
        'workstation_desc': 'تمرین و مدیریت بالینی',
        'bi_toets_desc': 'آمادگی و تمرین تست BI',
        'dutch_desc': 'مهارت های زبان هلندی حرفه ای',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'درس تکمیل شده',
        'days_active_lower': 'روزهای فعال',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'شروع به کار',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'آسان',
        'difficulty_medium': 'متوسط',
        'difficulty_hard': 'سخت',
        'attempts_short': 'تلاش',
        'continue_vp': 'ادامه',
        'no_virtual_patients_for_subject': 'هنوز هیچ بیمار مجازی برای این موضوع در دسترس نیست',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'هنوز ماژولی در دسترس نیست',
        'modules_coming_soon': 'ماژول ها به زودی در دسترس خواهند بود',
        'no_subjects': 'هیچ موضوعی وجود ندارد',
        'subjects_coming_soon': 'موضوعات به زودی در دسترس خواهند بود',
        'module_description': 'توضیحات ماژول',
        'subject_description': 'توضیحات موضوع',
        'scenario_description': 'توضیحات سناریو',
        'subject_name': 'نام موضوع',
        'path_description': 'توضیحات مسیر یادگیری',
        # Interface (from older version)
        'change_language': 'تغییر زبان',
        'toggle_theme': 'تغییر پوسته',
        'search': 'جستجو',
        'search_placeholder': 'جستجوی دوره ها، درس ها یا موضوعات...',
        'recent_searches': 'جستجوهای اخیر',
        'popular_topics': 'موضوعات محبوب',
        'search_tips': 'نکات:',
        'to_navigate': 'برای پیمایش',
        'to_select': 'برای انتخاب',
        'to_close': 'برای بستن',
        # Interactive Elements (from older version)
        'did_you_know': 'آیا می دانستید؟',
        'click_to_learn': 'برای یادگیری یک واقعیت جالب دندانپزشکی کلیک کنید',
        'fun_fact': 'واقعیت جالب',
        'tooth_fact': 'مینای دندان سخت ترین ماده در بدن انسان است!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'خطایی رخ داد. لطفاً صفحه را تازه کنید.',
        'ajax_error': 'خطایی هنگام بارگذاری داده ها رخ داد.',

        # Additional keys from index.html that were not in translations.py (translated)
        'platform_description': 'پلتفرم آموزشی مدرن برای آمادگی آزمون BIG در هلند. آموزش با کیفیت بالا با رویکردی فردی.',
        'learn_more': 'بیشتر بدانید',
        'exam_preparation': 'آمادگی آزمون',
        'languages_supported': 'زبان های پشتیبانی شده',
        'availability': 'در دسترس بودن',
        'interactive_learning': 'یادگیری تعاملی',
        'structured_learning': 'یادگیری ساختاریافته',
        'structured_learning_desc': 'برنامه آمادگی آزمون گام به گام',
        'clinical_cases_desc': 'تمرین بر روی سناریوهای پزشکی واقعی',
        'progress_tracking': 'پیگیری پیشرفت',
        'progress_tracking_desc': 'تجزیه و تحلیل دقیق یادگیری شما',
        'theory_title': 'تئوری',
        'theory_description': 'ماژول های ساختاریافته در آناتومی، فیزیولوژی و رادیولوژی',
        'anatomy': 'آناتومی',
        'physiology': 'فیزیولوژی',
        'radiology': 'رادیولوژی',
        'most_popular': 'محبوب ترین',
        'practice_title': 'تمرین',
        'practice_description': 'موارد بالینی و شبیه سازی تعامل با بیمار',
        'case_studies': 'مطالعات موردی',
        'communication': 'ارتباطات', # Already existed, confirm context
        'exam_description': 'آمادگی برای آزمون های واقعی با تجزیه و تحلیل نتایج',
        'mock_exams': 'آزمون های آزمایشی',
        'analytics': 'تحلیل',
        'strategy': 'استراتژی',
        'start_your_journey': 'سفر خود را آغاز کنید',
        'platform_features': 'ویژگی های پلتفرم',
        'comprehensive_approach': 'رویکرد جامع برای آمادگی دندانپزشکی',
        'multilingual_support': 'پشتیبانی چند زبانه',
        'multilingual_description': 'یادگیری به 8 زبان برای دانش آموزان از کشورهای مختلف',
        'flexible_schedule': 'برنامه انعطاف پذیر',
        'flexible_description': 'در زمان و سرعت دلخواه خود یاد بگیرید',
        'quality_assurance': 'تضمین کیفیت',
        'quality_description': 'محتوای توسعه یافته توسط کارشناسان دندانپزشکی',
        'support_247': 'پشتیبانی 24/7',
        'support_description': 'پشتیبانی 24 ساعته از کاربران',
        'learning_approach': 'رویکرد یادگیری',
        'our_methodology': 'روش شناسی ما',
        'evidence_based': 'سیستم یادگیری مبتنی بر شواهد',
        'adaptive_testing': 'تست تطبیقی',
        'adaptive_testing_desc': 'تست هایی که با سطح دانش شما برای یادگیری بهینه سازگار می شوند',
        'realistic_simulations': 'شبیه سازی های واقع گرایانه',
        'realistic_simulations_desc': 'بیماران مجازی و سناریوهای بالینی تا حد امکان نزدیک به واقعیت',
        'detailed_analytics': 'تجزیه و تحلیل دقیق',
        'detailed_analytics_desc': 'آمار پیشرفت دقیق با توصیه های شخصی',
        'community_learning': 'یادگیری اجتماعی',
        'community_learning_desc': 'جامعه فعال از دانشجویان و کارشناسان برای تبادل دانش',
        'join_thousands': 'به هزاران دانشجویی که با پلتفرم ما برای آزمون BIG آماده می شوند بپیوندید',
        'start_now': 'اکنون شروع کنید',
                # Hero секция
        'welcome_hero_title': 'دندانپزشک شوید',
        'welcome_hero_subtitle': 'مهارت‌های دندانپزشکی را فرا بگیرید. آزمون BIG را قبول شوید. شغل خود را در هلند متحول کنید.',
        'dental_academy': 'آکادمی دندانپزشکی',
        'start_free_trial': 'شروع آزمایش رایگان',
        'explore_platform': 'کاوش پلتفرم',
        
        # Особенности платформы
        'why_choose_us': 'چرا آکادمی دندانپزشکی را انتخاب کنیم؟',
        'platform_benefits': 'همه آنچه برای موفقیت در طب دندان هلندی نیاز دارید',
        'expert_content': 'محتوای متخصصین',
        'expert_content_desc': 'توسط متخصصان دندانپزشکی هلندی برای موفقیت در آزمون BIG تهیه شده',
        'virtual_patients': 'بیماران مجازی',
        'virtual_patients_desc': 'با سناریوهای واقعی بیماران و مطالعات موردی تمرین کنید',
        'adaptive_learning': 'یادگیری تطبیقی',
        'adaptive_learning_desc': 'سیستم هوش مصنوعی با سرعت و سبک یادگیری شما سازگار می‌شود',
        'multilingual': '۸ زبان',
        'multilingual_desc': 'به زبان مادری خود مطالعه کنید، اصطلاحات هلندی را فرا بگیرید',
        
        # Статистика
        'platform_stats': 'به هزاران دانشجوی موفق بپیوندید',
        'active_students': 'دانشجویان فعال',
        'success_rate': 'نرخ موفقیت %',
        'practice_questions': 'سؤالات تمرینی',
        'languages': 'زبان‌ها',
        
        # Отзывы
        'student_success': 'داستان‌های موفقیت دانشجویان',
        'testimonial_1': 'آکادمی دندانپزشکی به من کمک کرد تا آزمون BIG را در اولین تلاش قبول شوم. بیماران مجازی به طرز باورنکردنی واقعی بودند!',
        'testimonial_author_1': 'آنا مارتینز',
        'dentist_amsterdam': 'دندانپزشک، آمستردام',
        
        # Финальный CTA
        'ready_to_start': 'آماده شروع سفر خود هستید؟',
        'join_thousands_desc': 'به هزاران متخصص دندانپزشکی بپیوندید که برای آمادگی آزمون BIG به پلتفرم ما اعتماد دارند',
        'get_started_free': 'شروع رایگان',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 نکته: برای بهترین تجربه این اپ را به صفحه اصلی خود اضافه کنید!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'Farsça', # Corrected to Farsça
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Dil Seç',
        'toggle_theme': 'Tema Değiştir',
        'theme_changed': 'Tema değiştirildi',
        'language_changed': 'Dil başarıyla değiştirildi',
        'install_prompt': 'En iyi deneyim için bu uygulamayı yükleyin!',
        'install_success': 'Uygulama başarıyla yüklendi!',
        'network_error': 'Ağ hatası oluştu',
        'try_again': 'Tekrar dene',
        'loading': 'Yükleniyor...',
    },

'tr': {
        # === Navigation & Auth ===
        'home': 'Ana Sayfa',
        'learning': 'Learning',
        'learning_map': 'Learning Map',
        'tests': 'Tests',
        'patients': 'Patients',
        'ai_assistant': 'AI Assistant',
        'dashboard': 'Panel',
        'about_big': 'BIG Hakkında',
        'profile': 'Profil',
        'settings': 'Ayarlar',
        'admin_panel': 'Yönetici Paneli',
        'logout': 'Çıkış',
        'login': 'Giriş',
        'register': 'Kaydol',
        # === Homepage Content ===
        'seo_title': "Hollanda'daki Diş Hekimleri İçin BIG Sınavı Hazırlığı - Tandarts Olun", # Add 'seo_title' key
        'seo_description': "Hollanda'daki diş hekimlerini BIG kayıt sınavına (BI-toets) hazırlayan çevrimiçi platform. Çalışma materyalleri, deneme sınavları, ipuçları ve topluluk.", # Add 'seo_description' key
        'big_exam_for_dentists': 'Diş hekimleri için BIG sınavı',
        'successful_path_title': 'Diş hekimliği lisansına giden <span class="text-teal-600">başarılı yolunuz</span>',
        'complete_preparation': "Hollanda'daki yabancı diş hekimleri için BIG sınavına yönelik eksiksiz çevrimiçi hazırlık. Bugün öğrenmeye başlayın!", # Add 'complete_preparation' key
        'start_for_free': 'Ücretsiz başla',
        'learn_about_big': 'BIG sınavı hakkında bilgi edinin',
        'students': 'Öğrenci',
        'success_rate': '% Başarı oranı',
        'rating': 'Değerlendirme',
        'alt_big_exam_interface': 'BIG sınav arayüzü',
        'start_path_title': '<span class="text-gradient">BIG kaydına</span> giden yolculuğunuza başlayın', # Add 'start_path_title' key
        'professional_platform': "Diş hekimlerini Hollanda'daki BIG sınavına ve lisanslamaya hazırlayan profesyonel çevrimiçi platform", # Add 'professional_platform' key
        'structured_modules': 'Yapılandırılmış öğrenme modülleri',
        'professional_dutch': 'Profesyonel Hollandaca dili',
        'practice_exams': 'Deneme sınavları',
        'continue_learning': 'Öğrenmeye Devam Et',
        'about_big_exam': 'BIG Sınavı Hakkında',
        'passed_exam': 'Sınavı geçti',
        'dental_professionals': 'Diş hekimi profesyonelleri çizimi',
        'bi_tests': 'BI testleri',
        'exam': 'Sınav',
        'virtual_patient': 'Sanal Hasta',
        'why_choose_us': 'NEDEN BİZİ SEÇMELİSİNİZ?',
        'our_approach': '<span class="text-accent">BIG sınavına</span> hazırlık yaklaşımımız', # Add 'our_approach' key
        'comprehensive_system': 'Yabancı eğitimli diş hekimleri için özel olarak tasarlanmış kapsamlı bir hazırlık sistemi sunuyoruz',
        'structured_modules_desc': 'Resmi BIG kayıt gerekliliklerine ve gerçek deneyime dayalı özenle düzenlenmiş içerik',
        'interactive_flashcards': 'Etkileşimli Bilgi Kartları',
        'interactive_flashcards_desc': 'Aralıklı tekrar kullanarak temel kavramları ezberlemek için etkili yöntem',
        'medical_dutch': 'Tıbbi Hollandaca',
        'medical_dutch_desc': 'Hollandaca tıbbi terminoloji ve hasta iletişimi üzerine özel modül',
        'realistic_tests': 'Gerçekçi Testler',
        'realistic_tests_desc': 'BIG sınavının gerçek formatını ve zorluğunu simüle eden deneme testleri',
        'personal_analytics': 'Kişisel Analitik',
        'personal_analytics_desc': 'İlerlemenizi takip edin ve ek dikkat gerektiren alanları belirleyin',
        'community_support': 'Topluluk Desteği',
        'community_support_desc': 'Aynı yolculuktaki diğer diş hekimleriyle bağlantı kurun ve başarılı adayların görüşlerine erişin',
        'ready_to_start': 'BIG sınav hazırlığınıza başlamaya hazır mısınız?',
        'start_learning': 'Öğrenmeye Başla',
        'sign_up_now': 'Şimdi Kaydol',

        # === Learning Map Page ===
        'progress': 'İlerleme',
        'overall_progress': 'Genel İlerleme',
        'lessons_completed_of': '{total} dersten {completed} tamamlandı',
        'activity': 'Etkinlik',
        'days_short': 'gün',
        'learning_time_minutes': 'Çalışma süresi: {minutes} dk.',
        'total_time': 'Toplam Süre',
        'total_time_short': 'toplam süre',
        'exam_date_label': 'Tarih',
        'not_scheduled': 'planlanmadı',
        # Phases
        'phase1_title': 'Aşama 1: Temel Teori',
        'phase2_title': 'Aşama 2: Preklinik Beceriler',
        'phase3_title': 'Aşama 3: Klinik Akıl Yürütme',
        'phase4_title': 'Aşama 4: Sınav Stratejisi',
        # Phase 1 Cards
        'basic_medical_sciences': 'Temel Tıp Bilimleri',
        'basic_medical_knowledge': 'Temel tıp bilgisi',
        'thk_1': 'THK I',
        'thk_1_subtitle': 'Kariyoloji, Endo, Periodontoloji, Pedodonti',
        'thk_2': 'THK II',
        'thk_2_subtitle': 'Protez, Orto, Cerrahi, Kinesiyoloji',
        'radiology': 'Radyoloji',
        'radiology_subtitle': 'Radyolojinin temelleri, görüntü yorumlama',
        # Phase 2 Cards
        'preclinical_simodont_skills': 'Preklinik Simodont Becerileri',
        'preclinical_simodont_subtitle': 'Çürük preparasyonu, endodontik giriş, kuron preparasyonu',
        'professional_cleaning_title': 'Profesyonel Temizlik',
        'professional_cleaning_subtitle': 'Profesyonel diş temizliği, scaling',
        'module_in_development': 'Bu modül geliştirme aşamasındadır',
        # Phase 3 Cards
        'interactive_clinical_cases': 'İnteraktif Klinik Vakalar',
        'virtual_patients_desc': 'İnteraktif sanal hasta senaryoları ile klinik akıl yürütme ve iletişim becerilerinizi geliştirin.',
        'start_scenarios': 'Senaryolara Başla',
        'intake_interview_title': 'İlk Görüşme',
        'intake_interview_subtitle': 'İlk konsültasyon, iletişim becerileri',
        'treatment_planning': 'Tedavi Planlaması',
        'treatment_planning_subtitle': 'Tedavi planlamasının temelleri',
        # Phase 4 Cards
        'advanced_treatment_planning': 'İleri Tedavi Planlaması',
        'advanced_treatment_planning_subtitle': 'Casus pratiği, klinik vakalar',
        'statistics_methodology': 'İstatistik ve Metodoloji',
        'statistics_methodology_subtitle': 'Open Book hazırlığı',
        # Module/Button Items
        'premium': 'Premium',
        'test': 'Test',
        'repeat': 'Tekrarla',
        'repeat_test': 'Testi Tekrarla',
        'continue_progress': 'Devam Et ({progress}%)',
        'start': 'Başla',
        'start_test': 'Teste Başla',
        'loading': 'Yükleniyor...',
        'redirecting': 'Yönlendiriliyor...',

        # === General Learning Map Translations ===
        'subcategories': 'Alt Kategoriler',
        'subcategories_title': 'Alt Kategoriler',
        'topics_title': 'Konular',
        'lessons_title': 'Dersler',
        'min': 'dk',
        'days_active': 'Aktif Günler',
        'countdown': 'Geri Sayım',
        'days_until_exam': 'sınava kalan gün',
        'schedule_exam': 'Sınavı Planla',
        'recommended_for_you': 'Sizin için önerilenler',
        'recommendations': 'Sizin için önerilenler',
        'select_category': 'Öğrenmeye başlamak için bir kategori seçin',
        'ready_to_start_learning': 'Öğrenmeye başlamaya hazır mısınız?',
        'choose_subject_category': 'Başlamak için sol menüden bir konu veya kategori seçin',
        'select_date': 'Tarih seçin',
        'cancel': 'İptal',
        'save': 'Kaydet',
        'clinical_cases': 'Klinik Vakalar',
        'all_virtual_patients': 'Tüm Sanal Hastalar',
        # Dashboard
        'learning_dashboard': 'Öğrenim Paneli',
        'your_progress': 'İlerlemeniz',
        'activity_days': 'Etkinlik Günleri',
        'exam_date': 'Sınav Tarihi',
        'exam_date_placeholder': '15 Temmuz 2025',
        'change_date': 'Tarihi Değiştir',
        'customize_learning_plan': 'Öğrenme Planını Özelleştir',
        'unlock_all_features': 'Tüm Özellikleri Kilidi Aç',
        'upgrade_premium_description': 'Tüm modüllere erişim için premium plana yükseltin',
        'subscribe_now': 'Şimdi Abone Ol',
        'recommended_module': 'Önerilen Modül',
        'continue_this_module': 'Bu Modüle Devam Et',
        'dental_anatomy': 'Diş Anatomisi',
        'dental_anatomy_description': 'Dişlerin temel yapısı ve morfolojisi',
        'sections': 'bölümler',
        'go_to_learning': 'Öğrenmeye Git',
        'your_modules': 'Modülleriniz',
        'all_modules': 'Tüm Modüller',
        'terminology': 'Terminoloji',
        'physiology': 'Fizyoloji',
        'diagnostics': 'Tanı',
        'set_exam_date': 'Sınav Tarihi Belirle',
        'exam_date_saved': 'Sınav tarihi başarıyla kaydedildi',
        'error_saving_date': 'Sınav tarihi kaydedilirken hata oluştu',
        'server_error': 'Sunucu hatası',
        # General Learning Map (from older version, some moved/refined)
        'welcome_message': 'Hoş geldiniz!',
        'welcome_title': 'Become a Tandarts\'a Hoş Geldiniz!',
        'welcome_subtitle': 'BIG sınavına başarılı hazırlık yolunuz',
        'welcome_description': 'İnteraktif platformumuz sınavınıza etkili bir şekilde hazırlanmanıza yardımcı olacaktır. Öğrenmeye başlamak için bir bölüm seçin veya önerilen konuları keşfedin.',
        'select_subject_from_left_list': 'Soldaki listeden bir konu seçin',
        # Learning Paths (from older version)
        'knowledge_center': 'Bilgi Merkezi',
        'communication': 'İletişim',
        'preclinical_skills': 'Preklinik Beceriler',
        'workstation': 'İş İstasyonu',
        'bi_toets': 'BI-Toets',
        'virtual_patients': 'Sanal Hastalar',
        'dutch_for_dentists': 'Diş Hekimleri İçin Hollandaca',
        # Path Descriptions (from older version)
        'knowledge_center_desc': 'Teorik temeller ve anahtar kavramlar',
        'communication_desc': 'Hasta iletişim becerilerini geliştirin',
        'preclinical_desc': 'Temel diş prosedürleri',
        'workstation_desc': 'Klinik uygulama ve yönetim',
        'bi_toets_desc': 'BI-test hazırlığı ve pratiği',
        'dutch_desc': 'Profesyonel Hollandaca dil becerileri',
        # Progress and Stats (from older version, some merged with newer)
        'lessons_completed': 'ders tamamlandı',
        'days_active_lower': 'aktif gün',
        # Recommendations (from older version, some merged with newer)
        'getting_started': 'Başlarken',
        # Virtual Patients (from older version, some merged with newer)
        'difficulty_easy': 'Kolay',
        'difficulty_medium': 'Orta',
        'difficulty_hard': 'Zor',
        'attempts_short': 'deneme',
        'continue_vp': 'Devam Et',
        'no_virtual_patients_for_subject': 'Bu konu için henüz sanal hasta mevcut değil',
        # Modules and Subjects (from older version)
        'no_modules_yet': 'Henüz modül mevcut değil',
        'modules_coming_soon': 'Modüller yakında eklenecektir',
        'no_subjects': 'Konu yok',
        'subjects_coming_soon': 'Konular yakında eklenecektir',
        'module_description': 'Modül açıklaması',
        'subject_description': 'Konu açıklaması',
        'scenario_description': 'Senaryo açıklaması',
        'subject_name': 'Konu adı',
        'path_description': 'Öğrenme yolu açıklaması',
        # Interface (from older version)
        'change_language': 'Dili değiştir',
        'toggle_theme': 'Temayı değiştir',
        'search': 'Ara',
        'search_placeholder': 'Kursları, dersleri veya konuları ara...',
        'recent_searches': 'Son Aramalar',
        'popular_topics': 'Popüler Konular',
        'search_tips': 'İpuçları:',
        'to_navigate': 'gezinmek için',
        'to_select': 'seçmek için',
        'to_close': 'kapatmak için',
        # Interactive Elements (from older version)
        'did_you_know': 'Biliyor muydunuz?',
        'click_to_learn': 'İlginç bir diş hekimliği gerçeğini öğrenmek için tıklayın',
        'fun_fact': 'Eğlenceli Bilgi',
        'tooth_fact': 'Diş minesi insan vücudundaki en sert maddedir!',
        # Error Messages (from older version, some merged with newer)
        'js_error': 'Bir hata oluştu. Lütfen sayfayı yenileyin.',
        'ajax_error': 'Veriler yüklenirken bir hata oluştu.',

        # Additional keys from index.html that were not in translations.py (translated)
        "platform_description": "Hollanda'da BIG sınavına hazırlık için modern eğitim platformu. Bireysel yaklaşımla yüksek kaliteli eğitim.", # Add 'platform_description' key
        'learn_more': 'Daha fazla bilgi edin',
        'exam_preparation': 'Sınav Hazırlığı',
        'languages_supported': 'Desteklenen Diller',
        'availability': 'Erişilebilirlik',
        'interactive_learning': 'Etkileşimli Öğrenme',
        'structured_learning': 'Yapılandırılmış Öğrenme',
        'structured_learning_desc': 'Adım adım sınav hazırlık programı',
        'clinical_cases_desc': 'Gerçekçi tıbbi senaryolar üzerinde pratik yapın',
        'progress_tracking': 'İlerleme Takibi',
        'progress_tracking_desc': 'Öğreniminizin detaylı analizi',
        'theory_title': 'Teori',
        'theory_description': 'Anatomi, fizyoloji ve radyoloji üzerine yapılandırılmış modüller',
        'anatomy': 'Anatomi',
        'physiology': 'Fizyoloji',
        'radiology': 'Radyoloji',
        'most_popular': 'En Popüler',
        'practice_title': 'Pratik',
        'practice_description': 'Klinik vakalar ve hasta etkileşimi simülasyonu',
        'case_studies': 'Vaka Çalışmaları',
        'communication': 'İletişim',
        'exam_description': 'Sonuç analizi ile gerçek sınavlara hazırlık',
        'mock_exams': 'Deneme Sınavları',
        'analytics': 'Analizler',
        'strategy': 'Strateji',
        'start_your_journey': 'Yolculuğunuza Başlayın',
        'platform_features': 'Platform Özellikleri',
        'comprehensive_approach': 'Diş hekimliği hazırlığına kapsamlı yaklaşım',
        'multilingual_support': 'Çok Dilli Destek',
        'multilingual_description': 'Farklı ülkelerden gelen öğrenciler için 8 dilde öğrenim',
        'flexible_schedule': 'Esnek Program',
        'flexible_description': 'Kendi hızınızda ve uygun olduğunuz zaman öğrenin',
        'quality_assurance': 'Kalite Güvencesi',
        'quality_description': 'İçerik diş hekimliği uzmanları tarafından geliştirilmiştir',
        'support_247': '7/24 Destek',
        'support_description': 'Kesintisiz kullanıcı desteği',
        'learning_approach': 'Öğrenme Yaklaşımı',
        'our_methodology': 'Metodolojimiz',
        'evidence_based': 'Kanıta dayalı öğrenme sistemi',
        'adaptive_testing': 'Adaptif Test',
        'adaptive_testing_desc': 'Optimum öğrenme için bilgi seviyenize uyum sağlayan testler',
        'realistic_simulations': 'Gerçekçi Simülasyonlar',
        'realistic_simulations_desc': 'Gerçekliğe mümkün olduğunca yakın sanal hastalar ve klinik senaryolar',
        'detailed_analytics': 'Detaylı Analitik',
        'detailed_analytics_desc': 'Kişiselleştirilmiş önerilerle detaylı ilerleme istatistikleri',
        'community_learning': 'Topluluk Öğrenimi',
        'community_learning_desc': 'Bilgi alışverişi için aktif öğrenci ve uzman topluluğu',
        'join_thousands': 'Platformumuzla BIG sınavına hazırlanan binlerce öğrenciye katılın',
        'start_now': 'Şimdi Başla',
                # Hero секция
        'welcome_hero_title': 'Diş Hekimi Olun',
        'welcome_hero_subtitle': 'Diş hekimliği becerilerinde ustalaşın. BIG sınavını geçin. Hollanda\'daki kariyerinizi dönüştürün.',
        'dental_academy': 'Dental Academy',
        'start_free_trial': 'Ücretsiz Deneme Başlat',
        'explore_platform': 'Platformu Keşfet',
        
        # Особенности платформы
        'why_choose_us': 'Neden Dental Academy\'yi Seçmelisiniz?',
        'platform_benefits': 'Hollanda diş hekimliği pratiğinde başarılı olmak için ihtiyacınız olan her şey',
        'expert_content': 'Uzman İçeriği',
        'expert_content_desc': 'BIG sınav başarısı için Hollandalı diş hekimliği uzmanları tarafından düzenlenmiştir',
        'virtual_patients': 'Sanal Hastalar',
        'virtual_patients_desc': 'Gerçekçi hasta senaryoları ve vaka çalışmaları ile pratik yapın',
        'adaptive_learning': 'Uyarlamalı Öğrenme',
        'adaptive_learning_desc': 'AI destekli sistem öğrenme hızınıza ve tarzınıza uyum sağlar',
        'multilingual': '8 Dil',
        'multilingual_desc': 'Ana dilinizde çalışın, Hollandaca terminolojiyi öğrenin',
        
        # Статистика
        'platform_stats': 'Binlerce başarılı öğrenciye katılın',
        'active_students': 'Aktif Öğrenci',
        'success_rate': 'Başarı Oranı %',
        'practice_questions': 'Pratik Sorular',
        'languages': 'Dil',
        
        # Отзывы
        'student_success': 'Öğrenci Başarı Hikayeleri',
        'testimonial_1': 'Dental Academy BIG sınavını ilk denemede geçmeme yardımcı oldu. Sanal hastalar inanılmaz derecede gerçekçiydi!',
        'testimonial_author_1': 'Anna Martinez',
        'dentist_amsterdam': 'Diş Hekimi, Amsterdam',
        
        # Финальный CTA
        'ready_to_start': 'Yolculuğunuza Başlamaya Hazır mısınız?',
        'join_thousands_desc': 'BIG sınav hazırlığı için platformumuza güvenen binlerce diş hekimine katılın',
        'get_started_free': 'Ücretsiz Başlayın',
        
        # Быстрые подсказки
        'quick_tip_mobile': '💡 İpucu: En iyi deneyim için bu uygulamayı ana ekranınıza ekleyin!',
        
        # Языки
        'language_name_en': 'English',
        'language_name_nl': 'Nederlands',
        'language_name_ru': 'Русский',
        'language_name_uk': 'Українська',
        'language_name_es': 'Español',
        'language_name_pt': 'Português',
        'language_name_tr': 'Türkçe',
        'language_name_fa': 'Farsça', # Corrected to Farsça
        'language_name_ar': 'العربية',
        
        # UI элементы
        'select_language': 'Dil Seç',
        'toggle_theme': 'Tema Değiştir',
        'theme_changed': 'Tema değiştirildi',
        'language_changed': 'Dil başarıyla değiştirildi',
        'install_prompt': 'En iyi deneyim için bu uygulamayı yükleyin!',
        'install_success': 'Uygulama başarıyla yüklendi!',
        'network_error': 'Ağ hatası oluştu',
        'try_again': 'Tekrar dene',
        'loading': 'Yükleniyor...',
    },

    'ar': {
        # === Navigation & Auth ===
        'home': 'الرئيسية',
        'learning': 'التعلم',
        'learning_map': 'خريطة التعلم',
        'tests': 'الاختبارات',
        'patients': 'المرضى',
        'ai_assistant': 'مساعد ذكي',
        'dashboard': 'لوحة التحكم',
        'about_big': 'حول BIG',
        'profile': 'الملف الشخصي',
        'settings': 'الإعدادات',
        'admin_panel': 'لوحة الإدارة',
        'logout': 'تسجيل الخروج',
        'login': 'تسجيل الدخول',
        'register': 'التسجيل',
        
        # === Homepage Content ===
        'big_exam_for_dentists': 'امتحان BIG لأطباء الأسنان',
        'successful_path_title': 'طريقك الناجح إلى ترخيص طب الأسنان',
        'start_for_free': 'ابدأ مجانًا',
        'learn_about_big': 'تعرف على امتحان BIG',
        'students': 'طالب',
        'success_rate': '% معدل النجاح',
        'rating': 'التقييم',
        'continue_learning': 'متابعة التعلم',
        'about_big_exam': 'حول امتحان BIG',
        'virtual_patient': 'مريض افتراضي',
        'why_choose_us': 'لماذا تختارنا؟',
        'start_learning': 'ابدأ التعلم',
        
        # === Learning Map Page ===
        'progress': 'التقدم',
        'overall_progress': 'التقدم العام',
        'activity': 'النشاط',
        'days_short': 'يوم',
        'total_time': 'الوقت الإجمالي',
        'exam_date_label': 'التاريخ',
        'not_scheduled': 'غير مجدول',
        'basic_medical_sciences': 'العلوم الطبية الأساسية',
        'radiology': 'الأشعة',
        'preclinical_skills': 'المهارات قبل السريرية',
        'virtual_patients': 'مرضى افتراضيون',
        'treatment_planning': 'تخطيط العلاج',
        'premium': 'مميز',
        'test': 'اختبار',
        'start': 'ابدأ',
        'start_test': 'ابدأ الاختبار',
        'loading': 'جاري التحميل...',
        
        # === UI Elements ===
        'dark_mode': 'الوضع المظلم',
        'light_mode': 'الوضع المضيء', 
        'language': 'اللغة',
        'theme': 'المظهر',
        'switch_theme': 'تبديل المظهر',
        'current_language': 'اللغة الحالية',
        
        # === Authentication ===
        'register': 'التسجيل',
        'login': 'تسجيل الدخول',
        'already_have_account_signin': 'لديك حساب بالفعل؟ تسجيل الدخول',
        'create_account': 'إنشاء حساب',
        'enter_your_name': 'أدخل اسمك',
        'enter_your_email': 'أدخل بريدك الإلكتروني',
        'next': 'التالي',
        'back': 'السابق',
        'create_strong_password': 'إنشاء كلمة مرور قوية',
        'repeat_password': 'تكرار كلمة المرور',
        'submit': 'إرسال',
        'continue': 'متابعة',
        'start': 'ابدأ',
        
        # === Navigation (already exists but adding for consistency) ===
        'home': 'الرئيسية',
        'learning': 'التعلم', 
        'tests': 'الاختبارات',
        'patients': 'المرضى',
        'ai_assistant': 'المساعد الذكي',
        
        # === Additional UI ===
        'settings': 'الإعدادات',
        'profile': 'الملف الشخصي',
        'logout': 'تسجيل الخروج',
        'loading': 'جاري التحميل...',
        'error': 'خطأ',
        'success': 'نجح',
        'cancel': 'إلغاء',
        'save': 'حفظ',
        'patients_coming_soon': 'المرضى قادمون قريباً',
    },

    # === WELCOME PAGE CONTENT KEYS ===
    'become_tandarts': {
        'en': 'Become a Tandarts',
        'ru': 'Стань Дантистом',
        'nl': 'Word een Tandarts',
        'uk': 'Стань Дантистом',
        'es': 'Conviértete en Dentista',
        'pt': 'Torne-se um Dentista',
        'tr': 'Bir Diş Hekimi Ol',
        'fa': 'دندانپزشک شوید',
        'ar': 'كن طبيب أسنان'
    },
    'hero_subtitle': {
        'en': 'Master dental skills. Pass BIG exam. Transform your career in Netherlands.',
        'ru': 'Овладей навыками стоматологии. Сдай экзамен BIG. Преобрази свою карьеру в Нидерландах.',
        'nl': 'Beheers tandheelkundige vaardigheden. Slaag voor het BIG-examen. Transformeer je carrière in Nederland.',
        'uk': 'Опануй навички стоматології. Склади іспит BIG. Трансформуй свою кар\'єру в Нідерландах.',
        'es': 'Domina las habilidades dentales. Aprueba el examen BIG. Transforma tu carrera en los Países Bajos.',
        'pt': 'Domine habilidades odontológicas. Passe no exame BIG. Transforme sua carreira na Holanda.',
        'tr': 'Diş hekimliği becerilerinde ustalaşın. BIG sınavını geçin. Hollanda\'daki kariyerinizi dönüştürün.',
        'fa': 'مهارت‌های دندانپزشکی را فراگیرید. آزمون BIG را بگذرانید. شغل خود را در هلند متحول کنید.',
        'ar': 'أتقن مهارات طب الأسنان. اجتز امتحان BIG. حول مسيرتك المهنية في هولندا.'
    },
    'start_free_trial': {
        'en': 'Start Free Trial',
        'ru': 'Начать Бесплатно',
        'nl': 'Start Gratis Proefperiode',
        'uk': 'Почати Безкоштовно',
        'es': 'Comenzar Prueba Gratuita',
        'pt': 'Iniciar Teste Gratuito',
        'tr': 'Ücretsiz Deneme Başlat',
        'fa': 'شروع آزمایش رایگان',
        'ar': 'ابدأ التجربة المجانية'
    },
    'explore_platform': {
        'en': 'Explore Platform',
        'ru': 'Изучить Платформу',
        'nl': 'Verken Platform',
        'uk': 'Вивчити Платформу',
        'es': 'Explorar Plataforma',
        'pt': 'Explorar Plataforma',
        'tr': 'Platformu Keşfet',
        'fa': 'کاوش پلتفرم',
        'ar': 'استكشف المنصة'
    },
    'why_choose_dental_academy': {
        'en': 'Why Choose Dental Academy?',
        'ru': 'Почему Стоматологическая Академия?',
        'nl': 'Waarom Tandheelkunde Academie kiezen?',
        'uk': 'Чому Стоматологічна Академія?',
        'es': '¿Por qué elegir Academia Dental?',
        'pt': 'Por que escolher a Academia Dental?',
        'tr': 'Neden Diş Hekimliği Akademisi?',
        'fa': 'چرا آکادمی دندانپزشکی را انتخاب کنیم؟',
        'ar': 'لماذا تختار أكاديمية طب الأسنان؟'
    },
    'expert_content': {
        'en': 'Expert Content',
        'ru': 'Экспертный Контент',
        'nl': 'Expert Inhoud',
        'uk': 'Експертний Контент',
        'es': 'Contenido Experto',
        'pt': 'Conteúdo Especializado',
        'tr': 'Uzman İçeriği',
        'fa': 'محتوای متخصص',
        'ar': 'محتوى الخبراء'
    },
    'expert_content_description': {
        'en': 'Curated by Dutch dental professionals for BIG exam success',
        'ru': 'Составлено голландскими стоматологами для успеха на экзамене BIG',
        'nl': 'Samengesteld door Nederlandse tandartsen voor BIG-examensucces',
        'uk': 'Складено голландськими стоматологами для успіху на іспиті BIG',
        'es': 'Curado por profesionales dentales holandeses para el éxito en el examen BIG',
        'pt': 'Curado por profissionais dentários holandeses para sucesso no exame BIG',
        'tr': 'BIG sınav başarısı için Hollandalı diş hekimleri tarafından hazırlandı',
        'fa': 'توسط متخصصان دندانپزشکی هلندی برای موفقیت در آزمون BIG تنظیم شده',
        'ar': 'منسق من قبل أطباء الأسنان الهولنديين لنجاح امتحان BIG'
    },
    'virtual_patients': {
        'en': 'Virtual Patients',
        'ru': 'Виртуальные Пациенты',
        'nl': 'Virtuele Patiënten',
        'uk': 'Віртуальні Пацієнти',
        'es': 'Pacientes Virtuales',
        'pt': 'Pacientes Virtuais',
        'tr': 'Sanal Hastalar',
        'fa': 'بیماران مجازی',
        'ar': 'المرضى الافتراضيون'
    },
    'virtual_patients_description': {
        'en': 'Practice with realistic patient scenarios and case studies',
        'ru': 'Практикуйся с реалистичными сценариями пациентов и кейсами',
        'nl': 'Oefen met realistische patiëntscenario\'s en casestudies',
        'uk': 'Практикуйся з реалістичними сценаріями пацієнтів та кейсами',
        'es': 'Practica con escenarios realistas de pacientes y estudios de casos',
        'pt': 'Pratique com cenários realistas de pacientes e estudos de caso',
        'tr': 'Gerçekçi hasta senaryoları ve vaka çalışmaları ile pratik yapın',
        'fa': 'با سناریوهای واقعی بیمار و مطالعات موردی تمرین کنید',
        'ar': 'تدرب مع سيناريوهات المرضى الواقعية ودراسات الحالة'
    },
    'adaptive_learning': {
        'en': 'Adaptive Learning',
        'ru': 'Адаптивное Обучение',
        'nl': 'Adaptief Leren',
        'uk': 'Адаптивне Навчання',
        'es': 'Aprendizaje Adaptativo',
        'pt': 'Aprendizagem Adaptativa',
        'tr': 'Uyarlanabilir Öğrenme',
        'fa': 'یادگیری تطبیقی',
        'ar': 'التعلم التكيفي'
    },
    'adaptive_learning_description': {
        'en': 'AI-powered system adapts to your learning pace and style',
        'ru': 'ИИ-система адаптируется к твоему темпу и стилю обучения',
        'nl': 'AI-gestuurd systeem past zich aan je leertempo en -stijl aan',
        'uk': 'ІІ-система адаптується до твого темпу та стилю навчання',
        'es': 'Sistema impulsado por IA se adapta a tu ritmo y estilo de aprendizaje',
        'pt': 'Sistema alimentado por IA adapta-se ao seu ritmo e estilo de aprendizagem',
        'tr': 'AI destekli sistem öğrenme hızınıza ve tarzınıza uyum sağlar',
        'fa': 'سیستم مبتنی بر هوش مصنوعی با سرعت و سبک یادگیری شما سازگار می‌شود',
        'ar': 'نظام مدعوم بالذكاء الاصطناعي يتكيف مع وتيرة وأسلوب التعلم الخاص بك'
    },
    'nine_languages': {
        'en': '9 Languages',
        'ru': '9 Языков',
        'nl': '9 Talen',
        'uk': '9 Мов',
        'es': '9 Idiomas',
        'pt': '9 Idiomas',
        'tr': '9 Dil',
        'fa': '۹ زبان',
        'ar': '٩ لغات'
    },
    'nine_languages_description': {
        'en': 'Study in your native language, master Dutch terminology',
        'ru': 'Изучай на родном языке, освоив голландскую терминологию',
        'nl': 'Studeer in je moedertaal, beheers Nederlandse terminologie',
        'uk': 'Вивчай рідною мовою, освоюючи голландську термінологію',
        'es': 'Estudia en tu idioma nativo, domina la terminología holandesa',
        'pt': 'Estude na sua língua nativa, domine a terminologia holandesa',
        'tr': 'Ana dilinizde çalışın, Hollandaca terminolojiyi öğrenin',
        'fa': 'به زبان مادری خود مطالعه کنید، اصطلاحات هلندی را فرا بگیرید',
        'ar': 'ادرس بلغتك الأم، أتقن المصطلحات الهولندية'
    },
    
    # === VIRTUAL PATIENTS PAGE ===
    'practice_clinical_skills': {
        'en': 'Practice clinical skills with virtual patients. Each case is based on real clinical scenarios.',
        'ru': 'Практикуйся с виртуальными пациентами. Каждый случай основан на реальных клинических сценариях.',
        'nl': 'Oefen klinische vaardigheden met virtuele patiënten. Elke casus is gebaseerd op echte klinische scenario\'s.',
        'uk': 'Практикуйся з віртуальними пацієнтами. Кожен випадок базується на реальних клінічних сценаріях.',
        'es': 'Practica habilidades clínicas con pacientes virtuales. Cada caso se basa en escenarios clínicos reales.',
        'pt': 'Pratique habilidades clínicas com pacientes virtuais. Cada caso é baseado em cenários clínicos reais.',
        'tr': 'Sanal hastalarla klinik becerilerinizi geliştirin. Her vaka gerçek klinik senaryolara dayanmaktadır.',
        'fa': 'مهارت‌های بالینی را با بیماران مجازی تمرین کنید. هر مورد بر اساس سناریوهای بالینی واقعی است.',
        'ar': 'تدرب على المهارات السريرية مع المرضى الافتراضيين. كل حالة تعتمد على سيناريوهات سريرية حقيقية.'
    },
    'virtual_patients_development': {
        'en': 'Virtual patients are in development. Soon you\'ll be able to practice your skills!',
        'ru': 'Виртуальные пациенты находятся в разработке. Скоро вы сможете практиковать свои навыки!',
        'nl': 'Virtuele patiënten zijn in ontwikkeling. Binnenkort kun je je vaardigheden oefenen!',
        'uk': 'Віртуальні пацієнти в розробці. Незабаром ви зможете практикувати свої навички!',
        'es': 'Los pacientes virtuales están en desarrollo. ¡Pronto podrás practicar tus habilidades!',
        'pt': 'Pacientes virtuais estão em desenvolvimento. Em breve você poderá praticar suas habilidades!',
        'tr': 'Sanal hastalar geliştirilmekte. Yakında becerilerinizi pratik edebileceksiniz!',
        'fa': 'بیماران مجازی در حال توسعه هستند. به زودی خواهید توانست مهارت‌های خود را تمرین کنید!',
        'ar': 'المرضى الافتراضيون قيد التطوير. قريباً ستتمكن من ممارسة مهاراتك!'
    },
    
    # === TEST SYSTEM ===
    'test_system': {
        'en': 'Test System',
        'ru': 'Система Тестирования',
        'nl': 'Test Systeem',
        'uk': 'Система Тестування',
        'es': 'Sistema de Pruebas',
        'pt': 'Sistema de Testes',
        'tr': 'Test Sistemi',
        'fa': 'سیستم آزمون',
        'ar': 'نظام الاختبار'
    },
    'choose_test_type': {
        'en': 'Choose test type to check your knowledge',
        'ru': 'Выберите тип теста для проверки знаний',
        'nl': 'Kies testtype om je kennis te controleren',
        'uk': 'Оберіть тип тесту для перевірки знань',
        'es': 'Elige el tipo de prueba para verificar tu conocimiento',
        'pt': 'Escolha o tipo de teste para verificar seu conhecimento',
        'tr': 'Bilginizi kontrol etmek için test türünü seçin',
        'fa': 'نوع آزمون را برای بررسی دانش خود انتخاب کنید',
        'ar': 'اختر نوع الاختبار للتحقق من معرفتك'
    },
    'error_loading_tests': {
        'en': 'Error loading test categories',
        'ru': 'Ошибка загрузки категорий тестов',
        'nl': 'Fout bij laden van testcategorieën',
        'uk': 'Помилка завантаження категорій тестів',
        'es': 'Error al cargar las categorías de pruebas',
        'pt': 'Erro ao carregar categorias de teste',
        'tr': 'Test kategorileri yüklenirken hata',
        'fa': 'خطا در بارگیری دسته‌بندی آزمون‌ها',
        'ar': 'خطأ في تحميل فئات الاختبار'
    },
    'quick_start': {
        'en': 'Quick Start',
        'ru': 'Быстрый старт',
        'nl': 'Snelle start',
        'uk': 'Швидкий старт',
        'es': 'Inicio rápido',
        'pt': 'Início rápido',
        'tr': 'Hızlı başlangıç',
        'fa': 'شروع سریع',
        'ar': 'بداية سريعة'
    },
    'start_learning_journey': {
        'en': 'Start your learning journey',
        'ru': 'Начните свое обучение',
        'nl': 'Begin je leerreis',
        'uk': 'Почніть своє навчання',
        'es': 'Comienza tu viaje de aprendizaje',
        'pt': 'Comece sua jornada de aprendizado',
        'tr': 'Öğrenme yolculuğunuza başlayın',
        'fa': 'سفر یادگیری خود را شروع کنید',
        'ar': 'ابدأ رحلة التعلم'
    },
    'test_your_knowledge': {
        'en': 'Test your knowledge',
        'ru': 'Проверьте свои знания',
        'nl': 'Test je kennis',
        'uk': 'Перевірте свої знання',
        'es': 'Pon a prueba tus conocimientos',
        'pt': 'Teste seus conhecimentos',
        'tr': 'Bilginizi test edin',
        'fa': 'دانش خود را آزمایش کنید',
        'ar': 'اختبر معرفتك'
    },
    'get_instant_help': {
        'en': 'Get instant help',
        'ru': 'Получите мгновенную помощь',
        'nl': 'Krijg directe hulp',
        'uk': 'Отримайте миттєву допомогу',
        'es': 'Obtén ayuda instantánea',
        'pt': 'Obtenha ajuda instantânea',
        'tr': 'Anında yardım alın',
        'fa': 'کمک فوری دریافت کنید',
        'ar': 'احصل على مساعدة فورية'
    }

}

def get_translation(key, lang='en', **kwargs):
    """
    Возвращает перевод для ключа в указанном языке

    Args:
        key (str): Ключ для перевода
        lang (str): Код языка
        **kwargs: Параметры для форматирования строки перевода

    Returns:
        str: Переведенная строка
    """
    if lang not in translations:
        lang = 'en'

    # Сначала проверяем ключ в указанном языке
    translation_value = translations[lang].get(key)

    # Если ключ не найден в текущем языке и язык не английский, пробуем найти в английском
    if translation_value is None and lang != 'en':
        translation_value = translations['en'].get(key)

    # Если ключ все еще не найден (даже в английском), возвращаем сам ключ
    if translation_value is None:
        return key

    # Если есть параметры для форматирования, применяем их
    if kwargs:
        try:
            return translation_value.format(**kwargs)
        except KeyError as e:
            # Если ключ форматирования отсутствует в строке, просто возвращаем строку
            print(f"Warning: Formatting key '{e}' not found in translation for '{key}' in lang '{lang}'. Returning raw string.")
            return translation_value
        except Exception as e:
            # В случае другой ошибки форматирования возвращаем исходную строку
            print(f"Error formatting translation for key '{key}': {e}")
            return translation_value

    return translation_value

def get_available_languages():
    """Возвращает список доступных языков"""
    return list(translations.keys())

def get_language_names():
    """Возвращает словарь с названиями языков"""
    return {
        'en': 'English',
        'nl': 'Nederlands',
        'ru': 'Русский',
        'es': 'Español',
        'pt': 'Português',
        'uk': 'Українська',
        'fa': 'فارسی',
        'tr': 'Türkçe',
        'ar': 'العربية'
    }

def is_rtl_language(lang):
    """Проверяет, является ли язык языком с письмом справа налево"""
    rtl_languages = ['fa', 'ar', 'he']
    return lang in rtl_languages

def get_country_code(lang_code):
    """
    Возвращает код страны для флага по коду языка
    
    Args:
        lang_code (str): Код языка
        
    Returns:
        str: Код страны для отображения флага
    """
    country_mapping = {
        'en': 'gb',
        'nl': 'nl',
        'ru': 'ru',
        'uk': 'ua',
        'es': 'es',
        'pt': 'pt',
        'tr': 'tr',
        'fa': 'ir',
        'ar': 'sa'
    }
    return country_mapping.get(lang_code, 'gb')

def get_language_direction(lang_code):
    """
    Возвращает направление текста для языка (rtl или ltr)
    
    Args:
        lang_code (str): Код языка
        
    Returns:
        str: 'rtl' для языков с письмом справа налево, 'ltr' для остальных
    """
    return 'rtl' if is_rtl_language(lang_code) else 'ltr'

def merge_welcome_translations(main_translations, welcome_translations):
    """
    Объединяет переводы welcome страницы с основными переводами
    
    Args:
        main_translations (dict): Основной словарь переводов
        welcome_translations (dict): Словарь переводов welcome страницы
        
    Returns:
        dict: Объединенный словарь переводов
    """
    result = main_translations.copy()
    
    for lang_code, translations in welcome_translations.items():
        if lang_code in result:
            result[lang_code].update(translations)
        else:
            result[lang_code] = translations
    
    return result

def validate_translation_completeness():
    """Проверяет полноту переводов для всех языков"""
    base_keys = set(translations['en'].keys())
    incomplete_languages = {}

    for lang, lang_translations in translations.items():
        if lang == 'en':
            continue

        lang_keys = set(lang_translations.keys())
        missing_keys = base_keys - lang_keys
        extra_keys = lang_keys - base_keys

        if missing_keys or extra_keys:
            incomplete_languages[lang] = {
                'missing': list(missing_keys),
                'extra': list(extra_keys)
            }

    return incomplete_languages

# Для Flask приложения можно создать функцию-помощник
def create_translation_function(app):
    """
    Создает функцию перевода для использования в Flask шаблонах

    Args:
        app: Flask приложение
    """
    def translate(key, lang=None, **kwargs):
        if lang is None:
            # Получаем язык из Flask g объекта
            from flask import g
            lang = getattr(g, 'lang', 'en')

        return get_translation(key, lang, **kwargs)

    # Регистрируем функцию в Jinja2
    app.jinja_env.globals['t'] = translate
    return translate

# Пример использования для Flask
def setup_translations(app):
    """
    Настраивает систему переводов для Flask приложения

    Args:
        app: Flask приложение
    """
    # Создаем функцию перевода
    translate = create_translation_function(app)

    # Добавляем дополнительные функции в шаблоны
    app.jinja_env.globals.update({
        'get_available_languages': get_available_languages,
        'get_language_names': get_language_names,
        'is_rtl_language': is_rtl_language,
        'get_country_code': get_country_code,
        'get_language_direction': get_language_direction
    })

    return translate

if __name__ == '__main__':
    # Проверка полноты переводов
    print("Проверка полноты переводов:")
    incomplete = validate_translation_completeness()

    if incomplete:
        for lang, issues in incomplete.items():
            print(f"\n{lang.upper()}:")
            if issues['missing']:
                print(f"  Отсутствуют: {issues['missing'][:5]}...")  # Показываем первые 5
            if issues['extra']:
                print(f"  Лишние: {issues['extra'][:5]}...")
    else:
        print("Все переводы полные!")

    # Пример использования
    print(f"\nПример использования:")
    print(f"EN: {get_translation('welcome_title', 'en')}")
    print(f"RU: {get_translation('welcome_title', 'ru')}")
    print(f"NL: {get_translation('welcome_title', 'nl')}")
    print(f"Несуществующий ключ: {get_translation('non_existent', 'ru')}")
    print(f"lessons_completed_of (en): {get_translation('lessons_completed_of', 'en', completed=7, total=10)}")
    print(f"lessons_completed_of (ru): {get_translation('lessons_completed_of', 'ru', completed=7, total=10)}")
    print(f"learning_time_minutes (nl): {get_translation('learning_time_minutes', 'nl', minutes=120)}")
    print(f"platform_description (en): {get_translation('platform_description', 'en')}")
    print(f"platform_description (ru): {get_translation('platform_description', 'ru')}")
    print(f"platform_description (nl): {get_translation('platform_description', 'nl')}")