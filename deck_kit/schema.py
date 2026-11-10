"""A small JSON Schema validator, enough for the kit's own schemas.

The kit has no dependencies, so it carries the part of JSON Schema (draft 2020-12) its schemas
use, and refuses a schema that uses anything else: a keyword this file doesn't check is an error,
never a rule silently skipped. A full validator (the `jsonschema` package, an editor) reads the
same schema files and agrees with this one on them.
"""
import re

# Keywords that say something about a schema without constraining a value.
ANNOTATIONS = {'$schema', '$id', '$comment', '$defs', 'title', 'description', 'examples', 'default', 'deprecated'}

TYPES = {
    'object': lambda value: isinstance(value, dict),
    'array': lambda value: isinstance(value, list),
    'string': lambda value: isinstance(value, str),
    'boolean': lambda value: isinstance(value, bool),
    'null': lambda value: value is None,
    # JSON's true and false are Python's bool, a kind of int: never a number here.
    'integer': lambda value: (isinstance(value, int) and not isinstance(value, bool))
                             or (isinstance(value, float) and value.is_integer()),
    'number': lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
}


class SchemaError(Exception):
    """The schema itself can't be used: a keyword this validator doesn't check, or a broken reference."""


def errors(value, schema, root=None, path=''):
    """Every way `value` breaks `schema`, as "<where>: <what>" lines; an empty list when it holds."""
    root = schema if root is None else root
    if schema is True:
        return []
    if schema is False:
        return [f'{path or "the document"}: not allowed']
    found = []
    where = path or 'the document'

    def fail(message):
        found.append(f'{where}: {message}')

    for keyword, rule in schema.items():
        if keyword in ANNOTATIONS:
            continue
        if keyword == '$ref':
            found += errors(value, _resolve(rule, root), root, path)
        elif keyword == 'type':
            names = rule if isinstance(rule, list) else [rule]
            if not any(TYPES[name](value) for name in names):
                fail(f'must be {_article(" or ".join(names))}')
        elif keyword == 'enum':
            if not any(_same(value, choice) for choice in rule):
                fail('must be one of ' + ', '.join(_show(choice) for choice in rule))
        elif keyword == 'const':
            if not _same(value, rule):
                fail(f'must be {_show(rule)}')
        elif keyword in ('allOf', 'anyOf', 'oneOf'):
            results = [errors(value, option, root, path) for option in rule]
            passing = sum(not result for result in results)
            if keyword == 'allOf':
                for result in results:
                    found += result
            elif keyword == 'anyOf' and passing == 0:
                fail('matches none of the allowed forms (' + '; '.join(result[0] for result in results if result) + ')')
            elif keyword == 'oneOf' and passing != 1:
                fail(f'must match exactly one of the allowed forms, and matches {passing}')
        elif keyword == 'not':
            if not errors(value, rule, root, path):
                fail('is a form that is not allowed here')
        elif keyword in ('minLength', 'maxLength', 'pattern'):
            if isinstance(value, str):
                if keyword == 'minLength' and len(value) < rule:
                    fail('must not be empty' if rule == 1 else f'must have at least {rule} characters')
                elif keyword == 'maxLength' and len(value) > rule:
                    fail(f'must have at most {rule} characters')
                elif keyword == 'pattern' and not re.search(_pattern(rule), value):
                    fail(f'must match {rule}')
        elif keyword in ('minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum'):
            if TYPES['number'](value):
                if keyword == 'minimum' and value < rule:
                    fail(f'must be at least {rule}')
                elif keyword == 'maximum' and value > rule:
                    fail(f'must be at most {rule}')
                elif keyword == 'exclusiveMinimum' and value <= rule:
                    fail(f'must be more than {rule}')
                elif keyword == 'exclusiveMaximum' and value >= rule:
                    fail(f'must be less than {rule}')
        elif keyword in ('minItems', 'maxItems', 'uniqueItems', 'items'):
            if isinstance(value, list):
                if keyword == 'minItems' and len(value) < rule:
                    fail('must not be empty' if rule == 1 else f'must have at least {rule} items')
                elif keyword == 'maxItems' and len(value) > rule:
                    fail(f'must have at most {rule} items')
                elif keyword == 'uniqueItems' and rule and any(
                        _same(a, b) for index, a in enumerate(value) for b in value[:index]):
                    fail('must list each item once')
                elif keyword == 'items':
                    for index, item in enumerate(value):
                        found += errors(item, rule, root, f'{path}[{index}]')
        elif keyword in ('required', 'minProperties', 'maxProperties', 'properties', 'patternProperties',
                         'additionalProperties', 'propertyNames', 'dependentRequired'):
            if isinstance(value, dict):
                if keyword == 'required':
                    missing = [name for name in rule if name not in value]
                    if missing:
                        fail('missing ' + ', '.join(missing))
                elif keyword == 'minProperties' and len(value) < rule:
                    fail('must not be empty' if rule == 1 else f'must have at least {rule} keys')
                elif keyword == 'maxProperties' and len(value) > rule:
                    fail(f'must have at most {rule} keys')
                elif keyword == 'properties':
                    for name, sub in rule.items():
                        if name in value:
                            found += errors(value[name], sub, root, _join(path, name))
                elif keyword == 'patternProperties':
                    for pattern, sub in rule.items():
                        for name in value:
                            if re.search(pattern, name):
                                found += errors(value[name], sub, root, _join(path, name))
                elif keyword == 'additionalProperties':
                    named = set(schema.get('properties', {}))
                    patterns = list(schema.get('patternProperties', {}))
                    for name in value:
                        if name not in named and not any(re.search(pattern, name) for pattern in patterns):
                            if rule is False:
                                found.append(f'{_join(path, name)}: not a key this object has')
                            else:
                                found += errors(value[name], rule, root, _join(path, name))
                elif keyword == 'propertyNames':
                    for name in value:
                        found += [message.replace(_join(path, name), f'{_join(path, name)} (the key)', 1)
                                  for message in errors(name, rule, root, _join(path, name))]
                elif keyword == 'dependentRequired':
                    for name, needed in rule.items():
                        missing = [other for other in needed if name in value and other not in value]
                        if missing:
                            fail(f'{name} needs ' + ', '.join(missing))
        elif keyword == 'format':
            continue  # A hint for readers and editors; the check's own rules hold dates and URLs.
        else:
            raise SchemaError(f'{keyword}: a keyword this validator does not check')
    return found


def _resolve(reference, root):
    if not reference.startswith('#/'):
        raise SchemaError(f'{reference}: only references inside the same file are followed')
    target = root
    for part in reference[2:].split('/'):
        if not isinstance(target, dict) or part not in target:
            raise SchemaError(f'{reference}: nothing there')
        target = target[part]
    return target


def _pattern(rule):
    """A JSON Schema pattern for Python's `re`: its `$` is the end of the text, never before a last line break."""
    return rule[:-1] + r'\Z' if rule.endswith('$') and not rule.endswith('\\$') else rule


def _same(a, b):
    """Equal as JSON values: true is never 1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    return a == b


def _show(value):
    return '"' + value + '"' if isinstance(value, str) else str(value).lower() if isinstance(value, bool) else str(value)


def _article(name):
    return ('an ' if name[0] in 'aeio' else 'a ') + name


def _join(path, name):
    return f'{path}.{name}' if path else name
