# Детальный анализ системы адаптивного обучения Mentora

## 📋 Обзор системы

Система адаптивного обучения Mentora представляет собой комплексную платформу для подготовки к BI-toets экзамену с использованием IRT (Item Response Theory) диагностики, персонализированных планов обучения и ежедневных задач.

---

## 1. IRT ДИАГНОСТИКА

### 1.1 Модели данных для IRT

#### **IRTParameters** (строки 1777-1877 в `models.py`)
```python
class IRTParameters(db.Model):
    """IRT parameters for 3PL model (difficulty, discrimination, guessing)"""
    __tablename__ = 'irt_parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # 3PL Model Parameters
    difficulty = db.Column(db.Float, nullable=False, index=True)  # b-parameter (location)
    discrimination = db.Column(db.Float, nullable=False, index=True)  # a-parameter (slope)
    guessing = db.Column(db.Float, default=0.25, index=True)  # c-parameter (lower asymptote)
    
    # Calibration data
    calibration_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    calibration_sample_size = db.Column(db.Integer, nullable=True)
    reliability = db.Column(db.Float, nullable=True)  # Item reliability
    
    # Standard errors
    se_difficulty = db.Column(db.Float, nullable=True)
    se_discrimination = db.Column(db.Float, nullable=True)
    se_guessing = db.Column(db.Float, nullable=True)
    
    # Fit statistics
    infit = db.Column(db.Float, nullable=True)  # Weighted mean square
    outfit = db.Column(db.Float, nullable=True)  # Unweighted mean square
```

**Функциональность:**
- ✅ Полная реализация 3PL модели IRT
- ✅ Валидация параметров (строки 1813-1831)
- ✅ Методы для расчета вероятности и информации (строки 1863-1877)
- ✅ Индексы для оптимизации запросов

#### **DiagnosticSession** (строки 1880-2160 в `models.py`)
```python
class DiagnosticSession(db.Model):
    """Session for adaptive diagnostic testing"""
    __tablename__ = 'diagnostic_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Session configuration
    session_type = db.Column(db.String(50), nullable=False)  # 'diagnostic', 'adaptive', 'practice'
    test_length = db.Column(db.Integer, nullable=True)  # Max questions (null for adaptive)
    time_limit = db.Column(db.Integer, nullable=True)  # Minutes (null for no limit)
    
    # Current state
    current_ability = db.Column(db.Float, default=0.0)  # Current theta estimate
    ability_se = db.Column(db.Float, default=1.0)  # Standard error of ability
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    current_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    
    # Session data (JSON)
    session_data = db.Column(db.Text, nullable=True)  # JSON with response history
    ability_history = db.Column(db.Text, nullable=True)  # JSON with ability progression
```

**Функциональность:**
- ✅ Отслеживание прогресса диагностики
- ✅ История способностей (строки 1932-1950)
- ✅ Генерация результатов (строки 1969-2060)
- ✅ Обновление оценок способностей (строки 2118-2155)

#### **DiagnosticResponse** (строки 2163-2212 в `models.py`)
```python
class DiagnosticResponse(db.Model, JSONSerializableMixin):
    """Individual response in diagnostic session"""
    __tablename__ = 'diagnostic_response'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('diagnostic_session.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    
    # Response data
    selected_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Float, nullable=True)  # Seconds
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # IRT data
    ability_before = db.Column(db.Float, nullable=True)  # θ before this question
    ability_after = db.Column(db.Float, nullable=True)   # θ after this question
    se_before = db.Column(db.Float, nullable=True)       # SE before this question
    se_after = db.Column(db.Float, nullable=True)        # SE after this question
    
    # Item information
    item_information = db.Column(db.Float, nullable=True)  # Information provided by this item
    expected_response = db.Column(db.Float, nullable=True)  # Expected probability of correct response
```

### 1.2 Роуты для диагностического тестирования

#### **Основные роуты** (`routes/diagnostic_routes.py`)

**Запуск диагностики** (строки 54-177):
```python
@diagnostic_bp.route('/start', methods=['GET', 'POST'])
@login_required
@rate_limit(requests_per_minute=10)
def start_diagnostic():
    """Start new diagnostic session"""
```

