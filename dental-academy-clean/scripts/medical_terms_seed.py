#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Full seed file for a comprehensive medical terminology flashcard system.
Imports 250 medical terms across 5 difficulty tiers (Basic to Ultra-Elite).

Usage:
    python scripts/medical_terms_full_seed.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from extensions import db

# Try to import MedicalTerm, if it doesn't exist yet, define it here
try:
    from models import MedicalTerm, UserTermProgress
except ImportError:
    print("⚠️ MedicalTerm models not found in models.py")
    print("This is expected in Phase 1. Models should be added to models.py separately.")
    sys.exit(1)


# ====================================================================
# I. ДАННЫЕ ТЕРМИНОВ (250 ТЕРМИНОВ)
# ====================================================================

# 1. BASIC_TERMS (A1-B1) - 50 terms
BASIC_TERMS = [
    # ANATOMY - 10
    ('het hart', 'heart', 'anatomy_basic'), ('de long', 'lung', 'anatomy_basic'), 
    ('de maag', 'stomach', 'anatomy_basic'), ('de lever', 'liver', 'anatomy_basic'), 
    ('de nier', 'kidney', 'anatomy_basic'), ('het brein', 'brain', 'anatomy_basic'), 
    ('de keel', 'throat', 'anatomy_basic'), ('het bloedvat', 'blood vessel', 'anatomy_basic'), 
    ('de spier', 'muscle', 'anatomy_basic'), ('het bot', 'bone', 'anatomy_basic'),
    # SYMPTOMS - 10
    ('de pijn', 'pain', 'symptoms_basic'), ('de koorts', 'fever', 'symptoms_basic'), 
    ('de hoest', 'cough', 'symptoms_basic'), ('de hoofdpijn', 'headache', 'symptoms_basic'), 
    ('de misselijkheid', 'nausea', 'symptoms_basic'), ('het braken', 'vomiting', 'symptoms_basic'), 
    ('de diarree', 'diarrhea', 'symptoms_basic'), ('de vermoeidheid', 'fatigue', 'symptoms_basic'), 
    ('de duizeligheid', 'dizziness', 'symptoms_basic'), ('de kortademigheid', 'shortness of breath', 'symptoms_basic'),
    # DISEASES - 10
    ('de diabetes', 'diabetes', 'diseases_basic'), ('de hypertensie', 'hypertension', 'diseases_basic'), 
    ('de pneumonie', 'pneumonia', 'diseases_basic'), ('de griep', 'influenza', 'diseases_basic'), 
    ('het eczeem', 'eczema', 'diseases_basic'), ('de asthma', 'asthma', 'diseases_basic'), 
    ('de artritis', 'arthritis', 'diseases_basic'), ('de beroerte', 'stroke', 'diseases_basic'), 
    ('het hartinfarct', 'heart attack', 'diseases_basic'), ('de kanker', 'cancer', 'diseases_basic'),
    # TREATMENTS - 10
    ('de behandeling', 'treatment', 'treatments_basic'), ('de operatie', 'operation', 'treatments_basic'), 
    ('het medicijn', 'medicine', 'treatments_basic'), ('het antibioticum', 'antibiotic', 'treatments_basic'), 
    ('de injectie', 'injection', 'treatments_basic'), ('de pil', 'pill', 'treatments_basic'), 
    ('de zalf', 'ointment', 'treatments_basic'), ('de fysiotherapie', 'physiotherapy', 'treatments_basic'), 
    ('de radiotherapie', 'radiotherapy', 'treatments_basic'), ('de chirurgie', 'surgery', 'treatments_basic'),
    # DENTAL - 10
    ('de tand', 'tooth', 'dental_basic'), ('de kies', 'molar', 'dental_basic'), 
    ('de snijtand', 'incisor', 'dental_basic'), ('het tandvlees', 'gum', 'dental_basic'), 
    ('de cariës', 'cavity', 'dental_basic'), ('de parodontitis', 'periodontitis', 'dental_basic'), 
    ('de tandborstel', 'toothbrush', 'dental_basic'), ('de tandpasta', 'toothpaste', 'dental_basic'), 
    ('de vulling', 'filling', 'dental_basic'), ('de kroon', 'crown', 'dental_basic'),
]

