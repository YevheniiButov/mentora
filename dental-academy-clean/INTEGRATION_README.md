# Интеграция Frontend с Flask Backend для диагностической системы

## Обзор

Полная интеграция современного frontend интерфейса с Flask backend для системы диагностического тестирования BI-toets с использованием IRT (Item Response Theory).

## Архитектура системы

### Backend (Flask)
```
routes/
├── diagnostic_routes.py      # Основные маршруты диагностики
├── auth_routes.py           # Аутентификация
└── ...

utils/
├── rate_limiter.py          # Rate limiting
├── session_validator.py     # Валидация сессий
├── irt_engine.py           # IRT движок
└── ...

models/
├── DiagnosticSession       # Модель сессии диагностики
├── Question               # Модель вопроса
├── IRTParameters         # IRT параметры
└── ...
```

### Frontend (Modern JavaScript)
```
static/
├── css/
│   ├── assessment.css           # Основные стили
│   ├── mobile-diagnostic.css    # Мобильная оптимизация
│   └── premium-diagnostic.css   # Premium UX/UI
├── js/
│   ├── diagnostic.js            # Основной модуль
│   ├── micro-interactions.js    # Micro-interactions
│   └── premium-diagnostic.js    # Premium функциональность
└── ...
```

## API Endpoints

### 1. Запуск диагностики
```http
POST /big-diagnostic/start
Content-Type: application/json
X-CSRFToken: <token>

{
  "session_type": "adaptive_diagnostic",
  "test_length": null,
  "time_limit": 120
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 123,
  "question": {
    "id": 42,
    "text": "Een 35-jarige patiënt presenteert zich met...",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "image_url": null,
    "domain": "Therapeutische stomatologie",
    "difficulty_estimate": 0.8
  },
  "session_info": {
    "questions_answered": 0,
    "correct_answers": 0,
    "current_ability": 0.0,
    "confidence_interval": [0.0, 1.0],
    "domain_abilities": {},
    "estimated_questions_remaining": 50
  },
  "progress": 0,
  "total_questions_estimate": 50
}
```

### 2. Получение следующего вопроса
```http
POST /big-diagnostic/next-question
Content-Type: application/json
X-CSRFToken: <token>

{
  "session_id": 123,
  "previous_answer": 2,
  "response_time": 45
}
```

**Response:**
```json
{
  "success": true,
  "question": {
    "id": 43,
    "text": "Bij een patiënt met parodontitis...",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "domain": "Chirurgische stomatologie",
    "difficulty_estimate": 0.6
  },
  "session_info": {
    "questions_answered": 1,
    "correct_answers": 1,
    "current_ability": 0.45,
    "confidence_interval": [0.2, 0.7],
    "domain_abilities": {
      "therapeutisch": 0.6,
      "chirurgisch": 0.3,
      "prothetisch": 0.5
    },
    "estimated_questions_remaining": 25
  },
  "progress": 65
}
```

### 3. Отправка ответа
```http
POST /big-diagnostic/submit-answer
Content-Type: application/json
X-CSRFToken: <token>

{
  "session_id": 123,
  "question_id": 42,
  "selected_answer": 2,
  "response_time": 45
}
```

**Response:**
```json
{
  "success": true,
  "is_correct": true,
  "correct_answer": 2,
  "explanation": "Правильный ответ: Option 3. Это объяснение...",
  "session_updated": {
    "questions_answered": 1,
    "correct_answers": 1,
    "current_ability": 0.45
  },
  "session_completed": false
}
```

### 4. Результаты диагностики
```http
GET /big-diagnostic/results/123
```

**Response:**
```json
{
  "success": true,
  "session": {
    "id": 123,
    "status": "completed",
    "questions_answered": 15,
    "correct_answers": 12,
    "current_ability": 0.78,
    "started_at": "2024-12-01T10:00:00Z",
    "completed_at": "2024-12-01T10:45:00Z"
  },
  "results": {
    "final_ability": 0.78,
    "confidence_interval": [0.65, 0.91],
    "domain_breakdown": {
      "therapeutisch": 0.85,
      "chirurgisch": 0.72,
      "prothetisch": 0.68
    },
    "readiness_score": 0.78,
    "recommendations": ["Рекомендуется дополнительная подготовка в области..."]
  }
}
```

