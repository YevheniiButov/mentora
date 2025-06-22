import os
import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from flask import url_for
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkChecker:
    def __init__(self, base_url, templates_dir):
        self.base_url = base_url
        self.templates_dir = templates_dir
        self.checked_urls = set()
        self.broken_links = []
        self.static_files = set()
        
    def find_url_for_calls(self, content):
        """Находит все вызовы url_for в коде"""
        pattern = r'url_for\([\'"]([^\'"]+)[\'"]'
        return re.findall(pattern, content)
        
    def find_static_links(self, content):
        """Находит все ссылки на статические файлы"""
        pattern = r'{{ url_for\([\'"]static[\'"], filename=[\'"]([^\'"]+)[\'"]'
        return re.findall(pattern, content)
        
    def check_template(self, template_path):
        """Проверяет шаблон на наличие битых ссылок"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем url_for вызовы
            url_for_calls = self.find_url_for_calls(content)
            for endpoint in url_for_calls:
                self.check_endpoint(endpoint)
                
            # Проверяем статические файлы
            static_links = self.find_static_links(content)
            for static_file in static_links:
                self.check_static_file(static_file)
                
        except Exception as e:
            logger.error(f"Error checking template {template_path}: {e}")
            
    def check_endpoint(self, endpoint):
        """Проверяет доступность endpoint"""
        try:
            url = url_for(endpoint)
            if url not in self.checked_urls:
                self.checked_urls.add(url)
                response = requests.get(urljoin(self.base_url, url))
                if response.status_code != 200:
                    self.broken_links.append({
                        'url': url,
                        'status': response.status_code,
                        'type': 'endpoint'
                    })
        except Exception as e:
            logger.error(f"Error checking endpoint {endpoint}: {e}")
            
    def check_static_file(self, static_file):
        """Проверяет существование статического файла"""
        if static_file not in self.static_files:
            self.static_files.add(static_file)
            file_path = os.path.join('static', static_file)
            if not os.path.exists(file_path):
                self.broken_links.append({
                    'url': static_file,
                    'status': 404,
                    'type': 'static'
                })
                
    def check_all_templates(self):
        """Проверяет все шаблоны в директории"""
        for root, _, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    template_path = os.path.join(root, file)
                    self.check_template(template_path)
                    
    def generate_report(self):
        """Генерирует отчет о найденных проблемах"""
        report = {
            'total_checked': len(self.checked_urls) + len(self.static_files),
            'broken_links': self.broken_links,
            'broken_endpoints': [l for l in self.broken_links if l['type'] == 'endpoint'],
            'broken_static': [l for l in self.broken_links if l['type'] == 'static']
        }
        return report

def main():
    checker = LinkChecker(
        base_url='http://localhost:5000',
        templates_dir='templates'
    )
    checker.check_all_templates()
    report = checker.generate_report()
    
    print("\n=== Отчет о проверке ссылок ===")
    print(f"Всего проверено: {report['total_checked']}")
    print(f"Найдено битых ссылок: {len(report['broken_links'])}")
    
    if report['broken_endpoints']:
        print("\nБитые endpoints:")
        for link in report['broken_endpoints']:
            print(f"- {link['url']} (статус: {link['status']})")
            
    if report['broken_static']:
        print("\nБитые статические файлы:")
        for link in report['broken_static']:
            print(f"- {link['url']}")

if __name__ == '__main__':
    main() 