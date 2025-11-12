# Email: Вернитесь в Карту Обучения MENTORA (для неактивных пользователей)

## Стратегия для неактивных пользователей:

**Ключевые отличия от welcome email:**
- Более мотивирующий тон
- Акцент на том, что они упускают
- Напоминание о целях (подготовка к экзамену)
- Показ ценности платформы
- Элементы срочности (но мягкие)
- Возможность показать их прошлый прогресс (если был)

---

## Email Template (HTML) - Реактивация

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вернитесь к обучению</title>
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
                                👋 Мы скучаем по вам!
                            </h1>
                            <p style="margin: 16px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 18px; font-weight: 400;">
                                Ваша Карта Обучения ждет вас
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Personal Greeting -->
                            <p style="margin: 0 0 20px 0; color: #1a202c; font-size: 18px; font-weight: 600; line-height: 1.7;">
                                Привет, {{ user_name }}!
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #64748b; font-size: 16px; line-height: 1.7;">
                                Мы заметили, что вы давно не заходили в <strong style="color: #3ECDC1;">Карту Обучения MENTORA</strong>. 
                                Возможно, вы были заняты, но мы хотим напомнить: ваша подготовка к экзамену BI-toets продолжается, 
                                и мы здесь, чтобы помочь вам достичь цели! 🎯
                            </p>
                            
                            <!-- Progress Reminder (if exists) -->
                            {% if user_has_progress %}
                            <div style="background: linear-gradient(135deg, rgba(62, 205, 193, 0.1) 0%, rgba(50, 163, 154, 0.1) 100%); border-radius: 16px; padding: 24px; margin: 24px 0; border-left: 4px solid #3ECDC1;">
                                <p style="margin: 0 0 12px 0; color: #1a202c; font-size: 16px; font-weight: 600;">
                                    📈 Ваш прогресс:
                                </p>
                                <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6;">
                                    Вы уже начали свой путь! У вас есть {{ completed_tasks_count }} завершенных заданий. 
                                    Продолжайте двигаться вперед - каждый день приближает вас к успеху.
                                </p>
                            </div>
                            {% endif %}
                            
                            <!-- What You're Missing -->
                            <div style="background: #fff7ed; border-radius: 16px; padding: 24px; margin: 24px 0; border: 2px solid #fbbf24;">
                                <h3 style="margin: 0 0 16px 0; color: #92400e; font-size: 20px; font-weight: 700;">
                                    ⚡ Что вы упускаете:
                                </h3>
                                <ul style="margin: 0; padding-left: 24px; color: #78350f; font-size: 15px; line-height: 1.8;">
                                    <li style="margin-bottom: 10px;">Ежедневные персональные задания, которые помогают поддерживать регулярность</li>
                                    <li style="margin-bottom: 10px;">Новые адаптивные тесты для проверки знаний</li>
                                    <li style="margin-bottom: 10px;">Обновления в вашем прогрессе и статистике</li>
                                    <li style="margin-bottom: 0;">Доступ к архиву всех ваших активностей</li>
                                </ul>
                            </div>
                            
                            <!-- Main CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0 40px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{{ learning_map_url }}" 
                                           style="display: inline-block; background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); color: #ffffff; text-decoration: none; padding: 18px 48px; border-radius: 12px; font-weight: 600; font-size: 18px; box-shadow: 0 4px 16px rgba(62, 205, 193, 0.3); transition: transform 0.2s;">
                                            🔄 Вернуться к обучению
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Quick Reminder of Features -->
                            <div style="border-top: 2px solid #e2e8f0; padding-top: 30px; margin-top: 30px;">
                                
                                <h2 style="margin: 0 0 24px 0; color: #1a202c; font-size: 22px; font-weight: 700;">
                                    💡 Напоминание: что доступно в Карте Обучения
                                </h2>
                                
                                <!-- Feature Grid -->
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <!-- Feature 1 -->
                                        <td width="50%" valign="top" style="padding-right: 12px; padding-bottom: 20px;">
                                            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; height: 100%; border-top: 3px solid #3ECDC1;">
                                                <div style="font-size: 32px; margin-bottom: 12px;">👤</div>
                                                <h4 style="margin: 0 0 8px 0; color: #1a202c; font-size: 16px; font-weight: 600;">
                                                    Индивидуальный План
                                                </h4>
                                                <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.5;">
                                                    Ежедневные задания, созданные специально для вас
                                                </p>
                                            </div>
                                        </td>
                                        <!-- Feature 2 -->
                                        <td width="50%" valign="top" style="padding-left: 12px; padding-bottom: 20px;">
                                            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; height: 100%; border-top: 3px solid #667eea;">
                                                <div style="font-size: 32px; margin-bottom: 12px;">⚡</div>
                                                <h4 style="margin: 0 0 8px 0; color: #1a202c; font-size: 16px; font-weight: 600;">
                                                    IRT Тестирование
                                                </h4>
                                                <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.5;">
                                                    Quick Test, Full Test или Learning Mode
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <!-- Feature 3 -->
                                        <td width="50%" valign="top" style="padding-right: 12px; padding-bottom: 20px;">
                                            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; height: 100%; border-top: 3px solid #f093fb;">
                                                <div style="font-size: 32px; margin-bottom: 12px;">🎮</div>
                                                <h4 style="margin: 0 0 8px 0; color: #1a202c; font-size: 16px; font-weight: 600;">
                                                    Игры
                                                </h4>
                                                <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.5;">
                                                    Интерактивное обучение в игровой форме
                                                </p>
                                            </div>
                                        </td>
                                        <!-- Feature 4 -->
                                        <td width="50%" valign="top" style="padding-left: 12px; padding-bottom: 20px;">
                                            <div style="background: #f8fafc; border-radius: 12px; padding: 20px; height: 100%; border-top: 3px solid #4facfe;">
                                                <div style="font-size: 32px; margin-bottom: 12px;">📊</div>
                                                <h4 style="margin: 0 0 8px 0; color: #1a202c; font-size: 16px; font-weight: 600;">
                                                    Прогресс
                                                </h4>
                                                <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.5;">
                                                    Отслеживайте свой рост и достижения
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                            </div>
                            
                            <!-- Motivation Section -->
                            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); border-radius: 16px; padding: 28px; margin: 30px 0; text-align: center;">
                                <h3 style="margin: 0 0 16px 0; color: #1a202c; font-size: 20px; font-weight: 700;">
                                    🎯 Помните о своей цели
                                </h3>
                                <p style="margin: 0 0 20px 0; color: #64748b; font-size: 16px; line-height: 1.7;">
                                    Успешная сдача экзамена BI-toets требует регулярной практики. 
                                    Даже <strong style="color: #3ECDC1;">15-20 минут в день</strong> могут значительно улучшить ваши результаты.
                                </p>
                                <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.7; font-style: italic;">
                                    "Путь в тысячу миль начинается с одного шага" - вернитесь сегодня и сделайте этот шаг! 💪
                                </p>
                            </div>
                            
                            <!-- Secondary CTA -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0 20px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{{ learning_map_url }}" 
                                           style="display: inline-block; background: linear-gradient(135deg, #3ECDC1 0%, #32A39A 100%); color: #ffffff; text-decoration: none; padding: 16px 48px; border-radius: 12px; font-weight: 600; font-size: 18px; box-shadow: 0 8px 24px rgba(62, 205, 193, 0.35);">
                                            Открыть Карту Обучения →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Help & Support -->
                            <div style="border-top: 1px solid #e2e8f0; padding-top: 24px; margin-top: 30px; text-align: center;">
                                <p style="margin: 0 0 12px 0; color: #94a3b8; font-size: 14px;">
                                    Возникли вопросы или нужна помощь? Мы всегда готовы помочь!
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 14px;">
                                    Напишите нам на 
                                    <a href="mailto:support@mentora.nl" style="color: #3ECDC1; text-decoration: none; font-weight: 500;">support@mentora.nl</a>
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

