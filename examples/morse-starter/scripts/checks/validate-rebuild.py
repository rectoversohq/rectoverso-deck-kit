"""Hold a second build of a package to the first: the same notes, with the same identities.

    python scripts/checks/validate-rebuild.py first/Morse-starter-en.apkg second/Morse-starter-en.apkg

A learner's progress follows a note's GUID and its note type's id. A build that changed either
would make new cards beside the old ones, so two builds of one source must agree.
"""
import sys
import tempfile
from pathlib import Path

from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest


def identities(package):
    with tempfile.TemporaryDirectory() as temporary:
        collection = Collection(str(Path(temporary) / 'collection.anki2'))
        try:
            collection.import_anki_package(ImportAnkiPackageRequest(package_path=str(package)))
            # Each note's GUID, its note type's id and its fields, and the decks by name. (Read
            # through an import, a deck's id is the importing collection's own, so it isn't
            # compared here: the builder gives the package's deck the id the source declares.)
            notes = collection.db.all('select guid, mid, flds from notes order by guid')
            decks = sorted(collection.decks.name(row[0]) for row in collection.db.all('select distinct did from cards'))
            return notes, decks
        finally:
            collection.close()


if __name__ == '__main__':
    first, second = (Path(argument).resolve() for argument in sys.argv[1:3])
    if identities(first) != identities(second):
        raise SystemExit(f'{second.name}: a rebuild changed a note, a note type or the name of a deck')
    print(f'{second.name}: the rebuild has the same notes and identities')