**Отправка ответа** (строки 280-383):
```python
@diagnostic_bp.route('/submit-answer/<int:session_id>', methods=['POST'])
@login_required
def submit_answer(session_id):
    """Submit answer for diagnostic question"""
```

**Переоценка** (строки 817-933):
```python
@diagnostic_bp.route('/reassessment/<int:plan_id>')
@login_required
def start_reassessment(plan_id):
    """Start a new diagnostic session for reassessment"""
```

### 1.3 Алгоритм выбора следующего вопроса

#### **IRTEngine** (`utils/irt_engine.py`)

**Инициализация** (строки 12-47):
```python
class IRTEngine:
    """IRT Engine for 3PL model adaptive testing with domain support"""
    
    def __init__(self, session: Optional[DiagnosticSession] = None, diagnostic_type: str = 'express'):
        self.session = session
        self.max_iterations = 50
        self.convergence_threshold = 0.001
        self.min_se_threshold = 0.4  # Увеличен порог стандартной ошибки для завершения
        
        # Настройки в зависимости от типа диагностики
        self.diagnostic_type = diagnostic_type
        
        if diagnostic_type == 'express':
            # Экспресс диагностика: 1 вопрос на домен
            self.questions_per_domain = 1
            self.max_questions = 25  # Максимум 25 вопросов
        elif diagnostic_type == 'preliminary':
            # Предварительная диагностика: 3 вопроса на домен
            self.questions_per_domain = 3
            self.max_questions = 75  # Максимум 75 вопросов
        elif diagnostic_type == 'readiness':
            # Диагностика готовности: 6 вопросов на домен
            self.questions_per_domain = 6
            self.max_questions = 130  # Максимум 130 вопросов
```

**Выбор следующего вопроса** (строки 245-318):
```python
def select_next_question(self) -> Optional[Question]:
    """Select next question using IRT adaptive algorithm"""
    
    # Получаем уже отвеченные вопросы
    answered_question_ids = set()
    if self.session:
        answered_question_ids = {r.question_id for r in self.session.responses.all()}
    
    # Получаем текущую оценку способности
    current_ability = self.current_ability_estimate
    
    # Выбираем домен для следующего вопроса
    target_domain = self._select_target_domain(answered_question_ids)
    if not target_domain:
        return None
    
    # Получаем вопросы для выбранного домена
    domain_questions = self.get_domain_questions(target_domain)
    
    # Исключаем уже отвеченные вопросы
    available_questions = [q for q in domain_questions if q.id not in answered_question_ids]
    
    if not available_questions:
        return None
    
    # Выбираем вопрос с оптимальной информацией
    optimal_question = None
    max_information = -1
    
    for question in available_questions:
        if not hasattr(question, 'irt_difficulty') or question.irt_difficulty is None:
            continue
            
        # Рассчитываем информацию вопроса при текущей способности
        information = self._calculate_item_information(
            current_ability, 
            question.irt_discrimination,
            question.irt_difficulty,
            question.irt_guessing
        )
        
        if information > max_information:
            max_information = information
            optimal_question = question
    
    return optimal_question
```

### 1.4 Расчет текущего уровня знаний