# 2. ADVANCED_TERMS (B2-C1) - 50 terms
ADVANCED_TERMS = [
    # ANATOMY_ADVANCED - 10
    ('het cerebellum', 'cerebellum', 'anatomy_advanced'), ('de hypothalamus', 'hypothalamus', 'anatomy_advanced'), 
    ('de oesofagus', 'esophagus', 'anatomy_advanced'), ('de trachea', 'trachea', 'anatomy_advanced'), 
    ('het pericardium', 'pericardium', 'anatomy_advanced'), ('de glomerulus', 'glomerulus', 'anatomy_advanced'), 
    ('de wervelkolom', 'vertebral column / spine', 'anatomy_advanced'), ('de aorta', 'aorta', 'anatomy_advanced'), 
    ('het duodenum', 'duodenum', 'anatomy_advanced'), ('de bijnier', 'adrenal gland', 'anatomy_advanced'),
    # PATHOLOGY - 10
    ('de sclerodermie', 'scleroderma', 'pathology_advanced'), ('de trombose', 'thrombosis', 'pathology_advanced'), 
    ('de myocarditis', 'myocarditis', 'pathology_advanced'), ('de nefropathie', 'nephropathy', 'pathology_advanced'), 
    ('de encefalopathie', 'encephalopathy', 'pathology_advanced'), ('de hyperthyreoïdie', 'hyperthyroidism', 'pathology_advanced'), 
    ('het sarcoom', 'sarcoma', 'pathology_advanced'), ('de cirrose', 'cirrhosis', 'pathology_advanced'), 
    ('de diverticulitis', 'diverticulitis', 'pathology_advanced'), ('de polyneuropathie', 'polyneuropathy', 'pathology_advanced'),
    # DIAGNOSTICS_PROCEDURES - 10
    ('de biopsie', 'biopsy', 'diagnostics_advanced'), ('de echografie', 'ultrasound', 'diagnostics_advanced'), 
    ('de endoscopie', 'endoscopy', 'diagnostics_advanced'), ('de auscultatie', 'auscultation', 'diagnostics_advanced'), 
    ('de palpatie', 'palpation', 'diagnostics_advanced'), ('het elektrocardiogram (ECG)', 'electrocardiogram (ECG)', 'diagnostics_advanced'), 
    ('de venapunctie', 'venipuncture', 'diagnostics_advanced'), ('de reanimatie', 'resuscitation', 'diagnostics_advanced'), 
    ('de intubatie', 'intubation', 'diagnostics_advanced'), ('het consult', 'consultation / appointment', 'diagnostics_advanced'),
    # PHARMACOLOGY - 10
    ('de analgetica', 'analgesics', 'pharmacology_advanced'), ('de anticoagulantia', 'anticoagulants', 'pharmacology_advanced'), 
    ('de cytostatica', 'cytostatics', 'pharmacology_advanced'), ('de diuretica', 'diuretics', 'pharmacology_advanced'), 
    ('de sedativa', 'sedatives', 'pharmacology_advanced'), ('de vasoconstrictie', 'vasoconstriction', 'pharmacology_advanced'), 
    ('de farmacokinetiek', 'pharmacokinetics', 'pharmacology_advanced'), ('de werkingsmechanisme', 'mechanism of action', 'pharmacology_advanced'), 
    ('de dosering', 'dosage', 'pharmacology_advanced'), ('de contra-indicatie', 'contraindication', 'pharmacology_advanced'),
    # SYMPTOMATOLOGY_ADVANCED - 10
    ('de dyspneu', 'dyspnea (shortness of breath)', 'symptomatology_advanced'), ('de hemoptyse', 'hemoptysis (coughing up blood)', 'symptomatology_advanced'), 
    ('de paresthesie', 'paresthesia (pins and needles)', 'symptomatology_advanced'), ('het oedeem', 'edema (swelling)', 'symptomatology_advanced'), 
    ('de tachycardie', 'tachycardia (fast heart rate)', 'symptomatology_advanced'), ('de malaise', 'malaise', 'symptomatology_advanced'), 
    ('de icterus', 'jaundice', 'symptomatology_advanced'), ('de convulsie', 'convulsion / seizure', 'symptomatology_advanced'), 
    ('de asfyxie', 'asphyxia', 'symptomatology_advanced'), ('de retentie', 'retention (e.g., of urine)', 'symptomatology_advanced'),
    # HEALTHCARE_ADMINISTRATION - 19 terms (Dutch healthcare system)
    ('de eerstelijn', 'primary care / first-line care', 'healthcare_admin_advanced'), ('de tweedelijn', 'secondary care / second-line care', 'healthcare_admin_advanced'),
    ('de POH-GGZ', 'Primary Care Mental Health Practitioner / Mental Health Practice Support', 'healthcare_admin_advanced'), ('de wachtpost', 'out-of-hours service / emergency service', 'healthcare_admin_advanced'),
    ('het verwijsbeleid', 'referral policy', 'healthcare_admin_advanced'), ('het zorgpad', 'care pathway / clinical pathway', 'healthcare_admin_advanced'),
    ('de zorgverzekeraar', 'health insurer / health insurance company', 'healthcare_admin_advanced'), ('de eigen risico', 'deductible / excess', 'healthcare_admin_advanced'),
    ('de caseload', 'caseload', 'healthcare_admin_advanced'), ('de multidisciplinaire overleg (MDO)', 'Multidisciplinary Consultation / MDT', 'healthcare_admin_advanced'),
    ('het tuchtrecht', 'disciplinary law', 'healthcare_admin_advanced'), ('de Wvggz', 'Mental Health Care Act / Compulsory Mental Health Care Act', 'healthcare_admin_advanced'),
    ('de meldcode huiselijk geweld', 'Domestic Violence Reporting Code', 'healthcare_admin_advanced'), ('het journaal', 'medical journal / patient record', 'healthcare_admin_advanced'),
    ('het beleid', 'policy', 'healthcare_admin_advanced'), ('het SOAP-model', 'SOAP model (Subjective, Objective, Assessment, Plan)', 'healthcare_admin_advanced'),
    ('de overdracht', 'handover / transfer / referral', 'healthcare_admin_advanced'), ('de anamnese', 'medical history / anamnesis', 'healthcare_admin_advanced'),
    ('het patiëntendossier', 'patient file / medical record / patient dossier', 'healthcare_admin_advanced'),
]

