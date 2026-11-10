"""The contract's rules, on small decks made for each test: no Anki, no network, nothing outside this kit."""
import base64
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deck_kit import contract  # noqa: E402

REMOTE = 'https://github.com/rectoversohq/rectoverso-test'
# A payload's identities, as a deck writes them: UUIDs (docs/card-payload.md).
BOOK = '6f1d2c3b-4a59-4e68-9b7a-0c1d2e3f4a5b'
CARD = '0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d'

# A deck's rectoverso.json in an earlier layout (the public Capitals deck's 0.1.0-rc.1, as released): refused.
PUBLISHED_CAPITALS = {
    'id': 'rectoverso-capitals', 'version': '0.1.0-rc.1', 'status': 'prerelease',
    'title': {'en': 'Capitals', 'fr': 'Capitales'}, 'subject': {'en': 'Geography', 'fr': 'Géographie'},
    'license': 'CC-BY-4.0', 'proOnly': False, 'identityBase': 1867200400, 'guidPrefix': 'rv-capitals',
    'roster': 'iso-3166-1-249-applicable-v1', 'cards': 488, 'sounds': 0, 'pictures': 0, 'imageCredits': [],
    'sourceFiles': {'pictures': 'source/media', 'places': 'source/places.json'}, 'releaseTag': 'v0.1.0-rc.1',
    'languages': {
        'en': {'id': 'rectoverso-capitals-en', 'title': 'Capitals', 'cards': 488,
               'package': {'file': 'Capitals-en-488.apkg'}},
        'fr': {'id': 'rectoverso-capitals-fr', 'title': 'Capitales', 'cards': 488,
               'package': {'file': 'Capitales-fr-488.apkg'}}},
    'contentModifiedAt': '2026-11-02T13:44:58Z',
    'publication': {'remote': 'https://github.com/rectoversohq/rectoverso-capitals',
                    'release': 'https://github.com/rectoversohq/rectoverso-capitals/releases/tag/v0.1.0-rc.1',
                    'approved': True, 'visibility': 'public'}}