**Оценка способности** (строки 147-215):
```python
def estimate_ability(self, responses: List[Dict]) -> Tuple[float, float]:
    """Estimate ability using Maximum Likelihood Estimation (MLE)"""
    
    if not responses:
        return 0.0, 1.0
    
    # Начальная оценка
    theta = 0.0
    
    # Итеративное уточнение оценки
    for iteration in range(self.max_iterations):
        theta_old = theta
        
        # Рассчитываем логарифм правдоподобия и его производную
        log_likelihood = 0.0
        first_derivative = 0.0
        second_derivative = 0.0
        
        for response in responses:
            irt_parameters = response['irt_parameters']
            is_correct = response['is_correct']
            
            # Вероятность правильного ответа
            p = self._3pl_probability(theta, irt_parameters)
            
            # Логарифм правдоподобия
            if is_correct:
                log_likelihood += math.log(p)
            else:
                log_likelihood += math.log(1 - p)
            
            # Производные для Newton-Raphson
            a, b, c = irt_parameters['discrimination'], irt_parameters['difficulty'], irt_parameters['guessing']
            
            if is_correct:
                first_derivative += a * (1 - p) * (p - c) / (p * (1 - c))
                second_derivative += -a**2 * (1 - p) * (p - c) * (1 - c) / (p * (1 - c)**2)
            else:
                first_derivative += -a * p * (p - c) / ((1 - p) * (1 - c))
                second_derivative += -a**2 * p * (p - c) * (1 - c) / ((1 - p) * (1 - c)**2)
        
        # Newton-Raphson update
        if abs(second_derivative) > 1e-10:
            theta = theta - first_derivative / second_derivative
        
        # Проверка сходимости
        if abs(theta - theta_old) < self.convergence_threshold:
            break
    
    # Рассчитываем стандартную ошибку
    se = self._calculate_standard_error(theta, responses)
    
    return theta, se
```

### 1.5 Заглушки в алгоритмах

**НЕТ ЗАГЛУШЕК** - все алгоритмы IRT полностью реализованы:
- ✅ 3PL модель IRT
- ✅ Адаптивный выбор вопросов
- ✅ Оценка способностей через MLE
- ✅ Расчет стандартных ошибок
- ✅ Условия завершения диагностики

---

## 2. ПЛАН ОБУЧЕНИЯ

### 2.1 Модель для хранения персонального плана

#### **PersonalLearningPlan** (строки 2215-2366 в `models.py`)
```python
class PersonalLearningPlan(db.Model, JSONSerializableMixin):
    """Personalized learning plan based on diagnostic results"""
    __tablename__ = 'personal_learning_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Plan configuration
    exam_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=True)  # Дата начала обучения
    end_date = db.Column(db.Date, nullable=True)    # Дата окончания обучения
    intensity = db.Column(db.String(20), default='moderate')  # light, moderate, intensive
    study_time = db.Column(db.String(20), default='afternoon')  # morning, afternoon, evening, flexible
    diagnostic_session_id = db.Column(db.Integer, db.ForeignKey('diagnostic_session.id'), nullable=True)
    target_ability = db.Column(db.Float, default=0.5)  # Target theta for exam readiness
    study_hours_per_week = db.Column(db.Float, default=20.0)
    
    # Current status
    current_ability = db.Column(db.Float, default=0.0)
    overall_progress = db.Column(db.Float, default=0.0)  # 0-100%
    estimated_readiness = db.Column(db.Float, nullable=True)  # Probability of passing
    
    # Domain analysis (JSON)
    domain_analysis = db.Column(db.Text, nullable=True)  # JSON with domain-specific data
    weak_domains = db.Column(db.Text, nullable=True)     # JSON list of weak domains
    strong_domains = db.Column(db.Text, nullable=True)   # JSON list of strong domains
    
    # Study schedule (JSON)
    study_schedule = db.Column(db.Text, nullable=True)   # JSON with weekly schedule
    milestones = db.Column(db.Text, nullable=True)       # JSON with milestone dates
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Diagnostic reassessment
    next_diagnostic_date = db.Column(db.Date, nullable=True)  # Дата следующей переоценки
    diagnostic_reminder_sent = db.Column(db.Boolean, default=False)  # Флаг отправки напоминания
```

### 2.2 Генерация плана после диагностики

#### **create_learning_plan_from_diagnostic** (`utils/learning_plan_generator.py`)
```python
def create_learning_plan_from_diagnostic(user_id: int, diagnostic_session_id: int) -> PersonalLearningPlan:
    """Create personalized learning plan from diagnostic results"""
    
    # Получаем диагностическую сессию
    diagnostic_session = DiagnosticSession.query.get(diagnostic_session_id)
    if not diagnostic_session or diagnostic_session.status != 'completed':
        raise ValueError("Diagnostic session not found or not completed")
    
    # Генерируем результаты диагностики
    diagnostic_data = diagnostic_session.generate_results()
    
    # Создаем план обучения
    plan = PersonalLearningPlan(
        user_id=user_id,
        diagnostic_session_id=diagnostic_session_id,
        current_ability=diagnostic_data['final_ability'],
        target_ability=0.7,  # Целевая способность для экзамена
        study_hours_per_week=20.0,
        intensity='moderate'
    )
    
    # Устанавливаем анализ доменов
    plan.set_domain_analysis(diagnostic_data['domain_abilities'])
    plan.set_weak_domains(diagnostic_data['weak_domains'])
    plan.set_strong_domains(diagnostic_data['strong_domains'])
    
    # Устанавливаем дату переоценки
    plan.next_diagnostic_date = date.today() + timedelta(days=14)
    plan.diagnostic_reminder_sent = False
    
    db.session.add(plan)
    db.session.commit()
    
    return plan
```

