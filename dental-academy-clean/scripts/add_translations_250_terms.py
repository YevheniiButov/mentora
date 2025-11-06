#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add 8-language translations for 250 medical terms
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import MedicalTerm, db

# Translations for 269 terms (7 languages × 269 = 1883 translations)
TRANSLATIONS = {
    # BASIC TERMS (50) - anatomy_basic, symptoms_basic, diseases_basic, treatments_basic, dental_basic
    'het hart': {'ru': 'сердце', 'uk': 'серце', 'es': 'corazón', 'pt': 'coração', 'tr': 'kalp', 'fa': 'قلب', 'ar': 'القلب'},
    'de long': {'ru': 'лёгкое', 'uk': 'легеня', 'es': 'pulmón', 'pt': 'pulmão', 'tr': 'akciğer', 'fa': 'ریه', 'ar': 'الرئة'},
    'de maag': {'ru': 'желудок', 'uk': 'шлунок', 'es': 'estómago', 'pt': 'estômago', 'tr': 'mide', 'fa': 'معده', 'ar': 'المعدة'},
    'de lever': {'ru': 'печень', 'uk': 'печінка', 'es': 'hígado', 'pt': 'fígado', 'tr': 'karaciğer', 'fa': 'جگر', 'ar': 'الكبد'},
    'de nier': {'ru': 'почка', 'uk': 'нирка', 'es': 'riñón', 'pt': 'rim', 'tr': 'böbrek', 'fa': 'کلیه', 'ar': 'الكلية'},
    'het brein': {'ru': 'мозг', 'uk': 'мозок', 'es': 'cerebro', 'pt': 'cérebro', 'tr': 'beyin', 'fa': 'مغز', 'ar': 'الدماغ'},
    'de keel': {'ru': 'горло', 'uk': 'горло', 'es': 'garganta', 'pt': 'garganta', 'tr': 'boğaz', 'fa': 'حلق', 'ar': 'الحلق'},
    'het bloedvat': {'ru': 'кровеносный сосуд', 'uk': 'кровоносна судина', 'es': 'vaso sanguíneo', 'pt': 'vaso sanguíneo', 'tr': 'kan damarı', 'fa': 'رگ خونی', 'ar': 'الأوعية الدموية'},
    'de spier': {'ru': 'мышца', 'uk': 'м\'яз', 'es': 'músculo', 'pt': 'músculo', 'tr': 'kas', 'fa': 'ماهیچه', 'ar': 'العضلة'},
    'het bot': {'ru': 'кость', 'uk': 'кістка', 'es': 'hueso', 'pt': 'osso', 'tr': 'kemik', 'fa': 'استخوان', 'ar': 'العظم'},
    
    'de pijn': {'ru': 'боль', 'uk': 'біль', 'es': 'dolor', 'pt': 'dor', 'tr': 'ağrı', 'fa': 'درد', 'ar': 'الألم'},
    'de koorts': {'ru': 'лихорадка', 'uk': 'гарячка', 'es': 'fiebre', 'pt': 'febre', 'tr': 'ateş', 'fa': 'تب', 'ar': 'الحمى'},
    'de hoest': {'ru': 'кашель', 'uk': 'кашель', 'es': 'tos', 'pt': 'tosse', 'tr': 'öksürük', 'fa': 'سعال', 'ar': 'السعال'},
    'de hoofdpijn': {'ru': 'головная боль', 'uk': 'головний біль', 'es': 'dolor de cabeza', 'pt': 'dor de cabeça', 'tr': 'baş ağrısı', 'fa': 'سردرد', 'ar': 'الصداع'},
    'de misselijkheid': {'ru': 'тошнота', 'uk': 'нудота', 'es': 'náusea', 'pt': 'náusea', 'tr': 'bulantı', 'fa': 'تهوع', 'ar': 'الغثيان'},
    'het braken': {'ru': 'рвота', 'uk': 'блювання', 'es': 'vómito', 'pt': 'vômito', 'tr': 'kusma', 'fa': 'استفراغ', 'ar': 'القيء'},
    'de diarree': {'ru': 'диарея', 'uk': 'діарея', 'es': 'diarrea', 'pt': 'diarreia', 'tr': 'ishal', 'fa': 'اسهال', 'ar': 'الإسهال'},
    'de vermoeidheid': {'ru': 'усталость', 'uk': 'втома', 'es': 'fatiga', 'pt': 'cansaço', 'tr': 'yorgunluk', 'fa': 'خستگی', 'ar': 'التعب'},
    'de duizeligheid': {'ru': 'головокружение', 'uk': 'запаморочення', 'es': 'mareo', 'pt': 'tontura', 'tr': 'baş dönmesi', 'fa': 'گیجی', 'ar': 'الدوخة'},
    'de kortademigheid': {'ru': 'одышка', 'uk': 'задишка', 'es': 'falta de aliento', 'pt': 'falta de ar', 'tr': 'nefes darlığı', 'fa': 'تنگی نفس', 'ar': 'ضيق التنفس'},
    
    'de diabetes': {'ru': 'диабет', 'uk': 'діабет', 'es': 'diabetes', 'pt': 'diabetes', 'tr': 'diyabet', 'fa': 'دیابت', 'ar': 'السكري'},
    'de hypertensie': {'ru': 'гипертония', 'uk': 'гіпертензія', 'es': 'hipertensión', 'pt': 'hipertensão', 'tr': 'hipertansiyon', 'fa': 'فشار خون بالا', 'ar': 'ارتفاع ضغط الدم'},
    'de pneumonie': {'ru': 'пневмония', 'uk': 'пневмонія', 'es': 'neumonía', 'pt': 'pneumonia', 'tr': 'zatürre', 'fa': 'ذات الریه', 'ar': 'الالتهاب الرئوي'},
    'de griep': {'ru': 'грипп', 'uk': 'грип', 'es': 'gripe', 'pt': 'gripe', 'tr': 'grip', 'fa': 'آنفلوآنزا', 'ar': 'الإنفلونزا'},
    'het eczeem': {'ru': 'экзема', 'uk': 'екзема', 'es': 'eccema', 'pt': 'eczema', 'tr': 'egzama', 'fa': 'اگزما', 'ar': 'الأكزيما'},
    'de asthma': {'ru': 'астма', 'uk': 'астма', 'es': 'asma', 'pt': 'asma', 'tr': 'astım', 'fa': 'آسم', 'ar': 'الربو'},
    'de artritis': {'ru': 'артрит', 'uk': 'артрит', 'es': 'artritis', 'pt': 'artrite', 'tr': 'artrit', 'fa': 'آرتریت', 'ar': 'التهاب المفاصل'},
    'de beroerte': {'ru': 'инсульт', 'uk': 'інсульт', 'es': 'derrame cerebral', 'pt': 'derrame', 'tr': 'felç', 'fa': 'سکته مغزی', 'ar': 'السكتة الدماغية'},
    'het hartinfarct': {'ru': 'инфаркт', 'uk': 'інфаркт серця', 'es': 'infarto', 'pt': 'infarto', 'tr': 'kalp krizi', 'fa': 'سکته قلبی', 'ar': 'النوبة القلبية'},
    'de kanker': {'ru': 'рак', 'uk': 'рак', 'es': 'cáncer', 'pt': 'câncer', 'tr': 'kanser', 'fa': 'سرطان', 'ar': 'السرطان'},
    
    'de behandeling': {'ru': 'лечение', 'uk': 'лікування', 'es': 'tratamiento', 'pt': 'tratamento', 'tr': 'tedavi', 'fa': 'درمان', 'ar': 'العلاج'},
    'de operatie': {'ru': 'операция', 'uk': 'операція', 'es': 'operación', 'pt': 'operação', 'tr': 'operasyon', 'fa': 'عمل جراحی', 'ar': 'العملية'},
    'het medicijn': {'ru': 'лекарство', 'uk': 'ліки', 'es': 'medicina', 'pt': 'medicamento', 'tr': 'ilaç', 'fa': 'دارو', 'ar': 'الدواء'},
    'het antibioticum': {'ru': 'антибиотик', 'uk': 'антибіотик', 'es': 'antibiótico', 'pt': 'antibiótico', 'tr': 'antibiyotik', 'fa': 'آنتی بیوتیک', 'ar': 'المضاد الحيوي'},
    'de injectie': {'ru': 'инъекция', 'uk': 'ін\'єкція', 'es': 'inyección', 'pt': 'injeção', 'tr': 'iğne', 'fa': 'тзریق', 'ar': 'الحقنة'},
    'de pil': {'ru': 'таблетка', 'uk': 'таблетка', 'es': 'píldora', 'pt': 'comprimido', 'tr': 'hap', 'fa': 'قرص', 'ar': 'الحبة'},
    'de zalf': {'ru': 'мазь', 'uk': 'мазь', 'es': 'pomada', 'pt': 'pomada', 'tr': 'merhem', 'fa': 'پماد', 'ar': 'المرهم'},
    'de fysiotherapie': {'ru': 'физиотерапия', 'uk': 'фізіотерапія', 'es': 'fisioterapia', 'pt': 'fisioterapia', 'tr': 'fizyoterapia', 'fa': 'فیزیوتراپی', 'ar': 'العلاج الطبيعي'},
    'de radiotherapie': {'ru': 'радиотерапия', 'uk': 'радіотерапія', 'es': 'radioterapia', 'pt': 'radioterapia', 'tr': 'radyoterapi', 'fa': 'پرتودرمانی', 'ar': 'العلاج الإشعاعي'},
    'de chirurgie': {'ru': 'хирургия', 'uk': 'хірургія', 'es': 'cirugía', 'pt': 'cirurgia', 'tr': 'cerrahi', 'fa': 'جراحی', 'ar': 'الجراحة'},
    
    'de tand': {'ru': 'зуб', 'uk': 'зуб', 'es': 'diente', 'pt': 'dente', 'tr': 'diş', 'fa': 'دندان', 'ar': 'السن'},
    'de kies': {'ru': 'коренной зуб', 'uk': 'корінний зуб', 'es': 'molar', 'pt': 'molar', 'tr': 'azı', 'fa': 'دندان آسیاب', 'ar': 'الطاحن'},
    'de snijtand': {'ru': 'резец', 'uk': 'різець', 'es': 'incisivo', 'pt': 'incisivo', 'tr': 'kesici diş', 'fa': 'دندان برنده', 'ar': 'القاطع'},
    'het tandvlees': {'ru': 'дёсна', 'uk': 'ясна', 'es': 'encía', 'pt': 'gengiva', 'tr': 'diş eti', 'fa': 'لثه', 'ar': 'اللثة'},
    'de cariës': {'ru': 'кариес', 'uk': 'карієс', 'es': 'caries', 'pt': 'cárie', 'tr': 'çürük', 'fa': 'پوسیدگی دندان', 'ar': 'التسوس'},
    'de parodontitis': {'ru': 'пародонтит', 'uk': 'пародонтит', 'es': 'periodontitis', 'pt': 'periodontite', 'tr': 'periodontit', 'fa': 'پریودنتیت', 'ar': 'التهاب دواعم السن'},
    'de tandborstel': {'ru': 'зубная щетка', 'uk': 'зубна щітка', 'es': 'cepillo de dientes', 'pt': 'escova de dentes', 'tr': 'diş fırцыası', 'fa': 'مسواک', 'ar': 'فرشاة الأسنان'},
    'de tandpasta': {'ru': 'зубная паста', 'uk': 'зубна паста', 'es': 'pasta de dientes', 'pt': 'pasta de dentes', 'tr': 'diş macunu', 'fa': 'خمیردندان', 'ar': 'معجون الأسنان'},
    'de vulling': {'ru': 'пломба', 'uk': 'пломба', 'es': 'empaste', 'pt': 'obturação', 'tr': 'dolgu', 'fa': 'پرکردگی', 'ar': 'الحشو'},
    'de kroon': {'ru': 'коронка', 'uk': 'коронка', 'es': 'corona', 'pt': 'coroa', 'tr': 'taç', 'fa': 'تاج دندان', 'ar': 'التاج'},

    # ADVANCED_TERMS (50)
    # ANATOMY_ADVANCED - 10
    'het cerebellum': {'ru': 'мозжечок', 'uk': 'мозочок', 'es': 'cerebelo', 'pt': 'cerebelo', 'tr': 'beyincik', 'fa': 'مخچه'},
    'de hypothalamus': {'ru': 'гипоталамус', 'uk': 'гіпоталамус', 'es': 'hipotálamo', 'pt': 'hipotálamo', 'tr': 'hipotalamus', 'fa': 'هیپوتالاموس'},
    'de oesofagus': {'ru': 'пищевод', 'uk': 'стравохід', 'es': 'esófago', 'pt': 'esôfago', 'tr': 'yemek borusu', 'fa': 'مری'},
    'de trachea': {'ru': 'трахея', 'uk': 'трахея', 'es': 'tráquea', 'pt': 'traqueia', 'tr': 'soluk borusu', 'fa': 'نای'},
    'het pericardium': {'ru': 'перикард', 'uk': 'перикард', 'es': 'pericardio', 'pt': 'pericárdio', 'tr': 'perikard', 'fa': 'پریکارد'},
    'de glomerulus': {'ru': 'клубочек', 'uk': 'клубочок', 'es': 'glomérulo', 'pt': 'glomérulo', 'tr': 'glomerulus', 'fa': 'گلومرول'},
    'de wervelkolom': {'ru': 'позвоночник', 'uk': 'хребет', 'es': 'columna vertebral', 'pt': 'coluna vertebral', 'tr': 'omurga', 'fa': 'ستون فقرات'},
    'de aorta': {'ru': 'аорта', 'uk': 'аорта', 'es': 'aorta', 'pt': 'aorta', 'tr': 'aort', 'fa': 'آئورت'},
    'het duodenum': {'ru': 'двенадцатиперстная кишка', 'uk': 'дванадцятипала кишка', 'es': 'duodeno', 'pt': 'duodeno', 'tr': 'onikiparmak bağırsağı', 'fa': 'دوازدهه'},
    'de bijnier': {'ru': 'надпочечник', 'uk': 'наднирник', 'es': 'glándula suprarrenal', 'pt': 'glândula adrenal', 'tr': 'böbrek üstü bezi', 'fa': 'غده فوق کلیوی'},
    
    # PATHOLOGY - 10
    'de sclerodermie': {'ru': 'склеродермия', 'uk': 'склеродермія', 'es': 'esclerodermia', 'pt': 'esclerodermia', 'tr': 'skleroderma', 'fa': 'اسکلرودرمی'},
    'de trombose': {'ru': 'тромбоз', 'uk': 'тромбоз', 'es': 'trombosis', 'pt': 'trombose', 'tr': 'tromboz', 'fa': 'ترومبوز'},
    'de myocarditis': {'ru': 'миокардит', 'uk': 'міокардит', 'es': 'miocarditis', 'pt': 'miocardite', 'tr': 'miyokardit', 'fa': 'میوکاردیت'},
    'de nefropathie': {'ru': 'нефропатия', 'uk': 'нефропатія', 'es': 'nefropatía', 'pt': 'nefropatia', 'tr': 'nefropati', 'fa': 'نفروپاتی'},
    'de encefalopathie': {'ru': 'энцефалопатия', 'uk': 'енцефалопатія', 'es': 'encefalopatía', 'pt': 'encefalopatia', 'tr': 'ensefalopati', 'fa': 'آنسفالوپاتی'},
    'de hyperthyreoïdie': {'ru': 'гипертиреоз', 'uk': 'гіпертиреоз', 'es': 'hipertiroidismo', 'pt': 'hipertireoidismo', 'tr': 'hipertiroidi', 'fa': 'پرکاری تیروئید'},
    'het sarcoom': {'ru': 'саркома', 'uk': 'саркома', 'es': 'sarcoma', 'pt': 'sarcoma', 'tr': 'sarkom', 'fa': 'سارکوم'},
    'de cirrose': {'ru': 'цирроз', 'uk': 'цироз', 'es': 'cirrosis', 'pt': 'cirrose', 'tr': 'siroz', 'fa': 'سیروز'},
    'de diverticulitis': {'ru': 'дивертикулит', 'uk': 'дивертикуліт', 'es': 'diverticulitis', 'pt': 'diverticulite', 'tr': 'divertikülit', 'fa': 'دیورتیکولیت'},
    'de polyneuropathie': {'ru': 'полинейропатия', 'uk': 'полінейропатія', 'es': 'polineuropatía', 'pt': 'polineuropatia', 'tr': 'polinöropati', 'fa': 'پلی‌نوروپاتی'},
    
    # DIAGNOSTICS_PROCEDURES - 10
    'de biopsie': {'ru': 'биопсия', 'uk': 'біопсія', 'es': 'biopsia', 'pt': 'biópsia', 'tr': 'biyopsi', 'fa': 'بیوپسی'},
    'de echografie': {'ru': 'эхография', 'uk': 'ехографія', 'es': 'ecografía', 'pt': 'ecografia', 'tr': 'ultrasonografi', 'fa': 'سونوگرافی'},
    'de endoscopie': {'ru': 'эндоскопия', 'uk': 'ендоскопія', 'es': 'endoscopia', 'pt': 'endoscopia', 'tr': 'endoskopi', 'fa': 'آندوسکوپی'},
    'de auscultatie': {'ru': 'аускультация', 'uk': 'аускультація', 'es': 'auscultación', 'pt': 'ausculta', 'tr': 'oskültasyon', 'fa': 'سمع'},
    'de palpatie': {'ru': 'пальпация', 'uk': 'пальпація', 'es': 'palpación', 'pt': 'palpação', 'tr': 'palpasyon', 'fa': 'لمس'},
    'het elektrocardiogram (ECG)': {'ru': 'электрокардиограмма (ЭКГ)', 'uk': 'електрокардіограма (ЕКГ)', 'es': 'electrocardiograma (ECG)', 'pt': 'eletrocardiograma (ECG)', 'tr': 'elektrokardiyogram (EKG)', 'fa': 'الکتروکاردیوگرام (ECG)'},
    'de venapunctie': {'ru': 'венепункция', 'uk': 'венепункція', 'es': 'venopunción', 'pt': 'venopunção', 'tr': 'venipuncture', 'fa': 'رگ‌گیری'},
    'de reanimatie': {'ru': 'реанимация', 'uk': 'реанімація', 'es': 'reanimación', 'pt': 'reanimação', 'tr': 'resüsitasyon', 'fa': 'احیا'},
    'de intubatie': {'ru': 'интубация', 'uk': 'інтубація', 'es': 'intubación', 'pt': 'intubação', 'tr': 'entübasyon', 'fa': 'لوله گذاری'},
    'het consult': {'ru': 'консультация', 'uk': 'консультація', 'es': 'consulta', 'pt': 'consulta', 'tr': 'konsültasyon', 'fa': 'مشاوره'},
    
    # PHARMACOLOGY - 10
    'de analgetica': {'ru': 'анальгетики', 'uk': 'анальгетики', 'es': 'analgésicos', 'pt': 'analgésicos', 'tr': 'analjezikler', 'fa': 'مسکن‌ها'},
    'de anticoagulantia': {'ru': 'антикоагулянты', 'uk': 'антикоагулянти', 'es': 'anticoagulantes', 'pt': 'anticoagulantes', 'tr': 'antikoagülanlar', 'fa': 'داروهای ضد انعقاد'},
    'de cytostatica': {'ru': 'цитостатики', 'uk': 'цитостатики', 'es': 'citostáticos', 'pt': 'citostáticos', 'tr': 'sitostatikler', 'fa': 'داروهای سیتواستاتیک'},
    'de diuretica': {'ru': 'диуретики', 'uk': 'діуретики', 'es': 'diuréticos', 'pt': 'diuréticos', 'tr': 'diüretikler', 'fa': 'دیورتیک‌ها'},
    'de sedativa': {'ru': 'седативные средства', 'uk': 'седативні засоби', 'es': 'sedantes', 'pt': 'sedativos', 'tr': 'sedatifler', 'fa': 'آرامبخش‌ها'},
    'de vasoconstrictie': {'ru': 'вазоконстрикция', 'uk': 'вазоконстрикція', 'es': 'vasoconstricción', 'pt': 'vasoconstrição', 'tr': 'vazokonstriksiyon', 'fa': 'انقباض عروقی'},
    'de farmacokinetiek': {'ru': 'фармакокинетика', 'uk': 'фармакокінетика', 'es': 'farmacocinética', 'pt': 'farmacocinética', 'tr': 'farmakokinetik', 'fa': 'فارماکوکینتیک'},
    'de werkingsmechanisme': {'ru': 'механизм действия', 'uk': 'механізм дії', 'es': 'mecanismo de acción', 'pt': 'mecanismo de ação', 'tr': 'etki mekanizması', 'fa': 'مکانیسم اثر'},
    'de dosering': {'ru': 'дозировка', 'uk': 'дозування', 'es': 'dosificación', 'pt': 'dosagem', 'tr': 'dozaj', 'fa': 'دوز'},
    'de contra-indicatie': {'ru': 'противопоказание', 'uk': 'протипоказання', 'es': 'contraindicación', 'pt': 'contraindicação', 'tr': 'kontrendikasyon', 'fa': 'منع مصرف'},
    
    # SYMPTOMATOLOGY_ADVANCED - 10
    'de dyspneu': {'ru': 'одышка', 'uk': 'задишка', 'es': 'disnea', 'pt': 'dispneia', 'tr': 'dispne', 'fa': 'تنگی نفس'},
    'de hemoptyse': {'ru': 'кровохарканье', 'uk': 'кровохаркання', 'es': 'hemoptisis', 'pt': 'hemoptise', 'tr': 'hemoptizi', 'fa': 'خلط خونی'},
    'de paresthesie': {'ru': 'парестезия', 'uk': 'парестезія', 'es': 'parestesia', 'pt': 'parestesia', 'tr': 'parestezi', 'fa': 'پارستزی'},
    'het oedeem': {'ru': 'отёк', 'uk': 'набряк', 'es': 'edema', 'pt': 'edema', 'tr': 'ödem', 'fa': 'ادم'},
    'de tachycardie': {'ru': 'тахикардия', 'uk': 'тахікардія', 'es': 'taquicardia', 'pt': 'taquicardia', 'tr': 'taşikardi', 'fa': 'تاکی‌کاردی'},
    'de malaise': {'ru': 'недомогание', 'uk': 'нездужання', 'es': 'malestar', 'pt': 'mal-estar', 'tr': 'halsizlik', 'fa': 'کسالت'},
    'de icterus': {'ru': 'желтуха', 'uk': 'жовтяниця', 'es': 'ictericia', 'pt': 'icterícia', 'tr': 'ikter', 'fa': 'یرقان'},
    'de convulsie': {'ru': 'судорога', 'uk': 'судома', 'es': 'convulsión', 'pt': 'convulsão', 'tr': 'konvülsiyon', 'fa': 'تشنج'},
    'de asfyxie': {'ru': 'асфиксия', 'uk': 'асфіксія', 'es': 'asfixia', 'pt': 'asfixia', 'tr': 'asfiksi', 'fa': 'خفگی'},
    'de retentie': {'ru': 'задержка', 'uk': 'затримка', 'es': 'retención', 'pt': 'retenção', 'tr': 'retansiyon', 'fa': 'احتباس'},

    # ULTRA_ADVANCED_TERMS (50)
    # PATHOPHYSIOLOGY_RARE - 10
    'de anafylaxie': {'ru': 'анафилаксия', 'uk': 'анафілаксія', 'es': 'anafilaxia', 'pt': 'anafilaxia', 'tr': 'anafilaksi', 'fa': 'آنافیلاکسی'},
    'de ischemie': {'ru': 'ишемия', 'uk': 'ішемія', 'es': 'isquemia', 'pt': 'isquemia', 'tr': 'iskemi', 'fa': 'ایسکمی'},
    'de hypoxie': {'ru': 'гипоксия', 'uk': 'гіпоксія', 'es': 'hipoxia', 'pt': 'hipóxia', 'tr': 'hipoksi', 'fa': 'هیپوکسی'},
    'de disseminated intravasculaire stolling (DIS)': {'ru': 'диссеминированное внутрисосудистое свертывание (ДВС)', 'uk': 'дисеміноване внутрішньосудинне згортання (ДВС)', 'es': 'coagulación intravascular diseminada (CID)', 'pt': 'coagulação intravascular disseminada (CIVD)', 'tr': 'dissemine intravasküler koagülasyon (DIC)', 'fa': 'انعقاد درون‌رگی منتشر (DIC)'},
    'de maligniteit': {'ru': 'злокачественность', 'uk': 'злоякісність', 'es': 'malignidad', 'pt': 'malignidade', 'tr': 'malignite', 'fa': 'بدخیمی'},
    'de sepsis': {'ru': 'сепсис', 'uk': 'сепсис', 'es': 'sepsis', 'pt': 'sepse', 'tr': 'sepsis', 'fa': 'سپسیس'},
    'het longoedeem': {'ru': 'отек легких', 'uk': 'набряк легень', 'es': 'edema pulmonar', 'pt': 'edema pulmonar', 'tr': 'pulmoner ödem', 'fa': 'ادم ریوی'},
    'de hematoom': {'ru': 'гематома', 'uk': 'гематома', 'es': 'hematoma', 'pt': 'hematoma', 'tr': 'hematom', 'fa': 'هماتوم'},
    'de metastase': {'ru': 'метастаз', 'uk': 'метастаз', 'es': 'metástasis', 'pt': 'metástase', 'tr': 'metastaz', 'fa': 'متاستاز'},
    'de atrofie': {'ru': 'атрофия', 'uk': 'атрофія', 'es': 'atrofia', 'pt': 'atrofia', 'tr': 'atrofi', 'fa': 'آتروفی'},
    
    # INTERVENTION_SURGERY - 10
    'de laparoscopie': {'ru': 'лапароскопия', 'uk': 'лапароскопія', 'es': 'laparoscopia', 'pt': 'laparoscopia', 'tr': 'laparoskopi', 'fa': 'لاپاراسکوپی'},
    'de stentplaatsing': {'ru': 'стентирование', 'uk': 'стент', 'es': 'colocación de stent', 'pt': 'colocação de stent', 'tr': 'stent yerleştirme', 'fa': 'قرار دادن استنت'},
    'de tracheostomie': {'ru': 'трахеостомия', 'uk': 'трахеостомія', 'es': 'traqueostomía', 'pt': 'traqueostomia', 'tr': 'trakeostomi', 'fa': 'تراکئوستومی'},
    'de nefrectomie': {'ru': 'нефрэктомия', 'uk': 'нефректомія', 'es': 'nefrectomía', 'pt': 'nefrectomia', 'tr': 'nefrektomi', 'fa': 'نفرکتومی'},
    'de arteriografie': {'ru': 'артериография', 'uk': 'артеріографія', 'es': 'arteriografía', 'pt': 'arteriografia', 'tr': 'arteriyografi', 'fa': 'آرتریوگرافی'},
    'de profylaxe': {'ru': 'профилактика', 'uk': 'профілактика', 'es': 'profilaxis', 'pt': 'profilaxia', 'tr': 'profilaksi', 'fa': 'پیشگیری'},
    'de exsudatie': {'ru': 'экссудация', 'uk': 'ексудація', 'es': 'exudación', 'pt': 'exsudação', 'tr': 'eksüdasyon', 'fa': 'ترشح'},
    'de ablatie': {'ru': 'абляция', 'uk': 'абляція', 'es': 'ablación', 'pt': 'ablação', 'tr': 'ablasyon', 'fa': 'ابلیشن'},
    'de anesthesiologie': {'ru': 'анестезиология', 'uk': 'анестезіологія', 'es': 'anestesiología', 'pt': 'anestesiologia', 'tr': 'anesteziyoloji', 'fa': 'بیهوشی‌شناسی'},
    'de vitrectomie': {'ru': 'витрэктомия', 'uk': 'вітректомія', 'es': 'vitrectomía', 'pt': 'vitrectomia', 'tr': 'vitrektomi', 'fa': 'ویترکتومی'},
    
    # NEURO_PSYCHO - 10
    'de parese': {'ru': 'парез', 'uk': 'парез', 'es': 'paresia', 'pt': 'paresia', 'tr': 'parezi', 'fa': 'فلج جزئی'},
    'de dysfagie': {'ru': 'дисфагия', 'uk': 'дисфагія', 'es': 'disfagia', 'pt': 'disfagia', 'tr': 'disfaji', 'fa': 'دیسفاژی'},
    'de afasie': {'ru': 'афазия', 'uk': 'афазія', 'es': 'afasia', 'pt': 'afasia', 'tr': 'afazi', 'fa': 'آفازی'},
    'de dementie': {'ru': 'деменция', 'uk': 'деменція', 'es': 'demencia', 'pt': 'demência', 'tr': 'demans', 'fa': 'زوال عقل'},
    'de convulsieve stoornis': {'ru': 'судорожное расстройство', 'uk': 'судомний розлад', 'es': 'trastorno convulsivo', 'pt': 'transtorno convulsivo', 'tr': 'konvülsif bozukluk', 'fa': 'اختلال تشنجی'},
    'de neurotransmitter': {'ru': 'нейромедиатор', 'uk': 'нейромедіатор', 'es': 'neurotransmisor', 'pt': 'neurotransmissor', 'tr': 'nörotransmitter', 'fa': 'انتقال دهنده عصبی'},
    'de somatische stoornis': {'ru': 'соматическое расстройство', 'uk': 'соматичний розлад', 'es': 'trastorno somático', 'pt': 'transtorno somático', 'tr': 'somatik bozukluk', 'fa': 'اختلال جسمانی'},
    'de psychose': {'ru': 'психоз', 'uk': 'психоз', 'es': 'psicosis', 'pt': 'psicose', 'tr': 'psikoz', 'fa': 'روان‌پریشی'},
    'de depressieve episode': {'ru': 'депрессивный эпизод', 'uk': 'депресивний епізод', 'es': 'episodio depresivo', 'pt': 'episódio depressivo', 'tr': 'depresif dönem', 'fa': 'دوره افسردگی'},
    'de hallucinatie': {'ru': 'галлюцинация', 'uk': 'галюцинація', 'es': 'alucinación', 'pt': 'alucinação', 'tr': 'halüsinasyon', 'fa': 'توهم'},
    
    # CLINICAL_LATIN - 10
    'ad hoc': {'ru': 'ad hoc (специально для этого)', 'uk': 'ad hoc (спеціально для цього)', 'es': 'ad hoc', 'pt': 'ad hoc', 'tr': 'ad hoc', 'fa': 'برای این منظور'},
    'per se': {'ru': 'per se (по существу)', 'uk': 'per se (по суті)', 'es': 'per se', 'pt': 'per se', 'tr': 'per se', 'fa': 'به خودی خود'},
    'status quo': {'ru': 'status quo (существующее положение)', 'uk': 'status quo (існуючий стан)', 'es': 'status quo', 'pt': 'status quo', 'tr': 'status quo', 'fa': 'وضع موجود'},
    'de mortaliteit': {'ru': 'смертность', 'uk': 'смертність', 'es': 'mortalidad', 'pt': 'mortalidade', 'tr': 'mortalite', 'fa': 'مرگ و میر'},
    'de morbiditeit': {'ru': 'заболеваемость', 'uk': 'захворюваність', 'es': 'morbilidad', 'pt': 'morbidade', 'tr': 'morbidite', 'fa': 'عوارض'},
    'de incidentie': {'ru': 'заболеваемость', 'uk': 'захворюваність', 'es': 'incidencia', 'pt': 'incidência', 'tr': 'insidans', 'fa': 'میزان بروز'},
    'de prevalentie': {'ru': 'распространенность', 'uk': 'поширеність', 'es': 'prevalencia', 'pt': 'prevalência', 'tr': 'prevalans', 'fa': 'شیوع'},
    'de ethiologie': {'ru': 'этиология', 'uk': 'етіологія', 'es': 'etiología', 'pt': 'etiologia', 'tr': 'etiyoloji', 'fa': 'علت بیماری'},
    'in situ': {'ru': 'in situ (на месте)', 'uk': 'in situ (на місці)', 'es': 'in situ', 'pt': 'in situ', 'tr': 'in situ', 'fa': 'در محل اصلی'},
    'ex vivo': {'ru': 'ex vivo (вне организма)', 'uk': 'ex vivo (поза організмом)', 'es': 'ex vivo', 'pt': 'ex vivo', 'tr': 'ex vivo', 'fa': 'خارج از بدن'},
    
    # RARE_ANATOMY_GENETICS - 10
    'het axon': {'ru': 'аксон', 'uk': 'аксон', 'es': 'axón', 'pt': 'axônio', 'tr': 'akson', 'fa': 'آکسون'},
    'de dendriet': {'ru': 'дендрит', 'uk': 'дендрит', 'es': 'dendrita', 'pt': 'dendrito', 'tr': 'dendrit', 'fa': 'دندریت'},
    'de mitochondriën (mv.)': {'ru': 'митохондрии (мн.)', 'uk': 'мітохондрії (мн.)', 'es': 'mitocondrias (pl.)', 'pt': 'mitocôndrias (pl.)', 'tr': 'mitokondri', 'fa': 'میتوکندری'},
    'het genoom': {'ru': 'геном', 'uk': 'геном', 'es': 'genoma', 'pt': 'genoma', 'tr': 'genom', 'fa': 'ژنوم'},
    'de karyotype': {'ru': 'кариотип', 'uk': 'каріотип', 'es': 'cariotipo', 'pt': 'cariótipo', 'tr': 'karyotip', 'fa': 'کاریوتیپ'},
    'de hypofyse': {'ru': 'гипофиз', 'uk': 'гіпофіз', 'es': 'glándula pituitaria', 'pt': 'hipófise', 'tr': 'hipofiz', 'fa': 'هیپوفیز'},
    'de thyroïd': {'ru': 'щитовидная железа', 'uk': 'щитоподібна залоза', 'es': 'glándula tiroides', 'pt': 'tireoide', 'tr': 'tiroid bezi', 'fa': 'غده تیروئید'},
    'de ductus arteriosus': {'ru': 'артериальный проток', 'uk': 'артеріальна протока', 'es': 'conducto arterioso', 'pt': 'ducto arterioso', 'tr': 'duktus arteriosus', 'fa': 'مجرای شریانی'},
    'de vena cava': {'ru': 'полая вена', 'uk': 'порожниста вена', 'es': 'vena cava', 'pt': 'veia cava', 'tr': 'vena kava', 'fa': 'ورید اجوف'},
    'de pleuraholte': {'ru': 'плевральная полость', 'uk': 'плевральна порожнина', 'es': 'cavidad pleural', 'pt': 'cavidade pleural', 'tr': 'plevra boşluğu', 'fa': 'пространство плевры'},

    # EXPERT_TERMS (50)
    # EPIDEMIOLOGY_STATISTICS - 10
    'de cohortstudie': {'ru': 'когортное исследование', 'uk': 'когортне дослідження', 'es': 'estudio de cohorte', 'pt': 'estudo de coorte', 'tr': 'kohort çalışması', 'fa': 'مطالعه کوهورت'},
    'de bias (vertekening)': {'ru': 'систематическая ошибка (смещение)', 'uk': 'упередження (зміщення)', 'es': 'sesgo', 'pt': 'viés', 'tr': 'sapma (önyargı)', 'fa': 'سوگیری'},
    'de confounding factor': {'ru': 'вмешивающийся фактор', 'uk': 'змішуючий фактор', 'es': 'factor de confusión', 'pt': 'fator de confusão', 'tr': 'karıştırıcı faktör', 'fa': 'عامل مخدوش کننده'},
    'de randomisatie': {'ru': 'рандомизация', 'uk': 'рандомізація', 'es': 'aleatorización', 'pt': 'randomização', 'tr': 'randomizasyon', 'fa': 'تصادفی سازی'},
    'de significantie': {'ru': 'значимость', 'uk': 'значущість', 'es': 'significancia', 'pt': 'significância', 'tr': 'anlamlılık', 'fa': 'значимость'},
    'de hazard ratio': {'ru': 'отношение рисков', 'uk': 'відношення ризиків', 'es': 'razón de riesgo', 'pt': 'razão de risco', 'tr': 'tehlike oranı', 'fa': 'نسبت خطر'},
    'de regressie-analyse': {'ru': 'регрессионный анализ', 'uk': 'регресійний аналіз', 'es': 'análisis de regresión', 'pt': 'análise de regressão', 'tr': 'regresyon analizi', 'fa': 'تحلیل رگرسیون'},
    'de incidentiecijfer': {'ru': 'коэффициент заболеваемости', 'uk': 'показник захворюваності', 'es': 'tasa de incidencia', 'pt': 'taxa de incidência', 'tr': 'insidans hızı', 'fa': 'نرخ بروز'},
    'de validiteit': {'ru': 'валидность', 'uk': 'валідність', 'es': 'validez', 'pt': 'validade', 'tr': 'geçerlilik', 'fa': 'اعتبار'},
    'de betrouwbaarheid': {'ru': 'надежность', 'uk': 'надійність', 'es': 'fiabilidad', 'pt': 'confiabilidade', 'tr': 'güvenilirlik', 'fa': 'پایایی'},

    # ETHICS_LAW - 10
    'de informed consent': {'ru': 'информированное согласие', 'uk': 'інформована згода', 'es': 'consentimiento informado', 'pt': 'consentimento informado', 'tr': 'bilgilendirilmiş onam', 'fa': 'رضایت آگاهانه'},
    'de autonomie': {'ru': 'автономия', 'uk': 'автономія', 'es': 'autonomía', 'pt': 'autonomia', 'tr': 'özerklik', 'fa': 'استقلال'},
    'de non-maleficence': {'ru': 'непричинение вреда', 'uk': 'не шкодити', 'es': 'no maleficencia', 'pt': 'não maleficência', 'tr': 'zarar vermeme', 'fa': 'عدم بدخواهی'},
    'de vertrouwelijkheid': {'ru': 'конфиденциальность', 'uk': 'конфіденційність', 'es': 'confidencialidad', 'pt': 'confidencialidade', 'tr': 'gizlilik', 'fa': 'محرمانگی'},
    'de palliatieve zorg': {'ru': 'паллиативная помощь', 'uk': 'паліативна допомога', 'es': 'cuidados paliativos', 'pt': 'cuidados paliativos', 'tr': 'palyatif bakım', 'fa': 'مراقبت تسکینی'},
    'de euthanasie': {'ru': 'эвтаназия', 'uk': 'евтаназия', 'es': 'eutanasia', 'pt': 'eutanásia', 'tr': 'ötanazi', 'fa': 'اتانازی'},
    'de medische aansprakelijkheid': {'ru': 'медицинская ответственность', 'uk': 'медична відповідальність', 'es': 'responsabilidad médica', 'pt': 'responsabilidade médica', 'tr': 'tıbbi sorumluluk', 'fa': 'مسئولیت پزشکی'},
    'de second opinion': {'ru': 'второе мнение', 'uk': 'друга думка', 'es': 'segunda opinión', 'pt': 'segunda opinião', 'tr': 'ikinci görüş', 'fa': 'نظر دوم'},
    'de zorgstandaard': {'ru': 'стандарт ухода', 'uk': 'стандарт догляду', 'es': 'estándar de atención', 'pt': 'padrão de cuidado', 'tr': 'bakım standardı', 'fa': 'استاندارد مراقبت'},
    'de triage': {'ru': 'сортировка (триаж)', 'uk': 'сортування (тріаж)', 'es': 'triaje', 'pt': 'triagem', 'tr': 'triyaj', 'fa': 'تریاژ'},

    # ADVANCED_IMAGING - 10
    'de magnetische resonantiebeeldvorming (MRI)': {'ru': 'магнитно-резонансная томография (МРТ)', 'uk': 'магнітно-резонансна томографія (МРТ)', 'es': 'resonancia magnética (RM)', 'pt': 'ressonância magnética (RM)', 'tr': 'manyetik rezonans görüntüleme (MRG)', 'fa': 'تصویربرداری تشدید مغناطیسی (MRI)'},
    'de computertomografie (CT)': {'ru': 'компьютерная томография (КТ)', 'uk': 'комп\'ютерна томографія (КТ)', 'es': 'tomografía computarizada (TC)', 'pt': 'tomografia computadorizada (TC)', 'tr': 'bilgisayarlı tomografi (BT)', 'fa': 'توموگرافی کامپیوتری (CT)'},
    'de nucleaire geneeskunde': {'ru': 'ядерная медицина', 'uk': 'ядерна медицина', 'es': 'medicina nuclear', 'pt': 'medicina nuclear', 'tr': 'nükleer tıp', 'fa': 'پزشکی هسته‌ای'},
    'het scintigram': {'ru': 'сцинтиграмма', 'uk': 'сцинтиграма', 'es': 'centellograma', 'pt': 'cintilograma', 'tr': 'sintigram', 'fa': 'اسکن هسته‌ای'},
    'de perfusie': {'ru': 'перфузия', 'uk': 'перфузія', 'es': 'perfusión', 'pt': 'perfusão', 'tr': 'perfüzyon', 'fa': 'پرفیوژن'},
    'de resolutie': {'ru': 'разрешение', 'uk': 'роздільна здатність', 'es': 'resolución', 'pt': 'resolução', 'tr': 'çözünürlük', 'fa': 'وضوح'},
    'de radio-opaciteit': {'ru': 'радиоплотность', 'uk': 'радіощільність', 'es': 'radiopacidad', 'pt': 'radiopacidade', 'tr': 'radyopaklık', 'fa': 'رادیواپاسیتی'},
    'het contrastmiddel': {'ru': 'контрастное вещество', 'uk': 'контрастна речовина', 'es': 'medio de contraste', 'pt': 'agente de contraste', 'tr': 'kontrast madde', 'fa': 'ماده حاجب'},
    'de echogeniteit': {'ru': 'эхогенность', 'uk': 'ехогенність', 'es': 'ecogenicidad', 'pt': 'ecogenicidade', 'tr': 'ekojenite', 'fa': 'اکوژنیسیته'},
    'de laesie': {'ru': 'поражение (очаг)', 'uk': 'ураження', 'es': 'lesión', 'pt': 'lesão', 'tr': 'lezyon', 'fa': 'ضایعه'},

    # MOLECULAR_GENETICS - 10
    'de transcriptie': {'ru': 'транскрипция', 'uk': 'транскрипція', 'es': 'transcripción', 'pt': 'transcrição', 'tr': 'transkripsiyon', 'fa': 'رونویسی'},
    'de translatie': {'ru': 'трансляция', 'uk': 'трансляція', 'es': 'traducción', 'pt': 'tradução', 'tr': 'translasyon', 'fa': 'ترجمه'},
    'de mutatie': {'ru': 'мутация', 'uk': 'мутація', 'es': 'mutación', 'pt': 'mutação', 'tr': 'mutasyon', 'fa': 'جهش'},
    'de allel': {'ru': 'аллель', 'uk': 'алель', 'es': 'alelo', 'pt': 'alelo', 'tr': 'alel', 'fa': 'آلل'},
    'de recombinatie': {'ru': 'рекомбинация', 'uk': 'рекомбінація', 'es': 'recombinación', 'pt': 'recombinação', 'tr': 'rekombinasyon', 'fa': 'نوترکیبی'},
    'de apoptose': {'ru': 'апоптоз', 'uk': 'апоптоз', 'es': 'apoptosis', 'pt': 'apoptose', 'tr': 'apoptoz', 'fa': 'آپوپتوز'},
    'de differentiatie': {'ru': 'дифференциация', 'uk': 'диференціація', 'es': 'diferenciación', 'pt': 'diferenciação', 'tr': 'farklılaşma', 'fa': 'تمایز'},
    'de immunoglobuline': {'ru': 'иммуноглобулин', 'uk': 'імуноглобулін', 'es': 'inmunoglobulina', 'pt': 'imunoglobulina', 'tr': 'immünoglobulin', 'fa': 'ایمونوگلوبولین'},
    'de cytokine': {'ru': 'цитокин', 'uk': 'цитокін', 'es': 'citoquina', 'pt': 'citocina', 'tr': 'sitokin', 'fa': 'سیتوکین'},
    'de receptor': {'ru': 'рецептор', 'uk': 'рецептор', 'es': 'receptor', 'pt': 'receptor', 'tr': 'reseptör', 'fa': 'گیرنده'},

    # COMPLEX_CLINICAL_SYNDROMES - 10
    'de Guillain-Barré syndroom': {'ru': 'синдром Гийена-Барре', 'uk': 'синдром Гієна-Барре', 'es': 'síndrome de Guillain-Barré', 'pt': 'síndrome de Guillain-Barré', 'tr': 'Guillain-Barré sendromu', 'fa': 'سندرم گیلن باره'},
    'de chronische obstructieve longziekte (COPD)': {'ru': 'хроническая обструктивная болезнь легких (ХОБЛ)', 'uk': 'хронічна обструктивна хвороба легень (ХОЗЛ)', 'es': 'enfermedad pulmonar obstructiva crónica (EPOC)', 'pt': 'doença pulmonar obstrutiva crônica (DPOC)', 'tr': 'kronik obstrüktif akciğer hastalığı (KOAH)', 'fa': 'بیماری مزمن انسدادی ریه (COPD)'},
    'de congenitale afwijking': {'ru': 'врожденный порок', 'uk': 'вроджена аномалія', 'es': 'anomalía congénita', 'pt': 'anomalia congênita', 'tr': 'konjenital anomali', 'fa': 'ناهنجاری مادرزادی'},
    'de respiratoire insufficiëntie': {'ru': 'дыхательная недостаточность', 'uk': 'дихальна недостатність', 'es': 'insuficiencia respiratoria', 'pt': 'insuficiência respiratória', 'tr': 'solunum yetmezliği', 'fa': 'نارسایی تنفسی'},
    'de metabool syndroom': {'ru': 'метаболический синдром', 'uk': 'метаболічний синдром', 'es': 'síndrome metabólico', 'pt': 'síndrome metabólica', 'tr': 'metabolik sendrom', 'fa': 'سندرم متابولیک'},
    'de inflammatoire respons': {'ru': 'воспалительная реакция', 'uk': 'запальна відповідь', 'es': 'respuesta inflamatoria', 'pt': 'resposta inflamatória', 'tr': 'inflamatuar yanıt', 'fa': 'پاسخ التهابی'},
    'de prognose': {'ru': 'прогноз', 'uk': 'прогноз', 'es': 'pronóstico', 'pt': 'prognóstico', 'tr': 'prognoz', 'fa': 'پیش آگهی'},
    'de remissie': {'ru': 'ремиссия', 'uk': 'ремісія', 'es': 'remisión', 'pt': 'remissão', 'tr': 'remisyon', 'fa': 'بهبودی'},
    'de exacerbatie': {'ru': 'обострение', 'uk': 'загострення', 'es': 'exacerbación', 'pt': 'exacerbação', 'tr': 'alevlenme', 'fa': 'تشدید'},
    'de recidief': {'ru': 'рецидив', 'uk': 'рецидив', 'es': 'recidiva', 'pt': 'recidiva', 'tr': 'nüks', 'fa': 'عود'},

    # ULTRA_ELITE_TERMS (50)
    # IMMUNOLOGY_VIROLOGY - 10
    'de auto-immuniteit': {'ru': 'аутоиммунитет', 'uk': 'аутоімунітет', 'es': 'autoinmunidad', 'pt': 'autoimunidade', 'tr': 'otoimmünite', 'fa': 'خودایمنی'},
    'de immunocompetentie': {'ru': 'иммунокомпетентность', 'uk': 'імунокомпетентність', 'es': 'inmunocompetencia', 'pt': 'imunocompetência', 'tr': 'immün yeterlilik', 'fa': 'ایمنی صلاحیت'},
    'het antigeen': {'ru': 'антиген', 'uk': 'антиген', 'es': 'antígeno', 'pt': 'antígeno', 'tr': 'antijen', 'fa': 'آنتی‌ژن'},
    'het epitoop': {'ru': 'эпитоп', 'uk': 'епітоп', 'es': 'epítopo', 'pt': 'epítopo', 'tr': 'epitop', 'fa': 'اپیتوپ'},
    'de seroconversie': {'ru': 'сероконверсия', 'uk': 'сероконверсія', 'es': 'seroconversión', 'pt': 'soroconversão', 'tr': 'serokonversiyon', 'fa': 'سر و کانورژن'},
    'de commensale flora': {'ru': 'комменсальная флора', 'uk': 'коменсальна флора', 'es': 'flora comensal', 'pt': 'flora comensal', 'tr': 'komensal flora', 'fa': 'فلور کمکی'},
    'de fagocytose': {'ru': 'фагоцитоз', 'uk': 'фагоцитоз', 'es': 'fagocitosis', 'pt': 'fagocitose', 'tr': 'fagositoz', 'fa': 'فاگوسیتوز'},
    'de interferon': {'ru': 'интерферон', 'uk': 'інтерферон', 'es': 'interferón', 'pt': 'interferon', 'tr': 'interferon', 'fa': 'اینترفرون'},
    'de T-cel lymfocyt': {'ru': 'Т-лимфоцит', 'uk': 'Т-лімфоцит', 'es': 'linfocito T', 'pt': 'linfócito T', 'tr': 'T-hücresi lenfositi', 'fa': 'لنفوسیت سلول T'},
    'de resistentie': {'ru': 'резистентность', 'uk': 'резистентність', 'es': 'resistencia', 'pt': 'resistência', 'tr': 'direnç', 'fa': 'مقاومت'},

    # LABORATORY_INDICATORS - 10
    'de creatinineklaring': {'ru': 'клиренс креатинина', 'uk': 'кліренс креатиніну', 'es': 'aclaramiento de creatinina', 'pt': 'clearance de creatinina', 'tr': 'kreatinin klirensi', 'fa': 'کلیرانس کراتینین'},
    'de alkalische fosfatase (AF)': {'ru': 'щелочная фосфатаза (ЩФ)', 'uk': 'лужна фосфатаза (ЛФ)', 'es': 'fosfatasa alcalina (FA)', 'pt': 'fosfatase alcalina (FA)', 'tr': 'alkalen fosfataz (ALP)', 'fa': 'آلکالین فسفاتاز (ALP)'},
    'de C-reactieve proteïne (CRP)': {'ru': 'С-реактивный белок (СРБ)', 'uk': 'С-реактивний білок (СРБ)', 'es': 'proteína C reactiva (PCR)', 'pt': 'proteína C reativa (PCR)', 'tr': 'C-reaktif protein (CRP)', 'fa': 'پروتئین واکنش‌گر C (CRP)'},
    'de HbA1c': {'ru': 'HbA1c', 'uk': 'HbA1c', 'es': 'HbA1c', 'pt': 'HbA1c', 'tr': 'HbA1c', 'fa': 'هموگلوبین A1c'},
    'de elektrolytenbalans': {'ru': 'электролитный баланс', 'uk': 'електролітний баланс', 'es': 'equilibrio electrolítico', 'pt': 'equilíbrio eletrolítico', 'tr': 'elektrolit dengesi', 'fa': 'تعادل الکترولیت'},
    'de osmolaliteit': {'ru': 'осмоляльность', 'uk': 'осмоляльність', 'es': 'osmolalidad', 'pt': 'osmolalidade', 'tr': 'ozmolalite', 'fa': 'اسمولالیته'},
    'de bilirubinemie': {'ru': 'билирубинемия', 'uk': 'білірубінемія', 'es': 'bilirubinemia', 'pt': 'bilirubinemia', 'tr': 'bilirubinemi', 'fa': 'بیلی روبین خون'},
    'de troponine': {'ru': 'тропонин', 'uk': 'тропонін', 'es': 'troponina', 'pt': 'troponina', 'tr': 'troponin', 'fa': 'تروپونین'},
    'de arteriële bloedgasanalyse (ABGA)': {'ru': 'анализ газов артериальной крови (АГАК)', 'uk': 'аналіз газів артеріальної крові (АГАК)', 'es': 'gasometría arterial', 'pt': 'gasometria arterial', 'tr': 'arteriyel kan gazı analizi (AKG)', 'fa': 'آنالیز گاز خون شریانی (ABG)'},
    'het sedimentatie': {'ru': 'скорость оседания эритроцитов (СОЭ)', 'uk': 'швидкість осідання еритроцитів (ШОЕ)', 'es': 'tasa de sedimentación', 'pt': 'taxa de sedimentação', 'tr': 'sedimantasyon hızı', 'fa': 'سرعت رسوب'},

    # PATHOGNOMONIC_SIGNS - 10
    'de anisocorie': {'ru': 'анизокория', 'uk': 'анізокорія', 'es': 'anisocoria', 'pt': 'anisocoria', 'tr': 'anizokori', 'fa': 'نابرابری مردمک'},
    'de asterixis': {'ru': 'астериксис (тремор)', 'uk': 'астериксіс', 'es': 'asterixis', 'pt': 'asterixis', 'tr': 'asteriksis', 'fa': 'آستریکسیس'},
    'het teken van Babinski': {'ru': 'симптом Бабинского', 'uk': 'симптом Бабінського', 'es': 'signo de Babinski', 'pt': 'sinal de Babinski', 'tr': 'Babinski belirtisi', 'fa': 'علامت بابینسکی'},
    'de hemianopsie': {'ru': 'гемианопсия', 'uk': 'геміанопсія', 'es': 'hemianopsia', 'pt': 'hemianopsia', 'tr': 'hemianopsi', 'fa': 'همی‌آنوپسی'},
    'de clonus': {'ru': 'клонус', 'uk': 'клонус', 'es': 'clonus', 'pt': 'clonus', 'tr': 'klonus', 'fa': 'کلونوس'},
    'de cachexie': {'ru': 'кахексия', 'uk': 'кахексія', 'es': 'caquexia', 'pt': 'caquexia', 'tr': 'kaşeksi', 'fa': 'کاشکسی'},
    'de nystagmus': {'ru': 'нистагм', 'uk': 'ністагм', 'es': 'nistagmo', 'pt': 'nistagmo', 'tr': 'nistagmus', 'fa': 'نیستاگموس'},
    'de diaphoresis': {'ru': 'диафорез (профузное потоотделение)', 'uk': 'діафорез', 'es': 'diaforesis', 'pt': 'diaforese', 'tr': 'diyaforez', 'fa': 'تعریق شدید'},
    'de facies hippocratica': {'ru': 'маска Гиппократа', 'uk': 'маска Гіппократа', 'es': 'facies hipocrática', 'pt': 'fácies hipocrática', 'tr': 'fasiyes hippocratica', 'fa': 'چهره هیپوکراتیک'},
    'de xanthelasma': {'ru': 'ксантелазма', 'uk': 'ксантелазма', 'es': 'xantelasma', 'pt': 'xantelasma', 'tr': 'kzantelazma', 'fa': 'زانتلاسما'},

    # RESEARCH_ACADEMIC - 10
    'de meta-analyse': {'ru': 'метаанализ', 'uk': 'мета-аналіз', 'es': 'metaanálisis', 'pt': 'meta-análise', 'tr': 'meta-analiz', 'fa': 'متاآنالیز'},
    'de p-waarde': {'ru': 'p-значение', 'uk': 'p-значення', 'es': 'valor p', 'pt': 'valor p', 'tr': 'p-değeri', 'fa': 'پی-والیو'},
    'de interkwartielafstand (IKA)': {'ru': 'межквартильный размах (МКР)', 'uk': 'міжквартильний діапазон', 'es': 'rango intercuartil (RIC)', 'pt': 'intervalo interquartil (IIQ)', 'tr': 'çeyrekler arası açıklık (IQR)', 'fa': 'دامنه بین چارکی (IQR)'},
    'de dubbelblinde studie': {'ru': 'двойное слепое исследование', 'uk': 'подвійне сліпе дослідження', 'es': 'estudio doble ciego', 'pt': 'estudo duplo-cego', 'tr': 'çift kör çalışma', 'fa': 'مطالعه دوسوکور'},
    'de placebogecontroleerde studie': {'ru': 'плацебо-контролируемое исследование', 'uk': 'плацебо-контрольоване дослідження', 'es': 'estudio controlado con placebo', 'pt': 'estudo controlado por placebo', 'tr': 'plasebo kontrollü çalışma', 'fa': 'مطالعه کنترل شده با دارونما'},
    'de confounding': {'ru': 'смешение (кофаундинг)', 'uk': 'кофаундинг (змішування)', 'es': 'confusión', 'pt': 'viés de confusão', 'tr': 'karıştırma', 'fa': 'مخدوش سازی'},
    'de farmacovigilantie': {'ru': 'фармаконадзор', 'uk': 'фармаконагляд', 'es': 'farmacovigilancia', 'pt': 'farmacovigilância', 'tr': 'farmakovijilans', 'fa': 'دارویقظی'},
    'de casus-controle studie': {'ru': 'исследование случай-контроль', 'uk': 'дослідження випадок-контроль', 'es': 'estudio de caso y control', 'pt': 'estudo caso-controle', 'tr': 'vaka kontrol çalışması', 'fa': 'مطالعه مورد شاهدی'},
    'de reproduceerbaarheid': {'ru': 'воспроизводимость', 'uk': 'відтворюваність', 'es': 'reproducibilidad', 'pt': 'reprodutibilidade', 'tr': 'tekrarlanabilirlik', 'fa': 'تکرارپذیری'},
    'de nulhypothese': {'ru': 'нулевая гипотеза', 'uk': 'нульова гіпотеза', 'es': 'hipótesis nula', 'pt': 'hipótese nula', 'tr': 'boş hipotez', 'fa': 'فرضیه صفر'},

    # RARE_SYNDROMES_DISORDERS - 10
    'de Ziekte van Crohn': {'ru': 'болезнь Крона', 'uk': 'хвороба Крона', 'es': 'enfermedad de Crohn', 'pt': 'doença de Crohn', 'tr': 'Crohn hastalığı', 'fa': 'بیماری کرون'},
    'de ziekte van Wilson': {'ru': 'болезнь Вильсона', 'uk': 'хвороба Вільсона', 'es': 'enfermedad de Wilson', 'pt': 'doença de Wilson', 'tr': 'Wilson hastalığı', 'fa': 'بیماری ویльсона'},
    'het syndroom van Cushing': {'ru': 'синдром Кушинга', 'uk': 'синдром Кушинга', 'es': 'síndrome de Cushing', 'pt': 'síndrome de Cushing', 'tr': 'Cushing sendromu', 'fa': 'سندرم کوشینگ'},
    'de multiple sclerose (MS)': {'ru': 'рассеянный склероз (РС)', 'uk': 'розсіяний склероз (РС)', 'es': 'esclerosis múltiple (EM)', 'pt': 'esclerose múltipla (EM)', 'tr': 'multipl skleroz (MS)', 'fa': 'مولتیپل اسکلروزیس (MS)'},
    'de sarcoïdose': {'ru': 'саркоидоз', 'uk': 'саркоїдоз', 'es': 'sarcoidosis', 'pt': 'sarcoidose', 'tr': 'sarkoidoz', 'fa': 'سارکوئیدوز'},
    'de vasculitis': {'ru': 'васкулит', 'uk': 'васкуліт', 'es': 'vasculitis', 'pt': 'vasculite', 'tr': 'vaskülit', 'fa': 'واسکولیت'},
    'de pulmonale hypertensie': {'ru': 'легочная гипертензия', 'uk': 'легенева гіпертензія', 'es': 'hipertensión pulmonar', 'pt': 'hipertensão pulmonar', 'tr': 'pulmoner hipertansiyon', 'fa': 'پرفشاری خون ریوی'},
    'de Ziekte van Parkinson': {'ru': 'болезнь Паркинсона', 'uk': 'хвороба Паркінсона', 'es': 'enfermedad de Parkinson', 'pt': 'doença de Parkinson', 'tr': 'Parkinson hastalığı', 'fa': 'بیماری پارکینسون'},
    'de fibromyalgie': {'ru': 'фибромиалгия', 'uk': 'фіброміалгія', 'es': 'fibromialgia', 'pt': 'fibromialgia', 'tr': 'fibromiyalji', 'fa': 'فیبرومیالژیا'},
    'het retinoblastoom': {'ru': 'ретинобластома', 'uk': 'ретинобластома', 'es': 'retinoblastoma', 'pt': 'retinoblastoma', 'tr': 'retinoblastom', 'fa': 'رتینوبلاستوما'},

    # ADDITIONAL_VALIDATION_TERMS - 19
    # Организационная структура и Первичная помощь
    'de eerstelijn': {
        'ru': 'Первичное звено (Медицинская помощь, первый контакт, включая Huisarts)', 
        'en': 'Primary Care (The first level of healthcare, including the GP/Huisarts, which acts as the system\'s gatekeeper)', 
        'uk': 'Первинна ланка (Меддопомога, перший контакт)', 
        'es': 'Atención primaria (Primer nivel de atención)', 
        'pt': 'Cuidados primários (Primeiro ponto de contacto)', 
        'tr': 'Birinci basamak (İlk tıbbi temas)', 
        'fa': 'مراقبت اولیه (اولین سطح مراقبت)'
    },
    'de tweedelijn': {
        'ru': 'Вторичное звено (Специализированная помощь в больницах, доступ только по направлению)', 
        'en': 'Secondary Care (Specialized care, typically provided in hospitals and usually requiring a referral from a GP)', 
        'uk': 'Вторинна ланка (Спеціалізована допомога у лікарнях)', 
        'es': 'Atención secundaria (Atención especializada en hospitales)', 
        'pt': 'Cuidados secundários (Apoio especializado em hospitais)', 
        'tr': 'İкинчи басамак (Uzman hastane bakımı)', 
        'fa': 'مراقبت ثانویه (مراقبت تخصصی در بیمارستان)'
    },
    'de POH-GGZ': {
        'ru': 'Помощник семейного врача по психическому здоровью (POH-GGZ) (Оказывает краткосрочную психологическую помощь в практике GP)', 
        'en': 'GP Assistant Mental Health (POH-GGZ) (Provides short-term psychological support directly within the GP practice, a key feature of Dutch primary care)', 
        'uk': 'Помічник сімейного лікаря (Психічне здоров\'я, короткострокова допомога)', 
        'es': 'Asistente de médico de cabecera (Salud Mental en consulta)', 
        'pt': 'Assistente do médico de família (Apoio psicológico breve)', 
        'tr': 'Aile hekimi asistanı (Kısa süreli psikolojik destek)', 
        'fa': 'دستیار پزشک عمومی (سلامت روان، کمک کوتاه‌مدت)'
    },
    'de wachtpost': {
        'ru': 'Дежурный пункт (Huisartsenpost) (Оказывает срочную помощь семейного врача в нерабочее время)', 
        'en': 'GP Out-of-Hours Post (Huisartsenpost) (The point of contact for urgent GP care outside regular office hours)', 
        'uk': 'Черговий пункт (Невідкладна допомога GP у неробочий час)', 
        'es': 'Puesto de guardia (Atención urgente fuera del horario)', 
        'pt': 'Posto de atendimento noturno (Urgência fora de horas)', 
        'tr': 'Nöbetçi istasyon (Mesai dışı acil hizmet)', 
        'fa': 'پست کشیک (مراقبت فوری در ساعات غیر اداری)'
    },
    'het verwijsbeleid': {
        'ru': 'Политика направлений (Протоколы, определяющие необходимость и порядок направления к специалисту)', 
        'en': 'Referral Policy (Protocols and guidelines that dictate when and how a patient is referred from primary to secondary care)', 
        'uk': 'Політика направлень (Протоколи для направлення до спеціаліста)', 
        'es': 'Política de derivación (Reglas para referir al paciente)', 
        'pt': 'Política de encaminhamento (Protocolos para especialistas)', 
        'tr': 'Sevk politikası (Uzmanlara sevk kuralları)', 
        'fa': 'سیاست ارجاع (پروتکل‌های ارجاع به متخصص)'
    },
    'het zorgpad': {
        'ru': 'Путь пациента (Zorgpad) (Стандартизированный, междисциплинарный протокол для лечения конкретного заболевания)', 
        'en': 'Care Pathway (Zorgpad) (A standardized, multi-disciplinary treatment protocol for a specific condition, aiming for efficiency and quality)', 
        'uk': 'Шлях пацієнта (Стандартизований протокол лікування)', 
        'es': 'Trayectoria de atención (Protocolo estandarizado)', 
        'pt': 'Rota de cuidado (Protocolo de tratamento padronizado)', 
        'tr': 'Bakım yolu (Standart tedavi protokolü)', 
        'fa': 'مسیر مراقبت (پروتکل درمانی استاندارد)'
    },
    'de zorgverzekeraar': {
        'ru': 'Страховщик (медицинское страхование) (Организация, оплачивающая большую часть медицинских расходов)', 
        'en': 'Health Insurer (The organization responsible for financing most healthcare costs in the mandatory Dutch system)', 
        'uk': 'Страховик (Організація, що оплачує медичні витрати)', 
        'es': 'Aseguradora de salud (Financiador de costes)', 
        'pt': 'Seguradora de saúde (Financiamento obrigatório)', 
        'tr': 'Sağlık sigortası şirketi (Giderleri ödeyen kurum)', 
        'fa': 'شرکت بیمه درمانی (سازمان تامین مالی)'
    },
    'de eigen risico': {
        'ru': 'Собственный риск (франшиза) (Обязательная годовая сумма, которую пациент оплачивает сам до покрытия страховкой)', 
        'en': 'Deductible / Own Risk (The mandatory annual amount a patient must pay out-of-pocket before insurance coverage starts for certain costs)', 
        'uk': 'Власний ризик (Обов\'язкова річна сума оплати пацієнтом)', 
        'es': 'Riesgo propio (Monto anual a pagar por el paciente)', 
        'pt': 'Risco próprio (Franquia anual obrigatória)', 
        'tr': 'Öz risk (Sigorta öncesi zorunlu yıllık miktar)', 
        'fa': 'ریسک شخصی (فرانشیز سالانه اجباری)'
    },
    'de caseload': {
        'ru': 'Общее количество пациентов (Рабочая нагрузка)', 
        'en': 'Caseload (The total number of patients/cases a healthcare provider or practice is responsible for)', 
        'uk': 'Загальна кількість пацієнтів (Робоче навантаження)', 
        'es': 'Carga de casos (Número total de pacientes)', 
        'pt': 'Carga de pacientes (Volume de trabalho)', 
        'tr': 'Hasta yükü (Toplam hasta sayısı)', 
        'fa': 'بار مراجعین (تعداد کل بیماران)'
    },
    'de multidisciplinaire overleg (MDO)': {
        'ru': 'Мультидисциплинарное совещание (МДО) (Совещание разных специалистов для обсуждения сложного случая)', 
        'en': 'Multidisciplinary Team Meeting (MDO) (A consultation between various healthcare professionals to discuss and plan complex patient care)', 
        'uk': 'Мультидисциплінарна нарада (Обговорення складного випадку)', 
        'es': 'Reunión multidisciplinaria (Consulta de diferentes especialistas)', 
        'pt': 'Reunião multidisciplinar (Consulta de especialistas)', 
        'tr': 'Multidisipliner toplantı (Karmaşık vakaların görüşülmesi)', 
        'fa': 'مشورت چندرشته‌ای (بحث در مورد پرونده‌های پیچیده)'
    },
    
    # Процедуры, Документация и Юридические рамки
    'het tuchtrecht': {
        'ru': 'Дисциплинарное право (Система рассмотрения жалоб на профессиональное ненадлежащее поведение врача)', 
        'en': 'Disciplinary Law (The legal system used to judge and potentially sanction healthcare professionals for professional misconduct)', 
        'uk': 'Дисциплінарне право (Розгляд скарг на професійну поведінку)', 
        'es': 'Derecho disciplinario (Juicio por mala conducta)', 
        'pt': 'Direito disciplinar (Julgamento de má conduta profissional)', 
        'tr': 'Disiplin hukuku (Mesleki suistimal yargılama sistemi)', 
        'fa': 'حقوق انضباطی (سیستم رسیدگی به تخلفات حرفه‌ای)'
    },
    'de Wvggz': {
        'ru': 'Закон о принудительной психиатрической помощи (Закон, регулирующий недобровольное лечение в психиатрии)', 
        'en': 'Compulsory Mental Health Care Act (Wvggz) (The law governing involuntary admissions and treatment in mental healthcare)', 
        'uk': 'Закон про примусову психіатричну допомогу (Закон про недобровільне лікування)', 
        'es': 'Ley de atención psiquiátrica involuntaria (Regulación de tratamiento no voluntario)', 
        'pt': 'Lei de assistência psiquiátrica involuntária (Lei sobre tratamento não consensual)', 
        'tr': 'Zorunlu ruh sağlığı yasası (İstemsiz tedaviyi düzenleyen yasa)', 
        'fa': 'قانون مراقبت‌های اجباری روانی (قانون درمان غیر داوطلبانه)'
    },
    'de meldcode huiselijk geweld': {
        'ru': 'Кодекс по сообщению о домашнем насилии (Обязательный протокол для медработников при подозрении на насилие)', 
        'en': 'Domestic Violence Reporting Code (A mandatory five-step protocol for healthcare workers when domestic violence or child abuse is suspected)', 
        'uk': 'Кодекс повідомлення про домашнє насильство (Обов\'язковий протокол)', 
        'es': 'Código de notificación de violencia doméstica (Protocolo obligatorio para profesionales)', 
        'pt': 'Código de denúncia de violência doméstica (Protocolo obrigatório)', 
        'tr': 'Aile içi şiddet bildirim kodu (Şüpheli durumlarda zorunlu protokol)', 
        'fa': 'کد گزارش خشونت خانگی (پروتکل اجباری برای متخصصین)'
    },
    'het journaal': {
        'ru': 'Журнал (Амбулаторная карта/Бортовой журнал GP) (Хронологическая запись контактов с пациентом в первичной помощи)', 
        'en': 'Medical Record / Logbook (The chronological record of all patient contacts, central to documentation in primary care)', 
        'uk': 'Журнал (Хронологічний запис контактів пацієнта)', 
        'es': 'Diario (Registro cronológico de contactos)', 
        'pt': 'Diário (Registo cronológico de contactos)', 
        'tr': 'Günlük (Hasta temaslarının kronolojik kaydı)', 
        'fa': 'مجله (سجل زمانی تماس با بیمار)'
    },
    'het beleid': {
        'ru': 'План действий / Тактика лечения (Четко сформулированный план лечения и наблюдения)', 
        'en': 'Management Plan / Policy (The clearly stated plan for patient treatment and follow-up after diagnosis)', 
        'uk': 'План дій / Тактика лікування (Чіткий план лікування)', 
        'es': 'Política / Plan de acción (Plan de tratamiento)', 
        'pt': 'Política / Plano de ação (Estratégia de tratamento)', 
        'tr': 'Politika / Eylem planı (Tedavi taktiği)', 
        'fa': 'سياسة/برنامه عملی (تاکتیک درمانی)'
    },
    'het SOAP-model': {
        'ru': 'Модель SOAP (S-Subjectief, O-Objectief, A-Analyse, P-Plan) (Стандарт структурированного ведения медицинских записей)', 
        'en': 'SOAP Model (S-Subjective, O-Objective, A-Assessment, P-Plan) (The standard structure for clinical note-taking in many medical settings)', 
        'uk': 'Модель SOAP (Стандарт ведення мед. записів)', 
        'es': 'Modelo SOAP (Estructura de registro clínico)', 
        'pt': 'Modelo SOAP (Estrutura de notas clínicas)', 
        'tr': 'SOAP modeli (Klinik kayıt yapısı)', 
        'fa': 'مدل SOAP (ساختار ثبت سوابق بالینی)'
    },
    'de overdracht': {
        'ru': 'Передача (информации о пациенте) (Процесс передачи ответственности и информации другому специалисту/отделению)', 
        'en': 'Handover / Transfer (The process of transferring patient responsibility and information to another professional or department, requiring high accuracy)', 
        'uk': 'Передача (Передача інформації про пацієнта)', 
        'es': 'Transferencia (Paso de información y responsabilidad)', 
        'pt': 'Transferência (Passagem de informação e responsabilidade)', 
        'tr': 'Devir (Hasta bilgisi ve sorumluluk aktarımı)', 
        'fa': 'انتقال (انتقال مسئولیت و اطلاعات بیمار)'
    },
    'de anamnese': {
        'ru': 'Анамнез (Сбор истории болезни пациента)', 
        'en': 'Anamnesis / History Taking (The process of gathering the patient\'s medical history and current symptoms)', 
        'uk': 'Анамнез (Збір історії хвороби)', 
        'es': 'Anamnesis (Recopilación de historial médico)', 
        'pt': 'Anamnese (Coleta da história da doença)', 
        'tr': 'Anamnez (Hastalık öyküsü toplama)', 
        'fa': 'شرح حال (جمع‌آوری تاریخچه پزشکی)'
    },
    'het patiëntendossier': {
        'ru': 'Медицинская карта пациента (Полное собрание всех медицинских документов пациента)', 
        'en': 'Patient File / Dossier (The complete collection of all medical records and documentation for a patient)', 
        'uk': 'Медична карта пацієнта (Повний збір документів)', 
        'es': 'Expediente del paciente (Colección completa de registros)', 
        'pt': 'Prontuário do paciente (Coleção completa de registos)', 
        'tr': 'Hasta dosyası (Tüm tıbbi kayıtlar)', 
        'fa': 'پرونده بیمار (مجموعه کامل مدارک پزشکی)'
    }
}

