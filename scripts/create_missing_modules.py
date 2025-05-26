#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create missing modules identified by the analyze_modules.py script.
This script will create all the modules that are found in JSON files but missing from the database.

Usage:
    $ python -m scripts.create_missing_modules
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
    from models import Module, Subject
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


def create_missing_modules():
    """Create all missing modules identified by the analysis."""
    with app.app_context():
        # Dictionary mapping subject names to their IDs
        # Updated with actual subject IDs from your database
        subject_map = {
            "Basic Medical Sciences": 1,
            "THK I: Cariology/Endo/Perio/Pedo": 2,
            "THK II: Prostho/Surgery/Ortho": 3,
            "Radiology": 4,
            "Statistics": 5,
            "Methodology": 6,
            "Case 1 (Comprehensive Treatment)": 7,
            "Case 2 (Pediatric/ICDAS)": 8,
            "Case 3 (Trauma/Resorption)": 9,
        }
        
        # Default subject ID to use if not specified
        default_subject_id = 1  # Basic Medical Sciences
        
        # List of modules to create (title, subject_name)
        modules_to_create = [
            ('Clinical Cases', 'Basic Medical Sciences'),
            ('Clinical Cases (Caries)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Diagnosis of Caries', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Complications And Procedural Errors', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Complications and Procedural Errors', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Complications and procedural errors', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Endo-Perio, Systemic Links, And Trauma', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Endo-Perio, Systemic Links, and Trauma', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Endo-perio, systemic links, and trauma', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Final Test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Management Of Dental Pain', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Management of Dental Pain', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Management of dental pain', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Microbiology And Pathogenesis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Microbiology and Pathogenesis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Microbiology and pathogenesis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Pulp Pathology And Diagnosis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Pulp Pathology and Diagnosis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Pulp pathology and diagnosis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Surgical Endodontics And Alternatives', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Surgical Endodontics and Alternatives', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Surgical endodontics and alternatives', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Treatment Overview And Techniques', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Treatment Overview and Techniques', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Endodontics: Treatment overview and techniques', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Features in Children', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Final Test on Caries Management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Future of Cariology', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Invasive Methods and Minimal Preparation', 'Basic Medical Sciences'),
            ('Non-Surgical Intervention and Prevention', 'Basic Medical Sciences'),
            ('Pediatric Dentistry: Behavior Management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Behavior management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Caries Prevention Strategies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Caries prevention strategies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Dental Anatomy And Anomalies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Dental Anatomy and Anomalies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Dental Trauma Management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Dental anatomy and anomalies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Dental trauma management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Early Childhood Caries (ECC)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Early Childhood Caries (Ecc)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Early childhood caries (ecc)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Final Test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Infections And Emergencies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Infections and Emergencies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Infections and emergencies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Oral Pathology', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Oral pathology', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Pain And Anxiety Control', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Pain and Anxiety Control', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Pain and anxiety control', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Pulp Therapy', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Pulp therapy', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Restorative Techniques And Materials', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Restorative Techniques and Materials', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Restorative techniques and materials', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Special Healthcare Needs (SHCN)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Special Healthcare Needs (Shcn)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Pediatric Dentistry: Special healthcare needs (shcn)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Classification Of Diseases', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Classification of Diseases', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Classification of diseases', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Clinical Diagnosis And Staging', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Clinical Diagnosis and Staging', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Clinical diagnosis and staging', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Diagnosis: Clinical And Radiographic Examination', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Diagnosis: Clinical and Radiographic Examination', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Diagnosis: clinical and radiographic examination', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Etiology And Biofilm', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Etiology and Biofilm', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Etiology and biofilm', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Final Test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Microbial Plaque Hypotheses', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Microbial plaque hypotheses', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Non-Surgical Therapy (Initial And Maintenance Phases)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Non-Surgical Therapy (Initial and Maintenance Phases)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Non-surgical therapy (initial and maintenance phases)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Pathogenesis And Progression', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Pathogenesis and Progression', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Pathogenesis and progression', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Periodontal Plastic Surgery (Mucogingival Therapy, Esthetic Procedures)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Periodontal plastic surgery (mucogingival therapy, esthetic procedures)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk Factors And Risk Assessment', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk Factors And Systemic Associations', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk Factors and Risk Assessment', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk Factors and Systemic Associations', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk factors and risk assessment', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Risk factors and systemic associations', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Surgical Therapy (Principles, Indications, Techniques)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Periodontology: Surgical therapy (principles, indications, techniques)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('Risk Assessment and Strategy', 'Basic Medical Sciences'),
            ('Saliva Management: Artificial Saliva And Stimulants', 'Basic Medical Sciences'),
            ('Saliva Management: Artificial Saliva and Stimulants', 'Basic Medical Sciences'),
            ('Saliva Management: Artificial saliva and stimulants', 'Basic Medical Sciences'),
            ('Saliva Management: Substitutes And Stimulants', 'Basic Medical Sciences'),
            ('Saliva Management: Substitutes and Stimulants', 'Basic Medical Sciences'),
            ('Saliva Management: Substitutes and stimulants', 'Basic Medical Sciences'),
            ('Saliva Secretion: Physiology And Regulation', 'Basic Medical Sciences'),
            ('Saliva Secretion: Physiology and Regulation', 'Basic Medical Sciences'),
            ('Saliva Secretion: Physiology and regulation', 'Basic Medical Sciences'),
            ('Saliva: Clinical Applications In Dentistry', 'Basic Medical Sciences'),
            ('Saliva: Clinical Applications in Dentistry', 'Basic Medical Sciences'),
            ('Saliva: Clinical Relevance In Dentistry', 'Basic Medical Sciences'),
            ('Saliva: Clinical Relevance in Dentistry', 'Basic Medical Sciences'),
            ('Saliva: Clinical applications in dentistry', 'Basic Medical Sciences'),
            ('Saliva: Clinical relevance in dentistry', 'Basic Medical Sciences'),
            ('Saliva: Composition And Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Composition And Components', 'Basic Medical Sciences'),
            ('Saliva: Composition and Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Composition and Components', 'Basic Medical Sciences'),
            ('Saliva: Composition and biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Composition and components', 'Basic Medical Sciences'),
            ('Saliva: Diagnostic Applications And Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Diagnostic Applications and Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Diagnostic applications and biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Diagnostics And Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Diagnostics and Biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Diagnostics and biomarkers', 'Basic Medical Sciences'),
            ('Saliva: Final Test', 'Basic Medical Sciences'),
            ('Saliva: Final test', 'Basic Medical Sciences'),
            ('Saliva: Functions And Clinical Significance', 'Basic Medical Sciences'),
            ('Saliva: Functions and Clinical Significance', 'Basic Medical Sciences'),
            ('Saliva: Functions and clinical significance', 'Basic Medical Sciences'),
            ('Saliva: Future Perspectives And Advanced Diagnostics', 'Basic Medical Sciences'),
            ('Saliva: Future Perspectives and Advanced Diagnostics', 'Basic Medical Sciences'),
            ('Saliva: Future perspectives and advanced diagnostics', 'Basic Medical Sciences'),
            ('Saliva: Immune And Antimicrobial Functions', 'Basic Medical Sciences'),
            ('Saliva: Immune And Antimicrobial Roles', 'Basic Medical Sciences'),
            ('Saliva: Immune and Antimicrobial Functions', 'Basic Medical Sciences'),
            ('Saliva: Immune and Antimicrobial Roles', 'Basic Medical Sciences'),
            ('Saliva: Immune and antimicrobial functions', 'Basic Medical Sciences'),
            ('Saliva: Immune and antimicrobial roles', 'Basic Medical Sciences'),
            ('Saliva: Key Physiological Functions', 'Basic Medical Sciences'),
            ('Saliva: Key physiological functions', 'Basic Medical Sciences'),
            ('Saliva: Specific Functions In Oral Health', 'Basic Medical Sciences'),
            ('Saliva: Specific Functions in Oral Health', 'Basic Medical Sciences'),
            ('Saliva: Specific functions in oral health', 'Basic Medical Sciences'),
            ('Saliva: Wound Healing And Repair Mechanisms', 'Basic Medical Sciences'),
            ('Saliva: Wound Healing And Tissue Repair', 'Basic Medical Sciences'),
            ('Saliva: Wound Healing and Repair Mechanisms', 'Basic Medical Sciences'),
            ('Saliva: Wound Healing and Tissue Repair', 'Basic Medical Sciences'),
            ('Saliva: Wound healing and repair mechanisms', 'Basic Medical Sciences'),
            ('Saliva: Wound healing and tissue repair', 'Basic Medical Sciences'),
            ('Salivary Gland Disorders: Pathology And Management', 'Basic Medical Sciences'),
            ('Salivary Gland Disorders: Pathology and Management', 'Basic Medical Sciences'),
            ('Salivary Gland Disorders: Pathology and management', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging And Oral Health Implications', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging Effects And Geriatric Considerations', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging Effects and Geriatric Considerations', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging and Oral Health Implications', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging and oral health implications', 'Basic Medical Sciences'),
            ('Salivary Glands: Aging effects and geriatric considerations', 'Basic Medical Sciences'),
            ('Salivary Glands: Impact Of Systemic Diseases', 'Basic Medical Sciences'),
            ('Salivary Glands: Impact of Systemic Diseases', 'Basic Medical Sciences'),
            ('Salivary Glands: Impact of systemic diseases', 'Basic Medical Sciences'),
            ('Salivary Glands: Systemic Diseases And Dysfunction', 'Basic Medical Sciences'),
            ('Salivary Glands: Systemic Diseases and Dysfunction', 'Basic Medical Sciences'),
            ('Salivary Glands: Systemic diseases and dysfunction', 'Basic Medical Sciences'),
            ('clinical cases', 'Basic Medical Sciences'),
            ('clinical cases (caries)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('diagnosis of caries', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: complications and procedural errors', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: endo-perio, systemic links, and trauma', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: management of dental pain', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: microbiology and pathogenesis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: pulp pathology and diagnosis', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: surgical endodontics and alternatives', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('endodontics: treatment overview and techniques', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('features in children', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('final test on caries management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('future of cariology', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('invasive methods and minimal preparation', 'Basic Medical Sciences'),
            ('non-surgical intervention and prevention', 'Basic Medical Sciences'),
            ('pediatric dentistry: behavior management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: caries prevention strategies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: dental anatomy and anomalies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: dental trauma management', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: early childhood caries (ecc)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: infections and emergencies', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: oral pathology', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: pain and anxiety control', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: pulp therapy', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: restorative techniques and materials', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('pediatric dentistry: special healthcare needs (shcn)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: classification of diseases', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: clinical diagnosis and staging', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: diagnosis: clinical and radiographic examination', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: etiology and biofilm', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: final test', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: microbial plaque hypotheses', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: non-surgical therapy (initial and maintenance phases)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: pathogenesis and progression', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: periodontal plastic surgery (mucogingival therapy, esthetic procedures)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: risk factors and risk assessment', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: risk factors and systemic associations', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('periodontology: surgical therapy (principles, indications, techniques)', 'THK I: Cariology/Endo/Perio/Pedo'),
            ('risk assessment and strategy', 'Basic Medical Sciences'),
            ('saliva management: artificial saliva and stimulants', 'Basic Medical Sciences'),
            ('saliva management: substitutes and stimulants', 'Basic Medical Sciences'),
            ('saliva secretion: physiology and regulation', 'Basic Medical Sciences'),
            ('saliva: clinical applications in dentistry', 'Basic Medical Sciences'),
            ('saliva: clinical relevance in dentistry', 'Basic Medical Sciences'),
            ('saliva: composition and biomarkers', 'Basic Medical Sciences'),
            ('saliva: composition and components', 'Basic Medical Sciences'),
            ('saliva: diagnostic applications and biomarkers', 'Basic Medical Sciences'),
            ('saliva: diagnostics and biomarkers', 'Basic Medical Sciences'),
            ('saliva: final test', 'Basic Medical Sciences'),
            ('saliva: functions and clinical significance', 'Basic Medical Sciences'),
            ('saliva: future perspectives and advanced diagnostics', 'Basic Medical Sciences'),
            ('saliva: immune and antimicrobial functions', 'Basic Medical Sciences'),
            ('saliva: immune and antimicrobial roles', 'Basic Medical Sciences'),
            ('saliva: key physiological functions', 'Basic Medical Sciences'),
            ('saliva: specific functions in oral health', 'Basic Medical Sciences'),
            ('saliva: wound healing and repair mechanisms', 'Basic Medical Sciences'),
            ('saliva: wound healing and tissue repair', 'Basic Medical Sciences'),
            ('salivary gland disorders: pathology and management', 'Basic Medical Sciences'),
            ('salivary glands: aging and oral health implications', 'Basic Medical Sciences'),
            ('salivary glands: aging effects and geriatric considerations', 'Basic Medical Sciences'),
            ('salivary glands: impact of systemic diseases', 'Basic Medical Sciences'),
            ('salivary glands: systemic diseases and dysfunction', 'Basic Medical Sciences'),
        ]
        
        # Find existing modules to avoid duplicates (including case-insensitive matching)
        existing_modules_titles = {}
        for module in Module.query.all():
            existing_modules_titles[module.title.lower()] = module.title
        
        # Only process unique module titles
        unique_titles = set()
        modules_to_create_filtered = []
        
        for title, subject_name in modules_to_create:
            # Skip if this exact title already exists in the database
            if title in existing_modules_titles.values():
                logger.info(f"Module already exists (exact match): {title}")
                continue
            
            # Skip if a case-insensitive match already exists in the database
            if title.lower() in existing_modules_titles:
                logger.info(f"Module already exists (case match): {title} as {existing_modules_titles[title.lower()]}")
                continue
            
            # Skip if we've already added this title to our filtered list (case-insensitive)
            title_lower = title.lower()
            if title_lower in unique_titles:
                continue
            
            # Add to our filtered list
            unique_titles.add(title_lower)
            modules_to_create_filtered.append((title, subject_name))
        
        logger.info(f"Found {len(modules_to_create_filtered)} unique modules to create")
        
        # Create each module
        created_count = 0
        for title, subject_name in modules_to_create_filtered:
            # Get subject ID from the mapping, or use default
            subject_id = subject_map.get(subject_name, default_subject_id)
            
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
            
            # Special handling for final test modules
            if "final test" in title.lower():
                module.is_final_test = True
                module.module_type = "test"
                module.icon = "check-circle"
                module.is_premium = True
            
            db.session.add(module)
            created_count += 1
            logger.info(f"Created module: {title} (Subject ID: {subject_id})")
        
        # Commit changes
        if created_count > 0:
            db.session.commit()
            logger.info(f"Created {created_count} new modules")
        else:
            logger.info("No new modules created")


if __name__ == "__main__":
    create_missing_modules()