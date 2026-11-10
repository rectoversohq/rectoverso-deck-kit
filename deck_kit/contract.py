"""The deck contract's rules: what a deck's rectoverso.json and its notes must hold.

`check` reads a deck's repository and returns what each language's package is, or raises `Refusal`
with the first rule the deck breaks. Every rule is explained in docs/contract.md, and every refusal
in docs/check.md. Nothing here builds a package, opens Anki or reaches the network: the deck's own
`scripts/source_data.py` says what its notes are, and this file holds them to the contract.
"""
from dataclasses import dataclass
from datetime import datetime
import html
import json
from pathlib import Path
import re
import subprocess
import sys

from . import schema

KIT = Path(__file__).resolve().parents[1]

# A deck, and each of its sources, is open: never non-commercial (NC) or no-derivatives (ND).
OPEN_LICENSES = {'CC0-1.0', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'MIT', 'Apache-2.0', 'Public domain'}
# What a deck's rectoverso.json must hold.
REQUIRED = ('id', 'version', 'releaseTag', 'guidPrefix', 'identityBase', 'contentModifiedAt', 'publication',
            'title', 'subject', 'headline', 'description', 'categories', 'cards', 'pictures', 'creator', 'license', 'sources',
            'imageCredits', 'proOnly', 'sourceFiles', 'languages')
# The fields written in every language the deck ships.
LOCALIZED = ('title', 'subject', 'headline', 'description')
# The gallery's categories, as docs/contract.md lists them (a test holds the two together).
CATEGORIES = {
    'geography': {'en': 'Geography', 'fr': 'Géographie'},
    'history': {'en': 'History', 'fr': 'Histoire'},
    'languages': {'en': 'Languages', 'fr': 'Langues'},
    'sciences': {'en': 'Sciences', 'fr': 'Sciences'},
    'mathematics': {'en': 'Mathematics', 'fr': 'Mathématiques'},
    'medicine': {'en': 'Medicine', 'fr': 'Médecine'},
    'arts': {'en': 'Arts', 'fr': 'Arts'},
    'music': {'en': 'Music', 'fr': 'Musique'},
}
# The longest word a deck may put on its sound button: the app's own limit.
PLAY_LABEL_LIMIT = 20
# A deck's study options: the values of the app's Deck options, by the names the app reads.
STUDY = {'newCards': ('random', 'deckOrder'), 'newPosition': ('afterReviews', 'beforeReviews', 'mixed')}
NEW_PER_DAY = range(1, 1000)
# A prerequisite token: lowercase words and digits, hyphens between them.
TOKEN = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
# The pictures and sounds a note's field names.
MEDIA = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*["\']([^"\']+)["\']|\[sound:([^\]]+)\]', re.IGNORECASE)
# The note field that holds a card's payload.
PAYLOAD_FIELD = 'RectoVerso'


class Refusal(ValueError):
    """The deck breaks the contract: the message names the deck, the rule and, where it helps, the fix."""


@dataclass(frozen=True)
class Gallery:
    """Whose gallery a deck is checked for. The contract is the same for every deck; a gallery adds
    where its decks live and whether it takes one that isn't approved yet."""
    # Every deck's repository is under this URL ("https://github.com/rectoversohq/"); None: anywhere.
    organization: str = None
    # Only an edition its owner approved (publication.approved) passes.
    approved_only: bool = False
    # A Pro-only deck's repository starts with this ("rectoverso-pro-"), and no other deck's does; None: no rule.
    pro_prefix: str = None


# RectoVerso's own gallery: its decks are in its organization, approved, and its Pro decks named apart.
RECTOVERSO = Gallery('https://github.com/rectoversohq/', True, 'rectoverso-pro-')
# Any author's deck, before it is offered to a gallery.
ANYWHERE = Gallery()


def run(*args, cwd, **kwargs):
    return subprocess.run(args, cwd=cwd, check=True, text=True, **kwargs)


