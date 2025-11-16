#!/usr/bin/env python3
"""
Скрипт для загрузки Dutch Passages с вопросами
Использование: python scripts/seed_dutch_passages.py
"""

import os
import sys
from pathlib import Path
import json

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, DutchPassage, DutchQuestion
from datetime import datetime, timezone

# Данные пассажей (из JSON, который прислал пользователь)
PASSAGES_DATA = [
    {
        "passage": {
            "id": "nl_reading_001",
            "title": "De Revolutie van Kunstmatig Ontworpen Antilichamen: Wanneer AI de Biologie Ontmoet",
            "category": "biologie",
            "difficulty": "C1-C2",
            "language": "nl",
            "source": "Nature 2025 - Adapted",
            "word_count": 1150,
            "content": "# De Revolutie van Kunstmatig Ontworpen Antilichamen: Wanneer AI de Biologie Ontmoet\n\n## Inleiding: Een Doorbraak in Geneesmiddelenonderzoek\n\nDe afgelopen decennia hebben antilichamen zich gevestigd als een van de krachtigste wapens in de moderne geneeskunde. Met meer dan 160 antilichaamtherapieën op de markt en een verwachte waarde van ongeveer 445 miljard dollar in vijf jaar, blijven antilichamen onmisbaar voor de behandeling van infectieziekten, kanker en auto-immuunziekten. Ondanks hun cruciale rol in de therapie, bevat het proces voor het ontdekken van nieuwe antilichamen aanzienlijke beperking: het vertrouwen op dierimmunisatie, willekeurige bibliotheekscreening, of directe isolatie van antilichamen uit patiënten.\n\nNu heeft een baanbrekend onderzoek van wetenschappers onder leiding van Nobelprijswinnaar David Baker van de Universiteit van Washington aangetoond dat kunstmatige intelligentie antilichamen geheel \"vanuit het niets\" kan ontwerpen—met atoomnauwkeurigheid. Dit vertegenwoordigt een fundamentele verschuiving in hoe we biologische moleculen kunnen ontwerpen en optimaliseren.\n\n## Het Centrale Probleem: Waarom Antilichaamontwerp Zo Moeilijk Was\n\nAntilichamen functioneren door zich aan zeer specifieke plekken op virussen of giftige eiwitten vast te hechten—net als een sleutel die in één specifiek slot past. Deze precisie is kritisch: wanneer een geneesmiddel aan de verkeerde plek vast hecht, kan het onwerkzaam zijn of bijwerkingen veroorzaken.\n\nDe meest lastige onderdelen van antilichamen zijn de gebieden die als \"vingers\" functioneren—zij grijpen het doelmolecule. Historisch gezien waren deze vingers uitstekend moeilijk te ontwerpen omdat zij zeer buigzaam zijn. Computers konden de precieze vorm ervan niet voorspellen. Tot nu toe had de wetenschap daarom geen manier om antilichamen volledig via computer te ontwerpen en toch zeker te weten dat zij hun doelen zouden treffen.\n\n## De Oplossing: AI-Systemen voor Ontwerp\n\nDe onderzoekers gebruikten geavanceerde computer-modellen die traind waren op miljoenen bekende antilichaamstructuren. Dit proces werkt in meerdere stappen:\n\n1. **Vorm ontwerpen**: De computer voorspelt hoe het antilichaam zou moeten buigen en vouwen om precies op de juiste plaats te hechten.\n\n2. **Bouwstof bepalen**: Een tweede computerprogramma bepaalt welke chemische bouwblokken in deze vorm passen—net als puzzelstukken die in elkaar grijpen.\n\n3. **Haalbaarheid controleren**: Een derde systeem controleert of deze combinatie werkelijk in het lichaam zou kunnen functioneren en niet uiteen zou vallen.\n\n4. **Laboratoriumtesten**: De beloftenrijkste kandidaten werden vervolgens in het laboratorium gemaakt en getest met snelle screeningmethoden die miljarden kandidaten kunnen evalueren.\n\n## De Resultaten: Ongelooflijke Nauwkeurigheid\n\nDe onderzoekers concentreerden zich eerst op kleine antilichamen, afkomstig van dieren zoals lama's. Deze zijn waardevol omdat zij stabiel zijn en makkelijk in het lichaam kunnen werken.\n\nVier belangrijke doelen werden gekozen:\n\n- **Griepvirus**: Een belangrijk eiwit op influenza\n\n- **Een bacteriële vergif**: Afkomstig van gevaarlijke bacteriën\n\n- **Respiratoir virus**: Een virus dat de luchtwegen aantast\n\n- **Kanker-gerelateerd eiwit**: Een doel voor kankerbehandeling\n\nHet meest verbazingwekkende: experimenten toonden aan dat de kunstmatig ontworpen antilichamen met opmerkelijke precisie werkten—tot op het niveau van atomen nauwkeurig. Dit was niet vorheen mogelijk geweest. De onderzoekers gebruikten geavanceerde microscopie (duizenden keer sterker dan normale microscopen) om dit te bewijzen.\n\nIn één bijzonder succesvol geval blokkeerde het kunstmatig ontworpen antilichaam niet alleen een bacteriële vergif, maar beschermde het ook cellen tegen schade in laboratoriumproeven. Dit toonde aan dat de ontworpen antilichamen niet alleen theoretisch juist waren, maar ook werkelijk biologisch actief.\n\n## Van Ontwerp naar Therapie: Sterker Maken\n\nHoewel de kunstmatig ontworpen antilichamen succesvol waren, hechthen zij niet sterk genoeg aan hun doelen. Het was als een sleutel die in het juiste slot past maar niet sterk genoeg draait.\n\nDe onderzoekers gebruikten een genetisch systeem dat aan miljarden mutaties kon experimenteren in levend gist—als kunstmatige evolutie, maar miljoen keer sneller. Dit produceerde antilichamen die duizend keer sterker aan hun doelen hechthen.\n\nHet cruciale: ook na dit \"versterken\" bleven de antilichamen specifiek voor hun doelen. Zij hechthen nog steeds alleen aan waar zij hoorden te hechten.\n\n## Wat Dit Betekent voor Geneesmiddelen\n\nDeze doorbraak opent vele mogelijkheden:\n\n**Sneller onderzoek**: In plaats van jaren onderzoek kun je nu een computer gebruiken om een nieuw antilichaam in weken te ontwerpen.\n\n**Betere therapieën**: Veel doelen zijn \"moeilijk aan te vallen\" omdat zij zeer kleine veranderingen nodig hebben. Nu kan computer-ontwerp helpen.\n\n**Medicijnen voor zeldzame ziekten**: Onderzoek naar zeldzame ziekten was altijd duur. Met computerontwerp wordt het veel goedkoper.\n\n**Minder dierproeven**: Vroeger moest je dieren ziek maken om antilichamen te maken. Nu doet de computer het werk.\n\n## Toekomstige Uitdagingen\n\nDe onderzoekers waarschuwen dat er nog veel te doen is. Suikerketens op virusoppervlakken beïnvloeden hoe goed antilichamen werken, maar deze suikers zijn moeilijk voor computers te voorspellen. Volgende generatie AI-modellen moeten nog beter worden.\n\nDe computersoftware is gratis beschikbaar, dus onderzoekers wereldwijd kunnen dit gebruiken.\n\n## Conclusie: Een Nieuw Tijdperk voor Therapeutische Ontdekking\n\nDeze studie markeert een keerpunt in biologie: kunstmatige intelligentie kan nu niet alleen bestaande biologische systemen analyseren, maar kan ook nieuwe biologische moleculen ontwerpen met voorheen ongeëvenaarde precisie. De toekomst van geneesmiddelenontdekking ziet er niet meer uit als een race naar willekeurige kandidaten, maar als een methodische, door-computer-geleide expedition naar optimale therapeutische oplossingen.\n\nVoor miljarden mensen die wachten op behandelingen voor infecties, kanker, en auto-immuunziekten, zou dit kunnen betekenen dat geneesmiddelen sneller, goedkoper, en effectiever kunnen worden ontdekt dan ooit tevoren.",
            "vocabulary": [
                {"word": "hechten", "definition": "Vastklemmen, zich vasthouden aan iets; in dit geval: zich aan moleculen vast grepen"},
                {"word": "benadering", "definition": "Manier waarop iets benaderd wordt; strategie of methode"},
                {"word": "willekeurig", "definition": "Zonder patroon; lukraak; toevallig"},
                {"word": "voorkomen", "definition": "Tegengaan; verhinderen dat iets gebeurt; ook: zich voordoen"},
                {"word": "vervangen", "definition": "Iets anders in plaats van stellen; uitwisselen"},
                {"word": "verfijnd", "definition": "Geavanceerd, subtiel; zeer verfijnde of uitgekiend"},
                {"word": "bereiken", "definition": "Aankomen bij; tot iets komen; verwezenlijken"},
                {"word": "voortdurend", "definition": "Continu; zonder onderbreking; aanhoudend"},
                {"word": "keerpunt", "definition": "Cruciale moment waar alles verandert"},
                {"word": "ongeëvenaard", "definition": "Zonder gelijke; ongekend; nog nooit eerder gezien"}
            ]
        },
        "questions": [
            {
                "id": "q1",
                "type": "open",
                "question": "Wat was het centrale technische probleem dat artisanale antilichaamontdekking van volledig computationeel ontwerp belemmerde, en waarom waren de CDR-lussen zo kritiek in dit probleem?",
                "expected_points": [
                    "CDR-lussen zijn de meest variabele delen van antilichamen—de 'vingers' die epitopen grijpen",
                    "Hun extreme flexibiliteit maakte computerontwerp historisch onhaalbaar omdat hun structuur niet rigide genoeg was om nauwkeurig te voorspellen",
                    "Computers konden niet precies bepalen hoe deze lussen zich zouden vouwen of positioneren om hun doelen te bereiken",
                    "Dit was de kernreden waarom antilichaamontdekking afhankelijk was van fysieke methoden (immunisatie, screening)"
                ],
                "model_answer": "Het centrale probleem was dat de CDR-lussen (de 'vingers' van antilichamen die epitopen grijpen) zeer buigzaam zijn. Hun extreme flexibiliteit maakte het historisch onmogelijk voor computers om nauwkeurig te voorspellen hoe deze lussen zich zouden vouwen of positioneren om hun doelen te bereiken. Dit was de kernreden waarom antilichaamontdekking afhankelijk was van fysieke methoden zoals immunisatie en screening, in plaats van volledig computationeel ontwerp."
            },
            {
                "id": "q2",
                "type": "open",
                "question": "Beschrijf het drietrapsproces van RFdiffusion, ProteinMPNN en RoseTTAFold2. Welke specifieke functie vervult elk van deze AI-systemen, en waarom konden zij niet door één enkel AI-model worden vervangen?",
                "expected_points": [
                    "RFdiffusion: Genereert de 3D-structuur—het 'bouwplan'—van hoe het antilichaam zou moeten vouwen",
                    "ProteinMPNN: Bepaalt welke aminozuursequenties in die structuur passen—voegt de specifieke 'letters' toe",
                    "RoseTTAFold2: Valideert of die sequenties werkelijk zullen vouwen en binden zoals beoogd",
                    "Ze kunnen niet vervangen worden omdat elk een ander probleem oplost: geometrisch ontwerp, moleculaire samenstelling, en biologische haalbaarheid"
                ],
                "model_answer": "Het drietrapsproces bestaat uit: (1) RFdiffusion genereert de 3D-structuur—het 'bouwplan'—van hoe het antilichaam zou moeten vouwen. (2) ProteinMPNN bepaalt welke aminozuursequenties in die structuur passen—voegt de specifieke 'letters' toe. (3) RoseTTAFold2 valideert of die sequenties werkelijk zullen vouwen en binden zoals beoogd. Ze kunnen niet door één model worden vervangen omdat elk een ander probleem oplost: geometrisch ontwerp, moleculaire samenstelling, en biologische haalbaarheid."
            },
            {
                "id": "q3",
                "type": "open",
                "question": "Hoe bevestigde het gebruik van elektronenmicroscopie (cryo-EM) dat de computationeel ontworpen antilichamen niet slechts theoretische modellen waren, en wat specifieke waardes toonden deze experimenten aan over de precisie van het ontwerp?",
                "expected_points": [
                    "Cryo-EM produceerde echte, fysieke afbeeldingen van de antilichamen gebonden aan hun doelen",
                    "Dit kon vergeleken worden met computationele voorspellingen",
                    "Voor influenza waren de afwijkingen slechts 1,45 Ångströms (backbone) en 0,8 Ångströms (CDR3-lus)—atoomschaal precisie",
                    "Dit bewees dat kunstmatige ontwerp geen 'close enough' benadering was, maar werkelijk nauwkeurig was"
                ],
                "model_answer": "Cryo-EM produceerde echte, fysieke afbeeldingen van de antilichamen gebonden aan hun doelen, die vergeleken konden worden met computationele voorspellingen. Voor influenza waren de afwijkingen slechts 1,45 Ångströms (backbone) en 0,8 Ångströms (CDR3-lus)—atoomschaal precisie. Dit bewees dat kunstmatige ontwerp geen 'close enough' benadering was, maar werkelijk nauwkeurig was tot op het niveau van atomen."
            },
            {
                "id": "q4",
                "type": "open",
                "question": "Waarom was 'affinity maturation' via OrthoRep nodig, ondanks dat de computationele ontwerpen bereits de juiste epitopen bereikten? Wat was het verschil tussen structurele nauwkeurigheid en therapeutische bruikbaarheid?",
                "expected_points": [
                    "Structurele nauwkeurigheid ≠ sterke binding: het antilichaam kon de juiste plaats bereiken, maar hield niet stevig vast (bescheiden affinity)",
                    "OrthoRep maakte miljard mutaties mogelijk—evolutie in het laboratorium",
                    "Dit produceerde antilichamen met nanomolaire affiniteit (duizendvoudige verbetering)",
                    "Het belangrijkste: na maturation behielden zij specificiteit—zij bonden nog steeds correct"
                ],
                "model_answer": "Structurele nauwkeurigheid betekent niet automatisch sterke binding: het antilichaam kon de juiste plaats bereiken, maar hield niet stevig vast (bescheiden affinity). OrthoRep maakte miljard mutaties mogelijk—evolutie in het laboratorium. Dit produceerde antilichamen met nanomolaire affiniteit (duizendvoudige verbetering). Het belangrijkste: na maturation behielden zij specificiteit—zij bonden nog steeds alleen aan waar zij hoorden te hechten."
            },
            {
                "id": "q5",
                "type": "open",
                "question": "Vergelijk de traditionele antilichaamontdekkingsmethoden (immunisatie, bibliotheekscreening) met het RFdiffusion-systeem. Welke voordelen en potentiële nadelen ziet u in de AI-gebaseerde benadering?",
                "expected_points": [
                    "Voordelen: Snelheid (weken in plaats van jaren), Reproducibility, Ethisch (geen dieren nodig), Kosten-effectief",
                    "Potentiële nadelen: Initiële training vereist grote datasets, Nog steeds laboratoriumwerk nodig voor validatie, Humoraal antwoord van patiënten (immunogeniteit) nog niet volledig begrepen, Glycosyleringspatronen beïnvloeden binding (nog niet volledig voorspeld)"
                ],
                "model_answer": "Voordelen van RFdiffusion: snelheid (weken in plaats van jaren), reproducibility (computer kan altijd hetzelfde proces uitvoeren), ethisch (geen dieren nodig), kosten-effectief na initiële investering. Potentiële nadelen: initiële training vereist grote datasets, nog steeds laboratoriumwerk nodig voor validatie, humoraal antwoord van patiënten (immunogeniteit) nog niet volledig begrepen, glycosyleringspatronen beïnvloeden binding (nog niet volledig voorspeld)."
            },
            {
                "id": "q6",
                "type": "open",
                "question": "Welke drie medische gebieden zouden volgens het artikel het meest kunnen profiteren van de vermogen om antilichamen computationeel te ontwerpen, en waarom specifiek deze?",
                "expected_points": [
                    "'Moeilijk aan te vallen' targets (GPCRs): Deze vertegenwoordigen ~33% van farmaceutische doelen maar zijn notoir moeilijk omdat exacte structurele positionering nodig is",
                    "Zeldzame ziekten: Antilichaamontdekking was economisch onhaalbaar; nu kunnen computers het doen zonder kostbare immunisaties",
                    "Infectieziekten: Snelle aanpassung aan nieuwe varianten (aangegeven door influenza en TcdB examples)"
                ],
                "model_answer": "Drie medische gebieden: (1) 'Moeilijk aan te vallen' targets (GPCRs) vertegenwoordigen ~33% van farmaceutische doelen maar zijn notoir moeilijk omdat exacte structurele positionering nodig is. (2) Zeldzame ziekten: antilichaamontdekking was economisch onhaalbaar; nu kunnen computers het doen zonder kostbare immunisaties. (3) Infectieziekten: snelle aanpassung aan nieuwe varianten (aangegeven door influenza en TcdB examples)."
            },
            {
                "id": "q7",
                "type": "open",
                "question": "Het artikel noemt dat glycanen (suikers op virusoppervlakken) momenteel niet volledig door RFdiffusion kunnen worden inbegrepen in het ontwerp. Wat betekent dit praktisch voor de volgende generatie antilichaamontwerp, en hoe zou dit kunnen worden opgelost?",
                "expected_points": [
                    "Praktisch: de modellen ontwerpen antilichamen die 'kijken naar waar glycanen zijn,' maar kunnen niet volledig rekening houden met hun aanwezigheid",
                    "Dit kan binding verminderen of onverwachte interacties veroorzaken",
                    "Oplossing 1: AI-modellen uitbreiden om niet-eiwitatomen (glycanen, lipiden) te modelleren",
                    "Oplossing 2: Hybrid-benadering waarbij experimentele validatie vroeger in het proces plaatsvindt",
                    "Implicatie: volgende stap zou 'omnichemische' AI-modellen zijn—modellen die alle atomaire typen begrijpen"
                ],
                "model_answer": "Praktisch betekent dit dat de modellen antilichamen ontwerpen die 'kijken naar waar glycanen zijn,' maar niet volledig rekening kunnen houden met hun aanwezigheid. Dit kan binding verminderen of onverwachte interacties veroorzaken. Oplossingen: (1) AI-modellen uitbreiden om niet-eiwitatomen (glycanen, lipiden) te modelleren. (2) Hybrid-benadering waarbij experimentele validatie vroeger in het proces plaatsvindt. De volgende stap zou 'omnichemische' AI-modellen zijn—modellen die alle atomaire typen begrijpen."
            }
        ]
    },
    {
        "passage": {
            "id": "nl_reading_002",
            "title": "Waarom Plastic in Onze Oceanen Sneller Afbreekt dan Gedacht",
            "category": "milieu",
            "difficulty": "C1-C2",
            "language": "nl",
            "source": "PNAS 2024 - Adapted",
            "word_count": 1120,
            "content": "# Waarom Plastic in Onze Oceanen Sneller Afbreekt dan Gedacht\n\nTijdens decennia hebben wetenschappers aangenomen dat plastic in oceanen honderden of zelfs duizenden jaren zou blijven bestaan. Dit pessimistische beeld vormde de basis van veel klimaat- en milieubeleid. Echter, recent onderzoek suggereert een meer genuanceerd verhaal: onder bepaalde omstandigheden breekt plastic veel sneller af dan eerder werd gedacht.\n\nEen internationaal onderzoeksteam ontdekte dat bepaalde bacteriën en schimmels in de oceaan plastic kunnen 'eten'—het afbreken in kleinere moleculen. Deze microörganismen zijn niet nieuw; zij hebben zich waarschijnlijk miljoen jaren lang in oceanen bevonden. Wat wel nieuw is, is dat plasticvervuiling in de afgelopen decennia in volume is geëxplodeerd, wat bacteriën en schimmels de kans gaf om zich aan dit nieuwe 'voedsel' aan te passen.\n\n## Het Onderzoek\n\nWetenschappers uit meerdere landen verzamelden monsters van zeewatermicrobes in verschillende delen van de Atlantische Oceaan. Zij isoleerden organismen die in laboratorium-experimenten plastic afbraken. Het onderzoek toonde aan dat deze organismen specifieke enzymen produceren—biologische catalysators—die polymeren (de lange ketens waaruit plastic bestaat) kunnen breken.\n\nEen bijzonder interessant organisme was een bacteriënstam die gedeeltelijk plastic kon opeten. Dit bacterie had blijkbaar genetische mutaties ontwikkeld die haar in staat stelden een enzym te produceren dat polyethyleentereftalaat (PET)—een veel gebruikt plasticstype—kon afbreken.\n\nHet onderzoek toonde ook aan dat deze afbraaksnelheid afhankelijk is van verschillende factoren. Temperatuur speelt een rol: warmere oceanen zien snellere afbraak. Ook de chemische samenstelling van het plastic is belangrijk. Sommige plastictypen breken sneller af dan andere.\n\n## Implicaties en Voorzichtigheid\n\nAls eerste reactie klinkt dit goed nieuws: als plastic sneller afbreekt, is het milieuprobleem minder ernstig dan we dachten. Echter, wetenschappers waarschuwen dat dit nog niet het volledige verhaal is.\n\nTen eerste: zelfs als plastic sneller afbreekt, kan dit proces nog steeds tientallen of honderdden jaren duren in koude oceaangebieden. In warme tropen kan het sneller gaan, maar in arctische wateren verloopt het proces traag.\n\nTen tweede: wanneer plastic afbreekt, wordt het niet gewoon verdwenen. Het wordt opgebroken in microplastics—kleine stukjes plastic die nog steeds in het ecosysteem blijven. Deze microplastics worden ingenomen door vissen, krill en andere zeelevensvorm, wat negatieve gevolgen voor het zeeleven kan hebben.\n\nTen derde: de afbraakproducten van plastic zijn zelf niet altijd onschuldig. Sommige chemische stoffen die vrijkomen wanneer plastic afbreekt, kunnen toxisch zijn voor mariene organismen.\n\n## De Bredere Context\n\nHet feit dat bacteriën en schimmels plastic kunnen afbreken, is voorzichtig positief voor het toekomstig beheer van oceaanplasticide. Dit suggereert dat, in theoretische zin, de natuur zelf methoden heeft om bepaalde soorten vervuiling af te breken.\n\nHowel dit onderzoek fascinerend is, zeggen wetenschappers dat het niet betekent dat we onze plastic consumptie kunnen voortzetten zonder gevolgen. Het meest effectieve antwoord op oceaanplasticvervuiling blijft het voorkomen van plastic afval bij de bron: minder plastic produceren en beter recyclen.\n\nEr zijn ook pogingen om deze natuurlijke afbraakprocessen kunstmatig te versnellen. Wetenschappers werken aan genetically modified bacteriën die plastic sneller kunnen afbreken. Dit zou een potentiële hulpmiddel kunnen zijn in de toekomst, hoewel dit ook risico's met zich meebrengt.\n\nEindelijk onderstrepen deze bevindingen een belangrijk principe: ecosystemen zijn complex en adaptief. Wanneer miljoenenbiljoen tonnen nieuw materiaal in de oceaan terechtkomen, passen organismen zich aan. Dit is eerder een teken van nood dan van hoop—het suggereert dat de oceaan nu in een crisissituatie verkeert en zich moet aanpassen aan van mensen gemaakte vervuiling.",
            "vocabulary": [
                {"word": "afbreken", "definition": "In kleinere stukken/moleculen ontbinden; desintegreren; degraderen"},
                {"word": "aangenomen", "definition": "Verondersteld; gedacht dat iets waar is; aannemen"},
                {"word": "genuanceerd", "definition": "Met subtiele verschillen; niet zwart-wit; met nuances"},
                {"word": "geëxplodeerd", "definition": "Plotseling zeer sterk toegenomen; explosief gegroeid"},
                {"word": "aanpassen", "definition": "Zich aanpassen; veranderen om beter te passen bij nieuwe omstandigheden"},
                {"word": "verzamelden", "definition": "Bijeenbrachten; verzamelen (verleden tijd)"},
                {"word": "isoleerden", "definition": "Afzonderden; apart namen; isoleren (verleden tijd)"},
                {"word": "waarschuwen", "definition": "Voor gevaar of probleem waarschuwen; alert maken"}
            ]
        },
        "questions": [
            {
                "id": "q1",
                "type": "multiple_choice",
                "question": "Wat was de traditionele aanname over hoe lang plastic in oceanen zou blijven?",
                "options": [
                    "A) 10-20 jaar",
                    "B) 50-100 jaar",
                    "C) Honderden of duizenden jaren",
                    "D) Plastic breekt nooit af in oceanen"
                ],
                "correct_answer": "C",
                "explanation": "De tekst stelt duidelijk dat wetenschappers aannahmen dat plastic honderden of zelfs duizenden jaren zou blijven bestaan."
            },
            {
                "id": "q2",
                "type": "multiple_choice",
                "question": "Welk organisme kon in het onderzoek plastic afbreken?",
                "options": [
                    "A) Alleen bacteriën",
                    "B) Alleen schimmels",
                    "C) Alleen visssen",
                    "D) Bacteriën en schimmels"
                ],
                "correct_answer": "D",
                "explanation": "Het onderzoek identificeerde zowel bacteriën als schimmels die in staat waren plastic af te breken door specifieke enzymen te produceren."
            },
            {
                "id": "q3",
                "type": "open",
                "question": "Hoe hebben bacteriën zich aangepast om plastic te kunnen afbreken, en welk specifiek plasticstype werd genoemd?",
                "expected_points": [
                    "Genetische mutaties hebben zich ontwikkeld",
                    "Deze mutaties stelden bacteriën in staat enzymen te produceren",
                    "PET (polyethyleentereftalaat) werd als voorbeeld genoemd",
                    "Dit is een veel gebruikt plasticstype"
                ],
                "model_answer": "Bacteriënstammen hebben genetische mutaties ontwikkeld die hen in staat stelden enzymen te produceren die bepaalde plastictypen kunnen afbreken. Een specifiek voorbeeld was polyethyleentereftalaat (PET), een veel gebruikt plasticstype in verpakkingen."
            },
            {
                "id": "q4",
                "type": "open",
                "question": "Noem drie factoren die de afbraaksnelheid van plastic in oceanen beïnvloeden, en verklaar waarom dit belangrijk is.",
                "expected_points": [
                    "Temperatuur (warmer = sneller afbraak)",
                    "Chemische samenstelling van plastic (sommige breken sneller af)",
                    "Geografische locatie (arctisch vs tropen)",
                    "Belangrijk omdat het bepaalt hoe lang plastic in ecosysteem blijft"
                ],
                "model_answer": "Drie belangrijke factoren zijn temperatuur (warmere oceanen zien snellere afbraak), de chemische samenstelling van het plastic (sommige typen breken sneller af dan andere), en geografische locatie (arctische wateren hebben langzamere afbraak dan tropische wateren). Dit is belangrijk omdat het bepaalt hoe lang plastic in het oceaanecosysteem blijft en hoeveel schade het kan veroorzaken."
            },
            {
                "id": "q5",
                "type": "open",
                "question": "Waarom waarschuwen wetenschappers dat snellere afbraak van plastic niet hetzelfde is als het probleem oplossen?",
                "expected_points": [
                    "Afbraak leidt tot microplastics, niet verdwijning",
                    "Microplastics worden ingenomen door zeeleven",
                    "Afbraakproducten kunnen toxisch zijn",
                    "Proces duurt nog steeds tientallen/honderdden jaren in koude wateren"
                ],
                "model_answer": "Snellere afbraak leidt niet tot verdwijning van plastic—het breekt af in microplastics die nog steeds in het ecosysteem blijven. Deze microplastics worden ingenomen door vissen en ander zeeleven, wat schadelijk kan zijn. Bovendien kunnen de chemische stoffen die vrijkomen bij afbraak toxisch zijn. Zelfs met versnelde afbraak duurt het proces nog steeds tientallen of honderdden jaren in koude oceaangebieden."
            },
            {
                "id": "q6",
                "type": "multiple_choice",
                "question": "Wat stellen wetenschappers voor als het meest effectieve antwoord op oceaanplasticvervuiling?",
                "options": [
                    "A) Bacteriën introduceren die plastic afbreken",
                    "B) Minder plastic produceren en beter recyclen—voorkomen bij de bron",
                    "C) Alle plastic uit oceanen verwijderen met netten",
                    "D) Wachten tot bacteriën al het plastic afbreken"
                ],
                "correct_answer": "B",
                "explanation": "De tekst stelt duidelijk dat het meest effectieve antwoord het voorkomen van plastic afval bij de bron is: minder plastic produceren en beter recyclen."
            },
            {
                "id": "q7",
                "type": "multiple_choice",
                "question": "Wat suggereert het feit dat bacteriën zich hebben aangepast aan plastcafbraak over de toestand van de oceaan?",
                "options": [
                    "A) De oceaan herstelt zichzelf perfect",
                    "B) Het bewijs dat de natuur zich altijd aanpast",
                    "C) Dat de oceaan in een crisissituatie verkeert en zich moet aanpassen",
                    "D) Dat plastic geen probleem meer is"
                ],
                "correct_answer": "C",
                "explanation": "De tekst concludeert dat deze adaptatie 'eerder een teken van nood dan van hoop' is—het suggereert dat de oceaan nu in een crisissituatie verkeert en zich moet aanpassen aan van mensen gemaakte vervuiling."
            }
        ]
    },
    {
        "passage": {
            "id": "nl_reading_003",
            "title": "Hoe Archeologen Een Verloren Stad in het Amazoneregenwoud Ontdekten",
            "category": "archeologie",
            "difficulty": "C1-C2",
            "language": "nl",
            "source": "Nature Archaeology 2024 - Adapted",
            "word_count": 1090,
            "content": "# Hoe Archeologen Een Verloren Stad in het Amazoneregenwoud Ontdekten\n\nVoor honderden jaren hebben archeologen gefantaseerd over 'verloren steden' verborgen onder het dichte regenwoud van het Amazonegebied. Deze fascinatie werd voorgoed veranderd door een revolutionaire technologie: lidar (Light Detection and Ranging). Met behulp van lidar hebben onderzoekers ontdekt wat mogelijk een van de grootste pre-Colombiaanse steden in Zuid-Amerika is, verscholen onder de groene mantel van het regenwoud.\n\n## Wat is LIDAR?\n\nLidar is een technologie die laser-pulsen naar de grond stuurt en meet hoe lang het duurt voordat de laser terugkaatst. Dit creëert een gedetailleerde drie-dimensionale kaart van het landschap. Het grote voordeel van lidar boven traditionele fotografie is dat het door de bladerdak van het regenwoud kan dringen—het kan 'zien' wat onder de bomen verborgen ligt.\n\nTrustese technologie maakte het mogelijk om grote lijnen in het landschap te identificeren die niet zichtbaar zijn voor het blote oog of op satellietfoto's. Deze lijnen bleken kunstmatige aanlegde structuren te zijn, suggestief voor een complexe menselijke nederzetting.\n\n## De Ontdekking\n\nOnderzoekers richtten hun lidar-scans op een gebied in de Boliviaanse grensstreek van het Amazonegebied. Wat zij vonden, was verbijsterend: geometrische patronen die suggereerden dat een zeer georganiseerde bevolking deze regio had bewoond. De patronen toonden rechthoekige platforms, waterleidingen en gestructureerde plantagegebieden.\n\nNa analyse van de lidar-gegevens ging een onderzoekersteam ter plekke om fysieke bewijs te verzamelen. Zij vonden artefacten die werden gedateerd op ongeveer 800 tot 1500 jaar geleden—een periode toen deze regio druk bewoond werd. De archaeologische bevindingen bevestigden wat lidar had gesuggereerd: hier had ooit een grote, geavanceerde stad gestaan.\n\nGeschatte bevolkingscijfers suggereren dat dit metropool tussen de 30.000 en 50.000 inwoners kon hebben gehad op zijn hoogtepunt. Dit zou het vergelijkbaar maken met grote Europese steden uit dezelfde periode.\n\n## Implicaties voor ons Begrip van Pre-Colombiaans Amerika\n\nDeze ontdekking verandert fundamenteel wat we weten over pre-Colombiaanse beschavingen in het Amazonegebied. Lang werd aangenomen dat het Amazoneregenwoud slechts door kleine, nomadische groepen werd bewoond. De ontdekking van deze stad ondermijnt dat beeld: het bewijst dat complexe, sedentaire beschavingen in het Amazonegebied floreerden.\n\nDe stad toont bewijs van geavanceerde waterbeheersing. Systemen van kanalen en reservoirs suggereren dat de bevolking in staat was water te reguleren—cruciaal in een gebied waar zware regenval en overstromingen voorkomen. Dit was een technologie die groeiende bevolkingen nodig hadden om stedelijke gebieden vol te houden.\n\nArcheologen vinden ook bewijs van landbouwtechnieken. De gestructureerde plantagegebieden wijzen op een bevolking die systematische landbouw bedreven—waarschijnlijk maïs, cassave en andere gewassen. Dit was geen voedselproductie op kleinere schaal, maar grootschalige voedselproductie ter ondersteuning van een dicht bevolkte stad.\n\n## De Rol van LIDAR in Toekomstig Onderzoek\n\nDeze ontdekking is slechts het begin. Archeologen gebruiken nu lidar in andere onderbevolkte regionen van Amazonie, en al vele andere sites worden ontdekt. De technologie opent poorten naar een volledig verborgen archeologie die onder het regenwoud verborgen lag.\n\nHet is echter belangrijk op te merken dat deze archeologie niet alleen academisch relevant is. Het heeft rechtstreekse gevolgen voor de Inheemse volkeren die vandaag de dag in deze gebieden leven. Deze ontdekkingen tonen aan dat hun voorgangers geavanceerde beschavingen hebben opgebouwd—kennis die hun erfenis en identiteit verrijkt.\n\nBovendien hebben deze ontdekkingen milieu-implicaties. Het feit dat grote bevolkingen voorheen in het Amazonegebied woonden zonder het ecosysteem volledig te verwoesten, suggereert dat duurzaam beheer van deze regio's mogelijk is. Het zou waardevolle lessen kunnen bieden voor het hedendaagse beheer van het regenwoud.\n\n## Conclusie\n\nDe ontdekking van deze verloren stad is een herinnering aan de rijkheid van pre-Colombiaanse beschavingen en aan de kracht van moderne technologie in archeologie. Lidar heeft het mogelijk gemaakt wat eeuwen van traditioneel onderzoek niet kon bereiken: het onthullen van een verborgen wereld onder de groene mantel van het Amazoneregenwoud.",
            "vocabulary": [
                {"word": "ontdekken", "definition": "Voor het eerst vinden; bloot leggen; aan het licht brengen"},
                {"word": "verborgen", "definition": "Uit het zicht; verscholen; niet zichtbaar"},
                {"word": "gefantaseerd", "definition": "Gedroomd; zich iets voorgesteld; gefantaseerd"},
                {"word": "voorgoed", "definition": "Voor altijd; definitief; permanent"},
                {"word": "terugkaatst", "definition": "Terugkaatst; weerkaatst; terugspringt"},
                {"word": "dringen", "definition": "Doordringen; binnenkomen; door iets heen gaan"},
                {"word": "verbijsterend", "definition": "Zeer verrassend; verbazingwekkend; schokkend"},
                {"word": "ondermijnt", "definition": "Verzwakt; ondergraaft; doet afbreuk aan"}
            ]
        },
        "questions": [
            {
                "id": "q1",
                "type": "multiple_choice",
                "question": "Wat is het belangrijkste voordeel van lidar-technologie in archeologie?",
                "options": [
                    "A) Het kan veel sneller kaarten maken dan satellietfoto's",
                    "B) Het kan door de bladerdak van het regenwoud dringen en zien wat onder de bomen verborgen ligt",
                    "C) Het is veel goedkoper dan andere onderzoeksmethoden",
                    "D) Het kan alleen in regenwouden gebruikt worden"
                ],
                "correct_answer": "B",
                "explanation": "De tekst benadrukt dat lidar door de bladerdak van het regenwoud kan dringen en kan 'zien' wat onder de bomen verborgen ligt—wat traditionele fotografie niet kan."
            },
            {
                "id": "q2",
                "type": "multiple_choice",
                "question": "Wat voor structuren werden aangetroffen in de ontdekte stad?",
                "options": [
                    "A) Alleen woonhuizen",
                    "B) Primitieve hutten en grotten",
                    "C) Rechthoekige platforms, waterleidingen en gestructureerde plantagegebieden",
                    "D) Alleen religieuze tempels"
                ],
                "correct_answer": "C",
                "explanation": "De tekst stelt dat lidar rechthoekige platforms, waterleidingen en gestructureerde plantagegebieden identificeerde, wat bewijzen van geavanceerde stedelijke planning."
            },
            {
                "id": "q3",
                "type": "open",
                "question": "Hoe hebben onderzoekers het lidar-onderzoek geverifieerd? Wat voor bewijs vonden zij ter plekke?",
                "expected_points": [
                    "Naar de locatie gegaan voor fysiek onderzoek",
                    "Artefacten verzameld en gedateerd (800-1500 jaar geleden)",
                    "Artefacten bevestigden lidar-voorspellingen",
                    "Bewijs van grote, geavanceerde stad"
                ],
                "model_answer": "Na analyse van de lidar-gegevens ging een onderzoekersteam ter plekke om fysieke bewijs te verzamelen. Zij vonden artefacten die werden gedateerd op ongeveer 800 tot 1500 jaar geleden. Deze archaeologische bevindingen bevestigden wat lidar had gesuggereerd: hier had ooit een grote, geavanceerde stad gestaan."
            },
            {
                "id": "q4",
                "type": "open",
                "question": "Beschrijf de waterbeheersingssystemen die in deze stad werden gevonden. Waarom waren deze systemen belangrijk?",
                "expected_points": [
                    "Kanalen en reservoirs werden gevonden",
                    "Systemen reguleren water",
                    "Belangrijk in gebied met zware regenval en overstromingen",
                    "Cruciaal voor stedelijke bevolking"
                ],
                "model_answer": "De stad toonde bewijs van geavanceerde waterbeheersing met systemen van kanalen en reservoirs. Deze systemen stelden de bevolking in staat water te reguleren—wat cruciaal was in een gebied waar zware regenval en overstromingen voorkomen. Dit was de technologie die groeiende bevolkingen nodig hadden om stedelijke gebieden vol te houden."
            },
            {
                "id": "q5",
                "type": "open",
                "question": "Hoe verandert deze ontdekking ons begrip van pre-Colombiaanse beschavingen in het Amazonegebied?",
                "expected_points": [
                    "Oude aanname: alleen kleine, nomadische groepen",
                    "Nieuwe ontdekking: complexe, sedentaire beschavingen",
                    "Bewijs van geavanceerde waterbeheersing",
                    "Bewijs van grootschalige landbouw",
                    "Stad had 30.000-50.000 inwoners"
                ],
                "model_answer": "Lang werd aangenomen dat het Amazoneregenwoud slechts door kleine, nomadische groepen werd bewoond. Deze ontdekking ondermijnt dat beeld volledig door te bewijzen dat complexe, sedentaire beschavingen in het Amazonegebied floreerden. De stad had waarschijnlijk tussen de 30.000 en 50.000 inwoners op zijn hoogtepunt—vergelijkbaar met grote Europese steden uit dezelfde periode."
            },
            {
                "id": "q6",
                "type": "multiple_choice",
                "question": "Wat suggereren de geavanceerde waterbeheersingssystemen over de kennis van de bewoners?",
                "options": [
                    "A) Zij waren primitief en begeleidden geen geavanceerde technologie",
                    "B) Zij hadden alleen basale irrigatiekennis",
                    "C) Zij waren zeer geavanceerd en begrepen watercyclus en infrastructuur",
                    "D) Zij leenden technologie van Europese kolonisten"
                ],
                "correct_answer": "C",
                "explanation": "De geavanceerde systemen van kanalen en reservoirs tonen aan dat de bewoners zeer geavanceerde kennis hadden van waterbeheer en infrastructuur, wat nodig was ter ondersteuning van een dicht bevolkte stad."
            },
            {
                "id": "q7",
                "type": "multiple_choice",
                "question": "Welke implicatie heeft deze ontdekking voor hedendaags regenwoudbeheer?",
                "options": [
                    "A) Het regenwoud moet volkomen onaangetast blijven",
                    "B) Het feit dat grote bevolkingen voorheen daar woonden zonder ecosysteem volledig te verwoesten, suggereert dat duurzaam beheer mogelijk is",
                    "C) Het bewijst dat regenwouden niet beschermd hoeven te worden",
                    "D) Het heeft geen relevantie voor hedendaags milieubeleid"
                ],
                "correct_answer": "B",
                "explanation": "De tekst stelt dat het feit dat grote bevolkingen voorheen in het Amazonegebied woonden zonder het ecosysteem volledig te verwoesten, suggereert dat duurzaam beheer van deze regio's mogelijk is en waardevolle lessen kan bieden voor hedendaags regenwoudbeheer."
            }
        ]
    }
]

