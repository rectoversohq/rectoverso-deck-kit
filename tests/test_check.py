"""The check as an author runs it: on a deck's folder, for any gallery or for RectoVerso's own."""
import contextlib
import html
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

import check as command  # noqa: E402
from deck_kit import ANYWHERE, RECTOVERSO, Refusal, check, contract  # noqa: E402

EXAMPLE = KIT / 'examples/morse-starter'


class ExampleDeckTests(unittest.TestCase):
    """The worked example (examples/morse-starter) holds to the contract, prerequisites included."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.deck = Path(self.temporary.name) / 'morse-starter'
        shutil.copytree(EXAMPLE, self.deck)

    def metadata(self, **changes):
        metadata = json.loads((self.deck / 'rectoverso.json').read_text())
        metadata.update(changes)
        (self.deck / 'rectoverso.json').write_text(json.dumps(metadata))
        return metadata

    def test_the_example_passes_in_every_language(self):
        artifacts = check(EXAMPLE)
        self.assertEqual([(a['id'], a['language'], a['cards']) for a in artifacts],
                         [('morse-starter-en', 'en', 7), ('morse-starter-fr', 'fr', 7)])

    def test_its_words_wait_for_their_letters(self):
        for language in ('en', 'fr'):
            _, notes, _, _ = contract.source_inputs(EXAMPLE, language)
            payloads = [contract.payload(note) for note in notes]
            self.assertTrue(any(p.get('requires') for p in payloads) and any(p.get('introduces') for p in payloads))
            taught = set()
            for note, data in zip(notes, payloads):
                self.assertLessEqual(set(data.get('requires', [])), taught, note['guid'])
                taught.update(data.get('introduces', []))

    def test_a_deck_is_checked_wherever_it_lives_but_a_gallery_has_its_own_rules(self):
        self.assertEqual(len(check(self.deck, gallery=ANYWHERE)), 2)
        # RectoVerso's gallery takes decks of its own organization, approved.
        with self.assertRaisesRegex(Refusal, 'repository, version, tag or publication mismatch'):
            check(self.deck, gallery=RECTOVERSO)
        gallery = contract.Gallery(organization='https://github.com/example/', approved_only=True)
        with self.assertRaisesRegex(Refusal, 'only an approved deck'):
            check(self.deck, gallery=gallery)
        publication = self.metadata()['publication'] | {'approved': True}
        self.metadata(publication=publication)
        self.assertEqual(len(check(self.deck, gallery=gallery)), 2)

    def test_the_publication_names_the_decks_own_repository(self):
        publication = self.metadata()['publication']
        for change in ({'remote': 'https://github.com/example/another-deck'}, {'remote': 'http://github.com/example/morse-starter'},
                       {'release': 'https://github.com/example/morse-starter/releases/tag/v9.9.9'}):
            with self.subTest(change=change):
                self.metadata(publication=publication | change)
                with self.assertRaisesRegex(Refusal, 'repository, version, tag or publication mismatch'):
                    check(self.deck)
        self.metadata(publication=publication | {'approved': 'yes'})
        with self.assertRaisesRegex(Refusal, 'proOnly and publication.approved are true or false'):
            check(self.deck)
        self.metadata(publication=publication, proOnly=True)
        with self.assertRaisesRegex(Refusal, 'a Pro deck \\(proOnly\\) is private; every other deck is public'):
            check(self.deck)

    def test_the_edition_expected_is_the_edition_checked(self):
        with self.assertRaisesRegex(Refusal, 'repository, version, tag or publication mismatch'):
            check(self.deck, deck={'repository': 'morse-starter', 'tag': 'v1.0.1'})

    def test_a_folder_without_a_readable_rectoverso_json_is_refused(self):
        (self.deck / 'rectoverso.json').write_text('{"id": ')
        with self.assertRaisesRegex(Refusal, "rectoverso.json isn't JSON"):
            check(self.deck)
        (self.deck / 'rectoverso.json').write_text('[]')
        with self.assertRaisesRegex(Refusal, 'holds one JSON object'):
            check(self.deck)
        (self.deck / 'rectoverso.json').unlink()
        with self.assertRaisesRegex(Refusal, 'no rectoverso.json at the root'):
            check(self.deck)

    def test_a_value_of_the_wrong_shape_is_named_by_the_schema(self):
        self.metadata(sources='the dictionary')
        with self.assertRaisesRegex(Refusal, 'at least one source is required'):
            check(self.deck)
        self.metadata(sources=json.loads((EXAMPLE / 'rectoverso.json').read_text())['sources'], version='one')
        with self.assertRaisesRegex(Refusal, 'repository, version, tag or publication mismatch'):
            check(self.deck)
        # What the rules only read, the schema holds: a key of the wrong type, a version that isn't one.
        self.metadata(version='1.0', releaseTag='v1.0')
        self.metadata(publication=self.metadata()['publication'] | {'release': 'https://github.com/example/morse-starter/releases/tag/v1.0'})
        with self.assertRaisesRegex(Refusal, "isn't in the contract's shape: version: must match"):
            check(self.deck)

    def test_a_source_that_fails_says_so(self):
        (self.deck / 'scripts/source_data.py').write_text('def inputs(language):\n    raise RuntimeError("no cards yet")\n')
        with self.assertRaisesRegex(Refusal, 'scripts/source_data.py failed: RuntimeError: no cards yet'):
            check(self.deck)

    def test_the_command_says_what_it_found(self):
        for arguments, code, said in (([str(EXAMPLE)], 0, 'The deck holds to the contract'),
                                      ([str(EXAMPLE), '--rectoverso'], 1, 'Refused: morse-starter: repository')):
            with self.subTest(arguments=arguments):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    self.assertEqual(command.main(arguments), code)
                self.assertIn(said, out.getvalue() + err.getvalue())


class PayloadTests(unittest.TestCase):
    """A note's payload is one the app reads, or the card would come in without its identity."""

    def note(self, payload):
        field = payload if isinstance(payload, str) else html.escape(json.dumps(payload))
        return [{'guid': 'ex-morse-en-letter-e', 'fields': {'Front': '·', 'RectoVerso': field}}]

    def test_a_payload_the_app_cant_read_is_refused(self):
        good = {'v': 1, 'book': '6f1d2c3b-4a59-4e68-9b7a-0c1d2e3f4a5b', 'card': '0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d', 'kind': 'basic'}
        contract.verify_payloads('deck/en', self.note(good))
        contract.verify_payloads('deck/en', self.note(html.escape(json.dumps(good)) + '<img src="clean.png">'))
        contract.verify_payloads('deck/en', [{'guid': 'ex-morse-en-letter-e', 'fields': {'Front': '·'}}])
        for payload, message in (({key: value for key, value in good.items() if key != 'book'}, 'missing book'),
                                 (good | {'kind': 'flashcard'}, 'kind: must be one of'),
                                 (good | {'noteID': 12}, 'noteID: must be a string'),
                                 ('not JSON at all', "doesn't start with a JSON object"),
                                 ('{"v": 1, ', "doesn't start with a JSON object")):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(Refusal, 'ex-morse-en-letter-e: .*' + message):
                    contract.verify_payloads('deck/en', self.note(payload))


