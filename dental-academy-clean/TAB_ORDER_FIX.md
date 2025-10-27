# Исправление порядка вкладок на карте обучения

**Дата:** 2025-10-26  
**Задача:** Первая вкладка должна быть "Индивидуальный план", а не "IRT"

## Изменения

### 1. Порядок вкладок в HTML (строка 2659-2697)
Изменил порядок вкладок в HTML:
- **БЫЛО:** IRT → Virtual → Individual → Games → Progress → Planner
- **СТАЛО:** Individual → IRT → Virtual → Games → Progress → Planner

### 2. Вкладка по умолчанию (строка 3328)
Изменил начальную активную вкладку:
- **БЫЛО:** `const initialTab = validTabs.includes(tabParam) ? tabParam : 'irt';`
- **СТАЛО:** `const initialTab = validTabs.includes(tabParam) ? tabParam : 'individual';`

## Файл
- `templates/learning/learning_map_modern_style.html`

## Результат

Теперь при открытии карты обучения:
1. Первая вкладка (Individual Plan) будет активна по умолчанию
2. Вкладки расположены в порядке: Individual → IRT → Virtual → Games → Progress → Planner

