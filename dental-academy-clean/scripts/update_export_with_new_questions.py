#!/usr/bin/env python3
"""
Скрипт для добавления 20 новых вопросов в существующий экспортированный JSON файл
"""

import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_new_questions():
    """Создать 20 новых вопросов"""
    
    new_questions = [
        # COMMUNICATION (5 вопросов)
        {
            "id": 381,
            "text": "Een 45-jarige patiënt komt voor een controle en toont angst voor de tandarts. De patiënt heeft een grote restauratie op een kies (zie röntgenfoto). Wat is de beste eerste stap in de communicatie?",
            "options": ["Direct de behandeling bespreken", "De angst negeren en focussen op de procedure", "Luisteren naar de zorgen van de patiënt en empathie tonen", "De patiënt doorverwijzen naar een andere tandarts"],
            "correct_answer_index": 2,
            "correct_answer_text": "Luisteren naar de zorgen van de patiënt en empathie tonen",
            "explanation": "De eerste stap in angstmanagement is altijd het erkennen van de angst en empathie tonen. Dit bouwt vertrouwen op en maakt verdere communicatie mogelijk. Volgens Nederlandse richtlijnen moet angst altijd serieus worden genomen voordat behandeling wordt besproken.",
            "category": "Communication Skills",
            "domain": "COMMUNICATION",
            "domain_info": {
                "code": "COMMUNICATION",
                "name": "Communication Skills",
                "weight_percentage": 6.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Patient communication scenario with radiographic image",
            "learning_objectives": ["Angstmanagement", "Empatische communicatie", "Nederlandse richtlijnen"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["communicatie", "angst", "patiëntenzorg"],
            "irt_parameters": {
                "difficulty": -0.8,
                "discrimination": 1.1,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 382,
            "text": "Een patiënt heeft een grote cariëslaesie die endodontische behandeling vereist. Bij het verkrijgen van geïnformeerde toestemming moet u:",
            "options": ["Alleen de procedure uitleggen", "De procedure, risico's, alternatieven en prognose uitleggen", "Alleen de kosten bespreken", "De patiënt laten tekenen zonder uitleg"],
            "correct_answer_index": 1,
            "correct_answer_text": "De procedure, risico's, alternatieven en prognose uitleggen",
            "explanation": "Geïnformeerde toestemming vereist volledige uitleg van procedure, risico's, alternatieven en verwachte uitkomst. Dit is wettelijk verplicht in Nederland en essentieel voor ethische tandheelkundige zorg.",
            "category": "Informed Consent",
            "domain": "COMMUNICATION",
            "domain_info": {
                "code": "COMMUNICATION",
                "name": "Communication Skills",
                "weight_percentage": 6.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Informed consent for endodontic treatment",
            "learning_objectives": ["Geïnformeerde toestemming", "Wettelijke verplichtingen", "Ethische zorg"],
            "image_url": "xray_filling.jpg",
            "tags": ["toestemming", "endodontie", "ethiek"],
            "irt_parameters": {
                "difficulty": -0.5,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 383,
            "text": "Een patiënt van Marokkaanse afkomst weigert behandeling door een vrouwelijke tandarts. Wat is de beste aanpak?",
            "options": ["De patiënt dwingen om door de vrouwelijke tandarts behandeld te worden", "De patiënt weigeren en doorverwijzen", "Respect tonen voor culturele overtuigingen en een mannelijke collega vragen", "De patiënt beschuldigen van discriminatie"],
            "correct_answer_index": 2,
            "correct_answer_text": "Respect tonen voor culturele overtuigingen en een mannelijke collega vragen",
            "explanation": "Culturele gevoeligheid is essentieel in de Nederlandse gezondheidszorg. Respect voor culturele overtuigingen moet worden getoond, zolang dit de kwaliteit van zorg niet schaadt. Samenwerking met collega's is hier de juiste oplossing.",
            "category": "Cultural Sensitivity",
            "domain": "COMMUNICATION",
            "domain_info": {
                "code": "COMMUNICATION",
                "name": "Communication Skills",
                "weight_percentage": 6.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Cultural sensitivity in dental practice",
            "learning_objectives": ["Culturele gevoeligheid", "Respectvolle zorg", "Collegiale samenwerking"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["cultuur", "respect", "samenwerking"],
            "irt_parameters": {
                "difficulty": 0.2,
                "discrimination": 1.0,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 384,
            "text": "U ontdekt een grote cariëslaesie die mogelijk tot extractie leidt. Bij het breken van slecht nieuws moet u:",
            "options": ["De informatie direct en hard geven", "De informatie uitstellen tot de volgende afspraak", "De informatie voorzichtig maar eerlijk geven met ondersteuning", "De informatie alleen aan de familie geven"],
            "correct_answer_index": 2,
            "correct_answer_text": "De informatie voorzichtig maar eerlijk geven met ondersteuning",
            "explanation": "Het breken van slecht nieuws vereist een gebalanceerde aanpak: eerlijkheid gecombineerd met empathie en ondersteuning. De SPIKES-methode (Setting, Perception, Invitation, Knowledge, Empathy, Summary) is de gouden standaard.",
            "category": "Breaking Bad News",
            "domain": "COMMUNICATION",
            "domain_info": {
                "code": "COMMUNICATION",
                "name": "Communication Skills",
                "weight_percentage": 6.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Breaking bad news about tooth extraction",
            "learning_objectives": ["SPIKES-methode", "Empatische communicatie", "Patiëntondersteuning"],
            "image_url": "xray_endodontic.jpg",
            "tags": ["slecht nieuws", "empathie", "SPIKES"],
            "irt_parameters": {
                "difficulty": 0.0,
                "discrimination": 1.2,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 385,
            "text": "Een collega maakt een fout in de behandeling van een patiënt. Wat is de beste manier om dit te bespreken?",
            "options": ["De fout direct in het bijzijn van de patiënt bespreken", "De fout negeren om de relatie te beschermen", "De fout privé en constructief bespreken", "De fout direct melden bij de inspectie"],
            "correct_answer_index": 2,
            "correct_answer_text": "De fout privé en constructief bespreken",
            "explanation": "Collegiale communicatie moet respectvol en constructief zijn. Fouten moeten privé worden besproken met focus op leren en verbetering, niet op schuld. Dit bevordert een veilige leercultuur in de praktijk.",
            "category": "Colleague Communication",
            "domain": "COMMUNICATION",
            "domain_info": {
                "code": "COMMUNICATION",
                "name": "Communication Skills",
                "weight_percentage": 6.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Collegial communication about treatment errors",
            "learning_objectives": ["Collegiale communicatie", "Constructieve feedback", "Leercultuur"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["collegialiteit", "feedback", "leren"],
            "irt_parameters": {
                "difficulty": 0.3,
                "discrimination": 1.1,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # PRACTICAL_SKILLS (5 вопросов)
        {
            "id": 386,
            "text": "Op de röntgenfoto ziet u een grote restauratie op een kies. Wat is de belangrijkste reden om deze restauratie te evalueren?",
            "options": ["Alleen om de kosten te bepalen", "Om marginale lekkage en secundaire cariës uit te sluiten", "Om de kleur van de restauratie te beoordelen", "Om de patiënt gerust te stellen"],
            "correct_answer_index": 1,
            "correct_answer_text": "Om marginale lekkage en secundaire cariës uit te sluiten",
            "explanation": "Röntgenologische evaluatie van restauraties is essentieel om marginale lekkage en secundaire cariës te detecteren. Deze kunnen klinisch onzichtbaar zijn maar leiden tot verdere schade als ze niet worden behandeld.",
            "category": "Radiographic Interpretation",
            "domain": "PRACTICAL_SKILLS",
            "domain_info": {
                "code": "PRACTICAL_SKILLS",
                "name": "Practical Skills",
                "weight_percentage": 15.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Radiographic evaluation of dental restorations",
            "learning_objectives": ["Röntgendiagnostiek", "Restauratie-evaluatie", "Secundaire cariës"],
            "image_url": "xray_filling.jpg",
            "tags": ["röntgen", "restauratie", "diagnostiek"],
            "irt_parameters": {
                "difficulty": -0.3,
                "discrimination": 1.4,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 387,
            "text": "Bij het plaatsen van een rubberdam voor endodontische behandeling moet u eerst:",
            "options": ["Direct de rubberdam plaatsen", "De juiste klem selecteren op basis van de tand", "De patiënt verdoven", "De behandeling beginnen zonder rubberdam"],
            "correct_answer_index": 1,
            "correct_answer_text": "De juiste klem selecteren op basis van de tand",
            "explanation": "De juiste klemselectie is cruciaal voor succesvolle rubberdam plaatsing. De klem moet passen bij de anatomie van de tand en voldoende retentie bieden zonder schade aan te richten.",
            "category": "Clinical Techniques",
            "domain": "PRACTICAL_SKILLS",
            "domain_info": {
                "code": "PRACTICAL_SKILLS",
                "name": "Practical Skills",
                "weight_percentage": 15.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Rubber dam placement for endodontic treatment",
            "learning_objectives": ["Rubberdam techniek", "Klemselectie", "Endodontische procedure"],
            "image_url": "xray_endodontic.jpg",
            "tags": ["rubberdam", "endodontie", "techniek"],
            "irt_parameters": {
                "difficulty": 0.1,
                "discrimination": 1.2,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 388,
            "text": "Na behandeling van een patiënt met hepatitis B moet u:",
            "options": ["Alleen de handen wassen", "Alle instrumenten steriliseren volgens protocol", "De instrumenten alleen desinfecteren", "Niets speciaals doen"],
            "correct_answer_index": 1,
            "correct_answer_text": "Alle instrumenten steriliseren volgens protocol",
            "explanation": "Infectiepreventie is cruciaal. Alle instrumenten moeten worden gesteriliseerd volgens het WIP-protocol, ongeacht de patiëntstatus. Dit is een wettelijke verplichting in Nederland.",
            "category": "Infection Control",
            "domain": "PRACTICAL_SKILLS",
            "domain_info": {
                "code": "PRACTICAL_SKILLS",
                "name": "Practical Skills",
                "weight_percentage": 15.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Infection control after treating hepatitis B patient",
            "learning_objectives": ["Infectiepreventie", "WIP-protocol", "Sterilisatie"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["infectie", "sterilisatie", "protocol"],
            "irt_parameters": {
                "difficulty": -0.2,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 389,
            "text": "Een patiënt krijgt een anafylactische reactie na toediening van lokale verdoving. Wat is uw eerste actie?",
            "options": ["De behandeling voortzetten", "Adrenaline 1:1000 intramusculair toedienen", "De patiënt naar huis sturen", "Alleen de bloeddruk meten"],
            "correct_answer_index": 1,
            "correct_answer_text": "Adrenaline 1:1000 intramusculair toedienen",
            "explanation": "Anafylaxie is een levensbedreigende noodsituatie. Adrenaline 1:1000 intramusculair is de eerste en meest belangrijke behandeling. Dit moet binnen 5 minuten worden toegediend.",
            "category": "Emergency Procedures",
            "domain": "PRACTICAL_SKILLS",
            "domain_info": {
                "code": "PRACTICAL_SKILLS",
                "name": "Practical Skills",
                "weight_percentage": 15.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Anaphylactic reaction to local anesthesia",
            "learning_objectives": ["Anafylaxie", "Noodbehandeling", "Adrenaline toediening"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["anafylaxie", "nood", "adrenaline"],
            "irt_parameters": {
                "difficulty": 0.5,
                "discrimination": 1.5,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 390,
            "text": "Bij het maken van een röntgenfoto van de bovenkaak moet de bundelrichting:",
            "options": ["Van onder naar boven", "Van boven naar beneden", "Horizontaal", "Diagonaal"],
            "correct_answer_index": 1,
            "correct_answer_text": "Van boven naar beneden",
            "explanation": "Voor bovenkaak röntgenfoto's moet de bundel van boven naar beneden gericht zijn om de tandwortels en omliggende botstructuren correct af te beelden. Dit volgt de anatomische oriëntatie.",
            "category": "Dental Skills",
            "domain": "PRACTICAL_SKILLS",
            "domain_info": {
                "code": "PRACTICAL_SKILLS",
                "name": "Practical Skills",
                "weight_percentage": 15.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Radiographic technique for maxillary imaging",
            "learning_objectives": ["Röntgentechniek", "Anatomische oriëntatie", "Bovenkaak imaging"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["röntgen", "techniek", "anatomie"],
            "irt_parameters": {
                "difficulty": -0.1,
                "discrimination": 1.1,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # STATISTICS (5 вопросов)
        {
            "id": 391,
            "text": "In een gerandomiseerde gecontroleerde trial wordt de effectiviteit van een nieuwe restauratiemateriaal getest. Wat is de beste primaire uitkomstmaat?",
            "options": ["De kleur van de restauratie", "De overleving van de restauratie na 5 jaar", "De kosten van het materiaal", "De tijd van plaatsing"],
            "correct_answer_index": 1,
            "correct_answer_text": "De overleving van de restauratie na 5 jaar",
            "explanation": "De overleving van restauraties is de meest klinisch relevante uitkomstmaat. Dit is een harde eindpunt dat direct gerelateerd is aan de effectiviteit van de behandeling en patiëntuitkomsten.",
            "category": "Research Methodology",
            "domain": "STATISTICS",
            "domain_info": {
                "code": "STATISTICS",
                "name": "Statistics and Data Analysis",
                "weight_percentage": 5.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "RCT outcome measures for dental materials",
            "learning_objectives": ["RCT design", "Primaire uitkomstmaat", "Klinische relevantie"],
            "image_url": "xray_filling.jpg",
            "tags": ["RCT", "uitkomstmaat", "restauratie"],
            "irt_parameters": {
                "difficulty": 0.2,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 392,
            "text": "Een studie toont een p-waarde van 0.03. Dit betekent:",
            "options": ["Er is 97% kans dat de nulhypothese waar is", "Er is 3% kans dat het resultaat door toeval komt", "De behandeling is 97% effectief", "Er is geen statistisch significant verschil"],
            "correct_answer_index": 1,
            "correct_answer_text": "Er is 3% kans dat het resultaat door toeval komt",
            "explanation": "De p-waarde geeft de kans op het observeren van het resultaat of een extremer resultaat onder de nulhypothese. Een p-waarde van 0.03 betekent dat er 3% kans is dat het resultaat door toeval komt.",
            "category": "Data Interpretation",
            "domain": "STATISTICS",
            "domain_info": {
                "code": "STATISTICS",
                "name": "Statistics and Data Analysis",
                "weight_percentage": 5.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Statistical significance interpretation",
            "learning_objectives": ["P-waarde", "Statistische significantie", "Nulhypothese"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["statistiek", "p-waarde", "significantie"],
            "irt_parameters": {
                "difficulty": 0.4,
                "discrimination": 1.4,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 393,
            "text": "De prevalentie van cariës in een populatie is 25%. Dit betekent:",
            "options": ["25% van de mensen krijgt cariës per jaar", "25% van de mensen heeft op dit moment cariës", "25% van de mensen heeft ooit cariës gehad", "25% van de mensen zal cariës krijgen"],
            "correct_answer_index": 1,
            "correct_answer_text": "25% van de mensen heeft op dit moment cariës",
            "explanation": "Prevalentie is het aantal mensen met een aandoening op een bepaald moment gedeeld door de totale populatie. Het is een momentopname, niet een incidentie (nieuwe gevallen per tijdseenheid).",
            "category": "Epidemiology",
            "domain": "STATISTICS",
            "domain_info": {
                "code": "STATISTICS",
                "name": "Statistics and Data Analysis",
                "weight_percentage": 5.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Epidemiological concepts in dentistry",
            "learning_objectives": ["Prevalentie", "Epidemiologie", "Populatie-onderzoek"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["epidemiologie", "prevalentie", "populatie"],
            "irt_parameters": {
                "difficulty": -0.3,
                "discrimination": 1.2,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 394,
            "text": "Wat is het hoogste niveau van bewijs volgens de evidence-based tandheelkunde hiërarchie?",
            "options": ["Case reports", "Cohort studies", "Systematic reviews en meta-analyses", "Expert opinion"],
            "correct_answer_index": 2,
            "correct_answer_text": "Systematic reviews en meta-analyses",
            "explanation": "Systematic reviews en meta-analyses staan bovenaan de evidence-based hiërarchie omdat ze alle beschikbare evidence combineren en analyseren. Dit geeft de meest betrouwbare conclusies.",
            "category": "Evidence-Based Dentistry",
            "domain": "STATISTICS",
            "domain_info": {
                "code": "STATISTICS",
                "name": "Statistics and Data Analysis",
                "weight_percentage": 5.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Evidence hierarchy in dental research",
            "learning_objectives": ["Evidence-based tandheelkunde", "Hiërarchie van bewijs", "Systematic reviews"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["evidence", "hiërarchie", "meta-analyse"],
            "irt_parameters": {
                "difficulty": 0.0,
                "discrimination": 1.1,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 395,
            "text": "Een 95% betrouwbaarheidsinterval van 0.8-1.2 voor een odds ratio betekent:",
            "options": ["Er is 95% kans dat de ware waarde tussen 0.8 en 1.2 ligt", "Er is 95% kans dat er geen effect is", "Het effect is statistisch significant", "Het effect is klinisch relevant"],
            "correct_answer_index": 0,
            "correct_answer_text": "Er is 95% kans dat de ware waarde tussen 0.8 en 1.2 ligt",
            "explanation": "Het 95% betrouwbaarheidsinterval geeft het bereik aan waarin we 95% zeker zijn dat de ware waarde ligt. Als dit interval 1 bevat, is er geen statistisch significant effect.",
            "category": "Statistical Significance",
            "domain": "STATISTICS",
            "domain_info": {
                "code": "STATISTICS",
                "name": "Statistics and Data Analysis",
                "weight_percentage": 5.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Confidence interval interpretation",
            "learning_objectives": ["Betrouwbaarheidsinterval", "Odds ratio", "Statistische interpretatie"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["betrouwbaarheidsinterval", "odds ratio", "statistiek"],
            "irt_parameters": {
                "difficulty": 0.6,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # TREATMENT_PLANNING (5 вопросов)
        {
            "id": 396,
            "text": "Een patiënt heeft een grote cariëslaesie die de pulp bereikt (zie röntgenfoto). De eerste stap in het behandelplan is:",
            "options": ["Direct endodontische behandeling", "Pulpa vitaliteitstest uitvoeren", "Direct extractie", "Alleen restauratie plaatsen"],
            "correct_answer_index": 1,
            "correct_answer_text": "Pulpa vitaliteitstest uitvoeren",
            "explanation": "Pulpa vitaliteitstest is essentieel voordat behandeling wordt gepland. Zelfs als cariës de pulp bereikt, kan de pulp nog vitaal zijn. Dit bepaalt of endodontische behandeling of directe pulpacapping nodig is.",
            "category": "Case Analysis",
            "domain": "TREATMENT_PLANNING",
            "domain_info": {
                "code": "TREATMENT_PLANNING",
                "name": "Treatment Planning",
                "weight_percentage": 10.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Treatment planning for deep caries",
            "learning_objectives": ["Pulpa vitaliteitstest", "Behandelplanning", "Cariës management"],
            "image_url": "xray_endodontic.jpg",
            "tags": ["pulpa", "vitaliteit", "planning"],
            "irt_parameters": {
                "difficulty": 0.1,
                "discrimination": 1.4,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 397,
            "text": "Voor een patiënt met meerdere cariëslaesies moet de behandeling worden gepland op basis van:",
            "options": ["Alleen de kosten", "De urgentie en complexiteit van elke laesie", "De beschikbare tijd", "De voorkeur van de patiënt"],
            "correct_answer_index": 1,
            "correct_answer_text": "De urgentie en complexiteit van elke laesie",
            "explanation": "Behandelplanning moet gebaseerd zijn op urgentie (pijn, infectie) en complexiteit. Acute problemen krijgen voorrang, gevolgd door complexe behandelingen die meer tijd en planning vereisen.",
            "category": "Treatment Sequencing",
            "domain": "TREATMENT_PLANNING",
            "domain_info": {
                "code": "TREATMENT_PLANNING",
                "name": "Treatment Planning",
                "weight_percentage": 10.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Treatment sequencing for multiple caries lesions",
            "learning_objectives": ["Behandelplanning", "Urgentie", "Complexiteit"],
            "image_url": "xray_filling.jpg",
            "tags": ["planning", "urgentie", "complexiteit"],
            "irt_parameters": {
                "difficulty": -0.2,
                "discrimination": 1.2,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 398,
            "text": "Een patiënt met diabetes mellitus heeft een verhoogd risico op:",
            "options": ["Alleen cariës", "Alleen parodontitis", "Cariës, parodontitis en slechte wondgenezing", "Alleen slechte wondgenezing"],
            "correct_answer_index": 2,
            "correct_answer_text": "Cariës, parodontitis en slechte wondgenezing",
            "explanation": "Diabetes mellitus verhoogt het risico op meerdere orale gezondheidsproblemen door veranderde immuunrespons en vasculaire veranderingen. Dit vereist aangepaste behandelplanning en preventieve maatregelen.",
            "category": "Risk Assessment",
            "domain": "TREATMENT_PLANNING",
            "domain_info": {
                "code": "TREATMENT_PLANNING",
                "name": "Treatment Planning",
                "weight_percentage": 10.0
            },
            "difficulty_level": 1,
            "question_type": "multiple_choice",
            "clinical_context": "Risk assessment for diabetic patients",
            "learning_objectives": ["Risicobeoordeling", "Diabetes mellitus", "Orale complicaties"],
            "image_url": "xray_healthy_teeth.jpg",
            "tags": ["diabetes", "risico", "complicaties"],
            "irt_parameters": {
                "difficulty": 0.0,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 399,
            "text": "Een kies met een grote restauratie en secundaire cariës heeft een slechte prognose als:",
            "options": ["Alleen de restauratie groot is", "De wortels gezond zijn", "Er botverlies is en de wortels zijn aangetast", "De patiënt jong is"],
            "correct_answer_index": 2,
            "correct_answer_text": "Er botverlies is en de wortels zijn aangetast",
            "explanation": "Botverlies en wortelaantasting zijn de belangrijkste factoren voor slechte prognose. Deze factoren beïnvloeden de retentie van de tand en de mogelijkheid voor succesvolle behandeling.",
            "category": "Prognosis Evaluation",
            "domain": "TREATMENT_PLANNING",
            "domain_info": {
                "code": "TREATMENT_PLANNING",
                "name": "Treatment Planning",
                "weight_percentage": 10.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Prognosis evaluation for compromised teeth",
            "learning_objectives": ["Prognose", "Botverlies", "Wortelaantasting"],
            "image_url": "xray_filling.jpg",
            "tags": ["prognose", "botverlies", "wortels"],
            "irt_parameters": {
                "difficulty": 0.3,
                "discrimination": 1.4,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": 400,
            "text": "Een patiënt met een complexe medische geschiedenis vereist:",
            "options": ["Alleen tandheelkundige behandeling", "Samenwerking met de huisarts", "Multidisciplinaire aanpak met relevante specialisten", "Alleen parodontologische behandeling"],
            "correct_answer_index": 2,
            "correct_answer_text": "Multidisciplinaire aanpak met relevante specialisten",
            "explanation": "Complexe medische geschiedenis vereist multidisciplinaire aanpak om risico's te minimaliseren en optimale zorg te bieden. Samenwerking met relevante specialisten is essentieel voor veilige en effectieve behandeling.",
            "category": "Multidisciplinary Care",
            "domain": "TREATMENT_PLANNING",
            "domain_info": {
                "code": "TREATMENT_PLANNING",
                "name": "Treatment Planning",
                "weight_percentage": 10.0
            },
            "difficulty_level": 2,
            "question_type": "multiple_choice",
            "clinical_context": "Multidisciplinary approach for complex cases",
            "learning_objectives": ["Multidisciplinaire zorg", "Complexe gevallen", "Samenwerking"],
            "image_url": "xray_endodontic.jpg",
            "tags": ["multidisciplinair", "complex", "samenwerking"],
            "irt_parameters": {
                "difficulty": 0.4,
                "discrimination": 1.3,
                "guessing": 0.25,
                "calibration_date": datetime.now().isoformat()
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    return new_questions

def update_export_file():
    """Обновить экспортированный файл новыми вопросами"""
    
    print('📝 ОБНОВЛЕНИЕ ЭКСПОРТИРОВАННОГО ФАЙЛА')
    print('=' * 50)
    
    # Путь к существующему файлу
    export_file_path = '/Users/evgenijbutov/Desktop/demo/flask-app 2/dental-academy-clean/scripts/questions_export_20250812_020211.json'
    
    # Создаем резервную копию
    backup_path = export_file_path.replace('.json', '_backup.json')
    
    try:
        # Читаем существующий файл
        with open(export_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        print(f'📊 Загружено {len(existing_data)} существующих вопросов')
        
        # Создаем резервную копию
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f'💾 Создана резервная копия: {backup_path}')
        
        # Добавляем новые вопросы
        new_questions = create_new_questions()
        existing_data.extend(new_questions)
        
        print(f'✅ Добавлено {len(new_questions)} новых вопросов')
        
        # Сохраняем обновленный файл
        with open(export_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f'💾 Обновленный файл сохранен: {export_file_path}')
        
        # Показываем статистику
        print(f'\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:')
        print(f'   Всего вопросов: {len(existing_data)}')
        print(f'   Новых вопросов: {len(new_questions)}')
        
        # Статистика по доменам
        domain_stats = {}
        for question in existing_data:
            domain = question.get('domain', 'Unknown')
            if domain not in domain_stats:
                domain_stats[domain] = 0
            domain_stats[domain] += 1
        
        print(f'\n📋 РАСПРЕДЕЛЕНИЕ ПО ДОМЕНАМ:')
        for domain, count in sorted(domain_stats.items()):
            print(f'   {domain}: {count} вопросов')
        
        return True
        
    except Exception as e:
        print(f'❌ Ошибка при обновлении файла: {e}')
        return False

if __name__ == '__main__':
    print('🚀 Запуск обновления экспортированного файла...')
    
    success = update_export_file()
    
    if success:
        print('\n✅ Обновление файла завершено успешно!')
    else:
        print('\n❌ Обновление файла завершилось с ошибками!')
