"""What each language's package is: the deck kit's check, and this deck's own builder, both ask here.

`inputs(language)` returns four things, all plain JSON:

1. the language's expanded metadata: rectoverso.json without `languages`, plus the language's own
   id, package and sample, the deck's id as `deckID`, and the language's code;
2. its notes, in the order the deck is studied, each with its GUID, its note type and its fields;
3. its note types, by the name the notes use;
4. its Anki deck.

Standard library only: the check runs this file with nothing installed.
"""
import html
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Any fixed UUID of the deck's own: its card and deck ids are made from it, the same at every build.
NAMESPACE = uuid.UUID('5b0c8f0e-7d1a-4c56-9e2b-3a4f5d6c7b8a')
FIELDS = ['Front', 'Back', 'Kicker', 'Meta', 'Example', 'Note', 'RectoVerso']


def read(path):
    return json.loads((ROOT / path).read_text())


def inputs(language):
    meta = read('rectoverso.json')
    cards = read('source/cards.json')
    words = read(f'source/languages/{language}.json')
    artifact = meta['languages'][language]
    offset = sorted(meta['languages']).index(language)
    # The deck's id in RectoVerso's library: one per language, the same at every build.
    book = str(uuid.uuid5(NAMESPACE, f'{meta["guidPrefix"]}/{language}'))

    # The order the deck is studied in: each letter, and each word after the card its source names.
    order = [dict(letter, kind='letter') for letter in cards['letters']]
    for word in words['words']:
        place = next(index for index, item in enumerate(order) if item['id'] == word['after'])
        order.insert(place + 1, dict(word, kind='word'))

    notes = []
    for item in order:
        guid = f'{meta["guidPrefix"]}-{language}-{item["id"]}'
        payload = {'v': 1, 'book': book, 'card': str(uuid.uuid5(NAMESPACE, guid)), 'kind': 'basic', 'noteID': guid}
        if item['kind'] == 'letter':
            front, back, kicker = item['morse'], item['letter'], words['readLetter']
            # A letter's card teaches the letter.
            payload['introduces'] = [item['letter'].lower()]
        else:
            front = '   '.join(cards['morse'][letter] for letter in item['word'])
            back, kicker = item['word'], words['readWord']
            # A word's card builds on each of its letters, each named once.
            payload['requires'] = sorted({letter.lower() for letter in item['word']})
        fields = dict(zip(FIELDS, [front, back, kicker, '', '', '', html.escape(json.dumps(payload, ensure_ascii=False))]))
        notes.append({'guid': guid, 'model': 'morse', 'fields': fields})

    types = {'morse': {
        'id': meta['identityBase'] + 1000 + offset,
        'name': f'Morse starter ({language})',
        'fields': FIELDS,
        'templates': [{'name': 'Card 1', 'qfmt': '<div class="kicker">{{Kicker}}</div>{{Front}}',
                       'afmt': '{{FrontSide}}<hr id="answer">{{Back}}'}],
    }}
    deck = {'id': meta['identityBase'] + offset, 'name': artifact['title']}

    expanded = {key: value for key, value in meta.items() if key != 'languages'}
    expanded.update(id=artifact['id'], deckID=meta['id'], language=language, package=artifact['package'],
                    sample=artifact['sample'])
    return expanded, notes, types, deck