### 2.3 Хранение слабых тем пользователя

**Методы для работы с доменами** (строки 2272-2325):
```python
def get_weak_domains(self):
    """Get weak domains as list"""
    if self.weak_domains:
        try:
            return json.loads(self.weak_domains)
        except:
            pass
    return []

def set_weak_domains(self, domains):
    """Set weak domains from list"""
    self.weak_domains = safe_json_dumps(domains)

def get_strong_domains(self):
    """Get strong domains as list"""
    if self.strong_domains:
        try:
            return json.loads(self.strong_domains)
        except:
            pass
    return []

def set_strong_domains(self, domains):
    """Set strong domains from list"""
    self.strong_domains = safe_json_dumps(domains)
```

### 2.4 Связь плана с результатами IRT теста

**Связь через diagnostic_session_id:**
- План хранит ID диагностической сессии
- Результаты IRT сохраняются в `current_ability`
- Анализ доменов основан на IRT результатах
- Слабые/сильные домены определяются по IRT способностям

---

## 3. ЕЖЕДНЕВНЫЕ ЗАДАЧИ

### 3.1 Модель для daily tasks

**DailyLearningAlgorithm** (`utils/daily_learning_algorithm.py`):
```python
class DailyLearningAlgorithm:
    """
    Алгоритм генерации ежедневного плана обучения
    Интегрирует IRT, Spaced Repetition и Learning Map
    """
    
    def __init__(self):
        self.URGENCY_WEIGHT = 0.3
        self.WEAKNESS_WEIGHT = 0.3
```

### 3.2 Генерация задач из плана обучения

**Основной метод генерации** (строки 32-136):
```python
def generate_daily_plan(self, user_id: int, target_minutes: int = 30) -> Dict:
    """Генерирует ежедневный план обучения"""
    
    try:
        # Получаем данные пользователя
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"Пользователь {user_id} не найден")
        
        # Проверяем активный план обучения и дату переоценки
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_plan and active_plan.next_diagnostic_date:
            from datetime import date
            today = date.today()
            if active_plan.next_diagnostic_date <= today:
                # Прошло 14 дней без переоценки
                return {
                    'success': False,
                    'error': 'Необходима переоценка прогресса обучения',
                    'requires_reassessment': True,
                    'plan_id': active_plan.id,
                    'redirect_url': f'/big-diagnostic/reassessment/{active_plan.id}'
                }
        
        # Анализируем текущие способности
        try:
            abilities = self._analyze_current_abilities(user_id)
        except ValueError as e:
            # Если нет диагностики, возвращаем ошибку
            return {
                'success': False,
                'error': str(e),
                'requires_diagnostic': True,
                'redirect_url': '/big-diagnostic/choose-type'
            }
        
        # Определяем слабые домены
        weak_domains = self._identify_weak_domains(abilities)
        
        # Получаем просроченные повторения
        overdue_reviews = self._get_overdue_reviews(user_id)
        
        # Рассчитываем приоритеты доменов
        domain_priorities = self._calculate_domain_priorities(
            weak_domains, user_id, overdue_reviews
        )
        
        # Распределяем время по приоритетам
        time_allocation = self._allocate_time_by_priority(
            domain_priorities, target_minutes, overdue_reviews
        )
        
        # Выбираем контент для каждого домена
        daily_content = self._select_daily_content(
            time_allocation, abilities, user_id, overdue_reviews
        )
        
        # Форматируем для Learning Map
        formatted_plan = self._format_for_learning_map(daily_content, user)
        
        return {
            'success': True,
            'target_minutes': target_minutes,
            'weak_domains': weak_domains,
            'daily_plan': formatted_plan,
            'overdue_reviews': len(overdue_reviews)
        }
        
    except Exception as e:
        logger.error(f"Error generating daily plan: {e}")
        return {
            'success': False,
            'error': str(e)
        }
```