def load_schema(name):
    """One of the kit's schemas (schemas/<name>.schema.json)."""
    return json.loads((KIT / 'schemas' / (name + '.schema.json')).read_text())


def source_path(source, path):
    """A path the deck names, inside its own repository, that exists."""
    resolved = (source / path).resolve()
    if Path(path).is_absolute() or not resolved.is_relative_to(source.resolve()) or not resolved.exists():
        raise Refusal(f'{source.name}: missing or external source path {path}')
    return resolved


def source_tool(source, name):
    """A deck's tools are where every deck's are: data and builder in scripts/, validators in scripts/checks/."""
    directory = 'scripts/checks' if name in ('validate-anki.py', 'validate-rebuild.py') else 'scripts'
    return source_path(source, directory + '/' + name)


def source_inputs(source, language, python=sys.executable):
    """What the deck says a language's package is: its expanded metadata, notes, note types and deck.

    The deck's own `scripts/source_data.py` builds them (`inputs(language)`), in a process of its
    own: the check never copies a deck's logic, and a deck's code never runs inside the check."""
    source = Path(source)
    program = ('import json,sys; sys.path.insert(0,sys.argv[1]); '
               'from source_data import inputs; print(json.dumps(inputs(sys.argv[2])))')
    try:
        return json.loads(run(python, '-B', '-c', program, str(source_tool(source, 'source_data.py').parent),
                              language, cwd=source, capture_output=True).stdout)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or '').strip().splitlines()
        raise Refusal(f'{source.name}/{language}: scripts/source_data.py failed'
                      + (': ' + detail[-1] if detail else '')) from error


def sidecar_name(metadata):
    """The file that travels beside a package on its release: <package>.rectoverso.json."""
    return Path(metadata['package']['file']).with_suffix('.rectoverso.json').name


def text(value):
    return isinstance(value, str) and bool(value.strip())


def open_license(name):
    """No non-commercial (NC) or no-derivatives (ND) terms, whatever the spelling."""
    return text(name) and not re.search(r'(?:^|[^A-Z])N[CD](?:[^A-Z]|$)', name.upper())


def pro(name, gallery=RECTOVERSO):
    """Whether a repository's name is a Pro deck's, in a gallery that names them apart."""
    return bool(gallery.pro_prefix) and name.startswith(gallery.pro_prefix)


def deck_license(name, metadata):
    """A public deck's license is open; a Pro-only deck's may be its own terms, a LicenseRef- identifier."""
    value = metadata['license']
    if value in OPEN_LICENSES or (metadata['proOnly'] is True and re.fullmatch(r'LicenseRef-[A-Za-z0-9.-]+', str(value))):
        return
    raise Refusal(f'{name}: the deck needs an open license' + (' or its own LicenseRef- terms' if metadata['proOnly'] is True else ''))


def guid_prefix(metadata, language):
    """What every note GUID of this language starts with: the prefix, then the language (`rv-flags-fr-`)."""
    return f'{metadata["guidPrefix"]}-{language}-'


def picture_source(source, metadata, credit):
    """A credited picture is a file of the deck's pictures folder or, for a deck whose build renders its
    pictures (`renderedPictures`), the original the build renders it from, in the repository."""
    if metadata.get('renderedPictures'):
        original = credit.get('original')
        return text(original) and source_path(source, original).is_file()
    return (source_path(source, metadata['sourceFiles']['pictures']) / credit['file']).is_file()


def cover_files(metadata, language):
    """A language's cover files: its light ones, then its dark ones, each in the order a gallery shows them."""
    covers = (metadata.get('covers') or {}).get(language) or {}
    return [*covers.get('light', []), *covers.get('dark', [])]


