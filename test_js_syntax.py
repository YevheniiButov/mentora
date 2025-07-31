#!/usr/bin/env python3
# Test JavaScript syntax from enhanced-editor.html
import re
import os

def check_js_syntax():
    # Read the HTML file
    html_path = os.path.join(os.path.dirname(__file__), 'templates/admin/content_editor/enhanced_editor.html')
    
    if not os.path.exists(html_path):
        print(f"❌ File not found: {html_path}")
        return
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract JavaScript code between <script> tags
    script_pattern = r'<script[^>]*>([\s\S]*?)</script>'
    script_matches = re.findall(script_pattern, html_content)
    
    if script_matches:
        print(f"Found {len(script_matches)} script blocks")
        
        for i, js_code in enumerate(script_matches, 1):
            js_code = js_code.strip()
            
            # Skip external scripts
            if not js_code:
                print(f"⏩ Script block {i}: Empty (external script)")
                continue
            
            # Basic syntax checks
            errors = []
            
            # Check for unmatched braces
            brace_count = js_code.count('{') - js_code.count('}')
            if brace_count != 0:
                errors.append(f"Unmatched braces: {brace_count}")
            
            # Check for unmatched parentheses
            paren_count = js_code.count('(') - js_code.count(')')
            if paren_count != 0:
                errors.append(f"Unmatched parentheses: {paren_count}")
            
            # Check for unmatched brackets
            bracket_count = js_code.count('[') - js_code.count(']')
            if bracket_count != 0:
                errors.append(f"Unmatched brackets: {bracket_count}")
            
            # Check for template literals
            backtick_count = js_code.count('`')
            if backtick_count % 2 != 0:
                errors.append(f"Unmatched template literals: {backtick_count}")
            
            # Check for unterminated strings
            single_quote_count = js_code.count("'") - js_code.count("\\'")
            double_quote_count = js_code.count('"') - js_code.count('\\"')
            
            if single_quote_count % 2 != 0:
                errors.append(f"Unterminated single quotes")
            if double_quote_count % 2 != 0:
                errors.append(f"Unterminated double quotes")
            
            if errors:
                print(f"❌ Script block {i}: Syntax issues found")
                for error in errors:
                    print(f"   - {error}")
                print(f"   Code preview: {js_code[:200]}...")
            else:
                print(f"✅ Script block {i}: Basic syntax OK")
    else:
        print("No script blocks found")

if __name__ == "__main__":
    check_js_syntax() 