## Email Template (Текстовая версия) - Реактивация

```
МЫ СКУЧАЕМ ПО ВАМ! 👋
=====================

Привет, {{ user_name }}!

Мы заметили, что вы давно не заходили в Карту Обучения MENTORA. 
Возможно, вы были заняты, но мы хотим напомнить: ваша подготовка к экзамену 
BI-toets продолжается, и мы здесь, чтобы помочь вам достичь цели! 🎯

{% if user_has_progress %}
📈 ВАШ ПРОГРЕСС:
Вы уже начали свой путь! У вас есть {{ completed_tasks_count }} завершенных 
заданий. Продолжайте двигаться вперед - каждый день приближает вас к успеху.
{% endif %}

⚡ ЧТО ВЫ УПУСКАЕТЕ:

• Ежедневные персональные задания, которые помогают поддерживать регулярность
• Новые адаптивные тесты для проверки знаний
• Обновления в вашем прогрессе и статистике
• Доступ к архиву всех ваших активностей

🔄 ВЕРНУТЬСЯ К ОБУЧЕНИЮ: {{ learning_map_url }}

💡 НАПОМИНАНИЕ: ЧТО ДОСТУПНО В КАРТЕ ОБУЧЕНИЯ

👤 ИНДИВИДУАЛЬНЫЙ ПЛАН
Ежедневные задания, созданные специально для вас

⚡ IRT ТЕСТИРОВАНИЕ
Quick Test, Full Test или Learning Mode

🎮 ИГРЫ
Интерактивное обучение в игровой форме

📊 ПРОГРЕСС
Отслеживайте свой рост и достижения

📅 ПЛАНИРОВЩИК
Создавайте расписание и управляйте обучением

🗄️ АРХИВ
История всех ваших активностей

🎯 ПОМНИТЕ О СВОЕЙ ЦЕЛИ

Успешная сдача экзамена BI-toets требует регулярной практики. 
Даже 15-20 минут в день могут значительно улучшить ваши результаты.

"Путь в тысячу миль начинается с одного шага" - вернитесь сегодня 
и сделайте этот шаг! 💪

🔄 ОТКРЫТЬ КАРТУ ОБУЧЕНИЯ: {{ learning_map_url }}

---
Возникли вопросы? support@mentora.nl
© 2025 MENTORA. Отписаться: {{ unsubscribe_url }}
```

