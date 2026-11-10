#!/usr/bin/env python3
"""Check a deck against the RectoVerso deck contract.

    python3 kit/check.py                 # the deck in the current folder
    python3 kit/check.py path/to/deck
    python3 kit/check.py --rectoverso    # as RectoVerso's own gallery takes a deck

Exits 0 when the deck holds to the contract, 1 with the rule it breaks. docs/check.md has the rest.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deck_kit import ANYWHERE, RECTOVERSO, Refusal, __version__, check  # noqa: E402


def main(arguments=None):
    parser = argparse.ArgumentParser(description='Check a deck against the RectoVerso deck contract.')
    parser.add_argument('deck', nargs='?', default='.', help="the deck's folder (default: the current one)")
    parser.add_argument('--rectoverso', action='store_true',
                        help="hold the deck to RectoVerso's own gallery too: in its organization, approved, Pro decks named apart")
    parser.add_argument('--python', default=sys.executable,
                        help="the Python that runs the deck's scripts/source_data.py (default: this one)")
    parser.add_argument('--version', action='version', version='rectoverso-deck-kit ' + __version__)
    options = parser.parse_args(arguments)
    try:
        artifacts = check(options.deck, python=options.python, gallery=RECTOVERSO if options.rectoverso else ANYWHERE)
    except Refusal as refusal:
        print('Refused: ' + str(refusal), file=sys.stderr)
        return 1
    for artifact in artifacts:
        print(f"{artifact['id']}: {artifact['cards']} cards, {artifact['package']['file']}")
    print('The deck holds to the contract (kit ' + __version__ + ').')
    return 0


if __name__ == '__main__':
    sys.exit(main())
