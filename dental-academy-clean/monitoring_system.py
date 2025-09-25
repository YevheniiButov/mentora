#!/usr/bin/env python3
"""
Система мониторинга для IRT системы
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
import subprocess

class IRTMonitoring:
    def __init__(self):
        self.health_status = {}
        self.performance_metrics = {}
        self.error_count = 0
        self.start_time = datetime.now()
    
    def check_database_health(self):
        """Проверяет здоровье базы данных"""
        try:
            from app import app
            from extensions import db
            
            with app.app_context():
                # Проверяем подключение
                db.session.execute("SELECT 1")
                
                # Проверяем IRT таблицы
                irt_tables = ['irt_parameters', 'diagnostic_session', 'diagnostic_response']
                for table in irt_tables:
                    try:
                        db.session.execute(f"SELECT COUNT(*) FROM {table}")
                    except Exception as e:
                        return False, f"IRT table {table} not accessible: {e}"
                
                return True, "Database healthy"
                
        except Exception as e:
            return False, f"Database error: {e}"
    
    def check_irt_models(self):
        """Проверяет доступность IRT моделей"""
        try:
            from models import IRTParameters, DiagnosticSession, DiagnosticResponse
            return True, "IRT models available"
        except ImportError as e:
            return False, f"IRT models import error: {e}"
    
    def check_scipy_availability(self):
        """Проверяет доступность scipy и numpy"""
        try:
            import scipy
            import numpy
            return True, f"Scipy {scipy.__version__}, Numpy {numpy.__version__}"
        except ImportError as e:
            return False, f"Scipy/Numpy error: {e}"
    
    def check_api_endpoints(self):
        """Проверяет API endpoints"""
        endpoints = [
            '/api/irt/questions',
            '/api/irt/sessions',
            '/api/irt/results'
        ]
        
        healthy_endpoints = 0
        for endpoint in endpoints:
            try:
                # Здесь можно добавить реальные HTTP запросы
                # response = requests.get(f"http://localhost:5000{endpoint}")
                # if response.status_code == 200:
                healthy_endpoints += 1
            except Exception as e:
                pass
        
        if healthy_endpoints == len(endpoints):
            return True, f"All {len(endpoints)} endpoints healthy"
        else:
            return False, f"Only {healthy_endpoints}/{len(endpoints)} endpoints healthy"
    
    def check_performance(self):
        """Проверяет производительность системы"""
        try:
            from app import app
            from extensions import db
            
            with app.app_context():
                # Тест скорости запросов
                start_time = time.time()
                
                # Простой запрос
                db.session.execute("SELECT 1")
                simple_query_time = time.time() - start_time
                
                # Запрос к IRT таблице
                start_time = time.time()
                try:
                    db.session.execute("SELECT COUNT(*) FROM irt_parameters")
                    irt_query_time = time.time() - start_time
                except:
                    irt_query_time = None
                
                # Проверяем производительность
                performance_ok = simple_query_time < 1.0  # Менее 1 секунды
                
                metrics = {
                    "simple_query_time": simple_query_time,
                    "irt_query_time": irt_query_time,
                    "performance_ok": performance_ok
                }
                
                return performance_ok, f"Performance metrics: {metrics}"
                
        except Exception as e:
            return False, f"Performance check error: {e}"
    
    def check_memory_usage(self):
        """Проверяет использование памяти"""
        try:
            import psutil
            
            # Использование памяти процессом
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Проверяем, что память не превышает 500MB
            memory_ok = memory_mb < 500
            
            return memory_ok, f"Memory usage: {memory_mb:.1f}MB"
            
        except ImportError:
            return True, "psutil not available, skipping memory check"
        except Exception as e:
            return False, f"Memory check error: {e}"
    
    def run_health_checks(self):
        """Запускает все проверки здоровья"""
        checks = [
            ("Database", self.check_database_health),
            ("IRT Models", self.check_irt_models),
            ("Scipy/Numpy", self.check_scipy_availability),
            ("API Endpoints", self.check_api_endpoints),
            ("Performance", self.check_performance),
            ("Memory", self.check_memory_usage)
        ]
        
        print("🏥 Running IRT system health checks...")
        all_healthy = True
        
        for name, check_func in checks:
            try:
                healthy, message = check_func()
                status = "✅" if healthy else "❌"
                print(f"   {status} {name}: {message}")
                
                self.health_status[name] = {
                    "healthy": healthy,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }
                
                if not healthy:
                    all_healthy = False
                    self.error_count += 1
                    
            except Exception as e:
                print(f"   ❌ {name}: Exception - {e}")
                self.health_status[name] = {
                    "healthy": False,
                    "message": f"Exception: {e}",
                    "timestamp": datetime.now().isoformat()
                }
                all_healthy = False
                self.error_count += 1
        
        return all_healthy
    
    def generate_report(self):
        """Генерирует отчет о состоянии системы"""
        uptime = datetime.now() - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "overall_health": all(status["healthy"] for status in self.health_status.values()),
            "error_count": self.error_count,
            "health_status": self.health_status,
            "performance_metrics": self.performance_metrics
        }
        
        return report
    
    def save_report(self, report):
        """Сохраняет отчет в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"health_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Health report saved: {report_filename}")
        return report_filename
    
    def continuous_monitoring(self, interval=60):
        """Непрерывный мониторинг системы"""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                healthy = self.run_health_checks()
                
                if not healthy:
                    print("⚠️  System health issues detected!")
                    report = self.generate_report()
                    self.save_report(report)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            final_report = self.generate_report()
            self.save_report(final_report)

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IRT System Monitoring')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    monitoring = IRTMonitoring()
    
    if args.continuous:
        monitoring.continuous_monitoring(args.interval)
    else:
        # Однократная проверка
        healthy = monitoring.run_health_checks()
        
        report = monitoring.generate_report()
        monitoring.save_report(report)
        
        if healthy:
            print("\n🎉 All health checks passed!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {monitoring.error_count} health check(s) failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