def cover_name(prefix, file):
    """A cover's name: `<guidPrefix>[-<language>]-cover[-<light|dark>]-<n>.<png|jpg>`.

    A language only for a cover with words, its language's alone; without one, every language may
    show it. An appearance only for a cover made for light or dark mode; without one, it serves both.
    Returns (language or None, appearance or None, place), or None when the name isn't a cover's.
    The deck's prefix keeps every deck's covers apart where a gallery holds them together."""
    match = re.fullmatch(re.escape(prefix) + r'(?:-([a-z]{2}(?:-[a-z0-9]+)*))?-cover(?:-(light|dark))?-([1-9][0-9]*)\.(?:png|jpg)',
                         file)
    return (match[1], match[2], int(match[3])) if match else None


def verify_study(name, study):
    """A deck's study options, when given: one or more of newCards, newPerDay and newPosition, each a
    value the app's Deck options offer, and nothing else (the app would leave a misspelled key aside)."""
    if study is None:
        return
    if (not isinstance(study, dict) or not study or not set(study) <= {*STUDY, 'newPerDay'}
            or not all(study[key] in values for key, values in STUDY.items() if key in study)
            or ('newPerDay' in study and (type(study['newPerDay']) is not int or study['newPerDay'] not in NEW_PER_DAY))):
        choices = ', '.join(f'{key} ({" or ".join(values)})' for key, values in STUDY.items())
        raise Refusal(f'{name}: study, when given, sets one or more of {choices} and newPerDay '
                      f'({NEW_PER_DAY.start} to {NEW_PER_DAY.stop - 1}), and nothing else')


