#!/usr/bin/env python3
"""
Модификации существующих моделей для поддержки специальностей
Добавить в соответствующие классы в models.py
"""

# =============================================================================
# МОДИФИКАЦИИ ДЛЯ МОДЕЛИ Question
# =============================================================================

# Добавить в класс Question после существующих полей:

"""
# НОВЫЕ ПОЛЯ ДЛЯ СПЕЦИАЛЬНОСТЕЙ
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

# НОВОЕ: Связь с доменом специальности
specialty_domain_id = db.Column(db.Integer, db.ForeignKey('specialty_domains.id'), nullable=True, index=True)
"""

# Добавить в методы класса Question:

def get_irt_parameters(self):
    """Получить IRT параметры (калиброванные или временные)"""
    if self.is_calibrated and self.irt_parameters:
        return {
            'difficulty': self.irt_parameters.difficulty,
            'discrimination': self.irt_parameters.discrimination,
            'guessing': self.irt_parameters.guessing,
            'calibrated': True
        }
    else:
        return {
            'difficulty': self.temp_difficulty or 0.0,
            'discrimination': self.temp_discrimination or 1.0,
            'guessing': self.temp_guessing or 0.2,
            'calibrated': False
        }

def update_response_stats(self, is_correct: bool):
    """Обновить статистику ответов"""
    self.response_count += 1
    if is_correct:
        self.correct_count += 1
    
    # Проверяем, готов ли вопрос к калибровке
    if not self.is_calibrated and self.response_count >= self.specialty.calibration_threshold:
        self.calibration_status = 'ready_for_calibration'
    
    db.session.commit()

def get_accuracy(self):
    """Получить точность ответов"""
    if self.response_count == 0:
        return 0.0
    return (self.correct_count / self.response_count) * 100

# =============================================================================
# МОДИФИКАЦИИ ДЛЯ МОДЕЛИ IRTParameters
# =============================================================================

# Добавить в класс IRTParameters после существующих полей:

"""
# НОВОЕ: Связь со специальностью
specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False, index=True)

# НОВОЕ: Статус калибровки
calibration_status = db.Column(db.String(20), default='calibrated')  # calibrated, provisional, outdated

# НОВОЕ: Качество калибровки
calibration_quality = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
sample_size = db.Column(db.Integer, nullable=True)  # Размер выборки для калибровки
"""

# Добавить в методы класса IRTParameters:

def get_quality_score(self):
    """Получить численную оценку качества калибровки"""
    quality_scores = {
        'excellent': 1.0,
        'good': 0.8,
        'fair': 0.6,
        'poor': 0.4
    }
    return quality_scores.get(self.calibration_quality, 0.5)

def is_reliable(self):
    """Проверить надежность параметров"""
    return (
        self.calibration_quality in ['excellent', 'good'] and
        self.sample_size and self.sample_size >= 10 and
        self.reliability and self.reliability >= 0.7
    )

# =============================================================================
# МОДИФИКАЦИИ ДЛЯ МОДЕЛИ DiagnosticSession
# =============================================================================

# Добавить в класс DiagnosticSession после существующих полей:

"""
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
"""

# Добавить в методы класса DiagnosticSession:

def get_specialty(self):
    """Получить специальность сессии"""
    return self.specialty

def is_assessment_mode(self):
    """Проверить, является ли сессия диагностической"""
    return self.assessment_mode == 'assessment'

def is_pilot_session(self):
    """Проверить, является ли сессия пилотной"""
    return self.session_type == 'pilot'

def get_category_scores(self):
    """Получить оценки по категориям"""
    import json
    if self.category_scores:
        try:
            return json.loads(self.category_scores)
        except:
            return {}
    return {}

def set_category_scores(self, scores):
    """Установить оценки по категориям"""
    import json
    self.category_scores = json.dumps(scores)

def generate_results(self):
    """Генерировать результаты диагностики"""
    if self.status != 'completed':
        return None
    
    # Создаем запись результатов
    result = DiagnosticResult(
        session_id=self.id,
        user_id=self.user_id,
        specialty_id=self.specialty_id,
        theta_score=self.current_ability,
        standard_error=self.ability_se,
        total_questions=self.questions_answered,
        correct_answers=self.correct_answers,
        accuracy=self.get_accuracy(),
        percentile_rank=self.percentile_rank,
        category_scores=self.category_scores,
        session_duration=self.get_session_duration()
    )
    
    # Рассчитываем доверительный интервал
    from scipy import stats
    ci = stats.norm.interval(0.95, loc=self.current_ability, scale=self.ability_se)
    result.confidence_interval_lower = ci[0]
    result.confidence_interval_upper = ci[1]
    
    # Рассчитываем среднее время ответа
    responses = self.responses.all()
    if responses:
        total_time = sum(r.response_time for r in responses if r.response_time)
        result.avg_response_time = total_time / len(responses)
    
    db.session.add(result)
    self.results_generated = True
    db.session.commit()
    
    return result

def get_session_duration(self):
    """Получить длительность сессии в секундах"""
    if self.completed_at and self.started_at:
        return int((self.completed_at - self.started_at).total_seconds())
    return None

# =============================================================================
# МОДИФИКАЦИИ ДЛЯ МОДЕЛИ DiagnosticResponse
# =============================================================================

# Добавить в класс DiagnosticResponse после существующих полей:

"""
# НОВОЕ: Связь со специальностью
specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=False, index=True)

# НОВОЕ: Режим ответа
response_mode = db.Column(db.String(20), default='assessment')  # assessment, learning, pilot
"""

# Добавить в методы класса DiagnosticResponse:

def is_assessment_response(self):
    """Проверить, является ли ответ диагностическим"""
    return self.response_mode == 'assessment'

def is_pilot_response(self):
    """Проверить, является ли ответ пилотным"""
    return self.response_mode == 'pilot'

# =============================================================================
# МОДИФИКАЦИИ ДЛЯ МОДЕЛИ User
# =============================================================================

# Добавить в класс User после существующих полей:

"""
# НОВОЕ: Специальность пользователя
primary_specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id'), nullable=True, index=True)
"""

# Добавить в методы класса User:

def get_primary_specialty(self):
    """Получить основную специальность пользователя"""
    return self.primary_specialty

def get_diagnostic_history(self, specialty_id=None):
    """Получить историю диагностики"""
    query = self.diagnostic_sessions.filter_by(status='completed')
    if specialty_id:
        query = query.filter_by(specialty_id=specialty_id)
    return query.order_by(DiagnosticSession.completed_at.desc()).all()

def get_latest_diagnostic_result(self, specialty_id=None):
    """Получить последний результат диагностики"""
    sessions = self.get_diagnostic_history(specialty_id)
    if sessions:
        return sessions[0].result
    return None

def get_percentile_rank(self, specialty_id):
    """Получить процентильный ранг пользователя по специальности"""
    latest_result = self.get_latest_diagnostic_result(specialty_id)
    if latest_result:
        return latest_result.percentile_rank
    return None