# 3. ULTRA_ADVANCED_TERMS (C1-C2) - 50 terms
ULTRA_ADVANCED_TERMS = [
    # PATHOPHYSIOLOGY_RARE - 10
    ('de anafylaxie', 'anaphylaxis', 'pathophysiology_ultra'), ('de ischemie', 'ischemia', 'pathophysiology_ultra'), 
    ('de hypoxie', 'hypoxia', 'pathophysiology_ultra'), ('de disseminated intravasculaire stolling (DIS)', 'disseminated intravascular coagulation (DIC)', 'pathophysiology_ultra'), 
    ('de maligniteit', 'malignancy', 'pathophysiology_ultra'), ('de sepsis', 'sepsis', 'pathophysiology_ultra'), 
    ('het longoedeem', 'pulmonary edema', 'pathophysiology_ultra'), ('de hematoom', 'hematoma', 'pathophysiology_ultra'), 
    ('de metastase', 'metastasis', 'pathophysiology_ultra'), ('de atrofie', 'atrophy', 'pathophysiology_ultra'),
    # INTERVENTION_SURGERY - 10
    ('de laparoscopie', 'laparoscopy', 'intervention_ultra'), ('de stentplaatsing', 'stent placement', 'intervention_ultra'), 
    ('de tracheostomie', 'tracheostomy', 'intervention_ultra'), ('de nefrectomie', 'nephrectomy', 'intervention_ultra'), 
    ('de arteriografie', 'arteriography', 'intervention_ultra'), ('de profylaxe', 'prophylaxis', 'intervention_ultra'), 
    ('de exsudatie', 'exudation', 'intervention_ultra'), ('de ablatie', 'ablation', 'intervention_ultra'), 
    ('de anesthesiologie', 'anesthesiology', 'intervention_ultra'), ('de vitrectomie', 'vitrectomy', 'intervention_ultra'),
    # NEURO_PSYCHO - 10
    ('de parese', 'paresis (partial paralysis)', 'neuro_psycho_ultra'), ('de dysfagie', 'dysphagia (difficulty swallowing)', 'neuro_psycho_ultra'), 
    ('de afasie', 'aphasia', 'neuro_psycho_ultra'), ('de dementie', 'dementia', 'neuro_psycho_ultra'), 
    ('de convulsieve stoornis', 'convulsive disorder', 'neuro_psycho_ultra'), ('de neurotransmitter', 'neurotransmitter', 'neuro_psycho_ultra'), 
    ('de somatische stoornis', 'somatic disorder', 'neuro_psycho_ultra'), ('de psychose', 'psychosis', 'neuro_psycho_ultra'), 
    ('de depressieve episode', 'depressive episode', 'neuro_psycho_ultra'), ('de hallucinatie', 'hallucination', 'neuro_psycho_ultra'),
    # CLINICAL_LATIN - 10
    ('ad hoc', 'ad hoc (for this specific purpose)', 'clinical_latin_ultra'), ('per se', 'per se (by itself, intrinsically)', 'clinical_latin_ultra'), 
    ('status quo', 'status quo (existing state)', 'clinical_latin_ultra'), ('de mortaliteit', 'mortality', 'clinical_latin_ultra'), 
    ('de morbiditeit', 'morbidity', 'clinical_latin_ultra'), ('de incidentie', 'incidence', 'clinical_latin_ultra'), 
    ('de prevalentie', 'prevalence', 'clinical_latin_ultra'), ('de ethiologie', 'etiology (cause of disease)', 'clinical_latin_ultra'), 
    ('in situ', 'in situ (in its original place)', 'clinical_latin_ultra'), ('ex vivo', 'ex vivo (outside the organism)', 'clinical_latin_ultra'),
    # RARE_ANATOMY_GENETICS - 10
    ('het axon', 'axon', 'rare_anatomy_ultra'), ('de dendriet', 'dendrite', 'rare_anatomy_ultra'), 
    ('de mitochondriën (mv.)', 'mitochondria (pl.)', 'rare_anatomy_ultra'), ('het genoom', 'genome', 'rare_anatomy_ultra'), 
    ('de karyotype', 'karyotype', 'rare_anatomy_ultra'), ('de hypofyse', 'pituitary gland', 'rare_anatomy_ultra'), 
    ('de thyroïd', 'thyroid gland', 'rare_anatomy_ultra'), ('de ductus arteriosus', 'ductus arteriosus', 'rare_anatomy_ultra'), 
    ('de vena cava', 'vena cava', 'rare_anatomy_ultra'), ('de pleuraholte', 'pleural cavity', 'rare_anatomy_ultra'),
]