def verify_metadata(deck, source, metadata, python=sys.executable, gallery=ANYWHERE):
    """Hold a deck's rectoverso.json to the contract, then ask its source what each language's package is.

    `deck` says which deck and edition are expected: {"repository": <its id>, "tag": <its release tag>}
    (a gallery passes its own pin, so a deck that isn't the edition pinned is refused). Returns each
    language's expanded metadata, in the order of `languages`."""
    name = deck['repository']
    missing = [field for field in REQUIRED if field not in metadata]
    if missing:
        raise Refusal(f'{name}: missing {", ".join(missing)}')
    if set(deck) != {'repository', 'tag'}:
        raise Refusal(f'{name}: the registry only pins a tag; the deck carries its subject and covers')
    publication = metadata['publication']
    remote = publication.get('remote')
    if gallery.organization:
        canonical = gallery.organization + name
    else:
        canonical = remote if text(remote) and remote.startswith('https://') and remote.rstrip('/').rsplit('/', 1)[-1] == name else None
    if (metadata['id'] != name or metadata['releaseTag'] != deck['tag'] or 'v' + str(metadata['version']) != deck['tag']
            or canonical is None or remote != canonical
            or publication.get('release') != canonical + '/releases/tag/' + deck['tag']):
        raise Refusal(f'{name}: repository, version, tag or publication mismatch')
    if type(metadata['proOnly']) is not bool or type(publication.get('approved')) is not bool:
        raise Refusal(f'{name}: proOnly and publication.approved are true or false')
    if gallery.approved_only and publication['approved'] is not True:
        raise Refusal(f'{name}: only an approved deck, Pro or not (proOnly), enters the catalog')
    private = 'private' if metadata['proOnly'] else 'public'
    if gallery.pro_prefix and metadata['proOnly'] != pro(name, gallery) or publication.get('visibility') != private:
        raise Refusal(f'{name}: a Pro deck (proOnly) is private'
                      + (f' and named {gallery.pro_prefix}<title>' if gallery.pro_prefix else '')
                      + '; every other deck is public')
    # One GUID layout for every deck: a deck that names another form (`guidForm`) is refused.
    if ('guidForm' in metadata or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', str(metadata['guidPrefix']))
            or type(metadata['identityBase']) is not int):
        raise Refusal(f'{name}: invalid GUID prefix or identity base')
    rendered = metadata.get('renderedPictures', False)
    if type(rendered) is not bool:
        raise Refusal(f'{name}: renderedPictures is true or false')
    try:
        datetime.fromisoformat(metadata['contentModifiedAt'].replace('Z', '+00:00'))
    except (AttributeError, ValueError):
        raise Refusal(f'{name}: contentModifiedAt must be an ISO 8601 time')
    languages = metadata['languages']
    if (not isinstance(languages, dict) or not languages
            or any(not re.fullmatch(r'[a-z]{2}(?:-[A-Za-z0-9]+)*', str(language)) for language in languages)):
        raise Refusal(f'{name}: at least one shipped language is required')
    for field in LOCALIZED:
        value = metadata[field]
        if not isinstance(value, dict) or set(value) != set(languages) or not all(map(text, value.values())):
            raise Refusal(f'{name}: {field} in every shipped language is required')
    whats_new = metadata.get('whatsNew')
    if whats_new is not None and (not isinstance(whats_new, dict) or not whats_new or not set(whats_new) <= set(languages)
                                  or not all(map(text, whats_new.values()))):
        raise Refusal(f'{name}: whatsNew, when given, is this version\'s notes in shipped languages, none empty')
    play_label = metadata.get('playLabel')
    if play_label is not None and (not isinstance(play_label, dict) or not play_label
                                   or not set(play_label) <= set(languages)
                                   or not all(isinstance(word, str) and word == word.strip() and 0 < len(word) <= PLAY_LABEL_LIMIT
                                              and '\n' not in word for word in play_label.values())):
        raise Refusal(f'{name}: playLabel, when given, is the sound button\'s word in shipped languages, '
                      f'each on one line, 1 to {PLAY_LABEL_LIMIT} characters')
    verify_study(name, metadata.get('study'))
    categories = metadata['categories']
    if (not isinstance(categories, list) or not categories or len(set(map(str, categories))) != len(categories)
            or not all(isinstance(category, str) and category in CATEGORIES for category in categories)):
        raise Refusal(f'{name}: categories must list one or more of the contract\'s categories, once each')
    covers = metadata.get('covers')
    if covers is not None:
        if (not isinstance(covers, dict) or set(covers) != set(languages)
                or not all(isinstance(covers[language], dict) and set(covers[language]) == {'light', 'dark'}
                           and all(isinstance(covers[language][theme], list) and covers[language][theme]
                                   for theme in ('light', 'dark'))
                           for language in languages)):
            raise Refusal(f'{name}: each shipped language needs one or more light and dark cover files, in order')
        for language in languages:
            for theme in ('light', 'dark'):
                files = covers[language][theme]
                if len(set(map(str, files))) != len(files):
                    raise Refusal(f'{name}/{language}: a cover is listed once in its {theme} covers')
                for file in files:
                    parsed = cover_name(metadata['guidPrefix'], file) if text(file) else None
                    # A cover made for one appearance is only in that appearance's list; one named
                    # without an appearance may be in both.
                    if parsed is None or parsed[1] not in (None, theme):
                        raise Refusal(f'{name}/{language}: {file!r} isn\'t a {theme} cover\'s name, '
                                      f'{metadata["guidPrefix"]}[-<language>]-cover[-{theme}]-<n>.png')
                    # Only a cover without words serves several languages.
                    if parsed[0] is not None and parsed[0] != language:
                        raise Refusal(f'{name}/{language}: {file} has words in another language')
    if not text(metadata['creator']):
        raise Refusal(f'{name}: the deck\'s creator is required')
    deck_license(name, metadata)
    if not isinstance(metadata['sources'], list) or not metadata['sources']:
        raise Refusal(f'{name}: at least one source is required')
    for origin in metadata['sources']:
        if (not isinstance(origin, dict) or not all(text(origin.get(key)) for key in ('name', 'version', 'url', 'license'))
                or not origin['url'].startswith('https://')):
            raise Refusal(f'{name}: each source needs its name, version, license and https URL')
        if not open_license(origin['license']):
            raise Refusal(f'{name}: source {origin["name"]} needs an open license (no NC or ND)')
    credits = metadata['imageCredits']
    if (not isinstance(credits, list) or not all(isinstance(credit, dict) and text(credit.get('file')) for credit in credits)
            or len(credits) != metadata['pictures'] or len({credit['file'] for credit in credits}) != len(credits)):
        raise Refusal(f'{name}: image credit count mismatch')
    if not isinstance(metadata['sourceFiles'], dict):
        raise Refusal(f'{name}: sourceFiles names the paths the deck builds from')
    for key, path in metadata['sourceFiles'].items():
        if key != 'pictures' or credits:
            source_path(source, str(path))
    if credits and not rendered and 'pictures' not in metadata['sourceFiles']:
        raise Refusal(f'{name}: the pictures folder is missing from sourceFiles')
    for credit in credits:
        if credit.get('license') not in OPEN_LICENSES:
            raise Refusal(f'{name}: {credit.get("file")} needs an open license')
        if (Path(credit['file']).name != credit['file']
                or not picture_source(source, metadata, credit)
                or not text(credit.get('source')) or not text(credit.get('creator'))):
            raise Refusal(f'{name}: missing image or credit')
    for script in ('source_data.py', 'build.py', 'validate-anki.py', 'validate-rebuild.py'):
        source_tool(source, script)
    artifacts = []
    guids_seen, types_seen, decks_seen, artifact_ids, filenames = set(), set(), set(), set(), set()
    for language, artifact in languages.items():
        if not isinstance(artifact, dict) or 'sample' not in artifact:
            raise Refusal(f'{name}/{language}: the sample is missing')
        if (not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', str(artifact.get('id'))) or artifact['id'] in artifact_ids
                or set(artifact) != {'id', 'title', 'cards', 'package', 'sample'}):
            raise Refusal(f'{name}/{language}: invalid or duplicate artifact identity')
        artifact_ids.add(artifact['id'])
        if artifact['title'] != metadata['title'][language]:
            raise Refusal(f'{name}/{language}: the language\'s title differs from the deck\'s')
        package = artifact['package'] if isinstance(artifact['package'], dict) else {}
        file = package.get('file', '')
        if (set(package) != {'file'} or not isinstance(file, str) or Path(file).name != file or not file.endswith('.apkg')
                or file in filenames):
            raise Refusal(f'{name}/{language}: invalid release package name')
        filenames.add(file)
        expanded, notes, types, definition = source_inputs(source, language, python)
        expected = {key: value for key, value in metadata.items() if key != 'languages'}
        expected.update(id=artifact['id'], deckID=name, language=language, package=artifact['package'],
                        sample=artifact['sample'])
        if expanded != expected:
            raise Refusal(f'{name}/{language}: expanded metadata differs from the declared artifact')
        if (type(artifact['cards']) is not int or artifact['cards'] <= 0 or artifact['cards'] != metadata['cards']
                or sum(note.get('cards', 1) for note in notes) != artifact['cards']):
            raise Refusal(f'{name}/{language}: card count disagrees with the notes')
        guids = [note['guid'] for note in notes]
        prefix = guid_prefix(metadata, language)
        if len(set(guids)) != len(guids) or not all(guid.startswith(prefix) for guid in guids):
            raise Refusal(f'{name}/{language}: every note GUID must be unique and start with {prefix}')
        verify_sample(f'{name}/{language}', artifact['sample'], notes, metadata, source)
        verify_payloads(f'{name}/{language}', notes)
        verify_prerequisites(f'{name}/{language}', notes)
        kinds = types if isinstance(types, dict) else {str(index): kind for index, kind in enumerate(types)}
        if isinstance(types, dict) and any(note.get('model') not in kinds for note in notes):
            raise Refusal(f'{name}/{language}: a note uses an undeclared note type')
        type_ids = [kind['id'] for kind in kinds.values()]
        if (not type_ids or len(set(type_ids)) != len(type_ids) or guids_seen & set(guids)
                or types_seen & set(type_ids) or definition['id'] in decks_seen | types_seen | set(type_ids)):
            raise Refusal(f'{name}: language note, note type or deck identities collide')
        guids_seen.update(guids)
        types_seen.update(type_ids)
        decks_seen.add(definition['id'])
        artifacts.append(expanded)
    return artifacts


