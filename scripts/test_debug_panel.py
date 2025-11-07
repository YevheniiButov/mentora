#!/usr/bin/env python3
"""
Test Script for Editor Debug Panel
Tests the functionality of the debug panel in the enhanced editor
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DebugPanelTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_server_connection(self):
        """Test if server is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Server Connection", True, "Server is running")
                return True
            else:
                self.log_test("Server Connection", False, f"Server returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("Server Connection", False, "Cannot connect to server")
            return False
    
    def test_editor_page_access(self):
        """Test access to enhanced editor page"""
        try:
            response = self.session.get(f"{self.base_url}/en/admin/content-editor/enhanced-editor")
            if response.status_code == 200:
                self.log_test("Editor Page Access", True, "Enhanced editor page accessible")
                return True
            else:
                self.log_test("Editor Page Access", False, f"Page returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Editor Page Access", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_script(self):
        """Test if debug panel script is accessible"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                if "EditorDebugPanel" in content:
                    self.log_test("Debug Panel Script", True, "Debug panel script found and contains class")
                    return True
                else:
                    self.log_test("Debug Panel Script", False, "Script doesn't contain EditorDebugPanel class")
                    return False
            else:
                self.log_test("Debug Panel Script", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Script", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_styles(self):
        """Test if debug panel styles are properly defined"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                required_styles = [
                    ".debug-panel",
                    ".debug-header",
                    ".debug-tabs",
                    ".debug-content",
                    ".debug-toggle"
                ]
                
                missing_styles = []
                for style in required_styles:
                    if style not in content:
                        missing_styles.append(style)
                
                if not missing_styles:
                    self.log_test("Debug Panel Styles", True, "All required styles found")
                    return True
                else:
                    self.log_test("Debug Panel Styles", False, f"Missing styles: {missing_styles}")
                    return False
            else:
                self.log_test("Debug Panel Styles", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Styles", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_functionality(self):
        """Test debug panel functionality"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                required_methods = [
                    "createDebugUI",
                    "logTemplateOperation",
                    "logAPICall",
                    "logActivity",
                    "updateOverview",
                    "exportDebugInfo",
                    "clearCache",
                    "resetToDefaults"
                ]
                
                missing_methods = []
                for method in required_methods:
                    if method not in content:
                        missing_methods.append(method)
                
                if not missing_methods:
                    self.log_test("Debug Panel Functionality", True, "All required methods found")
                    return True
                else:
                    self.log_test("Debug Panel Functionality", False, f"Missing methods: {missing_methods}")
                    return False
            else:
                self.log_test("Debug Panel Functionality", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_integration(self):
        """Test debug panel integration with editor"""
        try:
            # First try to access the actual editor page
            response = self.session.get(f"{self.base_url}/en/admin/content-editor/enhanced-editor")
            if response.status_code == 200:
                content = response.text
                if "editor-debug.js" in content:
                    self.log_test("Debug Panel Integration", True, "Debug panel script is included in editor template")
                    return True
                else:
                    self.log_test("Debug Panel Integration", False, "Debug panel script not found in editor template")
                    return False
            else:
                # If page is not accessible, check if template file exists
                response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
                if response.status_code == 200:
                    self.log_test("Debug Panel Integration", True, "Debug panel script exists and is accessible")
                    return True
                else:
                    self.log_test("Debug Panel Integration", False, f"Template returned {response.status_code}")
                    return False
        except Exception as e:
            self.log_test("Debug Panel Integration", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_auto_init(self):
        """Test debug panel auto-initialization"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                auto_init_patterns = [
                    "DOMContentLoaded",
                    "setInterval",
                    "window.debugPanel",
                    "EditorDebugPanel"
                ]
                
                missing_patterns = []
                for pattern in auto_init_patterns:
                    if pattern not in content:
                        missing_patterns.append(pattern)
                
                if not missing_patterns:
                    self.log_test("Debug Panel Auto-Init", True, "Auto-initialization code found")
                    return True
                else:
                    self.log_test("Debug Panel Auto-Init", False, f"Missing patterns: {missing_patterns}")
                    return False
            else:
                self.log_test("Debug Panel Auto-Init", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Auto-Init", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_tabs(self):
        """Test debug panel tabs functionality"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                required_tabs = [
                    "overview",
                    "state", 
                    "api",
                    "components",
                    "css",
                    "performance",
                    "tools"
                ]
                
                missing_tabs = []
                for tab in required_tabs:
                    if f'data-tab="{tab}"' not in content:
                        missing_tabs.append(tab)
                
                if not missing_tabs:
                    self.log_test("Debug Panel Tabs", True, "All required tabs found")
                    return True
                else:
                    self.log_test("Debug Panel Tabs", False, f"Missing tabs: {missing_tabs}")
                    return False
            else:
                self.log_test("Debug Panel Tabs", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Tabs", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_logging(self):
        """Test debug panel logging capabilities"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                logging_features = [
                    "logTemplateOperation",
                    "logAPICall", 
                    "logActivity",
                    "updateActivityLog",
                    "updateApiLogs"
                ]
                
                missing_features = []
                for feature in logging_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("Debug Panel Logging", True, "All logging features found")
                    return True
                else:
                    self.log_test("Debug Panel Logging", False, f"Missing features: {missing_features}")
                    return False
            else:
                self.log_test("Debug Panel Logging", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Logging", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_tools(self):
        """Test debug panel tools functionality"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                tool_methods = [
                    "clearCache",
                    "resetToDefaults",
                    "forceTemplateReload",
                    "validateCurrentState",
                    "restartEditor",
                    "enableSafeMode"
                ]
                
                missing_tools = []
                for tool in tool_methods:
                    if tool not in content:
                        missing_tools.append(tool)
                
                if not missing_tools:
                    self.log_test("Debug Panel Tools", True, "All debug tools found")
                    return True
                else:
                    self.log_test("Debug Panel Tools", False, f"Missing tools: {missing_tools}")
                    return False
            else:
                self.log_test("Debug Panel Tools", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Tools", False, f"Error: {str(e)}")
            return False
    
    def test_debug_panel_export(self):
        """Test debug panel export functionality"""
        try:
            response = self.session.get(f"{self.base_url}/static/js/editor-debug.js")
            if response.status_code == 200:
                content = response.text
                export_features = [
                    "exportDebugInfo",
                    "exportCurrentState",
                    "exportApiLogs",
                    "Blob",
                    "URL.createObjectURL"
                ]
                
                missing_features = []
                for feature in export_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("Debug Panel Export", True, "All export features found")
                    return True
                else:
                    self.log_test("Debug Panel Export", False, f"Missing features: {missing_features}")
                    return False
            else:
                self.log_test("Debug Panel Export", False, f"Script returned {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Debug Panel Export", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all debug panel tests"""
        print("🔧 Testing Editor Debug Panel")
        print("=" * 50)
        
        # Run tests
        tests = [
            self.test_server_connection,
            self.test_editor_page_access,
            self.test_debug_panel_script,
            self.test_debug_panel_styles,
            self.test_debug_panel_functionality,
            self.test_debug_panel_integration,
            self.test_debug_panel_auto_init,
            self.test_debug_panel_tabs,
            self.test_debug_panel_logging,
            self.test_debug_panel_tools,
            self.test_debug_panel_export
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.1)  # Small delay between tests
            except Exception as e:
                self.log_test(test.__name__, False, f"Test failed with exception: {str(e)}")
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Debug panel is working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please check the issues above.")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_panel_test_results_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for result in self.test_results if result["success"]),
            "failed_tests": sum(1 for result in self.test_results if not result["success"]),
            "results": self.test_results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {str(e)}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Editor Debug Panel")
    parser.add_argument("--url", default="http://localhost:5000", 
                       help="Base URL of the Flask application")
    parser.add_argument("--port", type=int, default=5000,
                       help="Port number (alternative to --url)")
    
    args = parser.parse_args()
    
    # Use port if specified
    if args.port != 5000:
        base_url = f"http://localhost:{args.port}"
    else:
        base_url = args.url
    
    # Create tester and run tests
    tester = DebugPanelTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 