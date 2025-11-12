# Email: Добро пожаловать в Карту Обучения MENTORA

## Анализ Карты Обучения

### Основные функции:

1. **Individual Plan (Индивидуальный План)** - Персональные ежедневные задания, адаптированные под уровень пользователя
2. **IRT (Адаптивное Тестирование)** - Умная система оценки знаний с 3 режимами:
   - Quick Test (30 вопросов) - быстрая проверка
   - Full Test (60 вопросов) - полная оценка
   - Learning Mode (30 вопросов с объяснениями) - режим обучения
3. **Premium** - Расширенные возможности для премиум пользователей
4. **Games** - Интерактивные обучающие игры
5. **Progress** - Детальная статистика и отслеживание прогресса
6. **Planner** - Планировщик обучения с расписанием
7. **Archive** - История всех завершенных активностей (тексты, термины, тесты, виртуальные пациенты)

---

## Email Template (HTML)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Откройте свою Карту Обучения</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa; line-height: 1.6;">
    
    <!-- Email Container -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f7fa; padding: 40px 20px;">
        <tr>
            <td align="center">
                
                <!-- Main Content Card -->
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08); overflow: hidden; max-width: 600px;">
                    
                    <!-- Header with Gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); padding: 40px 40px 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                                🗺️ Добро пожаловать в Карту Обучения!
                            </h1>
                            <p style="margin: 16px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 18px; font-weight: 400;">
                                Ваш персональный центр подготовки к экзамену
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Welcome Message -->
                            <p style="margin: 0 0 30px 0; color: #1a202c; font-size: 16px; line-height: 1.7;">
                                Привет, {{ user_name }}! 👋
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #64748b; font-size: 16px; line-height: 1.7;">
                                Поздравляем с регистрацией в <strong style="color: #3ECDC1;">MENTORA</strong>! 
                                Теперь у вас есть доступ к мощной платформе подготовки, которая поможет вам 
                                эффективно готовиться к экзамену BI-toets.
                            </p>
                            
                            <!-- CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0 40px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{{ learning_map_url }}" 
                                           style="display: inline-block; background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 16px rgba(62, 205, 193, 0.3); transition: transform 0.2s;">
                                            🚀 Открыть Карту Обучения
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Features Section -->
                            <div style="border-top: 2px solid #e2e8f0; padding-top: 30px; margin-top: 30px;">
                                
                                <h2 style="margin: 0 0 24px 0; color: #1a202c; font-size: 24px; font-weight: 700;">
                                    ✨ Что вас ждет:
                                </h2>
                                
                                <!-- Feature 1: Individual Plan -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 4px solid #3ECDC1;">
                                    <tr>
                                        <td width="60" valign="top" style="padding-right: 16px;">
                                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                                👤
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <h3 style="margin: 0 0 8px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                                Индивидуальный План
                                            </h3>
                                            <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                                Ежедневные персональные задания, адаптированные под ваш уровень. 
                                                Система автоматически создает план на каждый день с учетом вашего прогресса.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 2: IRT Testing -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 4px solid #667eea;">
                                    <tr>
                                        <td width="60" valign="top" style="padding-right: 16px;">
                                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                                ⚡
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <h3 style="margin: 0 0 8px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                                Адаптивное Тестирование (IRT)
                                            </h3>
                                            <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                                <strong>Quick Test</strong> (30 вопросов) для быстрой проверки знаний, 
                                                <strong>Full Test</strong> (60 вопросов) для полной оценки, 
                                                или <strong>Learning Mode</strong> с объяснениями после каждого вопроса.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 3: Games -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 4px solid #f093fb;">
                                    <tr>
                                        <td width="60" valign="top" style="padding-right: 16px;">
                                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                                🎮
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <h3 style="margin: 0 0 8px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                                Интерактивные Игры
                                            </h3>
                                            <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                                Изучайте материал в игровой форме! Интерактивные модули делают обучение 
                                                увлекательным и эффективным.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 4: Progress & Archive -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 4px solid #4facfe;">
                                    <tr>
                                        <td width="60" valign="top" style="padding-right: 16px;">
                                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                                📊
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <h3 style="margin: 0 0 8px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                                Прогресс & Архив
                                            </h3>
                                            <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                                Отслеживайте свой прогресс в реальном времени и просматривайте историю 
                                                всех завершенных активностей: английские тексты, термины, тесты и виртуальных пациентов.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Feature 5: Planner -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px; background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 4px solid #10b981;">
                                    <tr>
                                        <td width="60" valign="top" style="padding-right: 16px;">
                                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                                📅
                                            </div>
                                        </td>
                                        <td valign="top">
                                            <h3 style="margin: 0 0 8px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                                Планировщик Обучения
                                            </h3>
                                            <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                                Создавайте расписание занятий, планируйте повторения и управляйте 
                                                своим учебным процессом эффективно.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                            </div>
                            
                            <!-- Benefits Section -->
                            <div style="background: linear-gradient(135deg, rgba(62, 205, 193, 0.1) 0%, rgba(50, 163, 154, 0.1) 100%); border-radius: 16px; padding: 24px; margin: 30px 0;">
                                <h3 style="margin: 0 0 16px 0; color: #1a202c; font-size: 20px; font-weight: 700;">
                                    🎯 Почему это работает:
                                </h3>
                                <ul style="margin: 0; padding-left: 24px; color: #64748b; font-size: 15px; line-height: 1.8;">
                                    <li style="margin-bottom: 8px;"><strong style="color: #3ECDC1;">Персонализация</strong> - система адаптируется под ваш уровень знаний</li>
                                    <li style="margin-bottom: 8px;"><strong style="color: #3ECDC1;">Адаптивность</strong> - IRT технология подбирает вопросы оптимальной сложности</li>
                                    <li style="margin-bottom: 8px;"><strong style="color: #3ECDC1;">Системность</strong> - ежедневные задания помогают поддерживать регулярность</li>
                                    <li style="margin-bottom: 8px;"><strong style="color: #3ECDC1;">Отслеживание</strong> - видите свой прогресс и слабые места в реальном времени</li>
                                </ul>
                            </div>
                            
                            <!-- Final CTA -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 40px 0 20px 0;">
                                <tr>
                                    <td align="center" style="padding: 30px 0; background: #f8fafc; border-radius: 16px;">
                                        <p style="margin: 0 0 20px 0; color: #1a202c; font-size: 18px; font-weight: 600;">
                                            Готовы начать? 🚀
                                        </p>
                                        <a href="{{ learning_map_url }}" 
                                           style="display: inline-block; background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); color: #ffffff; text-decoration: none; padding: 16px 48px; border-radius: 12px; font-weight: 600; font-size: 18px; box-shadow: 0 8px 24px rgba(62, 205, 193, 0.35);">
                                            Открыть Карту Обучения →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Help Section -->
                            <div style="border-top: 1px solid #e2e8f0; padding-top: 24px; margin-top: 30px; text-align: center;">
                                <p style="margin: 0 0 12px 0; color: #94a3b8; font-size: 14px;">
                                    💡 <strong style="color: #64748b;">Совет:</strong> При первом входе в Карту Обучения вы увидите 
                                    интерактивный тур, который поможет вам быстро освоиться с платформой.
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 14px;">
                                    Нужна помощь? Напишите нам на 
                                    <a href="mailto:support@mentora.nl" style="color: #3ECDC1; text-decoration: none;">support@mentora.nl</a>
                                </p>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f8fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 12px 0; color: #64748b; font-size: 14px;">
                                <strong style="color: #1a202c;">MENTORA</strong> - Ваш путь к успешной сдаче экзамена
                            </p>
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                © 2025 MENTORA. Все права защищены.
                            </p>
                            <p style="margin: 16px 0 0 0; color: #94a3b8; font-size: 12px;">
                                <a href="{{ unsubscribe_url }}" style="color: #94a3b8; text-decoration: underline;">Отписаться от рассылки</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>
