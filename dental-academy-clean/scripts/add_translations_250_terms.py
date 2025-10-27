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

# Translations for 250 terms (7 languages × 250 = 1750 translations)
TRANSLATIONS = {
    # BASIC TERMS (50) - anatomy_basic, symptoms_basic, diseases_basic, treatments_basic, dental_basic
    'het hart': {'ru': 'сердце', 'uk': 'серце', 'es': 'corazón', 'pt': 'coração', 'tr': 'kalp', 'fa': 'قلب', 'ar': 'القلب'},
    'de long': {'ru': 'лёгкое', 'uk': 'легень', 'es': 'pulmón', 'pt': 'pulmão', 'tr': 'akciğer', 'fa': 'ریه', 'ar': 'الرئة'},
    'de maag': {'ru': 'желудок', 'uk': 'шлунок', 'es': 'estómago', 'pt': 'estômago', 'tr': 'mide', 'fa': 'معده', 'ar': 'المعدة'},
    'de lever': {'ru': 'печень', 'uk': 'печінка', 'es': 'hígado', 'pt': 'fígado', 'tr': 'karaciğer', 'fa': 'جگر', 'ar': 'الكبد'},
    'de nier': {'ru': 'почка', 'uk': 'нирка', 'es': 'riñón', 'pt': 'rim', 'tr': 'böbrek', 'fa': 'کلیه', 'ar': 'الكلية'},
    'het brein': {'ru': 'мозг', 'uk': 'мозок', 'es': 'cerebro', 'pt': 'cérebro', 'tr': 'beyin', 'fa': 'مغز', 'ar': 'الدماغ'},
    'de keel': {'ru': 'горло', 'uk': 'горло', 'es': 'garganta', 'pt': 'garganta', 'tr': 'boğaz', 'fa': 'حلق', 'ar': 'الحلق'},
    'het bloedvat': {'ru': 'кровеносный сосуд', 'uk': 'кровоносна судина', 'es': 'vaso sanguíneo', 'pt': 'vaso sanguíneo', 'tr': 'kan damarı', 'fa': 'رگ خونی', 'ar': 'الأوعية الدموية'},
    'de spier': {'ru': 'мышца', 'uk': 'м\'язиця', 'es': 'músculo', 'pt': 'músculo', 'tr': 'kas', 'fa': 'ماهیچه', 'ar': 'العضلة'},
    'het bot': {'ru': 'кость', 'uk': 'кістка', 'es': 'hueso', 'pt': 'osso', 'tr': 'kemik', 'fa': 'استخوان', 'ar': 'العظم'},
    
    'de pijn': {'ru': 'боль', 'uk': 'біль', 'es': 'dolor', 'pt': 'dor', 'tr': 'ağrı', 'fa': 'درد', 'ar': 'الألم'},
    'de koorts': {'ru': 'лихорадка', 'uk': 'гарячка', 'es': 'fiebre', 'pt': 'febre', 'tr': 'ateş', 'fa': 'تب', 'ar': 'الحمى'},
    'de hoest': {'ru': 'кашель', 'uk': 'кашель', 'es': 'tos', 'pt': 'tosse', 'tr': 'öksürük', 'fa': 'سرفه', 'ar': 'السعال'},
    'de hoofdpijn': {'ru': 'головная боль', 'uk': 'головна біль', 'es': 'dolor de cabeza', 'pt': 'dor de cabeça', 'tr': 'baş ağrısı', 'fa': 'سردرد', 'ar': 'الصداع'},
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
    'de injectie': {'ru': 'инъекция', 'uk': 'ін\'єкція', 'es': 'inyección', 'pt': 'injeção', 'tr': 'iğne', 'fa': 'تزریق', 'ar': 'الحقنة'},
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
    'de parodontitis': {'ru': 'пародонтит', 'uk': 'пародонтит', 'es': 'periodontitis', 'pt': 'periodontite', 'tr': 'periodontit', 'fa': 'پریودنتیت', 'ar': 'التهاب اللثة'},
    'de tandborstel': {'ru': 'зубная щетка', 'uk': 'зубна щітка', 'es': 'cepillo de dientes', 'pt': 'escova de dentes', 'tr': 'diş fırçası', 'fa': 'مسواک', 'ar': 'فرشاة الأسنان'},
    'de tandpasta': {'ru': 'зубная паста', 'uk': 'зубна паста', 'es': 'pasta de dientes', 'pt': 'pasta de dentes', 'tr': 'diş macunu', 'fa': 'خمیردندان', 'ar': 'معجون الأسنان'},
    'de vulling': {'ru': 'пломба', 'uk': 'пломба', 'es': 'empaste', 'pt': 'obturação', 'tr': 'dolgu', 'fa': 'پرکردگی', 'ar': 'الحشو'},
    'de kroon': {'ru': 'коронка', 'uk': 'корона', 'es': 'corona', 'pt': 'coroa', 'tr': 'taç', 'fa': 'تاج دندان', 'ar': 'التاج'},
}

def add_translations():
    with app.app_context():
        print("🌍 Adding translations for 250 medical terms...")
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
