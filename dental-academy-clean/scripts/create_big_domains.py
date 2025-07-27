from models import BIGDomain
from extensions import db

# Список доменов (включая ALGEMENE_GENEESKUNDE из JSON)
domains_data = [
    {'name': 'Therapeutische stomatologie', 'code': 'THER', 'description': 'Behandeling van cariës, endodontie, restauraties'},
    {'name': 'Chirurgische stomatologie', 'code': 'SURG', 'description': 'Extracties, implantologie, chirurgische procedures'}, 
    {'name': 'Prothetische stomatologie', 'code': 'PROTH', 'description': 'Prothetiek, kronen, bruggen, prothesen'},
    {'name': 'Pediatrische stomatologie', 'code': 'PEDI', 'description': 'Tandheelkunde voor kinderen'},
    {'name': 'Parodontologie', 'code': 'PARO', 'description': 'Tandvlees en ondersteunende structuren'},
    {'name': 'Orthodontie', 'code': 'ORTHO', 'description': 'Bijtcorrectie en tandstand'}, 
    {'name': 'Preventie', 'code': 'PREV', 'description': 'Preventieve tandheelkunde'},
    {'name': 'Ethiek en recht', 'code': 'ETHIEK', 'description': 'Medische ethiek en Nederlandse wetgeving'},
    {'name': 'Anatomie', 'code': 'ANATOMIE', 'description': 'Anatomie van hoofd en hals'},
    {'name': 'Fysiologie', 'code': 'FYSIOLOGIE', 'description': 'Fysiologie van orale structuren'},
    {'name': 'Pathologie', 'code': 'PATHOLOGIE', 'description': 'Orale pathologie en ziekteprocessen'},
    {'name': 'Microbiologie', 'code': 'MICROBIOLOGIE', 'description': 'Orale microbiologie en infecties'},
    {'name': 'Materiaalkunde', 'code': 'MATERIAALKUNDE', 'description': 'Dentale materialen en eigenschappen'},
    {'name': 'Radiologie', 'code': 'RADIOLOGIE', 'description': 'Diagnostische beeldvorming'},
    {'name': 'Algemene geneeskunde', 'code': 'ALGEMENE', 'description': 'Systemische aandoeningen en medicatie'},
    {'name': 'Algemene geneeskunde', 'code': 'ALGEMENE_GENEESKUNDE', 'description': 'Systemische aandoeningen en medicatie'}  # Для совместимости с JSON
]

def create_big_domains():
    created_count = 0
    for domain_data in domains_data:
        existing = BIGDomain.query.filter_by(code=domain_data['code']).first()
        if not existing:
            domain = BIGDomain(
                name=domain_data['name'],
                code=domain_data['code'],
                description=domain_data['description']
            )
            db.session.add(domain)
            created_count += 1
            print(f"✅ Создан домен: {domain_data['code']} - {domain_data['name']}")
        else:
            print(f"⚠️ Домен уже существует: {domain_data['code']}")
    db.session.commit()
    print(f"\n🎯 Создано новых доменов: {created_count}")
    print(f"📊 Всего доменов в БД: {BIGDomain.query.count()}")
    print(f"\n📋 ВСЕ ДОМЕНЫ В БД:")
    for domain in BIGDomain.query.all():
        print(f"   {domain.code}: {domain.name}")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        create_big_domains() 