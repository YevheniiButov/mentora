#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to initialize the full structure of the educational platform database.
Creates the following hierarchy:
- LearningPath (Level 1: Exam Categories)
- Subject (Level 2: Main Topics/Sections)
- Module (Level 3: Subtopics)
- Final Test Modules and Test records

Usage:
    With Flask app context:
    $ flask shell
    >>> from scripts.init_full_structure import initialize_structure
    >>> initialize_structure()

    OR from command line:
    $ python -m scripts.init_full_structure
"""

import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

try:
    from app import app, db
    from models import LearningPath, Subject, Module, Test
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

# Define the structure of the educational content
STRUCTURE = {
    "Theory (MCQ)": [
        {
            "name": "Basic Medical Sciences",
            "description": "Fundamental biomedical concepts for dentistry",
            "icon": "activity",
            "modules": [
                "Saliva: Introduction and Overview",
                "Salivary Glands: Anatomy and Histology",
                # Add all other Basic Medical Sciences modules here
            ],
            "has_final_test": True
        },
        {
            "name": "THK I: Cariology/Endo/Perio/Pedo",
            "description": "Tooth-preserving treatments and related subjects",
            "icon": "tool",
            "modules": [
                "Fundamentals and Pathogenesis of Caries",
                "Epidemiology and Risk Factors",
                # Add all other Cariology modules here
                "Endodontics: Introduction and Morphology",
                # Add all other Endodontics modules here
                "Pediatric Dentistry: Tooth Development and Eruption",
                # Add all other Pediatric Dentistry modules here
                "Periodontology: Anatomy and Histology",
                # Add all other Periodontology modules here
            ],
            "has_final_test": True
        },
        {
            "name": "THK II: Prostho/Surgery/Ortho",
            "description": "Restorative dentistry, surgical procedures, and orthodontics",
            "icon": "grid",
            "modules": [
                # Add all THK II modules here
            ],
            "has_final_test": True
        },
        {
            "name": "Radiology",
            "description": "Dental imaging techniques and interpretation",
            "icon": "camera",
            "modules": [
                # Add all Radiology modules here
            ],
            "has_final_test": True
        },
        {
            "name": "Statistics",
            "description": "Statistical methods for healthcare research",
            "icon": "bar-chart-2",
            "modules": [
                # Add all Statistics modules here
            ],
            "has_final_test": True
        },
        {
            "name": "Methodology",
            "description": "Research methodology in dentistry",
            "icon": "layers",
            "modules": [
                # Add all Methodology modules here
            ],
            "has_final_test": True
        }
    ],
    "Short Answer": [
        # Define subjects for Short Answer learning path
    ],
    "Clinical Cases (Casus)": [
        {
            "name": "Case 1 (Comprehensive Treatment)",
            "description": "Complex cases requiring comprehensive treatment planning",
            "icon": "folder",
            "modules": [
                # Add all Case 1 modules here
            ],
            "has_final_test": True
        },
        {
            "name": "Case 2 (Pediatric/ICDAS)",
            "description": "Pediatric cases with ICDAS classification",
            "icon": "folder",
            "modules": [
                # Add all Case 2 modules here
            ],
            "has_final_test": True
        },
        {
            "name": "Case 3 (Trauma/Resorption)",
            "description": "Cases involving dental trauma and resorption",
            "icon": "folder",
            "modules": [
                # Add all Case 3 modules here
            ],
            "has_final_test": True
        }
    ],
    "Practical Part (Simodont, etc.)": [
        # Define subjects for Practical Part learning path
    ],
    "Interview Intake": [
        # Define subjects for Interview Intake learning path
    ]
}


def initialize_structure():
    """Initialize the full structure of learning paths, subjects, and modules."""
    # Use Flask application context if not already in one
    with app.app_context():
        try:
            # Start transaction
            session = db.session

            # 1. Create Learning Paths (if they don't exist)
            logger.info("Checking and creating Learning Paths...")
            learning_paths = {}
            for i, path_name in enumerate(STRUCTURE.keys(), 1):
                path = LearningPath.query.filter_by(name=path_name).first()
                if not path:
                    path = LearningPath(
                        name=path_name,
                        description=f"Exam category: {path_name}",
                        order=i,
                        icon="list-task" if i > 5 else ["list-task", "pencil-square", "card-list", "hammer", "chat-quote"][i-1]
                    )
                    session.add(path)
                    logger.info(f"Created LearningPath: {path_name}")
                else:
                    logger.info(f"LearningPath already exists: {path_name}")
                learning_paths[path_name] = path

            # Commit to ensure learning paths have IDs
            session.commit()

            # 2. Create Subjects and Modules
            for path_name, subjects in STRUCTURE.items():
                learning_path = learning_paths[path_name]
                
                for i, subject_data in enumerate(subjects, 1):
                    # Check if subject exists
                    subject = Subject.query.filter_by(
                        name=subject_data["name"],
                        learning_path_id=learning_path.id
                    ).first()
                    
                    if not subject:
                        # Create new subject
                        subject = Subject(
                            name=subject_data["name"],
                            description=subject_data.get("description", ""),
                            order=i,
                            icon=subject_data.get("icon", "folder2-open"),
                            learning_path_id=learning_path.id
                        )
                        session.add(subject)
                        logger.info(f"Created Subject: {subject_data['name']} (in {path_name})")
                    else:
                        logger.info(f"Subject already exists: {subject_data['name']} (in {path_name})")
                    
                    # Commit to ensure subject has ID
                    session.commit()
                    
                    # Create modules for this subject
                    for j, module_title in enumerate(subject_data.get("modules", []), 1):
                        module = Module.query.filter_by(
                            title=module_title,
                            subject_id=subject.id
                        ).first()
                        
                        if not module:
                            # Create module
                            module = Module(
                                title=module_title,
                                description=f"Content for {module_title}",
                                order=j,
                                icon="file-earmark-text",
                                module_type="content",
                                is_premium=False,
                                subject_id=subject.id,
                                is_final_test=False
                            )
                            session.add(module)
                            logger.info(f"Created Module: {module_title} (in {subject_data['name']})")
                        else:
                            logger.info(f"Module already exists: {module_title} (in {subject_data['name']})")
                    
                    # Create final test module if needed
                    if subject_data.get("has_final_test", False):
                        final_test_title = f"Final Test: {subject_data['name']}"
                        final_test_module = Module.query.filter_by(
                            title=final_test_title,
                            subject_id=subject.id,
                            is_final_test=True
                        ).first()
                        
                        if not final_test_module:
                            final_test_module = Module(
                                title=final_test_title,
                                description=f"Final assessment for {subject_data['name']}",
                                order=999,  # Place at the end
                                icon="check-circle",
                                module_type="test",
                                is_premium=True,
                                subject_id=subject.id,
                                is_final_test=True
                            )
                            session.add(final_test_module)
                            logger.info(f"Created Final Test Module: {final_test_title}")
                        else:
                            logger.info(f"Final Test Module already exists: {final_test_title}")
                        
                        # Commit to ensure final test module has ID
                        session.commit()
                        
                        # Create Test record associated with the subject
                        test = Test.query.filter_by(subject_final_test_id=subject.id).first()
                        if not test:
                            test = Test(
                                title=f"Final Test: {subject_data['name']}",
                                description=f"Comprehensive assessment for {subject_data['name']}",
                                test_type="final_subject",
                                subject_final_test_id=subject.id
                            )
                            session.add(test)
                            logger.info(f"Created Test record for subject: {subject_data['name']}")
                        else:
                            logger.info(f"Test record already exists for subject: {subject_data['name']}")
            
            # Final commit for all changes
            session.commit()
            logger.info("Database structure initialization completed successfully!")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error initializing database structure: {e}")
            raise


if __name__ == "__main__":
    with app.app_context():
        logger.info("Starting database structure initialization...")
        initialize_structure()
        logger.info("Structure initialization completed.")