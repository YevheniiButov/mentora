# utils/content_loader.py
import json
import os
import logging
from pathlib import Path

class ContentLoader:
    def __init__(self):
        self.learning_cards = {}
        self.tests = {}
        self._loaded = False
        self.cards_base_path = 'cards'
        self.topic_folder_mapping = {
            'caries': ['Caries', 'Fundamentals and Pathogenesis of Caries'],
            'periodontic': ['Periodontics', 'Periodontal Disease'],  
            'saliva': ['Saliva', 'Salivary Glands'],
            'statistic': ['Statistics', 'Dental Statistics'],
            # Добавьте другие соответствия папок и названий модулей
        }
    
    def load_content(self):
        """Загружает контент из JSON файлов по структуре папок"""
        if self._loaded:
            return
            
        try:
            cards_path = Path(self.cards_base_path)
            if not cards_path.exists():
                print(f"WARNING: Cards directory not found: {cards_path}")
                print(f"Current working directory: {os.getcwd()}")
                print(f"Expected path: {cards_path.absolute()}")
                return
            
            print(f"Loading content from: {cards_path.absolute()}")
            
            # Проходим по всем подпапкам в cards/
            for topic_folder in cards_path.iterdir():
                if topic_folder.is_dir():
                    topic_name = topic_folder.name.lower()
                    print(f"\n📁 Processing folder: {topic_name}")
                    
                    # Загружаем learning_cards.json из папки темы
                    cards_file = topic_folder / 'learning_cards.json'
                    if cards_file.exists():
                        try:
                            with open(cards_file, 'r', encoding='utf-8') as f:
                                cards_data = json.load(f)
                                
                            # Группируем карточки по module_title
                            for card in cards_data:
                                module_title = card.get('module_title', topic_name.title())
                                if module_title not in self.learning_cards:
                                    self.learning_cards[module_title] = []
                                self.learning_cards[module_title].append(card)
                            
                            print(f"  ✅ Loaded {len(cards_data)} learning cards")
                            
                            # Показываем уникальные module_title для отладки
                            unique_modules = set(card.get('module_title', 'No title') for card in cards_data)
                            print(f"  📚 Module titles found: {list(unique_modules)}")
                            
                        except Exception as e:
                            print(f"  ❌ Error loading cards from {cards_file}: {e}")
                    else:
                        print(f"  ⚠️  No learning_cards.json found in {topic_folder}")
                    
                    # Загружаем tests.json из папки темы
                    tests_file = topic_folder / 'tests.json'
                    if tests_file.exists():
                        try:
                            with open(tests_file, 'r', encoding='utf-8') as f:
                                tests_data = json.load(f)
                                
                            # Группируем тесты по module_title
                            for test in tests_data:
                                module_title = test.get('module_title', topic_name.title())
                                if module_title not in self.tests:
                                    self.tests[module_title] = []
                                self.tests[module_title].append(test)
                            
                            print(f"  ✅ Loaded {len(tests_data)} tests")
                            
                            # Показываем уникальные module_title для отладки
                            unique_modules = set(test.get('module_title', 'No title') for test in tests_data)
                            print(f"  🧪 Test module titles: {list(unique_modules)}")
                            
                        except Exception as e:
                            print(f"  ❌ Error loading tests from {tests_file}: {e}")
                    else:
                        print(f"  ⚠️  No tests.json found in {topic_folder}")
            
            self._loaded = True
            print(f"\n🎉 ContentLoader: Successfully loaded content!")
            print(f"📊 Total learning card modules: {len(self.learning_cards)}")
            print(f"📊 Total test modules: {len(self.tests)}")
            print(f"📊 All modules with content: {sorted(set(list(self.learning_cards.keys()) + list(self.tests.keys())))}")
                        
        except Exception as e:
            logging.error(f"Error loading content: {e}")
            print(f"❌ Error loading content: {e}")
    
    def get_all_topic_folders(self):
        """Возвращает список всех папок с темами"""
        cards_path = Path(self.cards_base_path)
        if not cards_path.exists():
            return []
        
        return [folder.name for folder in cards_path.iterdir() if folder.is_dir()]
    
    def get_module_subtopics(self, module_title):
        """Возвращает список подтем для модуля на основе точного или частичного совпадения"""
        if not self._loaded:
            self.load_content()
            
        subtopics = set()
        module_title_lower = module_title.lower()
        
        # Ищем точные совпадения и частичные совпадения
        for cards_module_title in self.learning_cards.keys():
            cards_title_lower = cards_module_title.lower()
            if (module_title_lower == cards_title_lower or 
                module_title_lower in cards_title_lower or 
                cards_title_lower in module_title_lower or
                # Проверяем ключевые слова
                any(word in cards_title_lower for word in module_title_lower.split())):
                subtopics.add(cards_module_title)
        
        for tests_module_title in self.tests.keys():
            tests_title_lower = tests_module_title.lower()
            if (module_title_lower == tests_title_lower or 
                module_title_lower in tests_title_lower or 
                tests_title_lower in module_title_lower or
                # Проверяем ключевые слова
                any(word in tests_title_lower for word in module_title_lower.split())):
                subtopics.add(tests_module_title)
        
        result = sorted(list(subtopics))
        print(f"🔍 Module '{module_title}' matched subtopics: {result}")
        return result
    
    def get_subtopic_content(self, subtopic_title):
        """Возвращает смешанный контент (карточки + тесты) для подтемы"""
        if not self._loaded:
            self.load_content()
            
        content = []
        
        # Добавляем карточки
        if subtopic_title in self.learning_cards:
            for card in self.learning_cards[subtopic_title]:
                content.append({
                    'type': 'learning_card',
                    'data': card
                })
        
        # Добавляем тесты
        if subtopic_title in self.tests:
            for test in self.tests[subtopic_title]:
                content.append({
                    'type': 'test',
                    'data': test
                })
        
        # Сортируем по порядку (если есть поле order) или по типу
        try:
            # Сначала сортируем по типу (карточки перед тестами), потом по порядку
            content.sort(key=lambda x: (
                0 if x['type'] == 'learning_card' else 1,
                x['data'].get('card_id', ''),
                x['data'].get('order', 999)
            ))
        except:
            pass
        
        print(f"📋 Subtopic '{subtopic_title}' has {len(content)} items")
        return content
    
    def get_all_modules(self):
        """Возвращает все доступные модули с их подтемами"""
        if not self._loaded:
            self.load_content()
            
        all_modules = set()
        all_modules.update(self.learning_cards.keys())
        all_modules.update(self.tests.keys())
        return sorted(list(all_modules))
    
    def get_content_stats(self):
        """Возвращает статистику загруженного контента"""
        if not self._loaded:
            self.load_content()
        
        stats = {
            'total_modules': len(set(list(self.learning_cards.keys()) + list(self.tests.keys()))),
            'modules_with_cards': len(self.learning_cards),
            'modules_with_tests': len(self.tests),
            'total_cards': sum(len(cards) for cards in self.learning_cards.values()),
            'total_tests': sum(len(tests) for tests in self.tests.values()),
            'modules_list': sorted(set(list(self.learning_cards.keys()) + list(self.tests.keys())))
        }
        return stats

# Создаем глобальный экземпляр
content_loader = ContentLoader()