# The layout's source interface, as Flags and Capitals write it: several note types a language.
SOURCE_DATA = '''import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def inputs(language):
    meta = json.loads((ROOT / 'rectoverso.json').read_text())
    artifact = meta['languages'][language]
    data = json.loads((ROOT / 'source/languages' / (language + '.json')).read_text())
    localized = dict(meta)
    localized.pop('languages')
    localized.update(id=artifact['id'], deckID=meta['id'], language=language, package=artifact['package'],
                     sample=artifact['sample'])
    return localized, data['notes'], data['types'], data['deck']
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()

class ContractTests(unittest.TestCase):
    """The contract every deck holds to (docs/contract.md), on a small deck made for each test."""

    gallery = contract.RECTOVERSO

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / 'source'
        (self.source / 'scripts/checks').mkdir(parents=True)
        (self.source / 'source/media').mkdir(parents=True)
        (self.source / 'source/languages').mkdir()
        (self.source / 'source/media/flag.png').write_bytes(b'picture')
        (self.source / 'scripts/source_data.py').write_text(SOURCE_DATA)
        for tool in ('scripts/build.py', 'scripts/checks/validate-anki.py', 'scripts/checks/validate-rebuild.py'):
            (self.source / tool).write_text('')
        self.entry = {'repository': 'rectoverso-test', 'tag': 'v1.0.0'}
        self.metadata = {
            'id': 'rectoverso-test', 'version': '1.0.0', 'status': 'release', 'releaseTag': 'v1.0.0',
            'guidPrefix': 'rv-test', 'identityBase': 1000, 'contentModifiedAt': '2026-11-03T00:00:00Z',
            'publication': {'remote': REMOTE, 'release': REMOTE + '/releases/tag/v1.0.0',
                            'approved': True, 'visibility': 'public'},
            'title': {'en': 'Test', 'fr': 'Essai'}, 'subject': {'en': 'Geography', 'fr': 'Géographie'},
            'headline': {'en': 'Every place, by its flag', 'fr': 'Chaque lieu, par son drapeau'},
            'description': {'en': 'Two hundred flags.', 'fr': 'Deux cents drapeaux.'},
            'categories': ['geography', 'history'], 'cards': 3, 'pictures': 1, 'sounds': 0,
            'creator': 'Simon Pinkas', 'license': 'CC-BY-4.0',
            'sources': [{'name': 'Natural Earth', 'version': '5.1.2', 'license': 'Public domain',
                         'url': 'https://www.naturalearthdata.com/about/terms-of-use/'}],
            'imageCredits': [{'file': 'flag.png', 'source': 'https://example.com/flag', 'creator': 'Author',
                              'license': 'Public domain'}],
            'proOnly': False, 'sourceFiles': {'pictures': 'source/media'}, 'languages': {}}
        self.data = {}
        for offset, (language, title) in enumerate([('en', 'Test'), ('fr', 'Essai')]):
            self.metadata['languages'][language] = {
                'id': 'rectoverso-test-' + language, 'title': title, 'cards': 3,
                'package': {'file': f'{title}-{language}-3.apkg'}, 'sample': f'rv-test-{language}-che-place-name'}
            types = {'place-name': {'id': 1000 + 100 * offset}, 'name-place': {'id': 1001 + 100 * offset}}
            notes = [{'guid': f'rv-test-{language}-che-place-name', 'model': 'place-name',
                      'fields': {'Flag': '<img src="flag.png" alt="Flag">', 'Place': 'Switzerland'}},
                     {'guid': f'rv-test-{language}-che-name-place', 'model': 'name-place'},
                     {'guid': f'rv-test-{language}-ita-place-name', 'model': 'place-name'}]
            self.data[language] = {'notes': notes, 'types': types, 'deck': {'id': 2000 + offset}}

    def verify(self, entry=None, metadata=None):
        metadata = self.metadata if metadata is None else metadata
        (self.source / 'rectoverso.json').write_text(json.dumps(metadata))
        for language, data in self.data.items():
            (self.source / 'source/languages' / (language + '.json')).write_text(json.dumps(data))
        return contract.verify_metadata(entry or self.entry, self.source, metadata, sys.executable,
                                        gallery=self.gallery)

    def test_duplicate_artifact_id_or_package_name_is_refused(self):
        for key, reason in [('id', 'duplicate artifact'), ('package', 'release package name')]:
            with self.subTest(key=key):
                metadata = copy.deepcopy(self.metadata)
                metadata['languages']['fr'][key] = copy.deepcopy(metadata['languages']['en'][key])
                with self.assertRaisesRegex(ValueError, reason):
                    self.verify(metadata=metadata)

    def test_published_flags_and_capitals_are_refused_until_republished(self):
        entry = {'repository': 'rectoverso-capitals', 'tag': 'v0.1.0-rc.1'}
        with self.assertRaisesRegex(
                ValueError, r'^rectoverso-capitals: missing headline, description, categories, creator, sources$'):
            contract.verify_metadata(entry, self.source, copy.deepcopy(PUBLISHED_CAPITALS), sys.executable)

    def test_missing_gallery_fields_are_refused(self):
        for field in ('headline', 'description', 'categories', 'creator', 'license', 'sources', 'title',
                      'proOnly'):
            with self.subTest(field=field):
                metadata = copy.deepcopy(self.metadata)
                del metadata[field]
                with self.assertRaisesRegex(ValueError, 'missing ' + field):
                    self.verify(metadata=metadata)

    def test_every_shipped_language_needs_its_text(self):
        for field in ('title', 'subject', 'headline', 'description'):
            for value in ({'en': 'Text'}, {'en': 'Text', 'fr': ' '}):
                with self.subTest(field=field, value=value):
                    metadata = copy.deepcopy(self.metadata)
                    metadata[field] = value
                    with self.assertRaisesRegex(ValueError, field + ' in every shipped language'):
                        self.verify(metadata=metadata)
        self.metadata['languages']['fr']['title'] = 'Autre'
        with self.assertRaisesRegex(ValueError, 'title differs'):
            self.verify()

    def test_whats_new_is_optional_and_in_shipped_languages(self):
        self.verify()
        metadata = copy.deepcopy(self.metadata)
        metadata['whatsNew'] = {'en': 'Sixty flags redrawn.'}
        self.verify(metadata=metadata)
        for value in ({}, {'de': 'Neu.'}, {'en': ' '}, 'Sixty flags redrawn.', {'en': 3}):
            with self.subTest(value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata['whatsNew'] = value
                with self.assertRaisesRegex(ValueError, 'whatsNew'):
                    self.verify(metadata=metadata)

    def test_a_play_label_is_optional_short_and_in_shipped_languages(self):
        metadata = copy.deepcopy(self.metadata)
        metadata['playLabel'] = {'en': 'Listen', 'fr': 'Écouter'}
        self.verify(metadata=metadata)
        for value in ({}, {'de': 'Hören'}, {'en': ' Listen'}, {'en': ''}, {'en': 'a' * (contract.PLAY_LABEL_LIMIT + 1)},
                      {'en': 'Lis\nten'}, {'en': 3}, 'Listen'):
            with self.subTest(value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata['playLabel'] = value
                with self.assertRaisesRegex(ValueError, 'playLabel'):
                    self.verify(metadata=metadata)

    def test_a_study_preset_is_optional_and_only_what_deck_options_offer(self):
        for value in ({'newCards': 'deckOrder', 'newPerDay': 6, 'newPosition': 'afterReviews'}, {'newPerDay': 999},
                      {'newCards': 'random'}, {'newPosition': 'mixed'}):
            with self.subTest(value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata['study'] = value
                self.verify(metadata=metadata)
        for value in ({}, {'newPerDay': 0}, {'newPerDay': 1000}, {'newPerDay': '6'}, {'newPerDay': True},
                      {'newPerDay': 6.0}, {'newCards': 'alphabetical'}, {'newPosition': 'first'},
                      {'newCards': 'deckOrder', 'newperday': 6}, 'deckOrder', ['deckOrder']):
            with self.subTest(value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata['study'] = value
                with self.assertRaisesRegex(ValueError, 'study'):
                    self.verify(metadata=metadata)

    def test_categories_come_from_the_contract_list(self):
        self.assertEqual(self.verify()[0]['categories'], ['geography', 'history'])
        for value in ([], ['geografy'], ['geography', 'geography'], 'geography', [{'en': 'Geography'}]):
            with self.subTest(value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata['categories'] = value
                with self.assertRaisesRegex(ValueError, 'categor'):
                    self.verify(metadata=metadata)

    def test_empty_creator_or_source_is_refused(self):
        for field, value, reason in [('creator', ' ', 'creator'), ('sources', [], 'source'),
                                     ('sources', [{'name': 'Natural Earth', 'version': '', 'license': 'Public domain',
                                                   'url': 'https://example.com'}], 'source needs'),
                                     ('sources', [{'name': 'Natural Earth', 'version': '5', 'license': 'Public domain',
                                                   'url': 'http://example.com'}], 'source needs')]:
            with self.subTest(field=field, value=value):
                metadata = copy.deepcopy(self.metadata)
                metadata[field] = value
                with self.assertRaisesRegex(ValueError, reason):
                    self.verify(metadata=metadata)

    def test_open_license_violations_are_refused(self):
        for path, value in [(('license',), 'CC-BY-NC-4.0'),
                            (('imageCredits', 0, 'license'), 'CC-BY-ND-4.0'),
                            (('sources', 0, 'license'), 'CC BY-NC-SA 4.0')]:
            with self.subTest(path=path):
                metadata = copy.deepcopy(self.metadata)
                target = metadata
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaisesRegex(ValueError, 'open licen'):
                    self.verify(metadata=metadata)

    def pro_deck(self):
        """The same deck as a Pro deck: its private rectoverso-pro- repository, its own terms."""
        name, remote = 'rectoverso-pro-test', 'https://github.com/rectoversohq/rectoverso-pro-test'
        metadata = copy.deepcopy(self.metadata)
        metadata.update(id=name, proOnly=True, license='LicenseRef-RectoVerso-Personal-Use-Draft',
                        publication={'remote': remote, 'release': remote + '/releases/tag/v1.0.0',
                                     'approved': True, 'visibility': 'private'})
        return {'repository': name, 'tag': 'v1.0.0'}, metadata

    def test_a_pro_deck_enters_the_catalog_from_its_private_repository(self):
        entry, metadata = self.pro_deck()
        artifacts = self.verify(entry=entry, metadata=metadata)
        self.assertEqual([(a['deckID'], a['proOnly']) for a in artifacts],
                         [('rectoverso-pro-test', True), ('rectoverso-pro-test', True)])
        metadata['license'] = 'CC-BY-4.0'
        self.assertEqual(len(self.verify(entry=entry, metadata=metadata)), 2)

    def test_pro_and_privacy_go_together(self):
        entry, pro = self.pro_deck()
        for label, entry, metadata in [
                ('public deck marked Pro', self.entry, self.metadata | {'proOnly': True}),
                ('public deck in a private repository',
                 self.entry, self.metadata | {'publication': self.metadata['publication'] | {'visibility': 'private'}}),
                ('Pro deck not marked Pro', entry, pro | {'proOnly': False, 'license': 'CC-BY-4.0'}),
                ('Pro deck in a public repository',
                 entry, pro | {'publication': pro['publication'] | {'visibility': 'public'}})]:
            with self.subTest(label), self.assertRaisesRegex(ValueError, 'a Pro deck .proOnly. is private'):
                self.verify(entry=entry, metadata=metadata)
        for metadata in (self.metadata, pro):
            with self.subTest(approved=False), self.assertRaisesRegex(ValueError, 'only an approved deck'):
                self.verify(entry=entry if metadata is pro else self.entry,
                            metadata=metadata | {'publication': metadata['publication'] | {'approved': False}})

    def test_only_a_pro_deck_may_have_its_own_terms(self):
        entry, pro = self.pro_deck()
        with self.assertRaisesRegex(ValueError, 'open license$'):
            self.verify(metadata=self.metadata | {'license': 'LicenseRef-RectoVerso-Personal-Use-Draft'})
        for license in ('Personal use', 'CC-BY-NC-4.0', 'LicenseRef-'):
            with self.subTest(license=license), self.assertRaisesRegex(ValueError, 'its own LicenseRef- terms'):
                self.verify(entry=entry, metadata=pro | {'license': license})

    def test_publication_must_name_this_repository_and_tag(self):
        for change in ({'releaseTag': 'v2.0.0'}, {'version': '2.0.0'}, {'id': 'rectoverso-other'},
                       {'publication': self.metadata['publication'] | {'remote': 'https://example.com'}},
                       {'publication': self.metadata['publication'] | {'release': REMOTE + '/releases/tag/v0.9.0'}}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'mismatch'):
                self.verify(metadata=self.metadata | change)

    def test_card_count_must_agree_with_the_notes(self):
        self.metadata['languages']['fr']['cards'] = 4
        with self.assertRaisesRegex(ValueError, 'card count'):
            self.verify()
        self.metadata['languages']['fr']['cards'] = 3
        self.data['fr']['notes'].pop()
        with self.assertRaisesRegex(ValueError, 'card count'):
            self.verify()
        # A note that makes several cards, as an image occlusion does, says how many.
        self.data['fr']['notes'][1]['cards'] = 2
        self.assertEqual(len(self.verify()), 2)

    def prerequisites(self, language, *cards):
        """Each note's payload, in order: what it requires and what it introduces (None: no payload)."""
        for note, card in zip(self.data[language]['notes'], cards):
            if card is not None:
                payload = {'v': 1, 'book': BOOK, 'card': CARD, 'kind': 'basic'} | card
                note.setdefault('fields', {})['RectoVerso'] = html.escape(json.dumps(payload)) + '<img src="flag.png">'

    def test_a_card_requires_only_what_a_card_of_its_package_introduces(self):
        for language in self.data:
            self.prerequisites(language, {'introduces': ['a']}, {'introduces': ['i']}, {'requires': ['a', 'i']})
        self.assertEqual(len(self.verify()), 2)
        # English introduces e; French requires it, and French is a package of its own.
        self.prerequisites('en', {'introduces': ['a', 'e']})
        self.prerequisites('fr', None, None, {'requires': ['a', 'e']})
        with self.assertRaisesRegex(ValueError, 'rectoverso-test/fr: .*ita-place-name requires e, which no card introduces'):
            self.verify()

    def test_prerequisites_are_lists_of_tokens(self):
        for key in ('requires', 'introduces'):
            for value in ('a', ['a', ''], ['a', 7], ['Hira A'], ['a', 'a'], {'a': True}):
                with self.subTest(key=key, value=value):
                    self.prerequisites('fr', {'introduces': ['a']}, {key: value})
                    with self.assertRaisesRegex(ValueError, 'che-name-place: ' + key + ' is a list of tokens'):
                        self.verify()
        self.prerequisites('fr', {'introduces': ['hira-3042']}, {'requires': ['hira-3042'], 'introduces': []})
        self.assertEqual(len(self.verify()), 2)

    def test_the_authored_order_teaches_before_it_asks(self):
        # A card can't wait for itself, nor two cards for each other: neither would ever come.
        self.prerequisites('fr', {'requires': ['a'], 'introduces': ['a']})
        with self.assertRaisesRegex(ValueError, 'che-place-name requires a, which only cards waiting for it introduce'):
            self.verify()
        self.prerequisites('fr', {'requires': ['i'], 'introduces': ['a']}, {'requires': ['a'], 'introduces': ['i']}, {})
        with self.assertRaisesRegex(ValueError, 'requires i, which only cards waiting for it introduce'):
            self.verify()
        # Every card's turn comes, but not in the order written: in deck order, あい would wait behind い.
        self.prerequisites('fr', {'introduces': ['a']}, {'requires': ['a', 'i']}, {'introduces': ['i']})
        with self.assertRaisesRegex(ValueError, 'che-name-place requires i, which no earlier card introduces'):
            self.verify()
        self.prerequisites('fr', {'introduces': ['a']}, {'introduces': ['i']}, {'requires': ['a', 'i']})
        self.assertEqual(len(self.verify()), 2)

    def test_prerequisites_are_checked_in_one_pass_over_a_large_deck(self):
        # A long course, each card building on the one before, then one taught only by a card
        # that waits for it: found, without comparing every card with every other.
        count = 20000
        notes = [{'guid': f'rv-test-fr-{index}', 'fields': {'RectoVerso': json.dumps(
            {'requires': [f't{index - 1}'] if index else [], 'introduces': [f't{index}']})}} for index in range(count)]
        contract.verify_prerequisites('rectoverso-test/fr', notes)
        notes[count // 2]['fields']['RectoVerso'] = json.dumps({'requires': [f't{count // 2}'], 'introduces': [f't{count // 2}']})
        with self.assertRaisesRegex(ValueError, f'rv-test-fr-{count // 2} requires t{count // 2}, which only cards waiting'):
            contract.verify_prerequisites('rectoverso-test/fr', notes)

    def test_several_note_types_keep_distinct_identities_across_languages(self):
        for language, field, value in [('fr', 'types', {'place-name': {'id': 1100}, 'name-place': {'id': 1001}}),
                                       ('fr', 'deck', {'id': 2000}),
                                       ('en', 'types', {'place-name': {'id': 1000}, 'name-place': {'id': 1000}})]:
            with self.subTest(language=language, field=field):
                original = self.data[language][field]
                self.data[language][field] = value
                with self.assertRaisesRegex(ValueError, 'identities collide'):
                    self.verify()
                self.data[language][field] = original

    def test_note_identities_carry_the_deck_prefix_and_language(self):
        for guid in ('rv-test-en-che-place-name-copy', 'rv-other-fr-che-place-name', 'rv-test-fr-che-name-place'):
            with self.subTest(guid=guid):
                notes = copy.deepcopy(self.data['fr']['notes'])
                self.data['fr']['notes'][0]['guid'] = guid
                with self.assertRaisesRegex(ValueError, 'GUID'):
                    self.verify()
                self.data['fr']['notes'] = notes
        self.data['fr']['notes'][1]['model'] = 'undeclared'
        with self.assertRaisesRegex(ValueError, 'undeclared note type'):
            self.verify()

    def test_every_deck_has_the_one_guid_layout(self):
        # One layout for every deck: the prefix, the language, then the note (rv-test-fr-…). A compact
        # form (rvPTfrV1001) and any guidForm key are refused.
        for change in ({'guidForm': 'compact'}, {'guidForm': 'hyphenated'}, {'guidPrefix': 'rvPT'}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'GUID'):
                self.verify(metadata=self.metadata | change)
        self.data['fr']['notes'][1]['guid'] = 'rv-testfrche-name-place'
        with self.assertRaisesRegex(ValueError, 'GUID must be unique and start with rv-test-fr-'):
            self.verify()

    def test_rendered_pictures_are_credited_by_their_original(self):
        # A deck whose build renders its pictures (the Periodic table, from its SVGs) ships no raster
        # in Git: each credit names the original the build renders, in the repository.
        (self.source / 'source/media/flag.png').unlink()
        with self.assertRaisesRegex(ValueError, 'missing image or credit'):
            self.verify()
        (self.source / 'artwork').mkdir()
        (self.source / 'artwork/flag.svg').write_text('<svg/>')
        self.metadata['imageCredits'][0]['original'] = 'artwork/flag.svg'
        self.metadata['renderedPictures'] = True
        del self.metadata['sourceFiles']['pictures']
        self.assertEqual(len(self.verify()), 2)
        for original in ('artwork/other.svg', '../flag.svg', None):
            with self.subTest(original=original):
                metadata = copy.deepcopy(self.metadata)
                metadata['imageCredits'][0]['original'] = original
                with self.assertRaisesRegex(ValueError, 'missing'):
                    self.verify(metadata=metadata)
        with self.assertRaisesRegex(ValueError, 'renderedPictures is true or false'):
            self.verify(metadata=self.metadata | {'renderedPictures': 'yes'})
        with self.assertRaisesRegex(ValueError, 'pictures folder is missing'):
            self.verify(metadata=self.metadata | {'renderedPictures': False})

    def test_each_language_names_its_own_sample(self):
        artifacts = self.verify()
        self.assertEqual([a['sample'] for a in artifacts], ['rv-test-en-che-place-name', 'rv-test-fr-che-place-name'])
        for sample in (None, ' '):
            with self.subTest(sample=sample):
                metadata = copy.deepcopy(self.metadata)
                if sample is None:
                    del metadata['languages']['fr']['sample']
                else:
                    metadata['languages']['fr']['sample'] = sample
                with self.assertRaisesRegex(ValueError, r'^rectoverso-test/fr: the sample is missing$'):
                    self.verify(metadata=metadata)

    def test_sample_must_be_a_card_of_its_own_package(self):
        # The English card's id isn't a French card: each package names its own.
        for sample in ('rv-test-en-che-place-name', 'rv-test-fr-deu-place-name'):
            with self.subTest(sample=sample):
                self.metadata['languages']['fr']['sample'] = sample
                with self.assertRaisesRegex(ValueError, 'sample ' + sample + ' is not a card of this package'):
                    self.verify()

    def test_sample_of_a_several_card_note_cannot_stand_alone(self):
        # A cloze of several blanks or an occlusion of several labels: its cards are siblings.
        self.data['fr']['notes'][0]['cards'] = 2
        self.data['fr']['notes'].pop()
        with self.assertRaisesRegex(ValueError, 'sample rv-test-fr-che-place-name can.t stand alone: its note makes 2 cards'):
            self.verify()
        self.metadata['languages']['fr']['sample'] = 'rv-test-fr-che-name-place'
        self.assertEqual(self.verify()[1]['sample'], 'rv-test-fr-che-name-place')

    def test_sample_names_one_card_of_a_several_card_note_by_its_number(self):
        # An occlusion of several labels (or a cloze of several blanks) names its card by the cloze's
        # number: <guid>/79 is a periodic table's Au, the card Anki numbers ord 78.
        note = self.data['fr']['notes'][0]
        note.update(cards=2, fields={'Image': '<img src="flag.png">',
                                     'Occlusion': '{{c1::image-occlusion:rect:left=.1}}{{c79::image-occlusion:rect:left=.2}}'})
        self.data['fr']['notes'].pop()
        self.metadata['languages']['fr']['sample'] = 'rv-test-fr-che-place-name/79'
        self.assertEqual(self.verify()[1]['sample'], 'rv-test-fr-che-place-name/79')
        for sample in ('rv-test-fr-che-place-name/2', 'rv-test-fr-che-place-name/0', 'rv-test-fr-che-place-name/079'):
            with self.subTest(sample=sample):
                self.metadata['languages']['fr']['sample'] = sample
                with self.assertRaisesRegex(ValueError, 'sample ' + sample + ' is not a card of this package'):
                    self.verify()
        self.assertEqual(contract.sample_card('rv-test-fr-che-place-name/79'), ('rv-test-fr-che-place-name', 79))
        self.assertEqual(contract.sample_card('rv-test-fr-che-place-name'), ('rv-test-fr-che-place-name', None))

    def test_sample_with_missing_media_cannot_stand_alone(self):
        fields = self.data['en']['notes'][0]['fields']
        for value in ('<img alt="Flag" src="other.png">', '[sound:anthem.mp3]', '<IMG SRC=\'../flag.png\'>'):
            with self.subTest(value=value):
                fields['Flag'] = value
                with self.assertRaisesRegex(ValueError, 'can.t stand alone: its media .* is missing'):
                    self.verify()
        # A file in the folder but not credited is missing from the deck too.
        (self.source / 'source/media/other.png').write_bytes(b'picture')
        fields['Flag'] = '<img src="other.png">'
        with self.assertRaisesRegex(ValueError, 'its media other.png is missing'):
            self.verify()
        (self.source / 'source/sounds').mkdir()
        (self.source / 'source/sounds/anthem.mp3').write_bytes(b'sound')
        self.metadata['sourceFiles']['sounds'] = 'source/sounds'
        fields['Flag'] = '<img src="flag.png"> [sound:anthem.mp3]'
        self.assertEqual(len(self.verify()), 2)

    def test_registry_entry_only_pins_the_tag(self):
        with self.assertRaisesRegex(ValueError, 'only pins'):
            self.verify(entry=self.entry | {'subject': {'en': 'Geography', 'fr': 'Géographie'}})

    def test_tools_are_in_scripts_never_at_the_root_or_outside(self):
        (self.source / 'scripts/checks/validate-anki.py').rename(self.source / 'validate-anki.py')
        with self.assertRaisesRegex(ValueError, 'missing or external'):
            self.verify()
        outside = self.root / 'external.py'
        outside.write_text('')
        (self.source / 'scripts/checks/validate-anki.py').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'external'):
            self.verify()

    def test_picture_folder_is_needed_only_with_pictures(self):
        (self.source / 'source/media/flag.png').unlink()
        with self.assertRaisesRegex(ValueError, 'missing image'):
            self.verify()
        (self.source / 'source/media').rmdir()
        self.metadata.update(pictures=0, imageCredits=[])
        for language, artifact in self.metadata['languages'].items():
            artifact['sample'] = f'rv-test-{language}-che-name-place'
        self.assertEqual(len(self.verify()), 2)

    def test_a_cover_is_named_by_its_deck_theme_and_place(self):
        """A cover's name: `<guidPrefix>[-<language>]-cover[-<light|dark>]-<n>.png` (docs/covers.md)."""
        fr = {'light': ['rv-test-fr-cover-light-1.png'], 'dark': ['rv-test-fr-cover-dark-1.png']}
        for en, reason in (({'light': ['cover.png'], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light cover's name"),
                           ({'light': ['rv-other-cover-light-1.png'], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light"),
                           ({'light': ['rv-test-cover-dark-1.png'], 'dark': ['rv-test-cover-dark-2.png']}, "isn't a light"),
                           ({'light': ['rv-test-cover-light-0.png'], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light"),
                           ({'light': ['rv-test-cover-light-1.webp'], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light"),
                           ({'light': ['covers/rv-test-cover-light-1.png'], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light"),
                           ({'light': [''], 'dark': ['rv-test-cover-dark-1.png']}, "isn't a light"),
                           ({'light': ['rv-test-cover-light-1.png'], 'dark': ['rv-test.apkg']}, "isn't a dark"),
                           ({'light': ['rv-test-cover-light-1.png', 'rv-test-cover-light-1.png'],
                             'dark': ['rv-test-cover-dark-1.png']}, 'listed once'),
                           ({'light': ['rv-test-cover-1.png'], 'dark': ['rv-test-cover-1.png', 'rv-test-cover-1.png']},
                            'listed once'),
                           ({'light': ['rv-test-cover-light-1.png'], 'dark': ['rv-test-cover-light-1.png']}, "isn't a dark"),
                           ({'light': ['rv-test-fr-cover-light-1.png'], 'dark': ['rv-test-cover-dark-1.png']},
                            'words in another language')):
            self.metadata['covers'] = {'en': en, 'fr': fr}
            with self.subTest(en=en), self.assertRaisesRegex(ValueError, reason):
                self.verify()


if __name__ == '__main__':
    unittest.main()
