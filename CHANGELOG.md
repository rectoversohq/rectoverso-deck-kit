# Changelog

What each version of the kit changed. Versions follow [docs/versioning.md](docs/versioning.md#the-kits-versions).

## 1.0.1

- **AGENTS.md:** the rules every deck's agents follow that the first version left out: start only on an explicit go, a go for one step isn't a go for the next, a dated entry for each decision, never invent a fact, and new-card stages as an introduction order.
- **Docs:** one package a language is the deck's rule; how a gallery groups packages for delivery is the gallery's own ([docs/languages.md](docs/languages.md), [docs/versioning.md](docs/versioning.md#a-release)).

## 1.0.0

The first version: the contract as RectoVerso 1.1 reads it.

- **The contract:** `rectoverso.json`, field by field ([docs/contract.md](docs/contract.md)), with its JSON Schema.
- **The card payload:** a note's `RectoVerso` field, with its JSON Schema, and the other fields the app reads ([docs/card-payload.md](docs/card-payload.md)).
- **Prerequisites:** a card's `requires` and `introduces`, for the app's **Lesson mode** ([docs/prerequisites.md](docs/prerequisites.md)).
- **The check:** `check.py` and the `deck_kit` module, for any deck or for RectoVerso's own gallery ([docs/check.md](docs/check.md)).
- **Covers, languages, versions and releases** ([docs/covers.md](docs/covers.md), [docs/languages.md](docs/languages.md), [docs/versioning.md](docs/versioning.md)).
- **An example deck,** `examples/morse-starter`, in English and French.
