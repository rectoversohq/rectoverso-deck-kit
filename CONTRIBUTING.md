# Contributing

The kit is the source of truth for the deck contract and the rules for authoring a deck. RectoVerso reads decks by it, and every deck is checked by it, so a change here is a change for all of them.

## How a change is made

- **By pull request.** `main` is protected; the tests run on every pull request; a merge waits for the owner's go.
- **Run the tests first:** `python3 -m unittest discover -s tests`. Python's standard library only: the kit has no dependencies, and gains none.
- **One change, everywhere at once.** A rule lives in four places that must agree: the check (`deck_kit/contract.py`), the schemas (`schemas/`), the pages (`docs/`), and the tests. The tests hold some of that together (the schemas' lists against the check's, the categories and every refusal against the pages); the rest is yours.
- **Add a line to [CHANGELOG.md](CHANGELOG.md)** under the next version.

## Changing the contract

A new field, value or form is a change to the contract.

1. **Propose it in an issue first:** what a deck needs to say, and what the app would do with it.
2. **The app follows before a deck uses it.** A deck can only say what the app reads. A contract change is tagged here once a version of RectoVerso reads it (or, for something the app ignores safely, once that is confirmed), never before.
3. **Additions are optional.** A deck that passed still passes: a new field is one a deck may leave out, and the app reads a deck without it as before. That is a minor version.
4. **A change that refuses a deck that passed, removes a field or changes what one means** is a major version, with a section in the changelog that says what each deck has to change.
5. **Read leniently, check strictly.** The app ignores what it doesn't know and never fails a whole deck over one optional value; the check refuses anything the app wouldn't read as the author meant.

## Writing

- The pages are written for someone who has never seen RectoVerso's own repository: no reference to its issues, its files or anyone's machine.
- American English. Interface names in bold (**Deck options**, **Lesson mode**).
- A page says what is true now. When and why something changed goes in the changelog.

## Licenses

By contributing you agree that your code is under the [MIT license](LICENSE) and your documents under [Creative Commons Attribution 4.0](LICENSE-docs.md).