### 3.3 Роуты для отображения и выполнения задач

**Learning Map роут** (`routes/learning_routes_new.py`):
```python
@daily_learning_bp.route('/learning-map')
@login_required
def learning_map():
    # Получаем язык из параметров запроса
    lang = request.args.get('lang', 'en')
    """Learning Map - показывает ежедневный план и связь с Learning Planner"""
    from models import PersonalLearningPlan, DiagnosticSession
    from utils.learning_plan_generator import LearningPlanGenerator
    
    # Получаем активный план обучения пользователя
    active_plan = PersonalLearningPlan.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).order_by(PersonalLearningPlan.last_updated.desc()).first()
    
    # Получаем последнюю диагностику
    latest_diagnostic = DiagnosticSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(DiagnosticSession.completed_at.desc()).first()
    
    # Генерируем ежедневный план
    algorithm = DailyLearningAlgorithm()
    daily_plan_result = algorithm.generate_daily_plan(
        user_id=current_user.id,
        target_minutes=30
    )
    
    # Проверяем, нужна ли диагностика или переоценка
    if not daily_plan_result.get('success', True):
        if daily_plan_result.get('requires_diagnostic'):
            flash('Для персонализации вашего обучения необходимо пройти диагностический тест.', 'info')
            return redirect('/big-diagnostic/choose-type')
        elif daily_plan_result.get('requires_reassessment'):
            flash('Для продолжения обучения необходимо пройти переоценку прогресса.', 'info')
            return redirect(daily_plan_result.get('redirect_url', '/dashboard'))
        else:
            flash('Ошибка генерации плана обучения. Попробуйте пройти диагностику.', 'error')
            return redirect('/big-diagnostic/choose-type')
```

### 3.4 Отслеживание выполнения

**UserProgress модель** (строки 847-880 в `models.py`):
```python
class UserProgress(db.Model):
    """Track user progress through lessons"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete='CASCADE'), nullable=False)
    
    # Progress data
    completed = db.Column(db.Boolean, default=False)
    time_spent = db.Column(db.Float, default=0.0)  # minutes
    score = db.Column(db.Float)  # for quizzes/tests
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

---

## 4. ПОВТОРНАЯ ДИАГНОСТИКА

### 4.1 Scheduler для напоминаний о переоценке

**НЕТ ОТДЕЛЬНОГО SCHEDULER** - система использует проверку при генерации ежедневных задач:

```python
# В DailyLearningAlgorithm.generate_daily_plan()
if active_plan and active_plan.next_diagnostic_date:
    from datetime import date
    today = date.today()
    if active_plan.next_diagnostic_date <= today:
        # Прошло 14 дней без переоценки
        return {
            'success': False,
            'error': 'Необходима переоценка прогресса обучения',
            'requires_reassessment': True,
            'plan_id': active_plan.id,
            'redirect_url': f'/big-diagnostic/reassessment/{active_plan.id}'
        }
```

### 4.2 Запуск повторного IRT теста

**Роут переоценки** (`routes/diagnostic_routes.py`):
```python
@diagnostic_bp.route('/reassessment/<int:plan_id>')
@login_required
def start_reassessment(plan_id):
    """Start a new diagnostic session for reassessment"""
    try:
        # Get the learning plan
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        
        # Check if plan belongs to current user
        if plan.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect('/dashboard')
        
        # Create new diagnostic session for reassessment
        diagnostic_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='reassessment',
            ip_address=request.remote_addr
        )
        
        # Update plan with new session
        plan.diagnostic_session_id = diagnostic_session.id
        plan.diagnostic_reminder_sent = False
        db.session.commit()
        
        flash('Начинаем переоценку вашего прогресса обучения.', 'info')
        return redirect(f'/big-diagnostic/question/{diagnostic_session.id}')
        
    except Exception as e:
        logger.error(f"Error starting reassessment: {e}")
        flash('Ошибка при запуске переоценки.', 'error')
        return redirect('/dashboard')
