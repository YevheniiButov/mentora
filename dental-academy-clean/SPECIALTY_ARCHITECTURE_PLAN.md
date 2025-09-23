# 🏗️ АРХИТЕКТУРА ДИАГНОСТИЧЕСКОЙ СИСТЕМЫ ДЛЯ ДВУХ СПЕЦИАЛЬНОСТЕЙ

## 📊 **1. МОДЕЛИ ДАННЫХ**

### **1.1 Новая модель Specialty**
```python
class Specialty(db.Model):
    """Специальности в системе диагностики"""
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # 'DENTIST', 'GP'
    name = db.Column(db.String(100), nullable=False)  # 'Стоматолог', 'Врач общей практики'
    name_en = db.Column(db.String(100), nullable=False)
    name_nl = db.Column(db.String(100), nullable=False)
    
    # Статус системы
    is_active = db.Column(db.Boolean, default=True)
    is_calibrated = db.Column(db.Boolean, default=False)  # Есть ли калиброванные вопросы
    total_questions = db.Column(db.Integer, default=0)
    calibrated_questions = db.Column(db.Integer, default=0)
    
    # IRT настройки
    irt_model = db.Column(db.String(10), default='3PL')  # 3PL, 2PL, 1PL
    calibration_threshold = db.Column(db.Integer, default=5)  # Минимум ответов для калибровки
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domains = db.relationship('SpecialtyDomain', backref='specialty', lazy='dynamic')
    questions = db.relationship('Question', backref='specialty', lazy='dynamic')
    diagnostic_sessions = db.relationship('DiagnosticSession', backref='specialty', lazy='dynamic')
```

### **1.2 Модификация модели Question**
```python
class Question(db.Model):
    # ... существующие поля ...
    
    # НОВОЕ: Связь со специальностью
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False, index=True)
    
    # НОВОЕ: Статус калибровки
    is_calibrated = db.Column(db.Boolean, default=False, index=True)
    calibration_status = db.Column(db.String(20), default='uncalibrated')  # uncalibrated, calibrating, calibrated
    
    # НОВОЕ: Счетчики для калибровки
    response_count = db.Column(db.Integer, default=0)  # Количество ответов
    correct_count = db.Column(db.Integer, default=0)   # Количество правильных ответов
    
    # НОВОЕ: Временные IRT параметры (до калибровки)
    temp_difficulty = db.Column(db.Float, nullable=True)  # Временная сложность
    temp_discrimination = db.Column(db.Float, nullable=True)  # Временная дискриминация
    temp_guessing = db.Column(db.Float, default=0.2)  # Временный параметр угадывания
```

### **1.3 Модификация модели IRTParameters**
```python
class IRTParameters(db.Model):
    # ... существующие поля ...
    
    # НОВОЕ: Связь со специальностью
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False, index=True)
    
    # НОВОЕ: Статус калибровки
    calibration_status = db.Column(db.String(20), default='calibrated')  # calibrated, provisional, outdated
    
    # НОВОЕ: Качество калибровки
    calibration_quality = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
    sample_size = db.Column(db.Integer, nullable=True)  # Размер выборки для калибровки
```

### **1.4 Модификация модели DiagnosticSession**
```python
class DiagnosticSession(db.Model):
    # ... существующие поля ...
    
    # НОВОЕ: Связь со специальностью
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False, index=True)
    
    # НОВОЕ: Режим диагностики
    assessment_mode = db.Column(db.String(20), default='assessment')  # assessment, learning
    
    # НОВОЕ: Тип сессии
    session_type = db.Column(db.String(30), default='diagnostic')  # diagnostic, pilot, calibration
    
    # НОВОЕ: Статус результатов
    results_generated = db.Column(db.Boolean, default=False)
    percentile_rank = db.Column(db.Float, nullable=True)  # Процентильный ранг
    category_scores = db.Column(db.Text, nullable=True)  # JSON с оценками по категориям
```

### **1.5 Новая модель SpecialtyDomain**
```python
class SpecialtyDomain(db.Model):
    """Домены для каждой специальности"""
    __tablename__ = 'specialty_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False)
    domain_code = db.Column(db.String(20), nullable=False)  # 'PHARMACOLOGY', 'CARDIOLOGY'
    domain_name = db.Column(db.String(100), nullable=False)
    domain_name_en = db.Column(db.String(100), nullable=False)
    domain_name_nl = db.Column(db.String(100), nullable=False)
    
    # Веса и приоритеты
    weight_percentage = db.Column(db.Float, nullable=False)
    is_critical = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=False)  # THEORETICAL, CLINICAL, etc.
    
    # Статистика
    question_count = db.Column(db.Integer, default=0)
    calibrated_count = db.Column(db.Integer, default=0)
    
    # Relationships
    questions = db.relationship('Question', backref='specialty_domain', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('specialty_id', 'domain_code', name='unique_specialty_domain'),
        db.Index('idx_specialty_domain', 'specialty_id', 'domain_code'),
    )
```

