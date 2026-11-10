# Morse starter

The deck kit's worked example: a deck small enough to read in one sitting, in English and French, that passes the check. It teaches four letters of Morse code, then three short words made of them, and each word [waits for its letters](../../docs/prerequisites.md).

| File | What to read it for |
|---|---|
| [rectoverso.json](rectoverso.json) | Every required field, a study preset, two languages. Annotated in [the contract](../../docs/contract.md#an-example-annotated). |
| [source/](source) | Content kept once (`cards.json`: the letters and their Morse) and each language's words beside it. |
| [scripts/source_data.py](scripts/source_data.py) | `inputs(language)`: the notes, their GUIDs, each card's payload with what it requires and introduces. |
| [scripts/build.py](scripts/build.py) | One language's package and its sidecar, built with Anki's Python library. |
| [scripts/checks/](scripts/checks) | A package opened in Anki, and a rebuild held to the first build. |

Check it, from the kit's root:

```sh
python3 check.py examples/morse-starter
```

Build it (this needs `pip install anki`; the check doesn't):

```sh
cd examples/morse-starter
python scripts/build.py --language en --out /tmp/morse/Morse-starter-en.apkg
python scripts/checks/validate-anki.py /tmp/morse/Morse-starter-en.apkg
```

It isn't published anywhere (`publication.approved` is `false`, and its repository address is a placeholder): it is here to be copied. In your own deck the kit sits at `kit/`, and the check is `python3 kit/check.py`.