# 4. EXPERT_TERMS (C2+) - 50 terms
EXPERT_TERMS = [
    # EPIDEMIOLOGY_STATISTICS - 10
    ('de cohortstudie', 'cohort study', 'epidemiology_expert'), ('de bias (vertekening)', 'bias', 'epidemiology_expert'), 
    ('de confounding factor', 'confounding factor', 'epidemiology_expert'), ('de randomisatie', 'randomization', 'epidemiology_expert'), 
    ('de significantie', 'significance', 'epidemiology_expert'), ('de hazard ratio', 'hazard ratio', 'epidemiology_expert'), 
    ('de regressie-analyse', 'regression analysis', 'epidemiology_expert'), ('de incidentiecijfer', 'incidence rate', 'epidemiology_expert'), 
    ('de validiteit', 'validity', 'epidemiology_expert'), ('de betrouwbaarheid', 'reliability / trustworthiness', 'epidemiology_expert'),
    # ETHICS_LAW - 10
    ('de informed consent', 'informed consent', 'ethics_expert'), ('de autonomie', 'autonomy', 'ethics_expert'), 
    ('de non-maleficence', 'non-maleficence (do no harm)', 'ethics_expert'), ('de vertrouwelijkheid', 'confidentiality', 'ethics_expert'), 
    ('de palliatieve zorg', 'palliative care', 'ethics_expert'), ('de euthanasie', 'euthanasia', 'ethics_expert'), 
    ('de medische aansprakelijkheid', 'medical liability', 'ethics_expert'), ('de second opinion', 'second opinion', 'ethics_expert'), 
    ('de zorgstandaard', 'care standard', 'ethics_expert'), ('de triage', 'triage', 'ethics_expert'),
    # ADVANCED_IMAGING - 10
    ('de magnetische resonantiebeeldvorming (MRI)', 'magnetic resonance imaging (MRI)', 'imaging_expert'), ('de computertomografie (CT)', 'computed tomography (CT)', 'imaging_expert'), 
    ('de nucleaire geneeskunde', 'nuclear medicine', 'imaging_expert'), ('het scintigram', 'scintigram', 'imaging_expert'), 
    ('de perfusie', 'perfusion', 'imaging_expert'), ('de resolutie', 'resolution', 'imaging_expert'), 
    ('de radio-opaciteit', 'radio-opacity', 'imaging_expert'), ('het contrastmiddel', 'contrast agent', 'imaging_expert'), 
    ('de echogeniteit', 'echogenicity', 'imaging_expert'), ('de laesie', 'lesion', 'imaging_expert'),
    # MOLECULAR_GENETICS - 10
    ('de transcriptie', 'transcription', 'molecular_expert'), ('de translatie', 'translation', 'molecular_expert'), 
    ('de mutatie', 'mutation', 'molecular_expert'), ('de allel', 'allele', 'molecular_expert'), 
    ('de recombinatie', 'recombination', 'molecular_expert'), ('de apoptose', 'apoptosis (programmed cell death)', 'molecular_expert'), 
    ('de differentiatie', 'differentiation', 'molecular_expert'), ('de immunoglobuline', 'immunoglobulin', 'molecular_expert'), 
    ('de cytokine', 'cytokine', 'molecular_expert'), ('de receptor', 'receptor', 'molecular_expert'),
    # COMPLEX_CLINICAL_SYNDROMES - 10
    ('de Guillain-Barré syndroom', 'Guillain-Barré syndrome', 'syndromes_expert'), ('de chronische obstructieve longziekte (COPD)', 'chronic obstructive pulmonary disease (COPD)', 'syndromes_expert'), 
    ('de congenitale afwijking', 'congenital anomaly', 'syndromes_expert'), ('de respiratoire insufficiëntie', 'respiratory failure', 'syndromes_expert'), 
    ('de metabool syndroom', 'metabolic syndrome', 'syndromes_expert'), ('de inflammatoire respons', 'inflammatory response', 'syndromes_expert'), 
    ('de prognose', 'prognosis', 'syndromes_expert'), ('de remissie', 'remission', 'syndromes_expert'), 
    ('de exacerbatie', 'exacerbation', 'syndromes_expert'), ('de recidief', 'recurrence / relapse', 'syndromes_expert'),
]

