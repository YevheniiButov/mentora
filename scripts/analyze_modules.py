#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze JSON files and extract all unique module titles.
Compares these with existing modules in the database to identify missing modules.

Usage:
    $ python -m scripts.analyze_modules path/to/cards
"""

import sys
import os
import json
import glob
import argparse
import logging
from pathlib import Path
from collections import Counter, defaultdict

# Add the parent directory to the path so we can import the application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

try:
    from app import app, db
    from models import Module, Subject, LearningPath
except ImportError as e:
    print(f"Error importing application modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('modules_analysis.txt')
    ]
)
logger = logging.getLogger(__name__)


def find_json_files(base_dir):
    """
    Recursively find all JSON files in the directory structure.
    
    Args:
        base_dir (str): The base directory to search in
    
    Returns:
        list: List of file paths
    """
    base_path = Path(base_dir)
    
    if not base_path.exists() or not base_path.is_dir():
        logger.error(f"Directory not found or is not a directory: {base_dir}")
        return []
    
    # Find all .json files recursively
    all_json_files = glob.glob(str(base_path / "**" / "*.json"), recursive=True)
    return all_json_files


def extract_module_titles_from_file(file_path):
    """
    Extract all unique module titles from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
    
    Returns:
        set: Set of unique module titles
    """
    module_titles = set()
    
    try:
        # Try different encodings
        encodings_to_try = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
        data = None
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                break
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError:
                continue
        
        if data is None:
            logger.warning(f"Could not read file with any encoding: {file_path}")
            return module_titles
        
        if not isinstance(data, list):
            logger.warning(f"File does not contain a list: {file_path}")
            return module_titles
        
        # Extract module titles
        for item in data:
            if isinstance(item, dict) and 'module_title' in item:
                title = item['module_title'].strip()
                module_titles.add(title)
                
                # Also add titles with common variations
                title_lower = title.lower()
                module_titles.add(title_lower)
                
                # Handle special cases for different letter cases
                if ': ' in title:
                    # Handle different capitalizations in parts after colon
                    parts = title.split(': ', 1)
                    if len(parts) == 2:
                        alt_title = f"{parts[0]}: {parts[1].title()}"
                        module_titles.add(alt_title)
                        
                        alt_title_2 = f"{parts[0]}: {parts[1].capitalize()}"
                        module_titles.add(alt_title_2)
        
        return module_titles
        
    except Exception as e:
        logger.error(f"Error extracting module titles from {file_path}: {e}")
        return module_titles


def analyze_module_titles(base_dir):
    """
    Analyze all JSON files to extract module titles and compare with existing modules.
    
    Args:
        base_dir (str): Path to the directory containing JSON files
    """
    # Find all JSON files
    json_files = find_json_files(base_dir)
    logger.info(f"Found {len(json_files)} JSON files to analyze")
    
    # Extract all module titles from files
    all_module_titles = set()
    file_module_map = defaultdict(set)
    module_occurrence = Counter()
    
    for file_path in json_files:
        rel_path = os.path.relpath(file_path, base_dir)
        module_titles = extract_module_titles_from_file(file_path)
        
        if module_titles:
            logger.info(f"Found {len(module_titles)} unique module titles in {rel_path}")
            all_module_titles.update(module_titles)
            
            for title in module_titles:
                file_module_map[title].add(rel_path)
                module_occurrence[title] += 1
    
    logger.info(f"Total unique module titles found across all files: {len(all_module_titles)}")
    
    # Get existing modules from database
    with app.app_context():
        existing_modules = {module.title.strip(): module for module in Module.query.all()}
        similar_modules = {}
        
        # Build a map of lowercase -> original case for fuzzy matching
        lowercase_to_original = {title.lower(): title for title in existing_modules.keys()}
        
        # Validate each found module title against the database
        missing_modules = []
        found_modules = []
        
        for title in sorted(all_module_titles):
            if title in existing_modules:
                found_modules.append((title, existing_modules[title].id))
            else:
                # Try case-insensitive match
                title_lower = title.lower()
                if title_lower in lowercase_to_original:
                    original_title = lowercase_to_original[title_lower]
                    similar_modules[title] = original_title
                    found_modules.append((title, existing_modules[original_title].id))
                else:
                    missing_modules.append(title)
        
        # Get all subjects for reference
        subjects = {subject.id: subject.name for subject in Subject.query.all()}
        
        # Log the results
        logger.info("\n=== ANALYSIS RESULTS ===")
        
        logger.info(f"\nFound {len(found_modules)} matching modules in database:")
        for title, module_id in found_modules[:20]:
            module = Module.query.get(module_id)
            subject_name = subjects.get(module.subject_id, "Unknown Subject")
            logger.info(f"  - '{title}' → Module ID: {module_id}, Subject: {subject_name}")
        
        if len(found_modules) > 20:
            logger.info(f"  ... and {len(found_modules) - 20} more")
        
        if similar_modules:
            logger.info(f"\nFound {len(similar_modules)} modules with case variations:")
            for variant, original in similar_modules.items():
                logger.info(f"  - '{variant}' → matches '{original}'")
        
        logger.info(f"\nFound {len(missing_modules)} modules missing from database:")
        for title in missing_modules:
            files = list(file_module_map[title])
            file_count = len(files)
            file_examples = files[:3]
            occurrence_count = module_occurrence[title]
            
            logger.info(f"  - '{title}' (found in {file_count} files, {occurrence_count} occurrences)")
            logger.info(f"    Examples: {', '.join(file_examples)}")
        
        # Generate SQL statements to create missing modules
        if missing_modules:
            logger.info("\n=== SQL STATEMENTS TO CREATE MISSING MODULES ===")
            logger.info("-- Execute these statements to create the missing modules")
            logger.info("-- You'll need to replace <subject_id> with the appropriate subject ID")
            
            for title in missing_modules:
                safe_title = title.replace("'", "''")  # Escape single quotes for SQL
                logger.info(f"""
