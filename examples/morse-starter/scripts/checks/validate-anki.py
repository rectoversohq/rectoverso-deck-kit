"""Open a built package with Anki and hold it to what the deck says of it.

    python scripts/checks/validate-anki.py /path/to/Morse-starter-en.apkg

Anki imports the package into an empty collection; every note the source declares must be there,
with its GUID, and every card must show something on its front and on its back.
"""
import json
import sys
import tempfile
from pathlib import Path

from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_data import inputs  # noqa: E402


def validate(package):
    meta = json.loads(package.with_suffix('.rectoverso.json').read_text())
    _, notes, _, _ = inputs(meta['language'])
    with tempfile.TemporaryDirectory() as temporary:
        collection = Collection(str(Path(temporary) / 'collection.anki2'))
        try:
            collection.import_anki_package(ImportAnkiPackageRequest(package_path=str(package)))
            guids = set(collection.db.list('select guid from notes'))
            if guids != {note['guid'] for note in notes}:
                raise SystemExit(f'{package.name}: its notes differ from the source\'s')
            if collection.card_count() != meta['cards']:
                raise SystemExit(f'{package.name}: {collection.card_count()} cards, {meta["cards"]} declared')
            for card_id in collection.find_cards(''):
                card = collection.get_card(card_id)
                if not card.question().strip() or not card.answer().strip():
                    raise SystemExit(f'{package.name}: an empty side on card {card_id}')
        finally:
            collection.close()
    print(f'{package.name}: opens in Anki with its {meta["cards"]} cards')


if __name__ == '__main__':
    validate(Path(sys.argv[1]).resolve())