# 5. ULTRA_ELITE_TERMS (C2++ Research) - 50 terms
ULTRA_ELITE_TERMS = [
    # IMMUNOLOGY_VIROLOGY - 10
    ('de auto-immuniteit', 'autoimmunity', 'immunology_elite'), ('de immunocompetentie', 'immunocompetence', 'immunology_elite'), 
    ('het antigeen', 'antigen', 'immunology_elite'), ('het epitoop', 'epitope', 'immunology_elite'), 
    ('de seroconversie', 'seroconversion', 'immunology_elite'), ('de commensale flora', 'commensal flora', 'immunology_elite'), 
    ('de fagocytose', 'phagocytosis', 'immunology_elite'), ('de interferon', 'interferon', 'immunology_elite'), 
    ('de T-cel lymfocyt', 'T-cell lymphocyte', 'immunology_elite'), ('de resistentie', 'resistance', 'immunology_elite'),
    # LABORATORY_INDICATORS - 10
    ('de creatinineklaring', 'creatinine clearance', 'laboratory_elite'), ('de alkalische fosfatase (AF)', 'alkaline phosphatase (ALP)', 'laboratory_elite'), 
    ('de C-reactieve proteïne (CRP)', 'C-reactive protein (CRP)', 'laboratory_elite'), ('de HbA1c', 'HbA1c', 'laboratory_elite'), 
    ('de elektrolytenbalans', 'electrolyte balance', 'laboratory_elite'), ('de osmolaliteit', 'osmolality', 'laboratory_elite'), 
    ('de bilirubinemie', 'bilirubinemia', 'laboratory_elite'), ('de troponine', 'troponin', 'laboratory_elite'), 
    ('de arteriële bloedgasanalyse (ABGA)', 'arterial blood gas analysis (ABG)', 'laboratory_elite'), ('het sedimentatie', 'sedimentation rate', 'laboratory_elite'),
    # PATHOGNOMONIC_SIGNS - 10
    ('de anisocorie', 'anisocoria', 'signs_elite'), ('de asterixis', 'asterixis (flapping tremor)', 'signs_elite'), 
    ('het teken van Babinski', 'Babinski sign', 'signs_elite'), ('de hemianopsie', 'hemianopsia', 'signs_elite'), 
    ('de clonus', 'clonus', 'signs_elite'), ('de cachexie', 'cachexia', 'signs_elite'), 
    ('de nystagmus', 'nystagmus', 'signs_elite'), ('de diaphoresis', 'diaphoresis (profuse sweating)', 'signs_elite'), 
    ('de facies hippocratica', 'facies hippocratica', 'signs_elite'), ('de xanthelasma', 'xanthelasma', 'signs_elite'),
    # RESEARCH_ACADEMIC - 10
    ('de meta-analyse', 'meta-analysis', 'research_elite'), ('de p-waarde', 'p-value', 'research_elite'), 
    ('de interkwartielafstand (IKA)', 'interquartile range (IQR)', 'research_elite'), ('de dubbelblinde studie', 'double-blind study', 'research_elite'), 
    ('de placebogecontroleerde studie', 'placebo-controlled study', 'research_elite'), ('de confounding', 'confounding (bias)', 'research_elite'), 
    ('de farmacovigilantie', 'pharmacovigilance', 'research_elite'), ('de casus-controle studie', 'case-control study', 'research_elite'), 
    ('de reproduceerbaarheid', 'reproducibility', 'research_elite'), ('de nulhypothese', 'null hypothesis', 'research_elite'),
    # RARE_SYNDROMES_DISORDERS - 10
    ('de Ziekte van Crohn', 'Crohn\'s disease', 'syndromes_elite'), ('de ziekte van Wilson', 'Wilson\'s disease', 'syndromes_elite'), 
    ('het syndroom van Cushing', 'Cushing\'s syndrome', 'syndromes_elite'), ('de multiple sclerose (MS)', 'multiple sclerosis (MS)', 'syndromes_elite'), 
    ('de sarcoïdose', 'sarcoidosis', 'syndromes_elite'), ('de vasculitis', 'vasculitis', 'syndromes_elite'), 
    ('de pulmonale hypertensie', 'pulmonary hypertension', 'syndromes_elite'), ('de Ziekte van Parkinson', 'Parkinson\'s disease', 'syndromes_elite'), 
    ('de fibromyalgie', 'fibromyalgia', 'syndromes_elite'), ('het retinoblastoom', 'retinoblastoma', 'syndromes_elite'),
]

