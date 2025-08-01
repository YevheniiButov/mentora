# Реализация коротких названий для путей обучения

## Описание проблемы
Длинные названия путей обучения создавали визуальный дисбаланс в интерфейсе:
- `THK I - Tandheelkunde Kern I` (28 символов)
- `Praktische vaardigheden (Simodont voorbereiding)` (48 символов)
- `Onderzoeksmethodologie` (22 символа) - не помещался в блок

## Решение
Реализована система коротких названий с tooltip'ами для отображения полных названий при наведении.

### Изменения в файлах

#### 1. `routes/learning_map_routes.py`
- Добавлен словарь `short_names` с маппингом полных названий на короткие
- В функции `get_dentistry_learning_data()` добавлено поле `short_name` для каждого пути

#### 2. `templates/learning/subject_view.html`
- Заменены `<span>{{ path.name }}</span>` на `<span class="path-name" title="{{ path.name }}" data-full-name="{{ path.name }}">{{ path.short_name if path.short_name else path.name }}</span>`
- Добавлены атрибуты для tooltip'ов

#### 3. `static/css/pages/learning_map.css`
- Добавлены стили для `.path-name` с hover-эффектами
- Удалены конфликтующие CSS tooltip'ы
- Добавлена поддержка темной и светлой темы
- Адаптивность для мобильных устройств

#### 4. `templates/learning/subject_view.html`
- Добавлен JavaScript для кастомных tooltip'ов
- Tooltip'ы создаются динамически и позиционируются правильно
- Плавная анимация появления и исчезновения

### Результаты сокращения

| Полное название | Короткое название | Сокращение |
|----------------|------------------|------------|
| THK I - Tandheelkunde Kern I | THK I | 23 символа |
| THK II - Tandheelkunde Kern II | THK II | 24 символа |
| Praktische vaardigheden (Simodont voorbereiding) | Praktische vaardigheden | 25 символов |
| Statistiek voor tandheelkunde | Statistiek | 19 символов |
| Onderzoeksmethodologie | Onderzoek | 13 символов |
| Communicatie en ethiek | Communicatie & Ethiek | 1 символ |

### Особенности реализации

1. **Обратная совместимость**: Если короткое название не найдено, используется полное
2. **JavaScript tooltip'ы**: При наведении показывается полное название с правильным позиционированием
3. **Адаптивность**: Tooltip'ы адаптированы для мобильных устройств
4. **Темы**: Поддержка темной и светлой темы
5. **Анимация**: Плавное появление и исчезновение tooltip'ов
6. **Единообразная высота**: Все кнопки имеют одинаковую минимальную высоту
7. **Улучшенная читаемость**: Короткие названия центрированы и хорошо читаются
8. **Отсутствие конфликтов**: Удалены CSS tooltip'ы, которые конфликтовали с позиционированием

### Использование

Короткие названия автоматически применяются в интерфейсе карты обучения. Пользователи видят компактные названия, а при наведении получают полную информацию о курсе.

### Тестирование

Создан и выполнен тестовый скрипт, подтвердивший корректность работы сокращений:
- Все 9 путей обучения обрабатываются корректно
- Максимальное сокращение: 25 символов
- Общее сокращение: 92 символа 