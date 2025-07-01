"""
Template Deployment System
Система развертывания шаблонов

Features:
- Backup system with versioning
- Preview generation
- Safe deployment with rollback
- Template conversion from GrapesJS to Jinja2
"""

import os
import json
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from flask import current_app
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Метаданные резервной копии"""
    timestamp: str
    user: str
    description: str
    template_path: str
    backup_hash: str
    file_size: int
    changes: List[str]
    version: str

@dataclass
class DeploymentConfig:
    """Конфигурация развертывания"""
    backup_enabled: bool = True
    preview_enabled: bool = True
    validation_enabled: bool = True
    max_backups: int = 10
    backup_dir: str = "backups/templates"
    preview_dir: str = "previews"
    temp_dir: str = "temp"

class TemplateDeployer:
    """Система развертывания шаблонов"""
    
    def __init__(self, config: Optional[DeploymentConfig] = None):
        self.config = config or DeploymentConfig()
        self.setup_directories()
        self.deployment_history = []
        
    def setup_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.config.backup_dir,
            self.config.preview_dir,
            self.config.temp_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def create_backup(self, template_path: str, user: str, description: str = "") -> BackupMetadata:
        """Создание резервной копии шаблона"""
        if not self.config.backup_enabled:
            return None
            
        try:
            # Проверка существования файла
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
                
            # Чтение содержимого файла
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Создание метаданных
            timestamp = datetime.now().isoformat()
            file_size = len(content)
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Создание имени файла резервной копии
            template_name = Path(template_path).stem
            backup_filename = f"{template_name}_{timestamp.replace(':', '-')}.zip"
            backup_path = os.path.join(self.config.backup_dir, backup_filename)
            
            # Создание ZIP архива
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('template.html', content)
                
                # Добавление метаданных
                metadata = BackupMetadata(
                    timestamp=timestamp,
                    user=user,
                    description=description,
                    template_path=template_path,
                    backup_hash=content_hash,
                    file_size=file_size,
                    changes=[],
                    version=self._get_version()
                )
                
                zipf.writestr('metadata.json', json.dumps(asdict(metadata), indent=2))
                
            # Очистка старых резервных копий
            self._cleanup_old_backups(template_name)
            
            logger.info(f"Backup created: {backup_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
            
    def _cleanup_old_backups(self, template_name: str):
        """Очистка старых резервных копий"""
        try:
            backup_files = []
            for file in os.listdir(self.config.backup_dir):
                if file.startswith(template_name) and file.endswith('.zip'):
                    file_path = os.path.join(self.config.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
                    
            # Сортировка по времени создания
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Удаление лишних файлов
            if len(backup_files) > self.config.max_backups:
                for file_path, _ in backup_files[self.config.max_backups:]:
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {file_path}")
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            
    def _get_version(self) -> str:
        """Получение версии системы"""
        return "1.0.0"
        
    def convert_grapesjs_to_jinja2(self, grapesjs_content: str) -> str:
        """Конвертация контента GrapesJS в Jinja2 шаблон"""
        try:
            # Извлечение HTML и CSS из GrapesJS
            html_match = re.search(r'<body[^>]*>(.*?)</body>', grapesjs_content, re.DOTALL)
            css_match = re.search(r'<style[^>]*>(.*?)</style>', grapesjs_content, re.DOTALL)
            
            if not html_match:
                raise ValueError("No HTML content found in GrapesJS output")
                
            html_content = html_match.group(1)
            css_content = css_match.group(1) if css_match else ""
            
            # Создание Jinja2 шаблона
            jinja2_template = f"""{{% extends "base.html" %}}

{{% block title %}}Generated Template{{% endblock %}}

{{% block head %}}
<style>
{css_content}
</style>
{{% endblock %}}