# Объединяем все наборы
ALL_TERMS = BASIC_TERMS + ADVANCED_TERMS + ULTRA_ADVANCED_TERMS + EXPERT_TERMS + ULTRA_ELITE_TERMS

# ====================================================================
# II. ОПИСАНИЯ КАТЕГОРИЙ (25 КАТЕГОРИЙ)
# ====================================================================

CATEGORY_DESCRIPTIONS = {
    # 1. BASIC (Difficulty 1-2)
    'anatomy_basic': {'description': 'Basic body structure and organs (A1)', 'difficulty': 1, 'frequency': 5},
    'symptoms_basic': {'description': 'Common patient complaints (A2)', 'difficulty': 1, 'frequency': 5},
    'diseases_basic': {'description': 'Common conditions and diagnoses (A2-B1)', 'difficulty': 2, 'frequency': 4},
    'treatments_basic': {'description': 'General medical treatments and procedures (A2-B1)', 'difficulty': 2, 'frequency': 4},
    'dental_basic': {'description': 'Basic dental terminology (A2)', 'difficulty': 2, 'frequency': 5},
    
    # 2. ADVANCED (Difficulty 3-4)
    'anatomy_advanced': {'description': 'Specialized human body structures and systems (B2)', 'difficulty': 3, 'frequency': 3},
    'pathology_advanced': {'description': 'Complex diseases and medical conditions (B2-C1)', 'difficulty': 4, 'frequency': 4},
    'diagnostics_advanced': {'description': 'Technical medical procedures and examination methods (B2)', 'difficulty': 3, 'frequency': 5},
    'pharmacology_advanced': {'description': 'Drug types, mechanisms, and therapeutic concepts (B2-C1)', 'difficulty': 4, 'frequency': 3},
    'symptomatology_advanced': {'description': 'Clinical, high-level terms for patient complaints (B2)', 'difficulty': 3, 'frequency': 4},
    'healthcare_admin_advanced': {'description': 'Dutch healthcare system administration, policies, and professional practice (B2-C1)', 'difficulty': 4, 'frequency': 5},

    # 3. ULTRA_ADVANCED (Difficulty 4-5)
    'pathophysiology_ultra': {'description': 'Advanced concepts of disease mechanisms and critical care (C1)', 'difficulty': 5, 'frequency': 4},
    'intervention_ultra': {'description': 'Highly specialized surgical and interventional procedures (C1)', 'difficulty': 5, 'frequency': 3},
    'neuro_psycho_ultra': {'description': 'Terms related to neurological deficits and psychological disorders (C1)', 'difficulty': 4, 'frequency': 4},
    'clinical_latin_ultra': {'description': 'Latin phrases, statistical and epidemiological concepts (C1)', 'difficulty': 5, 'frequency': 5},
    'rare_anatomy_ultra': {'description': 'Microscopic anatomy, cellular components, and genetics (C1)', 'difficulty': 4, 'frequency': 3},

    # 4. EXPERT (Difficulty 5)
    'epidemiology_expert': {'description': 'Concepts for research, statistics, and public health (C2)', 'difficulty': 5, 'frequency': 5},
    'ethics_expert': {'description': 'Medical-legal and ethical principles in healthcare (C2)', 'difficulty': 5, 'frequency': 4},
    'imaging_expert': {'description': 'Terminology for radiological reports and complex imaging techniques (C2)', 'difficulty': 5, 'frequency': 4},
    'molecular_expert': {'description': 'Cellular processes, genetics, and immunology (C2)', 'difficulty': 5, 'frequency': 3},
    'syndromes_expert': {'description': 'Diagnostic labels for multi-system diseases and clinical outcomes (C2)', 'difficulty': 5, 'frequency': 5},
    
    # 5. ULTRA_ELITE (Difficulty 5+)
    'immunology_elite': {'description': 'Advanced concepts in immunity, viruses, and microbial resistance (C2+)', 'difficulty': 5, 'frequency': 4},
    'laboratory_elite': {'description': 'Specific, high-level biochemical and hematological test names (C2+)', 'difficulty': 5, 'frequency': 5},
    'signs_elite': {'description': 'Rare or specific clinical signs essential for advanced diagnosis (C2+)', 'difficulty': 5, 'frequency': 4},
    'research_elite': {'description': 'Terminology specific to clinical trial design, biostatistics, and publication (C2+)', 'difficulty': 5, 'frequency': 5},
    'syndromes_elite': {'description': 'Highly specialized hereditary and systemic diseases (C2+)', 'difficulty': 5, 'frequency': 3},
}


