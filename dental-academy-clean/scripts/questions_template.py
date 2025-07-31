#!/usr/bin/env python3
"""
Шаблон для загрузки 160 вопросов из IRT vragen.docx
Скопируйте ваши вопросы в этот файл и запустите
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, QuestionCategory, IRTParameters, BIGDomain
import json

def load_questions_from_template():
    """Загружает вопросы из шаблона"""
    
    print("📝 ЗАГРУЗКА ВОПРОСОВ ИЗ ШАБЛОНА")
    print("=" * 40)
    
    with app.app_context():
        # Получаем категории
        categories = {cat.name: cat.id for cat in QuestionCategory.query.all()}
        print(f"📂 Найдено категорий: {len(categories)}")
        
        # Получаем домены
        domains = {}
        for domain in BIGDomain.query.all():
            domains[domain.code] = domain.id
            domains[domain.name] = domain.id
        print(f"🏷️ Найдено доменов: {len(domains)}")
        
        # ЗАМЕНИТЕ ЭТО НА ВАШИ 80 ВОПРОСОВ
        questions_data = [
    {
        "id": 1,
        "text": "KLINISCHE CASUS: Een 38-jarige patiënt meldt zich met klachten van hevige, kloppende pijn in de linker onderkaak die begon na het eten van warme soep gisteren. De pijn wordt erger 's nachts en bij het liggen. Medische anamnese: hypertensie (ACE-remmer), geen allergieën. Tandheelkundige anamnese: laatste controle 3 jaar geleden. Bij onderzoek: element 36 heeft een diepe cariëslaesie distaal, percussie sterk pijnlijk, koudetest geeft langdurige pijn (>30 seconden), vitaliteitstest positief. Röntgenfoto toont diepe cariës die de pulpa benadert, geen apicale veranderingen zichtbaar.\nVRAAG: Wat is de meest geëigende behandeling voor deze patiënt?",
        "options": [
            "Cariësbehandeling met indirecte pulpaoverkapping",
            "Partiële pulpotomie met MTA",
            "Complete pulpectomie en wortelkanaalbehandeling",
            "Extractie en directe implantatie",
            "Antibioticabehandeling (amoxicilline) gedurende 7 dagen"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Complete pulpectomie en wortelkanaalbehandeling",
        "explanation": "De klinische symptomen (spontane, kloppende pijn die verergert 's nachts, langdurige reactie op koud >30 seconden) wijzen op irreversibele pulpitis. Bij een volwassen patiënt met irreversibele pulpitis is complete pulpectomie en wortelkanaalbehandeling de geïndiceerde behandeling. Indirecte pulpaoverkapping (A) is gecontra-indiceerd bij irreversibele pulpitis. Partiële pulpotomie (B) is voornamelijk geïndiceerd bij jonge patiënten met onvolledige wortelvorming. Extractie (D) is te radicaal voor een restoreerbare tand. Antibiotica (E) zijn niet geïndiceerd zonder systemische infectieverschijnselen.",
        "category": "Acuut pulpitis",
        "domain": "THER",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["endodontie", "pijn", "diagnostiek", "pulpitis", "behandeling"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 2,
        "text": "KLINISCHE CASUS: Een 52-jarige patiënte komt voor routine controle. Medische anamnese: diabetes mellitus type 2 (HbA1c 6.8%), osteoporose (alendronaat). Bij inspectie: element 14 vertoont een diepe cariëslaesie palatinaal. Koudtest: kort pijnlijk, warm: geen reactie, percussie: niet pijnlijk. Bitewing röntgenfoto toont diepe cariës die mogelijk de pulpa raakt. Patiënte heeft geen spontane pijn of gevoeligheidsklachten.\nVRAAG: Wat is de beste behandelstrategie voor element 14?",
        "options": [
            "Directe pulpaoverkapping met calciumhydroxide",
            "Stepwise excavation in twee sessies",
            "Complete cariësexcavatie en indirecte pulpaoverkapping met MTA",
            "Profylactische wortelkanaalbehandeling",
            "Observatie en fluoridebehandeling"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Complete cariësexcavatie en indirecte pulpaoverkapping met MTA",
        "explanation": "Bij diepe cariës zonder tekenen van irreversibele pulpitis (normale vitaliteitstests, geen spontane pijn) is complete excavatie met indirecte pulpaoverkapping de standaardbehandeling. MTA heeft superieure eigenschappen boven calciumhydroxide bij diepe cariës. Directe pulpaoverkapping (A) is alleen geïndiceerd bij mechanische pulpa-expositie. Stepwise excavation (B) is minder voorspelbaar en vereist meerdere sessies. Profylactische endodontie (D) is te radicaal. Observatie (E) is inadequaat bij diepe cariës.",
        "category": "Diepe cariës behandeling",
        "domain": "THER",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["cariës", "restauratief", "behandeling", "MTA", "pulpa"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 3,
        "text": "KLINISCHE CASUS: Een 29-jarige patiënt belt 2 dagen na voltooiing van wortelkanaalbehandeling element 46. Klachten: toenemende pijn en zwelling submandibulair links, koorts 38.2°C, gevoel van \"hoog staan\" van de tand. Medische anamnese: gezond, geen medicatie. De behandeling verliep zonder complicaties, kanalen werden geïnstrumenteerd tot werklengte, goed gespoeld met NaOCl, tijdelijke vulling geplaatst.\nVRAAG: Wat is de meest waarschijnlijke oorzaak en eerste behandelstap?",
        "options": [
            "Overvulling met sealer - observatie en pijnstilling",
            "Acute apicale periodontitis - incisie en drainage, antibiotica",
            "Instrumentfractuur - verwijzing naar endodontist",
            "Perforatie wortels - reparatie met MTA",
            "Allergische reactie op NaOCl - antihistaminica en corticosteroïden"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Acute apicale periodontitis - incisie en drainage, antibiotica",
        "explanation": "De klinische symptomen (toenemende pijn, zwelling, koorts, gevoel van \"hoog staan\") 2 dagen post-endodontische behandeling wijzen op acute apicale periodontitis/abces. Dit kan optreden door bacteriële reactivatie na instrumentatie. Behandeling: incisie en drainage van de zwelling, antibiotica (amoxicilline 500mg 3x/dag), en mogelijk heropening van het kanaal voor drainage. De andere opties passen niet bij het klinische beeld en de tijdslijn.",
        "category": "Postoperatieve complicaties",
        "domain": "THER",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.2,
            "discrimination": 2.0,
            "guessing": 0.16
        },
        "image_url": null,
        "tags": ["endodontie", "complicaties", "pijn", "zwelling", "abces"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 4,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt wil element 21 laten herstellen na trauma 6 maanden geleden. Wortelkanaalbehandeling is succesvol afgerond. Klinisch onderzoek: groot kroondefect incisaal en labiaal, palatinale wand intact, geen gingivale ontsteking. Patiënt vraagt naar een \"natuurlijk ogende\" oplossing en heeft budget voor kwaliteitsbehandeling. Occlusie: lichte overbeet, geen bruxisme.\nVRAAG: Wat is de optimale restauratieve oplossing voor dit element?",
        "options": [
            "Directe composietreconstructie met ribbond versterking",
            "Endokroon in volkeramiek (lithium disilicaat)",
            "Post-en-kroon constructie met metaalvrije kroon",
            "Porseleinen facing na wortelverlenging",
            "Extractie en implantaat-gedragen kroon"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Endokroon in volkeramiek (lithium disilicaat)",
        "explanation": "Een endokroon is de optimale oplossing voor endodontisch behandelde tanden met groot kroondefect maar intacte palatinale wand. Voordelen: behoud van tandstructuur (geen stift nodig), uitstekende esthetiek met lithium disilicaat, voorspelbare lange termijn resultaten. Directe composiet (A) is minder duurzaam bij groot defect. Post-en-kroon (C) verwijdert onnodige tandstructuur. Facing (D) is ongeschikt na wortelkanaalbehandeling bij groot defect. Extractie (E) is te radicaal voor een restoreerbare tand.",
        "category": "Materiaalkeuze",
        "domain": "THER",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.7,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["restauratief", "endodontie", "esthetiek", "kronen"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 5,
        "text": "KLINISCHE CASUS: Een 35-jarige patiënt met droge mond (xerostomie) door medicatie (antidepressiva, antihistaminica) ontwikkelt frequent nieuwe cariëslaesies. Laatste 6 maanden: 4 nieuwe caviteiten. Voeding: regelmatig frisdrank en energie-drankjes voor het werk. Mondhygiëne: 2x daags tandenpoetsen, geen interdentale reiniging. Fluoride: standaard tandpasta (1450 ppm).\nVRAAG: Welk preventief protocol is het meest effectief voor deze hoogrisicopatiënt?",
        "options": [
            "Verhogen poetsfrequentie naar 3x daags met elektrische tandenborstel",
            "Fluoridetherapie: 5000 ppm tandpasta + wekelijkse fluoride spoeling",
            "Professionele fluoride applicatie iedere 3 maanden",
            "Chloorhexidine mondspoeling 0.12% gedurende 2 weken per maand",
            "Xylitol kauwgom 4x daags en suikervrije mondgel"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Fluoridetherapie: 5000 ppm tandpasta + wekelijkse fluoride spoeling",
        "explanation": "Bij hoogrisico cariëspatiënten met xerostomie is intensieve fluoridetherapie de meest effectieve benadering. Hooggeconcentreerde fluoridetandpasta (5000 ppm) + wekelijkse spoeling geeft optimale fluoride-beschikbaarheid. Studies tonen 30-50% cariësreductie. Verhoogde poetsfrequentie (A) alleen is onvoldoende. Professionele applicaties (C) zijn minder frequent dan dagelijkse blootstelling. Chloorhexidine (D) heeft beperkte lange-termijn effectiviteit. Xylitol (E) is aanvullend maar minder effectief dan fluoride.",
        "category": "Cariëspreventie",
        "domain": "THER",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.5,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["preventie", "cariës", "fluoride", "xerostomie", "risicopatiënt"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 6,
        "text": "KLINISCHE CASUS: Een 16-jarige sporter valt tijdens voetbal en fractureert element 11. Trauma 45 minuten geleden. Klinisch: kroonfractuur met blootliggende pulpa (2mm diameter), bloeding uit pulpa, matige pijn bij aanraking. Radiologisch: geen wortelfractuur, geen dislocatie, wortelontwikkeling voltooid. Tandenfragment niet teruggevonden. Tetanusvaccinatie is up-to-date.\nVRAAG: Wat is de optimale acute behandeling?",
        "options": [
            "Directe pulpaoverkapping met MTA en definitieve composietreconstructie",
            "Partiële pulpotomie tot gezond pulpaweefsel en MTA afdekking",
            "Complete pulpectomie en directe wortelkanaalbehandeling",
            "Extractie en bewaren alveool voor latere implantatie",
            "Tijdelijke afdekking en behandeling uitstellen tot 48 uur"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Partiële pulpotomie tot gezond pulpaweefsel en MTA afdekking",
        "explanation": "Bij gecompliceerde kroonfractuur binnen 24 uur bij jonge patiënt met voltooid gevormde wortel is partiële pulpotomie de behandeling van keuze. Dit behoudt pulpavitaliteit en vermijdt endodontische behandeling op jonge leeftijd. MTA heeft uitstekende biocompatibiliteit. Directe overkapping (A) heeft lager succespercentage bij grote expositie. Complete pulpectomie (C) is te radicaal voor vitale pulpa. Extractie (D) is veel te radicaal. Uitstel (E) vermindert successpercentage significant.",
        "category": "Gecompliceerde kroonfractuur",
        "domain": "THER",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 2.2,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["traumatologie", "pulpatherapie", "MTA", "acute zorg", "fractuur"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 7,
        "text": "KLINISCHE CASUS: Een 42-jarige patiënt heeft persisterende klachten 8 maanden na wortelkanaalbehandeling element 15. Klachten: milde drukpijn bij kauwen, soms opgezwollen gevoel. Klinisch: element heeft kroon, geen zwelling zichtbaar, percussie licht gevoelig. Röntgenfoto toont adequate vulling tot apex, maar periapicale transparantie 4x5mm die niet kleiner werd sinds controle 6 maanden geleden.\nVRAAG: Wat is de meest geëigende vervolgbehandeling?",
        "options": [
            "Observatie met controle over 6 maanden",
            "Niet-chirurgische endodontische herbehandeling",
            "Apexresectie met retrograde vulling",
            "Extractie en implantaat plaatsing",
            "Antibioticakuur amoxicilline/clavulaanzuur"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Niet-chirurgische endodontische herbehandeling",
        "explanation": "Persisterende periapicale laesie na adequate wortelkanaalbehandeling met symptomen duidt op mislukte primaire behandeling. Niet-chirurgische herbehandeling is de eerste keuze met 85% succespercentage. Observatie (A) is inadequaat bij symptomen. Chirurgie (C) is tweede keuze na gefaalde herbehandeling. Extractie (D) is te radicaal als eerste optie. Antibiotica (E) zijn niet geïndiceerd bij chronische asymptomatische apicale parodontitis.",
        "category": "Retreatment indicaties",
        "domain": "THER",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.9,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["endodontie", "herbehandeling", "complicaties", "periapicaal"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 8,
        "text": "KLINISCHE CASUS: Een 28-jarige patiënte wil element 12 laten restaureren na fractuur van oude composietvulling. Defect: incisaal 1/3 van kroon, geen dentine-expositie, labiaal glazuur geëtst door maagzuur (reflux). Patiënte heeft hoge esthetische verwachtingen. Behandeling gepland onder cofferdam isolatie.\nVRAAG: Welk adhesief protocol geeft de meest voorspelbare en duurzame hechting?",
        "options": [
            "Total-etch met fosforzuur 37% + twee-stap adhesief systeem",
            "Self-etch adhesief systeem + immediate dentin sealing",
            "Universal adhesief in self-etch mode + selective enamel etching",
            "Glazuur sandblasting + silaan + ongevulde hars",
            "Polyacrylzuur conditioner + glasionomeer basis"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Universal adhesief in self-etch mode + selective enamel etching",
        "explanation": "Voor gefractureerd glazuur gecombineerd met geëtst glazuur door zuur is universeel adhesief met selectieve glazuuretsing optimaal. Fosforzuurets op glazuur gevolgd door self-etch op dentine combineert optimale glazuurhechting met voorzichtige dentinebehandeling. Total-etch (A) kan overetsen bij gecompromitteerd glazuur. Zuiver self-etch (B) geeft suboptimale glazuurhechting. Sandblasting (D) is te agressief. Glasionomeer (E) heeft inadequate esthetiek.",
        "category": "Adhesie",
        "domain": "THER",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.8,
            "guessing": 0.23
        },
        "image_url": null,
        "tags": ["restauratief", "adhesie", "materialen", "glazuur", "esthetiek"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 9,
        "text": "KLINISCHE CASUS: Bij een 25-jarige patiënt wordt tijdens controle een cavitatie ontdekt in element 26 occlusaal. Cariësdetector toont gedemineraliseerd dentine. Laesie: 2mm diep, 3mm diameter. Bitewing toont radiolucente zone in buitenste dentine. Vitaliteitstest normaal, geen symptomen. Patiënt vraagt naar tandstructuur-sparende behandeling.\nVRAAG: Welke minimaal invasieve benadering is het meest geschikt?",
        "options": [
            "Traditionele caviteitspreparatie en amalgaamvulling",
            "Tunnel preparatie en glasionomeer restauratie",
            "Selectieve cariësexcavatie en directe composietvulling",
            "Ozontherapie en fluoride remineralisatie",
            "Cariostatische behandeling met zilverdiamine fluoride"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Selectieve cariësexcavatie en directe composietvulling",
        "explanation": "Selectieve cariësexcavatie behoudt maximaal gezonde tandstructuur door alleen geïnfecteerde dentine te verwijderen en geaffecteerde (remineraliseerbare) dentine te behouden. Dit gecombineerd met moderne adhesieve composietvulling geeft optimale resultaten. Traditionele preparatie (A) verwijdert onnodige tandstructuur. Tunnel preparatie (B) heeft een hoog faalpercentage. Ozon (D) is experimenteel zonder bewezen lange-termijn resultaten. SDF (E) is voor remming, niet definitieve restauratie.",
        "category": "Minimaal invasieve tandheelkunde",
        "domain": "THER",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["cariës", "minimaal invasief", "restauratief", "diagnostiek"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },
    {
        "id": 10,
        "text": "KLINISCHE CASUS: Een 55-jarige patiënt met diabetes type 2 (HbA1c 8.1%) presenteert zich met chronisch apicaal abces element 37. Eerste behandelsessie: mechanische preparatie tot apex, ruime irrigatie met NaOCl 2.5%. Symptomen persisteren na 1 week. Tweede sessie gepland voor medicamenteuze behandeling en vulling.\nVRAAG: Welk intracanaal medicament is het meest effectief voor deze situatie?",
        "options": [
            "Calciumhydroxide pasta voor 2 weken",
            "Chloorhexidine gel 2% voor 1 week",
            "Triple antibiotic paste (TAP) voor 4 weken",
            "Ledermix (corticosteroïd/antibioticum) voor 5 dagen",
            "Formocresol verdund 1:5 voor 1 week"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Calciumhydroxide pasta voor 2 weken",
        "explanation": "Calciumhydroxide blijft de gouden standaard voor intracanaal medicatie bij persisterende infectie. Alkalische pH (12.5) heeft een breed antimicrobieel spectrum en stimuleert reparatieve processen. Bij diabetische patiënten is adequate desinfectie cruciaal. CHX gel (B) heeft een kortere werkingsduur. TAP (C) kan resistentie veroorzaken. Ledermix (D) is voor symptoombestrijding, niet desinfectie. Formocresol (E) is toxisch en verouderd.",
        "category": "Medicamenteuze wortelkanaaldesinfectie",
        "domain": "THER",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.4,
            "discrimination": 1.4,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["endodontie", "medicatie", "infectie", "desinfectie", "abces"],
        "created_at": "2025-07-21T16:00:23Z",
        "updated_at": "2025-07-21T16:00:23Z"
    },{
        "id": 11,
        "text": "KLINISCHE CASUS: Een 68-jarige patiënt met atriumfibrilleren gebruikt apixaban (Eliquis) 5mg 2x daags. Element 16 moet worden geëxtraheerd wegens uitgebreide cariës en pijn. INR is niet bepaald (niet van toepassing bij DOAC). Laatste cardiale controle 3 maanden geleden was goed. Cardiologische contra-indicatie voor stoppen anticoagulatie. Geplande extractie is relatief eenvoudig (mobiele kroon, goede toegankelijkheid).\nVRAAG: Wat is het meest veilige perioperatieve anticoagulatie management?",
        "options": [
            "Apixaban stoppen 48 uur voor ingreep, hervatten na 24 uur",
            "Doorbehandelen op apixaban, lokale hemostase maatregelen",
            "Switchen naar heparine bridge therapy 5 dagen pre-operatief",
            "Apixaban reduceren naar 2.5mg 1x daags gedurende 1 week",
            "Extractie uitstellen en conservatieve behandeling proberen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Doorbehandelen op apixaban, lokale hemostase maatregelen",
        [cite_start]"explanation": "Bij patiënten op DOAC's (Direct Oral Anticoagulants) kan eenvoudige extractie veilig worden uitgevoerd zonder stoppen van medicatie, mits adequate lokale hemostase (tranexaminezuur, gelfoam, hechting)[cite: 178]. [cite_start]Moderne evidence toont geen verhoogd bloedingsrisico bij eenvoudige extracties[cite: 179]. [cite_start]Stoppen DOAC (A) verhoogt trombose-risico onnodig[cite: 179]. [cite_start]Bridge therapy (C) is gecompliceerd en niet nodig[cite: 180]. [cite_start]Dosisreductie (D) is niet evidence-based[cite: 180]. [cite_start]Uitstellen (E) lost het probleem niet op[cite: 180].",
        "category": "Extractie - Anticoagulantia",
        "domain": "SURG",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.3,
            "discrimination": 2.1,
            "guessing": 0.16
        },
        "image_url": null,
        "tags": ["extractie", "chirurgie", "anticoagulantia", "farmacologie", "hemostase"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 12,
        "text": "KLINISCHE CASUS: Een 32-jarige niet-roker presenteert zich met gefractureerd element 21 tot gingivaal niveau na fietsongeval. Wortel heeft verticale fractuur. Omliggende elementen zijn intact. Röntgenonderzoek: adequate botdimensies, geen apicale pathologie. Patiënt wenst snelle esthetische oplossing en heeft budget voor implantaatbehandeling.\nVRAAG: Welke implantatie timing is het meest geïndiceerd?",
        "options": [
            "Onmiddellijke implantatie met directe temporisering",
            "Early implantatie na 6-8 weken genezing",
            "Late implantatie na 3-4 maanden genezing",
            "Delayed implantatie na guided bone regeneration",
            "Socket preservation en implantatie na 6 maanden"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Early implantatie na 6-8 weken genezing",
        [cite_start]"explanation": "Bij gefractureerde voortand met intacte gingivale architectuur en adequate bot is early implantatie (6-8 weken) optimaal[cite: 191]. [cite_start]Dit geeft betere botgenezing dan immediate, maar behoudt zachte weefselen beter dan late implantatie[cite: 192]. [cite_start]Immediate (A) heeft hoger faalrisico bij fracturen[cite: 193]. [cite_start]Late implantatie (C) riskeert weefselcollaps[cite: 193]. [cite_start]GBR (D) is niet nodig bij adequate bot[cite: 193]. [cite_start]Socket preservation (E) is conservatiever maar langer durend[cite: 194].",
        "category": "Implantologie - Onmiddellijke implantatie",
        "domain": "SURG",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["implantologie", "chirurgie", "trauma", "esthetiek", "bot"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 13,
        "text": "KLINISCHE CASUS: Tijdens extractie van element 48 (geïmpacteerd horizontaal) treedt plots hevig bloeden op uit de alveolaire ruimte. Na controle van de extractieruimte wordt een kleine perforatie van de linguale cortex waargenomen. Patiënt rapporteert onmiddellijk volledig verlies van gevoeligheid in lip en kin rechts. Bloeding is onder controle gebracht.\nVRAAG: Wat is de meest geëigende directe behandeling van deze situatie?",
        "options": [
            "Vitamine B-complex injectie intramusculair onmiddellijk",
            "Corticosteroïden (prednisolon 1mg/kg) binnen 8 uur starten",
            "Chirurgische exploratie en eventuele zenuwreparatie direct",
            "Observatie en afwachten spontane recuperatie 6 maanden",
            "Verwijzing naar kaakchirurg binnen 72 uur"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Corticosteroïden (prednisolon 1mg/kg) binnen 8 uur starten",
        [cite_start]"explanation": "Acute nervus alveolaris inferior letsel tijdens extractie vereist onmiddellijke corticosteroïd therapie om oedeem en inflammatie te reduceren[cite: 206]. [cite_start]Prednisolon 1mg/kg binnen 8 uur geeft beste neurologische herstelkansen[cite: 207]. [cite_start]Vitamine B (A) is lange termijn ondersteuning, niet acute behandeling[cite: 207]. [cite_start]Directe chirurgie (C) is te agressief[cite: 208]. [cite_start]Observatie (D) mist het kritieke behandelvenster[cite: 208]. [cite_start]Verwijzing (E) moet wel, maar eerst medicamenteuze behandeling starten[cite: 208].",
        "category": "Chirurgische complicaties - Nervus alveolaris inferior",
        "domain": "SURG",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.4,
            "discrimination": 2.3,
            "guessing": 0.15
        },
        "image_url": null,
        "tags": ["chirurgie", "complicaties", "zenuwletsel", "noodsituatie", "corticosteroïden"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 14,
        "text": "KLINISCHE CASUS: Een 58-jarige edentate patiënt krijgt nieuwe volledige prothesen. Proefplaatsing toont interferentie van protheserand met vergrote tuber maxillae bilateraal. Tubers zijn 8mm prominent en veroorzaken drukpijn. Geen acute inflammatie. Patiënt heeft goede algemene gezondheid, gebruikt alleen hypertensie medicatie.\nVRAAG: Welke chirurgische benadering is het meest geschikt?",
        "options": [
            "Tuberplastiek met roterende instrumenten onder lokale anesthesie",
            "Laser excisie van overtollig weefsel",
            "Elektrocauter reductie van prominente gebieden",
            "Uitstellen chirurgie en prothese-aanpassing proberen",
            "Tuberectomie met verwijdering van complete tuber"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Tuberplastiek met roterende instrumenten onder lokale anesthesie",
        [cite_start]"explanation": "Tuberplastiek met roterende instrumenten (boren, frezen) onder lokale anesthesie is de standaard behandeling voor hyperplastische tubera die prothetische retentie belemmeren[cite: 219]. [cite_start]Gecontroleerde reductie met goede visualisatie[cite: 220]. [cite_start]Laser (B) heeft slechtere hemostase bij botwerk[cite: 220]. [cite_start]Elektrocauter (C) veroorzaakt thermische schade[cite: 220]. [cite_start]Prothetische aanpassing (D) compromitteert retentie[cite: 221]. [cite_start]Complete tuberectomie (E) is te radicaal en beschadigt retentieve zones[cite: 221].",
        "category": "Preprothetische chirurgie - Tuberplastiek",
        "domain": "SURG",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.5,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["chirurgie", "prothese", "preprothetisch", "tuberplastiek", "bot"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 15,
        "text": "KLINISCHE CASUS: Na inferieure alveolaris blok anesthesie voor extractie element 47 ontwikkelt een 45-jarige patiënt binnen 5 minuten: trismus (mondopening <20mm), dysfagie, en spraakstoornissen. Geen tekenen van allergische reactie. Vitale functies stabiel. Anesthesie was technisch moeilijk door beperkte mondopening.\nVRAAG: Wat is de meest waarschijnlijke diagnose en behandeling?",
        "options": [
            "Allergische reactie - adrenaline en corticosteroïden",
            "Hematoom in pterygomandibulaire ruimte - conservatieve behandeling",
            "Intravasculaire injectie - symptomatische ondersteuning",
            "Temporomandibulaire gewrichtsluxatie - reductiemanoeuvre",
            "Mediale pterygoideus spasme - spierrelaxatie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Hematoom in pterygomandibulaire ruimte - conservatieve behandeling",
        [cite_start]"explanation": "Combinatie van trismus, dysfagie en spraakstoornissen na technisch moeilijke IAB wijst op een hematoom in de pterygomandibulaire ruimte door bloedvatletsel[cite: 232]. Behandeling: conservatief met ijs, pijnstilling, zachte voeding, antibiotische profylaxe. [cite_start]Symptomen verbeteren geleidelijk over 7-14 dagen[cite: 233]. [cite_start]Allergische reactie (A) zou systemische symptomen geven[cite: 234]. [cite_start]Intravasculaire injectie (C) geeft andere symptomen[cite: 234]. [cite_start]TMJ luxatie (D) zou andere bevindingen geven[cite: 234].",
        "category": "Anesthesie - Lokale complicaties",
        "domain": "SURG",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 2.0,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["anesthesie", "complicaties", "hematoom", "trismus", "extractie"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 16,
        "text": "KLINISCHE CASUS: Een 38-jarige niet-roker heeft een geïsoleerd intrabony defect (8mm probing depth, 5mm attachment loss) aan element 14 mesiaal. Röntgenfoto toont 6mm verticaal botverlies. Initiële parodontale therapie resulteerde in verbetering van 8mm naar 6mm probing depth. Goede mondhygiëne, geen andere parodontale problemen.\nVRAAG: Welke regeneratieve techniek biedt de beste vooruitzichten?",
        "options": [
            "Open flap debridement zonder additieven",
            "Guided tissue regeneration met resorbeerbaar membraan + botsubstituut",
            "Enamel matrix derivative (Emdogain) alleen",
            "Plaatjes-rijk plasma (PRP) applicatie",
            "Free gingival graft voor mucogingivale correctie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Guided tissue regeneration met resorbeerbaar membraan + botsubstituut",
        [cite_start]"explanation": "Voor diepe intrabony defecten is guided tissue regeneration (GTR) met combinatie van barrièremembraan en botsubstituut de gouden standaard[cite: 246]. [cite_start]Gecontroleerde studies tonen superieure attachment gain versus open flap alleen[cite: 247]. [cite_start]EMD (C) is effectief maar minder dan GTR combinatie[cite: 247]. [cite_start]PRP (D) heeft beperkte evidence[cite: 248]. [cite_start]Free graft (E) adresseert niet het intrabony defect[cite: 248]. [cite_start]OFD alleen (A) geeft minimale regeneratie[cite: 248].",
        "category": "Parodontale chirurgie - Regeneratieve behandeling",
        "domain": "SURG",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["parodontologie", "chirurgie", "regeneratie", "bottransplantatie", "GTR"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 17,
        "text": "KLINISCHE CASUS: Een 55-jarige roker (30 pack-years) presenteert een asymmetrische, ulceratieve laesie van 12mm op de laterale tongrand rechts. Laesie bestaat 6 weken, is indolent en vertoont verheven, geïndureerde randen. Geen systemische symptomen. Cervicale lymfeklieren zijn niet palpabel vergroot.\nVRAAG: Welke diagnostische benadering is het meest geïndiceerd?",
        "options": [
            "Cytologisch uitstrijkje en 2 weken observatie",
            "Topicale corticosteroïden gedurende 10 dagen trial",
            "Incisiebiopsie van representatief gebied onmiddellijk",
            "Brush biopsie voor moleculaire analyse",
            "Verwijzing naar specialist en afwachten"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Incisiebiopsie van representatief gebied onmiddellijk",
        [cite_start]"explanation": "Asymmetrische, indurerende ulceratie bij een roker >2 weken is maligne-suspect en vereist onmiddellijke histopathologische diagnose[cite: 259]. [cite_start]Incisiebiopsie geeft een definitieve diagnose met weinig morbiditeit[cite: 260]. [cite_start]Cytologie (A) is onvoldoende specifiek[cite: 260]. [cite_start]Corticosteroïden (B) kunnen maligniteit maskeren[cite: 260]. [cite_start]Brush biopsie (D) is een screeningstool, geen definitieve diagnose[cite: 261]. [cite_start]Verwijzing zonder biopsie (E) veroorzaakt onnodige vertraging[cite: 261].",
        "category": "Biopsie - Verdachte laesie",
        "domain": "SURG",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["diagnostiek", "oncologie", "biopsie", "mondkanker", "roken"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 18,
        "text": "KLINISCHE CASUS: Een 28-jarige vrouw belt 3 dagen na extractie element 38 met klachten van toenemende, uitstralende pijn naar oor en kaakhoek. Pijnstillers helpen nauwelijks. Bij controle: lege, droge alveolaire socket zonder bloedklonter, grijswitte debris zichtbaar, geen purulente drainage. Omliggende gingiva bedekt normaal.\nVRAAG: Wat is de meest effectieve behandeling voor deze conditie?",
        "options": [
            "Antibiotica (amoxicilline) en systemische pijnstilling",
            "Zacht irrigeren en lokale anesthesie pasta applicatie",
            "Curettage van socket en nieuwe bloedklonter stimuleren",
            "Alveoguard of soortgelijke protectieve dressing plaatsen",
            "Verwijzing naar orale chirurg voor verdere behandeling"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Alveoguard of soortgelijke protectieve dressing plaatsen",
        [cite_start]"explanation": "Droge socket (alveolitis sicca) wordt behandeld met beschermende vulling zoals Alveoguard die pijn vermindert en genezing bevordert[cite: 273]. [cite_start]Dit geeft onmiddellijke pijnverlichting[cite: 274]. [cite_start]Antibiotica (A) zijn niet geïndiceerd bij droge socket[cite: 274]. [cite_start]Irrigatie (B) alleen is onvoldoende[cite: 274]. [cite_start]Curettage (C) veroorzaakt extra trauma[cite: 275]. [cite_start]Verwijzing (E) is niet nodig voor standaard droge socket[cite: 275].",
        "category": "Postoperatieve zorg - Droge alveolaire socket",
        "domain": "SURG",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["extractie", "postoperatief", "pijn", "complicaties", "alveolitis"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 19,
        "text": "KLINISCHE CASUS: Een 19-jarige student heeft bilateraal geïmpacteerde derde molaren onderkaak (horizontale positie, gedeeltelijk in ramus). Geen acute klachten momenteel. Orthodontische behandeling is afgerond. Mondhygiëne is goed. Ouders vragen om advies over preventieve extractie wegens familie-anamnese van problemen met verstandskiezen.\nVRAAG: Wat is de meest evidence-based aanbeveling?",
        "options": [
            "Bilaterale extractie adviseren wegens impactie en familie-anamnese",
            "Jaarlijkse monitoring en alleen ingrijpen bij problemen",
            "Unilaterale extractie als test en evaluatie resultaat",
            "Orthodontische tractie proberen voor eruptiebegeleiding",
            "Coronectomie als compromis tussen extractie en observatie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Jaarlijkse monitoring en alleen ingrijpen bij problemen",
        [cite_start]"explanation": "Huidige evidence ondersteunt een conservatieve benadering voor asymptomatische geïmpacteerde derde molaren[cite: 286]. [cite_start]Profylactische extractie wordt niet meer aanbevolen vanwege morbiditeit versus beperkte voordelen[cite: 287]. [cite_start]NICE guidelines adviseren observatie met interventie alleen bij pathologie[cite: 287]. [cite_start]Familie-anamnese (A) is geen absolute indicatie[cite: 288]. [cite_start]Unilaterale test (C) is onnodig[cite: 288]. [cite_start]Tractie (D) slaagt niet bij horizontale impactie[cite: 288]. [cite_start]Coronectomie (E) is voor specifieke indicaties[cite: 289].",
        "category": "Impactie - Preventieve extractie",
        "domain": "SURG",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.23
        },
        "image_url": null,
        "tags": ["extractie", "impactie", "verstandskiezen", "preventie", "chirurgie"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },
    {
        "id": 20,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt met implantaat in regio 16 (3 jaar geleden geplaatst) presenteert zich met recidiverende zwelling en bloeding rond het implantaat. Probing depth 8mm met purulente exsudaat. Röntgenfoto toont 4mm kraakbeenverlies rond implantaat vergeleken met baseline. Implantaat is osteogeïntegreerd en functioneel stabiel.\nVRAAG: Welke behandelstrategie is het meest geschikt voor deze peri-implantitis?",
        "options": [
            "Systemische antibiotica en verbeterde mondhygiëne instructie alleen",
            "Niet-chirurgische debridement met chloorhexidine irrigatie",
            "Chirurgische toegang, debridement en guided bone regeneration",
            "Explantatie van implantaat en site preservatie voor reimplantatie",
            "Laser therapy (Er:YAG) en photodynamic therapy"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Chirurgische toegang, debridement en guided bone regeneration",
        [cite_start]"explanation": "Moderate peri-implantitis (>4mm botverlies, purulente exsudaat) vereist chirurgische behandeling[cite: 301]. [cite_start]Open debridement met implantaatoppervlak decontaminatie en GBR biedt de beste resultaten voor botregeneratie[cite: 302]. [cite_start]Conservatieve behandeling (A,B) is onvoldoende bij gevestigde peri-implantitis[cite: 302]. [cite_start]Explantatie (D) is te radicaal bij een stabiel implantaat[cite: 303]. [cite_start]Laser therapy (E) is adjunctief, niet als monotherapie[cite: 303].",
        "category": "Implantaat complicaties - Peri-implantitis",
        "domain": "SURG",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["implantaat", "complicaties", "peri-implantitis", "chirurgie", "botregeneratie"],
        "created_at": "2025-07-21T16:02:28Z",
        "updated_at": "2025-07-21T16:02:28Z"
    },{
        "id": 21,
        "text": "KLINISCHE CASUS: Een 72-jarige edentate patiënt draagt volledige prothesen sinds 8 jaar. Klachten: onderprothese heeft slechte retentie en beweegt bij spreken en kauwen. Bovenprothese functioneert adequaat. Onderkaak toont matige resorptie, adequate vestibulaire diepte. Patiënt kan financieel geen implantaten bekostigen via de zorgverzekering en wenst conventionele oplossing.\nVRAAG: Welke behandelstrategie biedt de beste verbetering van onderprothese retentie?",
        "options": [
            "Softliner applicatie en halfjaarlijkse vervanging",
            "Nieuwe onderprothese met uitgebreide grenzen en neutrale zone techniek",
            "Vestibuloplastiek voor verdieping van de vestibulaire omslagplooi",
            "Conventionele rebase van bestaande prothese",
            "Tijdelijke fixatief gebruik en acceptatie van beperkingen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Nieuwe onderprothese met uitgebreide grenzen en neutrale zone techniek",
        "explanation": "Bij matige botresorptie maar adequate anatomie is een nieuwe prothese met optimale border molding en neutrale zone techniek de meest effectieve oplossing. De neutrale zone balanceert spier- en tongkrachten voor betere stabiliteit. Softliner (A) is een tijdelijke oplossing. Vestibuloplastiek (C) heeft beperkte lange termijn resultaten. Rebase (D) corrigeert geen ontwerpfouten. Fixatief (E) is symptomatische behandeling.",
        "category": "Volledige prothesen - Retentie en stabilisatie",
        "domain": "PROTH",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.5,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["prothetiek", "volledige prothese", "retentie", "stabilisatie", "neutrale zone"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 22,
        "text": "KLINISCHE CASUS: Een 65-jarige patiënt met 2 implantaten in de onderkaak (regio 33, 43) krijgt een implantaat-gedragen overdenture. Bar-clip systeem is geplaatst. Na 2 maanden klaagt patiënt over drukpijn aan de bar en moeilijkheden met in- en uitnemen van de prothese. Klinisch: erytheem rond bar, prothese past strak.\nVRAAG: Wat is de meest waarschijnlijke oorzaak en oplossing?",
        "options": [
            "Infectie rond implantaten - antibiotica en chloorhexidine spoeling",
            "Te strakke retentie bar-clip - clip activatie verminderen",
            "Inadequate mondhygiëne - intensieve hygiëne instructie",
            "Overbelasting implantaten - occlusale aanpassing",
            "Weefsel hyperplasie - chirurgische correctie van weke delen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Te strakke retentie bar-clip - clip activatie verminderen",
        "explanation": "Combinatie van drukpijn, moeilijk in/uitnemen en erytheem wijst op overretentie van bar-clip systeem. Clip activatie moet worden verminderd voor comfort en voorkoming van overbelasting. Te strakke retentie leidt tot force concentration en tissue irritatie. Infectie (A) zou andere symptomen geven. Hygiëne (C) alleen lost mechanische probleem niet op. Occlusie (D) is niet primaire oorzaak. Hyperplasie (E) ontstaat later bij chronische irritatie.",
        "category": "Implantaatprothetiek - Overkappingsprothese ontwerp",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["implantologie", "prothetiek", "overkappingsprothese", "complicaties", "retentie"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 23,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt heeft indicatie voor volkeramische kroon op element 11 na endodontische behandeling. Resterende kroonstructuur: 60% met palatinale wand intact. Gingiva is gezond, occlusie normaal zonder bruxisme. Hoge esthetische verwachtingen. Preparatie wordt uitgevoerd voor lithium disilicaat (e.max) kroon.\nVRAAG: Welke preparatie parameters zijn optimaal voor deze situatie?",
        "options": [
            "1.0mm reductie axiaal, 1.5mm incisaal, shoulder margin",
            "1.2mm reductie axiaal, 2.0mm incisaal, deep chamfer margin",
            "0.8mm reductie axiaal, 1.0mm incisaal, knife edge margin",
            "1.5mm reductie axiaal, 2.5mm incisaal, beveled shoulder",
            "2.0mm reductie axiaal, 3.0mm incisaal, butt joint margin"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "1.2mm reductie axiaal, 2.0mm incisaal, deep chamfer margin",
        "explanation": "Voor lithium disilicaat kronen zijn optimale preparatie dimensies: 1.2mm axiaal, 2.0mm incisaal voor adequate materiaaldikte en sterkte, deep chamfer margin voor beste pasvorm en cementlijn. Insufficiënte reductie (A,C) compromitteert sterkte en esthetiek. Knife edge (C) geeft een zwakke marge. Over-reductie (E) vereist onnodig uitgebreide preparatie. Beveled shoulder (D) is minder gecontroleerd dan chamfer.",
        "category": "Kronen en bruggen - Preparatie principes",
        "domain": "PROTH",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["kronen", "bruggen", "preparatie", "materialen", "esthetiek"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 24,
        "text": "KLINISCHE CASUS: Een 35-jarige vrouw presenteert zich met tweezijdige kaakpijn, beperkte mondopening (28mm), klikken bij opening en sluiting, en hoofdpijn. Symptomen bestaan 6 maanden en verergeren bij stress. Geen trauma anamnese. Occlusie toont posterieure kruisbeet rechts en anterieure geleiding op cuspids. Spierpalpatie toont gevoeligheid van masseter en temporalis bilateraal.\nVRAAG: Wat is de meest waarschijnlijke diagnose en eerste behandelstap?",
        "options": [
            "Anterieure discdislocatie met reductie - MRI en chirurgische consultatie",
            "Myofasciale pijn met beperkte opening - conservatieve behandeling",
            "Reumatoïde artritis TMJ - laboratorium onderzoek en systemische behandeling",
            "Anterieure discdislocatie zonder reductie - arthroscopie indicatie",
            "Bruxisme met occlusaal trauma - immediate splint therapie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Myofasciale pijn met beperkte opening - conservatieve behandeling",
        "explanation": "Klinische presentatie (bilaterale spierpijn, beperkte opening, klikken, stressrelatie) wijst op myofasciaal pijnsyndroom. Eerste lijn behandeling: rust, warmte, zachte voeding, stress management, fysiotherapie. MRI (A) is niet de eerste keuze zonder falen van conservatieve behandeling. RA (C) zou andere gewrichten betreffen. Discdislocatie zonder reductie (D) geeft andere symptomen. Splint (E) kan helpen maar is geen primaire behandeling.",
        "category": "TMJ disfunctie - Diagnostiek",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["TMJ", "diagnostiek", "pijn", "kaak", "myofasciaal"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 25,
        "text": "KLINISCHE CASUS: Een 28-jarige patiënte wenst esthetische verbetering van bovenelementen 13-23. Klachten: gele verkleuring na orthodontische behandeling, lichte malpositie elementen 12,22 (rotatie), klein diastema tussen 11,21. Elementen zijn vitaal, geen cariës, normale occlusie. Budget geen beperking, wenst minimaal invasieve oplossing.\nVRAAG: Welke behandeloptie biedt optimale esthetiek met minimale invasiviteit?",
        "options": [
            "Volkeramische facings op alle 6 elementen",
            "Combinatie: facings op 12,22 en bleken andere elementen",
            "Composiet facings (directe methode) op alle elementen",
            "Orthodontische correctie gevolgd door bleken",
            "Volkeramische kronen op malgepositioneerde elementen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Combinatie: facings op 12,22 en bleken andere elementen",
        "explanation": "Combinatiebehandeling maximaliseert conservatie: facings alleen waar vorm/positie correctie nodig (12,22), bleken voor kleurcorrectie andere vitale elementen. Dit bespaart tandstructuur en kosten. Facings op alle elementen (A) is overbehandeling. Composiet facings (C) hebben beperkte duurzaamheid. Orthodontie (D) duurt lang en lost verkleuring niet op. Kronen (E) zijn te invasief.",
        "category": "Esthetische tandheelkunde - Facing indicaties",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["esthetiek", "facings", "bleken", "restauratief", "minimaal invasief"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 26,
        "text": "KLINISCHE CASUS: Een 58-jarige patiënt mist elementen 14,15,16 en 25,26,27. Resterende elementen zijn gezond met goede parodontale status. Element 17 en 24 hebben minimale kronen. Patiënt wenst uitneembare oplossing vanwege kosten. Occlusie stabiel, adequate interarch afstand.\nVRAAG: Welk RPD design biedt optimale ondersteuning en stabiliteit?",
        "options": [
            "Bilaterale distale extensie met gegoten klemmen",
            "Tand-weefsel gedragen met opmetingkronen op 17,24",
            "Weefsel gedragen met lineaire klemmen en brede palatale bedekking",
            "Implantaat-weefsel gedragen met locator attachments",
            "Unilateraal ontwerp met extensie naar onbelaste zijde"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Tand-weefsel gedragen met opmetingkronen op 17,24",
        "explanation": "Bilaterale distale extensie casussen vereisen optimale abutment ondersteuning. Opmetingkronen op 17,24 creëren ideale retentieve ondersnijdingen, steunpunten, en geleidevlakken voor maximale prothetische stabiliteit. Dit compenseert voor tissue support in extension areas. Conventionele klemmen (A) geven suboptimale retentie op kleine kronen. Zuivere weefselondersteuning (C) heeft inadequate retentie. Implantaten (D) zijn buiten budget. Unilateraal ontwerp (E) geeft asymmetrische belasting.",
        "category": "Partiële prothetiek - Uitneembare partiële prothese (RPD) ontwerp",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["prothetiek", "RPD", "partiële prothese", "occlusie", "retentie"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 27,
        "text": "KLINISCHE CASUS: Een 40-jarige patiënt heeft indicatie voor posterieure kroon op element 46 na grote amalgaamfractuur. Resterende tandstructuur 50%, occlusale krachten hoog (clenching habiet), esthetiek secundair. Behandeling in één sessie gewenst (CEREC systeem). Kroon moet minimaal 10 jaar meegaan.\nVRAAG: Welk CAD/CAM materiaal is het meest geschikt voor deze indicatie?",
        "options": [
            "Lithium disilicaat (e.max CAD)",
            "Zirkoniumdioxide (Katana Zirconia)",
            "Polymeer geïnfiltreerd keramiek (Enamic)",
            "Leuciet versterkt glaskeramiek (ProCAD)",
            "Composiet harsblok (Lava Ultimate)"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Zirkoniumdioxide (Katana Zirconia)",
        "explanation": "Voor hoge occlusale belasting in posterieur gebied is zirkoniumdioxide optimaal door superieure flexural strength (>900 MPa) en fracture toughness. Lithium disilicaat (A) heeft lagere sterkte voor extreme belasting. Hybride keramiek (C,E) heeft beperkte sterkte. Leuciet keramiek (D) is verouderd voor posterieure belasting. Zirkonia biedt de beste lange termijn vooruitzichten bij bruxisme.",
        "category": "CAD/CAM restauraties - Materiaalkarakteristieken",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["CAD/CAM", "materialen", "kronen", "restauratief", "zirkoniumdioxide"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 28,
        "text": "KLINISCHE CASUS: Een 52-jarige patiënt ondergaat volledige mondrehabilitatie met kronen en bruggen na uitgebreide parodontale behandeling. Bij registratie van de kaakrelatie wordt 2mm discrepantie gevonden tussen centric relation (CR) en maximum intercuspidatie (MI). Patiënt heeft geen TMJ klachten momenteel.\nVRAAG: Hoe moet deze CR-MI discrepantie worden gemanaged in de definitieve restauraties?",
        "options": [
            "Restauraties maken in bestaande MI voor comfort patiënt",
            "Geleidelijke conditionering naar CR via tijdelijke restauraties",
            "Directe registratie in CR en acceptatie van initiële discomfort",
            "Orthodontische correctie voor eliminatie van discrepantie",
            "Compromis positie tussen CR en MI kiezen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Geleidelijke conditionering naar CR via tijdelijke restauraties",
        "explanation": "Bij significante CR-MI discrepantie tijdens volledige rehabilitatie is gefaseerde deprogrammering via tijdelijke restauraties de veiligste aanpak. Dit voorkomt acute TMJ disfunctie en musculaire adaptatieproblemen. Definitieve restauraties in MI (A) bestendigen een pathologische positie. Directe CR registratie (C) kan TMJ problemen veroorzaken. Orthodontie (D) is niet altijd mogelijk. Compromispositie (E) lost fundamentele discrepantie niet op.",
        "category": "Occlusie - Centrische relatie vs. centrische occlusie",
        "domain": "PROTH",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.2,
            "discrimination": 2.0,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["occlusie", "rehabilitatie", "TMJ", "kaakrelatie", "restauratief"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 29,
        "text": "KLINISCHE CASUS: Een 25-jarige patiënte heeft 4 maanden geleden implantaat gekregen in positie 21 na trauma. Implantaat is osteogeïntegreerd. Zachte weefselen tonen adequate genezing maar gingivale rand staat 1mm apicaler dan contralaterale element 11. Papillen zijn aanwezig maar niet ideaal. Patiënte heeft hoge esthetische verwachtingen.\nVRAAG: Welke prothetische strategie optimaliseert het esthetische resultaat?",
        "options": [
            "Directe plaatsing van definitieve kroon en acceptatie van marginaal niveau",
            "Temporisering met tissue conditioning en geleidelijke contouroptimalisatie",
            "Zacht weefselaugmentatie voor creatie van optimale gingivale architectuur",
            "Verwijdering en uitgestelde implantatie na site development",
            "Orthodontische extrusie van aangrenzende elementen voor nivellering"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Temporisering met tissue conditioning en geleidelijke contouroptimalisatie",
        "explanation": "In de esthetische zone is weefselconditionering via een tijdelijke kroon cruciaal voor optimalisatie van zachte weefselen. Geleidelijke contouren van het emergence profile stimuleren papilregeneratie en gingivale positie. Dit geeft superieure esthetische resultaten versus directe definitieve kroon (A). Zacht weefsel chirurgie (C) is invasief met beperkte voorspelbaarheid. Implantaatverwijdering (D) is te radicaal. Orthodontie (E) is complex en niet geïndiceerd.",
        "category": "Implantaatprothetiek - Esthetische zone",
        "domain": "PROTH",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["implantologie", "esthetiek", "prothetiek", "weke delen", "temporisering"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },
    {
        "id": 30,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt presenteert zich met gefractureerde porseleinen facing op lithium disilicaat kroon element 11, geplaatst 18 maanden geleden. Fractuur betreft alleen het facing porselein, de kern lithium disilicaat is intact. Margin integrity is goed, geen cariës. Occlusie toont heavy contact in protrusive movement.\nVRAAG: Wat is de meest geëigende behandeling voor deze situatie?",
        "options": [
            "Intraorale composietreparatie van gefractureerd gebied",
            "Complete vervanging van kroon met nieuwe fabricage",
            "Verwijdering van facing porselein en polijsten van lithium disilicaat",
            "Extraorale reparatie na verwijdering en recementatie",
            "Occlusale aanpassing en monitoring zonder directe reparatie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Verwijdering van facing porselein en polijsten van lithium disilicaat",
        "explanation": "Bij facing fractuur op een lithium disilicaat kern met intact onderliggend materiaal is verwijdering van het gefractureerde porselein en polijsten van het lithium disilicaat oppervlak de beste optie. Lithium disilicaat heeft goede esthetiek na polijsten. Composietreparatie (A) heeft beperkte hechting aan porselein. Complete vervanging (B) is overbehandeling. Extraorale reparatie (D) is complex en kostbaar. Monitoring (E) lost het esthetische probleem niet op.",
        "category": "Prothetische complicaties - Keramiekfractuur",
        "domain": "PROTH",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["prothetiek", "complicaties", "kronen", "facings", "reparatie"],
        "created_at": "2025-07-21T16:05:00Z",
        "updated_at": "2025-07-21T16:05:00Z"
    },{
        "id": 31,
        "text": "KLINISCHE CASUS: Een 5-jarig kind presenteert zich met spontane pijn in element 84 sinds 2 dagen. Moeder rapporteert nachtelijke pijn en pijnstillers helpen matig. Klinisch onderzoek: grote occlusale cariës, geen zwelling of fistel. Percussie matig pijnlijk, vitaliteitstest positief maar verlengde reactie op koud. Röntgenfoto toont diepe cariës nabij pulpa, geen apicale radiolucentie, wortelresorptie <1/3.\nVRAAG: Welke pulpatherapie is geïndiceerd voor dit melkelement?",
        "options": [
            "Indirecte pulpaoverkapping met calciumhydroxide",
            "Partiële pulpotomie met ijzersulfaat",
            "Pulpectomie met ZOE vulling van kanalen",
            "Extractie en space maintainer plaatsing",
            "Pulpotomie met formocresol (verdund 1:5)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Pulpectomie met ZOE vulling van kanalen",
        "explanation": "Symptomen wijzen op irreversibele pulpitis (spontane pijn, nachtelijke pijn, verlengde reactie). Bij melkelementen met irreversibele pulpitis en wortelresorptie <2/3 is pulpectomie geïndiceerd. ZOE is veilig en effectief voor melktanden. Indirecte overkapping (A) is inadequaat bij irreversibele pulpitis. Pulpotomie (B) is alleen geschikt voor reversibele pulpitis. Extractie (D) is te radicaal bij een restoreerbare tand. Formocresol (E) wordt vermeden vanwege toxiciteit.",
        "category": "Pulpatherapie melktanden",
        "domain": "PEDI",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["pediatrie", "pulpatherapie", "melktanden", "endodontie", "cariës"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 32,
        "text": "KLINISCHE CASUS: Een 7-jarig kind met extreme tandheelkundige angst komt voor eerste behandeling (2 cariëslaesies). Vorige pogingen bij andere tandartsen mislukten door oncontroleerbaar huilen en verzet. Ouders rapporteren normale ontwikkeling, geen medische problemen. Kind weigert mondonderzoek en reageert panisch op dentale instrumenten.\nVRAAG: Welke gedragsmanagement strategie is het meest geschikt als eerste benadering?",
        "options": [
            "Onmiddellijke sedatie met midazolam voor volledige behandeling",
            "Tell-show-do techniek met positieve bekrachtiging",
            "Fysieke fixatie met snelle voltooiing van de behandeling",
            "Lachgas sedatie vanaf eerste bezoek",
            "Verwijzing naar pediatrisch tandarts met algemene anesthesiefaciliteit"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Tell-show-do techniek met positieve bekrachtiging",
        "explanation": "Tell-show-do met positieve bekrachtiging is de eerste lijn gedragsmanagement voor angstige kinderen. Deze niet-farmacologische benadering bouwt vertrouwen en coping skills op. Systematische desensitisatie reduceert angst geleidelijk. Sedatie (A,D) is tweede lijn na falen van conservatieve methoden. Fysieke fixatie (C) is gecontra-indiceerd en traumatiserend. Algemene anesthesie (E) is laatste optie bij uitgebreide behandeling.",
        "category": "Gedragsmanagement - Angstig kind",
        "domain": "PEDI",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["pediatrie", "gedragsmanagement", "angst", "communicatie", "kinderen"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 33,
        "text": "KLINISCHE CASUS: Een 3-jarig kind valt en luxeert element 61 (laterale luxatie, 45 graden palatinaal). Trauma 2 uur geleden. Element is mobiel maar niet geëxtrudeerd. Ouders hebben fragment niet gevonden. Geen andere tandletsel, geen neurologische symptomen. Kind coöperatief redelijk voor onderzoek.\nVRAAG: Wat is de meest geëigende acute behandeling?",
        "options": [
            "Repositie en spalken gedurende 2 weken",
            "Extractie om schade aan permanente successor te voorkomen",
            "Repositie zonder spalken en follow-up",
            "Observatie zonder repositie, zachte kost",
            "Pulpectomie en repositie met spalken"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Extractie om schade aan permanente successor te voorkomen",
        "explanation": "Laterale luxatie van melkvoortanden bij jonge kinderen (3 jaar) heeft een hoog risico op schade aan de ontwikkelende permanente opvolger. Extractie voorkomt complicaties zoals dens in dente of calcificatie van de permanente tand. Repositie (A,C) riskeert mechanische schade aan de tandkiem. Observatie (D) lost luxatie niet op. Pulpectomie (E) is overbehandeling voor een melktand met slechte prognose.",
        "category": "Traumatologie - Melktandluxatie",
        "domain": "PEDI",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 2.0,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["pediatrie", "traumatologie", "melktanden", "luxatie", "extractie"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 34,
        "text": "KLINISCHE CASUS: Een 4-jarig kind uit een familie met hoog cariësrisico (ouders hebben veel vullingen, suikerhoudende voeding, suboptimale mondhygiëne) krijgt preventief advies. Lokaal drinkwater bevat 0.2ppm fluoride. Kind gebruikt standaard kindertandpasta. Eerste molaren tonen beginnende demineralisatie.\nVRAAG: Welk fluoride protocol is het meest effectief voor dit hoogrisicokind?",
        "options": [
            "Doorgaan met kindertandpasta (500ppm) en goede poetsfrequentie",
            "Overschakelen naar 1000ppm tandpasta onder supervisie",
            "Fluoridesupplementen (tabletten) 0.5mg dagelijks",
            "Professionele fluoridevernis applicatie iedere 3 maanden",
            "Combinatie: 1000ppm tandpasta + fluoridevernis halfjaarlijks"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Combinatie: 1000ppm tandpasta + fluoridevernis halfjaarlijks",
        "explanation": "Hoogrisicokinderen van 4 jaar profiteren van een intensief fluorideprotocol: 1000ppm tandpasta (veilig onder supervisie) + professionele vernisapplicaties. Studies tonen een additief effect van meerdere fluoridebronnen. Kindertandpasta alleen (A) is onvoldoende bij een hoog risico. Supplementen (C) zijn niet nodig bij tandpastagebruik. Vernis alleen (D) is suboptimaal zonder dagelijkse fluorideblootstelling.",
        "category": "Preventie - Fluorideprotocollen",
        "domain": "PEDI",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["pediatrie", "preventie", "fluoride", "cariësrisico", "mondhygiëne"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 35,
        "text": "KLINISCHE CASUS: Een 8-jarig kind in mixed dentition fase toont crowding in onderfront. Elementen 71,81 zijn geëxfolieerd, 31,41 erupteren linguaal. Beschikbare ruimte 22mm, required space 24mm (2mm tekort). Bovenkaak normale spacing. Ouders vragen om orthodontische evaluatie.\nVRAAG: Wat is de meest geëigende behandelings-timing voor dit ruimtegebrek?",
        "options": [
            "Onmiddellijke interceptieve orthodontie met uitneembaar apparaat",
            "Afwachten compleet mixed dentition (leeway space) voor evaluatie",
            "Extractietherapie van melkcaninen voor ruimtecreatie",
            "Vaste beugelbehandeling starten op 8-jarige leeftijd",
            "Serie-extractie protocol initiëren met 74,84"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Afwachten compleet mixed dentition (leeway space) voor evaluatie",
        "explanation": "Bij beperkte crowding (2mm) in het wisselgebit is afwachten tot complete tandenwissel wijs vanwege de leeway space. Uitval van molaren geeft 3-4mm extra ruimte per zijde. Premature interventie (A,D) kan overbehandeling zijn. Canine extracties (C) verstoren de normale ontwikkeling. Serie-extractie (E) is geïndiceerd bij ernstige crowding (>4mm tekort).",
        "category": "Ruimtegebrek - Wisselgebit",
        "domain": "PEDI",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["pediatrie", "orthodontie", "wisselgebit", "ruimtegebrek", "groeimodificatie"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 36,
        "text": "KLINISCHE CASUS: Een 6-jarig kind (gewicht 20kg) heeft lokale anesthesie nodig voor pulpotomie element 85. Kind is gezond, geen allergieën bekend. Vorige anesthesie ervaringen waren goed. Behandeling duurt naar verwachting 45 minuten. Standaard articaïne 4% met adrenaline 1:100.000 beschikbaar.\nVRAAG: Wat is de maximaal veilige dosering anesthesie voor dit kind?",
        "options": [
            "1.0ml (44mg articaïne) maximum voor complete behandeling",
            "1.8ml (72mg articaïne) - standaard carpule dosering",
            "2.2ml (88mg articaïne) - maximale pediatrische dosering",
            "0.5ml (22mg articaïne) - ultra-conservatieve dosering",
            "3.6ml (144mg articaïne) - volwassen equivalent dosering"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "2.2ml (88mg articaïne) - maximale pediatrische dosering",
        "explanation": "Veilige articaïnedosering voor kinderen: 7mg/kg maximum. Kind 20kg: 7×20=140mg maximum. 2.2ml (88mg) is veilig binnen deze limiet voor een 45-minuten behandeling. 1.0ml (A) kan onvoldoende zijn voor adequate anesthesie. Standaard carpule (B) is acceptabel maar conservatief. 0.5ml (D) is waarschijnlijk inadequaat. 3.6ml (E) overschrijdt de veiligheidsmarge aanzienlijk.",
        "category": "Anesthesie - Pediatrische dosering",
        "domain": "PEDI",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["pediatrie", "anesthesie", "farmacologie", "dosering", "veiligheid"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 37,
        "text": "KLINISCHE CASUS: Een 18 maanden oude peuter wordt gebracht door ouders voor eerste tandheelkundige controle. 8 elementen zijn geërupteerd (melkincisivi), geen zichtbare cariës. Ouders geven flesvoeding 's nachts, veel fruit als tussendoortjes. Fluoride tandpasta wordt niet gebruikt \"omdat kind nog niet kan spugen\".\nVRAAG: Welke primaire preventieve maatregel heeft hoogste prioriteit?",
        "options": [
            "Starten met fluoride-vrije kindertandpasta en poetsinstructie",
            "Stoppen nachtelijke flesvoeding en beperken suikerblootstelling",
            "Wachten tot 2 jaar voor fluoride tandpasta introductie",
            "Professionele fluoridevernis applicatie starten",
            "Orthodontische screening voor zuiggewoontes"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Stoppen nachtelijke flesvoeding en beperken suikerblootstelling",
        "explanation": "Nachtelijke flesvoeding is de hoogste risicofactor voor vroege kindercariës bij peuters. Lange suikerblootstelling tijdens slaap (verminderde speekselvloed) veroorzaakt rampante cariës. Stoppen van deze gewoonte heeft de grootste preventieve impact. Fluoride tandpasta (A) is belangrijk maar secundair aan dieetadvies. Wachten (C) mist preventiekansen. Professionele fluoride (D) is aanvullend. Orthodontie (E) is niet urgent op deze leeftijd.",
        "category": "Cariëspreventie - Vroege kinderjaren",
        "domain": "PEDI",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.4,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["pediatrie", "preventie", "cariës", "flesvoeding", "dieet"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 38,
        "text": "KLINISCHE CASUS: Een 7-jarig kind verliest element 75 door cariës. Röntgenfoto toont element 35 in crypte, eruptie verwacht over 4 jaar. Element 36 is geërupteerd, elementen 74,76 aanwezig. Ouders vragen of space maintainer nodig is.\nVRAAG: Welke space maintainer strategie is geïndiceerd?",
        "options": [
            "Geen space maintainer - natuurlijke ruimte sluiting accepteren",
            "Uitneembare partiële prothese met esthetiek en functie",
            "Vaste unilaterale space maintainer (band-en-loop)",
            "Bilaterale space maintainer voor symmetrische ondersteuning",
            "Kroon-en-loop op element 74 voor space maintenance"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Vaste unilaterale space maintainer (band-en-loop)",
        "explanation": "Prematuur verlies van de eerste melkmolaar vereist ruimtebehoud vanwege de lange periode tot opvolgereruptie (4 jaar). Vaste unilaterale band-en-loop op 36 is de gouden standaard: effectief, duurzaam, patiëntvriendelijk. Geen maintainer (A) resulteert in ruimteverlies. RPD (B) is complex voor jonge kinderen. Bilateraal (D) is onnodige overbehandeling. Kroon-en-loop (E) is minder retentief dan band-en-loop.",
        "category": "Ruimtebehoud - Prematuur molaarverlies",
        "domain": "PEDI",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["pediatrie", "orthodontie", "ruimtebehoud", "melktanden", "cariës"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 39,
        "text": "KLINISCHE CASUS: Een 12-jarig kind presenteert zich met gele, brokkelige tanden en extreme gevoeligheid. Alle permanente elementen zijn aangedaan. Familieanamnese toont vergelijkbare problemen bij vader. Geen andere medische problemen. Röntgenfoto toont normale wortelvorming maar dun, onregelmatig glazuur.\nVRAAG: Welke behandelstrategie is prioriteit voor dit kind?",
        "options": [
            "Onmiddellijke volledige mondrehabilitatie met kronen",
            "Desensibiliserende therapie en observatie tot volwassenheid",
            "Fluoridetherapie en beschermende harscoatings",
            "Extractie aangedane elementen en orthodontische spatiëring",
            "Verwijzing naar geneticus voor familiebegeleiding"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Fluoridetherapie en beschermende harscoatings",
        "explanation": "Bij amelogenesis imperfecta is het primaire doel bescherming van de resterende tandstructuur en symptoommanagement tijdens de groei. Fluoridetherapie + beschermende harscoatings bieden onmiddellijke verlichting en preserveren tandstructuur voor latere definitieve behandeling. Volledige rehabilitatie (A) is te vroeg tijdens de groei. Alleen observatie (B) is inadequaat voor symptomen. Extracties (D) zijn te radicaal. Genetische counseling (E) is belangrijk maar niet urgent.",
        "category": "Ontwikkelingsstoornissen - Amelogenesis imperfecta",
        "domain": "PEDI",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["pediatrie", "ontwikkelingsstoornis", "glazuur", "amelogenesis imperfecta", "fluoride"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },
    {
        "id": 40,
        "text": "KLINISCHE CASUS: Een 9-jarig kind heeft complexe behandeling nodig (4 restauraties) maar toont matige angst en coöperatieproblemen. Tell-show-do heeft beperkt succes gehad. Ouders vragen om sedatieoptie. Kind is gezond (ASA I), geen contra-indicaties voor N2O. Behandeling duurt ongeveer 90 minuten.\nVRAAG: Welk nitrous oxide protocol is veilig en effectief voor dit kind?",
        "options": [
            "10% N2O concentratie gedurende gehele behandeling",
            "30% N2O met oxygen monitoring en gradual induction",
            "50% N2O maximum concentratie voor optimale effect",
            "70% N2O met pulse oximetry en blood pressure monitoring",
            "Variabele concentratie 20-40% aangepast aan response"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Variabele concentratie 20-40% aangepast aan response",
        "explanation": "Optimale N2O sedatie gebruikt een titratieprotocol: start 20% en pas aan naar patiëntrespons tot 40% maximum. Dit individualiseert het sedatieniveau en maximaliseert veiligheid. Vaste lage concentratie (A) is mogelijk inadequaat. 30% (B) kan te hoog zijn als startdosis. 50% (C) en 70% (D) overschrijden pediatrische veiligheidsrichtlijnen. Moderne pediatrische sedatie gebruikt patiënt-specifieke titratie voor optimale resultaten.",
        "category": "Sedatie - Lachgasprotocol",
        "domain": "PEDI",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["pediatrie", "sedatie", "lachgas", "angstmanagement", "veiligheid"],
        "created_at": "2025-07-21T16:07:00Z",
        "updated_at": "2025-07-21T16:07:00Z"
    },{
        "id": 41,
        "text": "KLINISCHE CASUS: Een 35-jarige niet-roker presenteert zich met gegeneraliseerde gingivale zwelling en bloeding. Probing depths 4-7mm, attachment loss 3-5mm, radiografisch botverlies 30-50%. Symptomen ontwikkelden zich over 18 maanden. Familieanamnese: vader verloor alle tanden voor 40ste levensjaar. Geen systemische aandoeningen, goede mondheelkunde voorheen.\nVRAAG: Welke parodontitis classificatie past bij deze presentatie?",
        "options": [
            "Gingivitis geïnduceerd door plaque met lokale factoren",
            "Gegeneraliseerde parodontitis stadium II graad B",
            "Gegeneraliseerde parodontitis stadium III graad C",
            "Agressieve parodontitis gegeneraliseerde vorm",
            "Necrotiserende ulceratieve gingivitis (NUG)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Gegeneraliseerde parodontitis stadium III graad C",
        "explanation": "Volgens de nieuwe AAP/EFP classificatie (2017): gegeneraliseerde betrokkenheid (>30% tanden), stadium III (attachmentverlies 3-5mm, botverlies <50%), graad C (snelle progressie <2 jaar, sterke familie-anamnese). Snelle progressie en familie-anamnese duiden op graad C. Stadium II (B) onderschat de ernst. Oude classificatie 'agressieve parodontitis' (D) is verlaten. NUG (E) heeft andere klinische tekenen.",
        "category": "Parodontitis classificatie",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 2.0,
            "guessing": 0.16
        },
        "image_url": null,
        "tags": ["parodontologie", "diagnostiek", "classificatie", "parodontitis", "botverlies"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 42,
        "text": "KLINISCHE CASUS: Een 45-jarige roker (15 sigaretten/dag) heeft gegeneraliseerde parodontitis met probing depths 5-8mm. Initiële therapie met scaling en root planing is gepland. Patiënt gebruikt geen medicatie, goede algemene gezondheid. Vraagt of antibiotica nodig zijn en hoeveel sessies behandeling duurt.\nVRAAG: Welk evidence-based protocol is optimaal voor deze patiënt?",
        "options": [
            "Full-mouth desinfectie in 2 sessies + systemische antibiotica",
            "Quadrant-wise SRP over 4-6 weken, geen antibiotica",
            "Full-mouth SRP in 24 uur + chloorhexidine spoeling",
            "Laser-assisted parodontale therapie zonder instrumentatie",
            "Quadrant SRP + lokale antibiotica in alle pockets"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Full-mouth SRP in 24 uur + chloorhexidine spoeling",
        "explanation": "Full-mouth SRP binnen 24 uur (full-mouth desinfectie concept) toont superieure resultaten bij gegeneraliseerde parodontitis versus quadrant-wise behandeling. Voorkomt herinfectie tussen sessies. Chloorhexidine ondersteunt de genezing. Systemische antibiotica (A) zijn niet routinematig geïndiceerd. Quadrant-wise (B) is verouderd. Laser alleen (D) is inadequaat zonder mechanische debridement. Lokale antibiotica (E) zijn niet evidence-based voor alle pockets.",
        "category": "Niet-chirurgische therapie - SRP protocol",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["parodontologie", "SRP", "niet-chirurgisch", "gingivitis", "chloorhexidine"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 43,
        "text": "KLINISCHE CASUS: Een 38-jarige niet-rokende patiënt heeft na initiële therapie een persisterend 8mm intrabony defect aan element 47 distaal. Röntgenfoto toont 6mm verticaal botverlies. Omliggende parodontium is gezond, goede plaque controle. Patiënt wenst behoud van element en vraagt naar chirurgische opties.\nVRAAG: Welke regeneratieve techniek biedt de beste vooruitzichten voor dit defect?",
        "options": [
            "Modified Widman flap zonder regeneratieve materialen",
            "Guided tissue regeneration met titanium membraan + autoloog bot",
            "Enamel matrix derivative (EMD) alleen",
            "Bottransplantaat materiaal (xenograft) zonder membraan",
            "GTR met resorbeerbaar membraan + botsubstituut"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "GTR met resorbeerbaar membraan + botsubstituut",
        "explanation": "Voor diepe intrabony defecten biedt GTR met resorbeerbaar membraan + botsubstituut de beste regeneratieve resultaten. Combinatie geeft superieure klinische attachment gain versus monotherapieën. Niet-resorbeerbare membraan (B) heeft complicatie risico. EMD alleen (C) is minder effectief bij diepe defecten. Bottransplantaat alleen (D) mist barrière functie. Modified Widman (A) is niet-regeneratief.",
        "category": "Parodontale chirurgie - Regeneratieve procedures",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["parodontologie", "chirurgie", "regeneratie", "GTR", "bottransplantaat"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 44,
        "text": "KLINISCHE CASUS: Een 52-jarige patiënt met diabetes type 2 (HbA1c 8.5%) heeft gegeneraliseerde parodontitis. Na conventionele SRP blijven probing depths 6-7mm met persisterende bloeding. Diabetische controle is suboptimaal ondanks medicatie. Parodontale healing verloopt traag.\nVRAAG: Welke aanvullende behandelstrategie is het meest effectief?",
        "options": [
            "Systemische antibiotica (amoxicilline + metronidazol) 7 dagen",
            "Lokale antimicrobiële therapie (chloorhexidine chips)",
            "Intensieve diabetische controle + herhaalde SRP",
            "Onmiddellijke parodontale chirurgie voor betere toegang",
            "Laser therapy voor antimicrobieel effect"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Intensieve diabetische controle + herhaalde SRP",
        "explanation": "Bij diabetische patiënten met slechte glykemische controle (HbA1c >7%) is verbetering van de diabetische status cruciaal voor parodontale genezing. Studies tonen een bidirectionele relatie: parodontitis verslechtert de glykemische controle en vice versa. Intensieve glucose controle + herhaalde SRP geeft de beste resultaten. Antibiotica (A) hebben een tijdelijk effect. Lokale antimicrobiële middelen (B) hebben beperkte evidence bij diabetes. Chirurgie (D) is voorbarig zonder optimale systemische controle.",
        "category": "Systemische factoren - Diabetes en parodontitis",
        "domain": "PARO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.9,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["parodontologie", "diabetes", "systemisch", "SRP", "comorbiditeit"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 45,
        "text": "KLINISCHE CASUS: Een 28-jarige patiënt klaagt over gevoeligheid en esthetische problemen door gingivale recessie element 23 (Miller Class I, 4mm recessie). Patiënt heeft orthodontische behandeling gehad. Goede mondhygiëne, geen actieve parodontitis. Adequate keratinized gingiva width lateraal van defect.\nVRAAG: Welke mucogingivale procedure geeft het beste esthetische en functionele resultaat?",
        "options": [
            "Vrije gingivatransplantaat voor augmentatie gekeratiniseerd weefsel",
            "Coronaal verschoven flap met bindweefseltransplantaat",
            "Laterale schuiflap van aangrenzende gingiva",
            "Semilunar coronaal gepositioneerde flap",
            "Guided tissue regeneration met resorbeerbaar membraan"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Coronaal verschoven flap met bindweefseltransplantaat",
        "explanation": "Coronally advanced flap + connective tissue graft is de gouden standaard voor Miller Klasse I defecten. Geeft optimale wortelbedekking (85-95%) met uitstekende esthetiek en kleuraanpassing. Vrije transplantaat (A) heeft mindere esthetiek door kleurbismatch. Laterale flap (C) creëert een donor site defect. Semilunar flap (D) heeft onvoorspelbare resultaten bij >3mm recessie. GTR (E) is niet geïndiceerd voor mucogingivale defecten.",
        "category": "Mucogingivale procedures - Gingivale recessie",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["parodontologie", "chirurgie", "gingivale recessie", "esthetiek", "transplantaat"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 46,
        "text": "KLINISCHE CASUS: Een 50-jarige patiënt heeft implantaat in regio 16 (5 jaar geleden geplaatst) met klachten van occasionele pijn en bloeding bij tandenpoetsen. Probing depth 7mm met suppuration, 3mm botverlies versus baseline röntgenfoto. Implantaat is osteogeïntegreerd en stabiel.\nVRAAG: Welke behandelstrategie is geïndiceerd voor deze peri-implantitis?",
        "options": [
            "Niet-chirurgische debridement en monitoring 3 maanden",
            "Systemische antibiotica zonder mechanische behandeling",
            "Chirurgische toegang met implantoplastiek en decontaminatie",
            "Onmiddellijke implantaatverwijdering en site preservatie",
            "Lasertherapie (Er:YAG) en fotodynamische therapie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Chirurgische toegang met implantoplastiek en decontaminatie",
        "explanation": "Moderate peri-implantitis (>3mm botverlies, suppuratie) vereist chirurgische behandeling. Open debridement met implantoplastiek (gladmaking implantaat oppervlak) en decontaminatie heeft de beste evidence. Niet-chirurgische behandeling (A) is inadequaat bij gevestigde peri-implantitis. Antibiotica alleen (B) zijn onvoldoende. Implantaatverwijdering (D) is te radicaal bij een stabiel implantaat. Laser alleen (E) heeft beperkte penetratie in biofilm.",
        "category": "Peri-implantitis - Diagnostiek en behandeling",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["parodontologie", "implantaat", "peri-implantitis", "chirurgie", "infectie"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 47,
        "text": "KLINISCHE CASUS: Een 25-jarige student presenteert zich met acute pijn, bloeding en geur uit de mond. Klinisch: gingivale necrose en ulceratie interdentaal, papillen zijn \"afgesneden\", grijswit pseudomembraan. Koorts 38.5°C, malaise. Stress door examens, slechte voeding laatste weken, rookt 20 sigaretten/dag.\nVRAAG: Wat is de meest geëigende acute behandeling voor deze NUG?",
        "options": [
            "Systemische antibiotica (metronidazol) en afwachten genezing",
            "Onmiddellijke volledige scaling en root planing onder anesthesie",
            "Zachte debridement + chloorhexidine spoeling + antibiotica",
            "Waterstofperoxide spoeling en pijnstilling alleen",
            "Verwijzing naar specialist voor chirurgische behandeling"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Zachte debridement + chloorhexidine spoeling + antibiotica",
        "explanation": "NUG (Necrotizing Ulcerative Gingivitis) vereist onmiddellijke maar zachte debridement om necrotisch weefsel te verwijderen zonder gezond weefsel te beschadigen. Chloorhexidine voor antimicrobieel effect, metronidazol voor anaërobe bacteriën. Antibiotica alleen (A) zijn inadequaat zonder debridement. Agressieve SRP (B) kan weefselschade verergeren. H2O2 alleen (D) is onvoldoende. Chirurgie (E) is gecontra-indiceerd in de acute fase.",
        "category": "Necrotiserende parodontale ziekten - Acute behandeling",
        "domain": "PARO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["parodontologie", "NUG", "gingivitis", "acute infectie", "antibiotica"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 48,
        "text": "KLINISCHE CASUS: Een 45-jarige ex-roker (gestopt 2 jaar geleden) heeft succesvolle parodontale behandeling ondergaan. Huidige status: probing depths 2-4mm, geen bloeding bij sondering, goede plaque controle. Familieanamnese van parodontitis. Patiënt vraagt naar frequency van maintenance bezoeken.\nVRAAG: Welk maintenance interval is geïndiceerd voor deze patiënt?",
        "options": [
            "6 maanden interval - standaard voor alle parodontale patiënten",
            "3 maanden interval vanwege parodontitis historie",
            "4 maanden interval - compromis tussen risico en praktisch",
            "Individuele beoordeling op basis van risicofactoren",
            "2 maanden interval eerste jaar, daarna verlengen"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Individuele beoordeling op basis van risicofactoren",
        "explanation": "Moderne ondersteunende parodontale therapie gebruikt individuele risk assessment voor intervalbepaling. Factoren: parodontitis historie, genetische predispositie (familie-anamnese), ex-rookstatus, huidige stabiliteit. Voor deze patiënt: 3-4 maanden interval waarschijnlijk optimaal. Vaste intervallen (A,B,C) negeren individuele risico. Vast schema (E) mist een gepersonaliseerde benadering voor deze specifieke risicofactoren.",
        "category": "Ondersteunende parodontale therapie - Onderhoudsprotocol",
        "domain": "PARO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["parodontologie", "onderhoud", "preventie", "risicobeoordeling", "roken"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 49,
        "text": "KLINISCHE CASUS: Een 28-jarige zwangere vrouw (16 weken zwangerschap) ontwikkelt gegeneraliseerde gingivale zwelling en bloeding ondanks goede mondhygiëne. Pocketdieptes 3-5mm, geen attachmentverlies. Pyogeen granuloom ontwikkelt zich interdentaal tussen 11-21. Geen parodontitis historie voorheen.\nVRAAG: Welke behandelstrategie is veilig en effectief tijdens zwangerschap?",
        "options": [
            "Uitstellen behandeling tot na bevalling wegens risico's",
            "Zachte scaling en improved oral hygiene, granuloommonitoring",
            "Systemische antibiotica voor controleren inflammatie",
            "Onmiddellijke chirurgische excisie van pyogeen granuloom",
            "Intensieve chloorhexidine therapy zonder mechanische behandeling"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Zachte scaling en improved oral hygiene, granuloommonitoring",
        "explanation": "Zwangerschapsgingivitis vereist conservatieve behandeling tijdens zwangerschap. Zachte scaling is veilig en effectief voor controleren van ontsteking. Pyogeen granuloom monitoring is belangrijk omdat spontane regressie vaak post-partum optreedt. Uitstellen (A) riskeert progressie naar ernstige infectie. Antibiotica (B) zijn niet routinematig geïndiceerd. Chirurgie (D) is te reserveren voor bloedings-/functiestoornissen. CHX alleen (E) is inadequaat zonder plaque verwijdering.",
        "category": "Parodontitis en zwangerschap - Hormonale gingivitis",
        "domain": "PARO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["parodontologie", "zwangerschap", "gingivitis", "hormonaal", "mondhygiëne"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 50,
        "text": "KLINISCHE CASUS: Een 40-jarige patiënt heeft na initial SRP enkele residuele pockets 6-7mm met persisterende bloeding ondanks goede plaque controle. Systemische gezondheid is goed. Patiënt wenst local antimicrobiële therapie voor verbetering voordat surgery wordt overwogen.\nVRAAG: Welke lokale antimicrobiële therapie heeft beste evidence voor adjunctive gebruik?",
        "options": [
            "Chloorhexidine gelatin chips (PerioChip)",
            "Doxycycline hyclate gel (Atridox)",
            "Metronidazol gel lokale applicatie",
            "Minocycline microdeeltjes (Arestin)",
            "Tetracycline fiber delivery system"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Minocycline microdeeltjes (Arestin)",
        "explanation": "Minocycline microsferen (Arestin) hebben de beste evidence voor additionele pocketdiepte reductie en klinische attachment gain als aanvulling op SRP. Het is een sustained release systeem met 14-dagen therapeutische levels. Doxycycline gel (B) heeft goede evidence maar is minder handig. CHX chips (A) hebben een beperkt substantief effect. Metronidazol gel (C) heeft minder evidence. Tetracycline vezels (E) zijn een verouderd systeem.",
        "category": "Lokale medicamenteuze therapie - Aanvullende antibiotica",
        "domain": "PARO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["parodontologie", "antibiotica", "medicatie", "SRP", "pocket"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 51,
        "text": "KLINISCHE CASUS: Een 9-jarig kind in mixed dentition heeft Angle klasse II divisie 1 malocclusie met 7mm overjet. Skeletaal: ANB 6°, retrognate mandibula. Gewoonten: duimzuigen tot 6 jaar (gestopt), mondademhaling door adenoïde hypertrofie. Ouders vragen om vroege behandeling wegens pesten op school.\nVRAAG: Welke interceptieve behandeling is meest geïndiceerd op deze leeftijd?",
        "options": [
            "Functioneel apparaat (Twin Block) voor mandibulaire groei stimulatie",
            "Headgear voor maxillaire groei restrictie",
            "Uitstellen behandeling tot permanente dentitie",
            "Herbst apparaat voor overjet reductie",
            "Snelle maxillaire expansie voor transversaal probleem"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Functioneel apparaat (Twin Block) voor mandibulaire groei stimulatie",
        "explanation": "Bij groeiende patiënten (9 jaar) met skeletale klasse II en mandibulaire retrognathie zijn functionele apparaten zoals Twin Block eerste keuze voor early treatment. Optimale timing tijdens pubertal growth spurt. Stimuleert mandibulaire groei en verbetert facial profile. Headgear (B) minder patient-friendly. Uitstellen (C) mist growth potential. Herbst (D) meestal voor oudere kinderen. RME (E) niet geïndiceerd zonder transversaal probleem.",
        "category": "Interceptieve orthodontie - Klasse II behandeling",
        "domain": "ORTHO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.9,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["orthodontie", "klasse II", "groeimodificatie", "functioneel apparaat", "pediatrie"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 52,
        "text": "KLINISCHE CASUS: Een 16-jarige patiënt heeft orthodontische behandeling met extractie van premolaren 14,24,34,44. Na alignment fase moet extraction space worden gesloten. Totale space per kant: 7mm. Deep bite aanwezig. Treatment plan: en masse retraction van anterior segment.\nVRAAG: Welke biomechanische overwegingen zijn cruciaal voor controlled space closure?",
        "options": [
            "Lichte krachten (150g) en intrusieve component voor beetopening",
            "Zware krachten (300g) voor snelle space closure",
            "Sliding mechanics met lage frictie bracketsysteem",
            "Sluitingslussen met gecontroleerde kantelbeweging",
            "Tijdelijke verankeringstoestellen voor absolute verankering"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Lichte krachten (150g) en intrusieve component voor beetopening",
        "explanation": "En masse retraction vereist light forces (150-200g per side) voor controlled movement en intrusive component voor deep bite correction. Heavy forces (B) veroorzaken root resorption en loss of control. Sliding mechanics (C) kunnen friction problemen hebben bij space closure. Loops (D) geven minder controle bij en masse movement. TADs (E) zijn niet altijd nodig bij adequate anchor control.",
        "category": "Biomechanica - Ruimtesluiting",
        "domain": "ORTHO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["orthodontie", "biomechanica", "ruimtesluiting", "krachten", "extractie"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 53,
        "text": "KLINISCHE CASUS: Een 17-jarige patiënte ontwikkelt clicking en mild discomfort in TMJ during orthodontische behandeling (18 maanden actief). Behandeling behelst bite opening en klasse II elastics. Geen TMJ problemen voor orthodontie. Ouders maken zich zorgen over verband met behandeling.\nVRAAG: Hoe moet deze TMJ symptomatologie worden gemanaged?",
        "options": [
            "Onmiddellijke stopzetting van elastieken en beetopening",
            "Conservatief management: zacht dieet, warmtetherapie, monitoring",
            "MRI evaluatie en specialistische consultatie direct",
            "Occlusale aanpassing voor eliminatie van premature contacten",
            "Verandering naar functionele apparaattherapie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Conservatief management: zacht dieet, warmtetherapie, monitoring",
        "explanation": "Mild TMJ symptoms tijdens orthodontie zijn common en meestal temporary adaptive responses. Conservative management is eerste lijn: soft diet, heat therapy, stress reduction, monitoring. Symptoms resolven meestal binnen enkele weken. Stoppen behandeling (A) onnodige interruption. MRI (C) niet geïndiceerd bij mild symptoms. Occlusal adjustment (D) premature tijdens actieve behandeling. Treatment change (E) not warranted voor mild symptoms.",
        "category": "TMJ en orthodontie - Disfunctie relatie",
        "domain": "ORTHO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["orthodontie", "TMJ", "kaakgewricht", "pijn", "management"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 54,
        "text": "KLINISCHE CASUS: Een 19-jarige patiënt voltooit orthodontische behandeling na 2.5 jaar. Behandeling omvatte extraction van premolaren, space closure, en detailing. Final result: excellent alignment, ideal overjet/overbite, klasse I molars. Patiënt vraagt naar retention protocol en duration.\nVRAAG: Welk retention protocol biedt beste lange termijn stability?",
        "options": [
            "Uitneembare retentievers (Hawley) fulltime 6 maanden, dan 's nachts onbeperkt",
            "Vaste retentievers 3-3 beide kaken permanent",
            "Combinatie: vaste retentievers 3-3 + uitneembare retentievers 's nachts",
            "Clear aligners (Essix) 's nachts gedurende 2 jaar alleen",
            "Positioner therapie 6 maanden gevolgd door Hawley retainers"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Combinatie: vaste retentievers 3-3 + uitneembare retentievers 's nachts",
        "explanation": "Combination retention (fixed + removable) biedt beste lange termijn stability. Fixed retainers voorkomen relapse van anterior alignment, removable retainers maintienen arch form en posterior relationships. Pure fixed (B) inadequaat voor posterior control. Pure removable (A,D) riskeert anterior relapse. Positioners (E) zijn verouderd. Modern retention philosophy: \"retention for life\" met combination approach.",
        "category": "Retentieprotocollen - Stabiliteitsfactoren",
        "domain": "ORTHO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.6,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["orthodontie", "retentie", "stabiliteit", "behandeling", "nazorg"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 55,
        "text": "KLINISCHE CASUS: Een 12-jarige patiënt heeft klasse III malocclusie met anterior crossbite. Cephalometric analysis: SNA 78°, SNB 85°, ANB -7°. Facial growth prediction toont continued mandibulaire growth. Ouders vragen om treatment options en prognosis.\nVRAAG: Welke behandelstrategie is meest realistisch voor deze patiënt?",
        "options": [
            "Immediate orthopedic treatment met facemask therapy",
            "Growth modification met chin cup voor mandibulaire restrictie",
            "Camouflage treatment met dental compensation",
            "Orthodontic-surgical approach na growth completion",
            "Serial extraction voor space creation en alignment"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Orthodontic-surgical approach na growth completion",
        "explanation": "Severe skeletal klasse III (ANB -7°) bij 12-jarige met continued growth prediction heeft poor prognosis voor non-surgical correction. Orthodontic-surgical approach na growth completion (16-18 jaar) geeft stable, functional results. Facemask (A) heeft beperkte effectiviteit op deze leeftijd. Chin cup (B) questionable evidence. Camouflage (C) heeft limitations bij severe discrepancy. Serial extraction (E) lost skeletaal probleem niet op.",
        "category": "Malocclusie analyse - Klasse III behandeling",
        "domain": "ORTHO",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 2.0,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["orthodontie", "klasse III", "malocclusie", "chirurgie", "groeimodificatie"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 56,
        "text": "KLINISCHE CASUS: Een 14-jarige patiënt heeft impacted caninus 13 palatally. Lateral incisor 12 heeft normal root formation. Panoramic röntgenfoto toont canine crown level met apex van 12. No resorption van adjacent teeth zichtbaar. Space is adequate in arch.\nVRAAG: Welke exposure en traction strategie is optimaal voor deze situatie?",
        "options": [
            "Extraction van impacted canine wegens poor prognosis",
            "Closed eruption technique met orthodontic traction",
            "Open exposure en immediate bracket placement",
            "Surgical repositioning naar normale positie",
            "Wait-and-see approach tot 16 jaar"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Closed eruption technique met orthodontic traction",
        "explanation": "Palatally impacted canines hebben excellent prognosis met closed eruption technique. Maintains keratinized gingiva, better periodontal outcomes vs. open exposure. Success rate >95% bij adequate space. Open exposure (C) compromises gingival esthetics. Extraction (A) onnodige loss van important tooth. Surgical repositioning (D) riskeert pulpal damage. Wait-and-see (E) vermindert success rate door continued impaction.",
        "category": "Geïmpacteerde elementen - Canine vrijleggen",
        "domain": "ORTHO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["orthodontie", "geïmpacteerd", "caninus", "chirurgie", "tractie"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 57,
        "text": "KLINISCHE CASUS: Een 35-jarige patiënt wenst orthodontische behandeling voor crowding in onderfront. Parodontale status: generalized slight bone loss, probing depths 3-4mm, good plaque control na parodontale behandeling 1 jaar geleden. Geen actieve parodontitis.\nVRAAG: Welke orthodontische modificaties zijn nodig voor deze adult patient?",
        "options": [
            "Light forces (25g) en extended treatment duration",
            "Normal forces maar frequent monitoring parodontale status",
            "Intrusive movements vermijden wegens bone loss",
            "Gingival augmentation voor behandeling starten",
            "Extraction treatment voor force reduction"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Normal forces maar frequent monitoring parodontale status",
        "explanation": "Adult patients met stable periodontal health kunnen normale orthodontische forces tolereren (50-75g voor incisoren) mits frequent periodontal monitoring. Light forces (A) verlengen treatment unnecessarily. Intrusive movements (C) zijn mogelijk bij healthy periodontium. Gingival surgery (D) niet routine nodig. Extractions (E) niet geïndiceerd alleen voor periodontal reasons bij stable condition.",
        "category": "Volwassen orthodontie - Parodontale overwegingen",
        "domain": "ORTHO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["orthodontie", "volwassen", "parodontologie", "bone loss", "behandeling"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 58,
        "text": "KLINISCHE CASUS: Een 15-jarige patiënt belt 's avonds met severe pain na activation van orthodontische appliance (new archwire placement vanmiddag). Pain score 8/10, moeilijk eten en slapen. Geen trauma, appliance intact. Normale analgetica (paracetamol) gaven minimal relief.\nVRAAG: Welke immediate pain management strategie is meest effectief?",
        "options": [
            "Spoedafspraak voor apparaatdeactivatie",
            "Ibuprofen 400mg + paracetamol 500mg combinatie",
            "Topicale anestheticagel applicatie op brackets",
            "Koudetherapie en zacht dieet gedurende 48 uur",
            "Orthodontische was applicatie en geruststelling"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Ibuprofen 400mg + paracetamol 500mg combinatie",
        "explanation": "Combination analgetica (ibuprofen + paracetamol) geeft superieure pain relief vs. monotherapy voor orthodontic pain. Ibuprofen addresses inflammatory component, paracetamol provides additional analgesia. Safe combination bij adolescents. Emergency deactivation (A) onnodige treatment interruption. Topical anesthetics (C) temporary effect. Cold therapy (D) helpful maar inadequate alone. Wax (E) doesn't address pain mechanism.",
        "category": "Orthodontische noodgevallen - Acute pijnbehandeling",
        "domain": "ORTHO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.6,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["orthodontie", "noodgeval", "pijn", "farmacologie", "beugel"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 59,
        "text": "KLINISCHE CASUS: Een 16-jarige patiënte start orthodontische behandeling en vraagt naar bracket opties. Hoge esthetische wensen voor school/sociale activiteiten. Complex case met extractions en significant tooth movement nodig. Treatment duration geschat 2.5 jaar. Budget geen beperking.\nVRAAG: Welk bracket systeem biedt optimale balans tussen esthetiek en efficiency?",
        "options": [
            "Conventionele metalen brackets voor maximale efficiëntie",
            "Keramische brackets (kristallijne alumina) op alle tanden",
            "Keramische brackets alleen op anterior teeth, metal op posterior",
            "Linguale brackets voor complete invisible treatment",
            "Clear aligners (Invisalign) voor esthetic alternative"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Keramische brackets alleen op anterior teeth, metal op posterior",
        "explanation": "Hybrid approach (ceramic anterior, metal posterior) biedt optimale balans: esthetiek waar meest zichtbaar, efficiency in posterior zone waar forces het hoogst zijn. Pure ceramic (B) heeft friction issues en bracket fracture risk. Metal brackets (A) compromitteren esthetiek. Lingual (D) heeft steep learning curve en discomfort. Clear aligners (E) hebben limitations bij complex movements met extractions.",
        "category": "Orthodontische materialen - Bracketsystemen",
        "domain": "ORTHO",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["orthodontie", "materialen", "brackets", "esthetiek", "behandeling"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },
    {
        "id": 60,
        "text": "KLINISCHE CASUS: Een 11-jarig meisje heeft klasse II malocclusie met mandibulaire retrognathie. Ouders willen weten wanneer behandeling moet starten. Hand-wrist radiograph toont MP3 capping stage. Menarche nog niet opgetreden. Dental development: late mixed dentition.\nVRAAG: Wat is de optimale timing voor functional appliance therapy?",
        "options": [
            "Start immediate treatment voor maximum growth modification",
            "Wacht tot pubertal growth spurt (MP3u stage)",
            "Begin treatment na menarche when growth slows",
            "Defer treatment tot permanent dentition",
            "Start treatment onafhankelijk van skeletal maturation"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Wacht tot pubertal growth spurt (MP3u stage)",
        "explanation": "Functional appliance therapy is meest effectief tijdens pubertal growth spurt. MP3u stage (uncapping MP3) indicates upcoming peak growth velocity. Pre-pubertal treatment (A) heeft limited skeletal effect. Post-menarche (C) mist growth peak. Waiting voor permanent dentition (D) mist growth potential. Growth stage (E) is crucial voor functional appliance success - timing is everything.",
        "category": "Groeiprognose - Timing orthodontie",
        "domain": "ORTHO",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["orthodontie", "groei", "timing", "malocclusie", "functioneel apparaat"],
        "created_at": "2025-07-21T16:09:00Z",
        "updated_at": "2025-07-21T16:09:00Z"
    },{
        "id": 61,
        "text": "KLINISCHE CASUS: Een Nederlandse gemeente overweegt waterfluoridatie (0.7ppm) na advies van GGD. Huidige fluoride exposure: tandpasta 1450ppm, lokaal drinkwater 0.1ppm. Epidemiologische data tonen DMFT index 1.8 bij 12-jarigen (EU gemiddelde 1.2). Bezorgde ouders vragen naar veiligheid en effectiviteit.\nVRAAG: Wat is de evidence-based aanbeveling voor waterfluoridatie in deze situatie?",
        "options": [
            "Waterfluoridatie implementeren - bewezen populatie benefit",
            "Afwijzen wegens adequate fluoride exposure via tandpasta",
            "Gerichte fluorideprogramma's voor hoogrisicogroepen",
            "Verhogen fluoride concentratie tandpasta naar 5000ppm",
            "Wachten op meer veiligheidsonderzoek fluoride"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Gerichte fluorideprogramma's voor hoogrisicogroepen",
        "explanation": "Bij adequate fluoride exposure via tandpasta maar higher than average cariës prevalentie zijn targeted programs voor hoogrisico groepen meest cost-effective. Waterfluoridatie (A) geeft beperkte additional benefit bij huidige fluoride levels. Complete afwijzing (B) negeert hogere DMFT. High-concentration tandpasta (D) is individuele, niet populatie maatregel. Veiligheidsonderzoek (E) is al extensively gedaan - fluoride is veilig bij aanbevolen levels.",
        "category": "Fluoride waterfluoridatie - Populatie effecten",
        "domain": "PREV",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["preventie", "fluoride", "waterfluoridatie", "volksgezondheid", "cariës"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 62,
        "text": "KLINISCHE CASUS: Een 7-jarig kind krijgt eruptie van eerste permanente molaren. Element 36 toont diepe fissuren met beginnende demineralisatie (geen cavitatie). Element 46 heeft oppervlakkige fissuren, geen demineralisatie. Kind heeft hoog cariësrisico (vorige cariës, veel snacks). Ouders vragen naar fissuurlak.\nVRAAG: Welke lakstrategie is evidence-based voor deze situatie?",
        "options": [
            "Fissuurlak beide molaren immediate na complete eruptie",
            "Alleen element 36 lakken wegens beginnende demineralisatie",
            "Afwachten tot alle permanente molaren geërupteerd zijn",
            "Fluoride varnish applicatie alleen, geen lak",
            "Preventive resin restoration op 36, sealing op 46"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Fissuurlak beide molaren immediate na complete eruptie",
        "explanation": "Bij hoogrisico kinderen zijn fissuurlakken geïndiceerd op alle molaren met retentieve fissuren immediate na complete eruptie, onafhankelijk van demineralisatie status. Early intervention voorkomt cariësontwikkeling. Selective sealing (B) mist prevention opportunity op element 46. Wachten (C) verhoogt cariësrisiko. Fluoride alleen (D) inadequaat bij deep fissures. PRR (E) te invasief zonder cavitatie.",
        "category": "Fissuurlak - Indicaties en timing",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["preventie", "fissuurlak", "cariës", "kinderen", "molaren"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 63,
        "text": "KLINISCHE CASUS: Een 35-jarige patiënt ontwikkelt frequent nieuwe cariës ondanks goede mondhygiëne en fluoride gebruik. Dieet anamnese toont: 6x koffie/dag met suiker, energie-drankjes tijdens sport (4x/week), fruit smoothies als lunch replacement. BMI normaal, geen diabetes.\nVRAAG: Welke dieet modificatie heeft hoogste impact op cariësrisico reductie?",
        "options": [
            "Elimineren van alle suikerhoudende producten compleet",
            "Beperken frequentie sugar exposure tot maaltijden",
            "Switchen naar artificële zoetstoffen in alle producten",
            "Verhogen calcium/fosfor intake voor remineralisatie",
            "Timing optimalisatie: spoelen na elke sugar exposure"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Beperken frequentie sugar exposure tot maaltijden",
        "explanation": "Frequentie van sugar exposure is belangrijker dan totale hoeveelheid voor cariësrisico. 6x koffie + sports drinks + smoothies = continuous acid challenges. Beperken tot maaltijden (3x/dag) geeft recovery time voor remineralization. Complete eliminatie (A) unrealistic en onnodige. Artificële zoetstoffen (C) helpen maar addressing frequency is fundamenteel. Calcium/fosfor (D) heeft minimale impact vs. frequency reduction. Spoelen (E) is adjuvant, niet primary intervention.",
        "category": "Dieetadvisering - Cariësrisicomanagement",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["preventie", "dieet", "cariësrisico", "suiker", "voeding"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 64,
        "text": "KLINISCHE CASUS: Een 60-jarige patiënt gebruikt medicatie voor hypertensie (ACE-remmer), depressie (SSRI), en allergieën (antihistamine). Ontwikkelt droge mond, frequent nieuwe cariës cervical areas. Unstimulated salivary flow 0.08 ml/min (normaal >0.1). Stimulated flow 0.4 ml/min (normaal >1.0).\nVRAAG: Welke speeksel-gerichte preventie strategie is meest effectief?",
        "options": [
            "Medicatie wijziging met prescribing physician",
            "Salivary substitutes en frequent sip water protocol",
            "Xylitol kauwgom 4x daags na maaltijden",
            "Pilocarpine prescriptie voor stimulating residual function",
            "Combination approach: stimulants + substitutes + topical fluoride"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Combination approach: stimulants + substitutes + topical fluoride",
        "explanation": "Medicatie-induced xerostomie vereist comprehensive management omdat simple interventions inadequaat zijn bij severe hyposalivation. Combination approach maximaliseert benefit: xylitol/cholinergic stimulants voor residual function, substitutes voor comfort, high-dose fluoride voor remineralization. Medicatie change (A) niet altijd mogelijk. Substitutes alleen (B) inadequaat. Xylitol alleen (C) insufficient bij severe xerostemie. Pilocarpine alleen (D) heeft limited efficacy bij medicatie-induced xerostemie.",
        "category": "Speeksel functie - Xerostomie management",
        "domain": "PREV",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["preventie", "speeksel", "xerostomie", "cariës", "medicatie"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 65,
        "text": "KLINISCHE CASUS: Een 28-jarige zwangere vrouw (12 weken gestatie) komt voor routine controle. Verhoogd bloedingsrisiko gingivaal, morning sickness eerste trimester, cravings voor zuur snoep. Vraagt naar veiligheid tandheelkundige behandeling en optimal oral care tijdens zwangerschap.\nVRAAG: Welke preventieve adviezen zijn evidence-based veilig en effectief?",
        "options": [
            "Uitstellen alle tandheelkundige behandeling tot na bevalling",
            "Intensive fluoride therapy en scaling tweede trimester",
            "Chloorhexidine spoeling eerste trimester voor gingivitis",
            "Calcium supplementatie voor maternal tooth loss prevention",
            "Natrium bicarbonaat spoeling na morning sickness episodes"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Natrium bicarbonaat spoeling na morning sickness episodes",
        "explanation": "Morning sickness veroorzaakt acid erosion - sodium bicarbonate spoeling neutraliseert acid en beschermt tandstructuur. Veilig tijdens gehele zwangerschap. Uitstellen behandeling (A) riskeert progressie naar ernstige infectie. Intensive fluoride/scaling (B) veilig maar sodium bicarbonate prioriteit bij morning sickness. CHX (C) veilig maar addressed niet primary risk factor. Calcium supplementatie (D) is myth - \"lose tooth per pregnancy\" is niet evidence-based.",
        "category": "Zwangerschap - Preventieve counseling",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.6,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["preventie", "zwangerschap", "gingivitis", "erosie", "mondhygiëne"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 66,
        "text": "KLINISCHE CASUS: Een scholengemeenschap ontwikkelt oral health screening program voor 6-12 jarigen. Budget beperkt, moet cost-effective zijn. Doel: early detection cariës en orthodontische problemen, referral criteria ontwikkelen. Verschillende screening modellen worden overwogen.\nVRAAG: Welk screening model biedt optimale cost-effectiveness voor schoolpopulatie?",
        "options": [
            "Annual comprehensive dental examination door tandartsen",
            "Bi-annual screening door trained dental hygienists",
            "Teacher-based visual inspection met referral criteria",
            "Parental questionnaire screening met risk assessment",
            "Targeted screening hoogrisico kinderen via socioeconomic factors"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Bi-annual screening door trained dental hygienists",
        "explanation": "Bi-annual screening door trained dental hygienists biedt optimale balans tussen accuracy en cost-effectiveness. Hygienists kunnen adequaat screen voor common problems, kosten minder dan tandartsen. Annual frequency (A) te duur bij brede populatie. Teacher-based (C) mist clinical expertise. Questionnaires (D) hebben poor specificity. Targeted screening (E) mist problems bij \"low-risk\" children en heeft equity issues.",
        "category": "Populatie screening - Vroege detectieprogramma's",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["preventie", "screening", "kinderen", "volksgezondheid", "cost-effective"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 67,
        "text": "KLINISCHE CASUS: Een 55-jarige patiënt met recidiverende gingivitis ondanks adequate mechanical cleaning vraagt naar antimicrobiële spoeling. Medische historie: controlled diabetes (HbA1c 7.1%), geen allergieën. Current oral hygiene: 2x daags tandenpoetsen, interdentaal dagelijks.\nVRAAG: Welk chlorhexidine protocol is evidence-based voor deze indicatie?",
        "options": [
            "Chlorhexidine 0.12% continuous gebruik als dagelijkse spoeling",
            "Chlorhexidine 0.2% intermittent protocol: 2 weken per maand",
            "Chlorhexidine 0.12% korte-termijn gebruik: 2-3 weken maximum",
            "Chlorhexidine gel 1% local applicatie in gingivale sulcus",
            "Combinatie chlorhexidine + fluoride spoeling permanent"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Chlorhexidine 0.12% korte-termijn gebruik: 2-3 weken maximum",
        "explanation": "Chlorhexidine 0.12% voor 2-3 weken is evidence-based voor gingivitis treatment zonder significant resistance ontwikkeling of taste alteration. Continuous gebruik (A) veroorzaakt taste problems en potential resistance. Intermittent protocol (B) heeft beperkte evidence base. High concentration gel (D) is voor specific applications. Combination products (E) kunnen interactions hebben en zijn niet standard recommendation.",
        "category": "Antimicrobiële preventie - Chloorhexidine protocollen",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["preventie", "gingivitis", "chloorhexidine", "mondhygiëne", "antibioticum"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 68,
        "text": "KLINISCHE CASUS: Een 25-jarige professionele zwemmer ontwikkelt dental erosion door chloorwater exposure (pool 6 dagen/week). Additionele factors: energie-drankjes tijdens training, gastro-oesophageal reflux. Erosie vooral palatinaal op bovenelementen. Vraagt naar preventieve maatregelen.\nVRAAG: Welke preventie strategie adresseert multiple erosie factoren effectief?",
        "options": [
            "Custom-made mouthguard tijdens zwemmen alleen",
            "Proton pump inhibitor voor GERD + fluoride spoeling",
            "Comprehensive approach: mouthguard + dietary modification + medical treatment",
            "Professional fluoride applications om de 3 maanden",
            "Calcium/casein supplementatie voor remineralization"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Comprehensive approach: mouthguard + dietary modification + medical treatment",
        "explanation": "Multiple erosie faktoren vereisen comprehensive benadering: custom mouthguard tegen chlorine exposure, dietary counseling voor energy drinks, medical management van GERD. Single interventions (A,B,D,E) addresseren niet alle causative faktoren. Erosie prevention success vereist elimination/reduction van alle acid sources plus protective measures. Piecemeal approach heeft suboptimaal resultaat bij multiple exposures.",
        "category": "Erosiepreventie - Zure blootstelling management",
        "domain": "PREV",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["preventie", "erosie", "zuur", "dieet", "mondbeschermer"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 69,
        "text": "KLINISCHE CASUS: Een 40-jarige patiënt met Sjögren's syndroom heeft zeer droge mond en ontwikkelt rapid caries progression ondanks hoge-concentratie tandpasta (5000ppm). Salivary flow severely compromised. Vraagt naar additional professional fluoride treatment options.\nVRAAG: Welk professional fluoride protocol is meest effectief voor deze extreme high-risk situatie?",
        "options": [
            "Fluoride varnish (22,600ppm) elke 3 maanden applicatie",
            "Geaciduleerde fosfaatfluoride gel quarterly treatments",
            "Zilverdiaminefluoride 38% voor caries arrest",
            "Combination: frequent varnish + take-home trays met gel",
            "In-office iontophoresis fluoride delivery systeem"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Combination: frequent varnish + take-home trays met gel",
        "explanation": "Extreme xerostomie vereist maximum fluoride exposure: frequent professional varnish (monthly/bi-monthly) + daily custom tray delivery. Combination maximaliseert fluoride availability. Quarterly applications (A,B) inadequaat bij severe xerostemie. SDF (C) is voor specific lesions, niet comprehensive prevention. Iontophoresis (E) heeft beperkte evidence en availability. Daily fluoride exposure via trays + frequent varnish geeft beste protection bij compromised saliva.",
        "category": "Professionele fluoride - Hoogrisicopatiënten",
        "domain": "PREV",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["preventie", "fluoride", "xerostomie", "cariës", "hoogrisico"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },
    {
        "id": 70,
        "text": "KLINISCHE CASUS: Een verzorgingshuis ontwikkelt oral care protocol voor 80 bewoners (gemiddeld 82 jaar, 60% dementie, 40% dysfagie). Staff heeft beperkte dental training. Veel bewoners hebben poor oral hygiene, frequent aspiration pneumonia. Budget beperkt voor externe dental services.\nVRAAG: Welk evidence-based protocol vermindert oral-systemic health complications effectief?",
        "options": [
            "Weekly professional dental hygienist visits voor alle bewoners",
            "Daily chlorhexidine swabs door nursing staff voor high-risk residents",
            "Comprehensive daily oral care training voor all nursing staff",
            "Bi-weekly dentist visits met emergency-only treatment",
            "Family-based oral care met training van relatives"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Comprehensive daily oral care training voor all nursing staff",
        "explanation": "Training nursing staff in daily oral care heeft grootste impact op oral-systemic complications bij elderly populations. Daily care door trained staff is cost-effective en sustainable. Studies tonen reduced pneumonia rates bij comprehensive staff training programs. Weekly hygienist (A) te duur en insufficient frequency. CHX swabs (B) inadequaat zonder mechanical cleaning. Bi-weekly dentist (D) is treatment, niet prevention-focused. Family-based care (E) is inconsistent en many residents hebben geen family involvement.",
        "category": "Preventie in instellingen - Ouderenzorg",
        "domain": "PREV",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["preventie", "ouderenzorg", "mondhygiëne", "systemisch", "training"],
        "created_at": "2025-07-21T16:10:07Z",
        "updated_at": "2025-07-21T16:10:07Z"
    },{
        "id": 71,
        "text": "KLINISCHE CASUS: Een tandarts uit Polen is recent naar Nederland verhuisd en heeft Nederlands diploma tandheelkunde behaald. Wil tandartspraktijk starten maar is onzeker over BIG-registratie vereisten. Geen Nederlandse taalcertificatie, wel sterke klinische ervaring (8 jaar EU praktijk). Vraagt naar stappen voor legale praktijkvoering.\nVRAAG: Welke BIG-registratie vereisten zijn verplicht voor tandheelkundige praktijkvoering in Nederland?",
        "options": [
            "Nederlands diploma alleen - geen andere vereisten nodig",
            "BIG-registratie + aantoonbare Nederlandse taalvaardigheid",
            "EU-diploma erkenning voldoende - BIG-registratie optioneel",
            "BIG-registratie + continue medical education credits",
            "Praktijkervaring 5 jaar + collegiale toetsing alleen"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "BIG-registratie + aantoonbare Nederlandse taalvaardigheid",
        "explanation": "Voor tandheelkundige praktijk in Nederland zijn verplicht: (1) BIG-registratie bij CIBG met erkend diploma, (2) adequate Nederlandse taalbeheersing voor patiëntcommunicatie en collega-overleg. Alleen diploma (A) is onvoldoende. EU-erkenning (C) vereist nog steeds BIG-registratie. CME (D) is professional responsibility maar geen registratievereiste. Ervaring alleen (E) vervangt geen formele registratievereisten. BIG-wet Artikel 3 vereist zowel registratie EN taalcompetentie.",
        "category": "BIG-registratie - Professionele vereisten",
        "domain": "ETHIEK",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.4,
            "discrimination": 1.9,
            "guessing": 0.16
        },
        "image_url": null,
        "tags": ["ethiek", "wetgeving", "BIG-registratie", "taalvaardigheid", "beroepsvereisten"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 72,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt heeft indicatie voor uitgebreide parodontale chirurgie met bone grafting. Behandeling heeft risico's: postoperatieve pijn, zwelling, mogelijk zenuwletsel (<1%), kans op mislukking (15%). Patiënt stelt veel vragen, lijkt angstig. Alternatief: extractie + implantaten (hogere kosten).\nVRAAG: Welke informed consent elementen zijn juridisch verplicht volgens Nederlandse wetgeving?",
        "options": [
            "Mondeling consent voldoende bij routine parodontale behandeling",
            "Procedure uitleg + major complications + alternatives + schriftelijk consent",
            "Risk disclosure alleen bij >10% complication rate",
            "General consent form van praktijk + patient signature",
            "Consent proces mag worden gedelegeerd aan assistente"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Procedure uitleg + major complications + alternatives + schriftelijk consent",
        "explanation": "WGBO Artikel 7:448 vereist informed consent met: (1) procedure uitleg, (2) major risks disclosure (ook <1% bij serious consequences), (3) alternatives discussion, (4) schriftelijk vastleggen bij complexe behandeling. Mondelinge consent (A) is inadequaat bij chirurgie. Risk threshold (C) is niet 10% - serious consequences zoals zenuwletsel moeten altijd disclosed. General forms (D) zijn insufficient - specific consent nodig. Delegation (E) is niet toegestaan - tandarts moet personally inform.",
        "category": "Informed consent - Complexe behandeling",
        "domain": "ETHIEK",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 2.0,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["ethiek", "wetgeving", "informed consent", "patiëntenrechten", "aansprakelijkheid"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 73,
        "text": "KLINISCHE CASUS: Een tandartspraktijk digitaliseert patient records en vraagt om GDPR compliance advies. Patiënten vragen naar data access rights. Practice manager stelt voor: cloud storage (EU server), automated appointment reminders via WhatsApp, patient photos voor treatment documentation, marketing via patient email database.\nVRAAG: Welke GDPR requirements zijn van toepassing op tandheelkundige praktijken?",
        "options": [
            "Medische data heeft exemption van GDPR requirements",
            "Patient explicit consent nodig voor alle data processing",
            "Data minimization + security measures + patient rights respect",
            "GDPR alleen van toepassing op praktijken >250 werknemers",
            "WhatsApp communicatie toegestaan zolang encryptie gebruikt wordt"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Data minimization + security measures + patient rights respect",
        "explanation": "GDPR Article 9 vereist voor medische data: data minimization (only collect what's necessary), appropriate security measures, patient rights (access, portability, erasure). Medical data geen exemption (A). Explicit consent (B) niet voor all processing - legitimate interest/vital interests kunnen legal basis zijn. Size threshold (D) incorrect - GDPR geldt voor alle medical practices. WhatsApp (E) is niet GDPR-compliant voor medical communication regardless of encryption.",
        "category": "Privacy wetgeving - AVG-compliance",
        "domain": "ETHIEK",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["ethiek", "privacy", "AVG", "GDPR", "gegevensbescherming"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 74,
        "text": "KLINISCHE CASUS: Tijdens wortelkanaalbehandeling breekt instrument af in kanaal element 46. Tandarts probeert removal maar slaagt niet. Informeert patiënt, verwijst naar endodontist. Patiënt ontwikkelt pijn en zwelling 2 weken later. Endodontist rapporteert: \"instrument removal zeer moeilijk, prognose onzeker\". Patiënt dreigt met klacht.\nVRAAG: Wat zijn de professional liability overwegingen in deze situatie?",
        "options": [
            "Instrument fractuur is always medical malpractice",
            "Adequate informed consent + appropriate referral = defensible care",
            "Malpractice alleen bij proven negligence in technique",
            "Professional liability insurance dekt alle instrument fractures",
            "Tandarts moet kosten van specialistische behandeling betalen"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Malpractice alleen bij proven negligence in technique",
        "explanation": "Professional liability vereist proven negligence - niet alle complications zijn malpractice. Instrument fracture is known complication (1-5%) bij endodontie. Key factors: (1) standard technique gebruikt, (2) appropriate response (inform + refer), (3) adequate consent over risks. Always malpractice (A) incorrect - complications ≠ negligence. Adequate consent/referral (B) helpt defense maar negligence assessment blijft relevant. Insurance coverage (D) depends on policy terms. Cost responsibility (E) determined by liability assessment, niet automatic.",
        "category": "Professionele aansprakelijkheid - Behandelfout",
        "domain": "ETHIEK",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["ethiek", "aansprakelijkheid", "wanpraktijk", "endodontie", "complicaties"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 75,
        "text": "KLINISCHE CASUS: Een 15-jarige komt alleen voor spoedeisende behandeling (gebroken element 11 na sport). Ouders zijn niet bereikbaar (buitenland). Adolescent is intelligent, begrijpt treatment, wenst esthetische restauratie. Behandeling kan wachten tot ouders terug zijn (3 dagen) maar patient heeft schoolactiviteiten.\nVRAAG: Wat zijn de legal requirements voor behandeling van minors zonder ouderlijke toestemming?",
        "options": [
            "Geen behandeling zonder schriftelijke ouderlijke toestemming",
            "Emergency treatment alleen - geen esthetische procedures",
            "Minor van 16+ kan independent consent geven voor medical treatment",
            "Tandarts kan behandelen als minor \"wilsbekwaam\" wordt geacht",
            "School principal kan consent geven voor student medical care"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Tandarts kan behandelen als minor \"wilsbekwaam\" wordt geacht",
        "explanation": "Nederlandse wet (WGBO Article 7:450) allows behandeling van minors <16 als zij \"wilsbekwaam\" zijn - capable of understanding nature, consequences, alternatives van treatment. 15-jarige die procedure begrijpt en consequences kan assess wordt beschouwd als competent. Absolute parental consent (A) incorrect voor wilsbekwame minors. Emergency only (B) te restrictief. 16+ automatic consent (C) incorrect age threshold. School consent (E) has geen legal basis.",
        "category": "Kinderen en toestemming - Toestemming minderjarigen",
        "domain": "ETHIEK",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["ethiek", "wetgeving", "kinderen", "toestemming", "minderjarigen", "wilsbekwaamheid"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 76,
        "text": "KLINISCHE CASUS: Een tandarts krijgt juridische request voor patient records van behandeling 8 jaar geleden. Practice administrator meldt dat oude paper records zijn \"opgeruimd\" na 5 jaar volgens oude practice policy. Digital records vanaf 3 jaar geleden wel beschikbaar. Legal counsel patiënt vraagt naar retention requirements.\nVRAAG: Wat zijn de wettelijke bewaartermijnen voor tandheelkundige dossiers in Nederland?",
        "options": [
            "5 jaar na laatste behandeling voor volwassen patiënten",
            "10 jaar na laatste behandeling, 15 jaar voor pediatrische patiënten",
            "15 jaar na laatste behandeling voor alle patiënten",
            "20 jaar na meerderjarigheid voor pediatrische patiënten",
            "Permanent bewaren - geen verjaringstermijn"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "20 jaar na meerderjarigheid voor pediatrische patiënten",
        "explanation": "WGBO Article 7:454 bepaalt: medical records bewaren 15 jaar na laatste behandeling, of 20 jaar na bereiken meerderjarigheid voor pediatrische patiënten (longest period applies). 5 jaar (A) te kort. 10/15 jaar (B) incorrect for pediatrics. 15 jaar flat (C) mist pediatric extension. Permanent retention (E) niet vereist. Records destruction na 5 jaar was non-compliant met legal requirements - practice riskeert legal consequences voor inadequate record keeping.",
        "category": "Documentatie vereisten - Dossierbeheer",
        "domain": "ETHIEK",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["ethiek", "wetgeving", "dossierbeheer", "bewaartermijn", "patiëntendossier"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 77,
        "text": "KLINISCHE CASUS: Tijdens weekend krijgt tandarts telefoon van unknown patient met severe dental pain en facial swelling. Patient meldt: \"other dentists niet bereikbaar, emergency room verwees naar tandarts\". Tandarts heeft geen relationship met patient, practice is gesloten, geen assistant beschikbaar.\nVRAAG: Wat is de ethical en legal duty of care in deze noodsituatie?",
        "options": [
            "Geen verplichting - patient is niet eigen patiënt",
            "Telephone advice alleen - geen legal obligation voor treatment",
            "Emergency assessment en treatment indien medically necessary",
            "Referral naar andere tandarts of emergency services",
            "Antibiotics prescription zonder examination"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Emergency assessment en treatment indien medically necessary",
        "explanation": "Professional duty of care (KNMT richtlijnen + BIG-wet) vereist emergency response bij acute dental infections met systemic signs. Facial swelling kan indicate serious infection requiring immediate assessment. Geen obligation (A) incorrect voor medical emergencies. Telephone only (B) inadequaat bij potential cellulitis. Referral (D) acceptable als adequate emergency services available maar direct assessment preferred. Antibiotics zonder exam (E) is substandard care en prescription violation.",
        "category": "Noodsituaties - Zorgplicht",
        "domain": "ETHIEK",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 2.0,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["ethiek", "zorgplicht", "noodsituatie", "spoed", "aansprakelijkheid"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 78,
        "text": "KLINISCHE CASUS: Een tandarts behandelt patiënt met diabetes en cardiovasculaire ziekte. Parodontale behandeling is gepland. Huisarts heeft different opinion over antibiotic prophylaxis necessity. Cardiologist adviseert endocarditis prophylaxis, but current guidelines suggest dit niet nodig is. Patiënt is confused door conflicting advice.\nVRAAG: Hoe moet interdisciplinaire communication conflict worden geresolved?",
        "options": [
            "Follow eigen professional judgment - ignore other specialists",
            "Defer alle decisions naar medical specialists",
            "Direct consultation tussen professionals + documented consensus",
            "Let patient choose between conflicting recommendations",
            "Follow most conservative approach regardless of guidelines"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Direct consultation tussen professionals + documented consensus",
        "explanation": "Professional collaboration (BIG-wet Article 35) vereist direct consultation tussen healthcare providers voor resolve conflicting recommendations en establish evidence-based consensus. Patient care optimaliseren door interprofessional communication. Own judgment only (A) inadequaat bij conflicts. Complete deferral (B) abandons dental expertise. Patient choice (D) inappropriate voor medical decisions beyond patient expertise. Blanket conservative approach (E) ignores evidence-based guidelines.",
        "category": "Interdisciplinaire samenwerking - Communicatievereisten",
        "domain": "ETHIEK",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["ethiek", "samenwerking", "communicatie", "interdisciplinair", "richtlijnen"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 79,
        "text": "KLINISCHE CASUS: Een tandartspraktijk implementeert quality assurance program. Plan includes: peer review van treatment outcomes, patient satisfaction surveys, clinical audit van high-risk procedures, reporting van near-miss events. Question arises over legal protection van quality improvement activities.\nVRAAG: Welke legal protections bestaan voor bona fide quality improvement activities?",
        "options": [
            "Alle QI activities hebben absolute legal immunity",
            "Peer review discussions zijn protected als educational activities",
            "QI data kunnen niet worden gebruikt in malpractice litigation",
            "Professional development activities hebben qualified privilege protection",
            "Geen legal protection - alle activities kunnen subpoenaed worden"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Professional development activities hebben qualified privilege protection",
        "explanation": "Nederlandse wet provides qualified privilege voor bona fide professional development en quality improvement activities. Protection niet absolute (A) - bad faith activities niet protected. Pure educational designation (B) insufficient - must be systematic QI. QI data protection (C) niet absolute - depends on specific circumstances. Qualified privilege (D) accurate - protection exists but has limitations. No protection (E) incorrect - legal framework recognizes QI importance.",
        "category": "Kwaliteitsborging - Peer review",
        "domain": "ETHIEK",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.7,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["ethiek", "kwaliteitsborging", "peer review", "wetgeving", "aansprakelijkheid"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },
    {
        "id": 80,
        "text": "KLINISCHE CASUS: Een 70-jarige patiënt met multiple comorbidities (diabetes, heart disease) weigert aanbevolen extractie van infected tooth. Begrijpt risico's van sepsis maar \"wil geen tanden meer verliezen\". Familie dringt aan op treatment. Patiënt is mentally competent maar emotionally distressed over tooth loss.\nVRAAG: Hoe moet dit ethical conflict tussen patient autonomy en medical beneficence worden geresolved?",
        "options": [
            "Respect patient autonomy - honor refusal van treatment",
            "Override autonomy wegens serious medical risk",
            "Family consent kunnen substitute voor patient refusal",
            "Psychiatric evaluation voor competency assessment",
            "Compromise treatment met less invasive approach"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Respect patient autonomy - honor refusal van treatment",
        "explanation": "Medical ethics principle van autonomy (KNMT ethische code) requires respecting competent patient decisions, even quando medically inadvisable. Patient understands consequences and makes informed decision. Override autonomy (B) alleen bij incompetence. Family substitution (C) inappropriate voor competent adult. Psychiatric evaluation (D) niet geïndiceerd - emotional distress ≠ incompetence. Compromise (E) kan offered maar patient kan still refuse.",
        "category": "Ethische dilemma's - Autonomie vs. weldoen",
        "domain": "ETHIEK",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["ethiek", "autonomie", "weldoen", "patiëntenrechten", "dilemma"],
        "created_at": "2025-07-21T16:11:47Z",
        "updated_at": "2025-07-21T16:11:47Z"
    },{
        "id": 81,
        "text": "KLINISCHE CASUS: Een 22-jarige patiënt meldt zich met pijn bij het openen van de mond en een knakkend geluid aan de rechterzijde van zijn kaak. Bij palpatie is er gevoeligheid in de preauriculaire regio. De tandarts vermoedt een probleem met het kaakgewricht.\nVRAAG: Welke anatomische structuren vormen het temporomandibulaire gewricht (TMJ)?",
        "options": [
            "De processus coronoideus van de mandibula en het os zygomaticum",
            "Het caput mandibulae en de fossa mandibularis van het os temporale",
            "De processus condylaris van de mandibula en het os sphenoideum",
            "Het alveolaire bot van de maxilla en de processus palatinus",
            "Het os hyoideum en de processus styloideus van het os temporale"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Het caput mandibulae en de fossa mandibularis van het os temporale",
        "explanation": "Het temporomandibulaire gewricht (TMJ) is een complex gewricht dat wordt gevormd door het caput mandibulae (gewrichtskop van de onderkaak) en de fossa mandibularis (glenoide fossa) van het os temporale (slaapbeen).",
        "category": "Temporomandibulair Gewricht (TMJ)",
        "domain": "ANATOMIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["anatomie", "TMJ", "kaakgewricht", "mandibula", "os temporale"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 82,
        "text": "KLINISCHE CASUS: Een tandarts plant een extractie van een geïmpacteerde verstandskies (element 48) en wil de lokale anesthesie effectief aanleggen. De tandarts moet de nervus alveolaris inferior blokkeren.\nVRAAG: Welke opening in het bot moet de tandarts benaderen om de nervus alveolaris inferior te verdoven?",
        "options": [
            "Foramen infraorbitale",
            "Foramen mentale",
            "Foramen ovale",
            "Foramen mandibulae",
            "Foramen rotundum"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Foramen mandibulae",
        "explanation": "De nervus alveolaris inferior (onderste alveolaire zenuw) treedt de mandibula binnen via het foramen mandibulae aan de mediale zijde van de ramus mandibulae. Dit is de primaire injectieplaats voor een mandibulaire block-anesthesie.",
        "category": "Nervus alveolaris inferior",
        "domain": "ANATOMIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["anatomie", "zenuwen", "anesthesie", "mandibula", "foramen"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 83,
        "text": "KLINISCHE CASUS: Bij het onderzoeken van de mondholte van een patiënt merkt de tandarts op dat de patiënt moeite heeft met het sluiten van de lippen en er is sprake van kwijlen. De tandarts vermoedt schade aan een zenuw die de spieren van de mond reguleert.\nVRAAG: Welke craniale zenuw innerveert voornamelijk de spieren van faciale expressie?",
        "options": [
            "Nervus trigeminus (V)",
            "Nervus facialis (VII)",
            "Nervus glossopharyngeus (IX)",
            "Nervus hypoglossus (XII)",
            "Nervus vagus (X)"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Nervus facialis (VII)",
        "explanation": "De nervus facialis (VII) is verantwoordelijk voor de innervatie van vrijwel alle spieren die betrokken zijn bij faciale expressie, inclusief de orbicularis oris die de lippen sluit.",
        "category": "Craniale zenuwen - Faciale expressie",
        "domain": "ANATOMIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["anatomie", "zenuwen", "facialis", "gezichtsspieren", "innervatie"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 84,
        "text": "KLINISCHE CASUS: Een tandarts overweegt een sinusliftprocedure voor implantaatplaatsing in de posterieure maxilla. Het is cruciaal om de anatomie van de sinus maxillaris goed te begrijpen.\nVRAAG: Welke botstructuren vormen de grenzen van de sinus maxillaris?",
        "options": [
            "Os nasale, os lacrimale, os ethmoidale",
            "Os zygomaticum, os palatinum, os maxilla",
            "Os frontale, os sphenoideum, os ethmoidale",
            "Os temporale, os parietale, os occipitale",
            "Os hyoideum, cartilago thyroidea, cartilago cricoidea"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Os zygomaticum, os palatinum, os maxilla",
        "explanation": "De sinus maxillaris (kaakholte) bevindt zich in de maxilla (bovenkaakbeen). De wanden worden ook gevormd door delen van het os zygomaticum (jukbeen) en het os palatinum (gehemeltebeen).",
        "category": "Sinus maxillaris",
        "domain": "ANATOMIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["anatomie", "sinus", "maxilla", "bot", "chirurgie"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 85,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met een acute infectie in de ondertanden. De tandarts moet de lymfeklieren van de submentale regio controleren om de verspreiding van de infectie te beoordelen.\nVRAAG: Welke lymfeklieren draineren voornamelijk de onderste incisivi, de punt van de tong en de onderlip?",
        "options": [
            "Submandibulaire lymfeklieren",
            "Cervicale diepe lymfeklieren",
            "Preauriculaire lymfeklieren",
            "Submentale lymfeklieren",
            "Occipitale lymfeklieren"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Submentale lymfeklieren",
        "explanation": "De submentale lymfeklieren bevinden zich onder de kin en draineren de lymfe van de onderste incisivi, de punt van de tong, de onderlip en de kin.",
        "category": "Lymfedrainage van het hoofd en de nek",
        "domain": "ANATOMIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["anatomie", "lymfeklieren", "infectie", "hoofd en nek", "diagnostiek"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 86,
        "text": "KLINISCHE CASUS: Tijdens een extractie van een bovenmolaar merkt de tandarts een kleine communicatie op tussen de alveolaire socket en de mond-neus holte. De tandarts moet de patiënt instrueren over het voorkomen van verdere complicaties.\nVRAAG: Welke anatomische structuur is waarschijnlijk geperforeerd bij een oro-antrale communicatie in de bovenkaak?",
        "options": [
            "Sinus frontalis",
            "Sinus sphenoidalis",
            "Canalis incisivus",
            "Sinus maxillaris",
            "Foramen palatinum majus"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Sinus maxillaris",
        "explanation": "De sinus maxillaris (kaakholte) ligt direct boven de wortels van de bovenmolaren en premolaren. Een oro-antrale communicatie (verbinding tussen mond en sinus) ontstaat vaak na extractie van deze tanden door perforatie van de sinusbodem.",
        "category": "Mond-neus holte anatomie",
        "domain": "ANATOMIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["anatomie", "sinus", "complicaties", "chirurgie", "extractie", "maxilla"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 87,
        "text": "KLINISCHE CASUS: Een patiënt heeft ernstige pijn in de ondermolaren na een vulling. De pijn straalt uit naar het oor. De tandarts vermoedt dat de pijn afkomstig is van een specifieke zenuw die ook de innervatie van het oorgebied verzorgt.\nVRAAG: Welke zenuw is primair verantwoordelijk voor de innervatie van de ondertanden en een deel van het oor?",
        "options": [
            "Nervus facialis (VII)",
            "Nervus glossopharyngeus (IX)",
            "Nervus mandibularis (V3 tak van de N. trigeminus)",
            "Nervus hypoglossus (XII)",
            "Nervus lingualis"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Nervus mandibularis (V3 tak van de N. trigeminus)",
        "explanation": "De nervus mandibularis (V3), een tak van de nervus trigeminus, innerveert de ondertanden (via de nervus alveolaris inferior) en heeft ook takken die het oor en de temporomandibulaire regio van sensibele innervatie voorzien. Pijn die uitstraalt naar het oor is een klassiek symptoom van aandoeningen in het mandibularisgebied.",
        "category": "Nervus trigeminus takken",
        "domain": "ANATOMIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["anatomie", "zenuwen", "trigeminus", "mandibula", "pijn", "innervatie"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 88,
        "text": "KLINISCHE CASUS: Een kind heeft moeite met kauwen en de tandarts constateert dat de palatale cuspen van de ondermolaren contact maken met de buccale cuspen van de bovenmolaren. De tandarts wil de occlusie en de functie van de kauwspieren beoordelen.\nVRAAG: Welke van de volgende spieren is GEEN primaire kauwspier (masticatiespier)?",
        "options": [
            "Musculus masseter",
            "Musculus temporalis",
            "Musculus pterygoideus medialis",
            "Musculus pterygoideus lateralis",
            "Musculus buccinator"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Musculus buccinator",
        "explanation": "De musculus buccinator is een spier van de faciale expressie die de wang vormt en helpt bij het verzamelen van voedsel tussen de tanden. De primaire kauwspieren zijn de masseter, temporalis, mediale pterygoideus en laterale pterygoideus.",
        "category": "Kauwspieren",
        "domain": "ANATOMIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["anatomie", "spieren", "kauwen", "masticatie", "mond"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 89,
        "text": "KLINISCHE CASUS: Een tandarts moet een infiltratieanesthesie aanleggen in de bovenkaak, anterior van de eerste premolaar. Het is belangrijk de zenuwbaan van de tanden in dit gebied te kennen.\nVRAAG: Welke zenuw innerveert de maxillaire incisivi en canini?",
        "options": [
            "Nervus alveolaris superior posterior",
            "Nervus alveolaris superior medialis",
            "Nervus nasopalatinus",
            "Nervus infraorbitalis (met takken n. alveolaris superior anterior)",
            "Nervus palatinus major"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Nervus infraorbitalis (met takken n. alveolaris superior anterior)",
        "explanation": "De maxillaire incisivi en canini worden geïnnerveerd door de nervus alveolaris superior anterior, die een tak is van de nervus infraorbitalis (die zelf een tak is van de nervus maxillaris, V2).",
        "category": "Nervus trigeminus takken - Maxilla",
        "domain": "ANATOMIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["anatomie", "zenuwen", "maxilla", "anesthesie", "innervatie"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },
    {
        "id": 90,
        "text": "KLINISCHE CASUS: Een patiënt heeft een diepe sublinguale abces die zich snel verspreidt. De tandarts moet alert zijn op de anatomische structuren in de sublinguale regio om verdere complicaties te voorkomen.\nVRAAG: Welke van de volgende structuren bevindt zich NIET in de sublinguale regio?",
        "options": [
            "Ductus submandibularis (Wharton's duct)",
            "Nervus lingualis",
            "Arteria lingualis",
            "Glandula parotidea",
            "Glandula sublingualis"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Glandula parotidea",
        "explanation": "De glandula parotidea (oorspeekselklier) bevindt zich lateraal van de ramus mandibulae, anterior van het oor, en draineert via de ductus parotideus (Stensen's duct) in de wang. Het is geen structuur van de sublinguale regio (onder de tong).",
        "category": "Sublinguale regio anatomie",
        "domain": "ANATOMIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["anatomie", "mondbodem", "speekselklieren", "zenuwen", "vasculatuur"],
        "created_at": "2025-07-21T17:24:25Z",
        "updated_at": "2025-07-21T17:24:25Z"
    },{
        "id": 91,
        "text": "KLINISCHE CASUS: Een 40-jarige patiënt meldt zich met extreme droge mond (xerostomie), vooral 's nachts. De patiënt gebruikt meerdere medicijnen die bekend staan om speekselreductie als bijwerking. Dit beïnvloedt de mondgezondheid aanzienlijk.\nVRAAG: Welke fysiologische functie van speeksel is het meest cruciaal voor de bescherming van tanden tegen cariës?",
        "options": [
            "De initiatie van koolhydraatvertering door amylase",
            "Het smeermiddel-effect om wrijving tussen zachte weefsels te verminderen",
            "De remineralisatiecapaciteit door de aanwezigheid van calcium en fosfaat",
            "De antimicrobiële werking door lysozym en lactoferrine",
            "De mechanische reiniging van tanden en weefsels"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "De remineralisatiecapaciteit door de aanwezigheid van calcium en fosfaat",
        "explanation": "De remineralisatiecapaciteit van speeksel, door de oververzadiging met calcium en fosfaat, is essentieel voor het herstel van beginnende glazuurlaesies en de bescherming tegen cariës. Hoewel alle genoemde functies belangrijk zijn, is remineralisatie direct gekoppeld aan tandstructuurbehoud.",
        "category": "Speekselfysiologie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["fysiologie", "speeksel", "cariës", "remineralisatie", "xerostomie"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 92,
        "text": "KLINISCHE CASUS: Een tandarts legt lokale anesthesie aan in de onderkaak. Om de pulpa van de molaren effectief te verdoven, moet de geleiding van zenuwimpulsen worden geblokkeerd.\nVRAAG: Welke ionenbeweging is primair verantwoordelijk voor de depolarisatie van een zenuwcel tijdens de overdracht van een impuls?",
        "options": [
            "Instroom van kaliumionen (K+)",
            "Uitstroom van natriumionen (Na+)",
            "Instroom van natriumionen (Na+)",
            "Uitstroom van chloride-ionen (Cl-)",
            "Instroom van calciumionen (Ca2+)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Instroom van natriumionen (Na+)",
        "explanation": "Lokale anesthetica werken door de natriumkanalen te blokkeren, waardoor de instroom van natriumionen in de zenuwcel wordt voorkomen. Deze instroom is essentieel voor depolarisatie en de generatie van een actiepotentiaal, wat leidt tot blokkering van de zenuwimpuls.",
        "category": "Zenuwfysiologie en Anesthesie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["fysiologie", "zenuwen", "anesthesie", "depolarisatie", "natriumkanalen"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 93,
        "text": "KLINISCHE CASUS: Een patiënt met ernstige parodontitis vertoont aanzienlijk botverlies rond de tanden. De tandarts wil begrijpen hoe het botmetabolisme bijdraagt aan de parodontale afbraak.\nVRAAG: Welke celtypen zijn primair verantwoordelijk voor de resorptie (afbraak) van botweefsel?",
        "options": [
            "Osteoblasten",
            "Osteocyten",
            "Fibroblasten",
            "Osteoclasten",
            "Chondrocyten"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Osteoclasten",
        "explanation": "Osteoclasten zijn gespecialiseerde cellen die verantwoordelijk zijn voor de resorptie van botweefsel. Ze scheiden enzymen en zuren af om de organische matrix en minerale componenten van het bot af te breken. Osteoblasten zijn verantwoordelijk voor botvorming.",
        "category": "Botfysiologie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["fysiologie", "bot", "parodontitis", "resorptie", "osteoclasten"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 94,
        "text": "KLINISCHE CASUS: Een patiënt klaagt over gevoeligheid voor koude dranken na het plaatsen van een diepe vulling. De tandarts wil de fysiologische respons van de pulpa op deze stimuli begrijpen.\nVRAAG: Welke theorie verklaart het best de pulpale pijnrespons op thermische en osmotische stimuli via vloeistofbeweging in de dentinetubuli?",
        "options": [
            "De Directe Stimulatietheorie",
            "De Neurala Stimulatietheorie",
            "De Hydrodynamische Theorie",
            "De Odontoblastische Transductietheorie",
            "De Vasculaire Compressietheorie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "De Hydrodynamische Theorie",
        "explanation": "De hydrodynamische theorie stelt dat pijnprikkels (zoals koud of zoet) leiden tot een snelle beweging van vloeistof binnen de dentinetubuli. Deze vloeistofbeweging stimuleert de zenuwuiteinden in de pulpa (A-delta vezels), wat leidt tot pijnperceptie.",
        "category": "Dentine-pulpa complex fysiologie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.8,
            "guessing": 0.22
        },
        "image_url": null,
        "tags": ["fysiologie", "pulpa", "dentine", "pijn", "gevoeligheid"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 95,
        "text": "KLINISCHE CASUS: Een patiënt moet een uitgebreide orale chirurgie ondergaan. De tandarts wil de effecten van stress op het immuunsysteem en de wondgenezing bij deze patiënt minimaliseren.\nVRAAG: Welke hormonen worden primair geassocieerd met de stressrespons en kunnen de wondgenezing nadelig beïnvloeden?",
        "options": [
            "Insuline en Glucagon",
            "Thyroxine en Calcitonine",
            "Cortisol en Adrenaline",
            "Oestrogeen en Testosteron",
            "Groei hormoon en Prolactine"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Cortisol en Adrenaline",
        "explanation": "Cortisol (een glucocorticoïd) en adrenaline (epinefrine) zijn de belangrijkste hormonen van de stressrespons. Langdurig verhoogde niveaus van cortisol kunnen het immuunsysteem onderdrukken en de wondgenezing vertragen, wat relevant is bij orale chirurgie.",
        "category": "Endocriene fysiologie - Stressrespons",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["fysiologie", "endocrinologie", "stress", "wondgenezing", "hormonen"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 96,
        "text": "KLINISCHE CASUS: Een tandarts observeert bij een patiënt ernstige tanderosie, mogelijk door frequente blootstelling aan zure dranken. De tandarts wil de patiënt adviseren over het behoud van de mond-pH.\nVRAAG: Welk speekselbufferingsysteem is het meest belangrijke fysiologische mechanisme voor het neutraliseren van zuren in de mond?",
        "options": [
            "De fosfaatbuffersysteem",
            "De proteïnebuffersysteem",
            "Het bicarbonaatbuffersysteem",
            "Het calciumbuffersysteem",
            "Het ureumbuffersysteem"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Het bicarbonaatbuffersysteem",
        "explanation": "Het bicarbonaatbuffersysteem (H2CO3/HCO3-) is het meest dominante en belangrijkste buffersysteem in speeksel. Het speelt een cruciale rol bij het neutraliseren van zuren die door bacteriën worden geproduceerd of uit voedsel en dranken afkomstig zijn, en helpt zo de pH in de mond te stabiliseren.",
        "category": "Speekselbufferende capaciteit",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["fysiologie", "speeksel", "pH", "erosie", "buffering"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 97,
        "text": "KLINISCHE CASUS: Een patiënt heeft diabetes mellitus type 1 en presenteert zich met frequente orale candidiasis en vertraagde wondgenezing na een tandheelkundige ingreep. De tandarts wil de relatie tussen diabetes en orale complicaties begrijpen.\nVRAAG: Welk van de volgende fysiologische effecten van ongecontroleerde diabetes draagt het meest bij aan verhoogde orale infecties en slechte wondgenezing?",
        "options": [
            "Verhoogde bloedplaatjesaggregatie",
            "Verminderde vasculaire permeabiliteit",
            "Gestoorde chemotaxis van neutrofielen",
            "Verhoogde insulineproductie",
            "Lagere bloeddruk"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Gestoorde chemotaxis van neutrofielen",
        "explanation": "Bij ongecontroleerde diabetes is er sprake van een gestoorde functie van immuuncellen, met name neutrofielen. Dit omvat verminderde chemotaxis (vermogen om naar een infectiehaard te migreren) en fagocytose, wat leidt tot een verhoogd risico op infecties en een vertraagde, minder efficiënte wondgenezing. Hyperglykemie draagt ook bij aan een omgeving die gunstig is voor micro-organismen.",
        "category": "Fysiologie van ziekten - Diabetes",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 3,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 2.0,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["fysiologie", "diabetes", "immuunsysteem", "infectie", "wondgenezing", "neutrofielen"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 98,
        "text": "KLINISCHE CASUS: Een tandarts behandelt een patiënt met bruxisme en wil de fysiologie van spiercontractie begrijpen om de effecten van nachtelijke tandenknarsen te verminderen.\nVRAAG: Welke neurotransmitter is primair verantwoordelijk voor de neuromusculaire transmissie bij skeletspieren, leidend tot spiercontractie?",
        "options": [
            "Dopamine",
            "Serotonine",
            "GABA (Gamma-aminoboterzuur)",
            "Acetylcholine",
            "Glutamaat"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Acetylcholine",
        "explanation": "Acetylcholine is de belangrijkste neurotransmitter bij de neuromusculaire junctie, waar zenuwimpulsen worden overgedragen naar skeletspiervezels, wat resulteert in spiercontractie. Dit is fundamenteel voor het begrip van kauwspieractiviteit.",
        "category": "Spierfysiologie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.6,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["fysiologie", "spieren", "neurotransmitter", "acetylcholine", "bruxisme"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 99,
        "text": "KLINISCHE CASUS: Een patiënt klaagt over een aanhoudende, doffe pijn in een endodontisch behandelde tand, zelfs na een succesvolle wortelkanaalbehandeling. De tandarts overweegt de rol van C-vezels in pijnperceptie.\nVRAAG: Welke van de volgende kenmerken is typisch voor pijn geleid door ongemyeliniseerde C-vezels in de pulpa?",
        "options": [
            "Scherpe, gelokaliseerde, kortdurende pijn",
            "Snelle geleiding van de impuls",
            "Doffe, zeurende, moeilijk te lokaliseren pijn",
            "Activering van A-delta vezels",
            "Respons op lage intensiteit stimuli"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Doffe, zeurende, moeilijk te lokaliseren pijn",
        "explanation": "C-vezels zijn ongemyeliniseerde zenuwvezels die langzamer impulsen geleiden en verantwoordelijk zijn voor de perceptie van doffe, zeurende, aanhoudende en moeilijk te lokaliseren pijn. A-delta vezels daarentegen geleiden sneller en zijn verantwoordelijk voor scherpe, gelokaliseerde pijn.",
        "category": "Pijnfysiologie",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["fysiologie", "pijn", "zenuwvezels", "pulpa", "endodontie"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },
    {
        "id": 100,
        "text": "KLINISCHE CASUS: Een patiënt ondergaat een tandheelkundige ingreep en ervaart plotseling een vasovagale syncope. De tandarts moet de fysiologische mechanismen achter deze reactie begrijpen om adequaat te reageren.\nVRAAG: Welk deel van het autonome zenuwstelsel is primair verantwoordelijk voor de symptomen van een vasovagale reactie (bradycardie en hypotensie)?",
        "options": [
            "Het sympathische zenuwstelsel",
            "Het enterische zenuwstelsel",
            "Het somatische zenuwstelsel",
            "Het parasympathische zenuwstelsel",
            "Het centrale zenuwstelsel"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Het parasympathische zenuwstelsel",
        "explanation": "Een vasovagale syncope wordt veroorzaakt door een overactiviteit van de nervus vagus, die deel uitmaakt van het parasympathische zenuwstelsel. Dit leidt tot bradycardie (vertraging van de hartslag) en hypotensie (daling van de bloeddruk), wat resulteert in verminderde hersenperfusie en bewustzijnsverlies.",
        "category": "Autonoom zenuwstelsel",
        "domain": "FYSIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["fysiologie", "zenuwstelsel", "autonoom", "vasovagaal", "syncope", "noodsituatie"],
        "created_at": "2025-07-21T17:26:31Z",
        "updated_at": "2025-07-21T17:26:31Z"
    },{
        "id": 101,
        "text": "KLINISCHE CASUS: Een 55-jarige man, zware roker, presenteert zich met een niet-genezende, pijnloze zweer op de laterale tongrand die al 3 maanden aanwezig is. Er is sprake van induratie bij palpatie.\nVRAAG: Wat is de meest waarschijnlijke pathologische diagnose voor deze laesie?",
        "options": [
            "Aft (Aphthous ulcer)",
            "Herpes simplex virus infectie",
            "Squameus celcarcinoom",
            "Traumatische ulcus",
            "Candidiasis"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Squameus celcarcinoom",
        "explanation": "Een niet-genezende, pijnloze zweer met induratie bij een zware roker, die langer dan 2-3 weken bestaat, is zeer verdacht voor een squameus celcarcinoom (mondkanker). Dit vereist onmiddellijke biopsie. De andere opties zijn minder waarschijnlijk gezien de anamnese en klinische presentatie.",
        "category": "Orale Pathologie - Maligniteit",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["pathologie", "diagnostiek", "oncologie", "mondkanker", "roken"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 102,
        "text": "KLINISCHE CASUS: Een 7-jarig kind presenteert zich met koorts, malaise en pijnlijke blaasjes en zweren in de mond, voornamelijk op de gingiva en het palatum. Er zijn ook huidlaesies rond de mond.\nVRAAG: Welke pathologische aandoening is de meest waarschijnlijke oorzaak van deze symptomen?",
        "options": [
            "Recidiverende afteuze stomatitis",
            "Primaire herpetische gingivostomatitis",
            "Hand-, voet- en mondziekte",
            "Waterpokken (Varicella)",
            "Erythema multiforme"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Primaire herpetische gingivostomatitis",
        "explanation": "Primaire herpetische gingivostomatitis, veroorzaakt door het Herpes Simplex Virus type 1 (HSV-1), manifesteert zich vaak bij jonge kinderen met koorts, malaise, uitgebreide pijnlijke blaasjes die overgaan in zweren op de gingiva, palatum, tong en periorale huid. Hand-, voet- en mondziekte (C) heeft typisch laesies op handen en voeten. Recidiverende afteuze stomatitis (A) heeft geen systemische symptomen en de laesies zijn anders van aard.",
        "category": "Virale infecties",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["pathologie", "infectie", "virus", "kinderen", "gingivostomatitis"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 103,
        "text": "KLINISCHE CASUS: Een patiënt met chronische parodontitis vertoont significant botverlies. De tandarts wil de cellulaire mechanismen begrijpen die leiden tot botresorptie in parodontale aandoeningen.\nVRAAG: Welke ontstekingsmediator, vaak verhoogd bij parodontitis, stimuleert direct de activiteit van osteoclasten, leidend tot botafbraak?",
        "options": [
            "Histamine",
            "Bradykinine",
            "Interleukine-1 (IL-1)",
            "Tumor Necrose Factor-alpha (TNF-α)",
            "Prostaglandine E2 (PGE2)"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Tumor Necrose Factor-alpha (TNF-α)",
        "explanation": "Tumor Necrose Factor-alpha (TNF-α) en Interleukine-1 (IL-1) zijn krachtige pro-inflammatoire cytokinen die een centrale rol spelen in de pathogenese van parodontitis. Ze stimuleren direct de differentiatie en activiteit van osteoclasten, wat leidt tot de afbraak van alveolair bot. Prostaglandine E2 (PGE2) draagt ook bij, maar TNF-α is een primaire osteoclast-stimulator.",
        "category": "Parodontale Pathogenese - Botresorptie",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["pathologie", "parodontitis", "botresorptie", "ontsteking", "cytokinen"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 104,
        "text": "KLINISCHE CASUS: Een patiënt klaagt over pijn en zwelling na een tandheelkundige ingreep. Bij onderzoek is er roodheid, warmte en functio laesa (verlies van functie). De tandarts wil de basisprincipes van ontsteking begrijpen.\nVRAAG: Welke van de volgende is GEEN van de klassieke tekenen van acute ontsteking?",
        "options": [
            "Rubor (roodheid)",
            "Tumor (zwelling)",
            "Calor (warmte)",
            "Functio laesa (verlies van functie)",
            "Cyanose (blauwe verkleuring)"
        ],
        "correct_answer_index": 4,
        "correct_answer_text": "Cyanose (blauwe verkleuring)",
        "explanation": "De vier klassieke tekenen van ontsteking, zoals beschreven door Celsus en later door Virchow uitgebreid, zijn: Rubor (roodheid), Tumor (zwelling), Calor (warmte) en Dolor (pijn). Functio laesa (verlies van functie) werd later toegevoegd. Cyanose is een teken van zuurstoftekort, niet van ontsteking.",
        "category": "Algemene Pathologie - Ontsteking",
        "domain": "PATHOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["pathologie", "ontsteking", "acute ontsteking", "tekenen", "diagnostiek"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 105,
        "text": "KLINISCHE CASUS: Bij een röntgenopname van de kaak detecteert de tandarts een radiolucentie (donkere plek) rond de apex van een non-vitale tand. Dit kan duiden op een periapicale ontsteking.\nVRAAG: Welke pathologische entiteit is een cyste-achtige laesie die ontstaat uit de resten van Malassez rond de apex van een non-vitale tand?",
        "options": [
            "Radiculaire cyste",
            "Folliculaire cyste",
            "Dento-alveolaire abces",
            "Keratocystische odontogene tumor",
            "Bot dysplasie"
        ],
        "correct_answer_index": 0,
        "correct_answer_text": "Radiculaire cyste",
        "explanation": "De radiculaire cyste (ook wel periapicale cyste genoemd) is de meest voorkomende odontogene cyste. Deze ontstaat als gevolg van ontsteking rond de apex van een non-vitale tand, waarbij de epitheliale resten van Malassez worden gestimuleerd tot proliferatie en cystevorming. Een dento-alveolair abces (C) is een acute purulente infectie zonder epitheliale bekleding.",
        "category": "Odontogene cysten",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["pathologie", "diagnostiek", "röntgenologie", "cyste", "endodontie", "periapicaal"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 106,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met multiple, diffuse, witte laesies op de buccale mucosa die niet afschraapbaar zijn. De laesies hebben een kant-achtig (lace-like) patroon.\nVRAAG: Welke pathologische aandoening komt het meest overeen met deze klinische presentatie?",
        "options": [
            "Orale candidiasis (spruw)",
            "Leukoplakie",
            "Erytroplakie",
            "Orale lichen planus",
            "Geografische tong"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Orale lichen planus",
        "explanation": "Orale lichen planus (OLP) is een chronische mucocutane aandoening die vaak reticulair (kant-achtig) witte laesies op de buccale mucosa veroorzaakt (Wickham's striae), die niet afschraapbaar zijn. Candidiasis (A) is meestal afschraapbaar. Leukoplakie (B) is een witte, niet-afschraapbare laesie, maar heeft niet typisch het kant-achtige patroon. Erytroplakie (C) is rood.",
        "category": "Orale Mucosa Afwijkingen",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["pathologie", "mondmucosa", "lichen planus", "diagnostiek", "witte laesies"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 107,
        "text": "KLINISCHE CASUS: Een patiënt klaagt over een 'knobbeltje' in de mondbodem dat fluctueert in grootte, vooral tijdens het eten. Bij onderzoek wordt een blauwachtige, doorschijnende zwelling gezien.\nVRAAG: Welke pathologische entiteit is het meest waarschijnlijk in de mondbodem met deze beschrijving?",
        "options": [
            "Fibroom",
            "Ranula",
            "Lipoom",
            "Sialoliet",
            "Mucocele"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Ranula",
        "explanation": "Een ranula is een slijmretentiecyste van de sublinguale speekselklier (of ductus submandibularis) die zich manifesteert als een blauwachtige, doorschijnende, fluctuerende zwelling in de mondbodem, vaak groter wordend tijdens het eten. Een mucocele (E) is vergelijkbaar maar komt vaker voor op de onderlip en is meestal kleiner.",
        "category": "Speekselklierpathologie",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["pathologie", "speekselklieren", "mondbodem", "cyste", "ranula"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 108,
        "text": "KLINISCHE CASUS: Bij een 10-jarig kind wordt bij een routine röntgenopname een circumscripte radiolucentie gezien rond de kroon van een nog niet-geërupteerde permanente tand. De laesie is asymptomatisch.\nVRAAG: Welke pathologische entiteit wordt gekenmerkt door een radiolucentie rond de kroon van een niet-geërupteerde tand en is vaak geassocieerd met de follikel van de tand?",
        "options": [
            "Radiculaire cyste",
            "Folliculaire cyste (Dentigerous cyst)",
            "Periapicale granuloom",
            "Laterale parodontale cyste",
            "Ameloblastoom"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Folliculaire cyste (Dentigerous cyst)",
        "explanation": "Een folliculaire cyste (dentigerous cyst) is een ontwikkelingscyste die ontstaat uit de follikel van een niet-geërupteerde of geïmpacteerde tand. Radiologisch presenteert het zich als een goed gedefinieerde radiolucentie die de kroon van de betrokken tand omgeeft. Het is de meest voorkomende ontwikkelingsodontogene cyste.",
        "category": "Ontwikkelingscysten",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["pathologie", "cysten", "röntgenologie", "ontwikkelingsstoornis", "impactie"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 109,
        "text": "KLINISCHE CASUS: Een patiënt, bekend met frequent zuur braken als gevolg van gastro-oesofageale refluxziekte (GERD), presenteert zich met uitgebreide erosie van de tanden, vooral aan de palatinale zijde van de bovenfronttanden. De tandarts wil de pathofysiologie hiervan begrijpen.\nVRAAG: Welke type glazuurverlies is primair het resultaat van chemische dissolutie zonder bacteriële betrokkenheid?",
        "options": [
            "Cariës",
            "Abrasie",
            "Attrition",
            "Erosie",
            "Abfractie"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Erosie",
        "explanation": "Erosie is het verlies van tandweefsel als gevolg van chemische processen die geen bacteriën omvatten, zoals blootstelling aan zuren uit voeding (citrusvruchten, frisdranken) of maagzuur (bij GERD, boulimia). Cariës (A) is bacterieel. Abrasie (B) is mechanisch verlies door externe objecten. Attritie (C) is mechanisch verlies door tand-op-tand contact. Abfractie (E) is verlies door occlusale krachten aan de cervicale regio.",
        "category": "Niet-cariëuze tandweefselverliezen",
        "domain": "PATHOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["pathologie", "erosie", "glazuurverlies", "GERD", "mondgezondheid"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },
    {
        "id": 110,
        "text": "KLINISCHE CASUS: Een patiënt ontwikkelt ernstige pijn en zwelling na een tandheelkundige ingreep. De pathologie-diagnose wijst op een cellulitis, een diffuse ontsteking die zich verspreidt door de weefselspleten.\nVRAAG: Welk van de volgende is het meest kenmerkend voor cellulitis, in tegenstelling tot een abces?",
        "options": [
            "Gelokaliseerde, scherp afgebakende purulente collectie",
            "Spontane drainage via een fistel",
            "Diffuse, verspreide ontsteking zonder puscollectie in een kapsel",
            "Aanwezigheid van necrose in het centrum",
            "Vereist altijd chirurgische drainage"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Diffuse, verspreide ontsteking zonder puscollectie in een kapsel",
        "explanation": "Cellulitis is een acute, diffuse ontsteking van het bindweefsel die zich snel verspreidt langs fascieplaten en weefselspleten, zonder de vorming van een gelokaliseerde puscollectie in een kapsel. Een abces (A) is daarentegen een gelokaliseerde collectie van pus, vaak omgeven door een fibreus kapsel. Abcessen kunnen spontaan draineren (B) en vereisen vaak chirurgische drainage (E), terwijl cellulitis initieel meestal met antibiotica wordt behandeld.",
        "category": "Infectie en ontsteking",
        "domain": "PATHOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["pathologie", "infectie", "ontsteking", "cellulitis", "abces", "diagnostiek"],
        "created_at": "2025-07-21T17:33:57Z",
        "updated_at": "2025-07-21T17:33:57Z"
    },{
        "id": 111,
        "text": "KLINISCHE CASUS: Een tandarts wil een diepe caviteit prepareren in een bovenmolaar en plant een lokale anesthesie. De patiënt heeft een medische geschiedenis van hypertensie die goed onder controle is. De tandarts overweegt het gebruik van een lokaal anestheticum met een vasoconstrictor.\nVRAAG: Welke vasoconstrictor wordt het meest gebruikt in lokale anesthetica in de tandheelkunde en met welk type receptor werkt deze primair?",
        "options": [
            "Felypressine - werkt primair op vasopressine (V1) receptoren",
            "Adrenaline (Epinefrine) - werkt primair op bèta-adrenerge receptoren",
            "Adrenaline (Epinefrine) - werkt primair op alfa-adrenerge receptoren",
            "Noradrenaline (Norepinefrine) - werkt primair op bèta-adrenerge receptoren",
            "Lidocaïne - werkt primair op natriumkanalen"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Adrenaline (Epinefrine) - werkt primair op alfa-adrenerge receptoren",
        "explanation": "Adrenaline (Epinefrine) is de meest gebruikte vasoconstrictor in tandheelkundige lokale anesthetica. Het werkt voornamelijk via alfa-1 adrenerge receptoren in de bloedvaten, wat leidt tot vasoconstrictie en daarmee de vertraging van de opname van het anestheticum, verlenging van de anesthesieduur en vermindering van bloedingen. Hoewel het ook op bèta-receptoren werkt, zijn de vasoconstrictieve effecten dominant via alfa-receptoren. Lidocaïne (E) is het anestheticum zelf, geen vasoconstrictor.",
        "category": "Lokale Anesthesie - Vasoconstrictoren",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["farmacologie", "anesthesie", "adrenaline", "vasoconstrictor", "receptoren"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 112,
        "text": "KLINISCHE CASUS: Een patiënt met een acute dento-alveolaire abces presenteert zich met uitgebreide zwelling en systemische tekenen van infectie (koorts, malaise). De tandarts heeft besloten antibiotica voor te schrijven voorafgaand aan chirurgische drainage.\nVRAAG: Welk antibioticum is de eerste keuze voor de behandeling van de meeste dento-alveolaire infecties, tenzij er sprake is van een allergie?",
        "options": [
            "Clindamycine",
            "Metronidazol",
            "Amoxicilline",
            "Azithromycine",
            "Ciprofloxacine"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Amoxicilline",
        "explanation": "Amoxicilline is het antibioticum van eerste keuze voor de meeste odontogene infecties, zoals dento-alveolaire abcessen, vanwege zijn brede spectrum tegen de meest voorkomende orale bacteriën (zowel aerobe als anaërobe) en gunstige farmacokinetiek. Clindamycine (A) is een alternatief bij penicilline-allergie. Metronidazol (B) wordt vaak gecombineerd met amoxicilline bij ernstige anaërobe infecties, maar is zelden monotherapie van eerste keuze.",
        "category": "Antibiotica - Odontogene Infecties",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["farmacologie", "antibiotica", "infectie", "abces", "amoxicilline"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 113,
        "text": "KLINISCHE CASUS: Een patiënt die langdurig orale anticoagulantia (bijv. vitamine K-antagonisten zoals acenocoumarol) gebruikt, moet een extractie ondergaan. De tandarts wil het risico op bloedingen minimaliseren.\nVRAAG: Welke testparameter wordt gebruikt om de effectiviteit van vitamine K-antagonisten te monitoren en is cruciaal voor de bloedingscontrole in de tandheelkunde?",
        "options": [
            "Geactiveerde partiële tromboplastinetijd (APTT)",
            "Trombocytentelling",
            "Internationale Genormaliseerde Ratio (INR)",
            "Bloedingstijd",
            "Protrombinetijd (PT)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Internationale Genormaliseerde Ratio (INR)",
        "explanation": "De INR (Internationale Genormaliseerde Ratio) is de gestandaardiseerde maat voor de protrombinetijd (PT) en wordt gebruikt om de therapeutische effectiviteit van vitamine K-antagonisten (zoals acenocoumarol of fenprocoumon) te monitoren. Een stabiele INR binnen het therapeutische bereik is cruciaal voor het veilig uitvoeren van tandheelkundige ingrepen bij patiënten die deze medicatie gebruiken.",
        "category": "Anticoagulantia - Monitoring",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["farmacologie", "anticoagulantia", "INR", "bloeding", "extractie"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 114,
        "text": "KLINISCHE CASUS: Een patiënt meldt zich met pijn die direct na een tandheelkundige behandeling is ontstaan. De tandarts wil een passend analgeticum voorschrijven voor milde tot matige pijn.\nVRAAG: Welk type analgeticum werkt primair door de synthese van prostaglandinen te remmen, en wordt vaak gebruikt als eerste keuze bij tandheelkundige pijn?",
        "options": [
            "Opioïden (bijv. morfine)",
            "Benzodiazepinen (bijv. diazepam)",
            "Paracetamol (acetaminofen)",
            "NSAID's (bijv. ibuprofen)",
            "Lokale anesthetica (bijv. lidocaïne)"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "NSAID's (bijv. ibuprofen)",
        "explanation": "NSAID's (Non-Steroidal Anti-inflammatory Drugs), zoals ibuprofen, werken door de enzymen cyclo-oxygenase (COX-1 en COX-2) te remmen, die verantwoordelijk zijn voor de synthese van prostaglandinen. Prostaglandinen spelen een centrale rol bij pijn, ontsteking en koorts, waardoor NSAID's zeer effectief zijn bij tandheelkundige pijn. Paracetamol (C) heeft een ander werkingsmechanisme, voornamelijk centraal.",
        "category": "Analgetica - Werkingsmechanisme",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["farmacologie", "pijn", "analgetica", "NSAID's", "ibuprofen"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 115,
        "text": "KLINISCHE CASUS: Een patiënt is allergisch voor penicilline en heeft een orale infectie die antibiotica vereist. De tandarts moet een veilig en effectief alternatief kiezen.\nVRAAG: Welk antibioticum is een veelvoorkomend alternatief voor penicilline bij orale infecties, vooral bij patiënten met een penicilline-allergie?",
        "options": [
            "Cephalexine",
            "Clindamycine",
            "Doxycycline",
            "Erytromycine",
            "Ciprofloxacine"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Clindamycine",
        "explanation": "Clindamycine is een veelgebruikt alternatief voor penicilline (inclusief amoxicilline) bij patiënten met een penicilline-allergie en is effectief tegen de meeste orale anaërobe bacteriën die odontogene infecties veroorzaken. Erytromycine (D) is ook een macrolide dat bij allergieën kan worden gebruikt, maar clindamycine heeft vaak een breder relevant spectrum voor ernstigere dentale infecties. Cephalexine (A) is een cefalosporine en kan kruisallergieën veroorzaken bij penicilline-allergieën.",
        "category": "Antibiotica - Alternatieven bij allergie",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["farmacologie", "antibiotica", "allergie", "penicilline", "clindamycine"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 116,
        "text": "KLINISCHE CASUS: Een tandarts overweegt sedatie met lachgas voor een angstige patiënt. Het is belangrijk om de farmacokinetiek van lachgas te begrijpen.\nVRAAG: Welke eigenschap van lachgas (N2O) draagt bij aan de snelle onset en recovery?",
        "options": [
            "Hoge bloed/gas partitiecoëfficiënt",
            "Lage bloed/gas partitiecoëfficiënt",
            "Het wordt uitgebreid gemetaboliseerd in de lever",
            "Het wordt actief getransporteerd over de bloed-hersenbarrière",
            "Hoge oplosbaarheid in lipiden"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Lage bloed/gas partitiecoëfficiënt",
        "explanation": "Lachgas heeft een lage bloed/gas partitiecoëfficiënt, wat betekent dat het slecht oplosbaar is in bloed. Hierdoor bereikt het snel evenwicht tussen de alveolaire lucht en het bloed, en vervolgens tussen het bloed en de hersenen, wat resulteert in een snelle onset (begin) van het effect. Omgekeerd wordt het ook snel uit het bloed verwijderd bij beëindiging van de toediening, wat leidt tot een snelle recovery (herstel).",
        "category": "Sedatie - Lachgas farmacologie",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["farmacologie", "lachgas", "sedatie", "farmacokinetiek", "anesthesie"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 117,
        "text": "KLINISCHE CASUS: Een patiënt met diabetes type 2 gebruikt metformine. De tandarts plant een complexe chirurgische ingreep en moet rekening houden met mogelijke medicatie-interacties of complicaties.\nVRAAG: Welk fysiologisch effect heeft metformine primair en waarom is dit relevant voor een tandheelkundige patiënt met diabetes?",
        "options": [
            "Verhoogt de insulineproductie door de pancreas - kan hypoglykemie veroorzaken",
            "Verhoogt de glucosereabsorptie in de nieren - kan hyperglykemie veroorzaken",
            "Vermindert de glucoseproductie door de lever en verbetert de insulinegevoeligheid - verlaagt het risico op hyperglykemie",
            "Stimuleert de afbraak van vetten voor energie - kan ketoacidose veroorzaken",
            "Verhoogt de opname van glucose door spiercellen onafhankelijk van insuline - geen direct risico op fluctuaties"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Vermindert de glucoseproductie door de lever en verbetert de insulinegevoeligheid - verlaagt het risico op hyperglykemie",
        "explanation": "Metformine werkt primair door de glucoseproductie door de lever te verminderen (gluconeogenese) en door de insulinegevoeligheid in perifere weefsels (spieren, vetweefsel) te verbeteren. Dit verlaagt het bloedglucosegehalte en is gunstig voor patiënten met diabetes type 2. Het risico op hypoglykemie (lage bloedsuiker) is minimaal bij monotherapie met metformine, maar de algehele bloedglucosecontrole is essentieel voor een goede wondgenezing en infectiepreventie na tandheelkundige ingrepen.",
        "category": "Medicatie - Diabetes",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["farmacologie", "diabetes", "medicatie", "metformine", "bloedsuiker"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 118,
        "text": "KLINISCHE CASUS: Een patiënt met astma gebruikt een inhalator met salbutamol (een bèta-2-agonist). De tandarts moet rekening houden met mogelijke interacties of bijwerkingen tijdens de tandheelkundige behandeling.\nVRAAG: Welk van de volgende bijwerkingen kan direct worden geassocieerd met systemische absorptie van een bèta-2-agonist zoals salbutamol?",
        "options": [
            "Bradycardie",
            "Bronchoconstrictie",
            "Hypertensie",
            "Tachycardie en tremoren",
            "Hypoglykemie"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Tachycardie en tremoren",
        "explanation": "Salbutamol is een selectieve bèta-2-agonist die primair de luchtwegen verwijdt. Bij systemische absorptie kan het echter ook bèta-1-receptoren in het hart stimuleren, wat leidt tot tachycardie (versnelde hartslag), en bèta-2-receptoren in skeletspieren, wat tremoren kan veroorzaken. Dit zijn veelvoorkomende bijwerkingen, zelfs bij inhalatiegebruik, vooral bij hogere doses of gevoelige patiënten. Bradycardie (A) is een vertraagde hartslag, bronchoconstrictie (B) is het tegenovergestelde van het gewenste effect, en hypertensie (C) is niet direct het primaire effect.",
        "category": "Medicatie - Ademhalingsaandoeningen",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["farmacologie", "medicatie", "astma", "salbutamol", "bijwerkingen"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 119,
        "text": "KLINISCHE CASUS: Een tandarts wil de pijn en ontsteking na een uitgebreide extractie beheersen. Naast systemische analgetica overweegt de tandarts ook lokale middelen.\nVRAAG: Welk topisch medicament kan worden gebruikt om acute pijn en ontsteking van de mondslijmvliezen lokaal te verlichten na een trauma of chirurgische ingreep?",
        "options": [
            "Topisch fluoridegel",
            "Chloorhexidine mondspoeling",
            "Benzydamine hydrochloride mondspoeling",
            "Lidocaïne topische oplossing",
            "Dexamethason mondspoeling"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Benzydamine hydrochloride mondspoeling",
        "explanation": "Benzydamine hydrochloride is een NSAID met lokale anesthetische en ontstekingsremmende eigenschappen, vaak gebruikt als mondspoeling voor de verlichting van pijn en ontsteking van het mondslijmvlies na chirurgische ingrepen, trauma, of bij mucositis. Chloorhexidine (B) is primair antimicrobieel. Lidocaïne (D) is een anestheticum voor oppervlakkige verdoving, maar heeft geen ontstekingsremmende werking.",
        "category": "Lokale Medicatie - Pijn en Ontsteking",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["farmacologie", "topisch", "pijn", "ontsteking", "mondspoeling", "extractie"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 120,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met een allergische reactie na toediening van een lokaal anestheticum. Symptomen zijn onder andere urticaria en bronchospasmen. De tandarts moet snel en adequaat reageren.\nVRAAG: Welke medicatie is de eerste en meest cruciale behandeling voor een acute anafylactische reactie in de tandartspraktijk?",
        "options": [
            "Diazepam (IV)",
            "Hydrocortison (IV)",
            "Adrenaline (Epinefrine) (IM)",
            "Difenhydramine (IM)",
            "Salbutamol (inhalatie)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Adrenaline (Epinefrine) (IM)",
        "explanation": "Adrenaline (Epinefrine) intramusculair (IM) is de eerste en meest cruciale behandeling voor een acute anafylactische reactie. Het heeft krachtige alfa- en bèta-agonistische effecten die bronchospasmen tegengaan, bloeddruk verhogen en de zwelling verminderen. De andere middelen (hydrocortison, difenhydramine) zijn aanvullend en werken langzamer; salbutamol helpt alleen bij bronchospasmen.",
        "category": "Noodgevallen - Anafylaxie",
        "domain": "FARMACOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 2.0,
            "guessing": 0.16
        },
        "image_url": null,
        "tags": ["farmacologie", "noodgeval", "allergie", "anafylaxie", "adrenaline", "behandeling"],
        "created_at": "2025-07-21T17:39:04Z",
        "updated_at": "2025-07-21T17:39:04Z"
    },
    {
        "id": 121,
        "text": "KLINISCHE CASUS: Een 35-jarige patiënt presenteert zich met onverklaarbare pijn in de linker ondermolaarregio. Klinisch onderzoek is niet-conclusief, maar de tandarts vermoedt een periapicale pathologie. De tandarts wil de meest geschikte intraorale röntgenopname maken om de apicale regio van de molaar te beoordelen.\nVRAAG: Welke intraorale röntgenopname is het meest geschikt om de volledige tandlengte, inclusief de apex en het periapicale bot, van een ondermolaar gedetailleerd af te beelden?",
        "options": [
            "Bitewing-opname",
            "Occlusale opname",
            "Periapicale opname",
            "Panoramische opname (OPT)",
            "Cephalometrische opname"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Periapicale opname",
        "explanation": "Een periapicale opname is specifiek ontworpen om de gehele tandlengte, inclusief de kroon, wortel en het omliggende periapicale bot, gedetailleerd af te beelden. Dit is essentieel voor het diagnosticeren van periapicale laesies, wortelfracturen of endodontische problemen. Bitewing (A) is voor interproximale cariës en botniveau. Occlusale (B) is voor grotere gebieden van de kaak. Panoramisch (D) en cephalometrisch (E) zijn extraorale opnames die minder detail tonen voor individuele tanden.",
        "category": "Intraorale Radiografie - Technieken",
        "domain": "RADIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["radiologie", "diagnostiek", "röntgen", "periapicaal", "ondermolaar"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 122,
        "text": "KLINISCHE CASUS: Een 50-jarige patiënt presenteert zich met pijn en zwelling in de rechter kaakhoek, mogelijk gerelateerd aan een geïmpacteerde verstandskies (element 48). De tandarts wil een breed overzicht van de kaak, inclusief het kaakgewricht en de omliggende structuren.\nVRAAG: Welke extraorale röntgenopname biedt een panoramisch overzicht van de boven- en onderkaak, tanden, kaakgewrichten en omliggende structuren?",
        "options": [
            "Periapicale opname",
            "Bitewing-opname",
            "Panoramische opname (Orthopantomogram - OPT)",
            "Cephalometrische opname",
            "CT-scan"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Panoramische opname (Orthopantomogram - OPT)",
        "explanation": "Een panoramische opname (OPT of OPG) is een extraorale röntgentechniek die een breed overzicht biedt van beide kaken, alle tanden (geërupteerd en niet-geërupteerd), de kaakgewrichten, de maxillaire sinussen en een deel van de neusregio. Het is ideaal voor het beoordelen van geïmpacteerde tanden, algemene parodontale status en pathologieën over een groter gebied.",
        "category": "Extraorale Radiografie - Technieken",
        "domain": "RADIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["radiologie", "diagnostiek", "panoramisch", "OPT", "kaak", "geïmpacteerd"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 123,
        "text": "KLINISCHE CASUS: Een tandarts vermoedt een verticale wortelfractuur bij een endodontisch behandelde tand, maar dit is niet duidelijk zichtbaar op conventionele 2D röntgenopnames. De patiënt heeft aanhoudende pijn.\nVRAAG: Welke geavanceerde beeldvormingstechniek biedt driedimensionale beelden met hoge resolutie, ideaal voor het detecteren van subtiele fracturen, botdefecten en de relatie met anatomische structuren zoals zenuwkanalen en sinussen?",
        "options": [
            "Periapicale opname",
            "Bitewing-opname",
            "Cephalometrische opname",
            "Conische Bundel Computertomografie (CBCT)",
            "Magnetische Resonantie Beeldvorming (MRI)"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Conische Bundel Computertomografie (CBCT)",
        "explanation": "CBCT (Cone Beam Computed Tomography) is een 3D-beeldvormingstechniek die superieure detail en diagnostische waarde biedt in vergelijking met 2D-röntgenopnames voor complexe situaties. Het is uitermate geschikt voor het opsporen van verticale wortelfracturen, het beoordelen van wortelkanaalanatomie, botdefecten en de relatie met vitale structuren met een relatief lage stralingsdosis vergeleken met medische CT.",
        "category": "3D Beeldvorming - CBCT",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["radiologie", "diagnostiek", "CBCT", "3D", "fractuur", "endodontie"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 124,
        "text": "KLINISCHE CASUS: Een tandarts maakt intraorale röntgenopnames. Het is cruciaal om de stralingsdosis voor de patiënt zo laag mogelijk te houden volgens het ALARA-principe.\nVRAAG: Welke maatregel is het meest effectief in het reduceren van de stralingsdosis voor de patiënt tijdens röntgenopnames in de tandheelkunde?",
        "options": [
            "Het gebruik van D-speed film",
            "Een lange conus gebruiken (parallelliserende techniek)",
            "Het verhogen van de kilovoltage (kVp)",
            "Het gebruik van een loden schort bij alle opnames",
            "Het verlagen van de milliampere (mA)"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Een lange conus gebruiken (parallelliserende techniek)",
        "explanation": "Het gebruik van een lange conus (en de parallelliserende techniek) leidt tot minder divergentie van de röntgenbundel en dus minder strooistraling, wat resulteert in een lagere dosis voor de patiënt en een betere beeldkwaliteit. Het gebruik van D-speed film (A) is verouderd; F-speed film of digitale sensoren zijn beter. Het verhogen van de kVp (C) kan de dosis verminderen bij behoud van beeldkwaliteit, maar de lange conus is directer effectief voor dosisreductie in de praktijk. Een loden schort (D) beschermt, maar reduceert de dosis op het te fotograferen gebied niet. Het verlagen van de mA (E) vermindert de stralingsintensiteit, maar moet in balans zijn met de belichtingstijd.",
        "category": "Stralingshygiëne en -bescherming",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.21
        },
        "image_url": null,
        "tags": ["radiologie", "straling", "veiligheid", "ALARA", "röntgen"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 125,
        "text": "KLINISCHE CASUS: Een tandarts beoordeelt een panoramische röntgenopname en ziet een radiolucente laesie in de onderkaak die de wortels van meerdere tanden omvat. Het is cruciaal om te bepalen of de laesie geassocieerd is met de tanden of van non-odontogene oorsprong is.\nVRAAG: Welk radiografisch kenmerk suggereert het meest een maligne (kwaadaardige) laesie in het kaakbot?",
        "options": [
            "Scherp afgebakende, sclerotische rand",
            "Corticale doorbreking en onregelmatige, spiculated botranden",
            "Verplaatsing van tanden zonder resorptie",
            "Een uniforme radiodensiteit",
            "Aanwezigheid van een smalle, radiodense lijn rond de laesie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Corticale doorbreking en onregelmatige, spiculated botranden",
        "explanation": "Maligne laesies in het bot zijn vaak infiltratief en groeien snel, wat resulteert in onregelmatige, onscherpe en spiculated (stekelachtige) botranden ('sunburst' of 'onion-skin' patroon). Corticale doorbreking (erosie van het bot aan de buitenzijde) is ook een sterk teken van maligniteit. Goed afgebakende, sclerotische randen (A) en uniforme densiteit (D, E) duiden meer op benigne laesies. Verplaatsing van tanden zonder resorptie (C) is ook vaker geassocieerd met benigne, langzaam groeiende laesies zoals cysten.",
        "category": "Radiografische interpretatie - Botlaesies",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["radiologie", "diagnostiek", "botlaesies", "maligniteit", "röntgeninterpretatie"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 126,
        "text": "KLINISCHE CASUS: Een tandarts onderzoekt een patiënt met een vermoedelijke cariëslaesie op een proximale vlak van een molaar. Klinisch is de laesie moeilijk te zien. De tandarts wil een röntgenopname maken om de diagnose te bevestigen en de diepte van de laesie te beoordelen.\nVRAAG: Welke intraorale röntgenopname is het meest geschikt voor het detecteren van interproximale cariës en het beoordelen van het alveolaire botniveau?",
        "options": [
            "Periapicale opname",
            "Bitewing-opname",
            "Occlusale opname",
            "Panoramische opname (OPT)",
            "Cephalometrische opname"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Bitewing-opname",
        "explanation": "De bitewing-opname is specifiek ontworpen om de kronen van zowel de boven- als ondertanden in één opname af te beelden, met een lage stralingsdosis. Het is de meest gevoelige en geschikte techniek voor het detecteren van interproximale (tussen de tanden gelegen) cariëslaesies en het beoordelen van het botniveau bij parodontitis.",
        "category": "Intraorale Radiografie - Technieken",
        "domain": "RADIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.5,
            "discrimination": 1.6,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["radiologie", "diagnostiek", "cariës", "bitewing", "röntgen"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 127,
        "text": "KLINISCHE CASUS: Een tandarts is van plan implantaten te plaatsen in de onderkaak en moet de exacte locatie en het verloop van de nervus alveolaris inferior bepalen om zenuwschade te voorkomen.\nVRAAG: Welke röntgenopname is het meest nauwkeurig in het visualiseren van de nervus alveolaris inferior in 3D en het meten van de beschikbare bothoogte en breedte voor implantaatplaatsing?",
        "options": [
            "Panoramische opname (OPT)",
            "Periapicale opname",
            "Conische Bundel Computertomografie (CBCT)",
            "Transcraniale röntgenopname",
            "Occlusale opname"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Conische Bundel Computertomografie (CBCT)",
        "explanation": "CBCT biedt driedimensionale beelden met hoge resolutie, wat essentieel is voor pre-implantologische planning. Het maakt nauwkeurige metingen van botdimensies mogelijk en de precieze lokalisatie van vitale structuren zoals de nervus alveolaris inferior, waardoor het risico op zenuwschade tijdens implantaatplaatsing aanzienlijk wordt verminderd. Hoewel een OPT (A) een overzicht geeft, is het een 2D-opname met superpositie en minder nauwkeurigheid voor complexe implantaatplanning.",
        "category": "3D Beeldvorming - Implantaatplanning",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["radiologie", "implantologie", "CBCT", "zenuwen", "bot"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 128,
        "text": "KLINISCHE CASUS: Een patiënt heeft recent meerdere röntgenopnames gehad voor een complexe tandheelkundige behandeling. De patiënt maakt zich zorgen over de totale stralingsdosis. De tandarts legt uit dat de dosis wordt uitgedrukt in specifieke eenheden.\nVRAAG: Welke eenheid wordt meestal gebruikt om de effectieve stralingsdosis bij patiënten in de radiologie uit te drukken, rekening houdend met de gevoeligheid van verschillende weefsels voor straling?",
        "options": [
            "Gray (Gy)",
            "Sievert (Sv)",
            "Becquerel (Bq)",
            "Roentgen (R)",
            "Curie (Ci)"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Sievert (Sv)",
        "explanation": "De effectieve dosis, die het biologische risico van straling op de mens uitdrukt en rekening houdt met de gevoeligheid van verschillende organen en weefsels, wordt uitgedrukt in Sievert (Sv). Gray (Gy) is de eenheid voor de geabsorbeerde dosis (energie per massa). Becquerel (Bq) en Curie (Ci) zijn eenheden van radioactiviteit. Roentgen (R) is een oudere eenheid voor blootstelling aan straling.",
        "category": "Stralingsdosis - Eenheden",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["radiologie", "straling", "Sievert", "dosis", "veiligheid"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 129,
        "text": "KLINISCHE CASUS: Bij het beoordelen van röntgenopnames ziet de tandarts een 'ghost image' op een panoramische opname van een patiënt. Dit is een veelvoorkomend artefact.\nVRAAG: Welke van de volgende structuren veroorzaakt het meest frequent een 'ghost image' op een panoramische röntgenopname als gevolg van incorrecte positionering of het niet verwijderen van objecten?",
        "options": [
            "De cervicale wervelkolom",
            "Het foramen mentale",
            "De schaduw van de epiglottis",
            "Oorbellen of andere metalen objecten in het hoofd-halsgebied",
            "De nasolabiale plooi"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Oorbellen of andere metalen objecten in het hoofd-halsgebied",
        "explanation": "Een 'ghost image' (spookbeeld) op een panoramische röntgenopname is een artefact dat ontstaat wanneer een object zich buiten het focale vlak bevindt en het röntgenpad tweemaal kruist. Metalen objecten, zoals oorbellen, brillen, haarspelden of uitneembare prothesen, zijn de meest voorkomende oorzaken van dergelijke schaduwbeelden, die wazig, vergroot en aan de contralaterale zijde van het werkelijke object verschijnen.",
        "category": "Radiografische artefacten - Panoramisch",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["radiologie", "artefacten", "panoramisch", "röntgen", "diagnostiek"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },
    {
        "id": 130,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met een trauma aan de bovenkaak. De tandarts vermoedt een fractuur van de maxilla en wil de omvang van de schade beoordelen.\nVRAAG: Welke röntgenopname is het meest geschikt om een laterale verschuiving van de kaak, fracturen van de maxilla of mandibula, of dislocatie van het kaakgewricht te beoordelen in het geval van trauma?",
        "options": [
            "Bitewing-opname",
            "Periapicale opname",
            "Panoramische opname (OPT)",
            "Reverse Towne projectie",
            "Waters' projectie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Panoramische opname (OPT)",
        "explanation": "Hoewel een CT-scan (CBCT) de gouden standaard is voor complexe aangezichtsfracturen, is een panoramische opname (OPT) vaak de eerste keuze voor een algemene beoordeling bij trauma van de kaak. Het biedt een breed beeld van de gehele mandibula en maxilla, en kan helpen bij het detecteren van fracturen, dislocaties en de algemene relatie van de botstructuren. Specifieke projecties zoals Reverse Towne (D) zijn beter voor condyl fracturen en Waters' (E) voor sinussen, maar OPT geeft een algemeen overzicht.",
        "category": "Radiografie bij Trauma",
        "domain": "RADIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["radiologie", "trauma", "diagnostiek", "kaakfractuur", "panoramisch"],
        "created_at": "2025-07-21T17:40:00Z",
        "updated_at": "2025-07-21T17:40:00Z"
    },{
        "id": 131,
        "text": "KLINISCHE CASUS: Een patiënt met uitgebreide cariëslaesies wordt behandeld. De tandarts wil de microbiologische factoren begrijpen die primair verantwoordelijk zijn voor het initiëren van glazuurcariës.\nVRAAG: Welke bacteriesoort wordt primair geassocieerd met de initiatie en progressie van glazuurcariës door de productie van zuren uit fermenteerbare koolhydraten?",
        "options": [
            "Porphyromonas gingivalis",
            "Actinomyces israelii",
            "Streptococcus mutans",
            "Lactobacillus casei",
            "Treponema denticola"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Streptococcus mutans",
        "explanation": "Streptococcus mutans is de meest bekende en best bestudeerde bacterie die primair geassocieerd wordt met de initiatie van glazuurcariës. Het heeft het vermogen om suikers te metaboliseren tot zuren (acidogeen) en kan overleven in een zure omgeving (acidofiel), wat leidt tot demineralisatie van glazuur. Hoewel Lactobacillus (D) een rol speelt bij de progressie van cariës, is S. mutans de initiële factor.",
        "category": "Cariës Microbiologie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["microbiologie", "cariës", "bacteriën", "Streptococcus mutans", "glazuur"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 132,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met ernstige, necrotiserende parodontitis (NUG/NUP). De tandarts wil de microbiologische samenstelling van deze agressieve vorm van parodontitis begrijpen.\nVRAAG: Welke groep bacteriën, vaak aangeduid als 'rood complex', wordt sterk geassocieerd met chronische en agressieve parodontitis?",
        "options": [
            "Streptococcus sanguinis, Actinomyces viscosus, Veillonella parvula",
            "Aggregatibacter actinomycetemcomitans, Capnocytophaga spp., Eikenella corrodens",
            "Porphyromonas gingivalis, Tannerella forsythia, Treponema denticola",
            "Fusobacterium nucleatum, Prevotella intermedia, Campylobacter rectus",
            "Lactobacillus acidophilus, Streptococcus mutans, Bifidobacterium spp."
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Porphyromonas gingivalis, Tannerella forsythia, Treponema denticola",
        "explanation": "Het 'rode complex' is een groep van drie anaërobe bacteriën (Porphyromonas gingivalis, Tannerella forsythia en Treponema denticola) die sterk geassocieerd worden met de ernst van parodontitis en vaak in hogere aantallen aanwezig zijn bij patiënten met vergevorderde ziekte. Ze spelen een cruciale rol in de destructie van parodontale weefsels. Aggregatibacter actinomycetemcomitans (B) is belangrijk bij agressieve parodontitis, maar behoort niet tot het rode complex.",
        "category": "Parodontale Microbiologie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["microbiologie", "parodontitis", "bacteriën", "rood complex", "NUG"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 133,
        "text": "KLINISCHE CASUS: Een patiënt met een diepe endodontische infectie reageert niet op de initiële behandeling met antibiotica. De tandarts vermoedt de aanwezigheid van een biofilm in het wortelkanaal.\nVRAAG: Welke eigenschap van bacteriële biofilms maakt ze bijzonder resistent tegen antibiotica en de immuunrespons van de gastheer?",
        "options": [
            "Snelle mutatiesnelheid van bacteriën binnen de biofilm",
            "De aanwezigheid van een extracellulaire polymere matrix (EPS) die als barrière dient",
            "Het volledig ontbreken van metabole activiteit van bacteriën in de biofilm",
            "De hoge zuurgraad binnen de biofilm die antibiotica deactiveert",
            "De uitsluitende aanwezigheid van grampositieve bacteriën"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "De aanwezigheid van een extracellulaire polymere matrix (EPS) die als barrière dient",
        "explanation": "Bacteriële biofilms zijn structuren waarin bacteriën ingebed zijn in een zelf-geproduceerde extracellulaire polymere matrix (EPS). Deze matrix vormt een fysieke barrière die de penetratie van antibiotica belemmert en de bacteriën beschermt tegen de immuunrespons. Bovendien vertonen bacteriën binnen een biofilm vaak een verminderde metabole activiteit, wat ook bijdraagt aan resistentie. Dit maakt mechanische debridement (zoals bij wortelkanaalbehandeling) cruciaal voor biofilmverwijdering.",
        "category": "Bacteriële Biofilms",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["microbiologie", "biofilm", "antibioticaresistentie", "infectie", "endodontie"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 134,
        "text": "KLINISCHE CASUS: Een patiënt met immunosuppressie (bijv. na orgaantransplantatie) presenteert zich met uitgebreide witte, afschraapbare laesies op het mondslijmvlies. De tandarts vermoedt een schimmelinfectie.\nVRAAG: Welke schimmelsoort is de meest voorkomende oorzaak van orale candidiasis (spruw) in de mondholte?",
        "options": [
            "Aspergillus fumigatus",
            "Cryptococcus neoformans",
            "Candida albicans",
            "Histoplasma capsulatum",
            "Pneumocystis jirovecii"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Candida albicans",
        "explanation": "Candida albicans is veruit de meest voorkomende schimmel die orale candidiasis (spruw) veroorzaakt. Deze infectie treedt vaak op bij patiënten met immunosuppressie, gebruik van antibiotica, steroïden, of bij dragers van orale prothesen. De laesies zijn typisch witte, crème-achtige plaques die afschraapbaar zijn en een rood, bloedend oppervlak onthullen.",
        "category": "Schimmelinfecties",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["microbiologie", "schimmel", "infectie", "candidiasis", "immunosuppressie"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 135,
        "text": "KLINISCHE CASUS: Een tandarts is betrokken bij een ziekenhuiscasus waarbij een patiënt met een uitgebreide maxillofaciale infectie wordt behandeld. Er is bezorgdheid over multiresistente bacteriën.\nVRAAG: Welk mechanisme van antibioticaresistentie omvat de bacteriële productie van enzymen die het antibioticum afbreken, zoals bèta-lactamase dat penicilline deactiveert?",
        "options": [
            "Verminderde permeabiliteit van de bacteriële celwand",
            "Verandering van de antibioticum-bindingsplaats",
            "Effluxpompen die het antibioticum uit de cel pompen",
            "Enzymatische inactivatie van het antibioticum",
            "Ontwikkeling van alternatieve metabole routes"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Enzymatische inactivatie van het antibioticum",
        "explanation": "Enzymatische inactivatie is een veelvoorkomend mechanisme van antibioticaresistentie, waarbij bacteriën enzymen produceren (zoals bèta-lactamase) die het antibioticum chemisch modificeren of afbreken, waardoor het zijn antimicrobiële werking verliest. Dit is de reden waarom veel penicillines niet effectief zijn tegen bèta-lactamase producerende bacteriën.",
        "category": "Antibioticaresistentie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["microbiologie", "antibiotica", "resistentie", "enzymen", "bèta-lactamase"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 136,
        "text": "KLINISCHE CASUS: Een tandarts legt aan een patiënt uit dat een goede mondhygiëne cruciaal is voor het voorkomen van gingivitis. De patiënt vraagt welke micro-organismen primair verantwoordelijk zijn voor de initiatie van gingivitis.\nVRAAG: Welke van de volgende bacteriën zijn de primaire kolonisatoren die de initiële tandplak vormen en een belangrijke rol spelen bij het ontstaan van gingivitis?",
        "options": [
            "Porphyromonas gingivalis",
            "Fusobacterium nucleatum",
            "Streptococcus sanguinis",
            "Prevotella intermedia",
            "Treponema denticola"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Streptococcus sanguinis",
        "explanation": "Streptococcus sanguinis (voorheen S. sanguis) en andere orale streptokokken (zoals S. oralis, S. mitis) zijn vroege kolonisatoren van het tandoppervlak. Ze hechten zich aan het glazuur en vormen de initiële tandplak (biofilm). Hoewel niet direct pathogeen voor parodontitis, creëren ze een omgeving waarin andere, meer pathogene bacteriën zich later kunnen vestigen, wat leidt tot gingivitis en uiteindelijk parodontitis.",
        "category": "Tandplak en Gingivitis Microbiologie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["microbiologie", "gingivitis", "tandplak", "bacteriën", "Streptococcus"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 137,
        "text": "KLINISCHE CASUS: Een patiënt, bekend met een geschiedenis van endocarditis, moet een tandheelkundige extractie ondergaan. De tandarts overweegt antibiotische profylaxe om bacteriëmie te voorkomen.\nVRAAG: Welke bacteriesoorten zijn de meest voorkomende veroorzakers van infectieuze endocarditis die kunnen ontstaan na tandheelkundige procedures?",
        "options": [
            "Escherichia coli",
            "Staphylococcus aureus",
            "Orale streptokokken (bijv. Streptococcus viridans groep)",
            "Pseudomonas aeruginosa",
            "Clostridium difficile"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Orale streptokokken (bijv. Streptococcus viridans groep)",
        "explanation": "Orale streptokokken, met name de 'viridans'-groep streptokokken (zoals S. sanguinis, S. mitis, S. mutans), zijn de meest voorkomende veroorzakers van infectieuze endocarditis die kan optreden na tandheelkundige procedures. Deze bacteriën kunnen via bacteriëmie de bloedbaan binnendringen en zich hechten aan beschadigde hartkleppen. Daarom wordt bij risicopatiënten antibiotische profylaxe aanbevolen.",
        "category": "Systemische Infecties van Orale Oorsprong",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["microbiologie", "endocarditis", "systemische infectie", "streptokokken", "profylaxe"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 138,
        "text": "KLINISCHE CASUS: Een patiënt heeft last van een slechte adem (halitose). De tandarts wil de bacteriële oorzaken van halitose uitleggen.\nVRAAG: Welke groep bacteriën is primair verantwoordelijk voor de productie van vluchtige zwavelverbindingen (VSC's), de belangrijkste oorzaak van orale halitose?",
        "options": [
            "Facultatieve anaëroben",
            "Obligaat aeroben",
            "Grampositieve kokken",
            "Gramnegatieve anaëroben",
            "Acidofiele bacteriën"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Gramnegatieve anaëroben",
        "explanation": "Gramnegatieve anaërobe bacteriën, zoals Porphyromonas gingivalis, Tannerella forsythia, Treponema denticola (het rode complex), en Fusobacterium nucleatum, die vaak in subgingivale plak en op het achterste deel van de tong voorkomen, zijn primair verantwoordelijk voor de productie van vluchtige zwavelverbindingen (VSC's) door de afbraak van eiwitten, wat de belangrijkste oorzaak is van orale halitose.",
        "category": "Orale Halitose Microbiologie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["microbiologie", "halitose", "bacteriën", "anaëroben", "zwavelverbindingen"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 139,
        "text": "KLINISCHE CASUS: Een tandarts wil de steriliteit van instrumenten controleren na autoclavering. Het begrijpen van de mechanismen van sterilisatie is essentieel voor infectiepreventie.\nVRAAG: Welk micro-organisme wordt vaak gebruikt als biologische indicator voor de effectiviteit van stoomsterilisatie (autoclavering) vanwege zijn hoge resistentie tegen hitte?",
        "options": [
            "Escherichia coli",
            "Staphylococcus aureus",
            "Bacillus stearothermophilus (Geobacillus stearothermophilus)",
            "Clostridium difficile",
            "Candida albicans"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Bacillus stearothermophilus (Geobacillus stearothermophilus)",
        "explanation": "Bacillus stearothermophilus (nu Geobacillus stearothermophilus genoemd) is een thermofiele bacterie die zeer hittebestendige sporen vormt. Daarom wordt het routinematig gebruikt als biologische indicator om de effectiviteit van stoomsterilisatie (autoclavering) te valideren. Als de sporen van deze bacterie worden gedood, is de sterilisatie effectief geweest tegen alle andere, minder resistente micro-organismen.",
        "category": "Infectiepreventie - Sterilisatie",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["microbiologie", "sterilisatie", "autoclaaf", "infectiepreventie", "biologische indicator"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },
    {
        "id": 140,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met een acute tandheelkundige infectie, en de tandarts moet de verspreiding van de infectie via de bloedbaan begrijpen.\nVRAAG: Welke term beschrijft de tijdelijke aanwezigheid van bacteriën in de bloedbaan, die vaak optreedt na tandheelkundige procedures en in de meeste gevallen asymptomatisch en van voorbijgaande aard is?",
        "options": [
            "Sepsis",
            "Septische shock",
            "Bacteriëmie",
            "Viremie",
            "Toxemie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Bacteriëmie",
        "explanation": "Bacteriëmie is de aanwezigheid van levensvatbare bacteriën in de bloedbaan. Dit is een veelvoorkomend verschijnsel na diverse tandheelkundige procedures (zoals extracties, scaling), en hoewel het meestal van voorbijgaande aard en asymptomatisch is bij gezonde individuen, kan het bij risicopatiënten leiden tot ernstigere complicaties zoals infectieuze endocarditis. Sepsis (A) en septische shock (B) zijn ernstigere, systemische ontstekingsreacties op een infectie, vaak inclusief bacteriëmie.",
        "category": "Infectie en Verspreiding",
        "domain": "MICROBIOLOGIE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["microbiologie", "infectie", "bacteriëmie", "sepsis", "bloedbaan"],
        "created_at": "2025-07-21T18:27:57Z",
        "updated_at": "2025-07-21T18:27:57Z"
    },{
        "id": 141,
        "text": "KLINISCHE CASUS: Een tandarts is van plan een directe restauratie te plaatsen in een posterieure tand. De patiënt wenst een esthetische en duurzame oplossing. De tandarts overweegt het gebruik van een composiet.\nVRAAG: Welke component van composietrestauratiematerialen is primair verantwoordelijk voor de esthetische eigenschappen (transparantie en kleurstabiliteit) en de mechanische sterkte?",
        "options": [
            "De monomeermatrix (hars)",
            "De vulstoffen (fillers)",
            "Het koppelmiddel (silaan)",
            "De initiator (foto-initiator)",
            "De pigmenten"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "De vulstoffen (fillers)",
        "explanation": "De vulstoffen (fillers), zoals glas, kwarts of keramiekdeeltjes, zijn cruciaal voor de eigenschappen van composiet. Ze verbeteren de mechanische sterkte (hardheid, slijtvastheid, compressiesterkte), verminderen krimp, en beïnvloeden de optische eigenschappen zoals transparantie, opaciteit en kleurstabiliteit. De monomeermatrix (A) is de hars die polymeriseert. Het koppelmiddel (C) zorgt voor hechting tussen hars en vulstoffen. Initiator (D) start polymerisatie. Pigmenten (E) geven kleur, maar vulstoffen beïnvloeden de algehele esthetiek breder.",
        "category": "Composietmaterialen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["materiaalkunde", "composiet", "restauratief", "vullingen", "esthetiek"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 142,
        "text": "KLINISCHE CASUS: Een tandarts moet een afdruk nemen voor een kroon. De tandarts wil een materiaal gebruiken dat een hoge nauwkeurigheid en dimensionele stabiliteit biedt, zelfs na enige tijd.\nVRAAG: Welk afdrukmateriaal staat bekend om zijn superieure nauwkeurigheid, elastische herstel en lange termijn dimensionele stabiliteit, waardoor het ideaal is voor precisie-afdrukken zoals voor kronen en bruggen?",
        "options": [
            "Alginaten",
            "Condensatie-siliconen (C-siliconen)",
            "Polyethers",
            "Polysulfiden",
            "Zinkoxide-eugenol (ZOE) afdrukpasta"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Polyethers",
        "explanation": "Polyethers worden beschouwd als zeer nauwkeurige afdrukmaterialen met uitstekende dimensionele stabiliteit over tijd en goede hydrofiliteit, waardoor ze geschikt zijn voor vochtige omgevingen in de mond. Ze zijn populair voor precisiewerk zoals kronen, bruggen en implantaten. Alginaten (A) zijn minder nauwkeurig en dimensioneel instabiel. Condensatie-siliconen (B) hebben een zekere mate van krimp. Polysulfiden (D) zijn ook nauwkeurig maar minder gebruiksvriendelijk en hebben een onaangename geur. ZOE (E) is primair voor edentate afdrukken.",
        "category": "Afdrukmaterialen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["materiaalkunde", "afdrukken", "polyether", "nauwkeurigheid", "kroon"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 143,
        "text": "KLINISCHE CASUS: Een patiënt heeft een implantaat gekregen en de tandarts wil een definitieve kroon plaatsen. Het is belangrijk dat de kroon een hoge buigsterkte heeft en esthetisch aantrekkelijk is voor het frontgebied.\nVRAAG: Welk keramisch materiaal wordt steeds vaker gebruikt voor full-contour kronen in zowel het front als posterieur, en staat bekend om zijn hoge sterkte en toenemende esthetiek?",
        "options": [
            "Veldspaatporselein",
            "Leuciet-versterkt glaskeramiek",
            "Lithiumdisilicaat (bijv. e.max Press/CAD)",
            "Zirkoniumdioxide (Zirconia)",
            "Aluminiumoxide"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Zirkoniumdioxide (Zirkonia)",
        "explanation": "Zirkoniumdioxide (zirkonia) is de laatste jaren enorm populair geworden vanwege zijn uitzonderlijke buigsterkte en breuktaaiheid, waardoor het ideaal is voor posterieure kronen en bruggen. Recente ontwikkelingen hebben de translucentie (esthetiek) van zirkonia verbeterd, waardoor het ook steeds vaker in het front wordt toegepast. Lithiumdisilicaat (C) is ook sterk en esthetisch, maar zirkonia heeft over het algemeen een hogere sterkte. Veldspaatporselein (A) en leuciet-versterkt glaskeramiek (B) zijn minder sterk.",
        "category": "Keramische Materialen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["materiaalkunde", "keramiek", "zirkonia", "kronen", "implantaten", "esthetiek"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 144,
        "text": "KLINISCHE CASUS: Een tandarts moet een restauratie plaatsen in een patiënt met een hoog cariësrisico en wil een materiaal gebruiken dat fluoride afgeeft om secundaire cariës te voorkomen.\nVRAAG: Welk restauratiemateriaal staat bekend om zijn vermogen tot fluoride-afgifte en -opname, waardoor het een cariostatisch effect heeft?",
        "options": [
            "Amalgaam",
            "Composiet (conventioneel)",
            "Glasionomeercement (GIC)",
            "Compomeer",
            "Keramiek"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Glasionomeercement (GIC)",
        "explanation": "Glasionomeercement (GIC) is uniek onder de restauratiematerialen vanwege zijn vermogen om fluoride af te geven en opnieuw op te nemen uit de mondomgeving. Dit maakt het een uitstekende keuze voor patiënten met een hoog cariësrisico, als basis of als restauratie in niet-dragende gebieden, vanwege het cariostatische effect. Composiet (B) geeft geen fluoride af, en amalgaam (A) en keramiek (E) ook niet.",
        "category": "Fluoride-afgevende materialen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.6,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["materiaalkunde", "cariës", "fluoride", "glasionomeer", "preventie"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 145,
        "text": "KLINISCHE CASUS: Een tandarts gebruikt een bondingmiddel om een composietrestauratie aan de tand te hechten. Het begrijpen van de hechtingsmechanismen is essentieel voor succes.\nVRAAG: Welk van de volgende termen beschrijft het proces waarbij een adhesief in de gedemineraliseerde glazuur- en/of dentinestructuur penetreert en daar polymeriseert, wat leidt tot mechanische interlocking?",
        "options": [
            "Chemische hechting",
            "Micromechanische retentie",
            "Cohesieve hechting",
            "Macromechanische retentie",
            "Adsorptie"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Micromechanische retentie",
        "explanation": "Micromechanische retentie is het primaire hechtingsmechanisme van moderne adhesieven aan glazuur en dentine. Dit omvat het etsen (demineraliseren) van het tandoppervlak om microporositeiten te creëren, waarna het adhesief (bondingmiddel) in deze structuren penetreert en polymeriseert, resulterend in een 'resin tag' en een sterke, microscopische in elkaar grijpende verbinding. Chemische hechting (A) speelt een minder dominante rol bij de meeste composietadhesieven aan tandweefsel, behalve bij GIC's.",
        "category": "Adhesieve Systemen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["materiaalkunde", "adhesie", "bonding", "restauratief", "micromechanisch"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 146,
        "text": "KLINISCHE CASUS: Een tandarts wil een amalgaamrestauratie plaatsen in een posterieure tand. Het is belangrijk om de eigenschappen van dit materiaal te kennen.\nVRAAG: Welke van de volgende eigenschappen is een belangrijk voordeel van amalgaam als restauratiemateriaal, vooral in vergelijking met composieten?",
        "options": [
            "Superieure esthetiek",
            "Directe chemische hechting aan tandweefsel",
            "Minder gevoelig voor vochtcontaminatie tijdens plaatsing",
            "Hoge elasticiteitsmodulus",
            "Lage thermische geleidbaarheid"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Minder gevoelig voor vochtcontaminatie tijdens plaatsing",
        "explanation": "Amalgaam is historisch gezien een robuust restauratiemateriaal, en een van de belangrijkste voordelen is de relatieve ongevoeligheid voor vochtcontaminatie tijdens de plaatsing in vergelijking met composieten, die een strikte drooglegging vereisen voor optimale hechting. Esthetiek (A) is een nadeel van amalgaam. Het hecht niet chemisch (B) aan tandweefsel. De thermische geleidbaarheid (E) is relatief hoog, wat gevoeligheid kan veroorzaken.",
        "category": "Amalgaam",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.6,
            "discrimination": 1.6,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["materiaalkunde", "amalgaam", "restauratief", "eigenschappen", "vocht"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 147,
        "text": "KLINISCHE CASUS: Een tandarts gebruikt gips om studiemodellen van de patiënt te maken. Het is essentieel om de juiste verwerking van gips te begrijpen voor nauwkeurige modellen.\nVRAAG: Welke factor beïnvloedt de expansie en de werktijd van gips het meest direct?",
        "options": [
            "De temperatuur van het water",
            "De grootte van de gipskristallen",
            "De water/poeder ratio",
            "De mengtijd",
            "De omgevingsluchtvochtigheid"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "De water/poeder ratio",
        "explanation": "De water/poeder ratio is de meest kritische factor die de eigenschappen van gips beïnvloedt. Een hogere water/poeder ratio leidt tot een langere werktijd, minder sterkte, en minder expansie (krimp), terwijl een lagere ratio het tegenovergestelde effect heeft. Ook de temperatuur van het water (A) en de mengtijd (D) beïnvloeden dit, maar de water/poeder ratio is het meest bepalend.",
        "category": "Gipsmaterialen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["materiaalkunde", "gips", "modellen", "afdrukken", "expansie"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },{
        "id": 148,
        "text": "KLINISCHE CASUS: Een tandarts overweegt het gebruik van een glasvezelstift voor de opbouw van een endodontisch behandelde tand. Het is belangrijk de eigenschappen van vezelversterkte materialen te begrijpen.\nVRAAG: Welke eigenschap van glasvezelstiften draagt primair bij aan hun voordeel ten opzichte van metalen stiften voor de opbouw van endodontisch behandelde tanden?",
        "options": [
            "Hogere radiopaciteit",
            "Minder gevoelig voor corrosie",
            "Lagere elasticiteitsmodulus, vergelijkbaar met dentine",
            "Superieure hechting aan het worteldentine",
            "Hogere hardheid en stijfheid"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Lagere elasticiteitsmodulus, vergelijkbaar met dentine",
        "explanation": "Glasvezelstiften hebben een elasticiteitsmodulus (stijfheid) die veel dichter bij die van dentine ligt dan metalen stiften. Dit 'dentine-achtige' gedrag vermindert het risico op wortelfracturen onder belasting, omdat de stressverdeling in de wortel gunstiger is. Dit is een belangrijk voordeel voor de lange termijn prognose van endodontisch behandelde tanden. Hogere hardheid/stijfheid (E) is eerder een nadeel.",
        "category": "Opbouwmaterialen - Glasvezelstiften",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["materiaalkunde", "glasvezel", "stiften", "endodontie", "elasticiteitsmodulus"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 149,
        "text": "KLINISCHE CASUS: Een tandarts moet een cement kiezen voor het vastzetten van een keramische kroon. De hechtsterkte en duurzaamheid zijn cruciaal.\nVRAAG: Welk type cement combineert chemische hechting aan tandweefsel en metaal/keramiek, en fluoride-afgifte met een goede esthetiek, waardoor het veelzijdig inzetbaar is voor diverse restauraties?",
        "options": [
            "Zinkfosfaatcement",
            "Glasionomeercement (conventioneel)",
            "Harsgemodificeerd glasionomeercement (RM-GIC)",
            "Zinkoxide-eugenol cement",
            "Calciumhydroxide cement"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Harsgemodificeerd glasionomeercement (RM-GIC)",
        "explanation": "Harsgemodificeerd glasionomeercement (RM-GIC) is een hybride materiaal dat de voordelen van conventioneel GIC (fluoride-afgifte, chemische hechting) combineert met die van harsmaterialen (betere esthetiek, lagere gevoeligheid voor vocht bij uitharding). Dit maakt het een populaire keuze voor het cementeren van diverse indirecte restauraties en als basis of liner. Zinkfosfaat (A) is oud en hecht niet chemisch. Conventioneel GIC (B) is minder esthetisch. ZOE (D) is tijdelijk/basis. Calciumhydroxide (E) is een pulpaoverkappingsmateriaal.",
        "category": "Cementen",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["materiaalkunde", "cement", "kronen", "hechting", "fluoride"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },
    {
        "id": 150,
        "text": "KLINISCHE CASUS: Een tandarts overweegt het gebruik van een universeel adhesief systeem voor de hechtingsprocedure van een restauratie. Het is belangrijk de moderne classificatie en eigenschappen van deze adhesieven te begrijpen.\nVRAAG: Welke eigenschap is kenmerkend voor de nieuwere 'universele' adhesieven in vergelijking met oudere generaties adhesieven?",
        "options": [
            "Ze vereisen altijd een aparte etsstap met fosforzuur op glazuur en dentine.",
            "Ze zijn uitsluitend self-etch systemen en vereisen geen enkele vorm van etsing.",
            "Ze kunnen worden gebruikt in etch-and-rinse, self-etch en selectieve-ets modes.",
            "Ze hechten primair via chemische binding aan calciumionen in het dentine zonder micromechanische retentie.",
            "Ze zijn uitsluitend effectief voor glazuurhechting en niet voor dentine."
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Ze kunnen worden gebruikt in etch-and-rinse, self-etch en selectieve-ets modes.",
        "explanation": "Universele adhesieven zijn zo geformuleerd dat ze flexibel kunnen worden gebruikt met verschillende etstechnieken: etch-and-rinse (volledige etsing en spoeling), self-etch (zelf-etsing zonder spoeling), of selectieve glazuuretsing (alleen etsen van glazuur, self-etch op dentine). Deze veelzijdigheid is hun kenmerkende eigenschap. Dit in tegenstelling tot oudere generaties die een vaste etstechniek vereisten. Ze hechten zowel micromechanisch als via chemische interacties.",
        "category": "Adhesieve Systemen - Universele Adhesieven",
        "domain": "MATERIAALKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.9,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["materiaalkunde", "adhesieven", "bonding", "universeel", "etsing"],
        "created_at": "2025-07-21T18:28:50Z",
        "updated_at": "2025-07-21T18:28:50Z"
    },{
        "id": 151,
        "text": "KLINISCHE CASUS: Een 65-jarige patiënt met een voorgeschiedenis van myocardinfarct gebruikt een bètablokker en een ACE-remmer. De patiënt presenteert zich voor een geplande extractie van element 36. De tandarts moet rekening houden met de cardiovasculaire status van de patiënt.\nVRAAG: Welk van de volgende effecten kan optreden bij het gebruik van adrenaline (epinefrine) in lokale anesthetica bij patiënten met cardiovasculaire aandoeningen, vooral als voorzichtigheid niet wordt betracht?",
        "options": [
            "Bradycardie en hypotensie",
            "Verhoogd risico op longembolie",
            "Tachycardie, hypertensie en hartkloppingen",
            "Hypoglykemie en duizeligheid",
            "Verhoogde sedatie en ademhalingsdepressie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Tachycardie, hypertensie en hartkloppingen",
        "explanation": "Adrenaline (epinefrine) is een sympathicomimeticum dat alfa- en bèta-adrenerge receptoren stimuleert. Bij patiënten met cardiovasculaire aandoeningen kan systemische absorptie leiden tot ongewenste cardiale effecten zoals tachycardie (versnelde hartslag), hypertensie (verhoogde bloeddruk) en hartkloppingen, vooral bij hoge doses of intravasculaire injectie. Voorzichtigheid en aspiratie zijn essentieel. Bradycardie en hypotensie (A) zijn eerder kenmerkend voor een vasovagale reactie, niet voor adrenaline.",
        "category": "Cardiovasculaire Aandoeningen",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "cardiovasculair", "farmacologie", "adrenaline", "hypertensie", "myocardinfarct"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 152,
        "text": "KLINISCHE CASUS: Een 45-jarige patiënt met ongecontroleerde diabetes mellitus type 2 (HbA1c 9.0%) presenteert zich met uitgebreide parodontitis en frequente orale candidiasis. De tandarts plant een parodontale behandeling.\nVRAAG: Welk van de volgende is een direct gevolg van ongecontroleerde hyperglykemie dat bijdraagt aan orale complicaties bij diabetespatiënten?",
        "options": [
            "Verhoogde speekselvloed en verminderde orale pH",
            "Verminderde vasculaire permeabiliteit en verbeterde immuunrespons",
            "Verhoogde gevoeligheid voor infecties en vertraagde wondgenezing",
            "Verlaagd risico op cariës door verminderde suikerinname",
            "Versterking van het alveolaire bot"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Verhoogde gevoeligheid voor infecties en vertraagde wondgenezing",
        "explanation": "Ongecontroleerde hyperglykemie (hoge bloedsuikerspiegel) bij diabetespatiënten leidt tot een reeks fysiologische veranderingen die de mondgezondheid nadelig beïnvloeden. Dit omvat een verminderde functie van neutrofielen, microvasculaire complicaties en een verstoord metabolisme, wat resulteert in een verhoogde vatbaarheid voor infecties (zoals parodontitis en candidiasis) en een aanzienlijk vertraagde en gecompromitteerde wondgenezing.",
        "category": "Diabetes Mellitus",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.18
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "diabetes", "hyperglykemie", "infectie", "wondgenezing", "parodontitis"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 153,
        "text": "KLINISCHE CASUS: Een 70-jarige patiënt met artritis en een maagzweer gebruikt dagelijks NSAID's (Non-Steroidal Anti-inflammatory Drugs) voor pijnbeheersing. De tandarts moet hiermee rekening houden bij het voorschrijven van postoperatieve pijnstilling.\nVRAAG: Welk veelvoorkomend bijwerking van langdurig NSAID-gebruik is van direct belang voor de algemene gezondheid van een patiënt met een maagzweer?",
        "options": [
            "Hepatotoxiciteit (leverschade)",
            "Nefrotoxiciteit (nierschade)",
            "Gastro-intestinale bloedingen en ulceratie",
            "Verhoogd risico op bloedstolsels",
            "Otolarische problemen (oor- en evenwichtsproblemen)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Gastro-intestinale bloedingen en ulceratie",
        "explanation": "NSAID's werken door cyclo-oxygenase (COX) enzymen te remmen, wat de synthese van prostaglandinen vermindert. Prostaglandinen spelen een beschermende rol in de maag door de slijmproductie te stimuleren en de bloedtoevoer te handhaven. Langdurig gebruik van NSAID's kan deze bescherming aantasten, wat leidt tot een verhoogd risico op gastro-intestinale ulcera (maagzweren) en bloedingen, wat zeer gevaarlijk kan zijn, vooral bij patiënten met een bestaande maagzweer.",
        "category": "Farmacologie en Systemische Effecten - NSAID's",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "farmacologie", "NSAID's", "maagzweer", "bijwerkingen", "gastro-intestinaal"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 154,
        "text": "KLINISCHE CASUS: Een 30-jarige patiënte is zwanger (18 weken) en presenteert zich met gingivitis en een pyogeen granuloom. Ze maakt zich zorgen over tandheelkundige behandelingen tijdens de zwangerschap.\nVRAAG: Welke medische aandoening, indien aanwezig en onbehandeld, kan leiden tot een verhoogd risico op een premature geboorte of een laag geboortegewicht bij de pasgeborene?",
        "options": [
            "Cariës",
            "Milde gingivitis",
            "Chronische parodontitis",
            "Temporomandibulaire gewrichtspijn",
            "Orale herpes simplex infectie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Chronische parodontitis",
        "explanation": "Chronische parodontitis, vooral in ernstige vormen, is geassocieerd met een verhoogd risico op nadelige zwangerschapsuitkomsten, waaronder premature geboorte en laag geboortegewicht. Dit wordt toegeschreven aan de systemische ontsteking en de verspreiding van bacteriële producten vanuit de mond. Milde gingivitis (B) is minder een risico, maar moet wel behandeld worden. Cariës (A) heeft geen direct verband met prematuriteit.",
        "category": "Zwangerschap en Orale Gezondheid",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "zwangerschap", "parodontitis", "systemisch", "risico"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 155,
        "text": "KLINISCHE CASUS: Een patiënt met astma presenteert zich voor een routinecontrole. De patiënt gebruikt een inhalator met een corticosteroïd. De tandarts moet mogelijke orale bijwerkingen van deze medicatie beoordelen.\nVRAAG: Welke orale bijwerking wordt het meest frequent geassocieerd met het langdurig gebruik van inhalatiecorticosteroïden bij astmapatiënten?",
        "options": [
            "Verhoogd risico op cariës",
            "Gingivale hyperplasie",
            "Orale candidiasis (spruw)",
            "Droge mond (xerostomie)",
            "Verhoogde tanderosie"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Orale candidiasis (spruw)",
        "explanation": "Langdurig gebruik van inhalatiecorticosteroïden kan leiden tot immunosuppressie van de orale mucosa, wat de groei van de opportunistische schimmel Candida albicans bevordert. Dit resulteert in orale candidiasis (spruw), gekenmerkt door witte, afschraapbare laesies. Patiënten worden geadviseerd om na gebruik van de inhalator de mond te spoelen om het risico hierop te verminderen. Droge mond (D) kan een bijwerking zijn van sommige astmamedicatie, maar candidiasis is directer gerelateerd aan corticosteroïden.",
        "category": "Ademhalingsaandoeningen - Astma",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "astma", "medicatie", "bijwerkingen", "candidiasis"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 156,
        "text": "KLINISCHE CASUS: Een patiënt met een voorgeschiedenis van beroerte gebruikt acetylsalicylzuur (aspirine) 80mg dagelijks als trombocytenaggregatieremmer. De tandarts plant een extractie en moet rekening houden met het bloedingsrisico.\nVRAAG: Welk mechanisme van acetylsalicylzuur draagt bij aan het verhoogde bloedingsrisico?",
        "options": [
            "Remming van vitamine K-afhankelijke stollingsfactoren",
            "Directe lysis van bloedstolsels",
            "Irreversibele remming van cyclo-oxygenase (COX) in bloedplaatjes",
            "Verhoging van de protrombinetijd",
            "Vermindering van de aanmaak van trombine"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Irreversibele remming van cyclo-oxygenase (COX) in bloedplaatjes",
        "explanation": "Acetylsalicylzuur remt irreversibel het enzym cyclo-oxygenase (COX) in bloedplaatjes. Dit voorkomt de synthese van tromboxaan A2, een krachtige bloedplaatjesactivator en vasoconstrictor. Hierdoor wordt de plaatjesaggregatie (samenklontering van bloedplaatjes) verminderd, wat leidt tot een verlengde bloedingstijd en een verhoogd bloedingsrisico, zelfs bij lage doses aspirine.",
        "category": "Bloedingsstoornissen en Medicatie",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.0,
            "discrimination": 1.9,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "farmacologie", "bloeding", "aspirine", "trombocyten", "extractie"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 157,
        "text": "KLINISCHE CASUS: Een 55-jarige patiënt presenteert zich met acute pijn en zwelling in de rechter onderkaak, wijzend op een abces. De patiënt heeft ook last van gezwollen, pijnlijke lymfeklieren in de nek.\nVRAAG: Welke van de volgende structuren is een belangrijk onderdeel van het lymfestelsel en speelt een cruciale rol bij de afweer tegen infecties in het hoofd-halsgebied?",
        "options": [
            "Schildklier",
            "Bijnier",
            "Milt",
            "Lymfeklieren",
            "Hypofyse"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Lymfeklieren",
        "explanation": "Lymfeklieren zijn kleine, boonvormige organen die deel uitmaken van het lymfestelsel en het immuunsysteem. Ze filteren lymfevloeistof en bevatten immuuncellen die helpen bij het bestrijden van infecties. Bij een infectie in het hoofd-halsgebied, zoals een dentaal abces, kunnen de regionale lymfeklieren zwellen en pijnlijk worden als reactie op de infectie.",
        "category": "Lymfestelsel en Infectie",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.7,
            "discrimination": 1.6,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "lymfeklieren", "infectie", "immuunsysteem", "abces", "nek"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 158,
        "text": "KLINISCHE CASUS: Een tandarts onderzoekt een patiënt die klaagt over extreme vermoeidheid, gewichtstoename en een zwelling in de nek. De tandarts observeert ook een verdikking van de tong.\nVRAAG: Welke van de volgende endocriene aandoeningen kan leiden tot een verdikking van de tong (macroglossie) en andere systemische symptomen zoals vermoeidheid en gewichtstoename?",
        "options": [
            "Hyperthyreoïdie",
            "Hypothyreoïdie",
            "Ziekte van Addison",
            "Ziekte van Cushing",
            "Diabetes insipidus"
        ],
        "correct_answer_index": 1,
        "correct_answer_text": "Hypothyreoïdie",
        "explanation": "Hypothyreoïdie (een traag werkende schildklier) kan leiden tot een scala aan systemische symptomen, waaronder vermoeidheid, gewichtstoename, koude-intolerantie, en orale manifestaties zoals macroglossie (verdikking van de tong) en vertraagde tandontwikkeling bij kinderen. Dit komt door de ophoping van glycosaminoglycanen in weefsels. Hyperthyreoïdie (A) veroorzaakt het tegenovergestelde effect (gewichtstoename, warmte-intolerantie, vaak slank postuur).",
        "category": "Endocriene Aandoeningen",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 1.1,
            "discrimination": 1.8,
            "guessing": 0.20
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "endocrien", "schildklier", "hypothyreoïdie", "macroglossie", "systemisch"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 159,
        "text": "KLINISCHE CASUS: Een patiënt, bekend met COPD (Chronische Obstructieve Longziekte), presenteert zich met dyspneu (kortademigheid) in rust tijdens de tandheelkundige behandeling. De tandarts moet de patiënt comfortabel positioneren en de vitale functies monitoren.\nVRAAG: Welke van de volgende aanpassingen in de tandheelkundige stoelpositie is meestal het meest comfortabel voor een patiënt met COPD?",
        "options": [
            "Volledig rugligging (supine positie)",
            "Trendelenburg positie (hoofd lager dan voeten)",
            "Schommelpositie (hoofd hoger dan voeten, semi-zittend)",
            "Rechtstandig zittend met de voeten omhoog",
            "Laterale decubitus positie (op de zij liggen)"
        ],
        "correct_answer_index": 2,
        "correct_answer_text": "Schommelpositie (hoofd hoger dan voeten, semi-zittend)",
        "explanation": "Patiënten met COPD ervaren vaak dyspneu (kortademigheid), vooral in liggende positie. Een semi-zittende positie, waarbij het hoofd hoger is dan de voeten (schommelpositie), vergemakkelijkt de ademhaling en vermindert de druk op het diafragma. Volledig rugligging (A) en Trendelenburg (B) zouden de ademhaling bemoeilijken. Andere posities (D, E) zijn minder gangbaar of minder stabiel voor tandheelkundige procedures.",
        "category": "Ademhalingsaandoeningen - COPD",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 1,
        "irt_params": {
            "difficulty": 0.8,
            "discrimination": 1.7,
            "guessing": 0.19
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "COPD", "ademhaling", "patiëntpositionering", "dyspneu"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    },
    {
        "id": 160,
        "text": "KLINISCHE CASUS: Een patiënt presenteert zich met een verhoogde bloedingsneiging tijdens en na tandheelkundige procedures. De tandarts wil een basisbegrip hebben van hemostase.\nVRAAG: Welke van de volgende is de correcte volgorde van de primaire hemostase na een vaatletsel?",
        "options": [
            "Vaatvernauwing -> Trombocytenaggregatie -> Fibrinevorming",
            "Fibrinevorming -> Vaatvernauwing -> Trombocytenaggregatie",
            "Trombocytenaggregatie -> Vaatvernauwing -> Fibrinevorming",
            "Vaatvernauwing -> Trombocytenadhesie -> Trombocytenaggregatie",
            "Trombocytenadhesie -> Fibrinevorming -> Vaatvernauwing"
        ],
        "correct_answer_index": 3,
        "correct_answer_text": "Vaatvernauwing -> Trombocytenadhesie -> Trombocytenaggregatie",
        "explanation": "Primaire hemostase is het eerste proces dat optreedt na een vaatletsel om bloedverlies te stoppen. De correcte volgorde is: 1) Vasoconstrictie (vaatvernauwing) om de bloedstroom te verminderen. 2) Plaatjesadhesie (trombocytenadhesie) waarbij bloedplaatjes zich hechten aan het beschadigde endotheel. 3) Plaatjesaggregatie (trombocytenaggregatie) waarbij meer bloedplaatjes worden gerekruteerd en samenkomen om een 'plaatjesplug' te vormen. Fibrinevorming behoort tot de secundaire hemostase (stollingscascade), die de plaatjesplug stabiliseert.",
        "category": "Hemostase",
        "domain": "ALGEMENE_GENEESKUNDE",
        "difficulty_level": 2,
        "irt_params": {
            "difficulty": 0.9,
            "discrimination": 1.8,
            "guessing": 0.17
        },
        "image_url": null,
        "tags": ["algemene geneeskunde", "hemostase", "bloeding", "trombocyten", "fysiologie"],
        "created_at": "2025-07-21T18:48:38Z",
        "updated_at": "2025-07-21T18:48:38Z"
    }
        ]
        
        created_count = 0
        
        for i, q_data in enumerate(questions_data, 1):
            try:
                # Создаем вопрос
                question = Question(
                    text=q_data["text"],
                    options=json.dumps(q_data["options"]),
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    category_id=categories.get(q_data["category"], 1),
                    big_domain_id=domains.get(q_data["domain"], 1),
                    difficulty_level=q_data.get("difficulty_level", 3),
                    question_type="multiple_choice"
                )
                
                db.session.add(question)
                db.session.flush()
                
                # Создаем IRT параметры
                irt_params = q_data["irt_params"]
                irt = IRTParameters(
                    question_id=question.id,
                    difficulty=irt_params["difficulty"],
                    discrimination=irt_params["discrimination"],
                    guessing=irt_params["guessing"]
                )
                
                db.session.add(irt)
                db.session.commit()
                
                print(f"✅ Вопрос {i} создан (ID: {question.id})")
                created_count += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Ошибка при создании вопроса {i}: {e}")
        
        print(f"\n✅ Создано вопросов: {created_count}")
        return created_count

def main():
    """Основная функция"""
    
    print("🚀 ЗАГРУЗКА ВОПРОСОВ ИЗ ШАБЛОНА")
    print("=" * 50)
    print("📝 ИНСТРУКЦИЯ:")
    print("1. Откройте файл scripts/questions_template.py")
    print("2. Замените questions_data на ваши 80 вопросов")
    print("3. Запустите этот скрипт")
    print("=" * 50)
    
    try:
        count = load_questions_from_template()
        print(f"\n🎉 Загружено вопросов: {count}")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")

if __name__ == '__main__':
    main() 