class DocumentationTests(unittest.TestCase):
    """The pages say what the check does: its categories, and every refusal it can make."""

    def test_the_contract_page_lists_the_categories(self):
        page = (KIT / 'docs/contract.md').read_text()
        section = page.split('### Categories', 1)[1].split('###', 1)[0]
        rows = re.findall(r'^\| `([a-z]+)` \| ([^|]+) \| ([^|]+) \|$', section, re.MULTILINE)
        listed = {key: {'en': english.strip(), 'fr': french.strip()} for key, english, french in rows}
        self.assertEqual(listed, contract.CATEGORIES)

    def test_every_refusal_is_explained(self):
        page = ' '.join((KIT / 'docs/check.md').read_text().split())
        source = (KIT / 'deck_kit/contract.py').read_text()
        # Each refusal's opening words, after the deck's name: the page quotes them.
        openings = set()
        for literal in re.findall(r"raise Refusal\(\s*f?'((?:[^'\\]|\\.)*)'", source):
            words = re.sub(r'\{[^}]*\}(/\{[^}]*\})?: ', '', literal, count=1).replace("\\'", "'")
            words = re.split(r'\{', words)[0].strip()
            if len(words) >= 12:
                openings.add(words)
        self.assertGreater(len(openings), 30)
        missing = sorted(words for words in openings if words not in page)
        self.assertEqual(missing, [], 'docs/check.md explains every refusal')

    def test_every_link_between_the_pages_resolves(self):
        pages = [KIT / name for name in ('README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'LICENSE-docs.md')]
        pages += sorted((KIT / 'docs').glob('*.md')) + sorted((KIT / 'examples').glob('*/README.md'))

        def anchors(page):
            # GitHub's anchor for a heading: lowercase, punctuation dropped, spaces to hyphens.
            headings = re.findall(r'^#+ (.+)$', page.read_text(), re.MULTILINE)
            return {re.sub(r'[^a-z0-9 _-]', '', heading.lower().replace('`', '')).replace(' ', '-') for heading in headings}

        for page in pages:
            for target in re.findall(r'\]\(([^)\s]+)\)', page.read_text()):
                if target.startswith(('http://', 'https://', 'mailto:')):
                    continue
                path, _, anchor = target.partition('#')
                linked = (page.parent / path).resolve() if path else page
                with self.subTest(page=page.name, target=target):
                    self.assertTrue(linked.exists(), f'{page.name}: {target} leads nowhere')
                    if anchor and linked.suffix == '.md':
                        self.assertIn(anchor, anchors(linked), f'{page.name}: {target} names no heading')

    def test_the_pages_name_nothing_private(self):
        # Written for a stranger: no issue numbers, no machine's paths.
        for page in [KIT / 'README.md', KIT / 'AGENTS.md', KIT / 'CONTRIBUTING.md', *sorted((KIT / 'docs').glob('*.md'))]:
            text = page.read_text()
            with self.subTest(page=page.name):
                self.assertIsNone(re.search(r'(?<![\w&])#\d{2,}\b', text), 'an issue number')
                self.assertIsNone(re.search(r'/Users/|/Volumes/|~/Dev', text), "a machine's path")


if __name__ == '__main__':
    unittest.main()