# ====================================================================
# III. ОСНОВНАЯ ФУНКЦИЯ SEED
# ====================================================================

def clean_old_categories(app):
    """
    Удаляет все старые термины, чтобы избежать смешивания данных при повторном запуске.
    """
    with app.app_context():
        print("\n🗑️  Cleaning up database...")
        try:
            # Сначала удаляем все записи UserTermProgress, так как они ссылаются на MedicalTerm
            UserTermProgress.query.delete()
            # Затем удаляем все записи MedicalTerm
            MedicalTerm.query.delete()
            db.session.commit()
            print("✅ Database successfully wiped of old terms and progress.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {str(e)}")
            sys.exit(1)


def seed_full_terms(app):
    """
    Import all 250 medical terms into the database.
    """
    with app.app_context():
        print("\n" + "="*80)
        print("🚀 FULL MEDICAL TERMINOLOGY SEED (250 Terms, A1 to C2++)")
        print("="*80)
        
        # Предлагаем очистку перед импортом
        response = input("\nDo you want to **WIPE ALL EXISTING TERMS** before importing 250 new ones? (y/n): ").lower()
        if response == 'y':
            clean_old_categories(app)
        elif MedicalTerm.query.count() > 0:
            print(f"⚠️  {MedicalTerm.query.count()} terms currently exist. Proceeding with UPDATE/INSERT.")
        
        print(f"\n📚 Importing {len(ALL_TERMS)} medical terms...")
        print("-" * 80)
        
        imported_or_updated = 0
        errors = 0
        
        for dutch_term, english_term, category in ALL_TERMS:
            try:
                # Check if term already exists (and update if necessary)
                existing = MedicalTerm.query.filter_by(term_nl=dutch_term).first()
                
                # Get category metadata
                cat_info = CATEGORY_DESCRIPTIONS.get(category, {
                    'description': 'Uncategorized Term',
                    'difficulty': 3,
                    'frequency': 3
                })

                if existing:
                    # Update existing term
                    existing.term_en = english_term
                    existing.definition_nl = cat_info.get('description')
                    existing.category = category
                    existing.difficulty = cat_info.get('difficulty', 3)
                    existing.frequency = cat_info.get('frequency', 3)
                    db.session.add(existing)
                    # print(f"🔄 Updated: {dutch_term} ({category})")
                else:
                    # Create new term
                    term = MedicalTerm(
                        term_nl=dutch_term,
                        term_en=english_term,
                        definition_nl=cat_info.get('description'),
                        category=category,
                        difficulty=cat_info.get('difficulty', 3),
                        frequency=cat_info.get('frequency', 3)
                    )
                    
                    db.session.add(term)
                    # print(f"✅ Imported: {dutch_term} ({category})")

                imported_or_updated += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error importing/updating {dutch_term}: {str(e)}")
                errors += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*80)
            print(f"✅ SEED COMPLETED SUCCESSFULLY!")
            print(f"   📊 Imported/Updated: {imported_or_updated} terms")
            print(f"   ⚠️  Errors: {errors}")
            print(f"   📚 Total unique terms in database: {MedicalTerm.query.count()}")
            print("="*80 + "\n")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ SEED FAILED (Commit Error): {str(e)}")
            return False