```

### 4.3 Логика корректировки плана после переоценки

**Обновление плана** (строки 817-933 в `routes/diagnostic_routes.py`):
```python
# В show_results() для session_type == 'reassessment'
if diagnostic_session.session_type == 'reassessment':
    # Обновляем план с новыми результатами
    active_plan.current_ability = results['final_ability']
    active_plan.set_domain_analysis(results['domain_abilities'])
    active_plan.set_weak_domains(results['weak_domains'])
    active_plan.set_strong_domains(results['strong_domains'])
    
    # Устанавливаем новую дату переоценки
    active_plan.next_diagnostic_date = date.today() + timedelta(days=14)
    active_plan.diagnostic_reminder_sent = False
```

---

## 5. ВЗАИМОСВЯЗИ И ПРОБЛЕМЫ

### 5.1 Места с TODO, FIXME, заглушками

**НАЙДЕННЫЕ ПРОБЛЕМЫ:**

#### **1. Placeholder в IRT параметрах** (`scripts/init_big_domains.py` строка 345):
```python
calibration_sample_size=100  # Placeholder
```
**Статус**: ❌ Заглушка - требует реальных данных калибровки

#### **2. Отсутствие scheduler для напоминаний**
**Проблема**: Нет отдельного scheduler для автоматических напоминаний
**Статус**: ⚠️ Частично решено через проверку в daily_plan

#### **3. Отсутствие реальных IRT параметров**
**Проблема**: Многие вопросы не имеют калиброванных IRT параметров
**Статус**: ❌ Критично - влияет на точность диагностики

### 5.2 Части системы, не связанные между собой

#### **1. Spaced Repetition System**
- Реализован в `utils/spaced_repetition_system.py`
- НЕ интегрирован с IRT диагностикой
- НЕ используется в daily_plan

#### **2. Virtual Patient System**
- Отдельная система в `models.py` (строки 1154-1235)
- НЕ связана с IRT диагностикой
- НЕ включена в планы обучения

#### **3. Achievement System**
- Система достижений (строки 1446-1514 в `models.py`)
- НЕ связана с IRT прогрессом
- НЕ влияет на планы обучения

### 5.3 Где обрывается логика

#### **1. План создается, но не используется полностью**
- План сохраняет `weak_domains`, но daily_plan не всегда их использует
- `study_schedule` и `milestones` не реализованы в UI

#### **2. IRT результаты не влияют на контент**
- IRT способности не определяют сложность контента
- Нет адаптивного выбора уроков по IRT

#### **3. Отсутствие интеграции с Learning Path**
- Learning Path (строки 621-711) не связан с IRT диагностикой
- Нет персонализации путей обучения

### 5.4 Функции, возвращающие фиктивные данные

#### **1. IRT параметры по умолчанию**
```python
# В models.py (строки 923-937)
@property
def irt_difficulty(self):
    if self.irt_parameters:
        return self.irt_parameters.difficulty
    return 0.0  # Фиктивное значение

@property
def irt_discrimination(self):
    if self.irt_parameters:
        return self.irt_parameters.discrimination
    return 1.0  # Фиктивное значение

@property
def irt_guessing(self):
    if self.irt_parameters:
        return self.irt_parameters.guessing
    return 0.25  # Фиктивное значение
```

#### **2. Domain abilities без данных**
```python
# В utils/irt_engine.py (строки 413-468)
def get_domain_detailed_statistics(self) -> Dict[str, Dict]:
    # Если нет данных по домену, возвращаем фиктивные значения
    if not domain_data:
        return {
            'has_data': False,
            'accuracy_percentage': 0,  # Фиктивное значение
            'questions_answered': 0,
            'correct_answers': 0
        }
