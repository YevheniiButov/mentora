#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Recommendation Engine
Система автоматической генерации рекомендаций обучения на основе результатов тестирования
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestResult:
    """Результат тестирования по домену"""
    domain: str
    score: float  # 0-100
    total_questions: int
    correct_answers: int
    time_spent: float  # в минутах

@dataclass
class LearningRecommendation:
    """Рекомендация для обучения"""
    domain: str
    priority: str
    weight: float
    recommended_cards: List[str]
    card_sources: List[str]
    topics: List[str]
    estimated_time: int  # в минутах
    difficulty_level: str

class LearningRecommendationEngine:
    """Движок для генерации рекомендаций обучения"""
    
    def __init__(self, domain_mapping_path: str = "cards/domain_mapping.json"):
        """
        Инициализация движка
        
        Args:
            domain_mapping_path: Путь к файлу с маппингом доменов
        """
        self.domain_mapping_path = domain_mapping_path
        self.domain_mapping = self._load_domain_mapping()
        self.cards_cache = {}
        
    def _load_domain_mapping(self) -> Dict:
        """Загрузка маппинга доменов"""
        try:
            with open(self.domain_mapping_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: Файл {self.domain_mapping_path} не найден")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка: Неверный формат JSON в файле {self.domain_mapping_path}")
            return {}
    
    def analyze_test_results(self, test_results: List[TestResult]) -> Dict:
        """
        Анализ результатов тестирования
        
        Args:
            test_results: Список результатов тестирования
            
        Returns:
            Словарь с анализом результатов
        """
        analysis = {
            "overall_score": 0,
            "domain_scores": {},
            "weak_domains": [],
            "strong_domains": [],
            "priority_recommendations": []
        }
        
        if not test_results:
            return analysis
        
        # Общий балл
        total_score = sum(result.score for result in test_results)
        analysis["overall_score"] = total_score / len(test_results)
        
        # Анализ по доменам
        for result in test_results:
            analysis["domain_scores"][result.domain] = {
                "score": result.score,
                "performance_level": self._get_performance_level(result.score),
                "weight": self._get_domain_weight(result.domain),
                "priority": self._get_domain_priority(result.domain)
            }
            
            # Определение слабых и сильных областей
            if result.score < 60:
                analysis["weak_domains"].append(result.domain)
            elif result.score >= 90:
                analysis["strong_domains"].append(result.domain)
        
        # Приоритизация рекомендаций
        analysis["priority_recommendations"] = self._prioritize_recommendations(analysis)
        
        return analysis
    
    def _get_performance_level(self, score: float) -> str:
        """Определение уровня производительности"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "poor"
    
    def _get_domain_weight(self, domain: str) -> float:
        """Получение веса домена"""
        if domain in self.domain_mapping.get("domain_mapping", {}):
            return self.domain_mapping["domain_mapping"][domain].get("weight", 0)
        return 0
    
    def _get_domain_priority(self, domain: str) -> str:
        """Получение приоритета домена"""
        if domain in self.domain_mapping.get("domain_mapping", {}):
            return self.domain_mapping["domain_mapping"][domain].get("priority", "low")
        return "low"
    
    def _prioritize_recommendations(self, analysis: Dict) -> List[str]:
        """Приоритизация рекомендаций"""
        recommendations = []
        
        # Сначала слабые области с высоким приоритетом
        for domain in analysis["weak_domains"]:
            domain_info = analysis["domain_scores"][domain]
            if domain_info["priority"] == "high":
                recommendations.append(domain)
        
        # Затем слабые области со средним приоритетом
        for domain in analysis["weak_domains"]:
            domain_info = analysis["domain_scores"][domain]
            if domain_info["priority"] == "medium":
                recommendations.append(domain)
        
        # Затем слабые области с низким приоритетом
        for domain in analysis["weak_domains"]:
            domain_info = analysis["domain_scores"][domain]
            if domain_info["priority"] == "low":
                recommendations.append(domain)
        
        return recommendations
    
    def generate_learning_plan(self, test_results: List[TestResult]) -> List[LearningRecommendation]:
        """
        Генерация плана обучения
        
        Args:
            test_results: Результаты тестирования
            
        Returns:
            Список рекомендаций для обучения
        """
        analysis = self.analyze_test_results(test_results)
        recommendations = []
        
        for domain in analysis["priority_recommendations"]:
            domain_score = analysis["domain_scores"][domain]["score"]
            performance_level = analysis["domain_scores"][domain]["performance_level"]
            
            recommendation = self._create_domain_recommendation(
                domain, domain_score, performance_level
            )
            
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _create_domain_recommendation(
        self, 
        domain: str, 
        score: float, 
        performance_level: str
    ) -> Optional[LearningRecommendation]:
        """Создание рекомендации для домена"""
        
        if domain not in self.domain_mapping.get("domain_mapping", {}):
            return None
        
        domain_info = self.domain_mapping["domain_mapping"][domain]
        
        # Определение количества рекомендуемых карточек
        card_count = self._get_recommended_card_count(performance_level, domain_info)
        
        # Получение источников карточек
        card_sources = self._get_card_sources(domain_info)
        
        # Получение тем
        topics = self._get_domain_topics(domain_info)
        
        # Оценка времени обучения
        estimated_time = self._estimate_learning_time(card_count, performance_level)
        
        # Уровень сложности
        difficulty_level = self._get_difficulty_level(performance_level, domain_info["weight"])
        
        return LearningRecommendation(
            domain=domain,
            priority=domain_info["priority"],
            weight=domain_info["weight"],
            recommended_cards=self._get_recommended_cards(domain, card_sources, card_count),
            card_sources=card_sources,
            topics=topics,
            estimated_time=estimated_time,
            difficulty_level=difficulty_level
        )
    
    def _get_recommended_card_count(self, performance_level: str, domain_info: Dict) -> int:
        """Определение количества рекомендуемых карточек"""
        base_count = 0
        
        # Подсчет общего количества карточек в домене
        for source_info in domain_info.get("card_sources", {}).values():
            if "card_count" in source_info:
                base_count += source_info["card_count"]
            else:
                # Для источников без точного подсчета, используем приблизительную оценку
                base_count += 50  # Примерная оценка
        
        # Применение правил рекомендаций
        if performance_level == "poor":
            return min(base_count, 100)  # Все карточки, но не более 100
        elif performance_level == "fair":
            return min(base_count // 2, 50)
        elif performance_level == "good":
            return min(base_count // 4, 25)
        else:  # excellent
            return min(base_count // 8, 10)
    
    def _get_card_sources(self, domain_info: Dict) -> List[str]:
        """Получение источников карточек"""
        sources = []
        for source_name, source_info in domain_info.get("card_sources", {}).items():
            sources.append(source_name)
        return sources
    
    def _get_domain_topics(self, domain_info: Dict) -> List[str]:
        """Получение тем домена"""
        topics = []
        for source_info in domain_info.get("card_sources", {}).values():
            if "topics" in source_info:
                topics.extend(source_info["topics"])
        return list(set(topics))  # Удаление дубликатов
    
    def _estimate_learning_time(self, card_count: int, performance_level: str) -> int:
        """Оценка времени обучения в минутах"""
        base_time_per_card = 2  # минуты на карточку
        
        if performance_level == "poor":
            multiplier = 1.5  # Больше времени для слабых областей
        elif performance_level == "fair":
            multiplier = 1.2
        elif performance_level == "good":
            multiplier = 1.0
        else:  # excellent
            multiplier = 0.8  # Меньше времени для сильных областей
        
        return int(card_count * base_time_per_card * multiplier)
    
    def _get_difficulty_level(self, performance_level: str, weight: float) -> str:
        """Определение уровня сложности"""
        if performance_level == "poor":
            return "easy"  # Начинаем с простого
        elif performance_level == "fair":
            return "medium"
        elif performance_level == "good":
            return "medium"
        else:  # excellent
            return "hard"  # Только сложные карточки
    
    def _get_recommended_cards(self, domain: str, card_sources: List[str], card_count: int) -> List[str]:
        """Получение рекомендуемых карточек"""
        # В реальной реализации здесь будет логика загрузки и фильтрации карточек
        # Пока возвращаем заглушку
        return [f"{domain}_card_{i}" for i in range(1, min(card_count + 1, 11))]
    
    def generate_personalized_report(self, test_results: List[TestResult]) -> Dict:
        """
        Генерация персонализированного отчета
        
        Args:
            test_results: Результаты тестирования
            
        Returns:
            Персонализированный отчет
        """
        analysis = self.analyze_test_results(test_results)
        learning_plan = self.generate_learning_plan(test_results)
        
        report = {
            "test_summary": {
                "total_domains_tested": len(test_results),
                "overall_score": analysis["overall_score"],
                "performance_level": self._get_performance_level(analysis["overall_score"]),
                "weak_domains_count": len(analysis["weak_domains"]),
                "strong_domains_count": len(analysis["strong_domains"])
            },
            "domain_analysis": analysis["domain_scores"],
            "learning_recommendations": [
                {
                    "domain": rec.domain,
                    "priority": rec.priority,
                    "weight": rec.weight,
                    "card_count": len(rec.recommended_cards),
                    "card_sources": rec.card_sources,
                    "topics": rec.topics,
                    "estimated_time_minutes": rec.estimated_time,
                    "difficulty_level": rec.difficulty_level
                }
                for rec in learning_plan
            ],
            "study_plan": {
                "total_estimated_time": sum(rec.estimated_time for rec in learning_plan),
                "priority_order": [rec.domain for rec in learning_plan],
                "focus_areas": analysis["weak_domains"][:3]  # Топ-3 слабые области
            }
        }
        
        return report
    
    def export_learning_plan(self, test_results: List[TestResult], output_path: str):
        """
        Экспорт плана обучения в файл
        
        Args:
            test_results: Результаты тестирования
            output_path: Путь для сохранения файла
        """
        report = self.generate_personalized_report(test_results)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"План обучения сохранен в {output_path}")
        except Exception as e:
            print(f"Ошибка при сохранении плана обучения: {e}")


def main():
    """Пример использования движка"""
    
    # Создание движка
    engine = LearningRecommendationEngine()
    
    # Пример результатов тестирования
    test_results = [
        TestResult("Praktische vaardigheden", 45.0, 20, 9, 30),
        TestResult("Behandelplanning", 75.0, 15, 11, 25),
        TestResult("Mondziekten en kaakchirurgie", 85.0, 12, 10, 20),
        TestResult("Farmacologie", 30.0, 18, 5, 35),
        TestResult("Ethiek en recht", 90.0, 10, 9, 15)
    ]
    
    # Генерация отчета
    report = engine.generate_personalized_report(test_results)
    
    # Вывод результатов
    print("=== ПЕРСОНАЛИЗИРОВАННЫЙ ОТЧЕТ ОБ ОБУЧЕНИИ ===\n")
    
    print(f"Общий балл: {report['test_summary']['overall_score']:.1f}%")
    print(f"Уровень производительности: {report['test_summary']['performance_level']}")
    print(f"Слабых областей: {report['test_summary']['weak_domains_count']}")
    print(f"Сильных областей: {report['test_summary']['strong_domains_count']}\n")
    
    print("=== РЕКОМЕНДАЦИИ ДЛЯ ОБУЧЕНИЯ ===\n")
    
    for i, rec in enumerate(report['learning_recommendations'], 1):
        print(f"{i}. {rec['domain']} (Приоритет: {rec['priority']}, Вес: {rec['weight']}%)")
        print(f"   Карточек: {rec['card_count']}")
        print(f"   Время: {rec['estimated_time_minutes']} минут")
        print(f"   Сложность: {rec['difficulty_level']}")
        print(f"   Источники: {', '.join(rec['card_sources'])}")
        print(f"   Темы: {', '.join(rec['topics'][:3])}...")
        print()
    
    print("=== ПЛАН ИЗУЧЕНИЯ ===\n")
    print(f"Общее время: {report['study_plan']['total_estimated_time']} минут")
    print(f"Порядок изучения: {' → '.join(report['study_plan']['priority_order'])}")
    print(f"Фокус на: {', '.join(report['study_plan']['focus_areas'])}")
    
    # Экспорт в файл
    engine.export_learning_plan(test_results, "learning_plan.json")


if __name__ == "__main__":
    main() 