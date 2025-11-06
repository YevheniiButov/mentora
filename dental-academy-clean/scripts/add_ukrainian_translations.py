"""
Add Ukrainian translations to medical terms
"""
from app import app
from models import MedicalTerm, db

# Ukrainian translations for dental and medical terms
UKRAINIAN_TRANSLATIONS = {
    # Anatomy
    'de pijn': 'біль',
    'het hart': 'серце',
    'de long': 'легеня',
    'de maag': 'шлунок',
    'de lever': 'печінка',
    'de nier': 'нирка',
    'het brein': 'мозок',
    'de keel': 'горло',
    'het bloedvat': 'кровоносна судина',
    'de spier': 'м\'язиця',
    'het bot': 'кістка',
    
    # Symptoms
    'de koorts': 'гарячка',
    'de hoest': 'кашель',
    'de diarree': 'діарея',
    'de misselijkheid': 'нудота',
    'de hoofdpijn': 'головна біль',
    'de zwelling': 'набряк',
    'de roodheid': 'почервоніння',
    'de vermoeidheid': 'втома',
    'de jeuk': 'свербіж',
    'de verstopte neus': 'закладеність носа',
    
    # Diseases
    'de griep': 'грип',
    'de diabetes': 'діабет',
    'het asthma': 'астма',
    'de hartaanval': 'інфаркт',
    'de kanker': 'рак',
    'de tuberculose': 'туберкульоз',
    'de AIDS': 'СНІД',
    'de depressie': 'депресія',
    'de angststoornis': 'тривожний розлад',
    'de schizofrenie': 'шизофренія',
    
    # Treatments
    'het medicijn': 'ліки',
    'de pil': 'таблетка',
    'de injectie': 'ін\'єкція',
    'de operatie': 'операція',
    'de therapie': 'терапія',
    'de massage': 'масаж',
    'de fysiotherapie': 'фізіотерапія',
    'de bestraling': 'опромінення',
    'de chemotherapie': 'хіміотерапія',
    'de bloedtransfusie': 'переливання крові',
    
    # Dental
    'de tand': 'зуб',
    'de kies': 'корінний зуб',
    'de snijtand': 'різець',
    'het tandvlees': 'ясна',
    'de tandpijn': 'зубна біль',
    'de cariës': 'карієс',
    'de plak': 'зубний камінь',
    'de wortelkanaal': 'кореневий канал',
    'de kroon': 'зубна корона',
    'de brace': 'брекети',
}

def add_ukrainian_translations():
    with app.app_context():
        print("\n" + "="*70)
        print("Adding Ukrainian Translations to Medical Terms")
        print("="*70)
        
        added = 0
        not_found = 0
        
        for dutch_term, ukrainian_term in UKRAINIAN_TRANSLATIONS.items():
            term = MedicalTerm.query.filter_by(term_nl=dutch_term).first()
            
            if term:
                if not term.term_uk:
                    term.term_uk = ukrainian_term
                    added += 1
                    print(f"✓ {dutch_term} → {ukrainian_term}")
                else:
                    print(f"⏭️ {dutch_term} already has translation")
            else:
                not_found += 1
                print(f"✗ Not found: {dutch_term}")
        
        try:
            db.session.commit()
            print("\n" + "="*70)
            print(f"✅ COMPLETE!")
            print(f"   Added: {added} Ukrainian translations")
            print(f"   Not found: {not_found} terms")
            print(f"   Total terms in DB: {MedicalTerm.query.count()}")
            print("="*70 + "\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}\n")

if __name__ == '__main__':
    add_ukrainian_translations()