def payload(note):
    """A note's payload as the app reads it: the JSON object its "RectoVerso" field starts with (the
    field is HTML, so the JSON is escaped in it; what follows the object is left aside). None without one."""
    field = html.unescape((note.get('fields') or {}).get(PAYLOAD_FIELD) or '').lstrip()
    if not field.startswith('{'):
        return None
    try:
        return json.JSONDecoder().raw_decode(field)[0]
    except ValueError:
        return None


def verify_payloads(label, notes):
    """Each note's payload, when it has one, is one the app can read (schemas/card-payload.schema.json):
    a payload the app can't read costs the card its identity, so the check refuses it here."""
    rules = load_schema('card-payload')
    for note in notes:
        field = html.unescape((note.get('fields') or {}).get(PAYLOAD_FIELD) or '').lstrip()
        if not field:
            continue
        data = payload(note)
        if data is None:
            raise Refusal(f'{label}: {note["guid"]}: its {PAYLOAD_FIELD} field doesn\'t start with a JSON object')
        # Prerequisites have their own, more telling refusals (verify_prerequisites).
        found = [message for message in schema.errors(data, rules)
                 if not message.startswith(('requires', 'introduces'))]
        if found:
            raise Refusal(f'{label}: {note["guid"]}: its payload isn\'t one the app reads: ' + '; '.join(found[:3]))


