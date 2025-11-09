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
            f\"Data file {DATA_PATH} not found. "
            \"Run the PDF extraction beforehand.\"
        )

    entries = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    created = 0
    updated = 0

    with app.app_context():
        for item in entries:
            cat_number, cat_name = parse_category(item['category'])
            category_key = f\"dentistry_{cat_number}_{slugify(cat_name)}\"

            term_nl = item['nl'].strip()
            term_en = item['en'].strip()

            term = MedicalTerm.query.filter_by(term_nl=term_nl).first()

            if term:
                updated += 1
                term.term_en = term_en
                term.category = category_key
                if term.definition_nl is None:
                    term.definition_nl = term_en
                if term.difficulty is None:
                    term.difficulty = 1
                if term.frequency is None:
                    term.frequency = 1
            else:
                created += 1
                term = MedicalTerm(
                    term_nl=term_nl,
                    term_en=term_en,
                    definition_nl=term_en,
                    category=category_key,
                    difficulty=1,
                    frequency=1,
                )
                db.session.add(term)

        db.session.commit()

    print(f\"Imported dental terms: created={created}, updated={updated}\")


if __name__ == '__main__':
    main()

