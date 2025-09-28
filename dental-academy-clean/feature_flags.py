#!/usr/bin/env python3
"""
Система feature flags для безопасного включения IRT функций
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class FeatureFlags:
    def __init__(self, config_file: str = 'feature_flags.json'):
        self.config_file = config_file
        self.flags = self.load_flags()
    
    def load_flags(self) -> Dict[str, Any]:
        """Загружает feature flags из файла или создает дефолтные"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading feature flags: {e}")
                return self.get_default_flags()
        else:
            return self.get_default_flags()
    
    def get_default_flags(self) -> Dict[str, Any]:
        """Возвращает дефолтные feature flags"""
        return {
            "irt_enabled": False,
            "irt_pilot_mode": False,
            "irt_dentists": False,
            "irt_general_practitioners": False,
            "irt_calibration": False,
            "irt_analytics": False,
            "irt_debug_mode": False,
            "irt_performance_monitoring": False,
            "irt_error_tracking": False,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def save_flags(self):
        """Сохраняет feature flags в файл"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.flags, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving feature flags: {e}")
            return False
    
    def is_enabled(self, flag_name: str) -> bool:
        """Проверяет, включен ли feature flag"""
        return self.flags.get(flag_name, False)
    
    def enable(self, flag_name: str) -> bool:
        """Включает feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = True
            self.flags["last_updated"] = datetime.now().isoformat()
            return self.save_flags()
        return False
    
    def disable(self, flag_name: str) -> bool:
        """Выключает feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = False
            self.flags["last_updated"] = datetime.now().isoformat()
            return self.save_flags()
        return False
    
    def set_flag(self, flag_name: str, value: Any) -> bool:
        """Устанавливает значение feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = value
            self.flags["last_updated"] = datetime.now().isoformat()
            return self.save_flags()
        return False
    
    def get_all_flags(self) -> Dict[str, Any]:
        """Возвращает все feature flags"""
        return self.flags.copy()
    
    def enable_irt_system(self, pilot_mode: bool = True):
        """Включает IRT систему с настройками"""
        self.flags.update({
            "irt_enabled": True,
            "irt_pilot_mode": pilot_mode,
            "irt_dentists": True,  # Всегда включаем для стоматологов
            "irt_general_practitioners": False,  # Пока отключено
            "irt_calibration": True,
            "irt_analytics": True,
            "irt_performance_monitoring": True,
            "irt_error_tracking": True,
            "last_updated": datetime.now().isoformat()
        })
        return self.save_flags()
    
    def disable_irt_system(self):
        """Отключает IRT систему"""
        self.flags.update({
            "irt_enabled": False,
            "irt_pilot_mode": False,
            "irt_dentists": False,
            "irt_general_practitioners": False,
            "irt_calibration": False,
            "irt_analytics": False,
            "last_updated": datetime.now().isoformat()
        })
        return self.save_flags()
    
    def enable_pilot_mode(self):
        """Включает пилотный режим"""
        self.flags.update({
            "irt_enabled": True,
            "irt_pilot_mode": True,
            "irt_dentists": True,
            "irt_general_practitioners": True,  # Включаем для пилотирования
            "irt_calibration": True,
            "irt_analytics": True,
            "irt_debug_mode": True,
            "last_updated": datetime.now().isoformat()
        })
        return self.save_flags()
    
    def get_status_report(self) -> Dict[str, Any]:
        """Возвращает отчет о статусе feature flags"""
        enabled_flags = [name for name, value in self.flags.items() 
                        if isinstance(value, bool) and value]
        disabled_flags = [name for name, value in self.flags.items() 
                         if isinstance(value, bool) and not value]
        
        return {
            "total_flags": len([k for k, v in self.flags.items() if isinstance(v, bool)]),
            "enabled_count": len(enabled_flags),
            "disabled_count": len(disabled_flags),
            "enabled_flags": enabled_flags,
            "disabled_flags": disabled_flags,
            "last_updated": self.flags.get("last_updated"),
            "version": self.flags.get("version")
        }

# Глобальный экземпляр для использования в приложении
feature_flags = FeatureFlags()

def is_irt_enabled() -> bool:
    """Проверяет, включена ли IRT система"""
    return feature_flags.is_enabled("irt_enabled")

def is_irt_pilot_mode() -> bool:
    """Проверяет, включен ли пилотный режим"""
    return feature_flags.is_enabled("irt_pilot_mode")

def is_irt_dentists_enabled() -> bool:
    """Проверяет, включена ли IRT для стоматологов"""
    return feature_flags.is_enabled("irt_dentists")

def is_irt_general_practitioners_enabled() -> bool:
    """Проверяет, включена ли IRT для врачей общей практики"""
    return feature_flags.is_enabled("irt_general_practitioners")

def is_irt_calibration_enabled() -> bool:
    """Проверяет, включена ли калибровка IRT"""
    return feature_flags.is_enabled("irt_calibration")

def is_irt_analytics_enabled() -> bool:
    """Проверяет, включена ли IRT аналитика"""
    return feature_flags.is_enabled("irt_analytics")

def is_irt_debug_mode() -> bool:
    """Проверяет, включен ли debug режим"""
    return feature_flags.is_enabled("irt_debug_mode")

def main():
    """CLI для управления feature flags"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IRT Feature Flags Manager')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--enable', type=str, help='Enable flag')
    parser.add_argument('--disable', type=str, help='Disable flag')
    parser.add_argument('--enable-irt', action='store_true', help='Enable IRT system')
    parser.add_argument('--disable-irt', action='store_true', help='Disable IRT system')
    parser.add_argument('--pilot-mode', action='store_true', help='Enable pilot mode')
    parser.add_argument('--list', action='store_true', help='List all flags')
    
    args = parser.parse_args()
    
    if args.status:
        report = feature_flags.get_status_report()
        print("📊 Feature Flags Status:")
        print(f"   Total flags: {report['total_flags']}")
        print(f"   Enabled: {report['enabled_count']}")
        print(f"   Disabled: {report['disabled_count']}")
        print(f"   Last updated: {report['last_updated']}")
        
        if report['enabled_flags']:
            print("\n✅ Enabled flags:")
            for flag in report['enabled_flags']:
                print(f"   - {flag}")
        
        if report['disabled_flags']:
            print("\n❌ Disabled flags:")
            for flag in report['disabled_flags']:
                print(f"   - {flag}")
    
    elif args.enable:
        if feature_flags.enable(args.enable):
            print(f"✅ Enabled flag: {args.enable}")
        else:
            print(f"❌ Failed to enable flag: {args.enable}")
    
    elif args.disable:
        if feature_flags.disable(args.disable):
            print(f"✅ Disabled flag: {args.disable}")
        else:
            print(f"❌ Failed to disable flag: {args.disable}")
    
    elif args.enable_irt:
        if feature_flags.enable_irt_system():
            print("✅ IRT system enabled")
        else:
            print("❌ Failed to enable IRT system")
    
    elif args.disable_irt:
        if feature_flags.disable_irt_system():
            print("✅ IRT system disabled")
        else:
            print("❌ Failed to disable IRT system")
    
    elif args.pilot_mode:
        if feature_flags.enable_pilot_mode():
            print("✅ Pilot mode enabled")
        else:
            print("❌ Failed to enable pilot mode")
    
    elif args.list:
        flags = feature_flags.get_all_flags()
        print("📋 All Feature Flags:")
        for name, value in flags.items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"   {status} {name}: {value}")
            else:
                print(f"   📝 {name}: {value}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