def verify_prerequisites(label, notes):
    """What each card requires and introduces (docs/prerequisites.md), in the order the deck is written.

    Refused: a list that isn't one of tokens, each once; a token a card requires that no card of the
    same package introduces; a card that could never come (it waits for itself, or two cards wait
    for each other); and an order that asks before it teaches."""
    cards = []
    for note in notes:
        data = payload(note) or {}
        for key in ('requires', 'introduces'):
            tokens = data.get(key, [])
            if (type(tokens) is not list or len(set(map(str, tokens))) != len(tokens)
                    or not all(type(token) is str and TOKEN.fullmatch(token) for token in tokens)):
                raise Refusal(f'{label}: {note["guid"]}: {key} is a list of tokens, each once '
                              '(lowercase words and digits, hyphens between them)')
        cards.append((note['guid'], data.get('requires', []), data.get('introduces', [])))
    introduced = {token for _, _, introduces in cards for token in introduces}
    for guid, requires, _ in cards:
        missing = [token for token in requires if token not in introduced]
        if missing:
            raise Refusal(f'{label}: {guid} requires {", ".join(missing)}, which no card introduces')
    # Every card's turn must come: taught in any order that works, none is left waiting. Each
    # card is looked at once, as the last thing it misses is taught.
    missing = [len(set(requires)) for _, requires, _ in cards]
    held_back = {}
    for index, (_, requires, _) in enumerate(cards):
        for token in set(requires):
            held_back.setdefault(token, []).append(index)
    taught, ready = set(), [index for index, count in enumerate(missing) if count == 0]
    while ready:
        for token in cards[ready.pop()][2]:
            if token not in taught:
                taught.add(token)
                for index in held_back.get(token, ()):
                    missing[index] -= 1
                    if missing[index] == 0:
                        ready.append(index)
    stuck = next((card for card, count in zip(cards, missing) if count), None)
    if stuck:
        guid, requires, _ = stuck
        waited = [token for token in requires if token not in taught]
        raise Refusal(f'{label}: {guid} requires {", ".join(waited)}, which only cards waiting for it introduce')
    # And in the order written, the deck's own: each card after the cards that teach what it requires.
    taught = set()
    for guid, requires, introduces in cards:
        missing = [token for token in requires if token not in taught]
        if missing:
            raise Refusal(f'{label}: {guid} requires {", ".join(missing)}, which no earlier card introduces')
        taught.update(introduces)


