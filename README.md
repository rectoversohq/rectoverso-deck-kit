# RectoVerso deck kit

Everything a deck needs to be read well by [RectoVerso](https://rectoverso.code-think.com), a flashcard app for iPhone: the contract a deck holds to, a check that holds it to it, and the rules for writing one.

A deck here is an [Anki](https://apps.ankiweb.net) package (`.apkg`) built from a source repository. RectoVerso opens any Anki package. A deck that follows this kit also tells the app what Anki has no words for: which cards build on which, where a card's place is on a map, what a gallery shows of the deck before it is added.

## Who it's for

- **Deck authors,** who want their deck to study well in RectoVerso, opened as a file or offered in a gallery.
- **Agents** (Claude Code, Codex and others) working in a deck's repository: [AGENTS.md](AGENTS.md) is their way in.
- **RectoVerso itself:** the app's own gallery runs this check on every deck it adopts, so the kit and the app can't drift apart.

## What's in it

| Path | What it is |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | From an empty repository to a deck that passes the check. |
| [docs/contract.md](docs/contract.md) | `rectoverso.json`, field by field, with an annotated example. |
| [docs/card-payload.md](docs/card-payload.md) | What a note tells the app about its card: the payload, and the other fields the app reads. |
| [docs/prerequisites.md](docs/prerequisites.md) | Cards that build on each other, and the app's **Lesson mode**. |
| [docs/covers.md](docs/covers.md) | The pictures a gallery shows of a deck. |
| [docs/languages.md](docs/languages.md) | One deck in several languages; the rules for English and French. |
| [docs/check.md](docs/check.md) | Running the check, every refusal it can make and how to fix it, and the check in CI. |
| [docs/versioning.md](docs/versioning.md) | A deck's versions and releases, the kit's versions, and moving to a new one. |
| [schemas/](schemas) | JSON Schema (2020-12) for `rectoverso.json` and for a card's payload. |
| [deck_kit/](deck_kit), [check.py](check.py) | The check: Python's standard library, nothing to install. |
| [examples/morse-starter/](examples/morse-starter) | A small deck in English and French that passes the check, prerequisites included. |
| [tests/](tests) | The check's own tests. |

## A first look

Check the example deck, from a clone of this repository (Python 3.9 or later, nothing to install):

```sh
python3 check.py examples/morse-starter
```

```
morse-starter-en: 7 cards, Morse-starter-en.apkg
morse-starter-fr: 7 cards, Morse-starter-fr.apkg
The deck holds to the contract (kit 1.0.0).
```

In a deck's own repository the kit is a Git submodule at `kit/`, pinned to a version:

```sh
git submodule add https://github.com/rectoversohq/rectoverso-deck-kit.git kit
git -C kit checkout v1.0.0
python3 kit/check.py
```

[Getting started](docs/getting-started.md) goes from there to a deck of your own.

## What the check does, and doesn't

It reads the deck's `rectoverso.json` and asks the deck's own `scripts/source_data.py` what each language's notes are. Then it holds both to the contract: the fields and their values, the identities, the sample, the covers' names, the licenses, each card's payload, and the order cards teach in. It stops at the first rule the deck breaks and says which.

It doesn't build a package, open Anki, download a release or look at a picture. A deck's own checks do that ([Getting started](docs/getting-started.md#5-build-and-look)), and RectoVerso's gallery runs its own further checks on the packages it adopts: each one opened in Anki, imported and exported by the app's own code, and opened in Anki again.

## Versions

The kit is versioned as a whole ([CHANGELOG.md](CHANGELOG.md)). A deck pins the version it was written for, and moves to a new one by pull request ([Versioning](docs/versioning.md)). A change to the contract is made here first, and the app follows before any deck uses it ([CONTRIBUTING.md](CONTRIBUTING.md)).

## Licenses

The code (`check.py`, `deck_kit/`, `schemas/`, `tests/`, and the scripts in `examples/`) is under the [MIT license](LICENSE). The documents (this file, `AGENTS.md`, `docs/`, and the example deck's content) are under [Creative Commons Attribution 4.0](LICENSE-docs.md). © Simon Pinkas.

RectoVerso is on the [App Store](https://apps.apple.com/app/id6815844763). Questions: rectoverso@code-think.com.