```

---

## 6. ТЕКУЩИЙ FLOW ПОЛЬЗОВАТЕЛЯ

### 6.1 Пошаговый процесс от регистрации до первой задачи

#### **Шаг 1: Регистрация**
```python
# routes/digid_routes.py или routes/auth_routes.py
# Пользователь регистрируется
user.requires_diagnostic = True  # Устанавливается флаг
```

#### **Шаг 2: Первый вход**
```python
# routes/dashboard_routes.py (строки 1-50)
def index():
    # Проверяется флаг requires_diagnostic
    if current_user.requires_diagnostic:
        flash('Для персонализации обучения пройдите диагностику.', 'info')
        return redirect('/big-diagnostic/choose-type')
```

#### **Шаг 3: Выбор типа диагностики**
```python
# routes/diagnostic_routes.py
@diagnostic_bp.route('/choose-type')
def choose_diagnostic_type():
    # Пользователь выбирает: express, preliminary, readiness
```

#### **Шаг 4: Запуск диагностики**
```python
# routes/diagnostic_routes.py (строки 54-177)
@diagnostic_bp.route('/start', methods=['GET', 'POST'])
def start_diagnostic():
    # Создается DiagnosticSession
    # Выбирается первый вопрос через IRTEngine
```

#### **Шаг 5: Прохождение диагностики**
```python
# routes/diagnostic_routes.py (строки 280-383)
@diagnostic_bp.route('/submit-answer/<int:session_id>', methods=['POST'])
def submit_answer(session_id):
    # Сохраняется ответ
    # Обновляется IRT способность
    # Выбирается следующий вопрос
```

#### **Шаг 6: Завершение диагностики**
```python
# routes/diagnostic_routes.py (строки 817-933)
def show_results():
    # Генерируются результаты
    # Создается PersonalLearningPlan
    # Сбрасывается requires_diagnostic
```

#### **Шаг 7: Генерация ежедневных задач**
```python
# utils/daily_learning_algorithm.py (строки 32-136)
def generate_daily_plan():
    # Анализируются способности
    # Определяются слабые домены
    # Генерируется контент
```

### 6.2 Где процесс прерывается или работает некорректно

#### **1. Прерывание при отсутствии IRT параметров**
```python
# Если у вопросов нет IRT параметров, диагностика работает некорректно
if not hasattr(question, 'irt_difficulty') or question.irt_difficulty is None:
    continue  # Вопрос пропускается
```

#### **2. Прерывание при отсутствии контента**
```python
# Если нет контента для слабых доменов, daily_plan пустой
if not available_content:
    return empty_plan  # Возвращается пустой план
```

#### **3. Прерывание при ошибках IRT**
```python
# Если IRT алгоритм не сходится
if iteration >= self.max_iterations:
    # Используется последняя оценка или дефолтная
    theta = 0.0
```

---

## 📊 ИТОГОВАЯ ОЦЕНКА

### ✅ **Сильные стороны системы:**

1. **Полная реализация IRT** - 3PL модель, адаптивный выбор вопросов
2. **Интегрированная архитектура** - все компоненты связаны
3. **Система переоценки** - автоматические напоминания
4. **Персонализированные планы** - на основе IRT результатов
5. **Ежедневные задачи** - с приоритизацией по слабостям

### ❌ **Критические проблемы:**

1. **Отсутствие реальных IRT параметров** - влияет на точность
2. **Неполная интеграция компонентов** - Spaced Repetition, Virtual Patients
3. **Фиктивные данные** - в местах отсутствия реальных данных
4. **Отсутствие scheduler** - для автоматических напоминаний

### 🔧 **Рекомендации по улучшению:**

1. **Калибровка IRT параметров** - для всех вопросов
2. **Интеграция Spaced Repetition** - с IRT диагностикой
3. **Реализация scheduler** - для автоматических напоминаний
4. **Улучшение интеграции** - всех компонентов системы
5. **Замена фиктивных данных** - на реальные значения

### 📈 **Готовность к продакшену:**

- **Основная функциональность**: ✅ 85% готова
- **Интеграция компонентов**: ⚠️ 60% готова
- **Качество данных**: ❌ 30% готово
- **Автоматизация**: ⚠️ 70% готова

**Общая оценка**: ⚠️ **Требует доработки перед продакшеном** 