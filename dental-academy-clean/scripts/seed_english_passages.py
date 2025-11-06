#!/usr/bin/env python3
"""
Скрипт для загрузки English Passages с вопросами
Использование: python scripts/seed_english_passages.py
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, EnglishPassage, EnglishQuestion
from datetime import datetime, timezone
import json

# Маппинг названий пассажей к именам файлов изображений
PASSAGE_IMAGES = {
    "Artificial Intelligence in Healthcare": "ai-healthcare.png",
    "The Coffee Trade Through History": "coffee-trade.png",
    "Urban Green Spaces and Mental Health": "urban-green.png",
    "The Architecture of Ancient Rome": "roman-architecture.png",
    "Climate Change and Ocean Currents": "ocean-currents.png",
    "The Psychology of Color": "psychology-color.png",
    "The Evolution of Human Language": "language-evolution.png",
    "Renewable Energy Technologies": "renewable-energy.png",
    "The Science of Sleep": "sleep-science.png",
    "Space Exploration Milestones": "space-exploration.png"
}

def get_image_url(passage_title):
    """Получить URL изображения для пассажа"""
    image_filename = PASSAGE_IMAGES.get(passage_title)
    if image_filename:
        # Используем относительный путь для статических файлов
        return f"/static/images/passages/{image_filename}"
    return None

def seed_english_passages():
    """Загружает English passages с вопросами"""
    
    with app.app_context():
        try:
            print("🌱 Начинаем загрузку English passages...")
            
            # Ваши 4 passages
            passages_data = [
                {
                    'title': 'Artificial Intelligence in Healthcare',
                    'category': 'Technology',
                    'difficulty': 7.0,
                    'content': '''
A Artificial intelligence is rapidly transforming the healthcare industry, offering unprecedented opportunities to improve patient outcomes and streamline medical processes. Machine learning algorithms can now analyze vast amounts of medical data with remarkable speed and accuracy, identifying patterns that might escape human observation. Recent studies have shown that AI systems can diagnose certain conditions, such as skin cancer and diabetic retinopathy, with accuracy rates comparable to or exceeding those of experienced physicians. This technological advancement has sparked intense debate about the future role of human doctors in an increasingly automated medical landscape.

B The implementation of AI in clinical settings extends far beyond diagnostic applications. Predictive analytics powered by artificial intelligence can forecast patient deterioration hours before traditional warning signs appear, allowing medical staff to intervene proactively. In drug discovery, AI algorithms can screen millions of molecular compounds in days rather than years, accelerating the development of new treatments. Furthermore, AI-driven robotic systems are assisting surgeons in performing complex procedures with enhanced precision, reducing operation times and improving recovery rates. However, these innovations come with significant challenges, including the need for massive datasets to train algorithms effectively and concerns about data privacy and security.

C Despite the promising applications, the integration of AI into healthcare faces substantial obstacles. Many healthcare professionals express concern about over-reliance on automated systems, arguing that medicine requires human empathy and judgment that machines cannot replicate. There are also questions about liability when AI systems make errors, and regulatory frameworks have struggled to keep pace with technological advancement. Additionally, the substantial initial investment required for AI implementation presents a barrier for smaller medical facilities, potentially widening the gap between well-funded institutions and those serving underserved communities. Nevertheless, experts predict that within the next decade, AI will become an indispensable tool in modern medicine, fundamentally changing how healthcare is delivered worldwide.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to paragraph A, AI diagnostic systems:',
                            'options': {
                                'A': 'Are still significantly less accurate than human doctors',
                                'B': 'Can match or surpass expert physicians in certain diagnoses',
                                'C': 'Are mainly used for treating skin conditions',
                                'D': 'Have completely replaced human doctors in diagnostics'
                            },
                            'correct_answer': 'B',
                            'explanation': 'The passage states that AI can diagnose certain conditions \'with accuracy rates comparable to or exceeding those of experienced physicians\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'What advantage of AI in drug discovery is mentioned in paragraph B?',
                            'options': {
                                'A': 'It completely eliminates the need for human researchers',
                                'B': 'It reduces the cost of medications for patients',
                                'C': 'It can analyze molecular compounds much faster than traditional methods',
                                'D': 'It guarantees successful treatment outcomes'
                            },
                            'correct_answer': 'C',
                            'explanation': 'The text mentions that AI can \'screen millions of molecular compounds in days rather than years\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'AI predictive analytics can only identify patient problems after symptoms appear.',
                            'correct_answer': 'FALSE',
                            'explanation': 'The passage states that predictive analytics can \'forecast patient deterioration hours before traditional warning signs appear\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'Regulatory frameworks have successfully adapted to AI advancement in healthcare.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C explicitly states that \'regulatory frameworks have struggled to keep pace with technological advancement\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Most healthcare professionals fully support AI integration without concerns.',
                            'correct_answer': 'FALSE',
                            'explanation': 'The text mentions that \'many healthcare professionals express concern about over-reliance on automated systems\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'AI-driven robotic systems help surgeons perform procedures with enhanced _______.',
                            'correct_answer': 'precision',
                            'explanation': 'Directly stated in paragraph B.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Healthcare professionals argue that medicine requires human _______ that machines cannot replicate.',
                            'correct_answer': 'empathy',
                            'explanation': 'Found in paragraph C: \'medicine requires human empathy and judgment\'.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'The substantial _______ investment required for AI presents a barrier for smaller facilities.',
                            'correct_answer': 'initial',
                            'explanation': 'Paragraph C mentions \'substantial initial investment\'.'
                        }
                    ]
                },
                {
                    'title': 'The Coffee Trade Through History',
                    'category': 'History',
                    'difficulty': 7.0,
                    'content': '''
A Coffee's journey from a regional Ethiopian beverage to a global commodity represents one of history's most remarkable trade stories. Legend attributes the discovery of coffee to an Ethiopian goat herder named Kaldi in the 9th century, who noticed his goats becoming energetic after eating berries from a certain tree. From these humble origins, coffee spread throughout the Arabian Peninsula, where it became deeply integrated into Islamic culture. By the 15th century, coffee houses emerged in Mecca and Cairo, serving as important social and intellectual gathering places. The Ottoman Empire played a crucial role in coffee's early dissemination, with Istanbul's coffee houses becoming renowned centers of conversation and culture by the mid-16th century.

B European encounter with coffee began in earnest during the 17th century, initially met with suspicion and resistance. Some religious authorities condemned it as the "bitter invention of Satan," particularly because of its association with Islam. However, Pope Clement VIII famously tasted coffee in 1600 and gave it papal approval, declaring it too delicious to remain exclusively a Muslim drink. This endorsement accelerated coffee's acceptance across Catholic Europe. The first European coffee houses opened in Venice in 1645, followed rapidly by establishments in England, France, and Holland. These coffee houses evolved into vital institutions for business, politics, and intellectual discourse, earning the nickname "penny universities" because for the price of a penny, one could purchase coffee and engage in stimulating conversation. The London Stock Exchange and Lloyd's of London insurance company both originated in coffee houses.

C The colonial era transformed coffee from a luxury import into a mass-produced commodity through plantation systems in tropical colonies. The Dutch successfully cultivated coffee in Java by 1699, breaking the Arabian monopoly on coffee production. France introduced coffee cultivation to the Caribbean, while Portuguese colonizers established massive plantations in Brazil, which eventually became the world's largest coffee producer. This expansion came at tremendous human cost, relying heavily on enslaved African labor. The legacy of this colonial coffee economy persists today in the geographic distribution of coffee production, with most cultivation occurring in former colonies along the equatorial "coffee belt." Modern coffee trade continues to raise ethical questions about fair compensation for farmers and sustainable farming practices, though initiatives like Fair Trade certification attempt to address these historical inequities.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to the passage, coffee was first discovered in:',
                            'options': {
                                'A': 'The Arabian Peninsula',
                                'B': 'Ethiopia',
                                'C': 'The Ottoman Empire',
                                'D': 'Java'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph A states that legend attributes coffee\'s discovery to \'an Ethiopian goat herder\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'European coffee houses were called \'penny universities\' because:',
                            'options': {
                                'A': 'They were located near universities',
                                'B': 'They offered formal education courses',
                                'C': 'They provided intellectual conversation for a small fee',
                                'D': 'University students received discounts'
                            },
                            'correct_answer': 'C',
                            'explanation': 'The text explains that \'for the price of a penny, one could purchase coffee and engage in stimulating conversation\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Pope Clement VIII initially condemned coffee as inappropriate for Christians.',
                            'correct_answer': 'FALSE',
                            'explanation': 'While some religious authorities condemned it, Pope Clement VIII gave it approval after tasting it.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'The Dutch were the first to grow coffee outside Arabia successfully.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph C states the Dutch \'successfully cultivated coffee in Java by 1699, breaking the Arabian monopoly\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Fair Trade certification has completely solved all ethical issues in coffee production.',
                            'correct_answer': 'NOT GIVEN',
                            'explanation': 'The passage mentions Fair Trade \'attempts to address\' inequities but doesn\'t state whether it has completely solved them.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Coffee houses in the Ottoman Empire, particularly in _______, became renowned cultural centers.',
                            'correct_answer': 'Istanbul',
                            'explanation': 'Directly mentioned in paragraph A.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Brazil eventually became the world\'s largest _______ producer.',
                            'correct_answer': 'coffee',
                            'explanation': 'Stated in paragraph C.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'Most modern coffee cultivation occurs along the equatorial \'_______\'.',
                            'correct_answer': 'coffee belt',
                            'explanation': 'The exact phrase used in paragraph C.'
                        }
                    ]
                },
                {
                    'title': 'Urban Green Spaces and Mental Health',
                    'category': 'Environment',
                    'difficulty': 7.0,
                    'content': '''
A The relationship between urban green spaces and human psychological wellbeing has become an increasingly important topic as global urbanization accelerates. More than half of the world's population now lives in cities, a proportion expected to reach 68% by 2050. This rapid urban concentration has prompted researchers to investigate how city environments affect mental health. Studies consistently demonstrate that access to parks, gardens, and natural areas within urban settings provides significant psychological benefits. Residents living near green spaces report lower levels of stress, anxiety, and depression compared to those in areas dominated by concrete and asphalt. The mechanisms behind these benefits appear to involve both direct physiological responses to nature and indirect social effects facilitated by these communal spaces.

B Scientific research has identified several pathways through which green spaces promote mental health. Exposure to natural environments triggers measurable physiological changes, including reduced cortisol levels (the stress hormone) and decreased heart rate and blood pressure. The concept of "attention restoration theory" suggests that natural settings allow the brain's directed attention mechanisms to rest and recover from the constant stimulation of urban environments. Furthermore, green spaces encourage physical activity, which independently contributes to improved mental health through endorphin release and enhanced self-esteem. These areas also serve crucial social functions, providing venues for community interaction and reducing feelings of isolation that commonly afflict urban dwellers. A longitudinal study in Denmark found that children who grew up with access to green spaces had up to 55% lower risk of developing psychiatric disorders in adulthood.

C Despite compelling evidence for their importance, urban green spaces face numerous threats from development pressures and inadequate maintenance. Many cities prioritize construction of residential and commercial buildings over preservation of parks and natural areas, particularly in rapidly growing urban centers in developing nations. Additionally, existing green spaces are often distributed inequitably, with wealthier neighborhoods typically enjoying better access than lower-income areas—a phenomenon sometimes termed "environmental injustice." Urban planners and public health officials increasingly recognize the need to integrate green infrastructure into city design, viewing parks not as luxury amenities but as essential components of urban health infrastructure, comparable to hospitals and clinics in their contribution to community wellbeing.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'What percentage of the global population is expected to live in cities by 2050?',
                            'options': {
                                'A': '50%',
                                'B': '55%',
                                'C': '68%',
                                'D': '75%'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph A states \'a proportion expected to reach 68% by 2050\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'According to paragraph B, \'attention restoration theory\' proposes that natural settings:',
                            'options': {
                                'A': 'Completely eliminate stress from urban life',
                                'B': 'Allow brain attention mechanisms to rest and recover',
                                'C': 'Increase cortisol levels in the body',
                                'D': 'Replace the need for medical treatment'
                            },
                            'correct_answer': 'B',
                            'explanation': 'The text states natural settings \'allow the brain\'s directed attention mechanisms to rest and recover\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Children with access to green spaces have significantly lower risk of psychiatric disorders later in life.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph B mentions a Danish study finding \'up to 55% lower risk of developing psychiatric disorders in adulthood\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'All cities distribute green spaces equally across different income neighborhoods.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C explicitly mentions \'environmental injustice\' with wealthier neighborhoods having better access.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Urban planners now consider green spaces as essential health infrastructure.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph C states planners view parks \'not as luxury amenities but as essential components of urban health infrastructure\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Exposure to nature reduces _______, the stress hormone in the human body.',
                            'correct_answer': 'cortisol',
                            'explanation': 'Paragraph B mentions \'reduced cortisol levels (the stress hormone)\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Physical activity in green spaces contributes to mental health through _______ release.',
                            'correct_answer': 'endorphin',
                            'explanation': 'Stated in paragraph B.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'The unequal distribution of green spaces is sometimes called \'environmental _______\'.',
                            'correct_answer': 'injustice',
                            'explanation': 'Directly mentioned in paragraph C.'
                        }
                    ]
                },
                {
                    'title': 'The Architecture of Ancient Rome',
                    'category': 'Architecture',
                    'difficulty': 7.0,
                    'content': '''
A Ancient Roman architecture stands as one of humanity's most influential building traditions, with innovations that fundamentally shaped construction techniques for millennia. The Romans inherited architectural knowledge from the Greeks and Etruscans but transformed these influences through engineering ingenuity and practical ambition. Their most significant contribution was the development and widespread use of concrete, a revolutionary material that enabled construction on unprecedented scales. Roman concrete, made from volcanic ash, lime, and aggregate, proved remarkably durable—many structures built two thousand years ago remain standing today. This material allowed Roman builders to create vast interior spaces and complex curved structures that would have been impossible with traditional stone construction methods.

B The architectural achievements of Rome extended beyond material innovation to encompass sophisticated structural engineering. The arch, vault, and dome became signature elements of Roman building, distributing weight efficiently and enabling construction of massive public buildings. The Pantheon, completed in 126 AD, exemplifies Roman engineering prowess with its massive concrete dome spanning 43 meters—a record that stood for over 1,300 years until the construction of Florence Cathedral's dome. Roman architects also pioneered the use of the arch in aqueducts, creating elevated water channels that transported millions of liters daily to cities across the empire. These aqueducts relied on precise gradient calculations, demonstrating advanced mathematical understanding. The Romans' systematic approach to urban planning influenced city design for centuries, with their grid-pattern streets, central forums, and hierarchical arrangement of public buildings establishing templates that persist in modern urban centers.

C Beyond functionality, Roman architecture served powerful political and cultural purposes. Monumental buildings proclaimed imperial authority and Roman civilization's superiority, with structures like the Colosseum and Circus Maximus serving as venues for spectacles that reinforced social hierarchies and state power. Wealthy Romans commissioned elaborate private villas featuring innovative heating systems (hypocausts), intricate mosaics, and formal gardens, displaying their status through architectural sophistication. The empire's expansion spread Roman building techniques throughout Europe, North Africa, and the Middle East, creating an architectural language that transcended linguistic and cultural boundaries. This architectural legacy profoundly influenced later periods, particularly during the Renaissance when architects deliberately revived classical Roman forms and proportions. Today, government buildings, museums, and monuments worldwide continue to employ Roman architectural elements—columns, domes, and symmetrical facades—demonstrating the enduring appeal and authority of Roman design principles.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'What was the Romans\' most significant contribution to construction?',
                            'options': {
                                'A': 'The invention of the column',
                                'B': 'The development and use of concrete',
                                'C': 'The creation of grid-pattern streets',
                                'D': 'The construction of theaters'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph A states \'Their most significant contribution was the development and widespread use of concrete\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'The Pantheon\'s dome held a construction record for:',
                            'options': {
                                'A': '500 years',
                                'B': '800 years',
                                'C': 'Over 1,300 years',
                                'D': '2,000 years'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph B mentions \'a record that stood for over 1,300 years\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Roman concrete was made partly from volcanic ash.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph A states Roman concrete was \'made from volcanic ash, lime, and aggregate\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'The Greeks invented the architectural arch and gave it to the Romans.',
                            'correct_answer': 'NOT GIVEN',
                            'explanation': 'The passage mentions Romans inherited knowledge from Greeks but doesn\'t specifically state Greeks invented the arch.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Roman architecture had only functional purposes without political significance.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C explicitly states Roman architecture \'served powerful political and cultural purposes\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Roman aqueducts used the _______ to create elevated water channels.',
                            'correct_answer': 'arch',
                            'explanation': 'Paragraph B mentions \'the use of the arch in aqueducts\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Wealthy Romans used innovative heating systems called _______.',
                            'correct_answer': 'hypocausts',
                            'explanation': 'Directly stated in paragraph C.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'The _______ period deliberately revived classical Roman architectural forms.',
                            'correct_answer': 'Renaissance',
                            'explanation': 'Mentioned in paragraph C.'
                        }
                    ]
                },
                {
                    'title': 'Climate Change and Ocean Currents',
                    'category': 'Science',
                    'difficulty': 7.0,
                    'content': '''
A Ocean currents function as the planet's circulatory system, redistributing heat and regulating climate patterns across the globe. These massive movements of water, driven by wind, temperature differences, and the Earth's rotation, transport warm water from equatorial regions toward the poles while carrying cold water back toward the equator. The Atlantic Meridional Overturning Circulation (AMOC), commonly known as the Gulf Stream system, exemplifies this process by carrying warm water northward along the Atlantic coast, moderating temperatures in Western Europe and making cities like London significantly warmer than locations at similar latitudes. Without this thermal regulation, much of Northern Europe would experience climates comparable to those of northern Canada or Siberia.

B Climate scientists have observed concerning changes in ocean current patterns over recent decades, with potential implications for global weather systems. Rising atmospheric temperatures caused by greenhouse gas emissions are melting Arctic ice at accelerating rates, releasing massive quantities of fresh water into the North Atlantic. This influx of cold, fresh water disrupts the density-driven mechanisms that power the AMOC, as the system relies on cold, salty water sinking in the North Atlantic to maintain its circulation. Research published in 2021 indicated that the AMOC has weakened by approximately 15% since the mid-20th century, reaching its weakest state in over 1,600 years according to paleoclimate data. Computer models project that continued warming could lead to further weakening or even partial collapse of this critical current system within this century.

C The consequences of significant ocean current disruption would extend far beyond regional temperature changes. A weakened AMOC could paradoxically cause cooling in parts of Europe despite global warming trends, while simultaneously intensifying heat in other regions. Changes in ocean circulation patterns would alter precipitation distributions, potentially causing severe droughts in some areas and flooding in others. Marine ecosystems depend on nutrient cycling driven by ocean currents, and disruption could devastate fisheries that millions of people rely upon for food and livelihood. Furthermore, current weakening might accelerate sea-level rise along the North American Atlantic coast as water accumulates in regions where currents previously carried it away. These interconnected effects demonstrate how changes in one Earth system component can cascade through multiple environmental and social domains, underscoring the complexity of climate change impacts and the urgency of mitigation efforts.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to the passage, the Gulf Stream system makes Western Europe:',
                            'options': {
                                'A': 'Colder than locations at similar latitudes',
                                'B': 'Warmer than locations at similar latitudes',
                                'C': 'Similar in temperature to northern Canada',
                                'D': 'Unaffected by ocean currents'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph A states it moderates temperatures, making cities \'significantly warmer than locations at similar latitudes\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'What disrupts the AMOC according to paragraph B?',
                            'options': {
                                'A': 'Increased salinity in the ocean',
                                'B': 'Stronger winds in the Atlantic',
                                'C': 'Fresh water from melting Arctic ice',
                                'D': 'Underwater volcanic activity'
                            },
                            'correct_answer': 'C',
                            'explanation': 'The text explains that \'influx of cold, fresh water disrupts the density-driven mechanisms that power the AMOC\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'The AMOC has weakened by about 15% since the mid-20th century.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Directly stated in paragraph B: \'the AMOC has weakened by approximately 15%\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'A weakened AMOC would cause uniform warming across all regions.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C states it \'could paradoxically cause cooling in parts of Europe despite global warming trends\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Ocean current changes only affect water temperature and nothing else.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C describes multiple effects including precipitation, ecosystems, and sea levels.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Ocean currents are driven by wind, temperature differences, and the Earth\'s _______.',
                            'correct_answer': 'rotation',
                            'explanation': 'Listed in paragraph A as one of three driving forces.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'The AMOC relies on cold, _______ water sinking in the North Atlantic.',
                            'correct_answer': 'salty',
                            'explanation': 'Paragraph B mentions \'cold, salty water sinking\'.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'Marine ecosystems depend on _______ cycling driven by ocean currents.',
                            'correct_answer': 'nutrient',
                            'explanation': 'Stated in paragraph C.'
                        }
                    ]
                },
                {
                    'title': 'The Psychology of Color',
                    'category': 'Psychology',
                    'difficulty': 7.0,
                    'content': '''
A Color perception extends far beyond simple visual sensation, profoundly influencing human emotions, behavior, and cognitive performance in ways that researchers are only beginning to fully understand. The field of color psychology examines how different wavelengths of light affect psychological states and physiological responses. While some color associations appear culturally conditioned—white symbolizing purity in Western cultures but mourning in some Eastern traditions—other responses seem more universal. Studies consistently show that warm colors like red and orange tend to increase arousal and energy levels, while cool colors such as blue and green generally produce calming effects. These responses occur rapidly and often unconsciously, making color a powerful tool in environments ranging from hospitals to marketing campaigns.

B Scientific research has documented numerous specific effects of color on human performance and wellbeing. Blue lighting has been shown to enhance alertness and cognitive performance, particularly for tasks requiring sustained attention, which explains its increasing use in office environments and educational institutions. Conversely, exposure to red before examinations or competitive activities appears to impair performance, possibly because the color triggers anxiety responses associated with danger signals. Healthcare facilities increasingly paint patient rooms in soft greens and blues after studies demonstrated that these colors reduce stress and may even decrease pain perception and recovery time. The food industry exploits color psychology extensively—red and yellow dominate fast-food branding because these colors stimulate appetite and create a sense of urgency, while upscale restaurants favor subdued tones that encourage leisurely dining. Some prisons have experimented with painting violent offender cells in specific shades of pink, reporting reduced aggressive behavior, though the reliability of these findings remains debated.

C Despite accumulating evidence, color psychology faces methodological challenges that complicate research interpretation. Individual responses to color vary based on personal experiences, cultural background, and even temporary mood states, making it difficult to establish universal principles. Additionally, isolating color effects from other environmental factors proves challenging in real-world settings. Critics argue that some claimed color effects may result from expectancy bias—people behave in accordance with their beliefs about how colors should affect them rather than experiencing genuine physiological responses. Nevertheless, the practical applications of color psychology continue to expand, with architects, designers, and marketers incorporating color principles into their work. As neuroscience techniques advance, researchers hope to better understand the biological mechanisms underlying color perception's psychological impacts, potentially refining applications in therapeutic and educational contexts.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to paragraph A, warm colors like red and orange typically:',
                            'options': {
                                'A': 'Produce calming effects',
                                'B': 'Have no psychological impact',
                                'C': 'Increase energy levels',
                                'D': 'Improve memory'
                            },
                            'correct_answer': 'C',
                            'explanation': 'The text states warm colors \'tend to increase arousal and energy levels\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'Why do fast-food restaurants use red and yellow in their branding?',
                            'options': {
                                'A': 'These colors are the cheapest to produce',
                                'B': 'They stimulate appetite and urgency',
                                'C': 'They encourage leisurely dining',
                                'D': 'They reduce customer stress'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph B states these colors \'stimulate appetite and create a sense of urgency\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Blue lighting enhances cognitive performance for attention-requiring tasks.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph B explicitly states that blue lighting \'enhance alertness and cognitive performance, particularly for tasks requiring sustained attention\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'All color associations are culturally conditioned with no universal responses.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph A mentions \'some color associations appear culturally conditioned\' but \'other responses seem more universal\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'The effectiveness of pink paint in reducing prison violence is conclusively proven.',
                            'correct_answer': 'NOT GIVEN',
                            'explanation': 'Paragraph B mentions reports of reduced aggression but states \'the reliability of these findings remains debated\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Healthcare facilities paint rooms in soft greens and blues to reduce _______ and aid recovery.',
                            'correct_answer': 'stress',
                            'explanation': 'Paragraph B states these colors \'reduce stress and may even decrease pain perception\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Exposure to the color _______ before exams appears to impair performance.',
                            'correct_answer': 'red',
                            'explanation': 'Directly mentioned in paragraph B.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'Critics suggest some color effects may result from _______ bias.',
                            'correct_answer': 'expectancy',
                            'explanation': 'Paragraph C discusses \'expectancy bias\' as a potential explanation.'
                        }
                    ]
                },
                {
                    'title': 'The Evolution of Human Language',
                    'category': 'Linguistics',
                    'difficulty': 7.0,
                    'content': '''
A The origin of human language remains one of the most intriguing mysteries in evolutionary science, with scholars debating when, how, and why our species developed this unique communication system. Unlike animal communication, which typically conveys immediate information about threats, food sources, or mating opportunities, human language possesses several distinctive features: it is symbolic (words represent concepts rather than directly signaling things), generative (finite rules allow infinite sentence creation), and can describe abstract concepts, past events, and hypothetical scenarios. These characteristics enable humans to share complex ideas, transmit cultural knowledge across generations, and engage in collaborative planning—capabilities that arguably underpin human civilization's development. However, language leaves no fossil record, making its evolutionary trajectory difficult to trace definitively.

B Researchers have proposed various theories about language evolution's timeline and mechanisms. Some scholars advocate for a relatively recent and rapid emergence, suggesting language appeared between 50,000 and 100,000 years ago in anatomically modern humans, possibly coinciding with a genetic mutation that reorganized brain structures. This "sudden emergence" theory finds support in the archaeological record's apparent behavioral revolution around 50,000 years ago, marked by sophisticated tools, art, and long-distance trade networks that might indicate advanced linguistic capabilities. Alternative theories propose a more gradual evolution, with proto-linguistic systems emerging much earlier in human ancestors, perhaps 2 million years ago with Homo habilis, and gradually increasing in complexity. Comparative studies of primate communication reveal that great apes possess some precursor abilities—they can learn symbolic associations and combine symbols in simple ways—suggesting language evolution built upon existing cognitive capacities rather than appearing completely de novo.

C Neurological and genetic research provides additional insights into language evolution. The FOXP2 gene, sometimes called the "language gene," appears crucial for the fine motor control required for speech production. Humans possess a variant of this gene that differs from the versions found in other primates, and this variant emerged approximately 200,000 years ago. Individuals with FOXP2 mutations experience severe speech and language difficulties, demonstrating its importance. Brain imaging studies reveal that language processing activates specific regions, particularly Broca's area (speech production) and Wernicke's area (language comprehension) in the left hemisphere. These specialized brain regions suggest language has been subject to strong evolutionary selection pressures. Some researchers propose that language evolution was driven by social needs—managing increasingly complex group relationships required more sophisticated communication. Others emphasize practical advantages for coordinating hunting, sharing resources, and transmitting survival knowledge. Regardless of the specific pressures, language evolution clearly provided such enormous advantages that it became a defining human characteristic, fundamentally shaping how our species understands and interacts with the world.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'What distinguishes human language from animal communication according to paragraph A?',
                            'options': {
                                'A': 'It is louder and travels farther',
                                'B': 'It only conveys immediate threats',
                                'C': 'It is symbolic, generative, and can describe abstract concepts',
                                'D': 'It is simpler and easier to learn'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph A lists these three distinctive features of human language.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'The FOXP2 gene is important for:',
                            'options': {
                                'A': 'Visual processing',
                                'B': 'Fine motor control required for speech',
                                'C': 'Memory formation',
                                'D': 'Emotional regulation'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph C states FOXP2 \'appears crucial for the fine motor control required for speech production\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Language evolution can be easily traced through fossil records.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph A explicitly states \'language leaves no fossil record, making its evolutionary trajectory difficult to trace\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'Great apes possess some precursor abilities to language.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph B mentions apes \'can learn symbolic associations and combine symbols in simple ways\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'All researchers agree language appeared suddenly 50,000 years ago.',
                            'correct_answer': 'FALSE',
                            'explanation': 'The passage describes both \'sudden emergence\' and \'gradual evolution\' theories, showing disagreement.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Human language is _______, meaning finite rules allow infinite sentence creation.',
                            'correct_answer': 'generative',
                            'explanation': 'This definition is provided in paragraph A.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Broca\'s area in the brain is responsible for speech _______.',
                            'correct_answer': 'production',
                            'explanation': 'Paragraph C specifies \'Broca\'s area (speech production)\'.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'The human variant of FOXP2 emerged approximately _______ years ago.',
                            'correct_answer': '200000',
                            'explanation': 'Stated in paragraph C (accepts \'200,000\' or \'200000\').'
                        }
                    ]
                },
                {
                    'title': 'Renewable Energy Technologies',
                    'category': 'Technology',
                    'difficulty': 7.0,
                    'content': '''
A The transition from fossil fuels to renewable energy sources represents one of the most critical challenges and opportunities of the 21st century. Unlike coal, oil, and natural gas, which release carbon dioxide accumulated over millions of years, renewable energy technologies harness naturally replenishing resources such as sunlight, wind, water flow, and geothermal heat. Solar photovoltaic technology has experienced dramatic cost reductions over the past decade, with prices falling more than 80% since 2010, making it now the cheapest source of electricity in many regions. Wind power has similarly become economically competitive, with modern turbines capable of generating electricity at costs comparable to or lower than conventional power plants. These economic shifts, combined with growing concerns about climate change and air pollution, have accelerated renewable energy adoption worldwide.

B Despite impressive progress, renewable energy integration faces significant technical and practical obstacles. The fundamental challenge lies in intermittency—solar panels generate electricity only during daylight hours, and wind turbines depend on wind availability, creating mismatches between energy generation and consumption patterns. This variability requires either backup power sources or energy storage systems, both of which add costs and complexity. Battery technology, particularly lithium-ion batteries, has improved substantially, but storing electricity at grid scale remains expensive and materials-intensive. Furthermore, renewable installations require considerably more land than fossil fuel plants for equivalent energy output. A coal power station might occupy several acres, while a solar farm producing comparable electricity could require hundreds of acres. This spatial footprint raises concerns about habitat disruption and competing land uses, particularly as agriculture and urban development already constrain available space.

C Addressing renewable energy's limitations requires integrated approaches combining multiple technologies and strategies. Smart grid systems use sophisticated software to balance supply and demand in real-time, directing electricity where needed most efficiently. Complementary renewable sources can offset each other's intermittency—solar production peaks during summer days while wind often generates more power during winter nights. Hydrogen produced through electrolysis using excess renewable electricity offers a potential storage solution and clean fuel for transportation and industrial processes. Geothermal and hydroelectric power provide more consistent baseload electricity, stabilizing grids with high renewable penetration. Policy mechanisms also play crucial roles; countries like Germany and Denmark have achieved high renewable energy shares through supportive regulations, feed-in tariffs, and coordinated grid infrastructure investments. As technology continues advancing and societies recognize the urgent need to reduce greenhouse gas emissions, renewable energy is expected to dominate global electricity generation within the coming decades, fundamentally transforming energy systems that have relied on fossil fuels for over a century.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to paragraph A, solar photovoltaic prices have:',
                            'options': {
                                'A': 'Remained stable since 2010',
                                'B': 'Increased by 80%',
                                'C': 'Fallen more than 80% since 2010',
                                'D': 'Become the most expensive energy source'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Directly stated: \'prices falling more than 80% since 2010\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'The fundamental challenge of renewable energy integration is:',
                            'options': {
                                'A': 'High initial costs',
                                'B': 'Intermittency of generation',
                                'C': 'Lack of available technology',
                                'D': 'Public opposition'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph B states \'The fundamental challenge lies in intermittency\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Wind power is now economically competitive with conventional power plants.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph A states wind \'has similarly become economically competitive\'.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'Solar farms require less land than coal power stations for equivalent output.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph B indicates solar farms \'could require hundreds of acres\' compared to coal\'s \'several acres\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Battery storage at grid scale is currently inexpensive and easy to implement.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph B states \'storing electricity at grid scale remains expensive and materials-intensive\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Smart _______ systems balance electricity supply and demand in real-time.',
                            'correct_answer': 'grid',
                            'explanation': 'Paragraph C mentions \'Smart grid systems\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': '_______ power provides consistent baseload electricity to stabilize grids.',
                            'correct_answer': 'geothermal',
                            'explanation': 'Both geothermal and hydroelectric are mentioned; either answer acceptable, but \'geothermal\' appears first.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': '_______ produced through electrolysis offers a potential storage solution.',
                            'correct_answer': 'hydrogen',
                            'explanation': 'Stated in paragraph C.'
                        }
                    ]
                },
                {
                    'title': 'The Science of Sleep',
                    'category': 'Science',
                    'difficulty': 7.0,
                    'content': '''
A Sleep represents a fundamental biological necessity that occupies approximately one-third of human life, yet its precise functions and mechanisms remained largely mysterious until recent decades. Contemporary sleep research has revealed that far from being a passive state of rest, sleep involves complex active processes that are essential for physical health, cognitive function, and emotional regulation. During sleep, the brain cycles through distinct stages, each characterized by different patterns of electrical activity and serving specific purposes. Non-rapid eye movement (NREM) sleep, which comprises about 75% of total sleep time, appears particularly important for physical restoration and memory consolidation, while rapid eye movement (REM) sleep, marked by vivid dreaming and intense brain activity, plays crucial roles in emotional processing and creative problem-solving.

B The consequences of inadequate sleep extend far beyond simple fatigue, affecting virtually every physiological system. Chronic sleep deprivation has been linked to increased risk of cardiovascular disease, diabetes, obesity, and weakened immune function. Even moderate sleep restriction—sleeping six hours nightly instead of the recommended seven to nine—produces measurable cognitive impairments equivalent to being legally intoxicated. Sleep-deprived individuals demonstrate reduced attention spans, impaired decision-making abilities, and decreased memory formation. Furthermore, insufficient sleep disrupts hormonal balance, increasing production of ghrelin (which stimulates appetite) while decreasing leptin (which signals satiety), thereby promoting weight gain. Studies of shift workers, who frequently experience disrupted sleep schedules, reveal elevated rates of numerous health conditions, suggesting that irregular sleep patterns may be particularly harmful. The accumulation of these effects has led some researchers to describe modern society's sleep patterns as a public health crisis.

C Despite growing awareness of sleep's importance, understanding individual sleep requirements remains complex. While general guidelines recommend seven to nine hours for adults, optimal sleep duration varies based on age, genetics, lifestyle, and overall health. Some individuals function well on relatively little sleep—genuine "short sleepers" who naturally require only five to six hours without apparent negative effects—though such people represent a small minority of the population, perhaps 1-3%. More commonly, people mistakenly believe they have adapted to insufficient sleep when they have actually experienced a deterioration in performance that they no longer recognize. Improving sleep quality involves multiple strategies: maintaining consistent sleep schedules, avoiding screens before bedtime (as blue light suppresses melatonin production), creating cool, dark sleeping environments, and managing stress through relaxation techniques. As neuroscience continues advancing, researchers hope to develop more targeted interventions for sleep disorders and better understand sleep's essential but still partly enigmatic functions.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'According to paragraph A, REM sleep is important for:',
                            'options': {
                                'A': 'Physical restoration only',
                                'B': 'Memory consolidation',
                                'C': 'Emotional processing and creative problem-solving',
                                'D': 'Regulating body temperature'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph A states REM sleep \'plays crucial roles in emotional processing and creative problem-solving\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'What percentage of the population are genuine \'short sleepers\'?',
                            'options': {
                                'A': '10-15%',
                                'B': '5-8%',
                                'C': '1-3%',
                                'D': '20-25%'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph C states \'perhaps 1-3%\' of the population.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'NREM sleep comprises about 75% of total sleep time.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Directly stated in paragraph A.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'Six hours of sleep produces cognitive impairments similar to legal intoxication.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Paragraph B states \'sleeping six hours nightly... produces measurable cognitive impairments equivalent to being legally intoxicated\'.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'Everyone requires exactly the same amount of sleep regardless of age or genetics.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C explicitly states \'optimal sleep duration varies based on age, genetics, lifestyle, and overall health\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Sleep deprivation increases _______, a hormone that stimulates appetite.',
                            'correct_answer': 'ghrelin',
                            'explanation': 'Paragraph B mentions ghrelin \'which stimulates appetite\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Blue light from screens suppresses _______ production before bedtime.',
                            'correct_answer': 'melatonin',
                            'explanation': 'Stated in paragraph C.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'Adults are generally recommended to sleep _______ to nine hours.',
                            'correct_answer': 'seven',
                            'explanation': 'Paragraph B mentions \'the recommended seven to nine\' hours.'
                        }
                    ]
                },
                {
                    'title': 'Space Exploration Milestones',
                    'category': 'History',
                    'difficulty': 7.0,
                    'content': '''
A Humanity's venture into space represents one of the most ambitious and transformative endeavors in history, fundamentally altering our understanding of the universe and our place within it. The Space Age began dramatically on October 4, 1957, when the Soviet Union successfully launched Sputnik 1, the first artificial satellite to orbit Earth. This achievement shocked the United States and initiated the Space Race, a competition between the two superpowers that would drive rapid technological advancement throughout the following decades. Sputnik's success demonstrated the feasibility of space travel and had profound implications for both scientific research and geopolitical power dynamics. Within months, the United States responded with its own satellite program, and the competition escalated rapidly, encompassing increasingly ambitious goals from the first human spaceflight to lunar landing.

B The pinnacle of the Space Race arrived on July 20, 1969, when American astronaut Neil Armstrong became the first human to walk on the Moon during the Apollo 11 mission. This extraordinary achievement required overcoming immense technical challenges, from developing powerful enough rockets to creating life support systems capable of sustaining humans in the hostile lunar environment. The Apollo program employed over 400,000 people and consumed approximately $25 billion (equivalent to over $150 billion today), representing a massive commitment of resources driven by both scientific curiosity and Cold War competition. Beyond its historical significance, the lunar landing produced lasting benefits including technological innovations that found applications in computing, materials science, and telecommunications. The famous "Earthrise" photograph taken during Apollo 8 profoundly influenced environmental consciousness by showing Earth as a fragile, unified system floating in the void of space.

C Following the Apollo era, space exploration evolved from nationalistic competition toward international cooperation and diverse objectives. The International Space Station (ISS), launched in phases beginning in 1998, exemplifies this collaborative approach, with participation from the United States, Russia, Europe, Japan, and Canada. The ISS serves as a permanent laboratory for conducting experiments in microgravity, advancing understanding of biology, physics, and materials science while also providing valuable data on human adaptation to long-duration spaceflight. Robotic exploration has expanded humanity's reach throughout the solar system, with probes investigating Mars, Venus, Jupiter's moons, and Saturn's rings, while spacecraft like Voyager 1 have entered interstellar space. Private companies now complement government space agencies, with firms like SpaceX developing reusable rockets that dramatically reduce launch costs. Current ambitions include establishing permanent lunar bases, conducting crewed missions to Mars, and searching for signs of extraterrestrial life. As technology continues advancing, space exploration promises to remain at the frontier of human achievement, driven by our enduring desire to explore the unknown and perhaps eventually to become a multi-planetary species.
                    ''',
                    'questions': [
                        {
                            'number': 1,
                            'type': 'multiple_choice',
                            'text': 'The Space Age began with the launch of:',
                            'options': {
                                'A': 'Apollo 11',
                                'B': 'Sputnik 1',
                                'C': 'The International Space Station',
                                'D': 'Voyager 1'
                            },
                            'correct_answer': 'B',
                            'explanation': 'Paragraph A states \'The Space Age began dramatically on October 4, 1957, when the Soviet Union successfully launched Sputnik 1\'.'
                        },
                        {
                            'number': 2,
                            'type': 'multiple_choice',
                            'text': 'How much did the Apollo program cost (in modern equivalent)?',
                            'options': {
                                'A': '$25 billion',
                                'B': '$50 billion',
                                'C': 'Over $150 billion',
                                'D': '$200 billion'
                            },
                            'correct_answer': 'C',
                            'explanation': 'Paragraph B states it consumed \'$25 billion (equivalent to over $150 billion today)\'.'
                        },
                        {
                            'number': 3,
                            'type': 'true_false_ng',
                            'text': 'Neil Armstrong was the first human to walk on the Moon.',
                            'correct_answer': 'TRUE',
                            'explanation': 'Explicitly stated in paragraph B.'
                        },
                        {
                            'number': 4,
                            'type': 'true_false_ng',
                            'text': 'The International Space Station is operated exclusively by the United States.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph C lists multiple participating countries: US, Russia, Europe, Japan, and Canada.'
                        },
                        {
                            'number': 5,
                            'type': 'true_false_ng',
                            'text': 'The \'Earthrise\' photograph had no impact on environmental awareness.',
                            'correct_answer': 'FALSE',
                            'explanation': 'Paragraph B states it \'profoundly influenced environmental consciousness\'.'
                        },
                        {
                            'number': 6,
                            'type': 'fill_blank',
                            'text': 'Sputnik 1 was launched by the _______ Union in 1957.',
                            'correct_answer': 'Soviet',
                            'explanation': 'Paragraph A specifies \'the Soviet Union\'.'
                        },
                        {
                            'number': 7,
                            'type': 'fill_blank',
                            'text': 'Private companies like _______ are developing reusable rockets.',
                            'correct_answer': 'SpaceX',
                            'explanation': 'Mentioned in paragraph C.'
                        },
                        {
                            'number': 8,
                            'type': 'fill_blank',
                            'text': 'The Apollo program employed over _______ people.',
                            'correct_answer': '400000',
                            'explanation': 'Stated in paragraph B (accepts \'400,000\' or \'400000\').'
                        }
                    ]
                }
            ]
            
            # Проверяем, есть ли уже passages
            existing_count = EnglishPassage.query.count()
            print(f"📊 Текущее количество passages в БД: {existing_count}")
            
            # Загружаем passages (пропускаем существующие по title)
            loaded_count = 0
            skipped_count = 0
            for passage_data in passages_data:
                try:
                    # Проверяем, существует ли уже passage с таким title
                    existing_passage = EnglishPassage.query.filter_by(title=passage_data['title']).first()
                    if existing_passage:
                        # Обновляем изображение, если его нет, но есть в маппинге
                        image_url = get_image_url(passage_data['title'])
                        if image_url and not existing_passage.image_url:
                            existing_passage.image_url = image_url
                            db.session.commit()
                            print(f"🖼️  Обновлено изображение для: '{passage_data['title']}'")
                        else:
                            print(f"⏭️  Пропущен (уже существует): '{passage_data['title']}'")
                        skipped_count += 1
                        continue
                    
                    # Создаем passage с автоматическим добавлением изображения
                    image_url = get_image_url(passage_data['title'])
                    passage = EnglishPassage(
                        title=passage_data['title'],
                        text=passage_data['content'].strip(),
                        difficulty=int(passage_data.get('difficulty', 7)),  # IELTS band level (1-9)
                        category=passage_data.get('category', 'general').lower(),
                        word_count=len(passage_data['content'].strip().split()),
                        image_url=image_url
                    )
                    db.session.add(passage)
                    db.session.flush()  # Получаем ID passage
                    
                    # Создаем вопросы
                    for q_data in passage_data['questions']:
                        question_type = q_data.get('type', q_data.get('question_type', 'multiple_choice'))
                        question_number = q_data.get('number', q_data.get('question_number', 1))
                        question_text = q_data.get('text', q_data.get('question_text', ''))
                        
                        # Обработка options в зависимости от типа вопроса
                        options_json = None
                        if question_type == 'multiple_choice':
                            # Options уже в формате {"A": "...", "B": "..."}
                            if isinstance(q_data.get('options'), dict):
                                options_json = json.dumps(q_data['options'])
                            elif isinstance(q_data.get('options'), list):
                                # Если options в виде списка, преобразуем в dict
                                options_dict = {}
                                for idx, option_text in enumerate(q_data['options']):
                                    option_letter = chr(65 + idx)  # A, B, C, D...
                                    options_dict[option_letter] = option_text
                                options_json = json.dumps(options_dict)
                        
                        # Обработка correct_answer
                        correct_answer = q_data.get('correct_answer', '')
                        if isinstance(correct_answer, int):
                            # Если индекс, преобразуем в букву
                            correct_answer = chr(65 + correct_answer)
                        elif isinstance(correct_answer, str):
                            # Уже буква или текст (для fill_blank, true_false_ng)
                            correct_answer = correct_answer.upper() if correct_answer in ['TRUE', 'FALSE', 'NOT GIVEN'] else correct_answer
                        
                        question = EnglishQuestion(
                            passage_id=passage.id,
                            question_number=question_number,
                            question_text=question_text,
                            question_type=question_type,
                            options=options_json,
                            correct_answer=str(correct_answer),
                            explanation=q_data.get('explanation', '')
                        )
                        db.session.add(question)
                    
                    loaded_count += 1
                    image_info = f" (изображение: {image_url})" if image_url else " (без изображения)"
                    print(f"✅ Загружен passage: '{passage.title}' с {len(passage_data['questions'])} вопросами{image_info}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при загрузке passage '{passage_data.get('title', 'unknown')}': {e}")
                    db.session.rollback()
                    continue
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"\n✅ Успешно загружено {loaded_count} новых passages!")
            if skipped_count > 0:
                print(f"⏭️  Пропущено {skipped_count} существующих passages")
            print(f"📊 Всего passages в БД: {EnglishPassage.query.count()}")
            print(f"📊 Всего вопросов в БД: {EnglishQuestion.query.count()}")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    seed_english_passages()