---

## Ключевые отличия от Welcome Email:

### 1. **Тон и подход:**
   - ❌ Welcome: "Добро пожаловать!"
   - ✅ Reactivation: "Мы скучаем по вам!" (более личный, дружелюбный)

### 2. **Мотивация:**
   - ❌ Welcome: Описание функций
   - ✅ Reactivation: "Что вы упускаете" + напоминание о цели

### 3. **Прогресс:**
   - ❌ Welcome: Нет упоминания прогресса
   - ✅ Reactivation: Показ прошлого прогресса (если был) для мотивации

### 4. **Срочность:**
   - ❌ Welcome: Нет элементов срочности
   - ✅ Reactivation: Мягкое напоминание о важности регулярности

### 5. **Цитата:**
   - ✅ Reactivation: Добавлена мотивирующая цитата для вдохновения

### 6. **CTA:**
   - ❌ Welcome: "Открыть Карту Обучения"
   - ✅ Reactivation: "Вернуться к обучению" (более подходящий призыв)

### 7. **Визуальные акценты:**
   - ✅ Reactivation: Желтый блок "Что вы упускаете" для привлечения внимания
   - ✅ Reactivation: Синий блок с мотивацией и цитатой

### 8. **Структура:**
   - Более компактные карточки функций (2x2 grid вместо полных описаний)
   - Акцент на быстром напоминании, а не на полном объяснении

---

## Рекомендации по использованию:

1. **Сегментация:**
   - Отправлять пользователям, которые не заходили 7+ дней
   - Можно добавить условие: если у пользователя есть прогресс - показать его

2. **Персонализация:**
   - `{{ user_name }}` - имя пользователя
   - `{{ user_has_progress }}` - есть ли у пользователя завершенные задания
   - `{{ completed_tasks_count }}` - количество завершенных заданий
   - `{{ learning_map_url }}` - прямая ссылка на карту обучения

3. **Частота отправки:**
   - Первое письмо: через 7 дней неактивности
   - Второе письмо: через 14 дней (если не отписались)
   - Третье письмо: через 30 дней (последнее напоминание)

4. **A/B тестирование:**
   - Вариант A: Акцент на упущенных возможностях
   - Вариант B: Акцент на прогрессе и достижениях
   - Вариант C: Акцент на цели (экзамен)

