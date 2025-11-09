#!/usr/bin/env python3
"""
Import Dutch → English dental vocabulary into MedicalTerm entries
using data extracted from `static/dentaal_words_clean.json`.

Run with:
    python scripts/import_dental_terms.py
"""
import json
import re
from pathlib import Path

from app import app, db
from models import MedicalTerm


DATA_PATH = Path('static/dentaal_words_clean.json')


def slugify(value: str) -> str:
    """Basic slugifier for category names."""
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-')


def parse_category(raw: str) -> tuple[str, str]:
    """
    Return (category_id, category_name) given raw heading like
    '1. DE PERIODIEKE CONTROLE'.
    """
    match = re.match(r'^(\\d+)\\.\\s*(.+)$', raw)
    if not match:
        return 'general', raw.strip()
    number, name = match.groups()
    return number, name.strip()


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file {DATA_PATH} not found. "
            "Run the PDF extraction beforehand."
        )

    entries = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    created = 0
    updated = 0

    with app.app_context():
        for item in entries:
            cat_number, cat_name = parse_category(item['category'])
            raw_number, raw_name = parse_category(item['category'])
            cat_number = raw_number or 'general'
            cat_name = raw_name or 'General'
            slug = slugify(cat_name)
            if len(slug) > 35:
                slug = slug[:35]
            category_key = f"dentistry_{cat_number}_{slug}"
            if len(category_key) > 50:
                category_key = category_key[:50]

            term_nl = item['nl'].strip()
            term_en = item['en'].strip()
            term_ru = item.get('ru')
            term_uk = item.get('uk')
            term_es = item.get('es')
            term_pt = item.get('pt')
            term_tr = item.get('tr')
            term_fa = item.get('fa')
            term_ar = item.get('ar')

            term = MedicalTerm.query.filter_by(term_nl=term_nl).first()

            if term:
                updated += 1
                term.term_en = term_en
                term.category = category_key
                term.definition_nl = term.definition_nl or term_en
                term.difficulty = term.difficulty or 1
                term.frequency = term.frequency or 1
                term.term_ru = term_ru or term_en
                term.term_uk = term_uk or term_en
                term.term_es = term_es or term_en
                term.term_pt = term_pt or term_en
                term.term_tr = term_tr or term_en
                term.term_fa = term_fa or term_en
                term.term_ar = term_ar or term_en
            else:
                created += 1
                term = MedicalTerm(
                    term_nl=term_nl,
                    term_en=term_en,
                    term_ru=term_ru or term_en,
                    term_uk=term_uk or term_en,
                    term_es=term_es or term_en,
                    term_pt=term_pt or term_en,
                    term_tr=term_tr or term_en,
                    term_fa=term_fa or term_en,
                    term_ar=term_ar or term_en,
                    definition_nl=term_en,
                    category=category_key,
                    difficulty=1,
                    frequency=1,
                )
                db.session.add(term)

        db.session.commit()

    print(f"Imported dental terms: created={created}, updated={updated}")


if __name__ == '__main__':
    main()

