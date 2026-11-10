"""Build one language's package with Anki's own Python library.

    pip install anki
    python scripts/build.py --language en --out /somewhere/outside/the/repository/Morse-starter-en.apkg

Writes the package and, beside it, its sidecar (`<package>.rectoverso.json`): the language's
metadata with the package's size and SHA-256. Packages never go into Git: they are attached to
the deck's release.
"""
import argparse
import hashlib
import json
import tempfile
from datetime import datetime
from pathlib import Path

from anki.collection import Collection, ExportAnkiPackageOptions
from anki.decks import DeckId

from source_data import ROOT, inputs


def build(language, out):
    out = out.resolve()
    if out.is_relative_to(ROOT) or out.exists():
        raise SystemExit('Choose a new package path outside the repository.')
    meta, notes, types, deck = inputs(language)
    if out.name != meta['package']['file']:
        raise SystemExit(f'The package is named {meta["package"]["file"]} in rectoverso.json.')
    # Anki updates a note only when it is newer: every note carries the content's own time.
    modified = int(datetime.fromisoformat(meta['contentModifiedAt'].replace('Z', '+00:00')).timestamp())
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        collection = Collection(str(Path(temporary) / 'collection.anki2'))
        try:
            made = {}
            for key, kind in types.items():
                note_type = collection.models.new(kind['name'])
                for name in kind['fields']:
                    collection.models.add_field(note_type, collection.models.new_field(name))
                for template in kind['templates']:
                    card = collection.models.new_template(template['name'])
                    card.update(qfmt=template['qfmt'], afmt=template['afmt'])
                    collection.models.add_template(note_type, card)
                # The deck's own ids, the same at every build: an update finds the same note type.
                note_type.update(id=kind['id'], mod=modified)
                collection.models.update(note_type)
                made[key] = note_type
            anki_deck = collection.decks.new_deck_legacy(False)
            anki_deck.update(id=deck['id'], name=deck['name'])
            collection.decks.update(anki_deck)
            for position, source in enumerate(notes, start=1):
                note = collection.new_note(made[source['model']])
                note.guid = source['guid']
                for name, value in source['fields'].items():
                    note[name] = value
                collection.add_note(note, DeckId(deck['id']))
                # New cards come in the order the deck was written.
                collection.db.execute('update cards set due = ? where nid = ?', position, note.id)
            collection.db.execute('update notes set mod = ?', modified)
            collection.export_anki_package(
                out_path=str(out), options=ExportAnkiPackageOptions(with_scheduling=False, with_media=True), limit=None)
        finally:
            collection.close()
    meta['package'].update(bytes=out.stat().st_size, sha256=hashlib.sha256(out.read_bytes()).hexdigest())
    out.with_suffix('.rectoverso.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f'{out.name}: {len(notes)} notes')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--language', required=True)
    parser.add_argument('--out', type=Path, required=True)
    arguments = parser.parse_args()
    build(arguments.language, arguments.out)