## Безопасность

### CSRF Protection
```python
@require_csrf
def start_diagnostic():
    # CSRF token validation
    csrf_token = request.headers.get('X-CSRFToken')
    if not session_validator.validate_csrf(csrf_token):
        raise BadRequest('Invalid CSRF token')
```

### Rate Limiting
```python
@rate_limit(requests_per_minute=10)
def start_diagnostic():
    # Rate limiting applied
    user_id = current_user.id if current_user.is_authenticated else request.remote_addr
    if not rate_limiter.check_rate_limit(user_id, 10):
        raise TooManyRequests('Rate limit exceeded')
```

### Session Validation
```python
@validate_session
def get_next_question():
    # Session validation
    diagnostic_session = g.current_session
    if not session_validator.validate_session(diagnostic_session):
        raise BadRequest('Invalid or expired session')
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid data, CSRF failure)
- `401` - Unauthorized (authentication required)
- `404` - Not Found (session/question not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "success": false,
  "error": "Error message description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "additional error details"
  }
}
```

## Frontend Integration

### JavaScript API Client
```javascript
class DiagnosticAPI {
  constructor(csrfToken) {
    this.csrfToken = csrfToken;
    this.baseURL = '/big-diagnostic';
  }

  async startSession(sessionType = 'adaptive_diagnostic') {
    const response = await fetch(`${this.baseURL}/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({
        session_type: sessionType,
        test_length: null,
        time_limit: 120
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async getNextQuestion(sessionId, previousAnswer = null, responseTime = 0) {
    const response = await fetch(`${this.baseURL}/next-question`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({
        session_id: sessionId,
        previous_answer: previousAnswer,
        response_time: responseTime
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async submitAnswer(sessionId, questionId, selectedAnswer, responseTime = 0) {
    const response = await fetch(`${this.baseURL}/submit-answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.csrfToken
      },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        selected_answer: selectedAnswer,
        response_time: responseTime
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async getResults(sessionId) {
    const response = await fetch(`${this.baseURL}/results/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}
```

### State Management
```javascript
class DiagnosticState {
  constructor() {
    this.sessionId = null;
    this.currentQuestion = null;
    this.selectedAnswer = null;
    this.sessionInfo = null;
    this.isLoading = false;
    this.error = null;
  }

  updateSessionInfo(sessionInfo) {
    this.sessionInfo = sessionInfo;
    this.triggerEvent('sessionInfoUpdated', sessionInfo);
  }

  setCurrentQuestion(question) {
    this.currentQuestion = question;
    this.selectedAnswer = null;
    this.triggerEvent('questionUpdated', question);
  }

  setSelectedAnswer(answer) {
    this.selectedAnswer = answer;
    this.triggerEvent('answerSelected', answer);
  }

  setLoading(loading) {
    this.isLoading = loading;
    this.triggerEvent('loadingChanged', loading);
  }

  setError(error) {
    this.error = error;
    this.triggerEvent('errorOccurred', error);
  }

  triggerEvent(eventName, data) {
    const event = new CustomEvent(eventName, { detail: data });
    document.dispatchEvent(event);
  }
}
```

## Premium UX/UI Features

### Glassmorphism Effects
```css
.question-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border-radius: 20px;
}
```

### Micro-interactions
```javascript
class MicroInteractions {
  static celebrateCorrectAnswer() {
    const button = document.querySelector('.option-btn.selected');
    button.classList.add('celebrate');
    this.createParticles(button);
  }

  static showConfidenceLevel(confidence) {
    const progressBar = document.querySelector('.confidence-indicator');
    progressBar.style.setProperty('--confidence', `${confidence * 100}%`);
  }
}
```

### Sound Effects
```javascript
class SoundManager {
  constructor() {
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.sounds = {};
    this.enabled = true;
  }

  createTone(frequency, duration, type = 'sine') {
    return () => {
      if (!this.enabled) return;
      
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
      oscillator.type = type;
      
      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + duration);
    };
  }
}
```

## Мобильная оптимизация

### Touch-friendly элементы
```css
.option-btn, .nav-btn {
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
```

### Swipe gestures
```javascript
class TouchHandler {
  constructor(container) {
    this.threshold = 100;
    this.bindEvents();
  }

  handleTouchEnd(e) {
    const diffX = this.startX - this.currentX;
    if (Math.abs(diffX) > this.threshold) {
      if (diffX > 0) {
        this.triggerNext();
      } else {
        this.triggerPrevious();
      }
    }
  }
}
```

### Haptic feedback
```javascript
class HapticFeedback {
  trigger(type = 'light') {
    if ('vibrate' in navigator) {
      const patterns = {
        light: [10],
        medium: [20],
        heavy: [30]
      };
      navigator.vibrate(patterns[type]);
    }
  }
}
```

## Тестирование

### Unit Tests
```python
def test_start_diagnostic_session():
    response = client.post('/big-diagnostic/start', 
                          json={'session_type': 'adaptive_diagnostic'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'session_id' in data
    assert 'question' in data
```

### Integration Tests
```python
def test_diagnostic_flow():
    # Start session
    response = client.post('/big-diagnostic/start', 
                          json={'session_type': 'adaptive_diagnostic'})
    session_id = response.get_json()['session_id']
    
    # Get next question
    response = client.post('/big-diagnostic/next-question',
                          json={'session_id': session_id})
    assert response.status_code == 200
    
    # Submit answer
    response = client.post('/big-diagnostic/submit-answer',
                          json={'session_id': session_id, 'question_id': 1, 'selected_answer': 2})
    assert response.status_code == 200
```

### Frontend Tests
```javascript
describe('DiagnosticAPI', () => {
  it('should start diagnostic session', async () => {
    const api = new DiagnosticAPI('test-token');
    const result = await api.startSession();
    expect(result.success).toBe(true);
    expect(result.session_id).toBeDefined();
  });
});
```

## Мониторинг и логирование

### Backend Logging
```python
import logging

logger = logging.getLogger(__name__)

@diagnostic_bp.route('/start', methods=['POST'])
def start_diagnostic():
    try:
        # ... implementation
        logger.info(f"Started diagnostic session {session_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error starting diagnostic: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to start session'}), 500
```

### Frontend Analytics
```javascript
class Analytics {
  static trackEvent(eventName, data) {
    if (window.gtag) {
      gtag('event', eventName, data);
    }
  }

  static trackDiagnosticStart(sessionId) {
    this.trackEvent('diagnostic_start', { session_id: sessionId });
  }

  static trackQuestionAnswered(sessionId, questionId, isCorrect) {
    this.trackEvent('question_answered', {
      session_id: sessionId,
      question_id: questionId,
      is_correct: isCorrect
    });
  }
}
```

## Развертывание

### Environment Variables
```bash
# Flask configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Session configuration
SESSION_TIMEOUT=7200
CSRF_TOKEN_EXPIRY=3600
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Производительность

### Backend Optimizations
- Database connection pooling
- Redis caching for session data
- Async processing for heavy computations
- CDN for static assets

### Frontend Optimizations
- Code splitting and lazy loading
- Service worker for offline support
- Image optimization and WebP support
- Bundle size optimization

## Безопасность

### Data Protection
- All sensitive data encrypted at rest
- HTTPS enforcement
- Input validation and sanitization
- SQL injection prevention

### Access Control
- Role-based access control (RBAC)
- Session timeout and automatic logout
- IP-based access restrictions
- Audit logging for all actions

---

*Документация обновлена: Декабрь 2024* 