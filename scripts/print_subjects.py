#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to print all LearningPaths, Subjects and Modules from the database.
Use this to get the correct subject IDs for updating the create_missing_modules.py script.

Usage:
    $ python -m scripts.print_subjects
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import the application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

try:
    from app import app, db
    from models import LearningPath, Subject, Module
except ImportError as e:
    print(f"Error importing application modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_database_structure():
    """
    Print all LearningPaths, Subjects, and a sample of Modules from the database.
    """
    with app.app_context():
        print("\n=== LEARNING PATHS ===")
        print(f"{'ID':<5} {'Name':<50}")
        print("-" * 55)
        
        learning_paths = LearningPath.query.order_by(LearningPath.id).all()
        for lp in learning_paths:
            print(f"{lp.id:<5} {lp.name:<50}")
        
        print("\n=== SUBJECTS ===")
        print(f"{'ID':<5} {'Learning Path ID':<15} {'Name':<60}")
        print("-" * 80)
        
        subjects = Subject.query.order_by(Subject.learning_path_id, Subject.id).all()
        
        # Dictionary for the subject_map
        subject_map = {}
        
        for subject in subjects:
            print(f"{subject.id:<5} {subject.learning_path_id:<15} {subject.name:<60}")
            # Add to the subject_map
            subject_map[subject.name] = subject.id
        
        print("\n=== FIRST 10 MODULES (SAMPLE) ===")
        print(f"{'ID':<5} {'Subject ID':<10} {'Title':<70}")
        print("-" * 85)
        
        modules = Module.query.order_by(Module.id).limit(10).all()
        for module in modules:
            print(f"{module.id:<5} {module.subject_id:<10} {module.title:<70}")
        
        # Print the subject_map for create_missing_modules.py
        print("\n=== SUBJECT MAP FOR create_missing_modules.py ===")
        print("subject_map = {")
        for name, id in subject_map.items():
            print(f"    \"{name}\": {id},")
        print("}")


if __name__ == "__main__":
    print_database_structure()