def add_translations():
    with app.app_context():
        print("🌍 Adding translations for 269 medical terms...")
        print("=" * 70)
        
        added_count = 0
        not_found_count = 0
        
        for dutch_term, translations in TRANSLATIONS.items():
            term = MedicalTerm.query.filter_by(term_nl=dutch_term).first()
            
            if term:
                for lang, translation in translations.items():
                    if not getattr(term, f'term_{lang}', None):
                        setattr(term, f'term_{lang}', translation)
                        added_count += 1
                        print(f"✓ {dutch_term} → {lang.upper()}: {translation}")
            else:
                print(f"✗ Not found: {dutch_term}")
                not_found_count += 1
        
        try:
            db.session.commit()
            print("\n" + "="*70)
            print(f"✅ COMPLETE!")
            print(f"   Added: {added_count} translations")
            print(f"   Not found: {not_found_count} terms")
            
            # Verify
            total_terms = MedicalTerm.query.count()
            terms_with_all_langs = 0
            for term in MedicalTerm.query.all():
                langs = ['en', 'uk', 'ru', 'es', 'pt', 'tr', 'fa', 'ar']
                if all(getattr(term, f'term_{lang}', None) for lang in langs):
                    terms_with_all_langs += 1
            
            print(f"   Total terms: {total_terms}")
            print(f"   Terms with ALL 8 languages: {terms_with_all_langs}")
            print("="*70 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}\n")

if __name__ == '__main__':
    add_translations()
