"""The kit's schemas, and the small validator that reads them."""
import json
import sys
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

from deck_kit import schema  # noqa: E402
from deck_kit.contract import CATEGORIES, NEW_PER_DAY, OPEN_LICENSES, PLAY_LABEL_LIMIT, REQUIRED, STUDY, load_schema  # noqa: E402


class ValidatorTests(unittest.TestCase):
    def test_a_value_is_held_to_its_type_and_true_is_never_a_number(self):
        self.assertEqual(schema.errors(3, {'type': 'integer'}), [])
        self.assertEqual(schema.errors(True, {'type': 'integer'}), ['the document: must be an integer'])
        self.assertEqual(schema.errors(1, {'const': True}), ['the document: must be true'])
        self.assertEqual(schema.errors('a', {'type': ['string', 'null']}), [])

    def test_an_error_says_where(self):
        rules = {'type': 'object', 'required': ['a'], 'additionalProperties': False,
                 'properties': {'a': {'type': 'array', 'items': {'type': 'string', 'pattern': '^[a-z]+$'}}}}
        self.assertEqual(sorted(schema.errors({'a': ['x', 'Y'], 'b': 1}, rules)),
                         ['a[1]: must match ^[a-z]+$', 'b: not a key this object has'])
        self.assertEqual(schema.errors({}, rules), ['the document: missing a'])

    def test_a_pattern_ends_at_the_end_of_the_text(self):
        # JSON Schema's `$` is the end of the text; Python's also matches before a last line break.
        self.assertEqual(schema.errors('abc\n', {'pattern': '^[a-z]+$'}), ['the document: must match ^[a-z]+$'])

    def test_references_stay_in_the_file(self):
        rules = {'$defs': {'word': {'type': 'string', 'minLength': 1}}, 'properties': {'a': {'$ref': '#/$defs/word'}}}
        self.assertEqual(schema.errors({'a': ''}, rules), ['a: must not be empty'])
        with self.assertRaises(schema.SchemaError):
            schema.errors({}, {'$ref': 'https://example.com/other.json'})

    def test_a_keyword_it_doesnt_check_is_an_error_never_a_rule_skipped(self):
        with self.assertRaisesRegex(schema.SchemaError, 'contains'):
            schema.errors([], {'contains': {'type': 'string'}})


class SchemaFileTests(unittest.TestCase):
    """The two schema files say what the check's own rules say."""

    def test_the_schemas_use_only_what_the_validator_checks(self):
        def walk(rules, root):
            schema.errors(None, rules, root)  # Raises SchemaError on a keyword it doesn't check.
            for key, value in rules.items():
                for sub in (value.values() if key in ('properties', 'patternProperties', '$defs') else
                            value if key in ('allOf', 'anyOf', 'oneOf') else
                            [value] if key in ('items', 'additionalProperties', 'propertyNames', 'not') and isinstance(value, dict) else []):
                    walk(sub, root)
        for name in ('rectoverso', 'card-payload'):
            rules = load_schema(name)
            self.assertEqual(rules['$schema'], 'https://json-schema.org/draft/2020-12/schema')
            walk(rules, rules)

    def test_the_metadata_schema_and_the_rules_agree_on_their_lists(self):
        rules = load_schema('rectoverso')
        properties = rules['properties']
        self.assertEqual(tuple(rules['required']), REQUIRED)
        self.assertEqual(properties['categories']['items']['enum'], list(CATEGORIES))
        self.assertEqual(properties['playLabel']['additionalProperties']['maxLength'], PLAY_LABEL_LIMIT)
        study = properties['study']['properties']
        self.assertEqual({key: tuple(study[key]['enum']) for key in STUDY}, STUDY)
        self.assertEqual((study['newPerDay']['minimum'], study['newPerDay']['maximum']), (NEW_PER_DAY.start, NEW_PER_DAY.stop - 1))
        self.assertEqual(set(properties['imageCredits']['items']['properties']['license']['enum']), OPEN_LICENSES)

    def test_the_example_deck_is_in_both_schemas_shape(self):
        example = KIT / 'examples/morse-starter'
        self.assertEqual(schema.errors(json.loads((example / 'rectoverso.json').read_text()), load_schema('rectoverso')), [])

    def test_a_payload_must_be_one_the_app_reads(self):
        rules = load_schema('card-payload')
        payload = {'v': 1, 'book': '6f1d2c3b-4a59-4e68-9b7a-0c1d2e3f4a5b', 'card': '0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d', 'kind': 'basic'}
        self.assertEqual(schema.errors(payload, rules), [])
        self.assertEqual(schema.errors(payload | {'requires': ['a'], 'introduces': ['b'], 'somethingNew': 1}, rules), [])
        for change, message in [({'kind': 'flash'}, 'kind: must be one of'), ({'v': 2}, 'v: must be 1'),
                                ({'book': 'my-deck'}, 'book: must match'), ({'noteID': 7}, 'noteID: must be a string'),
                                ({'resources': [{'name': 'Romaji'}]}, 'resources[0]: missing text'),
                                ({'occlusion': {'imageName': 'a.png'}}, 'occlusion: missing box'),
                                ({'occlusion': {'imageName': 'a.png', 'box': [[0, 0], [1, 1]], 'shapes': [{'rect': [[0, 0], [1, 1]]}]}},
                                 'occlusion.shapes[0].rect: must be an object')]:
            with self.subTest(change=change):
                found = schema.errors(payload | change, rules)
                self.assertTrue(any(message in line for line in found), found)
        missing = dict(payload)
        del missing['card']
        self.assertEqual(schema.errors(missing, rules), ['the document: missing card'])


if __name__ == '__main__':
    unittest.main()