## 🎯 **2. РЕЖИМЫ РАБОТЫ**

### **2.1 Assessment Mode (Диагностический режим)**
```python
class AssessmentMode:
    """Чистая диагностика знаний"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
        self.irt_engine = IRTEngine()
        self.adaptive_selector = AdaptiveQuestionSelector()
    
    def start_diagnostic_session(self, user_id: int) -> DiagnosticSession:
        """Начать диагностическую сессию"""
        session = DiagnosticSession(
            user_id=user_id,
            specialty_id=self.specialty_id,
            assessment_mode='assessment',
            session_type='diagnostic'
        )
        return session
    
    def select_next_question(self, session: DiagnosticSession) -> Question:
        """Выбрать следующий вопрос для диагностики"""
        # Используем только калиброванные вопросы
        calibrated_questions = Question.query.filter_by(
            specialty_id=self.specialty_id,
            is_calibrated=True
        ).all()
        
        return self.adaptive_selector.select_optimal_question(
            session, calibrated_questions
        )
    
    def process_response(self, session: DiagnosticSession, question_id: int, 
                        is_correct: bool, response_time: float):
        """Обработать ответ пользователя"""
        # Обновляем IRT способность
        ability = self.irt_engine.update_ability_estimate(
            session, question_id, is_correct
        )
        
        # Сохраняем ответ
        response = DiagnosticResponse(
            session_id=session.id,
            question_id=question_id,
            is_correct=is_correct,
            response_time=response_time,
            ability_before=session.current_ability,
            ability_after=ability
        )
        
        return response
    
    def generate_results(self, session: DiagnosticSession) -> dict:
        """Генерировать результаты диагностики"""
        return {
            'theta_score': session.current_ability,
            'standard_error': session.ability_se,
            'percentile_rank': self._calculate_percentile_rank(session),
            'category_scores': self._calculate_category_scores(session),
            'total_questions': session.questions_answered,
            'accuracy': session.get_accuracy(),
            'diagnostic_complete': True
        }
```

### **2.2 Learning Mode (Режим обучения)**
```python
class LearningMode:
    """Режим обучения БЕЗ влияния на диагностику"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
    
    def get_learning_questions(self, domain: str = None, limit: int = 10) -> List[Question]:
        """Получить вопросы для обучения"""
        query = Question.query.filter_by(specialty_id=self.specialty_id)
        
        if domain:
            query = query.filter_by(domain=domain)
        
        return query.limit(limit).all()
    
    def show_question_with_explanation(self, question_id: int) -> dict:
        """Показать вопрос с объяснением"""
        question = Question.query.get(question_id)
        
        return {
            'question': question,
            'show_explanation': True,
            'learning_mode': True,
            'no_scoring': True  # Не влияет на диагностику
        }
```

## 📊 **3. СИСТЕМА РЕЗУЛЬТАТОВ**