```

---

## Email Template (Текстовая версия для альтернативного формата)

```
ДОБРО ПОЖАЛОВАТЬ В КАРТУ ОБУЧЕНИЯ MENTORA
==========================================

Привет, {{ user_name }}! 👋

Поздравляем с регистрацией в MENTORA! Теперь у вас есть доступ к мощной 
платформе подготовки, которая поможет вам эффективно готовиться к экзамену BI-toets.

🚀 ОТКРЫТЬ КАРТУ ОБУЧЕНИЯ: {{ learning_map_url }}

✨ ЧТО ВАС ЖДЕТ:

👤 ИНДИВИДУАЛЬНЫЙ ПЛАН
Ежедневные персональные задания, адаптированные под ваш уровень. 
Система автоматически создает план на каждый день с учетом вашего прогресса.

⚡ АДАПТИВНОЕ ТЕСТИРОВАНИЕ (IRT)
- Quick Test (30 вопросов) - быстрая проверка знаний
- Full Test (60 вопросов) - полная оценка по всем доменам
- Learning Mode (30 вопросов с объяснениями) - режим обучения

🎮 ИНТЕРАКТИВНЫЕ ИГРЫ
Изучайте материал в игровой форме! Интерактивные модули делают обучение 
увлекательным и эффективным.

📊 ПРОГРЕСС & АРХИВ
Отслеживайте свой прогресс в реальном времени и просматривайте историю 
всех завершенных активностей: английские тексты, термины, тесты и виртуальных пациентов.

📅 ПЛАНИРОВЩИК ОБУЧЕНИЯ
Создавайте расписание занятий, планируйте повторения и управляйте 
своим учебным процессом эффективно.

🎯 ПОЧЕМУ ЭТО РАБОТАЕТ:

• Персонализация - система адаптируется под ваш уровень знаний
• Адаптивность - IRT технология подбирает вопросы оптимальной сложности
• Системность - ежедневные задания помогают поддерживать регулярность
• Отслеживание - видите свой прогресс и слабые места в реальном времени

🚀 ГОТОВЫ НАЧАТЬ?
Откройте Карту Обучения: {{ learning_map_url }}

💡 СОВЕТ: При первом входе в Карту Обучения вы увидите интерактивный тур, 
который поможет вам быстро освоиться с платформой.

Нужна помощь? Напишите нам на support@mentora.nl

---
© 2025 MENTORA. Все права защищены.
Отписаться: {{ unsubscribe_url }}
```

---

## Ключевые элементы дизайна:

1. **Визуальная иерархия:**
   - Градиентный заголовок с брендовым цветом #3ECDC1
   - Четкое разделение секций
   - Цветные акценты для каждой функции

2. **Структура:**
   - Приветствие → Описание → CTA → Функции → Преимущества → Финальный CTA → Помощь

3. **Психологические триггеры:**
   - Эмодзи для визуальной привлекательности
   - Конкретные цифры (30, 60 вопросов)
   - Акцент на персонализации и адаптивности
   - Социальное доказательство (система используется)

4. **Призывы к действию:**
   - Два CTA кнопки (в начале и в конце)
   - Яркие цвета и градиенты
   - Четкий текст действия

5. **Мобильная адаптивность:**
   - Табличная верстка для совместимости с email-клиентами
   - Максимальная ширина 600px
   - Адаптивные отступы