def print_stats(app):
    """Print statistics about imported terms grouped by difficulty tier"""
    with app.app_context():
        stats = {
            '1. Basic (A1-B1)': 0,
            '2. Advanced (B2-C1)': 0,
            '3. Ultra-Advanced (C1-C2)': 0,
            '4. Expert (C2)': 0,
            '5. Ultra-Elite (C2+ Research)': 0
        }
        
        category_map = {
            'basic': '1. Basic (A1-B1)',
            'advanced': '2. Advanced (B2-C1)',
            'ultra': '3. Ultra-Advanced (C1-C2)',
            'expert': '4. Expert (C2)',
            'elite': '5. Ultra-Elite (C2+ Research)'
        }
        
        for category_name in CATEGORY_DESCRIPTIONS.keys():
            count = MedicalTerm.query.filter_by(category=category_name).count()
            
            # Определяем уровень сложности по названию категории
            for key_word, tier in category_map.items():
                if key_word in category_name:
                    stats[tier] += count
                    break
        
        print("\n📊 Statistics by Difficulty Tier:")
        print("-" * 50)
        total = 0
        for tier, count in stats.items():
            print(f"   {tier:35} {count:3} terms")
            total += count
        
        print("-" * 50)
        print(f"   {'TOTAL':35} {total:3} terms")
        print()


if __name__ == '__main__':
    # Use Flask app context
    with app.app_context():
        # Run seed
        success = seed_full_terms(app)
        
        # Print stats
        if success:
            print_stats(app)
            sys.exit(0)
        else:
            sys.exit(1)