### **3.1 Diagnostic Results**
```python
class DiagnosticResults:
    """Результаты диагностики БЕЗ обучающих компонентов"""
    
    def __init__(self, session: DiagnosticSession):
        self.session = session
        self.specialty = session.specialty
    
    def generate_comprehensive_report(self) -> dict:
        """Генерировать полный отчет диагностики"""
        return {
            # Основные метрики
            'theta_score': self.session.current_ability,
            'standard_error': self.session.ability_se,
            'confidence_interval': self._calculate_confidence_interval(),
            
            # Процентильный ранг
            'percentile_rank': self._calculate_percentile_rank(),
            'peer_comparison': self._get_peer_comparison(),
            
            # Статистика по категориям
            'category_scores': self._calculate_category_scores(),
            'domain_analysis': self._analyze_domain_performance(),
            
            # Метрики качества
            'total_questions': self.session.questions_answered,
            'accuracy': self.session.get_accuracy(),
            'response_time_avg': self._calculate_avg_response_time(),
            
            # Временные метки
            'session_duration': self._calculate_session_duration(),
            'completed_at': self.session.completed_at,
            
            # НЕ ВКЛЮЧАЕМ:
            # - learning_plan
            # - recommendations
            # - study_suggestions
            # - improvement_areas
        }
    
    def _calculate_percentile_rank(self) -> float:
        """Рассчитать процентильный ранг среди коллег"""
        # Сравниваем с другими пользователями той же специальности
        peer_sessions = DiagnosticSession.query.filter_by(
            specialty_id=self.session.specialty_id,
            status='completed'
        ).all()
        
        peer_abilities = [s.current_ability for s in peer_sessions]
        user_ability = self.session.current_ability
        
        # Рассчитываем процентиль
        below_count = sum(1 for ability in peer_abilities if ability < user_ability)
        percentile = (below_count / len(peer_abilities)) * 100 if peer_abilities else 50
        
        return round(percentile, 1)
    
    def _calculate_category_scores(self) -> dict:
        """Рассчитать оценки по категориям"""
        responses = self.session.responses.all()
        category_scores = {}
        
        for response in responses:
            question = response.question
            domain = question.specialty_domain
            
            if domain.category not in category_scores:
                category_scores[domain.category] = {
                    'correct': 0,
                    'total': 0,
                    'accuracy': 0.0
                }
            
            category_scores[domain.category]['total'] += 1
            if response.is_correct:
                category_scores[domain.category]['correct'] += 1
        
        # Рассчитываем точность
        for category in category_scores:
            total = category_scores[category]['total']
            correct = category_scores[category]['correct']
            category_scores[category]['accuracy'] = (correct / total) * 100 if total > 0 else 0
        
        return category_scores
```

## 🚀 **4. ПИЛОТИРОВАНИЕ ДЛЯ ВРАЧЕЙ**

### **4.1 Pilot Data Collection**
```python
class PilotDataCollector:
    """Сбор данных для калибровки вопросов врачей"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
        self.min_responses_per_question = 5
    
    def start_pilot_session(self, user_id: int) -> DiagnosticSession:
        """Начать пилотную сессию"""
        session = DiagnosticSession(
            user_id=user_id,
            specialty_id=self.specialty_id,
            session_type='pilot',
            assessment_mode='assessment'
        )
        return session
    
    def select_pilot_questions(self, session: DiagnosticSession) -> List[Question]:
        """Выбрать вопросы для пилотирования"""
        # Приоритет некалиброванным вопросам
        uncalibrated = Question.query.filter_by(
            specialty_id=self.specialty_id,
            is_calibrated=False
        ).order_by(Question.response_count.asc()).limit(20).all()
        
        return uncalibrated
    
    def collect_response_data(self, question_id: int, is_correct: bool, 
                            response_time: float, user_ability: float):
        """Собрать данные ответа для калибровки"""
        question = Question.query.get(question_id)
        
        # Обновляем счетчики
        question.response_count += 1
        if is_correct:
            question.correct_count += 1
        
        # Сохраняем данные для калибровки
        pilot_response = PilotResponse(
            question_id=question_id,
            user_ability=user_ability,
            is_correct=is_correct,
            response_time=response_time,
            specialty_id=self.specialty_id
        )
        
        db.session.add(pilot_response)
        db.session.commit()
        
        # Проверяем, готов ли вопрос к калибровке
        if question.response_count >= self.min_responses_per_question:
            self._trigger_calibration(question_id)
    
    def _trigger_calibration(self, question_id: int):
        """Запустить калибровку вопроса"""
        from utils.irt_calibration import IRTCalibrationService
        
        calibration_service = IRTCalibrationService()
        irt_params = calibration_service.calibrate_question_from_responses(question_id)
        
        if irt_params:
            # Обновляем статус вопроса
            question = Question.query.get(question_id)
            question.is_calibrated = True
            question.calibration_status = 'calibrated'
            db.session.commit()
```

### **4.2 Pilot Strategy**
```python
class PilotStrategy:
    """Стратегия привлечения врачей для пилотирования"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
    
    def get_pilot_incentives(self) -> dict:
        """Получить стимулы для участия в пилотировании"""
        return {
            'early_access': 'Ранний доступ к диагностической системе',
            'free_assessment': 'Бесплатная диагностика знаний',
            'peer_comparison': 'Сравнение с коллегами',
            'certificate': 'Сертификат участника пилотирования',
            'feedback': 'Персональная обратная связь по результатам'
        }
    
    def track_pilot_progress(self) -> dict:
        """Отслеживать прогресс пилотирования"""
        total_questions = Question.query.filter_by(specialty_id=self.specialty_id).count()
        calibrated_questions = Question.query.filter_by(
            specialty_id=self.specialty_id,
            is_calibrated=True
        ).count()
        
        return {
            'total_questions': total_questions,
            'calibrated_questions': calibrated_questions,
            'calibration_percentage': (calibrated_questions / total_questions) * 100 if total_questions > 0 else 0,
            'ready_for_adaptive': calibrated_questions >= 50  # Минимум для адаптивного тестирования
        }
```