def sample_card(sample):
    """A sample's note GUID and, for one card of a several-card note, its number (`<guid>/<n>`)."""
    match = re.fullmatch(r'(.+)/([1-9][0-9]*)', sample)
    return (match[1], int(match[2])) if match else (sample, None)


def verify_sample(label, sample, notes, metadata, source):
    """The sample a gallery opens alone, in the app's review: one card, with all its media.

    It names a note of this language's package by its GUID. A note that makes one card is named by
    its GUID alone; one card of a cloze of several blanks or an occlusion of several labels by its
    GUID and its cloze number (`<guid>/<n>`, the card Anki numbers ord n - 1). Every picture or
    sound its fields name is one of the deck's source files."""
    if not text(sample):
        raise Refusal(f'{label}: the sample is missing')
    guid, number = sample_card(sample)
    note = next((note for note in notes if note['guid'] == guid), None)
    if note is None or (number is not None and not any(
            re.search(r'\{\{c%d::' % number, str(value)) for value in (note.get('fields') or {}).values())):
        raise Refusal(f'{label}: the sample {sample} is not a card of this package')
    if number is None and note.get('cards', 1) != 1:
        raise Refusal(f'{label}: the sample {sample} can\'t stand alone: its note makes {note["cards"]} cards;'
                      f' name one of them as {guid}/<cloze number>')
    credited = {credit['file']: credit for credit in metadata['imageCredits']}
    for value in (note.get('fields') or {}).values():
        for picture, sound in MEDIA.findall(str(value)):
            folder = metadata['sourceFiles'].get('pictures' if picture else 'sounds')
            file = picture or sound
            if picture and file in credited and metadata.get('renderedPictures'):
                if not picture_source(source, metadata, credited[file]):
                    raise Refusal(f'{label}: the sample {sample} can\'t stand alone: its media {file} is missing')
                continue
            if ((picture and file not in credited) or not folder or Path(file).name != file
                    or not (source / folder / file).is_file()):
                raise Refusal(f'{label}: the sample {sample} can\'t stand alone: its media {file} is missing')


def check(source, python=sys.executable, gallery=ANYWHERE, deck=None):
    """Check the deck in the folder `source`: its rectoverso.json, then each language's notes.

    Returns each language's expanded metadata, or raises `Refusal`. `deck` is the edition expected
    ({"repository": …, "tag": …}); without one, the deck is checked as the edition it says it is."""
    source = Path(source).resolve()
    manifest = source / 'rectoverso.json'
    if not manifest.is_file():
        raise Refusal(f'{source.name}: no rectoverso.json at the root of the deck')
    try:
        metadata = json.loads(manifest.read_text())
    except ValueError as error:
        raise Refusal(f'{source.name}: rectoverso.json isn\'t JSON ({error})') from error
    if not isinstance(metadata, dict):
        raise Refusal(f'{source.name}: rectoverso.json holds one JSON object')
    name = metadata.get('id') if text(metadata.get('id')) else source.name
    deck = deck or {'repository': name, 'tag': metadata.get('releaseTag')}
    # The rules below say what is wrong in the contract's own words; the schema then catches what
    # they don't name (a value of the wrong type in a field they only read).
    shape = schema.errors(metadata, load_schema('rectoverso'))
    try:
        artifacts = verify_metadata(deck, source, metadata, python, gallery)
    except Refusal:
        raise
    except (AttributeError, KeyError, TypeError) as error:
        raise Refusal(f'{name}: rectoverso.json isn\'t in the contract\'s shape: '
                      + ('; '.join(shape[:5]) if shape else repr(error))) from error
    if shape:
        raise Refusal(f'{name}: rectoverso.json isn\'t in the contract\'s shape: ' + '; '.join(shape[:5]))
    return artifacts
