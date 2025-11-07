import json

with open('scripts/160.json', 'r', encoding='utf-8') as f:
    questions_data = json.load(f)

print(f"✅ JSON валидный!")
print(f"📊 Количество вопросов: {len(questions_data)}")

first_question = questions_data[0]
last_question = questions_data[-1]

print(f"🔍 Первый вопрос ID: {first_question['id']}")
print(f"🔍 Последний вопрос ID: {last_question['id']}")

required_fields = ['id', 'text', 'options', 'correct_answer_text', 'explanation', 'domain', 'irt_params']

print(f"\n📝 ПРОВЕРКА СТРУКТУРЫ ПЕРВЫХ 3 ВОПРОСОВ:")

for i in range(min(3, len(questions_data))):
    question = questions_data[i]
    question_id = question.get('id', f'unknown_{i+1}')
    print(f"\n--- Вопрос {question_id} ---")
    for field in required_fields:
        if field in question:
            if field == 'options':
                options_count = len(question[field])
                print(f"  ✅ {field}: {options_count} вариантов")
                for j, option in enumerate(question[field][:2]):
                    print(f"      {j+1}. {option[:50]}...")
            elif field == 'irt_params':
                irt = question[field]
                print(f"  ✅ {field}: difficulty={irt.get('difficulty')}, discrimination={irt.get('discrimination')}")
            elif field == 'text':
                text_preview = question[field][:100].replace('\n', ' ')
                print(f"  ✅ {field}: {text_preview}...")
            else:
                print(f"  ✅ {field}: OK")
        else:
            print(f"  ❌ {field}: ОТСУТСТВУЕТ")
    correct_answer = question.get('correct_answer_text', '')
    options = question.get('options', [])
    if correct_answer in options:
        correct_index = options.index(correct_answer)
        print(f"  ✅ Правильный ответ найден: индекс {correct_index}")
    else:
        print(f"  ❌ Правильный ответ НЕ найден в вариантах")
        print(f"      Искомый: {correct_answer[:50]}...")
        print(f"      Варианты: {[opt[:30] for opt in options]}")

print(f"\n📈 СТАТИСТИКА ПО ДОМЕНАМ:")
domains = {}
for question in questions_data:
    domain = question.get('domain', 'UNKNOWN')
    domains[domain] = domains.get(domain, 0) + 1
for domain, count in sorted(domains.items()):
    print(f"   {domain}: {count} вопросов")
total_domains = len(domains)
expected_domains = ['THER', 'SURG', 'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 'ETHIEK', 'ANATOMIE', 'FYSIOLOGIE', 'PATHOLOGIE', 'MICROBIOLOGIE', 'MATERIAALKUNDE', 'RADIOLOGIE', 'ALGEMENE']
print(f"\n🎯 Всего доменов найдено: {total_domains}")
print(f"🎯 Ожидаемых доменов: {len(expected_domains)}")
missing_domains = set(expected_domains) - set(domains.keys())
if missing_domains:
    print(f"⚠️ Отсутствующие домены: {missing_domains}")
else:
    print(f"✅ Все ожидаемые домены присутствуют!")
print(f"\n🔍 ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ:")
question_ids = [q.get('id') for q in questions_data]
unique_ids = set(question_ids)
print(f"   Уникальных ID: {len(unique_ids)} из {len(question_ids)}")
if len(unique_ids) != len(question_ids):
    print(f"   ❌ Найдены дублирующие ID!")
else:
    print(f"   ✅ Все ID уникальны")
difficulties = []
for question in questions_data:
    irt_params = question.get('irt_params', {})
    difficulty = irt_params.get('difficulty')
    if difficulty is not None:
        difficulties.append(difficulty)
if difficulties:
    min_diff = min(difficulties)
    max_diff = max(difficulties)
    avg_diff = sum(difficulties) / len(difficulties)
    print(f"   IRT Difficulty: min={min_diff:.2f}, max={max_diff:.2f}, avg={avg_diff:.2f}")
else:
    print(f"   ❌ IRT параметры не найдены")
print(f"\n🎯 ВЕРДИКТ: Файл готов к импорту!" if len(unique_ids) == len(question_ids) and difficulties else "⚠️ Есть проблемы, требующие внимания") 