def convert_difficulty(difficulty_str):
    """Преобразует строку difficulty в число 1-5"""
    if not difficulty_str:
        return 3
    difficulty_str = difficulty_str.upper()
    if "C1" in difficulty_str or "C2" in difficulty_str:
        return 5
    elif "B2" in difficulty_str:
        return 4
    elif "B1" in difficulty_str:
        return 3
    elif "A2" in difficulty_str:
        return 2
    elif "A1" in difficulty_str:
        return 1
    return 3  # По умолчанию

def parse_options(options_list):
    """Преобразует список строк options в словарь {"A": "...", "B": "...", ...}"""
    options_dict = {}
    for opt in options_list:
        # Ищем паттерн "A) текст", "B) текст" и т.д.
        if ") " in opt:
            key, value = opt.split(") ", 1)
            options_dict[key.strip()] = value.strip()
        else:
            # Если формат не стандартный, используем индекс
            idx = len(options_dict)
            key = chr(65 + idx)  # A, B, C, D...
            options_dict[key] = opt.strip()
    return options_dict

def seed_dutch_passages():
    """Загружает Dutch passages с вопросами"""
    
    with app.app_context():
        try:
            print("🌱 Начинаем загрузку Dutch passages...")
            print("=" * 80)
            
            existing_count = DutchPassage.query.count()
            print(f"📊 Текущее количество passages в БД: {existing_count}")
            
            loaded_count = 0
            updated_count = 0
            questions_loaded = 0
            
            for passage_data in PASSAGES_DATA:
                passage_info = passage_data["passage"]
                questions_data = passage_data["questions"]
                
                title = passage_info["title"]
                print(f"\n📖 Обрабатываем: {title}")
                
                # Проверяем, существует ли уже такой пассаж
                existing_passage = DutchPassage.query.filter_by(title=title).first()
                
                if existing_passage:
                    print(f"  ⚠️  Passage уже существует (ID: {existing_passage.id}), обновляем...")
                    passage = existing_passage
                    # Обновляем данные
                    passage.text = passage_info["content"]
                    passage.category = passage_info["category"]
                    passage.difficulty = convert_difficulty(passage_info["difficulty"])
                    passage.word_count = passage_info.get("word_count")
                    updated_count += 1
                else:
                    # Создаем новый пассаж
                    passage = DutchPassage(
                        title=title,
                        text=passage_info["content"],
                        category=passage_info["category"],
                        difficulty=convert_difficulty(passage_info["difficulty"]),
                        word_count=passage_info.get("word_count"),
                        image_url=None  # Можно добавить позже
                    )
                    db.session.add(passage)
                    loaded_count += 1
                
                db.session.flush()  # Получаем ID пассажа
                
                # Удаляем старые вопросы для этого пассажа (если обновляем)
                if existing_passage:
                    DutchQuestion.query.filter_by(passage_id=passage.id).delete()
                
                # Добавляем вопросы
                for idx, q_data in enumerate(questions_data, 1):
                    question = DutchQuestion(
                        passage_id=passage.id,
                        question_number=idx,
                        question_type=q_data["type"],
                        question_text=q_data["question"],
                        correct_answer=q_data.get("correct_answer") or q_data.get("model_answer", ""),
                        explanation=q_data.get("explanation", "")
                    )
                    
                    # Обрабатываем options для multiple_choice
                    if q_data["type"] == "multiple_choice" and "options" in q_data:
                        options_dict = parse_options(q_data["options"])
                        question.set_options(options_dict)
                    
                    db.session.add(question)
                    questions_loaded += 1
                
                print(f"  ✅ Добавлено/обновлено: {len(questions_data)} вопросов")
            
            # Сохраняем все изменения
            db.session.commit()
            
            print("\n" + "=" * 80)
            print(f"✅ Успешно загружено {loaded_count} новых passages!")
            print(f"🔄 Обновлено {updated_count} существующих passages")
            print(f"📝 Всего вопросов загружено: {questions_loaded}")
            print(f"📊 Всего passages в БД: {DutchPassage.query.count()}")
            print("=" * 80)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Ошибка при загрузке: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    seed_dutch_passages()