## 🔧 **5. МИГРАЦИЯ И РАЗВЕРТЫВАНИЕ**

### **5.1 Миграция данных**
```python
def migrate_to_specialty_system():
    """Миграция существующих данных к системе специальностей"""
    
    # 1. Создать специальность "Стоматолог"
    dentist_specialty = Specialty(
        code='DENTIST',
        name='Стоматолог',
        name_en='Dentist',
        name_nl='Tandarts',
        is_active=True,
        is_calibrated=True,
        total_questions=410,
        calibrated_questions=410
    )
    db.session.add(dentist_specialty)
    
    # 2. Создать специальность "Врач общей практики"
    gp_specialty = Specialty(
        code='GP',
        name='Врач общей практики',
        name_en='General Practitioner',
        name_nl='Huisarts',
        is_active=True,
        is_calibrated=False,
        total_questions=0,
        calibrated_questions=0
    )
    db.session.add(gp_specialty)
    
    # 3. Обновить существующие вопросы
    existing_questions = Question.query.all()
    for question in existing_questions:
        question.specialty_id = dentist_specialty.id
        question.is_calibrated = True
        question.calibration_status = 'calibrated'
    
    # 4. Обновить IRT параметры
    existing_irt_params = IRTParameters.query.all()
    for params in existing_irt_params:
        params.specialty_id = dentist_specialty.id
    
    db.session.commit()
```

### **5.2 API Endpoints**
```python
# Новые маршруты для специальностей
@diagnostic_bp.route('/specialties')
def get_specialties():
    """Получить список доступных специальностей"""
    specialties = Specialty.query.filter_by(is_active=True).all()
    return jsonify([s.to_dict() for s in specialties])

@diagnostic_bp.route('/specialties/<int:specialty_id>/start-assessment')
@login_required
def start_assessment(specialty_id):
    """Начать диагностическую сессию для специальности"""
    specialty = Specialty.query.get_or_404(specialty_id)
    
    if not specialty.is_calibrated:
        return jsonify({'error': 'Specialty not yet calibrated'}), 400
    
    assessment_mode = AssessmentMode(specialty_id)
    session = assessment_mode.start_diagnostic_session(current_user.id)
    
    return jsonify({
        'session_id': session.id,
        'specialty': specialty.to_dict(),
        'mode': 'assessment'
    })

@diagnostic_bp.route('/specialties/<int:specialty_id>/start-pilot')
@login_required
def start_pilot(specialty_id):
    """Начать пилотную сессию для калибровки"""
    specialty = Specialty.query.get_or_404(specialty_id)
    
    if specialty.is_calibrated:
        return jsonify({'error': 'Specialty already calibrated'}), 400
    
    pilot_collector = PilotDataCollector(specialty_id)
    session = pilot_collector.start_pilot_session(current_user.id)
    
    return jsonify({
        'session_id': session.id,
        'specialty': specialty.to_dict(),
        'mode': 'pilot'
    })
```

## ✅ **6. ПЛАН РЕАЛИЗАЦИИ**

### **Этап 1: Модели данных (1-2 дня)**
1. Создать модель `Specialty`
2. Создать модель `SpecialtyDomain`
3. Модифицировать `Question`, `IRTParameters`, `DiagnosticSession`
4. Создать миграции

### **Этап 2: Режимы работы (2-3 дня)**
1. Реализовать `AssessmentMode`
2. Реализовать `LearningMode`
3. Создать `DiagnosticResults`
4. Обновить IRT Engine для работы со специальностями

### **Этап 3: API и маршруты (1-2 дня)**
1. Создать новые API endpoints
2. Обновить существующие маршруты
3. Добавить валидацию специальностей

### **Этап 4: Пилотирование (1 день)**
1. Реализовать `PilotDataCollector`
2. Создать `PilotStrategy`
3. Добавить отслеживание прогресса калибровки

### **Этап 5: Тестирование и развертывание (1-2 дня)**
1. Миграция существующих данных
2. Тестирование системы
3. Развертывание на продакшене

**Общее время: 6-10 дней**
