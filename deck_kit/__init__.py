"""The RectoVerso deck kit's check: the deck contract's rules, in Python's standard library alone.

    from deck_kit import check, Refusal, RECTOVERSO

    check('path/to/deck')                      # any author's deck
    check('path/to/deck', gallery=RECTOVERSO)  # as RectoVerso's own gallery takes it

docs/check.md says how to run it, and what each refusal means.
"""
from .contract import (ANYWHERE, CATEGORIES, NEW_PER_DAY, OPEN_LICENSES, PLAY_LABEL_LIMIT, RECTOVERSO, STUDY, Gallery,
                       Refusal, check, cover_files, cover_name, guid_prefix, payload, sample_card, sidecar_name,
                       source_inputs, verify_metadata, verify_payloads, verify_prerequisites, verify_sample)

__version__ = '1.0.1'