INSERT INTO module (title, description, order, icon, module_type, is_premium, subject_id, is_final_test)
VALUES ('{safe_title}', 'Content for {safe_title}', 0, 'file-earmark-text', 'content', false, <subject_id>, false);
""")
        
        # Generate Python script to create modules
        if missing_modules:
            logger.info("\n=== PYTHON SCRIPT TO CREATE MISSING MODULES ===")
            
            script = """
from app import app, db
from models import Module, Subject

def create_missing_modules():
    with app.app_context():
        # Dictionary mapping subject names to their IDs
        # You need to update this with actual subject names and IDs
        subject_map = {
            "Basic Medical Sciences": 1,  # Replace with actual ID
            "THK I: Cariology/Endo/Perio/Pedo": 2,  # Replace with actual ID
            # Add more subject mappings as needed
        }
        
        # Default subject ID to use if not specified
        default_subject_id = 1  # Replace with appropriate default
        
        # List of modules to create (title, subject_name)
        modules_to_create = [
"""
            
            for title in missing_modules:
                escaped_title = title.replace("'", "\\'")
                # Try to guess the subject from the title
                subject_guess = "Basic Medical Sciences"  # Default guess
                
                # Look for keywords in the title to guess the subject
                lower_title = title.lower()
                if any(keyword in lower_title for keyword in ["caries", "cavity", "cariology"]):
                    subject_guess = "THK I: Cariology/Endo/Perio/Pedo"
                elif any(keyword in lower_title for keyword in ["endo", "root canal", "pulp"]):
                    subject_guess = "THK I: Cariology/Endo/Perio/Pedo"
                elif any(keyword in lower_title for keyword in ["perio", "gingiva", "periodont"]):
                    subject_guess = "THK I: Cariology/Endo/Perio/Pedo"
                elif any(keyword in lower_title for keyword in ["pedo", "pediatric", "child"]):
                    subject_guess = "THK I: Cariology/Endo/Perio/Pedo"
                elif any(keyword in lower_title for keyword in ["prostho", "crown", "bridge", "denture"]):
                    subject_guess = "THK II: Prostho/Surgery/Ortho"
                elif any(keyword in lower_title for keyword in ["surgery", "extraction", "implant"]):
                    subject_guess = "THK II: Prostho/Surgery/Ortho"
                elif any(keyword in lower_title for keyword in ["ortho", "orthodontic", "braces"]):
                    subject_guess = "THK II: Prostho/Surgery/Ortho"
                elif any(keyword in lower_title for keyword in ["radio", "xray", "cbct", "imaging"]):
                    subject_guess = "Radiology"
                elif any(keyword in lower_title for keyword in ["statistic", "data", "analysis"]):
                    subject_guess = "Statistics"
                
                script += f"            ('{escaped_title}', '{subject_guess}'),\n"
            
            script += """        ]
        
        # Create each module
        created_count = 0
        for title, subject_name in modules_to_create:
            # Get subject ID from the mapping, or use default
            subject_id = subject_map.get(subject_name, default_subject_id)
            
            # Check if module already exists
            existing = Module.query.filter_by(title=title).first()
            if existing:
                print(f"Module already exists: {title}")
                continue
            
            # Create new module
            module = Module(
                title=title,
                description=f"Content for {title}",
                order=0,
                icon="file-earmark-text",
                module_type="content",
                is_premium=False,
                subject_id=subject_id,
                is_final_test=False
            )
            
            db.session.add(module)
            created_count += 1
            print(f"Created module: {title} (Subject ID: {subject_id})")
        
        # Commit changes
        if created_count > 0:
            db.session.commit()
            print(f"Created {created_count} new modules")
        else:
            print("No new modules created")

if __name__ == "__main__":
    create_missing_modules()
"""
            
            logger.info(script)
            
            # Save the script to a file
            script_file_path = os.path.join(parent_dir, "scripts", "create_missing_modules.py")
            try:
                with open(script_file_path, "w") as f:
                    f.write(script)
                logger.info(f"\nScript saved to: {script_file_path}")
            except Exception as e:
                logger.error(f"Error saving script: {e}")
        
        logger.info("\n=== END OF ANALYSIS ===")


def main():
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(description='Analyze JSON files to extract module titles.')
    parser.add_argument('directory', help='Path to the directory containing card files (e.g., "cards")')
    args = parser.parse_args()
    
    logger.info(f"Starting modules analysis from directory: {args.directory}")
    analyze_module_titles(args.directory)


if __name__ == "__main__":
    main()