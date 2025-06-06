"""
AI Manager для Dental Academy с поддержкой RAG
Обеспечивает безопасную работу с пользовательскими API ключами и интеграцию с RAG системой
"""

import os
import json
import logging
import time
import asyncio
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import openai
import httpx

from models import db, User, UserAPIKey, AIConversation
from utils.rag_system import RAGSystem


class EncryptionManager:
    """Менеджер шифрования для API ключей"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Инициализация менеджера шифрования
        
        Args:
            encryption_key: Ключ шифрования (если None, читается из переменной среды)
        """
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Генерируем или читаем ключ из переменной среды
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                # Генерируем новый ключ и сохраняем в .env
                key = Fernet.generate_key().decode()
                # В продакшене ключ должен храниться в безопасном месте
                os.environ['ENCRYPTION_KEY'] = key
                print(f"⚠️  Новый ключ шифрования: {key}")
                print("⚠️  Сохраните его в переменной среды ENCRYPTION_KEY")
            
            self.cipher = Fernet(key.encode())
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Шифрует API ключ"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Расшифровывает API ключ"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()


class AIProviderManager:
    """Менеджер для работы с различными AI провайдерами"""
    
    PROVIDERS = {
        'groq': {
            'name': 'Groq',
            'base_url': 'https://api.groq.com/openai/v1',
            'models': ['llama-3.1-8b-instant', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768'],
            'free_tokens_daily': 10000,
            'description': 'Быстрый и бесплатный AI с дневным лимитом 10k токенов'
        },
        'deepseek': {
            'name': 'DeepSeek',
            'base_url': 'https://api.deepseek.com/v1',
            'models': ['deepseek-chat', 'deepseek-coder'],
            'free_tokens_daily': 10000,
            'description': 'Умный AI с бесплатным дневным лимитом 10k токенов'
        },
        'openai': {
            'name': 'OpenAI',
            'base_url': 'https://api.openai.com/v1',
            'models': ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
            'free_tokens_daily': None,
            'description': 'Премиум AI от OpenAI (платный)'
        }
    }
    
    @classmethod
    def get_provider_info(cls, provider: str) -> Dict[str, Any]:
        """Получает информацию о провайдере"""
        return cls.PROVIDERS.get(provider, {})
    
    @classmethod
    def get_all_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Получает информацию о всех провайдерах"""
        return cls.PROVIDERS
    
    @classmethod
    def validate_provider(cls, provider: str) -> bool:
        """Проверяет, поддерживается ли провайдер"""
        return provider in cls.PROVIDERS


class AIManager:
    """Основной менеджер AI системы с поддержкой RAG"""
    
    def __init__(self):
        """Инициализация AI Manager"""
        self.encryption_manager = EncryptionManager()
        self.rag_system = RAGSystem()
        self.logger = logging.getLogger(__name__)
        
        # Системные промпты для разных языков
        self.system_prompts = {
            'en': self._get_system_prompt_en(),
            'ru': self._get_system_prompt_ru(),
            'nl': self._get_system_prompt_nl(),
            'es': self._get_system_prompt_es(),
            'pt': self._get_system_prompt_pt(),
            'tr': self._get_system_prompt_tr(),
            'uk': self._get_system_prompt_uk(),
            'fa': self._get_system_prompt_fa()
        }
    
    def _get_system_prompt_en(self) -> str:
        """Системный промпт на английском"""
        return """You are an AI assistant for Dental Academy, an educational platform for dental students.

Your role:
- Help students learn dental concepts, procedures, and theory
- Answer questions about dental anatomy, pathology, treatments
- Provide study guidance and exam preparation tips
- Explain complex dental topics in simple terms
- Use the provided context from educational materials when available

Guidelines:
- Always prioritize accuracy and educational value
- Cite sources when using provided context
- Encourage critical thinking and practical application
- Be supportive and encouraging to students
- If unsure, recommend consulting with instructors or reliable sources

Context will be provided from the course materials to help answer questions."""
    
    def _get_system_prompt_ru(self) -> str:
        """Системный промпт на русском"""
        return """Вы AI-ассистент для Dental Academy - образовательной платформы для студентов-стоматологов.

Ваша роль:
- Помогать студентам изучать стоматологические концепции, процедуры и теорию
- Отвечать на вопросы по анатомии зубов, патологии, лечению
- Предоставлять руководство по учебе и подготовке к экзаменам
- Объяснять сложные стоматологические темы простыми словами
- Использовать предоставленный контекст из учебных материалов

Рекомендации:
- Всегда приоритизируйте точность и образовательную ценность
- Ссылайтесь на источники при использовании контекста
- Поощряйте критическое мышление и практическое применение
- Будьте поддерживающими и ободряющими для студентов
- При неуверенности рекомендуйте консультацию с преподавателями

Контекст из учебных материалов будет предоставлен для ответов на вопросы."""
    
    def _get_system_prompt_nl(self) -> str:
        """Системный промпт на голландском"""
        return """Je bent een AI-assistent voor Dental Academy, een educatief platform voor tandheelkunde studenten.

Je rol:
- Help studenten bij het leren van tandheelkundige concepten, procedures en theorie
- Beantwoord vragen over tandheelkundige anatomie, pathologie, behandelingen
- Bied studiegids en examenvoorbereiding tips
- Leg complexe tandheelkundige onderwerpen uit in eenvoudige termen
- Gebruik de verstrekte context van educatief materiaal wanneer beschikbaar

Richtlijnen:
- Prioriteer altijd nauwkeurigheid en educatieve waarde
- Citeer bronnen bij gebruik van verstrekte context
- Moedig kritisch denken en praktische toepassing aan
- Wees ondersteunend en bemoedigend voor studenten
- Bij onzekerheid, adviseer overleg met instructeurs of betrouwbare bronnen

Context wordt verstrekt uit cursusmateriaal om vragen te beantwoorden."""
    
    def _get_system_prompt_es(self) -> str:
        """Системный промпт на испанском"""
        return """Eres un asistente de IA para Dental Academy, una plataforma educativa para estudiantes de odontología.

Tu rol:
- Ayudar a los estudiantes a aprender conceptos, procedimientos y teoría dental
- Responder preguntas sobre anatomía dental, patología, tratamientos
- Proporcionar orientación de estudio y consejos de preparación para exámenes
- Explicar temas dentales complejos en términos simples
- Usar el contexto proporcionado de materiales educativos cuando esté disponible

Pautas:
- Siempre prioriza la precisión y el valor educativo
- Cita fuentes al usar el contexto proporcionado
- Fomenta el pensamiento crítico y la aplicación práctica
- Sé solidario y alentador con los estudiantes
- Si no estás seguro, recomienda consultar con instructores o fuentes confiables

Se proporcionará contexto de los materiales del curso para ayudar a responder preguntas."""
    
    def _get_system_prompt_pt(self) -> str:
        """Системный промпт на португальском"""
        return """Você é um assistente de IA para a Dental Academy, uma plataforma educacional para estudantes de odontologia.

Seu papel:
- Ajudar estudantes a aprender conceitos, procedimentos e teoria odontológica
- Responder perguntas sobre anatomia dental, patologia, tratamentos
- Fornecer orientação de estudo e dicas de preparação para exames
- Explicar tópicos dentais complexos em termos simples
- Usar o contexto fornecido de materiais educacionais quando disponível

Diretrizes:
- Sempre priorize precisão e valor educacional
- Cite fontes ao usar o contexto fornecido
- Incentive pensamento crítico e aplicação prática
- Seja solidário e encorajador com os estudantes
- Se incerto, recomende consultar instrutores ou fontes confiáveis

Contexto será fornecido dos materiais do curso para ajudar a responder perguntas."""
    
    def _get_system_prompt_tr(self) -> str:
        """Системный промпт на турецком"""
        return """Dental Academy için bir AI asistanısınız, diş hekimliği öğrencileri için eğitim platformu.

Rolünüz:
- Öğrencilerin diş hekimliği kavramları, prosedürler ve teoriyi öğrenmesine yardım etmek
- Diş anatomisi, patoloji, tedaviler hakkında soruları yanıtlamak
- Çalışma rehberliği ve sınav hazırlık ipuçları sağlamak
- Karmaşık diş konularını basit terimlerle açıklamak
- Mevcut olduğunda eğitim materyallerinden sağlanan bağlamı kullanmak

Kılavuzlar:
- Her zaman doğruluk ve eğitim değerini önceliklendirin
- Sağlanan bağlamı kullanırken kaynakları belirtin
- Eleştirel düşünme ve pratik uygulamayı teşvik edin
- Öğrencilere destekleyici ve cesaret verici olun
- Emin değilseniz, eğitmenler veya güvenilir kaynaklarla danışmayı önerin

Soruları yanıtlamaya yardımcı olmak için ders materyallerinden bağlam sağlanacaktır."""
    
    def _get_system_prompt_uk(self) -> str:
        """Системный промпт на украинском"""
        return """Ви - AI-асистент для Dental Academy, освітньої платформи для студентів-стоматологів.

Ваша роль:
- Допомагати студентам вивчати стоматологічні концепції, процедури та теорію
- Відповідати на запитання з анатомії зубів, патології, лікування
- Надавати керівництво з навчання та поради з підготовки до іспитів
- Пояснювати складні стоматологічні теми простими словами
- Використовувати наданий контекст з навчальних матеріалів

Рекомендації:
- Завжди пріоритизуйте точність та освітню цінність
- Посилайтеся на джерела при використанні наданого контексту
- Заохочуйте критичне мислення та практичне застосування
- Будьте підтримуючими та ободрюючими для студентів
- При невпевненості рекомендуйте консультацію з викладачами

Контекст з навчальних матеріалів буде наданий для відповідей на запитання."""
    
    def _get_system_prompt_fa(self) -> str:
        """Системный промпт на персидском"""
        return """شما یک دستیار هوش مصنوعی برای آکادمی دندانپزشکی هستید، پلتفرمی آموزشی برای دانشجویان دندانپزشکی.

نقش شما:
- کمک به دانشجویان برای یادگیری مفاهیم، روش‌ها و تئوری دندانپزشکی
- پاسخ به سؤالات در مورد آناتومی دندان، پاتولوژی، درمان‌ها
- ارائه راهنمایی مطالعه و نکات آماده‌سازی آزمون
- توضیح موضوعات پیچیده دندانپزشکی به زبان ساده
- استفاده از زمینه ارائه‌شده از مواد آموزشی در صورت موجود بودن

دستورالعمل‌ها:
- همیشه دقت و ارزش آموزشی را اولویت قرار دهید
- هنگام استفاده از زمینه ارائه‌شده، منابع را ذکر کنید
- تفکر انتقادی و کاربرد عملی را تشویق کنید
- نسبت به دانشجویان حمایت‌گر و دلگرم‌کننده باشید
- در صورت عدم اطمینان، مشورت با مربیان یا منابع معتبر را توصیه کنید

زمینه از مواد درسی برای کمک به پاسخ سؤالات ارائه خواهد شد."""
    
    def save_api_key(self, user_id: int, provider: str, api_key: str, key_name: str = None) -> UserAPIKey:
        """
        Сохраняет зашифрованный API ключ пользователя
        
        Args:
            user_id: ID пользователя
            provider: Провайдер AI (groq, deepseek, openai)
            api_key: API ключ
            key_name: Пользовательское имя ключа
            
        Returns:
            Объект UserAPIKey
        """
        if not AIProviderManager.validate_provider(provider):
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")
        
        # Проверяем API ключ
        if not self.validate_api_key(provider, api_key):
            raise ValueError("Недействительный API ключ")
        
        # Шифруем ключ
        encrypted_key = self.encryption_manager.encrypt_api_key(api_key)
        
        # Удаляем старый ключ если есть
        old_key = db.session.query(UserAPIKey).filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        
        if old_key:
            db.session.delete(old_key)
        
        # Создаем новый ключ
        user_api_key = UserAPIKey(
            user_id=user_id,
            provider=provider,
            encrypted_api_key=encrypted_key,
            key_name=key_name or f"{provider.title()} API Key"
        )
        
        db.session.add(user_api_key)
        db.session.commit()
        
        self.logger.info(f"Сохранен API ключ для пользователя {user_id}, провайдер {provider}")
        return user_api_key
    
    def get_user_api_key(self, user_id: int, provider: str) -> Optional[str]:
        """
        Получает расшифрованный API ключ пользователя
        
        Args:
            user_id: ID пользователя
            provider: Провайдер AI
            
        Returns:
            Расшифрованный API ключ или None
        """
        user_api_key = db.session.query(UserAPIKey).filter_by(
            user_id=user_id,
            provider=provider,
            is_active=True
        ).first()
        
        if not user_api_key:
            return None
        
        # Проверяем дневной лимит для бесплатных провайдеров
        provider_info = AIProviderManager.get_provider_info(provider)
        if provider_info.get('free_tokens_daily'):
            user_api_key.reset_daily_usage_if_needed()
            if user_api_key.tokens_used_today >= provider_info['free_tokens_daily']:
                self.logger.warning(f"Превышен дневной лимит токенов для {user_id}:{provider}")
                return None
        
        try:
            return self.encryption_manager.decrypt_api_key(user_api_key.encrypted_api_key)
        except Exception as e:
            self.logger.error(f"Ошибка расшифровки API ключа: {e}")
            return None
    
    def validate_api_key(self, provider: str, api_key: str) -> bool:
        """
        Валидирует API ключ делая тестовый запрос
        
        Args:
            provider: Провайдер AI
            api_key: API ключ для проверки
            
        Returns:
            True если ключ действителен
        """
        try:
            provider_info = AIProviderManager.get_provider_info(provider)
            if not provider_info:
                return False
            
            base_url = provider_info['base_url']
            
            # Создаем клиента для тестового запроса
            client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # Тестовый запрос
            response = client.chat.completions.create(
                model=provider_info['models'][0],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Валидация API ключа провайдера {provider} неудачна: {e}")
            return False
    
    def get_user_providers(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получает список настроенных провайдеров пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список провайдеров с информацией
        """
        user_keys = db.session.query(UserAPIKey).filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        providers = []
        for key in user_keys:
            provider_info = AIProviderManager.get_provider_info(key.provider)
            key.reset_daily_usage_if_needed()
            
            providers.append({
                'provider': key.provider,
                'name': provider_info.get('name', key.provider.title()),
                'key_name': key.key_name,
                'tokens_used_today': key.tokens_used_today,
                'total_tokens_used': key.total_tokens_used,
                'daily_limit': provider_info.get('free_tokens_daily'),
                'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
                'models': provider_info.get('models', []),
                'description': provider_info.get('description', '')
            })
        
        return providers
    
    def delete_api_key(self, user_id: int, provider: str) -> bool:
        """
        Удаляет API ключ пользователя
        
        Args:
            user_id: ID пользователя
            provider: Провайдер AI
            
        Returns:
            True если ключ удален
        """
        user_api_key = db.session.query(UserAPIKey).filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        
        if user_api_key:
            db.session.delete(user_api_key)
            db.session.commit()
            self.logger.info(f"Удален API ключ для пользователя {user_id}, провайдер {provider}")
            return True
        
        return False
    
    def chat_with_rag_context(self, 
                             user_id: int,
                             message: str,
                             language: str = 'en',
                             use_rag: bool = True,
                             provider: str = None,
                             model: str = None,
                             rag_filters: Dict = None) -> Dict[str, Any]:
        """
        Основной метод для чата с AI с использованием RAG контекста
        
        Args:
            user_id: ID пользователя
            message: Сообщение пользователя
            language: Язык общения
            use_rag: Использовать RAG контекст
            provider: Предпочтительный провайдер
            model: Предпочтительная модель
            rag_filters: Фильтры для RAG поиска
            
        Returns:
            Словарь с ответом AI и метаданными
        """
        start_time = time.time()
        
        try:
            # Получаем API ключ
            if not provider:
                # Выбираем первый доступный провайдер
                user_providers = self.get_user_providers(user_id)
                if not user_providers:
                    return {
                        'success': False,
                        'error': 'Нет настроенных API ключей',
                        'error_code': 'NO_API_KEYS'
                    }
                provider = user_providers[0]['provider']
            
            api_key = self.get_user_api_key(user_id, provider)
            if not api_key:
                return {
                    'success': False,
                    'error': f'API ключ для провайдера {provider} недоступен',
                    'error_code': 'INVALID_API_KEY'
                }
            
            # Получаем информацию о провайдере
            provider_info = AIProviderManager.get_provider_info(provider)
            if not model:
                model = provider_info['models'][0]
            
            # Генерируем RAG контекст если нужно
            rag_context = None
            sources = []
            
            if use_rag:
                try:
                    rag_result = self.rag_system.generate_rag_context(
                        query=message,
                        language=language,
                        filters=rag_filters
                    )
                    rag_context = rag_result.get('context')
                    sources = rag_result.get('sources', [])
                except Exception as e:
                    self.logger.warning(f"Ошибка RAG для пользователя {user_id}: {e}")
            
            # Формируем системный промпт
            system_prompt = self.system_prompts.get(language, self.system_prompts['en'])
            
            if rag_context:
                system_prompt += f"\n\nКонтекст из учебных материалов:\n{rag_context}"
            
            # Создаем клиента AI
            client = openai.OpenAI(
                api_key=api_key,
                base_url=provider_info['base_url']
            )
            
            # Выполняем запрос к AI
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Обновляем статистику использования токенов
            user_api_key = db.session.query(UserAPIKey).filter_by(
                user_id=user_id,
                provider=provider
            ).first()
            
            if user_api_key:
                user_api_key.add_token_usage(tokens_used)
            
            # Сохраняем разговор в БД
            conversation = AIConversation(
                user_id=user_id,
                user_message=message,
                ai_response=ai_response,
                provider=provider,
                model_used=model,
                tokens_used=tokens_used,
                response_time_ms=int((time.time() - start_time) * 1000),
                rag_sources=sources if sources else None,
                context_used=rag_context,
                language=language
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            self.logger.info(f"Успешный чат для пользователя {user_id}, токены: {tokens_used}")
            
            return {
                'success': True,
                'response': ai_response,
                'tokens_used': tokens_used,
                'provider': provider,
                'model': model,
                'sources': sources,
                'has_rag_context': bool(rag_context),
                'response_time_ms': int((time.time() - start_time) * 1000),
                'conversation_id': conversation.id
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка чата для пользователя {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'CHAT_ERROR'
            }
    
    def get_conversation_history(self, user_id: int, limit: int = 20, language: str = None) -> List[Dict[str, Any]]:
        """
        Получает историю разговоров пользователя
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей
            language: Фильтр по языку
            
        Returns:
            Список разговоров
        """
        query = db.session.query(AIConversation).filter_by(user_id=user_id)
        
        if language:
            query = query.filter_by(language=language)
        
        conversations = query.order_by(
            AIConversation.created_at.desc()
        ).limit(limit).all()
        
        history = []
        for conv in conversations:
            history.append({
                'id': conv.id,
                'user_message': conv.user_message,
                'ai_response': conv.ai_response,
                'provider': conv.provider,
                'model_used': conv.model_used,
                'tokens_used': conv.tokens_used,
                'sources': conv.rag_sources,
                'has_rag_context': bool(conv.context_used),
                'language': conv.language,
                'created_at': conv.created_at.isoformat(),
                'user_rating': conv.user_rating
            })
        
        return history
    
    def rate_conversation(self, user_id: int, conversation_id: int, rating: int, feedback: str = None) -> bool:
        """
        Оценивает разговор пользователя
        
        Args:
            user_id: ID пользователя
            conversation_id: ID разговора
            rating: Оценка (1-5)
            feedback: Текстовый отзыв
            
        Returns:
            True если оценка сохранена
        """
        if not 1 <= rating <= 5:
            return False
        
        conversation = db.session.query(AIConversation).filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        
        if not conversation:
            return False
        
        conversation.user_rating = rating
        if feedback:
            conversation.user_feedback = feedback
        
        db.session.commit()
        return True
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Получает статистику использования AI пользователем
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь со статистикой
        """
        try:
            # Общая статистика разговоров
            total_conversations = db.session.query(AIConversation).filter_by(user_id=user_id).count()
            total_tokens = db.session.query(db.func.sum(AIConversation.tokens_used)).filter_by(user_id=user_id).scalar() or 0
            
            # Статистика по провайдерам
            provider_stats = db.session.query(
                AIConversation.provider,
                db.func.count(AIConversation.id).label('count'),
                db.func.sum(AIConversation.tokens_used).label('tokens')
            ).filter_by(user_id=user_id).group_by(AIConversation.provider).all()
            
            # Средняя оценка
            avg_rating = db.session.query(db.func.avg(AIConversation.user_rating)).filter(
                AIConversation.user_id == user_id,
                AIConversation.user_rating.isnot(None)
            ).scalar()
            
            # Статистика по языкам
            language_stats = db.session.query(
                AIConversation.language,
                db.func.count(AIConversation.id).label('count')
            ).filter_by(user_id=user_id).group_by(AIConversation.language).all()
            
            return {
                'total_conversations': total_conversations,
                'total_tokens_used': int(total_tokens),
                'average_rating': float(avg_rating) if avg_rating else None,
                'provider_statistics': [
                    {
                        'provider': stat.provider,
                        'conversations': stat.count,
                        'tokens_used': int(stat.tokens or 0)
                    }
                    for stat in provider_stats
                ],
                'language_statistics': [
                    {
                        'language': stat.language,
                        'conversations': stat.count
                    }
                    for stat in language_stats
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики для пользователя {user_id}: {e}")
            return {} 