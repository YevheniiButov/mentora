# utils/profession_content.py
"""
Персонализированный контент для каждой медицинской специальности
"""

PROFESSION_CONTENT = {
    'tandarts': {
        'welcome': {
            'title': 'Welkom bij uw Tandheelkunde Leerkaart',
            'subtitle': 'Uw persoonlijke pad naar BIG-registratie en tandheelkundige excellentie',
            'description': '''
            Deze leerkaart is speciaal ontworpen voor internationale tandartsen die zich voorbereiden 
            op de BIG-toets en Nederlandse tandheelkundige praktijk. Onze adaptieve leerroute helpt u 
            systematisch alle benodigde competenties te ontwikkelen.
            ''',
            'icon': '🦷',
            'color_primary': '#3498db',
            'color_secondary': '#2980b9'
        },
        'getting_started': {
            'title': 'Zo werkt uw tandheelkunde leerpad',
            'steps': [
                {
                    'icon': '🎯',
                    'title': 'Start met kennistoets',
                    'description': '''
                    Begin met onze uitgebreide kennistoets die uw huidige niveau in Nederlandse 
                    tandheelkunde vaststelt. Deze toets evalueert:
                    • Anatomie en fysiologie van het orofaciale systeem
                    • Nederlandse behandelprotocollen en richtlijnen
                    • Materiaalkennis en instrumentarium
                    • Wetgeving en ethiek in Nederlandse zorgverlening
                    '''
                },
                {
                    'icon': '📊',
                    'title': 'Persoonlijk leerplan',
                    'description': '''
                    Op basis van uw resultaten maken we een gepersonaliseerd leerplan dat focust op:
                    • Zwakke kennisgebieden die extra aandacht vereisen
                    • Prioritering van onderwerpen voor optimale voorbereiding
                    • Realistische tijdsinschatting per module
                    • Concrete leerdoelen en mijlpalen
                    '''
                },
                {
                    'icon': '🧠',
                    'title': 'Adaptief leren',
                    'description': '''
                    Onze AI-gestuurde leeromgeving past zich aan uw voortgang aan:
                    • Moeilijke onderwerpen krijgen meer herhalingsoefeningen
                    • Succesvolle modules worden minder frequent herhaald
                    • Spaced repetition voor optimale kennisretentie
                    • Continue bijsturing van uw leerpad
                    '''
                },
                {
                    'icon': '💼',
                    'title': 'Praktijkvoorbereiding',
                    'description': '''
                    Bereid u voor op de Nederlandse tandheelkundige praktijk:
                    • Virtuele patiëntcases uit de Nederlandse praktijk
                    • Communicatie met patiënten in het Nederlands
                    • Administratieve procedures en verzekeringssysteem
                    • Kwaliteitseisen en protocollen
                    '''
                }
            ]
        },
        'modules_intro': '''
        Uw leerpad bestaat uit 7 gespecialiseerde modules, elk gericht op een specifiek 
        aspect van de Nederlandse tandheelkunde. Elke module bevat interactieve lessen, 
        oefenvragen en praktijkcases.
        '''
    },
    
    'apotheker': {
        'welcome': {
            'title': 'Welkom bij uw Farmacie Leerkaart',
            'subtitle': 'Uw route naar BIG-registratie en farmaceutische praktijk in Nederland',
            'description': '''
            Deze leerkaart begeleidt internationale apothekers bij de voorbereiding op de BIG-toets 
            en Nederlandse farmaceutische praktijk. Leer de specifieke Nederlandse procedures, 
            wetgeving en patiëntenzorg.
            ''',
            'icon': '💊',
            'color_primary': '#9b59b6',
            'color_secondary': '#8e44ad'
        },
        'getting_started': {
            'title': 'Zo werkt uw farmacie leerpad',
            'steps': [
                {
                    'icon': '🔬',
                    'title': 'Farmacologische kennistoets',
                    'description': '''
                    Start met een uitgebreide toets die uw kennis evalueert van:
                    • Nederlandse formularium en medicijnregistratie
                    • Interacties en contraindicaties
                    • Dosering en toedieningsvormen
                    • Bijwerkingen en monitoring
                    • Wetgeving rondom geneesmiddelen
                    '''
                },
                {
                    'icon': '📋',
                    'title': 'Gepersonaliseerd studieschema',
                    'description': '''
                    Uw persoonlijke leerplan richt zich op:
                    • Kennislacunes in farmacotherapie
                    • Nederlandse apotheekpraktijk en -procedures
                    • Patiëntcommunicatie en medicatiebegeleiding
                    • Kwaliteitszorg en risicomanagement
                    '''
                },
                {
                    'icon': '🎯',
                    'title': 'Adaptieve leerroute',
                    'description': '''
                    Het systeem past zich aan uw expertise aan:
                    • Focus op moeilijke farmacotherapeutische gebieden
                    • Herhalingsoefeningen voor kritieke interacties
                    • Praktijkgerichte casuïstiek
                    • Voortgangstracking per specialisatie
                    '''
                },
                {
                    'icon': '👥',
                    'title': 'Nederlandse apotheekpraktijk',
                    'description': '''
                    Praktische voorbereiding op de Nederlandse context:
                    • Zorgverzekeringssysteem en vergoedingen
                    • Samenwerking met huisartsen en specialisten
                    • Apotheekautomatisering en ICT-systemen
                    • Kwaliteits- en veiligheidsnormen
                    '''
                }
            ]
        },
        'modules_intro': '''
        Uw farmaceutische leerpad omvat 5 kernmodules die alle aspecten van de Nederlandse 
        apotheekpraktijk bestrijken, van medicatiebegeleiding tot wetgeving en kwaliteitszorg.
        '''
    },
    
    'verpleegkundige': {
        'welcome': {
            'title': 'Welkom bij uw Verpleegkunde Leerkaart',
            'subtitle': 'Uw pad naar BIG-registratie en Nederlandse verpleegkundige zorg',
            'description': '''
            Deze leerkaart ondersteunt internationale verpleegkundigen bij de voorbereiding op 
            de BIG-toets en integratie in de Nederlandse gezondheidszorg. Focus op patiëntenzorg, 
            veiligheid en Nederlandse zorgstandaarden.
            ''',
            'icon': '👩‍⚕️',
            'color_primary': '#e74c3c',
            'color_secondary': '#c0392b'
        },
        'getting_started': {
            'title': 'Zo werkt uw verpleegkunde leerpad',
            'steps': [
                {
                    'icon': '🏥',
                    'title': 'Zorgvaardigheden assessment',
                    'description': '''
                    Begin met een grondige evaluatie van uw verpleegkundige competenties:
                    • Anatomie, fysiologie en pathologie
                    • Nederlandse verpleegkundige procedures
                    • Medicatieveiligheid en toediening
                    • Infectiepreventie en hygiëne
                    • Communicatie en ethiek in de zorg
                    '''
                },
                {
                    'icon': '📊',
                    'title': 'Competentiegericht leerplan',
                    'description': '''
                    Uw persoonlijke ontwikkelingsroute focust op:
                    • Specifieke zorgvaardigheden die verbetering behoeven
                    • Nederlandse richtlijnen en protocollen
                    • Patiëntveiligheid en kwaliteitszorg
                    • Professionele communicatie en samenwerking
                    '''
                },
                {
                    'icon': '🔄',
                    'title': 'Adaptieve zorgtraining',
                    'description': '''
                    Het systeem past zich aan uw competentieniveau aan:
                    • Intensieve training voor uitdagende vaardigheden
                    • Praktijksimulaties en casus-studies
                    • Spaced repetition voor kritieke procedures
                    • Continue evaluatie en bijsturing
                    '''
                },
                {
                    'icon': '🎓',
                    'title': 'SKV accreditatie voorbereiding',
                    'description': '''
                    Speciale voorbereiding op Nederlandse zorgstandaarden:
                    • SKV accreditatiepunten en eisen
                    • Specialisatierichtingen (ICU, OK, etc.)
                    • Nederlandse zorgwetgeving en ethiek
                    • Multidisciplinaire samenwerking
                    '''
                }
            ]
        },
        'modules_intro': '''
        Uw verpleegkundige leerpad bestaat uit 6 modules die alle aspecten van moderne 
        Nederlandse verpleegkunde bestrijken, van basiszorg tot gespecialiseerde vaardigheden.
        '''
    },
    
    'huisarts': {
        'welcome': {
            'title': 'Welkom bij uw Huisartsgeneeskunde Leerkaart',
            'subtitle': 'Uw route naar BIG-registratie en Nederlandse huisartsenpraktijk',
            'description': '''
            Deze leerkaart begeleidt internationale artsen naar een succesvolle praktijk als 
            huisarts in Nederland. Focus op NHG-richtlijnen, preventieve zorg en de Nederlandse 
            zorgstructuur.
            ''',
            'icon': '🩺',
            'color_primary': '#27ae60',
            'color_secondary': '#229954'
        },
        'getting_started': {
            'title': 'Zo werkt uw huisartsgeneeskunde leerpad',
            'steps': [
                {
                    'icon': '🎯',
                    'title': 'Medische kennistoets',
                    'description': '''
                    Uitgebreide evaluatie van uw medische expertise:
                    • Nederlandse ziektebeelden en prevalenties
                    • NHG-richtlijnen en standaarden
                    • Farmacotherapie in de eerste lijn
                    • Diagnostiek en verwijsprotocollen
                    • Preventieve geneeskunde en screening
                    '''
                },
                {
                    'icon': '📋',
                    'title': 'NHG-gericht studieprogramma',
                    'description': '''
                    Uw leerplan is afgestemd op Nederlandse huisartsgeneeskunde:
                    • Prioritering van veel voorkomende aandoeningen
                    • NHG-standaarden en -richtlijnen
                    • Eerste lijnszorg en -protocollen
                    • Samenwerking met tweede lijn
                    '''
                },
                {
                    'icon': '🧠',
                    'title': 'Evidence-based leren',
                    'description': '''
                    Adaptief systeem gebaseerd op Nederlandse praktijk:
                    • Focus op lokale ziektepatronen
                    • Praktijkgerichte casuïstiek
                    • Beslisbomen en diagnostische strategieën
                    • Continue update van kennis
                    '''
                },
                {
                    'icon': '🏠',
                    'title': 'Praktijkmanagement',
                    'description': '''
                    Voorbereiding op de Nederlandse huisartsenpraktijk:
                    • Praktijkorganisatie en -management
                    • Samenwerking met POH en praktijkondersteuning
                    • Zorgverzekeringssysteem en declaraties
                    • Kwaliteitsindicatoren en accreditatie
                    '''
                }
            ]
        },
        'modules_intro': '''
        Uw huisartsgeneeskunde leerpad omvat 7 kernmodules gebaseerd op de NHG-richtlijnen 
        en Nederlandse eerstelijnszorg, van acute zorg tot chronische ziektemanagement.
        '''
    }
}

def get_profession_content(profession):
    """
    Haal personalized content op voor een specifieke professie
    """
    return PROFESSION_CONTENT.get(profession, PROFESSION_CONTENT['tandarts'])

def get_welcome_message(profession, user_name=None):
    """
    Genereer een gepersonaliseerd welkomstbericht
    """
    content = get_profession_content(profession)
    welcome = content['welcome']
    
    greeting = f"Welkom {user_name}!" if user_name else "Welkom!"
    
    return {
        'greeting': greeting,
        'title': welcome['title'],
        'subtitle': welcome['subtitle'],
        'description': welcome['description'],
        'icon': welcome['icon'],
        'color_primary': welcome['color_primary'],
        'color_secondary': welcome['color_secondary']
    }

def get_learning_instructions(profession):
    """
    Haal leerinstructies op voor een specifieke professie
    """
    content = get_profession_content(profession)
    return content['getting_started']

def get_modules_introduction(profession):
    """
    Haal module introductie op voor een specifieke professie
    """
    content = get_profession_content(profession)
    return content['modules_intro']