{{% block content %}}
{html_content}
{{% endblock %}}
"""
            
            return jinja2_template
            
        except Exception as e:
            logger.error(f"GrapesJS to Jinja2 conversion failed: {e}")
            raise
            
    def validate_template(self, template_content: str) -> List[str]:
        """Валидация шаблона"""
        issues = []
        
        try:
            # Проверка синтаксиса Jinja2
            if not self._validate_jinja2_syntax(template_content):
                issues.append("Invalid Jinja2 syntax")
                
            # Проверка безопасности
            security_issues = self._check_security(template_content)
            issues.extend(security_issues)
            
            # Проверка совместимости
            compatibility_issues = self._check_compatibility(template_content)
            issues.extend(compatibility_issues)
            
            return issues
            
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            issues.append(f"Validation error: {str(e)}")
            return issues
            
    def _validate_jinja2_syntax(self, content: str) -> bool:
        """Проверка синтаксиса Jinja2"""
        try:
            # Простая проверка баланса блоков
            open_blocks = content.count('{%')
            close_blocks = content.count('%}')
            
            if open_blocks != close_blocks:
                return False
                
            # Проверка корректности блоков
            block_pattern = r'{%\s*(if|for|block|extends|include|macro)\s+'
            if re.search(block_pattern, content):
                # Дополнительные проверки для блоков
                pass
                
            return True
            
        except Exception:
            return False
            
    def _check_security(self, content: str) -> List[str]:
        """Проверка безопасности"""
        issues = []
        
        # Проверка на потенциально опасные конструкции
        dangerous_patterns = [
            r'{{.*?request\.form.*?}}',  # Прямой доступ к form
            r'{{.*?request\.args.*?}}',  # Прямой доступ к args
            r'{{.*?config\[.*?\]}}',     # Прямой доступ к config
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potential security issue: {pattern}")
                
        return issues
        
    def _check_compatibility(self, content: str) -> List[str]:
        """Проверка совместимости"""
        issues = []
        
        # Проверка на использование несуществующих блоков
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        blocks = re.findall(block_pattern, content)
        
        # Проверка на использование несуществующих переменных
        var_pattern = r'{{\s*(\w+)\s*}}'
        variables = re.findall(var_pattern, content)
        
        # Здесь можно добавить проверки против известных блоков и переменных
        return issues
        
    def generate_preview(self, template_content: str, template_name: str) -> Dict:
        """Генерация предварительного просмотра"""
        if not self.config.preview_enabled:
            return {"preview_url": None, "message": "Preview disabled"}
            
        try:
            # Создание временного файла для предварительного просмотра
            preview_filename = f"preview_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            preview_path = os.path.join(self.config.preview_dir, preview_filename)
            
            # Создание HTML файла с предварительным просмотром
            preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview: {template_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .preview-header {{ background: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
        .preview-content {{ border: 1px solid #ccc; padding: 20px; }}
    </style>
</head>
<body>
    <div class="preview-header">
        <h2>Preview: {template_name}</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="preview-content">
        {template_content}
    </div>
</body>
</html>"""
            
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(preview_html)
                
            # Генерация URL для предварительного просмотра
            preview_url = f"/previews/{preview_filename}"
            
            logger.info(f"Preview generated: {preview_path}")
            
            return {
                "preview_url": preview_url,
                "preview_path": preview_path,
                "template_name": template_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            raise
            
    def deploy_to_production(self, template_content: str, target_path: str, 
                           user: str, description: str = "") -> Dict:
        """Развертывание в продакшн"""
        try:
            # Создание резервной копии
            if os.path.exists(target_path):
                backup_metadata = self.create_backup(target_path, user, description)
            else:
                backup_metadata = None
                
            # Валидация шаблона
            if self.config.validation_enabled:
                issues = self.validate_template(template_content)
                if issues:
                    raise ValueError(f"Template validation failed: {issues}")
                    
            # Создание временного файла
            temp_path = os.path.join(self.config.temp_dir, f"temp_{Path(target_path).name}")
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
            # Перемещение в продакшн
            shutil.move(temp_path, target_path)
            
            # Запись в историю развертываний
            deployment_record = {
                "timestamp": datetime.now().isoformat(),
                "user": user,
                "description": description,
                "target_path": target_path,
                "backup_metadata": backup_metadata,
                "status": "success"
            }
            
            self.deployment_history.append(deployment_record)
            
            logger.info(f"Deployment successful: {target_path}")
            
            return {
                "status": "success",
                "target_path": target_path,
                "backup_metadata": backup_metadata,
                "deployment_record": deployment_record
            }
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            
            # Запись неудачного развертывания
            deployment_record = {
                "timestamp": datetime.now().isoformat(),
                "user": user,
                "description": description,
                "target_path": target_path,
                "status": "failed",
                "error": str(e)
            }
            
            self.deployment_history.append(deployment_record)
            
            raise
            
    def rollback(self, target_path: str, user: str, backup_timestamp: str = None) -> Dict:
        """Откат к предыдущей версии"""
        try:
            # Поиск резервной копии
            backup_path = self._find_backup(target_path, backup_timestamp)
            if not backup_path:
                raise FileNotFoundError("Backup not found")
                
            # Извлечение содержимого из резервной копии
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                template_content = zipf.read('template.html').decode('utf-8')
                metadata_content = zipf.read('metadata.json').decode('utf-8')
                metadata = json.loads(metadata_content)
                
            # Создание резервной копии текущей версии
            current_backup = self.create_backup(target_path, user, "Rollback backup")
            
            # Восстановление из резервной копии
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
            # Запись в историю
            rollback_record = {
                "timestamp": datetime.now().isoformat(),
                "user": user,
                "action": "rollback",
                "target_path": target_path,
                "restored_from": backup_path,
                "current_backup": current_backup,
                "status": "success"
            }
            
            self.deployment_history.append(rollback_record)
            
            logger.info(f"Rollback successful: {target_path}")
            
            return {
                "status": "success",
                "target_path": target_path,
                "restored_from": backup_path,
                "metadata": metadata,
                "rollback_record": rollback_record
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
            
    def _find_backup(self, target_path: str, timestamp: str = None) -> Optional[str]:
        """Поиск резервной копии"""
        try:
            template_name = Path(target_path).stem
            
            if timestamp:
                # Поиск по конкретному времени
                backup_filename = f"{template_name}_{timestamp.replace(':', '-')}.zip"
                backup_path = os.path.join(self.config.backup_dir, backup_filename)
                
                if os.path.exists(backup_path):
                    return backup_path
                    
            else:
                # Поиск последней резервной копии
                backup_files = []
                for file in os.listdir(self.config.backup_dir):
                    if file.startswith(template_name) and file.endswith('.zip'):
                        file_path = os.path.join(self.config.backup_dir, file)
                        backup_files.append((file_path, os.path.getmtime(file_path)))
                        
                if backup_files:
                    # Сортировка по времени создания
                    backup_files.sort(key=lambda x: x[1], reverse=True)
                    return backup_files[0][0]
                    
            return None
            
        except Exception as e:
            logger.error(f"Backup search failed: {e}")
            return None
            
    def get_deployment_history(self, target_path: str = None) -> List[Dict]:
        """Получение истории развертываний"""
        if target_path:
            return [record for record in self.deployment_history 
                   if record.get('target_path') == target_path]
        else:
            return self.deployment_history
            
    def get_backup_list(self, template_name: str = None) -> List[Dict]:
        """Получение списка резервных копий"""
        try:
            backups = []
            
            for file in os.listdir(self.config.backup_dir):
                if file.endswith('.zip'):
                    if template_name and not file.startswith(template_name):
                        continue
                        
                    file_path = os.path.join(self.config.backup_dir, file)
                    
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zipf:
                            metadata_content = zipf.read('metadata.json').decode('utf-8')
                            metadata = json.loads(metadata_content)
                            
                        backups.append({
                            "file_path": file_path,
                            "filename": file,
                            "metadata": metadata,
                            "file_size": os.path.getsize(file_path),
                            "created": os.path.getmtime(file_path)
                        })
                        
                    except Exception as e:
                        logger.error(f"Error reading backup {file}: {e}")
                        continue
                        
            # Сортировка по времени создания
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Backup list retrieval failed: {e}")
            return []

# Пример использования
if __name__ == "__main__":
    # Создание конфигурации
    config = DeploymentConfig(
        backup_enabled=True,
        preview_enabled=True,
        validation_enabled=True,
        max_backups=5
    )
    
    # Создание экземпляра развертывания
    deployer = TemplateDeployer(config)
    
    # Пример контента GrapesJS
    grapesjs_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #f0f0f0; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Dental Academy</h1>
            </div>
            <div class="content">
                <p>This is a sample content.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Конвертация в Jinja2
        jinja2_content = deployer.convert_grapesjs_to_jinja2(grapesjs_content)
        print("Conversion successful")
        
        # Валидация
        issues = deployer.validate_template(jinja2_content)
        if issues:
            print(f"Validation issues: {issues}")
        
        # Генерация предварительного просмотра
        preview = deployer.generate_preview(jinja2_content, "example_template")
        print(f"Preview generated: {preview['preview_url']}")
        
        # Развертывание в продакшн
        deployment = deployer.deploy_to_production(
            jinja2_content, 
            "templates/example.html",
            user="admin",
            description="Example deployment"
        )
        print("Deployment successful")
        
    except Exception as e:
        print(f"Error: {e}") 